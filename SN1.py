"""
==============================================================
  AASHTO 1993 Rigid Pavement (PCC) Design Program
  โปรแกรมออกแบบโครงสร้างผิวทางคอนกรีต ตามมาตรฐาน AASHTO 1993
==============================================================
  ครอบคลุม:
    1. Slab Thickness Design (AASHTO 1993 Equation)
    2. Base / Subbase Layer Design & Composite k
    3. Dowel Bar Design
    4. Tie Bar Design
    5. PDF Report + Cross-section diagram
==============================================================
"""

import math
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyArrowPatch
from datetime import date
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm, mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, Image as RLImage
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
import os, io

# ─────────────────────────────────────────────
#  1.  INPUT PARAMETERS
# ─────────────────────────────────────────────
class SlabInputs:
    """พารามิเตอร์สำหรับออกแบบแผ่นคอนกรีต"""
    def __init__(self):
        self.W18        = 10.0      # ESAL (ล้านคัน)
        self.R          = 85        # Reliability (%)
        self.S0         = 0.35      # Overall Standard Deviation
        self.p0         = 4.5       # Initial Serviceability
        self.pt         = 2.5       # Terminal Serviceability
        self.Ec         = 27600     # Elastic Modulus คอนกรีต (MPa)
        self.Sc         = 4.5       # Modulus of Rupture S'c (MPa)
        self.J          = 3.2       # Load Transfer Coefficient
        self.Cd         = 1.0       # Drainage Coefficient
        self.k          = 54.0      # Modulus of Subgrade Reaction (MN/m³)

class BaseInputs:
    """พารามิเตอร์สำหรับ Base/Subbase"""
    def __init__(self):
        self.base_type  = "CTB"     # Granular / CTB / ATB / LCB
        self.base_thk   = 200       # ความหนา Base (mm)
        self.sub_type   = "Granular"# Granular / Stabilized / None
        self.sub_thk    = 150       # ความหนา Subbase (mm)
        self.CBR        = 8         # CBR ดินเดิม (%)
        self.E_base     = 2000      # Modulus Base (MPa)
        self.E_sub      = 150       # Modulus Subbase (MPa)
        self.E_sg       = 60        # Modulus Subgrade (MPa)
        self.sg_thk     = 300       # ความหนา Subgrade (mm)

class DowelInputs:
    """พารามิเตอร์ Dowel Bar"""
    def __init__(self):
        self.dia        = 32        # เส้นผ่าศูนย์กลาง (mm)
        self.spacing    = 300       # ระยะห่าง (mm)
        self.P_axle     = 80        # แรงกระทำต่อเพลา (kN)
        self.fc         = 28        # f'c คอนกรีต (MPa)

class TieInputs:
    """พารามิเตอร์ Tie Bar"""
    def __init__(self):
        self.lane_width = 3.75      # ความกว้างช่อง (m)
        self.dia        = 16        # เส้นผ่าศูนย์กลาง (mm)
        self.fy         = 390       # กำลังครากเหล็ก (MPa)
        self.friction   = 1.5       # ค่าสัมประสิทธิ์แรงเสียดทาน
        self.gamma_c    = 24        # น้ำหนักคอนกรีต (kN/m³)


# ─────────────────────────────────────────────
#  2.  ZR TABLE
# ─────────────────────────────────────────────
ZR_TABLE = {
    50: 0.000, 60: -0.253, 70: -0.524, 75: -0.674,
    80: -0.842, 85: -1.037, 90: -1.282, 91: -1.340,
    92: -1.405, 93: -1.476, 94: -1.555, 95: -1.645,
    96: -1.751, 97: -1.881, 97.5: -1.960, 98: -2.054,
    99: -2.327, 99.9: -3.090
}

def get_ZR(R_pct: float) -> float:
    """ดึงค่า ZR จาก Reliability (%)"""
    if R_pct in ZR_TABLE:
        return ZR_TABLE[R_pct]
    keys = sorted(ZR_TABLE.keys())
    for i in range(len(keys)-1):
        if keys[i] < R_pct < keys[i+1]:
            t = (R_pct - keys[i]) / (keys[i+1] - keys[i])
            return ZR_TABLE[keys[i]] + t*(ZR_TABLE[keys[i+1]] - ZR_TABLE[keys[i]])
    return ZR_TABLE[keys[-1]]


