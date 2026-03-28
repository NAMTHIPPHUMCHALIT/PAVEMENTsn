import streamlit as st
import math
import numpy as np
import os

# matplotlib fix
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as patches

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet

# =============================
# SLAB DESIGN
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

    target = math.log10(W18 * 1e6)

    Ec = Ec * 145.038
    Sc = Sc * 145.038
    k = k * 3.6839

    lo, hi = 1, 20
    for _ in range(100):
        mid = (lo + hi) / 2
        val = calc_log_W18(mid, ZR, 0.35, 2.0, Ec, Sc, 3.2, 1.0, k, 2.5)

        if val < target:
            lo = mid
        else:
            hi = mid

    D = math.ceil(mid * 4) / 4
    return round(D * 25.4)


# =============================
# LAYER DESIGN
# =============================
def design_layers(D, CBR):
    if CBR < 3:
        base, subbase = 250, 200
    elif CBR < 8:
        base, subbase = 200, 150
    elif CBR < 15:
        base, subbase = 150, 100
    else:
        base, subbase = 120, 80

    return base, subbase, D + base + subbase


# =============================
# DRAW WITH LEGEND 🔥
# =============================
def draw_cross_section(D, base, subbase):

    layers = [
        ("PCC Slab", D, "#90CAF9"),
        ("Base Layer", base, "#A5D6A7"),
        ("Subbase Layer", subbase, "#FFE082"),
        ("Subgrade Soil", 300, "#D7CCC8")
    ]

    fig, ax = plt.subplots(figsize=(6,6))

    y = 0
    for name, thk, color in layers:
        rect = patches.Rectangle((0, y), 10, thk, facecolor=color)
        ax.add_patch(rect)

        ax.text(5, y + thk/2,
                f"{name}\n{thk} mm",
                ha='center', va='center', fontsize=10, weight='bold')

        y += thk

    ax.set_xlim(0, 10)
    ax.set_ylim(0, y)
    ax.invert_yaxis()
    ax.axis('off')

    plt.savefig("cross_section.png", dpi=150, bbox_inches="tight")
    plt.close()


# =============================
# DESCRIPTION TEXT 🔥
# =============================
def get_layer_description(D, base, subbase):
    return f"""
โครงสร้างผิวทางคอนกรีต (Rigid Pavement) นี้ประกอบด้วย:

1. PCC Slab หนา {D} mm ทำหน้าที่รับน้ำหนักจราจรหลัก
2. Base หนา {base} mm ช่วยกระจายแรงและเพิ่มความแข็งแรง
3. Subbase หนา {subbase} mm ปรับปรุงชั้นรองรับและลดการทรุดตัว
4. Subgrade คือดินเดิม ทำหน้าที่รองรับโครงสร้างทั้งหมด

โครงสร้างนี้ออกแบบตามแนวทาง AASHTO 1993
"""


# =============================
# PDF
# =============================
def generate_pdf(D, base, subbase, total, desc):
    doc = SimpleDocTemplate("AASHTO_Report.pdf")
    styles = getSampleStyleSheet()

    story = []
    story.append(Paragraph("Pavement Design Report", styles["Title"]))
    story.append(Spacer(1, 20))

    story.append(Paragraph(f"PCC = {D} mm", styles["Normal"]))
    story.append(Paragraph(f"Base = {base} mm", styles["Normal"]))
    story.append(Paragraph(f"Subbase = {subbase} mm", styles["Normal"]))
    story.append(Paragraph(f"Total = {total} mm", styles["Normal"]))

    story.append(Spacer(1, 20))
    story.append(Paragraph(desc, styles["Normal"]))

    if os.path.exists("cross_section.png"):
        story.append(Spacer(1, 20))
        story.append(Image("cross_section.png", width=350, height=350))

    doc.build(story)


# =============================
# UI
# =============================
st.title("🛣️ Pavement Layer Design (AASHTO 1993)")

W18 = st.number_input("W18 (Million ESAL)", 15.0)
R = st.selectbox("Reliability", [85, 90, 95])
k = st.number_input("k (MN/m³)", 54.0)
CBR = st.number_input("CBR (%)", 8)

Ec = st.number_input("Ec (MPa)", 27600)
Sc = st.number_input("Sc (MPa)", 4.8)

if st.button("🚀 Run Design"):

    D = design_slab(W18, R, Ec, Sc, k)
    base, subbase, total = design_layers(D, CBR)

    st.success(f"PCC = {D} mm")
    st.info(f"Base = {base} mm")
    st.info(f"Subbase = {subbase} mm")
    st.warning(f"Total = {total} mm")

    # draw
    draw_cross_section(D, base, subbase)
    st.image("cross_section.png")

    # description
    desc = get_layer_description(D, base, subbase)
    st.markdown("### 📌 คำอธิบายโครงสร้าง")
    st.write(desc)

    # pdf
    generate_pdf(D, base, subbase, total, desc)

    with open("AASHTO_Report.pdf", "rb") as f:
        st.download_button("📄 Download PDF", f)
