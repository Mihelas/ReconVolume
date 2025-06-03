import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import seaborn as sns

st.set_page_config(page_title="Lyophilized Drug Product Reconstitution Calculator", layout="wide")

plt.style.use('seaborn')
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
st.button("Calculate Reconstitution Parameters", type="primary", on_click=lambda: setattr(st.session_state, 'calculate_clicked', True))

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
    # In the visualization section:
if st.session_state.calculate_clicked:
    # ... (previous calculations remain the same)

    # Visualizations
    st.header("Visualizations")

    # Create two columns for the graphs
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Mass Distribution")
        
        fig = plt.figure(figsize=(10, 8))
        ax = fig.add_subplot(111, projection='3d')
        
        # Define positions
        xpos = np.array([0, 1, 2])
        ypos = np.array([0, 0, 0])
        zpos = np.zeros(3)
        
        # Define dimensions
        dx = np.ones(3) * 0.5
        dy = np.ones(3) * 0.5
        
        # Create 3D bars for solid mass
        solid_heights = np.array(mass_data['Solid'])
        liquid_heights = np.array(mass_data['Liquid'])
        
        # Plot solid bars
        solid_bars = ax.bar3d(xpos, ypos, zpos, dx, dy, solid_heights, 
                             color='#ff9999', alpha=0.8, shade=True)
        
        # Plot liquid bars on top of solid bars
        liquid_bars = ax.bar3d(xpos, ypos, solid_heights, dx, dy, liquid_heights, 
                              color='#99ccff', alpha=0.8, shade=True)
        
        # Customize the plot
        ax.set_title('Mass Distribution Across Process Steps', pad=20)
        ax.set_xlabel('Process Step')
        ax.set_ylabel('')
        ax.set_zlabel('Mass (g)')
        
        # Set x-axis labels
        ax.set_xticks(xpos + dx/2)
        ax.set_xticklabels(mass_data['Category'])
        
        # Add legend with fancy box
        legend = ax.legend(['Solid', 'Liquid'], 
                          bbox_to_anchor=(1.15, 0.5),
                          loc='center left',
                          bbox_transform=ax.transAxes,
                          fancybox=True, 
                          shadow=True,
                          framealpha=1,
                          edgecolor='black')
        legend.get_frame().set_facecolor('white')
        
        # Add value labels
        for i in range(len(xpos)):
            solid_height = solid_heights[i]
            liquid_height = liquid_heights[i]
            
            # Label for solid portion
            ax.text(xpos[i] + dx[i]/2, ypos[i], solid_height/2, 
                   f'{solid_height:.2f}',
                   horizontalalignment='center',
                   verticalalignment='center')
            
            # Label for liquid portion (if present)
            if liquid_height > 0:
                ax.text(xpos[i] + dx[i]/2, ypos[i], solid_height + liquid_height/2,
                       f'{liquid_height:.2f}',
                       horizontalalignment='center',
                       verticalalignment='center')
        
        # Adjust view angle for better visualization
        ax.view_init(elev=20, azim=45)
        plt.tight_layout()
        st.pyplot(fig)

    with col2:
        st.subheader("Volume Distribution")
        
        fig = plt.figure(figsize=(10, 8))
        ax = fig.add_subplot(111, projection='3d')
        
        # Define positions
        xpos = np.array([0, 1, 2])
        ypos = np.array([0, 0, 0])
        zpos = np.zeros(3)
        
        # Define dimensions
        dx = np.ones(3) * 0.5
        dy = np.ones(3) * 0.5
        
        # Create 3D bars for volumes
        solid_heights = np.array(volume_data['Solid'])
        liquid_heights = np.array(volume_data['Liquid'])
        
        # Plot solid bars
        solid_bars = ax.bar3d(xpos, ypos, zpos, dx, dy, solid_heights, 
                             color='#ff9999', alpha=0.8, shade=True)
        
        # Plot liquid bars on top of solid bars
        liquid_bars = ax.bar3d(xpos, ypos, solid_heights, dx, dy, liquid_heights, 
                              color='#99ccff', alpha=0.8, shade=True)
        
        # Customize the plot
        ax.set_title('Volume Distribution Across Process Steps', pad=20)
        ax.set_xlabel('Process Step')
        ax.set_ylabel('')
        ax.set_zlabel('Volume (mL)')
        
        # Set x-axis labels
        ax.set_xticks(xpos + dx/2)
        ax.set_xticklabels(volume_data['Category'])
        
        # Add legend with fancy box
        legend = ax.legend(['Solid', 'Liquid'], 
                          bbox_to_anchor=(1.15, 0.5),
                          loc='center left',
                          bbox_transform=ax.transAxes,
                          fancybox=True, 
                          shadow=True,
                          framealpha=1,
                          edgecolor='black')
        legend.get_frame().set_facecolor('white')
        
        # Add value labels
        for i in range(len(xpos)):
            solid_height = solid_heights[i]
            liquid_height = liquid_heights[i]
            
            # Label for solid portion
            ax.text(xpos[i] + dx[i]/2, ypos[i], solid_height/2, 
                   f'{solid_height:.2f}',
                   horizontalalignment='center',
                   verticalalignment='center')
            
            # Label for liquid portion (if present)
            if liquid_height > 0:
                ax.text(xpos[i] + dx[i]/2, ypos[i], solid_height + liquid_height/2,
                       f'{liquid_height:.2f}',
                       horizontalalignment='center',
                       verticalalignment='center')
        
        # Adjust view angle for better visualization
        ax.view_init(elev=20, azim=45)
        plt.tight_layout()
        st.pyplot(fig)

    # Component comparison visualization
    st.subheader("Component Concentration Comparison")

    # Only create the comparison chart if there are components to compare
    components = [drug_name] + excipient_names
    pre_concentrations = [drug_conc] + excipient_concentrations
    post_concentrations = [drug_conc_after] + excipient_conc_after
    
    if components:
        fig = plt.figure(figsize=(12, 6))
        ax = fig.add_subplot(111, projection='3d')
        
        # Define positions
        xpos = np.arange(len(components))
        ypos = np.array([0, 1])  # Two positions for pre and post
        zpos = 0
        
        # Define dimensions
        dx = 0.3
        dy = 0.3
        
        # Create meshgrid for positions
        xpos_mesh, ypos_mesh = np.meshgrid(xpos, ypos)
        xpos_mesh = xpos_mesh.flatten()
        ypos_mesh = ypos_mesh.flatten()
        
        # Create heights array
        heights = np.array(pre_concentrations + post_concentrations)
        
        # Create colors array
        colors = ['royalblue' if y == 0 else 'darkorange' for y in ypos_mesh]
        
        # Plot 3D bars
        bars = ax.bar3d(xpos_mesh, ypos_mesh, np.zeros_like(heights),
                       dx, dy, heights, color=colors, alpha=0.8, shade=True)
        
        # Customize the plot
        ax.set_title('Component Concentration Comparison', pad=20)
        ax.set_xlabel('Components')
        ax.set_ylabel('Stage')
        ax.set_zlabel('Concentration (mg/mL)')
        
        # Set axis labels
        ax.set_xticks(xpos)
        ax.set_xticklabels(components, rotation=45)
        ax.set_yticks([0, 1])
        ax.set_yticklabels(['Pre-Lyophilization', 'Post-Reconstitution'])
        
        # Add legend with fancy box
        legend = ax.legend(['Pre-Lyophilization', 'Post-Reconstitution'],
                          bbox_to_anchor=(1.15, 0.5),
                          loc='center left',
                          bbox_transform=ax.transAxes,
                          fancybox=True, 
                          shadow=True,
                          framealpha=1,
                          edgecolor='black')
        legend.get_frame().set_facecolor('white')
        
        # Add value labels
        for i, height in enumerate(heights):
            ax.text(xpos_mesh[i], ypos_mesh[i], height,
                   f'{height:.2f}',
                   horizontalalignment='center',
                   verticalalignment='bottom')
        
        # Adjust view angle for better visualization
        ax.view_init(elev=20, azim=45)
        plt.tight_layout()
        st.pyplot(fig)
    else:
        st.write("No components to compare.")

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