import streamlit as st
import math
import numpy as np
import matplotlib.pyplot as plt
import os
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

# =============================
# AASHTO FUNCTION
# =============================
def calc_log_W18(D, ZR, S0, DPSI, Ec, Sc, J, Cd, k, pt):
    try:
        A = ZR * S0
        B = 7.35 * math.log10(D + 1) - 0.06
        C = math.log10(DPSI / 3) / (1 + (1.624e7 / (D + 1)**8.46))
        ek = (Ec / k) ** 0.25
        inner = D**0.75 - 18.42 / ek

        if inner <= 0:
            return -999

        D_part = (4.22 - 0.32 * pt) * math.log10(
            (Sc * Cd * (D**0.75 - 1.132)) / (215.63 * J * inner)
        )

        return A + B + C + D_part
    except:
        return -999


# =============================
# DESIGN
# =============================
def design_slab(W18, R, S0, p0, pt, Ec, Sc, J, Cd, k):

    ZR_map = {85: -1.037, 90: -1.282, 95: -1.645}
    ZR = ZR_map.get(R, -1.282)

    DPSI = p0 - pt
    target = math.log10(W18 * 1e6)

    Ec = Ec * 145.038
    Sc = Sc * 145.038
    k = k * 3.6839

    lo, hi = 1, 20
    for _ in range(100):
        mid = (lo + hi) / 2
        val = calc_log_W18(mid, ZR, S0, DPSI, Ec, Sc, J, Cd, k, pt)

        if val < target:
            lo = mid
        else:
            hi = mid

    D = math.ceil(mid * 4) / 4
    return round(D * 25.4)


# =============================
# VALIDATION
# =============================
def validate_inputs(W18, k, CBR):
    warnings = []

    if W18 <= 0:
        warnings.append("❌ W18 ต้องมากกว่า 0")

    if k < 20:
        warnings.append("⚠️ k ต่ำมาก อาจทำให้ pavement หนามาก")

    if CBR < 3:
        warnings.append("⚠️ CBR ต่ำมาก ต้องปรับปรุงดิน")

    return warnings


# =============================
# PLOT
# =============================
def plot_graph(W18, D):
    D_range = np.linspace(100, 400, 100)
    W = (D_range / D) ** 4 * W18

    plt.figure()
    plt.plot(D_range, W)
    plt.scatter([D], [W18])
    plt.xlabel("Thickness (mm)")
    plt.ylabel("W18 (Million)")
    plt.grid()

    plt.savefig("plot.png")
    plt.close()


# =============================
# PDF
# =============================
def generate_pdf(D):
    doc = SimpleDocTemplate("AASHTO_Report.pdf")
    styles = getSampleStyleSheet()

    story = []
    story.append(Paragraph("AASHTO 1993 Design Report", styles["Title"]))
    story.append(Spacer(1, 20))
    story.append(Paragraph(f"Slab Thickness = {D} mm", styles["Normal"]))

    doc.build(story)


# =============================
# STREAMLIT UI
# =============================
st.set_page_config(page_title="AASHTO 1993", layout="centered")

st.title("🛣️ AASHTO 1993 Rigid Pavement Design")

# INPUT
W18 = st.number_input("W18 (Million ESAL)", value=15.0)
R = st.selectbox("Reliability (%)", [85, 90, 95])
k = st.number_input("Subgrade k (MN/m³)", value=54.0)
CBR = st.number_input("CBR (%)", value=8)

st.subheader("Material Properties")
Ec = st.number_input("Ec (MPa)", value=27600)
Sc = st.number_input("Sc (MPa)", value=4.8)

# RUN
if st.button("🚀 Run Design"):

    warnings = validate_inputs(W18, k, CBR)

    for w in warnings:
        st.warning(w)

    D = design_slab(W18, R, 0.35, 4.5, 2.5, Ec, Sc, 3.2, 1.0, k)

    st.success(f"✅ Slab Thickness = {D} mm")

    # Plot
    plot_graph(W18, D)
    st.image("plot.png")

    # PDF
    generate_pdf(D)

    with open("AASHTO_Report.pdf", "rb") as f:
        st.download_button("📄 Download PDF", f, file_name="AASHTO_Report.pdf")