# ─────────────────────────────────────────────
#  3.  SLAB THICKNESS DESIGN
# ─────────────────────────────────────────────
def calc_log_W18(D_in: float, ZR: float, S0: float, DPSI: float,
                 Ec: float, Sc: float, J: float, Cd: float,
                 k: float, pt: float) -> float:
    """
    AASHTO 1993 Equation for Rigid Pavement
    คืนค่า log10(W18) ที่ได้จาก D ที่กำหนด
    """
    A = ZR * S0
    B = 7.35 * math.log10(D_in + 1) - 0.06
    C_num = math.log10(DPSI / (4.5 - 1.5))
    C_den = 1.0 + (1.624e7 / (D_in + 1)**8.46)
    C = C_num / C_den
    ek = (Ec / k) ** 0.25
    inner = D_in**0.75 - 18.42 / ek
    if inner <= 0:
        return -999.0
    numer_sn = Sc * Cd * (D_in**0.75 - 1.132)
    denom_sn = 215.63 * J * inner
    if numer_sn <= 0 or denom_sn <= 0:
        return -999.0
    D_part = (4.22 - 0.32 * pt) * math.log10(numer_sn / denom_sn)
    return A + B + C + D_part


def design_slab(inp: SlabInputs) -> dict:
    """ออกแบบความหนาแผ่นคอนกรีต — คืนผลลัพธ์เป็น dict"""
    ZR   = get_ZR(inp.R)
    DPSI = inp.p0 - inp.pt
    W18  = inp.W18 * 1e6
    target = math.log10(W18)

    # ── Unit conversions to US Customary (AASHTO equation uses these) ──
    # Ec: MPa → psi  (1 MPa = 145.038 psi)
    Ec_psi = inp.Ec * 145.038
    # S'c: MPa → psi
    Sc_psi = inp.Sc * 145.038
    # k: MN/m³ → pci  (1 MN/m³ = 3.6839 pci)
    k_pci  = inp.k * 3.6839

    # Bisection solve for D (inches)
    # Find upper bound that gives logW18 > target
    hi = 5.0
    for _ in range(30):
        v = calc_log_W18(hi, ZR, inp.S0, DPSI,
                         Ec_psi, Sc_psi, inp.J, inp.Cd, k_pci, inp.pt)
        if v >= target:
            break
        hi *= 1.5
    lo = 1.0
    for _ in range(150):
        mid = (lo + hi) / 2
        val = calc_log_W18(mid, ZR, inp.S0, DPSI,
                           Ec_psi, Sc_psi, inp.J, inp.Cd, k_pci, inp.pt)
        if val < target:
            lo = mid
        else:
            hi = mid
    D_calc = mid

    # ปัดขึ้นทวีคูณ 0.25 นิ้ว
    D_design = math.ceil(D_calc * 4) / 4
    D_mm     = round(D_design * 25.4)

    # Verify
    logW18_check = calc_log_W18(D_design, ZR, inp.S0, DPSI,
                                Ec_psi, Sc_psi, inp.J, inp.Cd, k_pci, inp.pt)

    return {
        "ZR":           ZR,
        "DPSI":         DPSI,
        "W18_ESAL":     W18,
        "logW18_target":target,
        "D_calc_in":    D_calc,
        "D_design_in":  D_design,
        "D_mm":         D_mm,
        "logW18_check": logW18_check,
        "Ec_psi":       Ec_psi,
        "Sc_psi":       Sc_psi,
        "k_pci":        k_pci,
        "inputs":       inp,
    }


# ─────────────────────────────────────────────
#  4.  BASE / SUBBASE DESIGN
# ─────────────────────────────────────────────
BASE_MODULUS = {
    "Granular": (100,   400),   # (min, typical max) MPa
    "CTB":      (2000, 10000),
    "ATB":      (1500,  7000),
    "LCB":      (5000, 15000),
}

def design_base(inp: BaseInputs, D_slab_mm: float) -> dict:
    """คำนวณ k composite และโครงสร้างชั้นรองรับ"""
    # k ดินเดิมจาก CBR (Heukelom & Klomp approximate)
    k_sg = inp.CBR * 10.0   # MN/m³  (approximate)

    # k composite จาก Subbase (simplified Westergaard approach)
    k_comp = k_sg
    if inp.sub_type.lower() != "none" and inp.sub_thk > 0:
        h2 = inp.sub_thk / 1000.0
        k_comp = k_sg * (1 + (inp.E_sub / inp.E_sg) * (h2**0.45) * 0.1)

    # k adjusted จาก Base
    h1 = inp.base_thk / 1000.0
    k_adj = k_comp * (1 + (inp.E_base / (k_comp * 1000)) * (h1**0.35) * 0.15)

    sub_used = inp.sub_thk if inp.sub_type.lower() != "none" else 0
    total_structural = D_slab_mm + inp.base_thk + sub_used

    return {
        "k_sg":              round(k_sg, 2),
        "k_composite":       round(k_comp, 2),
        "k_adjusted":        round(k_adj, 2),
        "total_structural_mm": total_structural,
        "inputs":            inp,
        "D_slab_mm":         D_slab_mm,
    }


