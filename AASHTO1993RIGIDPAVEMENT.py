"""
AASHTO 1993 Rigid Pavement Design Tool — Streamlit Version
ออกแบบโครงสร้างผิวทางคอนกรีต ตามมาตรฐาน AASHTO 1993
"""

import streamlit as st
import math
import io
from datetime import datetime

# ══════════════════════════════════════════════════════
#  PAGE CONFIG
# ══════════════════════════════════════════════════════
st.set_page_config(
    page_title="AASHTO 1993 Rigid Pavement Design",
    page_icon="🛣️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ══════════════════════════════════════════════════════
#  CUSTOM CSS
# ══════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600;700&family=Sarabun:wght@300;400;600;700&display=swap');

:root {
  --bg:       #0b1120;
  --surface:  #131c2e;
  --panel:    #1a2640;
  --border:   #243354;
  --accent:   #3b82f6;
  --accent2:  #06b6d4;
  --gold:     #f59e0b;
  --green:    #10b981;
  --red:      #ef4444;
  --text:     #e2e8f0;
  --muted:    #64748b;
  --concrete: #94a3b8;
  --subbase:  #fbbf24;
  --subgrade: #34d399;
}

html, body, [data-testid="stAppViewContainer"] {
    background: var(--bg) !important;
    font-family: 'Sarabun', sans-serif;
    color: var(--text);
}

[data-testid="stSidebar"] {
    background: var(--surface) !important;
    border-right: 1px solid var(--border);
}

[data-testid="stSidebar"] * { color: var(--text) !important; }

h1, h2, h3 { font-family: 'JetBrains Mono', monospace !important; }

.stButton > button {
    background: linear-gradient(135deg, #1d4ed8, #2563eb) !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-weight: 700 !important;
    font-size: 15px !important;
    padding: 12px 28px !important;
    width: 100% !important;
    transition: all 0.2s !important;
    box-shadow: 0 4px 15px rgba(37,99,235,0.4) !important;
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 25px rgba(37,99,235,0.6) !important;
}

.result-card {
    background: var(--panel);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 20px 24px;
    margin-bottom: 16px;
}
.result-card.highlight {
    border-color: var(--accent);
    box-shadow: 0 0 20px rgba(59,130,246,0.2);
}

.metric-box {
    background: linear-gradient(135deg, var(--surface), var(--panel));
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 16px;
    text-align: center;
}
.metric-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 11px;
    color: var(--muted);
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-bottom: 6px;
}
.metric-value {
    font-family: 'JetBrains Mono', monospace;
    font-size: 26px;
    font-weight: 700;
    color: var(--accent);
}
.metric-unit {
    font-size: 13px;
    color: var(--muted);
    margin-top: 2px;
}

.layer-bar {
    border-radius: 6px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 18px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 13px;
    font-weight: 600;
    margin-bottom: 3px;
    border: 1px solid rgba(255,255,255,0.08);
}

.section-title {
    font-family: 'JetBrains Mono', monospace;
    font-size: 13px;
    font-weight: 700;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: var(--accent2);
    border-left: 3px solid var(--accent2);
    padding-left: 10px;
    margin: 20px 0 12px 0;
}

.info-tag {
    display: inline-block;
    background: rgba(59,130,246,0.15);
    border: 1px solid rgba(59,130,246,0.3);
    border-radius: 4px;
    padding: 2px 8px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 11px;
    color: var(--accent);
    margin: 2px;
}

.formula-box {
    background: #0a1628;
    border: 1px solid var(--border);
    border-left: 3px solid var(--gold);
    border-radius: 8px;
    padding: 14px 18px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 11px;
    color: #94a3b8;
    line-height: 1.8;
    margin: 10px 0;
}

div[data-testid="stNumberInput"] input,
div[data-testid="stSelectbox"] select {
    background: #0f172a !important;
    border: 1px solid var(--border) !important;
    border-radius: 6px !important;
    color: var(--text) !important;
    font-family: 'JetBrains Mono', monospace !important;
}

.stSelectbox > div > div {
    background: #0f172a !important;
    border-color: var(--border) !important;
}

[data-testid="stExpander"] {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
}

.stTab [data-baseweb="tab"] {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 12px !important;
}

hr { border-color: var(--border) !important; }

.top-header {
    background: linear-gradient(135deg, #0f1f3d 0%, #1a3464 50%, #0f1f3d 100%);
    border: 1px solid #243354;
    border-radius: 14px;
    padding: 28px 32px;
    margin-bottom: 24px;
    position: relative;
    overflow: hidden;
}
.top-header::before {
    content: '';
    position: absolute;
    top: -50%;
    left: -50%;
    width: 200%;
    height: 200%;
    background: radial-gradient(circle at 70% 50%, rgba(59,130,246,0.08) 0%, transparent 60%);
    pointer-events: none;
}
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════
#  DESIGN ENGINE
# ══════════════════════════════════════════════════════

ZR_TABLE = {
    50: 0.000, 60: -0.253, 70: -0.524, 75: -0.674,
    80: -0.841, 85: -1.037, 90: -1.282, 91: -1.340,
    92: -1.405, 93: -1.476, 94: -1.555, 95: -1.645,
    96: -1.751, 97: -1.881, 98: -2.054, 99: -2.327,
}

def get_zr(R):
    return min(ZR_TABLE.items(), key=lambda x: abs(x[0] - R))[1]

def calc_esal(aadt, truck_pct, growth_rate, design_life, ldf, tff):
    aadt_trucks = aadt * (truck_pct / 100)
    r = growth_rate / 100
    gf = design_life if r == 0 else ((1 + r)**design_life - 1) / r
    return aadt_trucks * tff * ldf * 365 * gf, gf

def solve_slab(W18, ZR, S0, delta_PSI, Pt, Ec_psi, Sc_psi, Cd, J, k_pci):
    """Bisection solve for slab thickness D (inches)"""
    target = math.log10(max(W18, 1))

    def f(D):
        if D <= 0:
            return -999
        try:
            t1 = ZR * S0
            t2 = 7.35 * math.log10(D + 1) - 0.06
            t3 = math.log10(delta_PSI / 3.0) / (1 + 1.624e7 / (D + 1)**8.46)
            inner = D**0.75 - 18.42 / (Ec_psi / k_pci)**0.25
            if inner <= 0:
                return -999
            t4 = (4.22 - 0.32 * Pt) * math.log10(Sc_psi * Cd * (D**0.75 - 1.132) / (215.63 * J * inner))
            return t1 + t2 + t3 + t4
        except:
            return -999

    lo, hi = 2.0, 36.0
    for _ in range(120):
        mid = (lo + hi) / 2
        if f(mid) < target:
            lo = mid
        else:
            hi = mid
        if hi - lo < 0.0005:
            break
    D = (lo + hi) / 2
    return D, D * 25.4

def get_subbase(k_MPa, D_mm):
    if k_MPa < 27:   base = 300
    elif k_MPa < 55: base = 200
    elif k_MPa < 110:base = 150
    else:            base = 100
    return int(base + max(0, (D_mm - 200) * 0.08))

def get_subgrade(k_MPa):
    if k_MPa < 27:   return 300
    elif k_MPa < 55: return 200
    else:            return 150

def design(p):
    Ec_psi = p['Ec'] * 145.038
    Sc_psi = p['Sc'] * 145.038
    k_pci  = p['k'] / 0.2714
    ZR     = get_zr(p['R'])
    dPSI   = p['pi'] - p['pt']

    W18, gf = calc_esal(p['aadt'], p['truck_pct'], p['growth'], p['life'], p['ldf'], p['tff'])
    D_in, D_mm = solve_slab(W18, ZR, p['S0'], dPSI, p['pt'], Ec_psi, Sc_psi, p['Cd'], p['J'], k_pci)
    D_design_mm = math.ceil(D_mm / 25) * 25
    D_design_in = D_design_mm / 25.4

    sub_mm  = get_subbase(p['k'], D_design_mm)
    sgrd_mm = get_subgrade(p['k'])

    return {
        'W18': W18, 'gf': gf, 'ZR': ZR, 'dPSI': dPSI,
        'D_calc_mm': D_mm, 'D_calc_in': D_in,
        'D_mm': D_design_mm, 'D_in': D_design_in,
        'sub_mm': sub_mm, 'sgrd_mm': sgrd_mm,
        'total_mm': D_design_mm + sub_mm + sgrd_mm,
        'Ec_psi': Ec_psi, 'Sc_psi': Sc_psi, 'k_pci': k_pci,
        'p': p,
    }


# ══════════════════════════════════════════════════════
#  PDF GENERATOR
# ══════════════════════════════════════════════════════

def make_pdf(r):
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.lib.units import mm
    from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer,
                                     Table, TableStyle, HRFlowable)
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_CENTER, TA_LEFT

    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4,
        rightMargin=20*mm, leftMargin=20*mm,
        topMargin=20*mm, bottomMargin=20*mm)

    C_DARK  = colors.HexColor('#0f1f3d')
    C_BLUE  = colors.HexColor('#1d4ed8')
    C_CYAN  = colors.HexColor('#0891b2')
    C_LIGHT = colors.HexColor('#eff6ff')
    C_CON   = colors.HexColor('#dbeafe')
    C_SUB   = colors.HexColor('#fef3c7')
    C_SGRD  = colors.HexColor('#d1fae5')
    C_GRAY  = colors.HexColor('#64748b')
    C_WHITE = colors.white

    styles = getSampleStyleSheet()
    def S(name, **kw):
        return ParagraphStyle(name, **kw)

    T  = S('TT', fontSize=17, fontName='Helvetica-Bold', textColor=C_DARK,  alignment=TA_CENTER, spaceAfter=4)
    ST = S('ST', fontSize=10, fontName='Helvetica',      textColor=C_GRAY,  alignment=TA_CENTER, spaceAfter=10)
    H  = S('H',  fontSize=12, fontName='Helvetica-Bold', textColor=C_BLUE,  spaceBefore=14, spaceAfter=6)
    N  = S('N',  fontSize=9,  fontName='Helvetica',      textColor=colors.black, spaceAfter=3)
    NB = S('NB', fontSize=9,  fontName='Helvetica-Bold', textColor=colors.black)

    p = r['p']
    story = []

    story.append(Paragraph("รายงานการออกแบบโครงสร้างผิวทางคอนกรีต", T))
    story.append(Paragraph("Rigid Pavement Design Report  ·  AASHTO 1993 Standard", ST))
    story.append(Paragraph(f"วันที่ออกแบบ: {datetime.now().strftime('%d/%m/%Y  %H:%M น.')}", ST))
    story.append(HRFlowable(width="100%", thickness=2, color=C_BLUE, spaceAfter=10))

    # ── Input ──
    story.append(Paragraph("1. ข้อมูลนำเข้า (Input Parameters)", H))
    cw = [90*mm, 45*mm, 25*mm]
    rows = [['พารามิเตอร์', 'ค่าที่ใช้', 'หน่วย'],
            ['AADT (ปริมาณจราจรเฉลี่ยต่อวัน)', f"{p['aadt']:,.0f}", 'คัน/วัน'],
            ['สัดส่วนรถบรรทุก', f"{p['truck_pct']:.1f}", '%'],
            ['อัตราการเติบโตของจราจร', f"{p['growth']:.1f}", '%/ปี'],
            ['อายุออกแบบ', f"{p['life']:.0f}", 'ปี'],
            ['ความน่าเชื่อถือ (R)', f"{p['R']:.0f}", '%'],
            ['Overall Std Deviation (S0)', f"{p['S0']:.2f}", '-'],
            ['Initial PSI (pi)', f"{p['pi']:.1f}", '-'],
            ['Terminal PSI (pt)', f"{p['pt']:.1f}", '-'],
            ['Modulus of Elasticity of Concrete', f"{p['Ec']:,.0f}", 'MPa'],
            ['Modulus of Rupture (Sc)', f"{p['Sc']:.2f}", 'MPa'],
            ['Drainage Coefficient (Cd)', f"{p['Cd']:.2f}", '-'],
            ['Load Transfer Coefficient (J)', f"{p['J']:.1f}", '-'],
            ['Modulus of Subgrade Reaction (k)', f"{p['k']:.0f}", 'MPa/m'],
            ['Lane Distribution Factor', f"{p['ldf']:.2f}", '-'],
            ['Truck Factor (TFF)', f"{p['tff']:.2f}", '-']]

    t = Table(rows, colWidths=cw)
    t.setStyle(TableStyle([
        ('BACKGROUND',    (0,0), (-1,0), C_BLUE),
        ('TEXTCOLOR',     (0,0), (-1,0), C_WHITE),
        ('FONTNAME',      (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE',      (0,0), (-1,-1), 9),
        ('ROWBACKGROUNDS',(0,1), (-1,-1), [C_WHITE, C_LIGHT]),
        ('GRID',          (0,0), (-1,-1), 0.4, colors.lightgrey),
        ('ALIGN',         (1,0), (-1,-1), 'CENTER'),
        ('VALIGN',        (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING',    (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t)

    # ── Calc ──
    story.append(Paragraph("2. ผลการคำนวณกลาง (Intermediate Results)", H))
    rows2 = [['รายการ', 'ค่า', 'หน่วย'],
             ['Growth Factor (GF)', f"{r['gf']:.3f}", '-'],
             ['ZR (Standard Normal Deviate)', f"{r['ZR']:.3f}", '-'],
             ['ΔPSi (pi - pt)', f"{r['dPSI']:.1f}", '-'],
             ['18-kip ESAL สะสม', f"{r['W18']:,.0f}", 'ESAL'],
             ['k (แปลงหน่วย)', f"{r['k_pci']:.1f}", 'pci'],
             ['Ec (แปลงหน่วย)', f"{r['Ec_psi']:,.0f}", 'psi'],
             ['Sc (แปลงหน่วย)', f"{r['Sc_psi']:.1f}", 'psi'],
             ['ความหนาคำนวณ (D computed)', f"{r['D_calc_mm']:.1f}", 'mm'],
             ['ความหนาออกแบบ (ปัดขึ้น 25 mm)', f"{r['D_mm']:.0f}", 'mm']]

    t2 = Table(rows2, colWidths=cw)
    t2.setStyle(TableStyle([
        ('BACKGROUND',    (0,0), (-1,0), C_CYAN),
        ('TEXTCOLOR',     (0,0), (-1,0), C_WHITE),
        ('FONTNAME',      (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE',      (0,0), (-1,-1), 9),
        ('ROWBACKGROUNDS',(0,1), (-1,-1), [C_WHITE, C_LIGHT]),
        ('GRID',          (0,0), (-1,-1), 0.4, colors.lightgrey),
        ('ALIGN',         (1,0), (-1,-1), 'CENTER'),
        ('VALIGN',        (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING',    (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t2)

    # ── Layer Summary ──
    story.append(Paragraph("3. สรุปความหนาโครงสร้างทาง (Pavement Layer Summary)", H))
    rows3 = [['ชั้นทาง', 'วัสดุ', 'ความหนา (mm)', '(inch)'],
             ['Concrete Slab', 'Portland Cement Concrete',
              str(r['D_mm']),  f"{r['D_in']:.2f}"],
             ['Subbase', 'Granular / Lean Concrete',
              str(r['sub_mm']), f"{r['sub_mm']/25.4:.2f}"],
             ['Subgrade Prep', 'Compacted Subgrade',
              str(r['sgrd_mm']), f"{r['sgrd_mm']/25.4:.2f}"],
             ['รวม / Total', '',
              str(r['total_mm']), f"{r['total_mm']/25.4:.2f}"]]

    cw3 = [55*mm, 55*mm, 30*mm, 22*mm]
    t3 = Table(rows3, colWidths=cw3)
    t3.setStyle(TableStyle([
        ('BACKGROUND',    (0,0), (-1,0), C_DARK),
        ('TEXTCOLOR',     (0,0), (-1,0), C_WHITE),
        ('FONTNAME',      (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE',      (0,0), (-1,-1), 9),
        ('BACKGROUND',    (0,1), (-1,1), C_CON),
        ('BACKGROUND',    (0,2), (-1,2), C_SUB),
        ('BACKGROUND',    (0,3), (-1,3), C_SGRD),
        ('BACKGROUND',    (0,4), (-1,4), C_DARK),
        ('TEXTCOLOR',     (0,4), (-1,4), C_WHITE),
        ('FONTNAME',      (0,4), (-1,4), 'Helvetica-Bold'),
        ('GRID',          (0,0), (-1,-1), 0.4, colors.grey),
        ('ALIGN',         (2,0), (-1,-1), 'CENTER'),
        ('VALIGN',        (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING',    (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t3)

    # ── Cross section visual ──
    story.append(Spacer(1, 8*mm))
    story.append(Paragraph("4. แผนภาพหน้าตัดโครงสร้าง (Cross Section Diagram)", H))

    total = r['total_mm']
    layers_vis = [
        (r['D_mm'],    C_CON,  f"Concrete Slab  —  {r['D_mm']} mm  ({r['D_in']:.2f}\")"),
        (r['sub_mm'],  C_SUB,  f"Subbase  —  {r['sub_mm']} mm"),
        (r['sgrd_mm'], C_SGRD, f"Subgrade Prep  —  {r['sgrd_mm']} mm"),
    ]
    sec = []
    sec_styles = []
    row_i = 0
    for thick, col, label in layers_vis:
        n_rows = max(1, round((thick / total) * 10))
        for i in range(n_rows):
            if i == n_rows // 2:
                sec.append([label])
            else:
                sec.append([""])
            sec_styles.append(('BACKGROUND', (0, row_i), (0, row_i), col))
            row_i += 1

    ts3 = Table(sec, colWidths=[160*mm])
    ts3.setStyle(TableStyle([
        ('FONTNAME',     (0,0), (-1,-1), 'Helvetica'),
        ('FONTSIZE',     (0,0), (-1,-1), 9),
        ('ALIGN',        (0,0), (-1,-1), 'CENTER'),
        ('VALIGN',       (0,0), (-1,-1), 'MIDDLE'),
        ('ROWHEIGHT',    (0,0), (-1,-1), 12),
        ('BOX',          (0,0), (-1,-1), 1.5, C_DARK),
        ('INNERGRID',    (0,0), (-1,-1), 0.3, colors.lightgrey),
    ] + sec_styles))
    story.append(ts3)

    # ── Notes ──
    story.append(Spacer(1, 6*mm))
    story.append(HRFlowable(width="100%", thickness=1, color=C_GRAY, spaceAfter=6))
    story.append(Paragraph("หมายเหตุ / Notes", NB))
    for n_txt in [
        "• ออกแบบตาม AASHTO 1993 Guide for Design of Pavement Structures",
        "• ความหนาแผ่นคอนกรีตปัดขึ้นทุก 25 mm",
        "• ควรตรวจสอบ Subbase ตามมาตรฐานกรมทางหลวงหรือ AASHTO เพิ่มเติม",
        "• ค่า k ที่ใช้คือ Composite k หลังวาง Subbase",
        "• ESAL คำนวณจาก AADT × Truck% × LDF × TFF × 365 × GF",
    ]:
        story.append(Paragraph(n_txt, N))

    doc.build(story)
    buf.seek(0)
    return buf.read()


# ══════════════════════════════════════════════════════
#  MAIN APP
# ══════════════════════════════════════════════════════

def main():
    # ── Top Header ──
    st.markdown("""
    <div class="top-header">
      <div style="font-family:'JetBrains Mono',monospace; font-size:11px;
                  color:#3b82f6; letter-spacing:0.15em; margin-bottom:6px;">
        AASHTO 1993 STANDARD
      </div>
      <div style="font-family:'JetBrains Mono',monospace; font-size:28px;
                  font-weight:700; color:#e2e8f0; line-height:1.2;">
        Rigid Pavement Design
      </div>
      <div style="font-size:15px; color:#94a3b8; margin-top:6px;">
        ออกแบบโครงสร้างผิวทางคอนกรีต — Portland Cement Concrete Pavement
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Sidebar Inputs ──
    with st.sidebar:
        st.markdown("""
        <div style="font-family:'JetBrains Mono',monospace; font-size:13px;
                    font-weight:700; color:#60a5fa; padding:8px 0 14px 0;
                    border-bottom:1px solid #243354; margin-bottom:16px;">
          ⚙️  ข้อมูลนำเข้า (Input)
        </div>
        """, unsafe_allow_html=True)

        # ── Traffic ──
        st.markdown('<div class="section-title">🚛 ข้อมูลจราจร</div>', unsafe_allow_html=True)
        aadt      = st.number_input("AADT (คัน/วัน)",          min_value=100,  max_value=500000, value=5000,  step=100)
        truck_pct = st.number_input("สัดส่วนรถบรรทุก (%)",      min_value=1.0,  max_value=100.0,  value=15.0,  step=0.5)
        growth    = st.number_input("อัตราเติบโตจราจร (%/ปี)",  min_value=0.0,  max_value=20.0,   value=3.0,   step=0.5)
        life      = st.number_input("อายุออกแบบ (ปี)",           min_value=5,    max_value=50,     value=20,    step=5)
        ldf       = st.number_input("Lane Dist. Factor",         min_value=0.1,  max_value=1.0,    value=0.5,   step=0.05,
                                     help="0.4–0.9 แล้วแต่จำนวนช่องจราจร")
        tff       = st.number_input("Truck Factor (ESAL/truck)", min_value=0.1,  max_value=10.0,   value=1.0,   step=0.1,
                                     help="ค่า Equivalency Factor เฉลี่ย")

        # ── Reliability ──
        st.markdown('<div class="section-title">📊 ความน่าเชื่อถือ</div>', unsafe_allow_html=True)
        R_opts = [50, 60, 70, 75, 80, 85, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99]
        R = st.selectbox("Reliability R (%)", R_opts,
                          index=R_opts.index(95),
                          help="ทางสายหลัก 95-99%, ทางรอง 80-90%")
        S0 = st.number_input("Overall Std Dev (S0)", min_value=0.2, max_value=0.5, value=0.35, step=0.01,
                              help="Rigid: 0.30–0.40")
        pi = st.number_input("Initial PSI (pi)",     min_value=3.0, max_value=5.0, value=4.5,  step=0.1)
        pt = st.number_input("Terminal PSI (pt)",    min_value=1.5, max_value=3.5, value=2.5,  step=0.1)

        # ── Material ──
        st.markdown('<div class="section-title">🏗️ คุณสมบัติวัสดุ</div>', unsafe_allow_html=True)

        preset = st.selectbox("Preset วัสดุ", ["กำหนดเอง", "มาตรฐานทั่วไป", "คุณภาพสูง", "ดินฐานอ่อน"])
        presets_data = {
            "มาตรฐานทั่วไป": (27500, 4.50, 1.00, 3.2, 54),
            "คุณภาพสูง":     (30000, 5.00, 1.10, 2.8, 80),
            "ดินฐานอ่อน":   (25000, 4.20, 0.90, 3.8, 27),
            "กำหนดเอง":      (27500, 4.50, 1.00, 3.2, 54),
        }
        def_ec, def_sc, def_cd, def_j, def_k = presets_data[preset]

        Ec = st.number_input("Elastic Modulus Ec (MPa)",    min_value=10000, max_value=50000, value=def_ec, step=500,
                              help="ทั่วไป 20,000–35,000 MPa")
        Sc = st.number_input("Modulus of Rupture Sc (MPa)", min_value=2.0,   max_value=8.0,   value=def_sc, step=0.1,
                              help="ทั่วไป 4.0–5.5 MPa")
        Cd = st.number_input("Drainage Coefficient (Cd)",   min_value=0.5,   max_value=1.5,   value=def_cd, step=0.05,
                              help="ระบายน้ำดีเยี่ยม=1.25, ดีมาก=1.20, ดี=1.15, พอใช้=1.00, แย่=0.75")
        J  = st.number_input("Load Transfer Coeff (J)",     min_value=1.5,   max_value=5.0,   value=def_j,  step=0.1,
                              help="มี Dowel bar=2.5-3.1, ไม่มี=3.6-4.4")
        k  = st.number_input("Subgrade k (MPa/m)",          min_value=10,    max_value=500,   value=def_k,  step=5,
                              help="27=อ่อน, 54=ปานกลาง, 110=ดี, 220=ดีมาก")

        st.markdown("<br>", unsafe_allow_html=True)
        calc_btn = st.button("▶  คำนวณ / DESIGN NOW", use_container_width=True)

    # ══════════════════════════════════════════════════════
    #  CALCULATION & DISPLAY
    # ══════════════════════════════════════════════════════
    if calc_btn or 'result' in st.session_state:

        if calc_btn:
            with st.spinner("กำลังคำนวณ..."):
                params = dict(aadt=aadt, truck_pct=truck_pct, growth=growth,
                               life=life, R=R, S0=S0, pi=pi, pt=pt,
                               Ec=Ec, Sc=Sc, Cd=Cd, J=J, k=k, ldf=ldf, tff=tff)
                try:
                    st.session_state.result = design(params)
                except Exception as e:
                    st.error(f"เกิดข้อผิดพลาด: {e}")
                    return

        r = st.session_state.result

        # ── Key Metrics ──
        st.markdown('<div class="section-title">📐 ผลการออกแบบ</div>', unsafe_allow_html=True)

        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.markdown(f"""
            <div class="metric-box">
              <div class="metric-label">Concrete Slab</div>
              <div class="metric-value">{r['D_mm']}</div>
              <div class="metric-unit">mm  ({r['D_in']:.2f}")</div>
            </div>""", unsafe_allow_html=True)
        with c2:
            st.markdown(f"""
            <div class="metric-box">
              <div class="metric-label">Subbase</div>
              <div class="metric-value" style="color:#f59e0b">{r['sub_mm']}</div>
              <div class="metric-unit">mm  ({r['sub_mm']/25.4:.2f}")</div>
            </div>""", unsafe_allow_html=True)
        with c3:
            st.markdown(f"""
            <div class="metric-box">
              <div class="metric-label">Subgrade Prep</div>
              <div class="metric-value" style="color:#10b981">{r['sgrd_mm']}</div>
              <div class="metric-unit">mm  ({r['sgrd_mm']/25.4:.2f}")</div>
            </div>""", unsafe_allow_html=True)
        with c4:
            st.markdown(f"""
            <div class="metric-box">
              <div class="metric-label">Total Depth</div>
              <div class="metric-value" style="color:#e2e8f0">{r['total_mm']}</div>
              <div class="metric-unit">mm  ({r['total_mm']/25.4:.2f}")</div>
            </div>""", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        col_left, col_right = st.columns([1.1, 1])

        # ── Cross Section Diagram ──
        with col_left:
            st.markdown('<div class="section-title">📏 หน้าตัดโครงสร้าง</div>', unsafe_allow_html=True)

            total = r['total_mm']
            layers = [
                (r['D_mm'],    '#bfdbfe', '#1d4ed8', '🔷', 'Concrete Slab',
                 f"{r['D_mm']} mm  ·  {r['D_in']:.2f}\""),
                (r['sub_mm'],  '#fef3c7', '#92400e', '🟨', 'Subbase',
                 f"{r['sub_mm']} mm  ·  {r['sub_mm']/25.4:.2f}\""),
                (r['sgrd_mm'], '#d1fae5', '#065f46', '🟩', 'Subgrade Prep',
                 f"{r['sgrd_mm']} mm  ·  {r['sgrd_mm']/25.4:.2f}\""),
            ]

            # Road surface
            st.markdown("""
            <div style="background:#475569; height:10px; border-radius:4px 4px 0 0;
                        text-align:center; font-size:10px; color:#94a3b8;
                        font-family:'JetBrains Mono',monospace; line-height:10px;
                        margin-bottom:2px;">
            </div>
            <div style="text-align:center; font-size:10px; color:#64748b;
                        font-family:'JetBrains Mono',monospace; margin-bottom:4px;">
              ▲ ผิวจราจร (Road Surface)
            </div>
            """, unsafe_allow_html=True)

            for thick, bg, text_col, sym, name, desc in layers:
                pct = thick / total
                height = max(50, int(pct * 280))
                st.markdown(f"""
                <div class="layer-bar" style="background:{bg}; height:{height}px; color:{text_col};">
                  <span>{sym} {name}</span>
                  <span style="font-size:12px;">{desc}</span>
                </div>
                """, unsafe_allow_html=True)

            # Subgrade
            st.markdown("""
            <div style="background:linear-gradient(90deg,#4c1d95,#5b21b6);
                        height:24px; border-radius:0 0 6px 6px;
                        display:flex; align-items:center; justify-content:center;
                        font-family:'JetBrains Mono',monospace;
                        font-size:11px; color:#c4b5fd; margin-top:2px;">
              ▼  Subgrade (ชั้นดินเดิม)
            </div>
            """, unsafe_allow_html=True)

        # ── Calculation Details ──
        with col_right:
            st.markdown('<div class="section-title">🔢 ผลการคำนวณ</div>', unsafe_allow_html=True)

            st.markdown(f"""
            <div class="result-card highlight">
              <div style="font-family:'JetBrains Mono',monospace; font-size:11px;
                          color:#64748b; margin-bottom:8px;">18-kip ESAL สะสม</div>
              <div style="font-family:'JetBrains Mono',monospace; font-size:22px;
                          font-weight:700; color:#fbbf24;">{r['W18']:,.0f}</div>
              <div style="font-size:12px; color:#64748b; margin-top:4px;">ESALs ตลอด {r['p']['life']:.0f} ปี</div>
            </div>
            """, unsafe_allow_html=True)

            items = [
                ("Growth Factor (GF)",    f"{r['gf']:.3f}",        "-"),
                ("ZR",                    f"{r['ZR']:.3f}",        "-"),
                ("ΔPsi",                  f"{r['dPSI']:.1f}",      "-"),
                ("k (แปลงหน่วย)",         f"{r['k_pci']:.1f}",    "pci"),
                ("Ec (แปลงหน่วย)",        f"{r['Ec_psi']:,.0f}",  "psi"),
                ("Sc (แปลงหน่วย)",        f"{r['Sc_psi']:.1f}",   "psi"),
                ("D คำนวณได้",             f"{r['D_calc_mm']:.1f}", "mm"),
                ("D ออกแบบ (ปัดขึ้น 25mm)",f"{r['D_mm']}",        "mm ✓"),
            ]

            rows_html = ""
            for i, (lbl, val, unit) in enumerate(items):
                bg = "#131c2e" if i % 2 == 0 else "#1a2640"
                rows_html += f"""
                <div style="display:flex; justify-content:space-between; align-items:center;
                            background:{bg}; padding:7px 12px; border-radius:4px; margin:2px 0;
                            font-family:'JetBrains Mono',monospace; font-size:12px;">
                  <span style="color:#94a3b8;">{lbl}</span>
                  <span style="color:#e2e8f0; font-weight:600;">{val}
                    <span style="color:#475569; font-size:10px;"> {unit}</span>
                  </span>
                </div>"""
            st.markdown(f'<div class="result-card">{rows_html}</div>', unsafe_allow_html=True)

            # Formula reference
            with st.expander("📐 สมการ AASHTO 1993"):
                st.markdown("""
                <div class="formula-box">
log₁₀(W18) = ZR·S0 + 7.35·log₁₀(D+1) − 0.06<br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;+ log₁₀(ΔPSI/3) / [1 + 1.624×10⁷/(D+1)⁸·⁴⁶]<br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;+ (4.22 − 0.32·pt)·log₁₀(Sc·Cd·(D⁰·⁷⁵−1.132) /<br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[215.63·J·(D⁰·⁷⁵ − 18.42/(Ec/k)⁰·²⁵)])<br><br>
<span style="color:#fbbf24;">D</span> = ความหนาแผ่นคอนกรีต (นิ้ว)<br>
<span style="color:#60a5fa;">W18</span> = 18-kip ESAL สะสม<br>
<span style="color:#34d399;">k</span> = Modulus of Subgrade Reaction (pci)
                </div>
                """, unsafe_allow_html=True)

        # ── Layer Summary Table ──
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="section-title">📋 ตารางสรุปโครงสร้างทาง</div>', unsafe_allow_html=True)

        import pandas as pd
        df = pd.DataFrame({
            'ชั้นทาง':       ['Concrete Slab', 'Subbase', 'Subgrade Prep', '▶ รวมทั้งหมด'],
            'วัสดุ':         ['Portland Cement Concrete', 'Granular / Lean Concrete',
                               'Compacted Subgrade', ''],
            'ความหนา (mm)':  [r['D_mm'], r['sub_mm'], r['sgrd_mm'], r['total_mm']],
            'ความหนา (in)':  [round(r['D_in'],2),
                               round(r['sub_mm']/25.4,2),
                               round(r['sgrd_mm']/25.4,2),
                               round(r['total_mm']/25.4,2)],
        })
        st.dataframe(df, use_container_width=True, hide_index=True,
                      column_config={
                          'ความหนา (mm)': st.column_config.NumberColumn(format="%d mm"),
                          'ความหนา (in)': st.column_config.NumberColumn(format="%.2f in"),
                      })

        # ── PDF Export ──
        st.markdown("<br>", unsafe_allow_html=True)
        col_pdf1, col_pdf2, col_pdf3 = st.columns([1,1,1])
        with col_pdf2:
            try:
                pdf_bytes = make_pdf(r)
                fname = f"AASHTO1993_Design_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"
                st.download_button(
                    label="📄  Download รายงาน PDF",
                    data=pdf_bytes,
                    file_name=fname,
                    mime="application/pdf",
                    use_container_width=True,
                )
            except Exception as e:
                st.error(f"PDF error: {e}")

    else:
        # Placeholder
        st.markdown("""
        <div style="text-align:center; padding:80px 40px;
                    background:#131c2e; border-radius:14px;
                    border:1px dashed #243354; margin-top:20px;">
          <div style="font-size:48px; margin-bottom:16px;">🛣️</div>
          <div style="font-family:'JetBrains Mono',monospace; font-size:16px;
                      color:#3b82f6; font-weight:700; margin-bottom:8px;">
            กรอกข้อมูลในแถบซ้าย
          </div>
          <div style="color:#64748b; font-size:14px;">
            แล้วกดปุ่ม <b style="color:#60a5fa;">▶ คำนวณ</b> เพื่อดูผลการออกแบบทันที
          </div>
          <div style="margin-top:20px; display:flex; gap:8px; justify-content:center; flex-wrap:wrap;">
            <span class="info-tag">AASHTO 1993</span>
            <span class="info-tag">PCC Pavement</span>
            <span class="info-tag">ESAL Calculation</span>
            <span class="info-tag">PDF Report</span>
          </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<br>', unsafe_allow_html=True)
        with st.expander("ℹ️  ข้อมูลโปรแกรม"):
            st.markdown("""
            **โปรแกรมนี้คำนวณอะไร**
            - ✅ 18-kip ESAL สะสมตลอดอายุออกแบบ (พร้อม Growth Factor)
            - ✅ ความหนาแผ่นคอนกรีต ด้วยสมการ AASHTO 1993 (Bisection Method)
            - ✅ ความหนา Subbase ตามค่า k และขนาดแผ่น
            - ✅ ความหนา Subgrade Preparation
            - ✅ Export รายงาน PDF ฉบับสมบูรณ์

            **อ้างอิง**: AASHTO (1993). *Guide for Design of Pavement Structures*.
            American Association of State Highway and Transportation Officials.
            """)


if __name__ == "__main__":
    main()
