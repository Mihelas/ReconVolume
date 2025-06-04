import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from io import BytesIO
from datetime import datetime

# Set page config and style
st.set_page_config(page_title="Lyophilized Drug Product Reconstitution Calculator", layout="wide")
plt.style.use('seaborn-whitegrid')
sns.set_palette("husl")

# Initialize session states
if 'calculate_clicked' not in st.session_state:
    st.session_state.calculate_clicked = False

if 'excipients' not in st.session_state:
    st.session_state.excipients = []

# Define available excipients
AVAILABLE_EXCIPIENTS = [
    "Histidine",
    "Histidine HCl",
    "Sucrose",
    "PS80",
    "Custom excipient"
]

# Create a function to add new excipient
def add_excipient():
    st.session_state.excipients.append({
        'name': '',
        'concentration': 0.0
    })

# Create a function to remove excipient
def remove_excipient(index):
    st.session_state.excipients.pop(index)

# Function to export data to Excel
def export_to_excel(pre_lyo_df, post_recon_df, recon_df, mass_data, volume_data, 
                   components, pre_concentrations, post_concentrations, figures):
    """Create an Excel file with all calculation results and graphs."""
    output = BytesIO()
    
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        # Write DataFrames to different sheets
        pre_lyo_df.to_excel(writer, sheet_name='Pre-Lyophilization', index=False)
        post_recon_df.to_excel(writer, sheet_name='Post-Reconstitution', index=False)
        recon_df.to_excel(writer, sheet_name='Reconstitution Details', index=False)
        
        # Create a sheet for component comparison
        comp_df = pd.DataFrame({
            'Component': components,
            'Pre-Lyophilization (mg/mL)': pre_concentrations,
            'Post-Reconstitution (mg/mL)': post_concentrations
        })
        comp_df.to_excel(writer, sheet_name='Component Comparison', index=False)
        
        # Get the workbook and create a format for headers
        workbook = writer.book
        header_format = workbook.add_format({
            'bold': True,
            'fg_color': '#D7E4BC',
            'border': 1
        })
        
        # Add the figures to a separate sheet
        worksheet = workbook.add_worksheet('Visualizations')
        
        # Save each figure
        row = 0
        for name, fig in figures.items():
            imgdata = BytesIO()
            fig.savefig(imgdata, format='png', bbox_inches='tight')
            worksheet.insert_image(row, 0, '', {'image_data': imgdata})
            row += 30  # Space for next image
        
        # Adjust column widths
        for sheet in writer.sheets.values():
            sheet.set_column('A:Z', 15)
            
    return output

st.title("Lyophilized Drug Product Reconstitution Calculator")

st.markdown("""
This application calculates the required diluent volume for reconstitution of lyophilized drug products,
accounting for solid content displacement and density corrections.
""")

# Create two columns for input parameters
col1, col2 = st.columns(2)

with col1:
    st.subheader("Pre-Lyophilization Parameters")
    
    # Drug inputs
    st.markdown("##### Drug")
    drug_name = st.text_input("Drug Name", value="SARxxxx")
    drug_conc = st.number_input("Drug Concentration (mg/mL)", value=8.0, step=0.1)
    
    # Process parameters
    st.markdown("##### Process Parameters")
    filling_volume = st.number_input("Filling Volume (mL)", value=8.0, step=0.1)
    density_pre_lyo = st.number_input("Density of Solution Prior to Lyophilization (mg/mL)", value=1030.0, step=1.0)

with col2:
    st.subheader("Reconstitution Parameters")
    
    # Reconstitution parameters
    recon_volume = st.number_input("Target Volume After Reconstitution (mL)", value=4.0, step=0.1)
    density_post_recon = st.number_input("Density of Reconstituted Solution (mg/mL)", value=1030.0, step=1.0)
    diluent_density = st.number_input("Diluent Density (e.g., Water) (mg/mL)", value=998.2, step=0.1)
    
    # Vial information
    st.markdown("##### Vial Information")
    vial_options = {"2R": 3.4, "10R": 14.0, "20R": 25.0}
    selected_vial = st.selectbox("Vial Size", options=list(vial_options.keys()))
    brim_fill_volume = vial_options[selected_vial]
    st.write(f"Brim Fill Volume: {brim_fill_volume} mL")