# ─────────────────────────────────────────────
#  5.  DOWEL BAR DESIGN
# ─────────────────────────────────────────────
def design_dowel(inp: DowelInputs, D_mm: float) -> dict:
    """
    ออกแบบ Dowel Bar
    - แรงต่อ dowel bar
    - ความเค้นแบกรับ σ_b ≤ 4f'c (allowable)
    - ความยาว dowel
    """
    # จำนวน dowel bars ที่รับแรงร่วม (ภายใน 1800 mm จาก load)
    n_eff = max(1, int(1800 / inp.spacing))
    P_per = inp.P_axle / n_eff          # kN ต่อแท่ง

    # ความเค้นแบกรับ (Bearing Stress)
    A_contact = inp.dia * inp.dia * math.pi / 4   # mm²
    sigma_b = P_per * 1000 / A_contact             # MPa  (P kN → N)

    fb_allow = 4.0 * inp.fc                         # MPa
    status   = "PASS" if sigma_b <= fb_allow else "FAIL"

    # ขนาด dowel ที่แนะนำ: D/8 นิ้ว (ประมาณ D*3.17 mm) ไม่ต่ำกว่า 25 mm
    dia_recommend = max(25, round((D_mm / 25.4) / 8 * 25.4 / 5) * 5)

    # ความยาว dowel (ปัดขึ้น 25 mm)
    L_dowel = max(300, math.ceil(D_mm * 1.8 / 25) * 25)

    return {
        "n_effective":      n_eff,
        "P_per_dowel_kN":   round(P_per, 2),
        "sigma_b_MPa":      round(sigma_b, 2),
        "fb_allow_MPa":     round(fb_allow, 2),
        "status":           status,
        "dia_recommend_mm": dia_recommend,
        "L_dowel_mm":       L_dowel,
        "inputs":           inp,
    }


# ─────────────────────────────────────────────
#  6.  TIE BAR DESIGN
# ─────────────────────────────────────────────
def design_tie(inp: TieInputs, D_mm: float) -> dict:
    """
    ออกแบบ Tie Bar (เหล็กยึด)
    As = 1.2 × γ_c × D × W × f / fy
    """
    D_m  = D_mm / 1000.0
    # As = 1.2 * γc(kN/m³) * D(m) * W(m) * f / fy(MPa=kN/mm²)  → mm²/m
    As_mm2_per_m = (1.2 * inp.gamma_c * D_m * inp.lane_width * inp.friction
                    / (inp.fy / 1000.0))   # kN/m² / (kN/mm²) = mm²/m

    A_bar = math.pi * inp.dia**2 / 4.0   # mm²
    spacing_calc = A_bar / As_mm2_per_m * 1000  # mm
    spacing_use  = min(800, max(100, math.floor(spacing_calc / 25) * 25))  # ปัดลง 25 mm

    # ความยาว tie bar (development length + embedment)
    Ld = max(500, round((75 * inp.dia + 75) / 25) * 25)

    As_provided = A_bar / spacing_use * 1000   # mm²/m

    return {
        "As_required_mm2_m":  round(As_mm2_per_m, 1),
        "spacing_mm":         spacing_use,
        "L_tie_mm":           Ld,
        "As_provided_mm2_m":  round(As_provided, 1),
        "inputs":             inp,
    }


# ─────────────────────────────────────────────
#  7.  CROSS-SECTION DIAGRAM
# ─────────────────────────────────────────────
LAYER_COLORS = {
    "PCC":      "#AEC6E8",
    "Granular": "#C5E1A5",
    "CTB":      "#90CAF9",
    "ATB":      "#FFCC80",
    "LCB":      "#80DEEA",
    "Subbase":  "#FFECB3",
    "Subgrade": "#D7CCC8",
    "Soil":     "#BCAAA4",
}

