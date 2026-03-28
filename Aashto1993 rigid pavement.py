import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# =============================
# UNIT CONVERSION
# =============================
def MPa_to_psi(x):
    return x * 145.038

def kN_to_psi(x):
    return x * 0.145038

# =============================
# AASHTO FUNCTION
# =============================
def aashto_rigid_design(W18, Zr, So, delta_PSI, Pt, Sc, Cd, J, Ec):

    def equation(D):
        term1 = Zr * So
        term2 = 7.35 * np.log10(D + 1) - 0.06

        term3 = np.log10(delta_PSI / (4.5 - 1.5))
        term3 = term3 / (1 + (1.624e7 / (D + 1)**8.46))

        numerator = Sc * Cd * (D**0.75 - 1.132)
        denominator = 215.63 * J * (D**0.75 - (18.42 / Ec**0.25))

        term4 = (4.22 - 0.32 * Pt) * np.log10(numerator / denominator)

        return term1 + term2 + term3 + term4 - np.log10(W18)

    D = 5.0
    for _ in range(1000):
        f = equation(D)
        df = (equation(D + 0.01) - f) / 0.01
        D = D - f / df
        if abs(f) < 1e-6:
            break

    return D


# =============================
# DOWEL DESIGN (simple rule)
# =============================
def dowel_design(D):
    diameter = D / 8        # inch
    spacing = 300           # mm
    length = 450            # mm
    return diameter, spacing, length

# =============================
# TIE BAR DESIGN
# =============================
def tie_bar_design(D):
    diameter = 12  # mm
    length = 600   # mm
    spacing = 750  # mm
    return diameter, length, spacing

# =============================
# UI DESIGN
# =============================
st.set_page_config(layout="wide")

st.title("🚧 AASHTO 1993 Pavement Design (Advanced)")

col1, col2 = st.columns([1, 2])

with col1:
    st.header("📥 Input (SI Unit)")

    W18 = st.slider("Traffic W18", 1e5, 1e8, 5e6)
    Zr = st.slider("Zr", -3.0, 0.0, -1.282)
    So = st.slider("So", 0.2, 0.5, 0.35)

    delta_PSI = st.slider("ΔPSI", 1.0, 3.0, 1.5)
    Pt = st.slider("Pt", 1.5, 3.0, 2.5)

    Sc_MPa = st.slider("Sc (MPa)", 3.0, 6.0, 4.5)
    Ec_MPa = st.slider("Ec (MPa)", 20000, 40000, 30000)

    Cd = st.slider("Cd", 0.7, 1.2, 1.0)
    J = st.slider("J", 2.0, 4.5, 3.2)

    k = st.slider("Subgrade k (MN/m³)", 20, 150, 50)

# =============================
# CONVERT UNIT
# =============================
Sc = MPa_to_psi(Sc_MPa)
Ec = MPa_to_psi(Ec_MPa)

# =============================
# CALCULATION
# =============================
D = aashto_rigid_design(W18, Zr, So, delta_PSI, Pt, Sc, Cd, J, Ec)

dowel = dowel_design(D)
tie = tie_bar_design(D)

# =============================
# OUTPUT
# =============================
with col2:
    st.header("📊 Result")

    st.metric("Thickness (inch)", f"{D:.2f}")
    st.metric("Thickness (cm)", f"{D*2.54:.2f}")

    st.subheader("🪵 Dowel Design")
    st.write(f"Diameter ≈ {dowel[0]:.2f} inch")
    st.write(f"Spacing = {dowel[1]} mm")
    st.write(f"Length = {dowel[2]} mm")

    st.subheader("🔩 Tie Bar Design")
    st.write(f"Diameter = {tie[0]} mm")
    st.write(f"Length = {tie[1]} mm")
    st.write(f"Spacing = {tie[2]} mm")

    st.subheader("🌱 Subgrade")
    st.write(f"k = {k} MN/m³")

# =============================
# GRAPH
# =============================
st.subheader("📈 D vs W18")

W_range = np.linspace(1e5, 1e8, 20)
D_vals = [aashto_rigid_design(w, Zr, So, delta_PSI, Pt, Sc, Cd, J, Ec) for w in W_range]

fig, ax = plt.subplots()
ax.plot(W_range, D_vals)
ax.set_xlabel("W18")
ax.set_ylabel("Thickness (inch)")

st.pyplot(fig)