# Separate section for excipients
st.subheader("Excipients")
excipients_col1, excipients_col2 = st.columns([1, 3])

with excipients_col1:
    st.button("+ Add Excipient", on_click=add_excipient)

with excipients_col2:
    for i, excipient in enumerate(st.session_state.excipients):
        col1, col2, col3 = st.columns([2, 2, 1])
        
        with col1:
            selected_excipient = st.selectbox(
                "Select Excipient",
                AVAILABLE_EXCIPIENTS,
                key=f"excipient_select_{i}"
            )
            
            if selected_excipient == "Custom excipient":
                custom_name = st.text_input("Enter excipient name", key=f"custom_name_{i}")
                st.session_state.excipients[i]['name'] = custom_name
            else:
                st.session_state.excipients[i]['name'] = selected_excipient
        
        with col2:
            concentration = st.number_input(
                "Concentration (mg/mL)",
                value=st.session_state.excipients[i]['concentration'],
                step=0.01,
                key=f"excipient_conc_{i}"
            )
            st.session_state.excipients[i]['concentration'] = concentration
        
        with col3:
            st.write("")  # Add some spacing
            st.write("")  # Add some spacing
            if st.button("Remove", key=f"remove_{i}"):
                remove_excipient(i)
                st.experimental_rerun()

# Add a calculate button
st.button("Calculate Reconstitution Parameters", type="primary", 
         on_click=lambda: setattr(st.session_state, 'calculate_clicked', True))

