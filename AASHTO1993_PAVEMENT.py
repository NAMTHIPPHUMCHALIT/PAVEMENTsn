"""
AASHTO 1993 Pavement Design Tool — Streamlit
ออกแบบโครงสร้างผิวทาง (Rigid & Flexible) ตามมาตรฐาน AASHTO 1993
หน่วยผลลัพธ์: เซนติเมตร (cm)
"""

import streamlit as st
import math
import io
from datetime import datetime

# ══════════════════════════════════════════════════════════════
#  PAGE CONFIG
# ══════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="AASHTO 1993 Pavement Design",
    page_icon="🛣️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ══════════════════════════════════════════════════════════════
#  GLOBAL CSS
# ══════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600;700&family=Sarabun:wght@300;400;600;700&display=swap');

html, body, [data-testid="stAppViewContainer"] {
    background: #080f1e !important;
    font-family: 'Sarabun', sans-serif;
    color: #dde3ed;
}
[data-testid="stSidebar"] {
    background: #0d1526 !important;
    border-right: 1px solid #1c2d4a;
}
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] div { color: #c8d3e6 !important; }

section[data-testid="stSidebarContent"] { padding-top: 1rem; }

h1,h2,h3 { font-family: 'IBM Plex Mono', monospace !important; }

/* Tabs */
[data-baseweb="tab-list"] {
    background: #0d1526 !important;
    border-radius: 10px !important;
    padding: 4px !important;
    gap: 4px !important;
    border: 1px solid #1c2d4a !important;
}
[data-baseweb="tab"] {
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 13px !important;
    font-weight: 600 !important;
    border-radius: 7px !important;
    color: #7a8fad !important;
    background: transparent !important;
    padding: 8px 20px !important;
}
[aria-selected="true"][data-baseweb="tab"] {
    color: #ffffff !important;
}

/* Buttons */
.stButton > button {
    background: linear-gradient(135deg, #1a4fbd 0%, #1e6bff 100%) !important;
    color: #fff !important;
    border: none !important;
    border-radius: 9px !important;
    font-family: 'IBM Plex Mono', monospace !important;
    font-weight: 700 !important;
    font-size: 14px !important;
    padding: 12px 0 !important;
    width: 100% !important;
    letter-spacing: 0.04em !important;
    box-shadow: 0 4px 18px rgba(30,107,255,.35) !important;
    transition: all .2s !important;
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 28px rgba(30,107,255,.55) !important;
}

/* Download button */
[data-testid="stDownloadButton"] > button {
    background: linear-gradient(135deg, #0e6640 0%, #15a058 100%) !important;
    color: #fff !important;
    border: none !important;
    border-radius: 9px !important;
    font-family: 'IBM Plex Mono', monospace !important;
    font-weight: 700 !important;
    font-size: 13px !important;
    padding: 10px 0 !important;
    width: 100% !important;
    box-shadow: 0 4px 14px rgba(21,160,88,.35) !important;
}
[data-testid="stDownloadButton"] > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 22px rgba(21,160,88,.55) !important;
}

/* Metric cards */
.metric-card {
    background: linear-gradient(145deg, #0f1d35, #152540);
    border: 1px solid #1c3158;
    border-radius: 12px;
    padding: 18px 20px 14px;
    text-align: center;
    transition: border-color .25s;
}
.metric-card:hover { border-color: #2d5be0; }
.metric-lbl {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 10px;
    letter-spacing: .12em;
    text-transform: uppercase;
    color: #4a6580;
    margin-bottom: 6px;
}
.metric-val {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 30px;
    font-weight: 700;
    line-height: 1;
}
.metric-unit {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 12px;
    color: #4a6580;
    margin-top: 4px;
}

/* Section headers */
.sec-hdr {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: .14em;
    text-transform: uppercase;
    padding: 6px 12px;
    border-radius: 5px;
    margin: 18px 0 10px;
    display: inline-block;
}
.sec-rigid   { background: rgba(59,130,246,.12); color: #60a5fa; border-left: 3px solid #3b82f6; }
.sec-flex    { background: rgba(245,158,11,.10); color: #fbbf24; border-left: 3px solid #f59e0b; }
.sec-neutral { background: rgba(148,163,184,.08); color: #94a3b8; border-left: 3px solid #475569; }

/* Info panels */
.info-panel {
    background: #0c1828;
    border: 1px solid #1c2d4a;
    border-radius: 10px;
    padding: 14px 18px;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 11px;
    color: #7a90b0;
    line-height: 1.85;
}

/* Layer bar */
.layer-wrap { margin-bottom: 3px; }
.layer-bar {
    border-radius: 7px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 16px;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 12px;
    font-weight: 600;
    border: 1px solid rgba(255,255,255,.07);
}

/* Result row */
.res-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 7px 14px;
    border-radius: 5px;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 12px;
    margin: 2px 0;
}
.res-label { color: #7a90b0; }
.res-value { color: #dde3ed; font-weight: 600; }
.res-unit  { color: #3a4f6a; font-size: 10px; margin-left: 4px; }

/* Top banner */
.top-banner {
    background: linear-gradient(135deg,#0b1930 0%,#122244 50%,#0b1930 100%);
    border: 1px solid #1c3158;
    border-radius: 14px;
    padding: 26px 32px 22px;
    margin-bottom: 22px;
    position: relative;
    overflow: hidden;
}
.top-banner::after {
    content:'';
    position:absolute;
    right:-80px; top:-80px;
    width:260px; height:260px;
    background: radial-gradient(circle, rgba(30,107,255,.12) 0%, transparent 70%);
    pointer-events:none;
}

/* expander */
[data-testid="stExpander"] {
    background: #0d1526 !important;
    border: 1px solid #1c2d4a !important;
    border-radius: 9px !important;
}

hr { border-color: #1c2d4a !important; }
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
#  ─── DESIGN ENGINES ───
# ══════════════════════════════════════════════════════════════

ZR_MAP = {50:0.000, 60:-0.253, 70:-0.524, 75:-0.674, 80:-0.841,
          85:-1.037, 90:-1.282, 91:-1.340, 92:-1.405, 93:-1.476,
          94:-1.555, 95:-1.645, 96:-1.751, 97:-1.881, 98:-2.054,
          99:-2.327}

def get_zr(R):
    return min(ZR_MAP.items(), key=lambda x: abs(x[0]-R))[1]

def calc_esal(aadt, truck_pct, growth, life, ldf, tff):
    r = growth / 100.0
    gf = life if r == 0 else ((1+r)**life - 1) / r
    return aadt * (truck_pct/100) * tff * ldf * 365 * gf, gf

# ── Rigid (JPCP) ─────────────────────────────────────────────
def solve_rigid(W18, ZR, S0, dPSI, pt, Ec_psi, Sc_psi, Cd, J, k_pci):
    """Bisection solve for D (inches) — AASHTO 1993 rigid equation."""
    target = math.log10(max(W18, 1.0))

    def f(D):
        if D <= 0: return -999.0
        try:
            t1 = ZR * S0
            t2 = 7.35 * math.log10(D+1) - 0.06
            t3 = math.log10(dPSI/3.0) / (1 + 1.624e7/(D+1)**8.46)
            inner = D**0.75 - 18.42/(Ec_psi/k_pci)**0.25
            if inner <= 0: return -999.0
            t4 = (4.22 - 0.32*pt) * math.log10(Sc_psi*Cd*(D**0.75 - 1.132)
                                                  / (215.63*J*inner))
            return t1 + t2 + t3 + t4
        except Exception:
            return -999.0

    lo, hi = 2.0, 40.0
    for _ in range(200):
        mid = (lo+hi)/2
        if f(mid) < target: lo = mid
        else:                hi = mid
        if hi-lo < 0.0002:  break
    D_in = (lo+hi)/2
    return D_in, D_in * 2.54  # → cm

# ── Flexible (HMA) ───────────────────────────────────────────
def solve_flexible(W18, ZR, S0, dPSI, pt, MR_psi):
    """Bisection solve for SN — AASHTO 1993 flexible equation."""
    target = math.log10(max(W18, 1.0))

    def f(SN):
        if SN <= 0: return -999.0
        try:
            t1 = ZR * S0
            t2 = 9.36 * math.log10(SN+1) - 0.20
            t3 = math.log10(dPSI/2.7) / (0.4 + 1094/(SN+1)**5.19)
            t4 = 2.32 * math.log10(MR_psi) - 8.07
            return t1 + t2 + t3 + t4
        except Exception:
            return -999.0

    lo, hi = 0.5, 20.0
    for _ in range(200):
        mid = (lo+hi)/2
        if f(mid) < target: lo = mid
        else:                hi = mid
        if hi-lo < 0.0002:  break
    return (lo+hi)/2

def layer_thickness_from_SN(SN, a1, m1, a2, m2, a3, m3,
                              D1_min_cm=5.0, D2_min_cm=10.0, D3_min_cm=10.0):
    def cm_to_in(x): return x / 2.54

    SN1_req = SN * 0.45
    D1_in = max(SN1_req / (a1*m1), cm_to_in(D1_min_cm))
    D1_in = math.ceil(D1_in / (0.5/2.54)) * (0.5/2.54)
    SN1 = a1 * m1 * D1_in

    SN_rem2 = SN - SN1
    if SN_rem2 > 0:
        D2_in = max(SN_rem2 / (a2*m2), cm_to_in(D2_min_cm))
    else:
        D2_in = cm_to_in(D2_min_cm)
    D2_in = math.ceil(D2_in / (1.0/2.54)) * (1.0/2.54)
    SN2 = a2 * m2 * D2_in

    SN_rem3 = SN - SN1 - SN2
    if SN_rem3 > 0:
        D3_in = max(SN_rem3 / (a3*m3), cm_to_in(D3_min_cm))
    else:
        D3_in = cm_to_in(D3_min_cm)
    D3_in = math.ceil(D3_in / (1.0/2.54)) * (1.0/2.54)
    SN3 = a3 * m3 * D3_in

    SN_provided = SN1 + SN2 + SN3

    return (D1_in*2.54, D2_in*2.54, D3_in*2.54,
            SN1, SN2, SN3, SN_provided)

def subgrade_prep_cm(MR_psi):
    if MR_psi < 4000:  return 30.0
    elif MR_psi < 7000: return 20.0
    else:               return 15.0

def run_rigid(p):
    Ec_psi  = p['Ec_MPa'] * 145.038
    Sc_psi  = p['Sc_MPa'] * 145.038
    k_pci   = p['k_MPam'] / 0.2714
    ZR      = get_zr(p['R'])
    dPSI    = p['pi'] - p['pt']
    W18, gf = calc_esal(p['aadt'], p['truck_pct'], p['growth'],
                         p['life'], p['ldf'], p['tff'])

    D_in, D_cm = solve_rigid(W18, ZR, p['S0'], dPSI, p['pt'],
                               Ec_psi, Sc_psi, p['Cd'], p['J'], k_pci)
    D_design_cm = math.ceil(D_cm / 2.5) * 2.5

    if p['k_MPam'] < 27:    sub_cm = 30.0
    elif p['k_MPam'] < 55:  sub_cm = 20.0
    elif p['k_MPam'] < 110: sub_cm = 15.0
    else:                    sub_cm = 10.0
    sgrd_cm = 30.0 if p['k_MPam'] < 27 else (20.0 if p['k_MPam'] < 55 else 15.0)

    return dict(
        type='rigid', W18=W18, gf=gf, ZR=ZR, dPSI=dPSI,
        D_calc_cm=D_cm, D_cm=D_design_cm,
        sub_cm=sub_cm, sgrd_cm=sgrd_cm,
        total_cm=D_design_cm+sub_cm+sgrd_cm,
        Ec_psi=Ec_psi, Sc_psi=Sc_psi, k_pci=k_pci, p=p
    )

def run_flexible(p):
    MR_psi  = p['MR_MPa'] * 145.038
    ZR      = get_zr(p['R'])
    dPSI    = p['pi'] - p['pt']
    W18, gf = calc_esal(p['aadt'], p['truck_pct'], p['growth'],
                         p['life'], p['ldf'], p['tff'])

    SN = solve_flexible(W18, ZR, p['S0'], dPSI, p['pt'], MR_psi)

    D1,D2,D3,SN1,SN2,SN3,SN_prov = layer_thickness_from_SN(
        SN,
        p['a1'], p['m1'], p['a2'], p['m2'], p['a3'], p['m3'],
        p['D1_min'], p['D2_min'], p['D3_min']
    )
    sgrd_cm = subgrade_prep_cm(MR_psi)

    return dict(
        type='flexible', W18=W18, gf=gf, ZR=ZR, dPSI=dPSI,
        SN_req=SN, SN_prov=SN_prov, SN1=SN1, SN2=SN2, SN3=SN3,
        D1_cm=D1, D2_cm=D2, D3_cm=D3,
        sgrd_cm=sgrd_cm,
        total_cm=D1+D2+D3+sgrd_cm,
        MR_psi=MR_psi, p=p
    )


# ══════════════════════════════════════════════════════════════
#  ─── PDF GENERATOR ───
# ══════════════════════════════════════════════════════════════

def make_pdf_rigid(r):
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.lib.units import mm
    from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer,
                                     Table, TableStyle, HRFlowable)
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_CENTER

    p = r['p']
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4,
                             rightMargin=20*mm, leftMargin=20*mm,
                             topMargin=20*mm, bottomMargin=20*mm)

    CB   = colors.HexColor('#0f1f3d')
    CACC = colors.HexColor('#1d4ed8')
    CCON = colors.HexColor('#dbeafe')
    CSUB = colors.HexColor('#fef3c7')
    CSGD = colors.HexColor('#d1fae5')
    CGRY = colors.HexColor('#64748b')

    def PS(n, **kw): return ParagraphStyle(n, **kw)
    TT = PS('TT', fontSize=17, fontName='Helvetica-Bold', textColor=CB, alignment=TA_CENTER, spaceAfter=4)
    ST = PS('ST', fontSize=10, fontName='Helvetica',      textColor=CGRY, alignment=TA_CENTER, spaceAfter=10)
    H  = PS('H',  fontSize=12, fontName='Helvetica-Bold', textColor=CACC, spaceBefore=14, spaceAfter=6)
    N  = PS('N',  fontSize=9,  fontName='Helvetica',      textColor=colors.black, spaceAfter=3)
    NB = PS('NB', fontSize=9,  fontName='Helvetica-Bold', textColor=colors.black)

    story = []
    story.append(Paragraph("รายงานการออกแบบโครงสร้างผิวทางคอนกรีต", TT))
    story.append(Paragraph("Rigid Pavement (JPCP) Design Report  ·  AASHTO 1993", ST))
    story.append(Paragraph(f"วันที่: {datetime.now().strftime('%d/%m/%Y  %H:%M น.')}", ST))
    story.append(HRFlowable(width="100%", thickness=2, color=CACC, spaceAfter=10))

    cw = [90*mm, 45*mm, 25*mm]

    story.append(Paragraph("1. ข้อมูลนำเข้า (Input Parameters)", H))
    rows = [['พารามิเตอร์','ค่า','หน่วย'],
            ['AADT',f"{p['aadt']:,.0f}",'คัน/วัน'],
            ['สัดส่วนรถบรรทุก',f"{p['truck_pct']:.1f}",'%'],
            ['อัตราเติบโต',f"{p['growth']:.1f}",'%/ปี'],
            ['อายุออกแบบ',f"{p['life']:.0f}",'ปี'],
            ['Reliability (R)',f"{p['R']:.0f}",'%'],
            ['S0',f"{p['S0']:.2f}",'-'],
            ['Initial PSI',f"{p['pi']:.1f}",'-'],
            ['Terminal PSI',f"{p['pt']:.1f}",'-'],
            ['Ec',f"{p['Ec_MPa']:,.0f}",'MPa'],
            ['Sc (MR)',f"{p['Sc_MPa']:.2f}",'MPa'],
            ['Cd',f"{p['Cd']:.2f}",'-'],
            ['J',f"{p['J']:.1f}",'-'],
            ['k (subgrade)',f"{p['k_MPam']:.0f}",'MPa/m'],
            ['Lane Dist. Factor',f"{p['ldf']:.2f}",'-'],
            ['Truck Factor',f"{p['tff']:.2f}",'-']]
    t = _make_table(rows, cw, CACC)
    story.append(t)

    story.append(Paragraph("2. ผลการคำนวณกลาง (Intermediate Results)", H))
    rows2 = [['รายการ','ค่า','หน่วย'],
             ['Growth Factor',f"{r['gf']:.3f}",'-'],
             ['ZR',f"{r['ZR']:.3f}",'-'],
             ['ΔPSi',f"{r['dPSI']:.1f}",'-'],
             ['18-kip ESAL',f"{r['W18']:,.0f}",'ESAL'],
             ['k (แปลง)',f"{r['k_pci']:.1f}",'pci'],
             ['Ec (แปลง)',f"{r['Ec_psi']:,.0f}",'psi'],
             ['Sc (แปลง)',f"{r['Sc_psi']:.1f}",'psi'],
             ['D คำนวณ',f"{r['D_calc_cm']:.2f}",'cm'],
             ['D ออกแบบ (ปัดขึ้น 2.5 cm)',f"{r['D_cm']:.1f}",'cm']]
    story.append(_make_table(rows2, cw, colors.HexColor('#0891b2')))

    story.append(Paragraph("3. สรุปความหนาโครงสร้างทาง (Layer Summary)", H))
    rows3 = [['ชั้นทาง','วัสดุ','ความหนา (cm)','ความหนา (mm)'],
             ['Concrete Slab','Portland Cement Concrete',
              f"{r['D_cm']:.1f}", f"{r['D_cm']*10:.0f}"],
             ['Subbase','Granular / Lean Concrete',
              f"{r['sub_cm']:.1f}", f"{r['sub_cm']*10:.0f}"],
             ['Subgrade Prep','Compacted Subgrade',
              f"{r['sgrd_cm']:.1f}", f"{r['sgrd_cm']*10:.0f}"],
             ['รวม / Total','',
              f"{r['total_cm']:.1f}", f"{r['total_cm']*10:.0f}"]]
    cw3=[55*mm,55*mm,25*mm,22*mm]
    t3 = Table(rows3, colWidths=cw3)
    t3.setStyle(TableStyle([
        ('BACKGROUND',(0,0),(-1,0),CB),('TEXTCOLOR',(0,0),(-1,0),colors.white),
        ('FONTNAME',(0,0),(-1,0),'Helvetica-Bold'),('FONTSIZE',(0,0),(-1,-1),9),
        ('BACKGROUND',(0,1),(-1,1),CCON),('BACKGROUND',(0,2),(-1,2),CSUB),
        ('BACKGROUND',(0,3),(-1,3),CSGD),
        ('BACKGROUND',(0,4),(-1,4),CB),('TEXTCOLOR',(0,4),(-1,4),colors.white),
        ('FONTNAME',(0,4),(-1,4),'Helvetica-Bold'),
        ('GRID',(0,0),(-1,-1),0.4,colors.grey),
        ('ALIGN',(2,0),(-1,-1),'CENTER'),('VALIGN',(0,0),(-1,-1),'MIDDLE'),
        ('TOPPADDING',(0,0),(-1,-1),5),('BOTTOMPADDING',(0,0),(-1,-1),5),
    ]))
    story.append(t3)

    _add_notes(story, N, NB, 'rigid')
    doc.build(story)
    buf.seek(0)
    return buf.read()


def make_pdf_flexible(r):
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.lib.units import mm
    from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer,
                                     Table, TableStyle, HRFlowable)
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_CENTER

    p = r['p']
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4,
                             rightMargin=20*mm, leftMargin=20*mm,
                             topMargin=20*mm, bottomMargin=20*mm)

    CB   = colors.HexColor('#1a1200')
    CACC = colors.HexColor('#b45309')
    CHMA = colors.HexColor('#fde68a')
    CBAS = colors.HexColor('#fed7aa')
    CSUB = colors.HexColor('#d1fae5')
    CSGD = colors.HexColor('#e0e7ff')
    CGRY = colors.HexColor('#64748b')

    def PS(n, **kw): return ParagraphStyle(n, **kw)
    TT = PS('TT2', fontSize=17, fontName='Helvetica-Bold', textColor=colors.HexColor('#1c0a00'), alignment=TA_CENTER, spaceAfter=4)
    ST = PS('ST2', fontSize=10, fontName='Helvetica', textColor=CGRY, alignment=TA_CENTER, spaceAfter=10)
    H  = PS('H2',  fontSize=12, fontName='Helvetica-Bold', textColor=CACC, spaceBefore=14, spaceAfter=6)
    N  = PS('N2',  fontSize=9,  fontName='Helvetica', textColor=colors.black, spaceAfter=3)
    NB = PS('NB2', fontSize=9,  fontName='Helvetica-Bold', textColor=colors.black)

    story = []
    story.append(Paragraph("รายงานการออกแบบโครงสร้างผิวทางยืดหยุ่น", TT))
    story.append(Paragraph("Flexible Pavement (HMA) Design Report  ·  AASHTO 1993", ST))
    story.append(Paragraph(f"วันที่: {datetime.now().strftime('%d/%m/%Y  %H:%M น.')}", ST))
    story.append(HRFlowable(width="100%", thickness=2, color=CACC, spaceAfter=10))

    cw = [90*mm, 45*mm, 25*mm]

    story.append(Paragraph("1. ข้อมูลนำเข้า (Input Parameters)", H))
    rows = [['พารามิเตอร์','ค่า','หน่วย'],
            ['AADT',f"{p['aadt']:,.0f}",'คัน/วัน'],
            ['สัดส่วนรถบรรทุก',f"{p['truck_pct']:.1f}",'%'],
            ['อัตราเติบโต',f"{p['growth']:.1f}",'%/ปี'],
            ['อายุออกแบบ',f"{p['life']:.0f}",'ปี'],
            ['Reliability (R)',f"{p['R']:.0f}",'%'],
            ['S0',f"{p['S0']:.2f}",'-'],
            ['Initial PSI',f"{p['pi']:.1f}",'-'],
            ['Terminal PSI',f"{p['pt']:.1f}",'-'],
            ['Resilient Modulus (MR)',f"{p['MR_MPa']:.0f}",'MPa'],
            ['a1 (HMA surface coeff)',f"{p['a1']:.3f}",'-'],
            ['a2 (Base coeff)',f"{p['a2']:.3f}",'-'],
            ['a3 (Subbase coeff)',f"{p['a3']:.3f}",'-'],
            ['m1/m2/m3',f"{p['m1']:.2f}/{p['m2']:.2f}/{p['m3']:.2f}",'-'],
            ['Lane Dist. Factor',f"{p['ldf']:.2f}",'-'],
            ['Truck Factor',f"{p['tff']:.2f}",'-']]
    story.append(_make_table(rows, cw, CACC))

    story.append(Paragraph("2. ผลการคำนวณกลาง (Intermediate Results)", H))
    rows2 = [['รายการ','ค่า','หน่วย'],
             ['Growth Factor',f"{r['gf']:.3f}",'-'],
             ['ZR',f"{r['ZR']:.3f}",'-'],
             ['ΔPSi',f"{r['dPSI']:.1f}",'-'],
             ['18-kip ESAL',f"{r['W18']:,.0f}",'ESAL'],
             ['MR (แปลง)',f"{r['MR_psi']:,.0f}",'psi'],
             ['SN ที่ต้องการ (required)',f"{r['SN_req']:.2f}",'-'],
             ['SN ที่ได้ (provided)',f"{r['SN_prov']:.2f}",'-'],
             ['SN1 (surface)',f"{r['SN1']:.2f}",'-'],
             ['SN2 (base)',f"{r['SN2']:.2f}",'-'],
             ['SN3 (subbase)',f"{r['SN3']:.2f}",'-']]
    story.append(_make_table(rows2, cw, colors.HexColor('#0891b2')))

    story.append(Paragraph("3. สรุปความหนาโครงสร้างทาง (Layer Summary)", H))
    rows3 = [['ชั้นทาง','วัสดุ','ความหนา (cm)','ความหนา (mm)'],
             ['ชั้น HMA Surface','Hot Mix Asphalt',
              f"{r['D1_cm']:.1f}", f"{r['D1_cm']*10:.0f}"],
             ['ชั้น Base Course','Crushed Stone / Gravel Base',
              f"{r['D2_cm']:.1f}", f"{r['D2_cm']*10:.0f}"],
             ['ชั้น Subbase','Granular Subbase',
              f"{r['D3_cm']:.1f}", f"{r['D3_cm']*10:.0f}"],
             ['Subgrade Prep','Compacted Subgrade',
              f"{r['sgrd_cm']:.1f}", f"{r['sgrd_cm']*10:.0f}"],
             ['รวม / Total','',
              f"{r['total_cm']:.1f}", f"{r['total_cm']*10:.0f}"]]
    cw3=[55*mm,55*mm,25*mm,22*mm]
    t3 = Table(rows3, colWidths=cw3)
    t3.setStyle(TableStyle([
        ('BACKGROUND',(0,0),(-1,0),colors.HexColor('#1a1200')),
        ('TEXTCOLOR',(0,0),(-1,0),colors.white),
        ('FONTNAME',(0,0),(-1,0),'Helvetica-Bold'),
        ('FONTSIZE',(0,0),(-1,-1),9),
        ('BACKGROUND',(0,1),(-1,1),CHMA),
        ('BACKGROUND',(0,2),(-1,2),CBAS),
        ('BACKGROUND',(0,3),(-1,3),CSUB),
        ('BACKGROUND',(0,4),(-1,4),CSGD),
        ('BACKGROUND',(0,5),(-1,5),colors.HexColor('#1a1200')),
        ('TEXTCOLOR',(0,5),(-1,5),colors.white),
        ('FONTNAME',(0,5),(-1,5),'Helvetica-Bold'),
        ('GRID',(0,0),(-1,-1),0.4,colors.grey),
        ('ALIGN',(2,0),(-1,-1),'CENTER'),
        ('VALIGN',(0,0),(-1,-1),'MIDDLE'),
        ('TOPPADDING',(0,0),(-1,-1),5),
        ('BOTTOMPADDING',(0,0),(-1,-1),5),
    ]))
    story.append(t3)

    _add_notes(story, N, NB, 'flexible')
    doc.build(story)
    buf.seek(0)
    return buf.read()


def _make_table(rows, cw, hdr_color):
    from reportlab.lib import colors
    from reportlab.platypus import Table, TableStyle
    CLIT = colors.HexColor('#f0f7ff')
    t = Table(rows, colWidths=cw)
    t.setStyle(TableStyle([
        ('BACKGROUND',(0,0),(-1,0), hdr_color),
        ('TEXTCOLOR',(0,0),(-1,0),colors.white),
        ('FONTNAME',(0,0),(-1,0),'Helvetica-Bold'),
        ('FONTSIZE',(0,0),(-1,-1),9),
        ('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white, CLIT]),
        ('GRID',(0,0),(-1,-1),0.4,colors.lightgrey),
        ('ALIGN',(1,0),(-1,-1),'CENTER'),
        ('VALIGN',(0,0),(-1,-1),'MIDDLE'),
        ('TOPPADDING',(0,0),(-1,-1),4),
        ('BOTTOMPADDING',(0,0),(-1,-1),4),
    ]))
    return t


def _add_notes(story, N, NB, ptype):
    from reportlab.lib import colors
    from reportlab.platypus import HRFlowable, Spacer
    story.append(Spacer(1, 6))
    story.append(HRFlowable(width="100%", thickness=1,
                             color=colors.HexColor('#94a3b8'), spaceAfter=6))
    story.append(Paragraph("หมายเหตุ / Notes", NB))
    notes_rigid = [
        "• ออกแบบตาม AASHTO 1993 Guide for Design of Pavement Structures",
        "• ความหนาแผ่นคอนกรีตปัดขึ้นทุก 2.5 cm",
        "• ค่า k ที่ใช้คือ Composite k หลังวาง Subbase",
        "• ESAL = AADT x Truck% x LDF x TFF x 365 x GF",
        "• หน่วยความหนาในรายงาน: เซนติเมตร (cm)",
    ]
    notes_flex = [
        "• ออกแบบตาม AASHTO 1993 Guide for Design of Pavement Structures",
        "• SN แจกแจงเป็น D1, D2, D3 ตามขั้นตอน Layer-by-Layer",
        "• ความหนาแต่ละชั้นปัดขึ้นตามมาตรฐาน",
        "• ESAL = AADT x Truck% x LDF x TFF x 365 x GF",
        "• หน่วยความหนาในรายงาน: เซนติเมตร (cm)",
    ]
    notes = notes_rigid if ptype == 'rigid' else notes_flex
    for n in notes:
        story.append(Paragraph(n, N))


# ══════════════════════════════════════════════════════════════
#  ─── UI HELPERS ───
# ══════════════════════════════════════════════════════════════

def section(label, cls='sec-neutral'):
    st.markdown(f'<div class="sec-hdr {cls}">{label}</div>', unsafe_allow_html=True)

def metric_card(label, value, unit, color='#3b82f6'):
    st.markdown(f"""
    <div class="metric-card">
      <div class="metric-lbl">{label}</div>
      <div class="metric-val" style="color:{color}">{value}</div>
      <div class="metric-unit">{unit}</div>
    </div>""", unsafe_allow_html=True)

def res_row(label, value, unit, even=True):
    bg = '#0c1828' if even else '#101e32'
    st.markdown(f"""
    <div class="res-row" style="background:{bg}">
      <span class="res-label">{label}</span>
      <span class="res-value">{value}<span class="res-unit">{unit}</span></span>
    </div>""", unsafe_allow_html=True)

def draw_rigid_section(r):
    total = r['total_cm']
    layers = [
        (r['D_cm'],    '#bfdbfe','#1d4ed8', '▦ Concrete Slab',
         f"{r['D_cm']:.1f} cm"),
        (r['sub_cm'],  '#fef3c7','#92400e', '▩ Subbase',
         f"{r['sub_cm']:.1f} cm"),
        (r['sgrd_cm'], '#d1fae5','#065f46', '▪ Subgrade Prep',
         f"{r['sgrd_cm']:.1f} cm"),
    ]
    _draw_layers(layers, total)

def draw_flex_section(r):
    total = r['total_cm']
    layers = [
        (r['D1_cm'],   '#1c1400','#fbbf24', '▦ HMA Surface',
         f"{r['D1_cm']:.1f} cm"),
        (r['D2_cm'],   '#451a03','#fb923c', '▩ Base Course',
         f"{r['D2_cm']:.1f} cm"),
        (r['D3_cm'],   '#d1fae5','#065f46', '▪ Subbase',
         f"{r['D3_cm']:.1f} cm"),
        (r['sgrd_cm'], '#e0e7ff','#3730a3', '● Subgrade Prep',
         f"{r['sgrd_cm']:.1f} cm"),
    ]
    _draw_layers(layers, total)

def _draw_layers(layers, total):
    st.markdown("""
    <div style="background:#334155;height:8px;border-radius:5px 5px 0 0;
                margin-bottom:2px;"></div>
    <div style="text-align:center;font-family:'IBM Plex Mono',monospace;
                font-size:10px;color:#64748b;margin-bottom:6px;">
      ▲ ผิวจราจร (Road Surface)</div>
    """, unsafe_allow_html=True)
    for thick, bg, tc, name, desc in layers:
        pct = thick / total
        h = max(44, int(pct * 300))
        st.markdown(f"""
        <div class="layer-wrap">
          <div class="layer-bar" style="background:{bg};height:{h}px;color:{tc};">
            <span>{name}</span><span style="font-size:13px;">{desc}</span>
          </div>
        </div>""", unsafe_allow_html=True)
    st.markdown("""
    <div style="background:linear-gradient(90deg,#312e81,#4338ca);
                height:22px;border-radius:0 0 6px 6px;margin-top:2px;
                display:flex;align-items:center;justify-content:center;
                font-family:'IBM Plex Mono',monospace;font-size:10px;color:#a5b4fc;">
      ▼ Subgrade (ชั้นดินเดิม)</div>
    """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
#  ─── SIDEBAR INPUT FUNCTION (with unique key prefix) ───
# ══════════════════════════════════════════════════════════════

def sidebar_traffic(prefix=""):
    """
    Render traffic & reliability inputs in sidebar.
    prefix: unique string ('r_' for Rigid, 'f_' for Flexible)
    to avoid duplicate widget IDs.
    """
    st.markdown(f'<div class="sec-hdr sec-neutral">🚛 ข้อมูลจราจร</div>',
                unsafe_allow_html=True)
    aadt  = st.number_input("AADT (คัน/วัน)", 100, 1000000, 8000, 100,
                             key=f"{prefix}aadt")
    tp    = st.number_input("สัดส่วนรถบรรทุก (%)", 1.0, 100.0, 15.0, 0.5,
                             key=f"{prefix}truck_pct")
    gr    = st.number_input("อัตราเติบโตจราจร (%/ปี)", 0.0, 20.0, 3.0, 0.5,
                             key=f"{prefix}growth")
    life  = st.number_input("อายุออกแบบ (ปี)", 5, 50, 20, 5,
                             key=f"{prefix}life")
    ldf   = st.number_input("Lane Distribution Factor", 0.1, 1.0, 0.5, 0.05,
                             help="0.4–0.9 ตามจำนวนช่องจราจร",
                             key=f"{prefix}ldf")
    tff   = st.number_input("Truck Factor (ESAL/truck)", 0.1, 15.0, 1.0, 0.1,
                             help="Equivalency Factor เฉลี่ยสำหรับรถบรรทุก",
                             key=f"{prefix}tff")
    st.markdown('<div class="sec-hdr sec-neutral">📊 ความน่าเชื่อถือ</div>',
                unsafe_allow_html=True)
    R_opts = [50,60,70,75,80,85,90,91,92,93,94,95,96,97,98,99]
    R  = st.selectbox("Reliability R (%)", R_opts, index=R_opts.index(95),
                       help="ทางสายหลัก 95-99% | ทางรอง 80-90%",
                       key=f"{prefix}R")
    S0 = st.number_input("Overall Std Dev (S0)", 0.20, 0.50, 0.35, 0.01,
                          key=f"{prefix}S0")
    pi = st.number_input("Initial PSI (pi)", 3.0, 5.0, 4.5, 0.1,
                          key=f"{prefix}pi")
    pt = st.number_input("Terminal PSI (pt)", 1.5, 3.5, 2.5, 0.1,
                          key=f"{prefix}pt")
    return dict(aadt=aadt, truck_pct=tp, growth=gr, life=life,
                ldf=ldf, tff=tff, R=R, S0=S0, pi=pi, pt=pt)


# ══════════════════════════════════════════════════════════════
#  ─── MAIN APP ───
# ══════════════════════════════════════════════════════════════

def main():
    # Banner
    st.markdown("""
    <div class="top-banner">
      <div style="font-family:'IBM Plex Mono',monospace;font-size:11px;
                  color:#3b82f6;letter-spacing:.18em;margin-bottom:6px;">
        AASHTO 1993 STANDARD
      </div>
      <div style="font-family:'IBM Plex Mono',monospace;font-size:26px;
                  font-weight:700;color:#e2e8f0;line-height:1.2;">
        Pavement Design Tool
      </div>
      <div style="font-size:15px;color:#7a90b0;margin-top:6px;">
        ออกแบบโครงสร้างผิวทางคอนกรีต (Rigid) และผิวทางยืดหยุ่น (Flexible) &nbsp;·&nbsp; ผลลัพธ์หน่วย <b style="color:#60a5fa;">เซนติเมตร</b>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Tab selector ─────────────────────────────────────────
    tab_rigid, tab_flex = st.tabs([
        "🔷  Rigid Pavement (คอนกรีต)",
        "🟧  Flexible Pavement (แอสฟัลต์)"
    ])

    # ═══════════════════════════════════════════════════════
    #  TAB 1 — RIGID
    #  All sidebar widgets for Rigid go inside this tab's
    #  with-block so they only render when tab is active,
    #  and they all carry prefix "r_" for unique keys.
    # ═══════════════════════════════════════════════════════
    with tab_rigid:
        with st.sidebar:
            st.markdown("""
            <div style="font-family:'IBM Plex Mono',monospace;font-size:12px;
                        font-weight:700;color:#60a5fa;padding:6px 0 14px;
                        border-bottom:1px solid #1c2d4a;margin-bottom:14px;">
              ⚙️  ข้อมูลนำเข้า — Rigid
            </div>""", unsafe_allow_html=True)

            # Traffic inputs with "r_" prefix
            traffic_r = sidebar_traffic(prefix="r_")

            st.markdown('<div class="sec-hdr sec-rigid">🏗️ คุณสมบัติวัสดุ — Rigid</div>',
                        unsafe_allow_html=True)

            preset_r = st.selectbox("Preset วัสดุ (Rigid)",
                                     ["มาตรฐานทั่วไป","คุณภาพสูง","ดินฐานอ่อน","กำหนดเอง"],
                                     key='r_preset')
            pdata = {"มาตรฐานทั่วไป":(27500,4.50,1.00,3.2,54),
                     "คุณภาพสูง":    (30000,5.00,1.10,2.8,80),
                     "ดินฐานอ่อน":  (25000,4.20,0.90,3.8,27),
                     "กำหนดเอง":     (27500,4.50,1.00,3.2,54)}
            dec,dsc,dcd,dj,dk = pdata[preset_r]

            Ec   = st.number_input("Elastic Modulus Ec (MPa)", 10000, 50000, dec, 500,
                                    help="ทั่วไป 20,000–35,000 MPa", key='r_Ec')
            Sc   = st.number_input("Modulus of Rupture Sc (MPa)", 2.0, 8.0, dsc, 0.1,
                                    help="ทั่วไป 4.0–5.5 MPa", key='r_Sc')
            Cd   = st.number_input("Drainage Coeff (Cd)", 0.5, 1.5, dcd, 0.05,
                                    help="ดีเยี่ยม=1.25 | ดี=1.15 | พอใช้=1.00 | แย่=0.75",
                                    key='r_Cd')
            J    = st.number_input("Load Transfer (J)", 1.5, 5.0, dj, 0.1,
                                    help="มี Dowel bar=2.5-3.1 | ไม่มี=3.6-4.4",
                                    key='r_J')
            k    = st.number_input("Subgrade k (MPa/m)", 10, 500, dk, 5,
                                    help="27=อ่อน | 54=ปานกลาง | 110=ดี | 220=ดีมาก",
                                    key='r_k')

            st.markdown("<br>", unsafe_allow_html=True)
            calc_r = st.button("▶  คำนวณ Rigid Pavement", key='btn_r')

        if calc_r:
            p = {**traffic_r, 'Ec_MPa':Ec, 'Sc_MPa':Sc, 'Cd':Cd, 'J':J, 'k_MPam':k}
            with st.spinner("กำลังคำนวณ..."):
                try:
                    st.session_state['res_rigid'] = run_rigid(p)
                except Exception as e:
                    st.error(f"เกิดข้อผิดพลาด: {e}")

        if 'res_rigid' in st.session_state:
            _show_rigid_results(st.session_state['res_rigid'])

    # ═══════════════════════════════════════════════════════
    #  TAB 2 — FLEXIBLE
    #  All sidebar widgets carry prefix "f_" for unique keys.
    # ═══════════════════════════════════════════════════════
    with tab_flex:
        with st.sidebar:
            st.markdown("""
            <div style="font-family:'IBM Plex Mono',monospace;font-size:12px;
                        font-weight:700;color:#fbbf24;padding:6px 0 14px;
                        border-bottom:1px solid #1c2d4a;margin-bottom:14px;">
              ⚙️  ข้อมูลนำเข้า — Flexible
            </div>""", unsafe_allow_html=True)

            # Traffic inputs with "f_" prefix
            traffic_f = sidebar_traffic(prefix="f_")

            st.markdown('<div class="sec-hdr sec-flex">🛞 คุณสมบัติวัสดุ — Flexible</div>',
                        unsafe_allow_html=True)

            preset_f = st.selectbox("Preset วัสดุ (Flexible)",
                                     ["มาตรฐานทั่วไป","ปริมาณจราจรมาก","ดินฐานอ่อน","กำหนดเอง"],
                                     key='f_preset')
            fdata = {
                "มาตรฐานทั่วไป": (69, 0.44,0.14,0.11,1.0,1.0,1.0, 5,15,15),
                "ปริมาณจราจรมาก":(100,0.44,0.18,0.13,1.0,1.0,1.0, 7,20,20),
                "ดินฐานอ่อน":    (34, 0.42,0.12,0.10,0.9,0.8,0.8, 5,20,20),
                "กำหนดเอง":      (69, 0.44,0.14,0.11,1.0,1.0,1.0, 5,15,15),
            }
            dmr,da1,da2,da3,dm1,dm2,dm3,dd1,dd2,dd3 = fdata[preset_f]

            MR = st.number_input("Resilient Modulus MR (MPa)", 10, 300, dmr, 1,
                                  help="อ่อน~34MPa | ปานกลาง~69MPa | แข็ง~138MPa",
                                  key='f_MR')
            st.markdown("**Layer Coefficients & Drainage Factors**")
            c1, c2 = st.columns(2)
            with c1:
                a1 = st.number_input("a1 (HMA)", 0.20, 0.60, da1, 0.01, key='f_a1',
                                      help="Structural coefficient ชั้น HMA")
                a2 = st.number_input("a2 (Base)", 0.05, 0.40, da2, 0.01, key='f_a2')
                a3 = st.number_input("a3 (Subbase)", 0.03, 0.25, da3, 0.01, key='f_a3')
            with c2:
                m1 = st.number_input("m1", 0.4, 1.4, dm1, 0.05, key='f_m1',
                                      help="Drainage factor ชั้น HMA")
                m2 = st.number_input("m2", 0.4, 1.4, dm2, 0.05, key='f_m2')
                m3 = st.number_input("m3", 0.4, 1.4, dm3, 0.05, key='f_m3')

            st.markdown("**ความหนาขั้นต่ำแต่ละชั้น (cm)**")
            c3, c4, c5 = st.columns(3)
            with c3: d1m = st.number_input("HMA min",  2.5, 25.0, float(dd1), 2.5, key='f_d1m')
            with c4: d2m = st.number_input("Base min",  5.0, 50.0, float(dd2), 2.5, key='f_d2m')
            with c5: d3m = st.number_input("Sub min",   5.0, 50.0, float(dd3), 2.5, key='f_d3m')

            st.markdown("<br>", unsafe_allow_html=True)
            calc_f = st.button("▶  คำนวณ Flexible Pavement", key='btn_f')

        if calc_f:
            p2 = {**traffic_f,
                  'MR_MPa':MR,
                  'a1':a1,'a2':a2,'a3':a3,
                  'm1':m1,'m2':m2,'m3':m3,
                  'D1_min':d1m,'D2_min':d2m,'D3_min':d3m}
            with st.spinner("กำลังคำนวณ..."):
                try:
                    st.session_state['res_flex'] = run_flexible(p2)
                except Exception as e:
                    st.error(f"เกิดข้อผิดพลาด: {e}")

        if 'res_flex' in st.session_state:
            _show_flex_results(st.session_state['res_flex'])


# ══════════════════════════════════════════════════════════════
#  ─── RESULT DISPLAY FUNCTIONS ───
# ══════════════════════════════════════════════════════════════

def _show_rigid_results(r):
    st.markdown('<div class="sec-hdr sec-rigid">📐 ผลการออกแบบ — Rigid Pavement</div>',
                unsafe_allow_html=True)

    c1,c2,c3,c4 = st.columns(4)
    with c1: metric_card("Concrete Slab", f"{r['D_cm']:.1f}", "cm", "#60a5fa")
    with c2: metric_card("Subbase",        f"{r['sub_cm']:.1f}", "cm", "#f59e0b")
    with c3: metric_card("Subgrade Prep",  f"{r['sgrd_cm']:.1f}", "cm", "#10b981")
    with c4: metric_card("Total Depth",    f"{r['total_cm']:.1f}", "cm", "#e2e8f0")

    st.markdown("<br>", unsafe_allow_html=True)
    col_l, col_r = st.columns([1.05, 1])

    with col_l:
        st.markdown('<div class="sec-hdr sec-rigid">📏 หน้าตัดโครงสร้าง</div>',
                    unsafe_allow_html=True)
        draw_rigid_section(r)

    with col_r:
        st.markdown('<div class="sec-hdr sec-rigid">🔢 ผลการคำนวณ</div>',
                    unsafe_allow_html=True)

        st.markdown(f"""
        <div style="background:linear-gradient(135deg,#0c1e3a,#122540);
                    border:1px solid #1c3158;border-radius:10px;
                    padding:16px 20px;margin-bottom:10px;">
          <div style="font-family:'IBM Plex Mono',monospace;font-size:10px;
                      color:#4a6580;letter-spacing:.1em;margin-bottom:6px;">
            18-kip ESAL สะสม</div>
          <div style="font-family:'IBM Plex Mono',monospace;font-size:24px;
                      font-weight:700;color:#fbbf24;">{r['W18']:,.0f}</div>
          <div style="font-size:12px;color:#4a6580;margin-top:4px;">
            ESALs ตลอด {r['p']['life']:.0f} ปี &nbsp;·&nbsp; GF = {r['gf']:.3f}</div>
        </div>""", unsafe_allow_html=True)

        items = [("ZR",f"{r['ZR']:.3f}","-"),
                 ("ΔPsi",f"{r['dPSI']:.1f}","-"),
                 ("k",f"{r['k_pci']:.1f}","pci"),
                 ("Ec",f"{r['Ec_psi']:,.0f}","psi"),
                 ("Sc",f"{r['Sc_psi']:.1f}","psi"),
                 ("D คำนวณ",f"{r['D_calc_cm']:.2f}","cm"),
                 ("D ออกแบบ ✓",f"{r['D_cm']:.1f}","cm"),
                 ("Subbase",f"{r['sub_cm']:.1f}","cm"),
                 ("Subgrade Prep",f"{r['sgrd_cm']:.1f}","cm"),
                 ("Total",f"{r['total_cm']:.1f}","cm")]
        for i,(lb,v,u) in enumerate(items):
            res_row(lb, v, u, i%2==0)

        with st.expander("📐 สมการ AASHTO 1993 Rigid"):
            st.markdown("""
            <div class="info-panel">
log10(W18) = ZR·S0 + 7.35·log10(D+1) − 0.06<br>
&nbsp;+ log10(ΔPSI/3) / [1 + 1.624e7/(D+1)<sup>8.46</sup>]<br>
&nbsp;+ (4.22−0.32·pt)·log10(Sc·Cd·(D<sup>0.75</sup>−1.132) /<br>
&nbsp;&nbsp;&nbsp;[215.63·J·(D<sup>0.75</sup> − 18.42/(Ec/k)<sup>0.25</sup>)])<br><br>
<span style="color:#fbbf24;">D</span> = ความหนาแผ่นคอนกรีต (นิ้ว)<br>
<span style="color:#60a5fa;">k</span> = Modulus of Subgrade Reaction (pci)
            </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="sec-hdr sec-rigid">📋 ตารางสรุปโครงสร้างทาง</div>',
                unsafe_allow_html=True)
    import pandas as pd
    df = pd.DataFrame({
        'ชั้นทาง':        ['Concrete Slab','Subbase','Subgrade Prep','▶ รวม'],
        'วัสดุ':          ['Portland Cement Concrete','Granular / Lean Concrete',
                            'Compacted Subgrade',''],
        'ความหนา (cm)':  [r['D_cm'], r['sub_cm'], r['sgrd_cm'], r['total_cm']],
        'ความหนา (mm)':  [r['D_cm']*10, r['sub_cm']*10, r['sgrd_cm']*10, r['total_cm']*10],
    })
    st.dataframe(df, use_container_width=True, hide_index=True,
                  column_config={
                      'ความหนา (cm)': st.column_config.NumberColumn(format="%.1f cm"),
                      'ความหนา (mm)': st.column_config.NumberColumn(format="%.0f mm"),
                  })

    st.markdown("<br>", unsafe_allow_html=True)
    _,mid,_ = st.columns([1,1.2,1])
    with mid:
        try:
            pdf = make_pdf_rigid(r)
            fname = f"Rigid_AASHTO1993_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"
            st.download_button("📄  Download รายงาน PDF (Rigid)", pdf, fname,
                                "application/pdf", use_container_width=True)
        except Exception as e:
            st.error(f"PDF error: {e}")


def _show_flex_results(r):
    st.markdown('<div class="sec-hdr sec-flex">📐 ผลการออกแบบ — Flexible Pavement</div>',
                unsafe_allow_html=True)

    c1,c2,c3,c4,c5 = st.columns(5)
    with c1: metric_card("HMA Surface",  f"{r['D1_cm']:.1f}", "cm", "#fbbf24")
    with c2: metric_card("Base Course",  f"{r['D2_cm']:.1f}", "cm", "#fb923c")
    with c3: metric_card("Subbase",       f"{r['D3_cm']:.1f}", "cm", "#34d399")
    with c4: metric_card("Subgrade Prep", f"{r['sgrd_cm']:.1f}", "cm", "#818cf8")
    with c5: metric_card("Total Depth",   f"{r['total_cm']:.1f}", "cm", "#e2e8f0")

    st.markdown("<br>", unsafe_allow_html=True)
    col_l, col_r = st.columns([1.05, 1])

    with col_l:
        st.markdown('<div class="sec-hdr sec-flex">📏 หน้าตัดโครงสร้าง</div>',
                    unsafe_allow_html=True)
        draw_flex_section(r)

    with col_r:
        st.markdown('<div class="sec-hdr sec-flex">🔢 ผลการคำนวณ</div>',
                    unsafe_allow_html=True)

        sn_ok = r['SN_prov'] >= r['SN_req']
        sn_color = "#34d399" if sn_ok else "#f87171"
        st.markdown(f"""
        <div style="background:linear-gradient(135deg,#1a1200,#241a00);
                    border:1px solid #3d2e00;border-radius:10px;
                    padding:16px 20px;margin-bottom:10px;">
          <div style="font-family:'IBM Plex Mono',monospace;font-size:10px;
                      color:#78550a;letter-spacing:.1em;margin-bottom:4px;">
            18-kip ESAL สะสม</div>
          <div style="font-family:'IBM Plex Mono',monospace;font-size:24px;
                      font-weight:700;color:#fbbf24;">{r['W18']:,.0f}</div>
          <div style="font-size:12px;color:#78550a;margin-top:6px;">
            GF = {r['gf']:.3f} &nbsp;·&nbsp;
            <span style="color:{sn_color};">SN ต้องการ {r['SN_req']:.2f} → ได้ {r['SN_prov']:.2f}
            {'✓' if sn_ok else '✗'}</span>
          </div>
        </div>""", unsafe_allow_html=True)

        items = [("ZR",f"{r['ZR']:.3f}","-"),
                 ("ΔPsi",f"{r['dPSI']:.1f}","-"),
                 ("MR",f"{r['MR_psi']:,.0f}","psi"),
                 ("SN required",f"{r['SN_req']:.3f}","-"),
                 ("SN provided",f"{r['SN_prov']:.3f}","-"),
                 ("SN1 (HMA)",f"{r['SN1']:.3f}","-"),
                 ("SN2 (Base)",f"{r['SN2']:.3f}","-"),
                 ("SN3 (Subbase)",f"{r['SN3']:.3f}","-"),
                 ("HMA D1",f"{r['D1_cm']:.1f}","cm"),
                 ("Base D2",f"{r['D2_cm']:.1f}","cm"),
                 ("Subbase D3",f"{r['D3_cm']:.1f}","cm"),
                 ("Subgrade Prep",f"{r['sgrd_cm']:.1f}","cm"),
                 ("Total",f"{r['total_cm']:.1f}","cm")]
        for i,(lb,v,u) in enumerate(items):
            res_row(lb, v, u, i%2==0)

        with st.expander("📐 สมการ AASHTO 1993 Flexible"):
            st.markdown("""
            <div class="info-panel">
log10(W18) = ZR·S0 + 9.36·log10(SN+1) − 0.20<br>
&nbsp;+ log10(ΔPSI/2.7) / [0.4 + 1094/(SN+1)<sup>5.19</sup>]<br>
&nbsp;+ 2.32·log10(MR) − 8.07<br><br>
<span style="color:#fbbf24;">SN</span> = Structural Number<br>
<span style="color:#fb923c;">SN = a1·D1·m1 + a2·D2·m2 + a3·D3·m3</span><br>
<span style="color:#34d399;">MR</span> = Resilient Modulus (psi)
            </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="sec-hdr sec-flex">📋 ตารางสรุปโครงสร้างทาง</div>',
                unsafe_allow_html=True)
    import pandas as pd
    df = pd.DataFrame({
        'ชั้นทาง':        ['HMA Surface','Base Course','Subbase','Subgrade Prep','▶ รวม'],
        'วัสดุ':          ['Hot Mix Asphalt','Crushed Stone / Gravel Base',
                            'Granular Subbase','Compacted Subgrade',''],
        'ความหนา (cm)':  [r['D1_cm'],r['D2_cm'],r['D3_cm'],r['sgrd_cm'],r['total_cm']],
        'ความหนา (mm)':  [r['D1_cm']*10,r['D2_cm']*10,r['D3_cm']*10,r['sgrd_cm']*10,r['total_cm']*10],
        'SN':             [f"{r['SN1']:.3f}",f"{r['SN2']:.3f}",f"{r['SN3']:.3f}",'-',
                            f"{r['SN_prov']:.3f}"],
    })
    st.dataframe(df, use_container_width=True, hide_index=True,
                  column_config={
                      'ความหนา (cm)': st.column_config.NumberColumn(format="%.1f cm"),
                      'ความหนา (mm)': st.column_config.NumberColumn(format="%.0f mm"),
                  })

    st.markdown("<br>", unsafe_allow_html=True)
    _,mid,_ = st.columns([1,1.2,1])
    with mid:
        try:
            pdf = make_pdf_flexible(r)
            fname = f"Flexible_AASHTO1993_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"
            st.download_button("📄  Download รายงาน PDF (Flexible)", pdf, fname,
                                "application/pdf", use_container_width=True)
        except Exception as e:
            st.error(f"PDF error: {e}")


# ══════════════════════════════════════════════════════════════
if __name__ == "__main__":
    main()
