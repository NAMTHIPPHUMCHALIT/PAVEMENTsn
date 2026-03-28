import streamlit as st
import math
import numpy as np
import os

# ✅ FIX matplotlib
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet

# =============================
# AASHTO SLAB DESIGN
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


def design_slab(W18, R, Ec, Sc, k):
    ZR_map = {85: -1.037, 90: -1.282, 95: -1.645}
    ZR = ZR_map.get(R, -1.282)

    S0 = 0.35
    DPSI = 4.5 - 2.5
    target = math.log10(W18 * 1e6)

    Ec = Ec * 145.038
    Sc = Sc * 145.038
    k = k * 3.6839

    lo, hi = 1, 20
    for _ in range(100):
        mid = (lo + hi) / 2
        val = calc_log_W18(mid, ZR, S0, DPSI, Ec, Sc, 3.2, 1.0, k, 2.5)

        if val < target:
            lo = mid
        else:
            hi = mid

    D = math.ceil(mid * 4) / 4
    return round(D * 25.4)


# =============================
# LAYER DESIGN (NEW 🔥)
# =============================
def design_layers(D, CBR):
    # Base thickness (rule of thumb)
    if CBR < 5:
        base = 250
    elif CBR < 10:
        base = 200
    else:
        base = 150

    # Subbase thickness
    if CBR < 5:
        subbase = 200
    elif CBR < 10:
        subbase = 150
    else:
        subbase = 100

    total = D + base + subbase

    return base, subbase, total


# =============================
# DRAW LAYERS (NEW 🔥)
# =============================
def draw_layers(D, base, subbase):
    layers = ["PCC Slab", "Base", "Subbase"]
    thickness = [D, base, subbase]

    plt.figure(figsize=(4,6))
    plt.barh(layers, thickness)
    plt.xlabel("Thickness (mm)")
    plt.title("Pavement Structure")

    plt.savefig("layers.png")
    plt.close()


# =============================
# PDF
# =============================
def generate_pdf(D, base, subbase, total):
    doc = SimpleDocTemplate("AASHTO_Report.pdf")
    styles = getSampleStyleSheet()

    story = []
    story.append(Paragraph("AASHTO 1993 Pavement Design", styles["Title"]))
    story.append(Spacer(1, 20))

    story.append(Paragraph(f"PCC Slab = {D} mm", styles["Normal"]))
    story.append(Paragraph(f"Base = {base} mm", styles["Normal"]))
    story.append(Paragraph(f"Subbase = {subbase} mm", styles["Normal"]))
    story.append(Paragraph(f"Total Thickness = {total} mm", styles["Normal"]))

    if os.path.exists("layers.png"):
        story.append(Spacer(1, 20))
        story.append(Image("layers.png", width=300, height=400))

    doc.build(story)


# =============================
# UI
# =============================
st.title("🛣️ Pavement Design (Layered)")

W18 = st.number_input("W18 (Million ESAL)", 15.0)
R = st.selectbox("Reliability", [85, 90, 95])
k = st.number_input("k (MN/m³)", 54.0)
CBR = st.number_input("CBR (%)", 8)

Ec = st.number_input("Ec (MPa)", 27600)
Sc = st.number_input("Sc (MPa)", 4.8)

if st.button("Run Design"):

    # slab
    D = design_slab(W18, R, Ec, Sc, k)

    # layers
    base, subbase, total = design_layers(D, CBR)

    st.success(f"PCC Slab = {D} mm")
    st.info(f"Base = {base} mm")
    st.info(f"Subbase = {subbase} mm")
    st.warning(f"Total Thickness = {total} mm")

    # plot
    draw_layers(D, base, subbase)
    st.image("layers.png")

    # pdf
    generate_pdf(D, base, subbase, total)

    with open("AASHTO_Report.pdf", "rb") as f:
        st.download_button("Download PDF", f)