# Only show results if calculate button has been clicked
if st.session_state.calculate_clicked:
    # Calculate total solid content including dynamic excipients
    excipient_conc_sum = sum(exc['concentration'] for exc in st.session_state.excipients)
    total_solid_conc = drug_conc + excipient_conc_sum
    wfi_conc = density_pre_lyo - total_solid_conc

    # Calculate per vial amounts
    drug_amount = drug_conc * filling_volume
    
    # Create lists for excipient names and calculations
    excipient_names = [exc['name'] for exc in st.session_state.excipients]
    excipient_concentrations = [exc['concentration'] for exc in st.session_state.excipients]
    excipient_amounts = [conc * filling_volume for conc in excipient_concentrations]
    
    total_solid_amount = total_solid_conc * filling_volume
    wfi_amount = wfi_conc * filling_volume

    # Calculate reconstitution parameters
    theoretical_solid_mass = total_solid_amount  # mg/vial
    diluent_mass_needed = (recon_volume * density_post_recon) - theoretical_solid_mass  # mg/vial
    diluent_volume_needed = diluent_mass_needed / diluent_density  # mL/vial

    # Calculate concentrations after reconstitution
    drug_conc_after = drug_amount / recon_volume
    excipient_conc_after = [amount / recon_volume for amount in excipient_amounts]
    wfi_conc_after = (wfi_amount + diluent_mass_needed) / recon_volume

    # Display results
    st.header("Calculation Results")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Pre-Lyophilization Composition")
        pre_lyo_data = {
            "Component": [drug_name] + excipient_names + ["Total Solids", "WFI"],
            "Concentration (mg/mL)": [drug_conc] + excipient_concentrations + [total_solid_conc, wfi_conc],
            "Amount per Vial (mg)": [drug_amount] + excipient_amounts + [total_solid_amount, wfi_amount]
        }
        pre_lyo_df = pd.DataFrame(pre_lyo_data)
        st.dataframe(pre_lyo_df)

    with col2:
        st.subheader("Post-Reconstitution Composition")
        post_recon_data = {
            "Component": [drug_name] + excipient_names + ["WFI"],
            "Concentration (mg/mL)": [drug_conc_after] + excipient_conc_after + [wfi_conc_after]
        }
        post_recon_df = pd.DataFrame(post_recon_data)
        st.dataframe(post_recon_df)

    # Reconstitution calculation details
    st.subheader("Reconstitution Calculation Details")
    recon_details = {
        "Parameter": ["Theoretical Solid Mass", "Mass of Diluent Needed", "Volume of Diluent to Add"],
        "Value": [f"{theoretical_solid_mass:.2f} mg/vial", f"{diluent_mass_needed:.2f} mg/vial", f"{diluent_volume_needed:.4f} mL/vial"],
    }
    recon_df = pd.DataFrame(recon_details)
    st.dataframe(recon_df)

    # Visualizations
    st.header("Visualizations")

    # Prepare data for mass visualization
    mass_data = {
        'Category': ['Liquide+Solid', 'Solid', 'Recon+Solid'],
        'Solid': [total_solid_amount/1000, total_solid_amount/1000, total_solid_amount/1000],  # Converting to grams
        'Liquid': [wfi_amount/1000, 0, diluent_mass_needed/1000]  # Converting to grams
    }

    # Prepare data for volume visualization
    volume_data = {
        'Category': ['Liquide+Solid', 'Solid', 'Recon+Solid'],
        'Solid': [total_solid_amount/(density_pre_lyo), total_solid_amount/(density_pre_lyo), total_solid_amount/(density_post_recon)],
        'Liquid': [wfi_amount/diluent_density, 0, diluent_volume_needed]
    }

    # Create two columns for the graphs
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Masses")
        
        fig1, ax = plt.subplots(figsize=(10, 6))
        
        # Define positions and width
        categories = mass_data['Category']
        x = np.arange(len(categories))
        width = 0.6
        
        # Create stacked bar chart for masses
        solid_bars = ax.bar(x, mass_data['Solid'], width, label='Solid', color='#3366cc')
        liquid_bars = ax.bar(x, mass_data['Liquid'], width, bottom=mass_data['Solid'], 
                             label='Liquid', color='#99ccff')
        
        # Add value labels on the bars
        for i, category in enumerate(categories):
            solid_height = mass_data['Solid'][i]
            liquid_height = mass_data['Liquid'][i]
            total_height = solid_height + liquid_height
            
            # Label for solid portion (if significant)
            if solid_height > 0.1:
                ax.text(i, solid_height/2, f'{solid_height:.1f}', 
                        ha='center', va='center', color='white', fontweight='bold')
            
            # Label for liquid portion (if present)
            if liquid_height > 0.1:
                ax.text(i, solid_height + liquid_height/2, f'{liquid_height:.1f}', 
                        ha='center', va='center', color='white', fontweight='bold')
            
            # Total label on top
            ax.text(i, total_height + 0.1, f'{total_height:.1f}', 
                    ha='center', va='bottom', color='black')
            
        # Customize the plot
        ax.set_ylabel('Mass (g)')
        ax.set_title('Masses')
        ax.set_xticks(x)
        ax.set_xticklabels(categories)
        ax.legend(loc='upper right', frameon = True, fancybox=True, shadow=True, framealpha=1, facecolor='white')
        
        plt.tight_layout()
        st.pyplot(fig1)

    with col2:
        st.subheader("Volumes")
        
        fig2, ax = plt.subplots(figsize=(10, 6))
        
        # Define positions and width
        categories = volume_data['Category']
        x = np.arange(len(categories))
        width = 0.6
        
        # Create stacked bar chart for volumes
        solid_bars = ax.bar(x, volume_data['Solid'], width, label='Solid', color='#3366cc')
        liquid_bars = ax.bar(x, volume_data['Liquid'], width, bottom=volume_data['Solid'], 
                             label='Liquid', color='#99ccff')
        
        # Customize the plot
        ax.set_ylabel('Volume (mL)')
        ax.set_title('Volumes')
        ax.set_xticks(x)
        ax.set_xticklabels(categories)
        ax.legend(loc='upper right', frameon = True, fancybox=True, shadow=True, framealpha=1, facecolor='white')
        
        # Add value labels on the bars
        for i, category in enumerate(categories):
            solid_height = volume_data['Solid'][i]
            liquid_height = volume_data['Liquid'][i]
            total_height = solid_height + liquid_height
            
            # Label for solid portion (if significant)
            if solid_height > 0.1:
                ax.text(i, solid_height/2, f'{solid_height:.1f}', 
                        ha='center', va='center', color='white', fontweight='bold')
            
            # Label for liquid portion (if present)
            if liquid_height > 0.1:
                ax.text(i, solid_height + liquid_height/2, f'{liquid_height:.1f}', 
                        ha='center', va='center', color='white', fontweight='bold')
            
            # Total label on top
            ax.text(i, total_height + 0.1, f'{total_height:.1f}', 
                    ha='center', va='bottom', color='black')
        
        plt.tight_layout()
        st.pyplot(fig2)

    # Component comparison visualization
    st.subheader("Component Concentration Comparison")
    
    # Only create the comparison chart if there are components to compare
    components = [drug_name] + excipient_names
    pre_concentrations = [drug_conc] + excipient_concentrations
    post_concentrations = [drug_conc_after] + excipient_conc_after
    
    if components:
        fig3, ax = plt.subplots(figsize=(12, 6))
        
        x = np.arange(len(components))
        width = 0.35
        
        pre_bars = ax.bar(x - width/2, pre_concentrations, width, 
                         label='Pre-Lyophilization', color='royalblue')
        post_bars = ax.bar(x + width/2, post_concentrations, width, 
                          label='Post-Reconstitution', color='darkorange')
        
        ax.set_ylabel('Concentration (mg/mL)')
        ax.set_title('Component Concentration Comparison')
        ax.set_xticks(x)
        ax.set_xticklabels(components, rotation=45)
        ax.legend(loc='best', frameon = True, fancybox=True, shadow=True, facecolor='white')
        
        # Add value labels
        for bars in [pre_bars, post_bars]:
            for bar in bars:
                height = bar.get_height()
                if height > 0:
                    ax.text(bar.get_x() + bar.get_width()/2., height,
                           f'{height:.1f}',
                           ha='center', va='bottom')
        
        plt.tight_layout()
        st.pyplot(fig3)
    else:
        st.write("No components to compare.")
        fig3 = plt.figure()  # Empty figure as placeholder

    # Prepare figures for export
    figures = {
        'Masses': fig1,
        'Volumes': fig2,
        'Component Comparison': fig3
    }
    
    # Create download button
    excel_file = export_to_excel(
        pre_lyo_df, 
        post_recon_df, 
        recon_df,
        mass_data,
        volume_data,
        components,
        pre_concentrations,
        post_concentrations,
        figures
    )
    
    # Generate timestamp for filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    st.download_button(
        label="📥 Download Results as Excel",
        data=excel_file.getvalue(),
        file_name=f"lyophilization_calculation_{timestamp}.xlsx",
        mime="application/vnd.ms-excel",
    )

