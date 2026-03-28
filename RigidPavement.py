import streamlit as st
import math
import numpy as np
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as patches

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet

# =============================
# UNIT
# =============================
def mm_to_cm(x): return x/10
def mm_to_in(x): return x/25.4

# =============================
# AASHTO
# =============================
def calc_log_W18(D, ZR, Ec, Sc, k):
    DPSI = 2.0
    S0 = 0.35

    Ec = Ec * 145.038
    Sc = Sc * 145.038
    k = k * 3.6839

    try:
        A = ZR * S0
        B = 7.35 * math.log10(D + 1) - 0.06
        C = math.log10(DPSI / 3) / (1 + (1.624e7 / (D + 1)**8.46))
        ek = (Ec / k) ** 0.25
        inner = D**0.75 - 18.42 / ek

        if inner <= 0:
            return -999

        D_part = (4.22 - 0.32 * 2.5) * math.log10(
            (Sc * (D**0.75 - 1.132)) / (215.63 * 3.2 * inner)
        )

        return A + B + C + D_part
    except:
        return -999


def design_slab(W18, R, Ec, Sc, k):
    ZR_map = {85: -1.037, 90: -1.282, 95: -1.645}
    ZR = ZR_map.get(R, -1.282)

    target = math.log10(W18 * 1e6)

    lo, hi = 1, 20
    for _ in range(100):
        mid = (lo + hi) / 2
        val = calc_log_W18(mid, ZR, Ec, Sc, k)

        if val < target:
            lo = mid
        else:
            hi = mid

    return round(math.ceil(mid*4)/4 * 25.4)

# =============================
# LAYER
# =============================
def design_layers(D, CBR):
    if CBR < 5:
        return 200, 150
    elif CBR < 10:
        return 180, 120
    else:
        return 150, 100

# =============================
# DRAW
# =============================
def draw_section(D, base, sub):
    fig, ax = plt.subplots(figsize=(6,6))

    layers = [
        ("PCC", D, "#90CAF9"),
        ("Base", base, "#A5D6A7"),
        ("Subbase", sub, "#FFE082"),
        ("Subgrade", 300, "#D7CCC8")
    ]

    y = 0
    for name, thk, color in layers:
        rect = patches.Rectangle((0, y), 10, thk, facecolor=color)
        ax.add_patch(rect)
        ax.text(5, y+thk/2, f"{name}\n{thk} mm",
                ha='center', va='center', weight='bold')
        y += thk

    ax.set_xlim(0,10)
    ax.set_ylim(0,y)
    ax.invert_yaxis()
    ax.axis('off')

    plt.savefig("section.png", dpi=150, bbox_inches="tight")
    plt.close()

# =============================
# PDF REPORT
# =============================
def generate_pdf(D, base, sub, total):

    doc = SimpleDocTemplate("AASHTO_Report.pdf")
    styles = getSampleStyleSheet()

    story = []

    story.append(Paragraph("AASHTO 1993 Rigid Pavement Design Report", styles["Title"]))
    story.append(Spacer(1,20))

    # Table
    data = [
        ["Layer","mm","cm","inch"],
        ["PCC", D, f"{mm_to_cm(D):.1f}", f"{mm_to_in(D):.2f}"],
        ["Base", base, f"{mm_to_cm(base):.1f}", f"{mm_to_in(base):.2f}"],
        ["Subbase", sub, f"{mm_to_cm(sub):.1f}", f"{mm_to_in(sub):.2f}"],
        ["Total", total, f"{mm_to_cm(total):.1f}", f"{mm_to_in(total):.2f}"]
    ]

    t = Table(data)
    t.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,0),colors.grey),
        ("GRID",(0,0),(-1,-1),1,colors.black)
    ]))

    story.append(t)
    story.append(Spacer(1,20))

    # Description
    story.append(Paragraph(
        "PCC เป็นชั้นรับแรงหลัก, Base และ Subbase ช่วยกระจายแรงลงสู่ Subgrade",
        styles["Normal"]
    ))

    if os.path.exists("section.png"):
        story.append(Spacer(1,20))
        story.append(Image("section.png", width=350, height=350))

    doc.build(story)

# =============================
# UI
# =============================
st.title("🛣️ AASHTO 1993 (Full Report Version)")

W18 = st.number_input("W18",15.0)
R = st.selectbox("Reliability",[85,90,95])
k = st.number_input("k",54.0)
CBR = st.number_input("CBR",8)

Ec = st.number_input("Ec",27600)
Sc = st.number_input("Sc",4.8)

if st.button("Run Design"):

    D = design_slab(W18,R,Ec,Sc,k)
    base, sub = design_layers(D,CBR)
    total = D+base+sub

    st.success(f"PCC = {D} mm ({mm_to_cm(D):.1f} cm, {mm_to_in(D):.2f} in)")

    draw_section(D,base,sub)
    st.image("section.png")

    generate_pdf(D,base,sub,total)

    with open("AASHTO_Report.pdf","rb") as f:
        st.download_button("Download Report",f)
