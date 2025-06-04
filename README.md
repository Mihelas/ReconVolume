# ReconVolume - Lyophilized Drug Product Reconstitution Calculator

## Description
This Streamlit application calculates the required diluent volume for reconstitution of lyophilized drug products, accounting for solid content displacement and density corrections. It provides an interactive interface for pharmaceutical scientists to determine precise reconstitution parameters and visualize the mass and volume distributions across different process steps.

## Features
- Dynamic excipient management with customizable components
- Real-time calculations of reconstitution parameters
- Interactive data visualization
- Comprehensive result tables
- Support for different vial sizes
- Density-corrected calculations

## Application Guide

### Input Parameters

#### Pre-Lyophilization Parameters
- **Drug Name**: Name identifier for the drug
- **Drug Concentration**: Concentration in mg/mL
- **Filling Volume**: Initial volume in mL
- **Density**: Solution density prior to lyophilization in mg/mL

#### Excipients Management
- Add multiple excipients using the "+ Add Excipient" button
- Choose from predefined excipients or add custom ones
- Specify concentration for each excipient

#### Reconstitution Parameters
- **Target Volume**: Desired final volume after reconstitution
- **Reconstituted Density**: Expected density after reconstitution
- **Diluent Density**: Density of the reconstitution medium (typically WFI)

#### Vial Information
- Select from available vial sizes (2R, 10R, 20R)
- Brim fill volumes are automatically populated

### Outputs

#### Calculation Results

##### Pre-Lyophilization Composition
- Component-wise concentrations and amounts
- Total solids content
- WFI content

##### Post-Reconstitution Composition
- Final concentrations of all components
- Required diluent volume

#### Visualizations

##### Mass Distribution
- Stacked bar chart showing solid and liquid masses
- Values in grams
- Three process steps:
  * Liquid+Solid
  * Solid
  * Recon+Solid

##### Volume Distribution
- Stacked bar chart showing solid and liquid volumes
- Values in mL
- Three process steps:
  * Liquid+Solid
  * Solid
  * Recon+Solid

## Excel Export Format

The downloaded Excel file (`lyophilization_calculation_YYYYMMDD_HHMMSS.xlsx`) contains the following sheets:

1. **Pre-Lyophilization**
   - Complete composition table
   - Components, concentrations, and amounts per vial

2. **Post-Reconstitution**
   - Final composition table
   - Components and their final concentrations

3. **Reconstitution Details**
   - Key calculation parameters
   - Final volumes and masses

4. **Component Comparison**
   - Side-by-side comparison of concentrations
   - Pre-lyophilization vs post-reconstitution values

5. **Visualizations**
   - Mass distribution chart
   - Volume distribution chart
   - Component concentration comparison chart
   - All charts include data labels and legends

## Calculations and Methodology

1. **Pre-Lyophilization Stage**
   - Total solid content calculation
   - Initial mass and volume calculations

2. **Mass Balance Principle**
   - Conservation of solid content
   - Per vial calculations

3. **Reconstitution Calculations**
   - Target volume considerations
   - Density corrections
   - Diluent volume determination

4. **Volume Displacement**
   - Solid content displacement effects
   - Final volume adjustments

## Support

For technical support or scientific questions, please contact Nicholas Michelarakis.

## Version History
v1.0 (June 2025): Initial release with core calculation features and Excel export functionality

