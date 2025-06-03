import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="Lyophilized Drug Product Reconstitution Calculator", layout="wide")

st.title("Lyophilized Drug Product Reconstitution Calculator")

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
    
    filling_volume = st.number_input("Filling Volume (mL)", value=8.0, step=0.1)
    density_pre_lyo = st.number_input("Density Prior to Lyophilization (mg/mL)", value=1030.0, step=1.0)

with col2:
    st.subheader("Reconstitution Parameters")
    recon_volume = st.number_input("Target Volume After Reconstitution (mL)", value=4.0, step=0.1)
    density_post_recon = st.number_input("Density After Reconstitution (mg/mL)", value=1030.0, step=1.0)
    diluent_density = st.number_input("Diluent Density (mg/mL)", value=998.2, step=0.1)

# Basic calculations
total_solid_conc = drug_conc + hist_conc + hist_hcl_conc + sucrose_conc + ps80_conc
theoretical_solid_mass = total_solid_conc * filling_volume
diluent_mass_needed = (recon_volume * density_post_recon) - theoretical_solid_mass
diluent_volume_needed = diluent_mass_needed / diluent_density

# Display results
st.header("Results")
st.write(f"Total Solid Content: {total_solid_conc:.2f} mg/mL")
st.write(f"Theoretical Solid Mass: {theoretical_solid_mass:.2f} mg/vial")
st.write(f"Required Diluent Volume: {diluent_volume_needed:.4f} mL/vial")