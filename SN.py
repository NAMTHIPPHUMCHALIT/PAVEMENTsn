import streamlit as st
import numpy as np
from scipy.optimize import fsolve
import pandas as pd

# Page configuration
st.set_page_config(page_title="AASHTO 1993 Pavement Design", layout="wide")

st.title("🛣️ AASHTO 1993 Pavement Design Calculator")
st.markdown("Calculate Structural Number (SN) for flexible pavement design")

# Sidebar for inputs
st.sidebar.header("📊 Design Parameters")

# Traffic
st.sidebar.subheader("Traffic Data")
w18 = st.sidebar.number_input(
    "Design ESALs (W₁₈) in millions",
    min_value=0.01,
    value=5.0,
    step=0.1,
    help="Predicted 18-kip equivalent single axle loads"
)

# Reliability
st.sidebar.subheader("Reliability")
reliability = st.sidebar.slider(
    "Reliability (R) %",
    min_value=50,
    max_value=99,
    value=95,
    help="Level of confidence in the design"
)

# Standard deviation
so = st.sidebar.number_input(
    "Overall Standard Deviation (So)",
    min_value=0.30,
    max_value=0.50,
    value=0.45,
    step=0.01,
    help="Typically 0.45 for flexible pavements"
)

# Serviceability
st.sidebar.subheader("Serviceability")
pi = st.sidebar.number_input(
    "Initial Serviceability (pi)",
    min_value=3.0,
    max_value=5.0,
    value=4.5,
    step=0.1
)

pt = st.sidebar.number_input(
    "Terminal Serviceability (pt)",
    min_value=1.5,
    max_value=3.0,
    value=2.5,
    step=0.1
)

# Subgrade
st.sidebar.subheader("Subgrade Properties")
mr = st.sidebar.number_input(
    "Effective Resilient Modulus (MR) in psi",
    min_value=1000,
    max_value=20000,
    value=7500,
    step=500,
    help="Subgrade resilient modulus"
)

# Calculate button
calculate = st.sidebar.button("🔢 Calculate SN", type="primary")

# ZR values based on reliability
def get_zr(reliability):
    """Get standard normal deviate for given reliability"""
    zr_values = {
        50: 0.000, 60: -0.253, 70: -0.524, 75: -0.674,
        80: -0.841, 85: -1.037, 90: -1.282, 95: -1.645,
        99: -2.327, 99.9: -3.090
    }
    return zr_values.get(reliability, -1.645)

# AASHTO 1993 equation
def aashto_equation(sn, w18, zr, so, delta_psi, mr):
    """
    AASHTO 1993 flexible pavement design equation
    This function returns the difference between calculated and input W18
    """
    term1 = zr * so
    term2 = 9.36 * np.log10(sn + 1) - 0.20
    term3 = np.log10(delta_psi / (4.2 - 1.5)) / (0.40 + 1094 / (sn + 1)**5.19)
    term4 = 2.32 * np.log10(mr) - 8.07
    
    log_w18_calc = term1 + term2 + term3 + term4
    w18_calc = 10**log_w18_calc
    
    return w18_calc - w18 * 1e6  # Convert millions to units

# Layer coefficient guidelines
def get_layer_coefficients():
    """Display typical layer coefficient values"""
    st.subheader("📋 Typical Layer Coefficients (AASHTO 1993)")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Surface Course (a₁)**")
        data_surface = {
            "Material": ["Hot Mix Asphalt", "Surface Treatment"],
            "a₁ Range": ["0.35 - 0.44", "0.20 - 0.30"]
        }
        st.table(pd.DataFrame(data_surface))
    
    with col2:
        st.markdown("**Base Course (a₂)**")
        data_base = {
            "Material": ["Crushed Stone", "Cement Treated", "Asphalt Treated"],
            "a₂ Range": ["0.10 - 0.14", "0.20 - 0.28", "0.30 - 0.40"]
        }
        st.table(pd.DataFrame(data_base))
    
    st.markdown("**Subbase Course (a₃)**")
    data_subbase = {
        "Material": ["Granular Subbase", "Cement Treated", "Lime Treated"],
        "a₃ Range": ["0.08 - 0.12", "0.15 - 0.20", "0.10 - 0.15"]
    }
    st.table(pd.DataFrame(data_subbase))