def draw_cross_section(slab_res: dict, base_res: dict,
                       dowel_res: dict, tie_res: dict,
                       save_path: str = "/tmp/cross_section.png"):
    """วาดภาพตัดขวางโครงสร้างผิวทาง"""
    D_mm      = slab_res["D_mm"]
    base_in   = base_res["inputs"]
    sub_used  = base_in.sub_thk if base_in.sub_type.lower() != "none" else 0
    sg_thk    = base_in.sg_thk

    layers = [
        ("PCC Concrete Slab", D_mm,             LAYER_COLORS["PCC"]),
        (f"{base_in.base_type} Base",
                              base_in.base_thk,  LAYER_COLORS.get(base_in.base_type, "#B0BEC5")),
    ]
    if sub_used > 0:
        layers.append((f"{base_in.sub_type} Subbase",
                       sub_used, LAYER_COLORS["Subbase"]))
    layers.append(("Subgrade", sg_thk,      LAYER_COLORS["Subgrade"]))
    layers.append(("Natural Soil (CBR=%d%%)" % base_in.CBR,
                   80,                           LAYER_COLORS["Soil"]))

    total_h = sum(h for _, h, _ in layers)
    fig, ax = plt.subplots(figsize=(12, 7))
    ax.set_xlim(0, 10)
    ax.set_ylim(-total_h - 20, 80)
    ax.axis("off")
    ax.set_facecolor("white")
    fig.patch.set_facecolor("white")

    y = 0
    for name, h, col in layers:
        rect = mpatches.FancyBboxPatch((1.0, y - h), 8.0, h,
               boxstyle="square,pad=0", linewidth=0.8,
               edgecolor="#555", facecolor=col)
        ax.add_patch(rect)
        fs = 9.5 if h < 60 else 10.5
        ax.text(5.0, y - h/2, f"{name}\n{h} mm",
                ha="center", va="center", fontsize=fs,
                fontweight="bold" if name.startswith("PCC") else "normal",
                color="#1a1a1a")
        # dimension line
        ax.annotate("", xy=(0.6, y), xytext=(0.6, y - h),
                    arrowprops=dict(arrowstyle="<->", color="#444", lw=0.8))
        ax.text(0.4, y - h/2, f"{h}", ha="right", va="center",
                fontsize=8, color="#444")
        y -= h

    # dowel bar schematic inside slab
    slab_y_top  = 0
    slab_y_bot  = -D_mm
    dw_y = (slab_y_top + slab_y_bot) / 2
    for xd in [2.8, 3.8, 5.0, 6.2, 7.2]:
        ax.plot([xd, xd+0.8], [dw_y, dw_y], lw=4, color="#555", solid_capstyle="round")
    ax.text(5.0, dw_y + D_mm*0.18,
            f"Dowel Bar Ø{dowel_res['inputs'].dia}@{dowel_res['inputs'].spacing} mm",
            ha="center", fontsize=8, color="#333", style="italic")

    # total structural depth annotation
    struct_bot = -(D_mm + base_in.base_thk + sub_used)
    ax.annotate("", xy=(9.6, 0), xytext=(9.6, struct_bot),
                arrowprops=dict(arrowstyle="<->", color="#1565C0", lw=1.2))
    ax.text(9.75, struct_bot/2,
            f"Structural\n{abs(struct_bot)} mm",
            ha="left", va="center", fontsize=8.5, color="#1565C0")

    ax.set_title(
        f"AASHTO 1993 Rigid Pavement — Cross Section\n"
        f"PCC = {D_mm} mm  |  Base = {base_in.base_thk} mm  |  "
        f"Subbase = {sub_used} mm  |  Subgrade CBR = {base_in.CBR}%",
        fontsize=11, pad=12, color="#1a1a1a")

    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches="tight",
                facecolor="white")
    plt.close()
    return save_path


# ─────────────────────────────────────────────
#  8.  SENSITIVITY PLOT  (D vs W18)
# ─────────────────────────────────────────────
def draw_sensitivity(inp: SlabInputs, D_design: float,
                     save_path: str = "/tmp/sensitivity.png"):
    """กราฟความสัมพันธ์ D กับ W18"""
    D_range = np.linspace(6, 22, 160)
    ZR   = get_ZR(inp.R)
    DPSI = inp.p0 - inp.pt
    Ec_psi = inp.Ec * 145.038
    Sc_psi = inp.Sc * 145.038
    k_pci  = inp.k  * 3.6839

    logW_vals = [calc_log_W18(d, ZR, inp.S0, DPSI,
                               Ec_psi, Sc_psi, inp.J, inp.Cd,
                               k_pci, inp.pt) for d in D_range]
    W18_vals  = [10**v / 1e6 if v > 0 else 0 for v in logW_vals]

    fig, ax = plt.subplots(figsize=(10, 5.5))
    ax.plot(D_range * 25.4, W18_vals, color="#1565C0", lw=2)
    ax.axvline(D_design * 25.4, color="#C62828", lw=1.5,
               linestyle="--", label=f"D design = {D_design*25.4:.0f} mm")
    ax.axhline(inp.W18, color="#2E7D32", lw=1.5,
               linestyle="--", label=f"W18 = {inp.W18:.1f} M ESAL")
    ax.scatter([D_design * 25.4], [inp.W18], color="#C62828", s=80, zorder=5)

    ax.set_xlabel("Slab Thickness D (mm)", fontsize=11)
    ax.set_ylabel("W18 (Million ESAL)", fontsize=11)
    ax.set_title("Sensitivity: Slab Thickness vs Traffic Loading (AASHTO 1993)",
                 fontsize=12, pad=10)
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)
    ax.set_facecolor("#FAFAFA")
    fig.patch.set_facecolor("white")

    # annotate design point
    ax.annotate(f"Design point\n({D_design*25.4:.0f} mm, {inp.W18:.1f}M)",
                xy=(D_design*25.4, inp.W18),
                xytext=(D_design*25.4 + 30, inp.W18 * 1.3),
                fontsize=9, color="#C62828",
                arrowprops=dict(arrowstyle="->", color="#C62828", lw=1))

    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close()
    return save_path


