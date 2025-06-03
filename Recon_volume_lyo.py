import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(page_title="Lyophilized Drug Product Reconstitution Calculator", layout="wide")

st.title("Lyophilized Drug Product Reconstitution Calculator")

st.markdown("""
This application calculates the required diluent volume for reconstitution of lyophilized drug products,
accounting for solid content displacement and density corrections.
""")

# Create two columns for input parameters
col1, col2 = st.columns(2)

with col1:
    st.subheader("Pre-Lyophilization Parameters")
    
    # Drug and excipient inputs
    st.markdown("##### Drug and Excipients")
    drug_name = st.text_input("Drug Name", value="SARxxxx")
    drug_conc = st.number_input("Drug Concentration (mg/mL)", value=8.0, step=0.1)
    
    # Create expandable section for excipients
    with st.expander("Excipients"):
        hist_conc = st.number_input("Histidine Concentration (mg/mL)", value=1.15, step=0.01)
        hist_hcl_conc = st.number_input("Histidine HCl Concentration (mg/mL)", value=0.54, step=0.01)
        sucrose_conc = st.number_input("Sucrose Concentration (mg/mL)", value=80.0, step=0.1)
        ps80_conc = st.number_input("PS80 Concentration (mg/mL)", value=0.5, step=0.01)
    
    # Process parameters
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

# Calculate total solid content
total_solid_conc = drug_conc + hist_conc + hist_hcl_conc + sucrose_conc + ps80_conc
wfi_conc = density_pre_lyo - total_solid_conc

# Calculate per vial amounts
drug_amount = drug_conc * filling_volume
hist_amount = hist_conc * filling_volume
hist_hcl_amount = hist_hcl_conc * filling_volume
sucrose_amount = sucrose_conc * filling_volume
ps80_amount = ps80_conc * filling_volume
total_solid_amount = total_solid_conc * filling_volume
wfi_amount = wfi_conc * filling_volume

# Calculate reconstitution parameters
theoretical_solid_mass = total_solid_amount  # mg/vial
diluent_mass_needed = (recon_volume * density_post_recon) - theoretical_solid_mass  # mg/vial
diluent_volume_needed = diluent_mass_needed / diluent_density  # mL/vial

# Calculate concentrations after reconstitution
drug_conc_after = drug_amount / recon_volume
hist_conc_after = hist_amount / recon_volume
hist_hcl_conc_after = hist_hcl_amount / recon_volume
sucrose_conc_after = sucrose_amount / recon_volume
ps80_conc_after = ps80_amount / recon_volume
wfi_conc_after = (wfi_amount + diluent_mass_needed) / recon_volume

# Display results
st.header("Calculation Results")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Pre-Lyophilization Composition")
    
    # Create a DataFrame for pre-lyophilization composition
    pre_lyo_data = {
        "Component": [drug_name, "Histidine", "Histidine HCl", "Sucrose", "PS80", "Total Solids", "WFI"],
        "Concentration (mg/mL)": [drug_conc, hist_conc, hist_hcl_conc, sucrose_conc, ps80_conc, total_solid_conc, wfi_conc],
        "Amount per Vial (mg)": [drug_amount, hist_amount, hist_hcl_amount, sucrose_amount, ps80_amount, total_solid_amount, wfi_amount]
    }
    
    pre_lyo_df = pd.DataFrame(pre_lyo_data)
    st.dataframe(pre_lyo_df)

with col2:
    st.subheader("Post-Reconstitution Composition")
    
    # Create a DataFrame for post-reconstitution composition
    post_recon_data = {
        "Component": [drug_name, "Histidine", "Histidine HCl", "Sucrose", "PS80", "WFI"],
        "Concentration (mg/mL)": [drug_conc_after, hist_conc_after, hist_hcl_conc_after, sucrose_conc_after, ps80_conc_after, wfi_conc_after]
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

tab1, tab2 = st.tabs(["Composition Comparison", "Reconstitution Diagram"])

with tab1:
    # Create a bar chart comparing pre and post reconstitution concentrations
    fig, ax = plt.subplots(figsize=(10, 6))
    
    components = [drug_name, "Histidine", "Histidine HCl", "Sucrose", "PS80"]
    x = np.arange(len(components))
    width = 0.35
    
    ax.bar(x - width/2, [drug_conc, hist_conc, hist_hcl_conc, sucrose_conc, ps80_conc], 
           width, label='Pre-Lyophilization', color='royalblue')
    ax.bar(x + width/2, [drug_conc_after, hist_conc_after, hist_hcl_conc_after, sucrose_conc_after, ps80_conc_after], 
           width, label='Post-Reconstitution', color='darkorange')
    
    ax.set_ylabel('Concentration (mg/mL)')
    ax.set_title('Component Concentration Comparison')
    ax.set_xticks(x)
    ax.set_xticklabels(components, rotation=45)
    ax.legend()
    
    plt.tight_layout()
    st.pyplot(fig)

with tab2:
    # Create pie charts for the reconstitution process
    fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(15, 5))
    
    # Pre-lyophilization
    ax1.pie([total_solid_conc, wfi_conc], labels=["Solids", "WFI"], 
            colors=['#66b3ff', '#99ffcc'], autopct='%1.1f%%')
    ax1.set_title("Pre-Lyophilization")
    
    # Lyophilized cake
    solid_components = [drug_conc, hist_conc, hist_hcl_conc, sucrose_conc, ps80_conc]
    ax2.pie(solid_components, 
            labels=[drug_name, "Histidine", "Histidine HCl", "Sucrose", "PS80"],
            colors=['#ff9999', '#ffcc99', '#ffff99', '#ccff99', '#99ccff'],
            autopct='%1.1f%%')
    ax2.set_title("Lyophilized Cake")
    
    # Reconstituted solution
    recon_components = [drug_conc_after, hist_conc_after, hist_hcl_conc_after, 
                       sucrose_conc_after, ps80_conc_after, wfi_conc_after]
    ax3.pie(recon_components,
            labels=[drug_name, "Histidine", "Histidine HCl", "Sucrose", "PS80", "WFI"],
            colors=['#ff9999', '#ffcc99', '#ffff99', '#ccff99', '#99ccff', '#99ffcc'],
            autopct='%1.1f%%')
    ax3.set_title("Reconstituted Solution")
    
    plt.tight_layout()
    st.pyplot(fig)

# Add a section for notes and explanations
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