# Main calculation
if calculate:
    st.header("📈 Calculation Results")
    
    # Get ZR value
    zr = get_zr(reliability)
    delta_psi = pi - pt
    
    # Display input summary
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Design ESALs", f"{w18:.2f} M")
        st.metric("Reliability", f"{reliability}%")
    
    with col2:
        st.metric("ZR", f"{zr:.3f}")
        st.metric("ΔPSI", f"{delta_psi:.1f}")
    
    with col3:
        st.metric("So", f"{so:.2f}")
        st.metric("MR", f"{mr:,} psi")
    
    # Solve for SN
    try:
        # Initial guess for SN
        sn_initial = 3.0
        
        # Solve equation
        sn_solution = fsolve(
            aashto_equation,
            sn_initial,
            args=(w18, zr, so, delta_psi, mr)
        )[0]
        
        if sn_solution > 0:
            st.success(f"### 🎯 Required Structural Number (SN) = **{sn_solution:.2f}**")
            
            # Layer thickness calculation section
            st.header("🏗️ Pavement Layer Thickness Design")
            
            st.info("**Formula**: SN = a₁×D₁ + a₂×D₂×m₂ + a₃×D₃×m₃")
            st.markdown("Where: aᵢ = layer coefficient, Dᵢ = thickness (inches), mᵢ = drainage coefficient")
            
            # Input layer coefficients
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("**Surface Layer**")
                a1 = st.number_input("a₁ (Surface)", 0.20, 0.50, 0.40, 0.01)
                d1 = st.number_input("D₁ (inches)", 1.0, 12.0, 4.0, 0.5)
            
            with col2:
                st.markdown("**Base Layer**")
                a2 = st.number_input("a₂ (Base)", 0.05, 0.40, 0.14, 0.01)
                m2 = st.number_input("m₂ (drainage)", 0.50, 1.20, 1.00, 0.05)
                d2 = st.number_input("D₂ (inches)", 0.0, 24.0, 6.0, 0.5)
            
            with col3:
                st.markdown("**Subbase Layer**")
                a3 = st.number_input("a₃ (Subbase)", 0.05, 0.25, 0.11, 0.01)
                m3 = st.number_input("m₃ (drainage)", 0.50, 1.20, 1.00, 0.05)
                d3 = st.number_input("D₃ (inches)", 0.0, 24.0, 8.0, 0.5)
            
            # Calculate provided SN
            sn_provided = a1 * d1 + a2 * d2 * m2 + a3 * d3 * m3
            
            st.markdown("---")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Required SN", f"{sn_solution:.2f}")
            with col2:
                st.metric("Provided SN", f"{sn_provided:.2f}")
            with col3:
                difference = sn_provided - sn_solution
                st.metric("Difference", f"{difference:.2f}", 
                         delta="✓ OK" if difference >= 0 else "✗ Insufficient")
            
            if sn_provided >= sn_solution:
                st.success("✅ Design is adequate! Provided SN meets the requirement.")
            else:
                st.error("⚠️ Design is inadequate! Increase layer thicknesses.")
            
        else:
            st.error("Invalid result. Please check input parameters.")
            
    except Exception as e:
        st.error(f"Calculation error: {str(e)}")
        st.info("Try adjusting input parameters.")

else:
    st.info("👈 Enter design parameters in the sidebar and click 'Calculate SN'")
    get_layer_coefficients()

# Additional information
st.markdown("---")
with st.expander("ℹ️ About AASHTO 1993 Design Method"):
    st.markdown("""
    The AASHTO 1993 pavement design method uses the following equation:
    
    $$
    \log_{10}(W_{18}) = Z_R \cdot S_0 + 9.36 \cdot \log_{10}(SN+1) - 0.20 + \\frac{\log_{10}[\Delta PSI/(4.2-1.5)]}{0.40 + \\frac{1094}{(SN+1)^{5.19}}} + 2.32 \cdot \log_{10}(M_R) - 8.07
    $$
    
    **Key Parameters:**
    - **W₁₈**: Predicted 18-kip ESALs
    - **ZR**: Standard normal deviate (based on reliability)
    - **So**: Overall standard deviation (0.45 typical)
    - **SN**: Structural Number (to be calculated)
    - **ΔPSI**: Change in serviceability (pi - pt)
    - **MR**: Effective resilient modulus of subgrade (psi)
    """)

st.markdown("---")
st.caption("Developed for AASHTO 1993 Flexible Pavement Design | Educational Purpose")