# ─────────────────────────────────────────────
#  9.  PDF REPORT
# ─────────────────────────────────────────────
def generate_pdf(slab_res, base_res, dowel_res, tie_res,
                 img_cross, img_sens,
                 out_path="/mnt/user-data/outputs/AASHTO1993_Design_Report.pdf"):
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    doc = SimpleDocTemplate(out_path, pagesize=A4,
                            rightMargin=2*cm, leftMargin=2*cm,
                            topMargin=2*cm, bottomMargin=2*cm)
    styles = getSampleStyleSheet()
    story  = []

    # Custom styles
    title_style = ParagraphStyle("TitleTH", parent=styles["Title"],
                                 fontSize=16, spaceAfter=4, alignment=TA_CENTER)
    h1_style    = ParagraphStyle("H1", parent=styles["Heading1"],
                                 fontSize=13, textColor=colors.HexColor("#0D47A1"),
                                 spaceAfter=4, spaceBefore=12)
    h2_style    = ParagraphStyle("H2", parent=styles["Heading2"],
                                 fontSize=11, textColor=colors.HexColor("#1565C0"),
                                 spaceAfter=3, spaceBefore=8)
    body_style  = ParagraphStyle("Body", parent=styles["Normal"],
                                 fontSize=10, leading=14)
    note_style  = ParagraphStyle("Note", parent=styles["Normal"],
                                 fontSize=9, textColor=colors.HexColor("#666666"),
                                 leading=12)

    def tbl(data, col_widths=None, header_bg=colors.HexColor("#0D47A1")):
        t = Table(data, colWidths=col_widths)
        style = TableStyle([
            ("BACKGROUND",  (0,0), (-1,0), header_bg),
            ("TEXTCOLOR",   (0,0), (-1,0), colors.white),
            ("FONTNAME",    (0,0), (-1,0), "Helvetica-Bold"),
            ("FONTSIZE",    (0,0), (-1,-1), 9.5),
            ("ROWBACKGROUNDS", (0,1), (-1,-1),
             [colors.white, colors.HexColor("#EEF2FF")]),
            ("GRID",        (0,0), (-1,-1), 0.4, colors.HexColor("#BBBBBB")),
            ("TOPPADDING",  (0,0), (-1,-1), 4),
            ("BOTTOMPADDING",(0,0),(-1,-1), 4),
            ("LEFTPADDING", (0,0), (-1,-1), 6),
            ("RIGHTPADDING",(0,0), (-1,-1), 6),
            ("VALIGN",      (0,0), (-1,-1), "MIDDLE"),
        ])
        t.setStyle(style)
        return t

    # ── Title ──────────────────────────────────────────────
    story.append(Paragraph("AASHTO 1993 Rigid Pavement Design Report", title_style))
    story.append(Paragraph("รายงานการออกแบบโครงสร้างผิวทางคอนกรีต", title_style))
    story.append(Spacer(1, 4))
    story.append(Paragraph(f"วันที่ออกแบบ: {date.today().strftime('%d %B %Y')}",
                            ParagraphStyle("sub", parent=styles["Normal"],
                                           fontSize=9, alignment=TA_CENTER,
                                           textColor=colors.HexColor("#555"))))
    story.append(HRFlowable(width="100%", thickness=1.5,
                             color=colors.HexColor("#0D47A1"), spaceAfter=8))

    # ── 1. Slab Design ─────────────────────────────────────
    story.append(Paragraph("1.  Slab Thickness Design", h1_style))
    s = slab_res;  si = s["inputs"]
    story.append(Paragraph("1.1  Input Parameters", h2_style))
    story.append(tbl([
        ["Parameter", "Symbol", "Value", "Unit"],
        ["Traffic Loading",       "W18",  f"{si.W18:.1f} M",  "Million ESAL"],
        ["Reliability",           "R",    f"{si.R}%",          ""],
        ["Standard Normal Deviate","ZR",  f"{s['ZR']:.3f}",   ""],
        ["Overall Std. Deviation", "S₀",  f"{si.S0:.2f}",     ""],
        ["Initial Serviceability", "p₀",  f"{si.p0:.1f}",     ""],
        ["Terminal Serviceability","pₜ",  f"{si.pt:.1f}",     ""],
        ["ΔPSI",                  "ΔPSI", f"{s['DPSI']:.1f}", ""],
        ["Elastic Modulus (PCC)", "Ec",   f"{si.Ec:,}",       "MPa"],
        ["Modulus of Rupture",    "S'c",  f"{si.Sc:.1f}",     "MPa"],
        ["Load Transfer Coeff.",  "J",    f"{si.J:.1f}",      ""],
        ["Drainage Coefficient",  "Cd",   f"{si.Cd:.2f}",     ""],
        ["Subgrade Reaction",     "k",    f"{si.k:.1f}",      "MN/m³"],
    ], col_widths=[5.5*cm, 2.5*cm, 3*cm, 3*cm]))

    story.append(Spacer(1, 8))
    story.append(Paragraph("1.2  Design Results", h2_style))
    story.append(tbl([
        ["Result", "Value", "Unit"],
        ["log₁₀(W18) — target",  f"{s['logW18_target']:.4f}", ""],
        ["D (computed)",         f"{s['D_calc_in']:.3f}",     "in"],
        ["D (rounded up 0.25in)",f"{s['D_design_in']:.2f}",  "in"],
        ["D (design)",           f"{s['D_mm']}",              "mm"],
        ["log₁₀(W18) — verify",  f"{s['logW18_check']:.4f}", ""],
    ], col_widths=[8*cm, 4*cm, 2*cm]))

    # highlight box
    story.append(Spacer(1, 6))
    story.append(tbl([
        ["SLAB DESIGN THICKNESS",
         f"{s['D_design_in']:.2f} in  =  {s['D_mm']} mm"]
    ], col_widths=[9*cm, 5*cm],
       header_bg=colors.HexColor("#1565C0")))

    # formula note
    story.append(Spacer(1, 6))
    story.append(Paragraph(
        "สมการ: log₁₀(W18) = Z_R·S₀ + 7.35·log₁₀(D+1) − 0.06 + "
        "[log₁₀(ΔPSI/3)] / [1 + 1.624×10⁷/(D+1)⁸·⁴⁶] + "
        "(4.22−0.32pₜ)·log₁₀[S'c·Cd·(D⁰·⁷⁵−1.132) / (215.63·J·(D⁰·⁷⁵−18.42/(Ec/k)⁰·²⁵))]",
        note_style))

    # ── 2. Base Layer ──────────────────────────────────────
    story.append(Paragraph("2.  Base / Subbase Layer Design", h1_style))
    bi = base_res["inputs"]
    story.append(tbl([
        ["Layer", "Type / Description", "Thickness", "E (MPa)"],
        ["PCC Slab",  "Portland Cement Concrete",
         f"{slab_res['D_mm']} mm", f"{si.Ec:,}"],
        ["Base",      bi.base_type,
         f"{bi.base_thk} mm",       f"{bi.E_base:,}"],
        ["Subbase",   bi.sub_type if bi.sub_type.lower()!="none" else "—",
         f"{bi.sub_thk} mm" if bi.sub_type.lower()!="none" else "—",
         f"{bi.E_sub:,}" if bi.sub_type.lower()!="none" else "—"],
        ["Subgrade",  f"CBR = {bi.CBR}%",
         f"{bi.sg_thk} mm",          f"{bi.E_sg}"],
    ], col_widths=[3*cm, 5.5*cm, 3*cm, 2.5*cm]))

    story.append(Spacer(1, 6))
    story.append(tbl([
        ["k Calculation", "Value", "Unit"],
        ["k subgrade (from CBR)",      f"{base_res['k_sg']:.1f}",       "MN/m³"],
        ["k composite (with subbase)", f"{base_res['k_composite']:.2f}", "MN/m³"],
        ["k adjusted (with base)",     f"{base_res['k_adjusted']:.2f}",  "MN/m³"],
        ["Total structural thickness", f"{base_res['total_structural_mm']}", "mm"],
    ], col_widths=[8*cm, 3*cm, 3*cm]))

    # ── 3. Dowel Bar ───────────────────────────────────────
    story.append(Paragraph("3.  Dowel Bar Design", h1_style))
    di = dowel_res["inputs"]
    stat_color = colors.HexColor("#1B5E20") if dowel_res["status"]=="PASS" else colors.HexColor("#B71C1C")
    story.append(tbl([
        ["Parameter",             "Value",                        "Unit"],
        ["Dowel diameter",        f"Ø {di.dia}",                 "mm"],
        ["Dowel spacing",         f"{di.spacing}",               "mm"],
        ["Dowel length",          f"{dowel_res['L_dowel_mm']}",  "mm"],
        ["Design axle load (P)",  f"{di.P_axle:.0f}",            "kN"],
        ["No. of effective dowels",f"{dowel_res['n_effective']}", ""],
        ["Force per dowel",       f"{dowel_res['P_per_dowel_kN']:.2f}", "kN"],
        ["Bearing stress σ_b",    f"{dowel_res['sigma_b_MPa']:.2f}",    "MPa"],
        ["Allowable (4f'c)",      f"{dowel_res['fb_allow_MPa']:.1f}",   "MPa"],
        ["Status",                dowel_res["status"],            ""],
    ], col_widths=[7*cm, 4*cm, 3*cm]))
    story.append(Spacer(1, 4))
    story.append(Paragraph(
        f"สรุป: ความเค้นแบกรับ = {dowel_res['sigma_b_MPa']:.2f} MPa "
        f"{'≤' if dowel_res['status']=='PASS' else '>'} "
        f"{dowel_res['fb_allow_MPa']:.1f} MPa (4f'c) → {dowel_res['status']}",
        ParagraphStyle("stat", parent=styles["Normal"], fontSize=10,
                       textColor=stat_color, leading=14)))

    # ── 4. Tie Bar ─────────────────────────────────────────
    story.append(Paragraph("4.  Tie Bar Design", h1_style))
    ti = tie_res["inputs"]
    story.append(tbl([
        ["Parameter",              "Value",                       "Unit"],
        ["Lane width W",           f"{ti.lane_width:.2f}",       "m"],
        ["Tie bar diameter",       f"DB {ti.dia}",               "mm"],
        ["Yield strength fy",      f"{ti.fy}",                   "MPa"],
        ["Friction coefficient f", f"{ti.friction:.1f}",         ""],
        ["Unit weight γ_c",        f"{ti.gamma_c:.0f}",          "kN/m³"],
        ["As required",            f"{tie_res['As_required_mm2_m']:.1f}", "mm²/m"],
        ["Spacing used",           f"{tie_res['spacing_mm']}",   "mm"],
        ["As provided",            f"{tie_res['As_provided_mm2_m']:.1f}", "mm²/m"],
        ["Tie bar length",         f"{tie_res['L_tie_mm']}",     "mm"],
    ], col_widths=[7*cm, 4*cm, 3*cm]))

    # ── Figures ────────────────────────────────────────────
    story.append(Paragraph("5.  Cross-Section & Sensitivity Analysis", h1_style))
    story.append(RLImage(img_cross, width=15*cm, height=8.5*cm))
    story.append(Spacer(1, 8))
    story.append(RLImage(img_sens,  width=15*cm, height=8*cm))

    # ── Footer note ────────────────────────────────────────
    story.append(Spacer(1, 10))
    story.append(HRFlowable(width="100%", thickness=0.5,
                             color=colors.HexColor("#AAAAAA"), spaceAfter=4))
    story.append(Paragraph(
        "อ้างอิง: AASHTO Guide for Design of Pavement Structures, 1993. "
        "American Association of State Highway and Transportation Officials.",
        note_style))

    doc.build(story)
    return out_path