# Always show methodology explanation
with st.expander("Methodology and Calculations Explained"):
    st.markdown("""
    ### Reconstitution Volume Calculation Methodology
    
    1. **Pre-Lyophilization Stage**:
       - Starting with a liquid formulation containing the active drug and excipients
       - Total solid content is calculated as the sum of all components except water
       - Initial filling volume and density are used to calculate the total mass in the vial
    
    2. **Mass Balance Principle**:
       - Total solids remain constant through the process
       - Per vial calculation: Solid content = Concentration × Initial Volume
    
    3. **Reconstitution Target**:
       - Target volume after reconstitution determines final concentrations
       - Final density consideration affects the amount of diluent needed
    
    4. **Diluent (WFI) Volume Calculation**:
       - Accounts for solid mass displacement and density differences
       - Formula: Diluent Volume = (Target Volume × Target Density - Solid Mass) / Diluent Density
    """)

st.sidebar.header("About")
st.sidebar.info("""
This calculator helps pharmaceutical scientists determine the correct amount of diluent 
needed for reconstitution of lyophilized drug products, accounting for solid content 
displacement and density differences.
""")

st.sidebar.header("References")
st.sidebar.markdown("""
- USP <1> Injections and Implanted Drug Products
- Ph. Eur. 5.1.1 Methods of Preparation of Sterile Products
""")