# ─────────────────────────────────────────────
#  10.  CONSOLE REPORT
# ─────────────────────────────────────────────
def print_report(slab_res, base_res, dowel_res, tie_res):
    sep = "─" * 60
    print("\n" + "═"*60)
    print("  AASHTO 1993 RIGID PAVEMENT DESIGN")
    print("  โปรแกรมออกแบบโครงสร้างผิวทางคอนกรีต")
    print("═"*60)

    print(f"\n{'1. SLAB THICKNESS DESIGN':^60}")
    print(sep)
    si = slab_res["inputs"]
    print(f"  W18 Traffic Loading  : {si.W18:.1f} Million ESAL")
    print(f"  Reliability          : {si.R}%  (ZR = {slab_res['ZR']:.3f})")
    print(f"  S0                   : {si.S0:.2f}")
    print(f"  p0 / pt / ΔPSI       : {si.p0} / {si.pt} / {slab_res['DPSI']:.1f}")
    print(f"  Ec                   : {si.Ec:,} MPa")
    print(f"  S'c                  : {si.Sc:.1f} MPa")
    print(f"  J                    : {si.J:.1f}")
    print(f"  Cd                   : {si.Cd:.2f}")
    print(f"  k                    : {si.k:.1f} MN/m³")
    print(sep)
    print(f"  D (computed)         : {slab_res['D_calc_in']:.3f} in")
    print(f"  D (design, round up) : {slab_res['D_design_in']:.2f} in")
    print(f"  *** D DESIGN         : {slab_res['D_mm']} mm ***")
    print(f"  logW18 check         : {slab_res['logW18_check']:.4f} "
          f"(target {slab_res['logW18_target']:.4f})")

    print(f"\n{'2. BASE / SUBBASE':^60}")
    print(sep)
    bi = base_res["inputs"]
    print(f"  Base type / thickness: {bi.base_type} / {bi.base_thk} mm")
    print(f"  Subbase type / thk   : {bi.sub_type} / "
          f"{bi.sub_thk if bi.sub_type.lower()!='none' else '—'} mm")
    print(f"  Subgrade CBR         : {bi.CBR}%")
    print(f"  k (from CBR)         : {base_res['k_sg']:.1f} MN/m³")
    print(f"  k composite          : {base_res['k_composite']:.2f} MN/m³")
    print(f"  k adjusted           : {base_res['k_adjusted']:.2f} MN/m³")
    print(f"  Total structural thk : {base_res['total_structural_mm']} mm")

    print(f"\n{'3. DOWEL BAR':^60}")
    print(sep)
    di = dowel_res["inputs"]
    print(f"  Diameter / Spacing   : Ø{di.dia} mm @ {di.spacing} mm")
    print(f"  Length               : {dowel_res['L_dowel_mm']} mm")
    print(f"  No. effective dowels : {dowel_res['n_effective']}")
    print(f"  Force per dowel      : {dowel_res['P_per_dowel_kN']:.2f} kN")
    print(f"  Bearing stress σ_b   : {dowel_res['sigma_b_MPa']:.2f} MPa")
    print(f"  Allowable (4f'c)     : {dowel_res['fb_allow_MPa']:.1f} MPa")
    stat = dowel_res["status"]
    print(f"  STATUS               : {'✓ PASS' if stat=='PASS' else '✗ FAIL'}")

    print(f"\n{'4. TIE BAR':^60}")
    print(sep)
    ti = tie_res["inputs"]
    print(f"  Lane width           : {ti.lane_width:.2f} m")
    print(f"  Tie bar size         : DB{ti.dia}")
    print(f"  As required          : {tie_res['As_required_mm2_m']:.1f} mm²/m")
    print(f"  Spacing              : {tie_res['spacing_mm']} mm")
    print(f"  As provided          : {tie_res['As_provided_mm2_m']:.1f} mm²/m")
    print(f"  Length               : {tie_res['L_tie_mm']} mm")
    print("\n" + "═"*60)


# ─────────────────────────────────────────────
#  11.  MAIN
# ─────────────────────────────────────────────
def run_design(
    # ── Slab ──
    W18=10.0, R=85, S0=0.35, p0=4.5, pt=2.5,
    Ec=27600, Sc=4.5, J=3.2, Cd=1.0, k=54.0,
    # ── Base ──
    base_type="CTB", base_thk=200, sub_type="Granular", sub_thk=150,
    CBR=8, E_base=2000, E_sub=150, E_sg=60, sg_thk=300,
    # ── Dowel ──
    dowel_dia=32, dowel_spacing=300, P_axle=80, fc=28,
    # ── Tie ──
    lane_width=3.75, tie_dia=16, fy=390, friction=1.5, gamma_c=24,
):
    """
    ฟังก์ชันหลักสำหรับรัน design ทั้งหมด
    คืนค่า (slab_res, base_res, dowel_res, tie_res, pdf_path)
    """
    # Build input objects
    si = SlabInputs()
    si.W18=W18; si.R=R; si.S0=S0; si.p0=p0; si.pt=pt
    si.Ec=Ec; si.Sc=Sc; si.J=J; si.Cd=Cd; si.k=k

    bi = BaseInputs()
    bi.base_type=base_type; bi.base_thk=base_thk
    bi.sub_type=sub_type;   bi.sub_thk=sub_thk
    bi.CBR=CBR; bi.E_base=E_base; bi.E_sub=E_sub
    bi.E_sg=E_sg; bi.sg_thk=sg_thk

    di = DowelInputs()
    di.dia=dowel_dia; di.spacing=dowel_spacing
    di.P_axle=P_axle; di.fc=fc

    ti = TieInputs()
    ti.lane_width=lane_width; ti.dia=tie_dia
    ti.fy=fy; ti.friction=friction; ti.gamma_c=gamma_c

    # Run design
    slab_res  = design_slab(si)
    base_res  = design_base(bi, slab_res["D_mm"])
    dowel_res = design_dowel(di, slab_res["D_mm"])
    tie_res   = design_tie(ti, slab_res["D_mm"])

    # Print console
    print_report(slab_res, base_res, dowel_res, tie_res)

    # Draw figures
    img_cross = draw_cross_section(slab_res, base_res, dowel_res, tie_res,
                                   "/tmp/cross_section.png")
    img_sens  = draw_sensitivity(si, slab_res["D_design_in"],
                                 "/tmp/sensitivity.png")

    # Generate PDF
    pdf_path = generate_pdf(slab_res, base_res, dowel_res, tie_res,
                            img_cross, img_sens)
    print(f"\n  PDF Report saved → {pdf_path}")
    return slab_res, base_res, dowel_res, tie_res, pdf_path


# ─────────────────────────────────────────────
#  RUN WITH DEFAULT / EXAMPLE VALUES
# ─────────────────────────────────────────────
if __name__ == "__main__":
    run_design(
        # ─── Slab ───────────────────────────
        W18         = 15.0,     # 15 ล้าน ESAL
        R           = 90,       # Reliability 90%
        S0          = 0.35,
        p0          = 4.5,
        pt          = 2.5,
        Ec          = 27600,    # MPa
        Sc          = 4.8,      # MPa
        J           = 3.2,      # มีไหล่ทางคอนกรีต
        Cd          = 1.0,
        k           = 54.0,     # MN/m³
        # ─── Base Layer ─────────────────────
        base_type   = "CTB",
        base_thk    = 200,      # mm
        sub_type    = "Granular",
        sub_thk     = 150,      # mm
        CBR         = 8,
        E_base      = 3000,     # MPa
        E_sub       = 150,
        E_sg        = 60,
        sg_thk      = 300,
        # ─── Dowel Bar ───────────────────────
        dowel_dia   = 32,       # mm
        dowel_spacing = 300,    # mm
        P_axle      = 80,       # kN
        fc          = 28,       # MPa
        # ─── Tie Bar ────────────────────────
        lane_width  = 3.75,     # m
        tie_dia     = 16,       # mm
        fy          = 390,
        friction    = 1.5,
        gamma_c     = 24,
    )
