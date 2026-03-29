"""
AASHTO 1993 Rigid Pavement (Concrete) Design Tool
ออกแบบโครงสร้างผิวทางคอนกรีต ตามมาตรฐาน AASHTO 1993
"""

import Streamlit as tk
from Streamlit import ttk, messagebox, filedialog
import math
import os
import sys
from datetime import datetime

# ─────────────────────────────────────────────
# AASHTO 1993 RIGID PAVEMENT DESIGN ENGINE
# ─────────────────────────────────────────────

def calc_esal(aadt, truck_pct, growth_rate, design_life, ldf=0.5, tff=1.0):
    """คำนวณ ESAL (Equivalent Single Axle Load)"""
    aadt_trucks = aadt * (truck_pct / 100)
    # Growth factor (geometric series)
    if growth_rate == 0:
        gf = design_life
    else:
        r = growth_rate / 100
        gf = ((1 + r)**design_life - 1) / r
    daily_esal = aadt_trucks * tff * ldf
    total_esal = daily_esal * 365 * gf
    return total_esal, gf

def aashto93_rigid(W18, ZR, S0, delta_PSI, Pt, E_c, Sc, Cd, J, k):
    """
    AASHTO 1993 Rigid Pavement Design Equation (iterative solve for D)
    
    log10(W18) = ZR*S0 + 7.35*log10(D+1) - 0.06
                + log10(delta_PSI/(4.5-1.5)) / (1 + 1.624e7/(D+1)^8.46)
                + (4.22 - 0.32*Pt)*log10(Sc*Cd*(D^0.75 - 1.132) /
                  (215.63*J*(D^0.75 - (18.42/(E_c/k)^0.25))))

    Solve for D (slab thickness in inches) by bisection
    """
    target = math.log10(max(W18, 1))

    def f(D):
        if D <= 0:
            return -999
        try:
            term1 = ZR * S0
            term2 = 7.35 * math.log10(D + 1) - 0.06
            term3_num = math.log10(delta_PSI / (4.5 - 1.5))
            term3_den = 1 + (1.624e7 / (D + 1)**8.46)
            term3 = term3_num / term3_den

            Ec_k_ratio = E_c / k
            inner = D**0.75 - (18.42 / (Ec_k_ratio**0.25))
            if inner <= 0:
                return -999
            numer = Sc * Cd * (D**0.75 - 1.132)
            denom = 215.63 * J * inner
            if denom <= 0:
                return -999
            term4 = (4.22 - 0.32 * Pt) * math.log10(numer / denom)

            return term1 + term2 + term3 + term4
        except:
            return -999

    # Bisection: find D such that f(D) = target
    lo, hi = 2.0, 24.0
    for _ in range(100):
        mid = (lo + hi) / 2
        val = f(mid)
        if val < target:
            lo = mid
        else:
            hi = mid
        if hi - lo < 0.001:
            break
    D_inch = (lo + hi) / 2
    D_mm = D_inch * 25.4
    return D_inch, D_mm

def get_subbase_thickness(k_subgrade, D_slab_mm):
    """กำหนดความหนา Subbase ตามค่า k และความหนาแผ่นคอนกรีต"""
    # AASHTO guideline: subbase ขั้นต่ำ 100mm, เพิ่มตาม k ต่ำ
    if k_subgrade < 27:       # Soft (MPa/m)
        base = 300
    elif k_subgrade < 55:     # Medium
        base = 200
    elif k_subgrade < 110:    # Good
        base = 150
    else:                      # Excellent
        base = 100
    # เพิ่มเล็กน้อยถ้าแผ่นหนา
    extra = max(0, (D_slab_mm - 200) * 0.1)
    return round(base + extra)

def get_subgrade_prep(k_subgrade):
    """ความหนาชั้น Subgrade Preparation"""
    if k_subgrade < 27:
        return 300
    elif k_subgrade < 55:
        return 200
    else:
        return 150

def design_pavement(params):
    """รันการออกแบบทั้งหมด คืนค่า dict ผลลัพธ์"""
    # Unpack
    aadt       = params['aadt']
    truck_pct  = params['truck_pct']
    growth     = params['growth_rate']
    life       = params['design_life']
    R          = params['reliability']      # %
    S0         = params['S0']
    pi         = params['pi']               # Initial PSI
    pt         = params['pt']               # Terminal PSI
    Ec         = params['Ec']               # MPa → psi
    Sc         = params['Sc']               # MR of concrete (psi)
    Cd         = params['Cd']
    J          = params['J']
    k_MPa      = params['k']               # MPa/m (modulus of subgrade reaction)
    ldf        = params['ldf']
    tff        = params['tff']

    # Convert units
    Ec_psi  = Ec * 145.038   # MPa → psi
    Sc_psi  = Sc * 145.038
    k_pci   = k_MPa / 0.2714  # MPa/m → pci (lb/in³)

    # ZR from reliability
    zr_table = {50: 0.000, 60: -0.253, 70: -0.524, 75: -0.674,
                80: -0.841, 85: -1.037, 90: -1.282, 91: -1.340,
                92: -1.405, 93: -1.476, 94: -1.555, 95: -1.645,
                96: -1.751, 97: -1.881, 98: -2.054, 99: -2.327, 99.9: -3.090}
    # Find nearest
    ZR = min(zr_table.items(), key=lambda x: abs(x[0] - R))[1]

    delta_PSI = pi - pt

    # ESAL
    W18, gf = calc_esal(aadt, truck_pct, growth, life, ldf, tff)

    # Solve slab thickness
    D_in, D_mm = aashto93_rigid(W18, ZR, S0, delta_PSI, pt, Ec_psi, Sc_psi, Cd, J, k_pci)

    # Round up to nearest 25mm
    D_design_mm = math.ceil(D_mm / 25) * 25
    D_design_in = D_design_mm / 25.4

    # Sub-layers
    subbase_mm = get_subbase_thickness(k_MPa, D_design_mm)
    subgrade_mm = get_subgrade_prep(k_MPa)

    # Total
    total_mm = D_design_mm + subbase_mm + subgrade_mm

    return {
        'W18': W18,
        'ZR': ZR,
        'delta_PSI': delta_PSI,
        'growth_factor': gf,
        'D_calc_mm': D_mm,
        'D_design_mm': D_design_mm,
        'D_design_in': D_design_in,
        'subbase_mm': subbase_mm,
        'subgrade_mm': subgrade_mm,
        'total_mm': total_mm,
        'k_pci': k_pci,
        'Ec_psi': Ec_psi,
        'Sc_psi': Sc_psi,
        'params': params,
    }


# ─────────────────────────────────────────────
# PDF REPORT GENERATOR
# ─────────────────────────────────────────────

def generate_pdf(result, filepath):
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.lib.units import mm, cm
    from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer,
                                     Table, TableStyle, HRFlowable)
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
    from reportlab.pdfgen import canvas as rl_canvas

    p = result['params']

    # Colors
    PRIMARY   = colors.HexColor('#1a365d')
    ACCENT    = colors.HexColor('#2b6cb0')
    LIGHT     = colors.HexColor('#ebf8ff')
    CONCRETE  = colors.HexColor('#e2e8f0')
    SUBBASE   = colors.HexColor('#fef3c7')
    SUBGRADE  = colors.HexColor('#d1fae5')
    GRAY      = colors.HexColor('#718096')

    doc = SimpleDocTemplate(filepath, pagesize=A4,
                            rightMargin=20*mm, leftMargin=20*mm,
                            topMargin=20*mm, bottomMargin=20*mm)
    story = []
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle('Title', fontSize=16, fontName='Helvetica-Bold',
                                  textColor=PRIMARY, alignment=TA_CENTER, spaceAfter=4)
    sub_style   = ParagraphStyle('Sub', fontSize=10, fontName='Helvetica',
                                  textColor=GRAY, alignment=TA_CENTER, spaceAfter=12)
    head_style  = ParagraphStyle('Head', fontSize=12, fontName='Helvetica-Bold',
                                  textColor=PRIMARY, spaceBefore=12, spaceAfter=6)
    normal      = ParagraphStyle('Norm', fontSize=9, fontName='Helvetica',
                                  textColor=colors.black, spaceAfter=2)
    bold_norm   = ParagraphStyle('BNorm', fontSize=9, fontName='Helvetica-Bold',
                                  textColor=colors.black)

    # ── Header ──
    story.append(Paragraph("รายงานการออกแบบโครงสร้างผิวทางคอนกรีต", title_style))
    story.append(Paragraph("Rigid Pavement Design Report  |  AASHTO 1993", sub_style))
    story.append(Paragraph(f"วันที่ออกแบบ: {datetime.now().strftime('%d/%m/%Y %H:%M')}", sub_style))
    story.append(HRFlowable(width="100%", thickness=2, color=PRIMARY, spaceAfter=12))

    # ── Input Parameters ──
    story.append(Paragraph("1. ข้อมูลนำเข้า (Input Parameters)", head_style))
    inp_data = [
        ['พารามิเตอร์', 'ค่าที่ใช้', 'หน่วย'],
        ['AADT (ปริมาณจราจรเฉลี่ยต่อวัน)', f"{p['aadt']:,.0f}", 'คัน/วัน'],
        ['สัดส่วนรถบรรทุก', f"{p['truck_pct']:.1f}", '%'],
        ['อัตราการเติบโตของจราจร', f"{p['growth_rate']:.1f}", '%/ปี'],
        ['อายุออกแบบ', f"{p['design_life']:.0f}", 'ปี'],
        ['ความน่าเชื่อถือ (R)', f"{p['reliability']:.0f}", '%'],
        ['ค่าเบี่ยงเบน ZR', f"{result['ZR']:.3f}", '-'],
        ['Overall Standard Deviation (S0)', f"{p['S0']:.2f}", '-'],
        ['Initial PSI (pi)', f"{p['pi']:.1f}", '-'],
        ['Terminal PSI (pt)', f"{p['pt']:.1f}", '-'],
        ['ΔPsi', f"{result['delta_PSI']:.1f}", '-'],
        ['Modulus of Elasticity of Concrete (Ec)', f"{p['Ec']:,.0f}", 'MPa'],
        ['Modulus of Rupture (Sc)', f"{p['Sc']:.1f}", 'MPa'],
        ['Drainage Coefficient (Cd)', f"{p['Cd']:.2f}", '-'],
        ['Load Transfer Coefficient (J)', f"{p['J']:.1f}", '-'],
        ['Modulus of Subgrade Reaction (k)', f"{p['k']:.0f}", 'MPa/m'],
        ['Lane Distribution Factor', f"{p['ldf']:.2f}", '-'],
        ['Truck Factor (TFF)', f"{p['tff']:.2f}", '-'],
    ]
    col_w = [85*mm, 40*mm, 30*mm]
    t = Table(inp_data, colWidths=col_w)
    t.setStyle(TableStyle([
        ('BACKGROUND',   (0,0), (-1,0), PRIMARY),
        ('TEXTCOLOR',    (0,0), (-1,0), colors.white),
        ('FONTNAME',     (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE',     (0,0), (-1,-1), 9),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, LIGHT]),
        ('GRID',         (0,0), (-1,-1), 0.5, colors.lightgrey),
        ('ALIGN',        (1,0), (-1,-1), 'CENTER'),
        ('VALIGN',       (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING',   (0,0), (-1,-1), 4),
        ('BOTTOMPADDING',(0,0), (-1,-1), 4),
    ]))
    story.append(t)

    # ── Calculation Results ──
    story.append(Paragraph("2. ผลการคำนวณ (Design Results)", head_style))
    calc_data = [
        ['รายการ', 'ผลการคำนวณ', 'หน่วย'],
        ['Growth Factor (GF)', f"{result['growth_factor']:.3f}", '-'],
        ['18-kip ESAL สะสมตลอดอายุออกแบบ', f"{result['W18']:,.0f}", 'ESAL'],
        ['k (แปลง)', f"{result['k_pci']:.1f}", 'pci'],
        ['Ec (แปลง)', f"{result['Ec_psi']:,.0f}", 'psi'],
        ['Sc (แปลง)', f"{result['Sc_psi']:.1f}", 'psi'],
        ['ความหนาคอนกรีตที่คำนวณได้', f"{result['D_calc_mm']:.1f}", 'mm'],
        ['ความหนาคอนกรีตที่ออกแบบ (ปัดขึ้น 25mm)', f"{result['D_design_mm']:.0f}", 'mm'],
    ]
    t2 = Table(calc_data, colWidths=col_w)
    t2.setStyle(TableStyle([
        ('BACKGROUND',   (0,0), (-1,0), ACCENT),
        ('TEXTCOLOR',    (0,0), (-1,0), colors.white),
        ('FONTNAME',     (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE',     (0,0), (-1,-1), 9),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, LIGHT]),
        ('GRID',         (0,0), (-1,-1), 0.5, colors.lightgrey),
        ('ALIGN',        (1,0), (-1,-1), 'CENTER'),
        ('VALIGN',       (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING',   (0,0), (-1,-1), 4),
        ('BOTTOMPADDING',(0,0), (-1,-1), 4),
    ]))
    story.append(t2)

    # ── Layer Summary ──
    story.append(Paragraph("3. สรุปความหนาโครงสร้างทาง (Pavement Layer Summary)", head_style))
    layers = [
        ['ชั้นทาง', 'วัสดุ', 'ความหนา (mm)', 'ความหนา (inch)'],
        ['ชั้นที่ 1 - Concrete Slab', 'Portland Cement Concrete',
         str(result['D_design_mm']), f"{result['D_design_in']:.2f}"],
        ['ชั้นที่ 2 - Subbase', 'Granular Subbase / Lean Concrete',
         str(result['subbase_mm']), f"{result['subbase_mm']/25.4:.2f}"],
        ['ชั้นที่ 3 - Subgrade Prep', 'Compacted Subgrade',
         str(result['subgrade_mm']), f"{result['subgrade_mm']/25.4:.2f}"],
        ['รวมทั้งหมด', '', str(result['total_mm']),
         f"{result['total_mm']/25.4:.2f}"],
    ]
    t3 = Table(layers, colWidths=[55*mm, 55*mm, 30*mm, 30*mm - 5])
    t3.setStyle(TableStyle([
        ('BACKGROUND',   (0,0), (-1,0), PRIMARY),
        ('TEXTCOLOR',    (0,0), (-1,0), colors.white),
        ('FONTNAME',     (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE',     (0,0), (-1,-1), 9),
        ('BACKGROUND',   (0,1), (-1,1), CONCRETE),
        ('BACKGROUND',   (0,2), (-1,2), SUBBASE),
        ('BACKGROUND',   (0,3), (-1,3), SUBGRADE),
        ('BACKGROUND',   (0,4), (-1,4), colors.HexColor('#1a365d')),
        ('TEXTCOLOR',    (0,4), (-1,4), colors.white),
        ('FONTNAME',     (0,4), (-1,4), 'Helvetica-Bold'),
        ('GRID',         (0,0), (-1,-1), 0.5, colors.grey),
        ('ALIGN',        (2,0), (-1,-1), 'CENTER'),
        ('VALIGN',       (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING',   (0,0), (-1,-1), 5),
        ('BOTTOMPADDING',(0,0), (-1,-1), 5),
    ]))
    story.append(t3)

    # ── Section Diagram ──
    story.append(Spacer(1, 8*mm))
    story.append(Paragraph("4. หน้าตัดโครงสร้างผิวทาง (Cross Section)", head_style))

    # Draw cross-section as a table visual
    total = result['total_mm']
    layers_draw = [
        (result['D_design_mm'],  CONCRETE, "Concrete Slab",   f"{result['D_design_mm']} mm"),
        (result['subbase_mm'],   SUBBASE,  "Subbase",          f"{result['subbase_mm']} mm"),
        (result['subgrade_mm'],  SUBGRADE, "Subgrade Prep",    f"{result['subgrade_mm']} mm"),
    ]
    sec_data = []
    for thick, col, name, t_str in layers_draw:
        pct = thick / total
        rows = max(1, round(pct * 8))
        for i in range(rows):
            if i == rows // 2:
                sec_data.append([f"{name}  —  {t_str}"])
            else:
                sec_data.append([""])

    sec_style = []
    row = 0
    for thick, col, name, t_str in layers_draw:
        pct = thick / total
        rows = max(1, round(pct * 8))
        for i in range(rows):
            sec_style.append(('BACKGROUND', (0, row), (0, row), col))
            row += 1

    sec_table = Table(sec_data, colWidths=[155*mm])
    sec_table.setStyle(TableStyle([
        ('FONTNAME',     (0,0), (-1,-1), 'Helvetica'),
        ('FONTSIZE',     (0,0), (-1,-1), 9),
        ('ALIGN',        (0,0), (-1,-1), 'CENTER'),
        ('VALIGN',       (0,0), (-1,-1), 'MIDDLE'),
        ('ROWHEIGHT',    (0,0), (-1,-1), 10),
        ('BOX',          (0,0), (-1,-1), 1, PRIMARY),
        ('INNERGRID',    (0,0), (-1,-1), 0.3, colors.grey),
    ] + sec_style))
    story.append(sec_table)

    # ── Notes ──
    story.append(Spacer(1, 6*mm))
    story.append(HRFlowable(width="100%", thickness=1, color=GRAY, spaceAfter=6))
    story.append(Paragraph("หมายเหตุ / Notes", bold_norm))
    notes = [
        "• การออกแบบใช้สมการ AASHTO 1993 Guide for Design of Pavement Structures",
        "• ความหนาแผ่นคอนกรีตปัดขึ้นทุก 25 mm ตามมาตรฐาน",
        "• ควรตรวจสอบความหนา Subbase ตามมาตรฐานกรมทางหลวงไทย",
        "• ค่า k ที่ใช้คือ Composite k หลังจากวาง Subbase แล้ว",
        "• ESAL คำนวณจากปริมาณจราจร อัตราเติบโต และ Truck Factor",
    ]
    for note in notes:
        story.append(Paragraph(note, normal))

    doc.build(story)


# ─────────────────────────────────────────────
# TKINTER GUI
# ─────────────────────────────────────────────

class PavementApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("AASHTO 1993 — Rigid Pavement Design")
        self.geometry("1100x780")
        self.resizable(True, True)
        self.configure(bg="#0f172a")
        self.result = None

        self._build_style()
        self._build_ui()

    def _build_style(self):
        style = ttk.Style(self)
        style.theme_use('clam')
        style.configure('TNotebook',        background='#0f172a', borderwidth=0)
        style.configure('TNotebook.Tab',    background='#1e293b', foreground='#94a3b8',
                         padding=[14, 6], font=('Consolas', 9, 'bold'))
        style.map('TNotebook.Tab',
                  background=[('selected', '#2563eb')],
                  foreground=[('selected', 'white')])
        style.configure('TFrame',           background='#0f172a')
        style.configure('TLabel',           background='#0f172a', foreground='#e2e8f0',
                         font=('Consolas', 9))
        style.configure('TEntry',           fieldbackground='#1e293b', foreground='#f1f5f9',
                         insertcolor='white', font=('Consolas', 10), borderwidth=1,
                         relief='solid')
        style.configure('TCombobox',        fieldbackground='#1e293b', foreground='#f1f5f9',
                         font=('Consolas', 10))
        style.configure('TLabelframe',      background='#0f172a', foreground='#60a5fa',
                         font=('Consolas', 9, 'bold'), borderwidth=1, relief='solid')
        style.configure('TLabelframe.Label',background='#0f172a', foreground='#60a5fa',
                         font=('Consolas', 9, 'bold'))

    def _lbl_entry(self, parent, row, text, default, unit="", tip=""):
        ttk.Label(parent, text=text).grid(row=row, column=0, sticky='w', pady=3, padx=4)
        var = tk.StringVar(value=str(default))
        e = ttk.Entry(parent, textvariable=var, width=12)
        e.grid(row=row, column=1, padx=8, pady=3)
        if unit:
            ttk.Label(parent, text=unit, foreground='#94a3b8').grid(row=row, column=2, sticky='w')
        if tip:
            ttk.Label(parent, text=f"  ← {tip}", foreground='#475569',
                       font=('Consolas', 8)).grid(row=row, column=3, sticky='w')
        return var

    def _build_ui(self):
        # Top bar
        top = tk.Frame(self, bg='#0f172a', pady=10)
        top.pack(fill='x', padx=20)
        tk.Label(top, text="AASHTO 1993", bg='#0f172a', fg='#2563eb',
                  font=('Consolas', 22, 'bold')).pack(side='left')
        tk.Label(top, text="  RIGID PAVEMENT DESIGN", bg='#0f172a', fg='#94a3b8',
                  font=('Consolas', 13)).pack(side='left')

        # Main frame split
        main = tk.Frame(self, bg='#0f172a')
        main.pack(fill='both', expand=True, padx=16, pady=4)

        # Left: inputs
        left = tk.Frame(main, bg='#0f172a')
        left.pack(side='left', fill='y', padx=(0,10))

        # Right: output
        right = tk.Frame(main, bg='#0f172a')
        right.pack(side='left', fill='both', expand=True)

        # ── INPUT NOTEBOOK ──
        nb = ttk.Notebook(left)
        nb.pack(fill='both', expand=True)

        # Tab 1: Traffic
        t1 = ttk.Frame(nb)
        nb.add(t1, text='🚛  จราจร')
        self.v_aadt      = self._lbl_entry(t1, 0, 'AADT (คัน/วัน)',      5000,   'คัน/วัน')
        self.v_truck_pct = self._lbl_entry(t1, 1, 'สัดส่วนรถบรรทุก',      15,     '%')
        self.v_growth    = self._lbl_entry(t1, 2, 'อัตราเติบโต',           3,      '%/ปี')
        self.v_life      = self._lbl_entry(t1, 3, 'อายุออกแบบ',            20,     'ปี')
        self.v_ldf       = self._lbl_entry(t1, 4, 'Lane Dist. Factor',     0.5,    '',   '0.4–0.9')
        self.v_tff       = self._lbl_entry(t1, 5, 'Truck Factor (TFF)',    1.0,    '',   'ESAL/truck')

        # Tab 2: Reliability
        t2 = ttk.Frame(nb)
        nb.add(t2, text='📊  ความน่าเชื่อถือ')
        r_opts = ['50','60','70','75','80','85','90','91','92','93','94','95','96','97','98','99']
        ttk.Label(t2, text='Reliability (R)').grid(row=0, column=0, sticky='w', pady=3, padx=4)
        self.v_R = tk.StringVar(value='95')
        ttk.Combobox(t2, textvariable=self.v_R, values=r_opts, width=10,
                      state='readonly').grid(row=0, column=1, padx=8, pady=3)
        ttk.Label(t2, text='%', foreground='#94a3b8').grid(row=0, column=2, sticky='w')
        self.v_S0 = self._lbl_entry(t2, 1, 'Std Deviation (S0)', 0.35, '',  '0.30–0.40')
        self.v_pi = self._lbl_entry(t2, 2, 'Initial PSI (pi)',   4.5,  '',  '4.2–4.5')
        self.v_pt = self._lbl_entry(t2, 3, 'Terminal PSI (pt)',  2.5,  '',  '2.0–3.0')

        # Tab 3: Material
        t3 = ttk.Frame(nb)
        nb.add(t3, text='🏗️  วัสดุ')
        self.v_Ec  = self._lbl_entry(t3, 0, "Elastic Modulus (Ec)",    27500, 'MPa', '20000-35000')
        self.v_Sc  = self._lbl_entry(t3, 1, "Modulus of Rupture (Sc)", 4.5,   'MPa', '4.0-5.5')
        self.v_Cd  = self._lbl_entry(t3, 2, "Drainage Coeff (Cd)",     1.0,   '',    '0.7–1.25')
        self.v_J   = self._lbl_entry(t3, 3, "Load Transfer (J)",       3.2,   '',    '2.5–4.4')
        self.v_k   = self._lbl_entry(t3, 4, "Subgrade k",              54,    'MPa/m','27-270')

        # Preset buttons
        tk.Label(t3, text='Preset วัสดุ:', bg='#0f172a', fg='#94a3b8',
                  font=('Consolas', 8)).grid(row=5, column=0, sticky='w', pady=(10,2), padx=4)
        pbf = tk.Frame(t3, bg='#0f172a')
        pbf.grid(row=6, column=0, columnspan=4, sticky='w', padx=4)

        presets = [('ทั่วไป', 27500, 4.5, 1.0, 3.2, 54),
                   ('คุณภาพสูง', 30000, 5.0, 1.1, 2.8, 80),
                   ('ดินอ่อน', 25000, 4.2, 0.9, 3.8, 27)]
        for name, ec, sc, cd, j, k in presets:
            def make_cmd(e=ec, s=sc, c=cd, jj=j, kk=k):
                def cmd():
                    self.v_Ec.set(e); self.v_Sc.set(s)
                    self.v_Cd.set(c); self.v_J.set(jj); self.v_k.set(kk)
                return cmd
            tk.Button(pbf, text=name, command=make_cmd(),
                       bg='#1e3a5f', fg='#93c5fd', font=('Consolas', 8),
                       relief='flat', padx=6, pady=2, cursor='hand2').pack(side='left', padx=3)

        # ── CALCULATE BUTTON ──
        calc_btn = tk.Button(left, text="▶  คำนวณ  /  DESIGN",
                              command=self.run_design,
                              bg='#2563eb', fg='white',
                              font=('Consolas', 11, 'bold'),
                              relief='flat', padx=20, pady=10, cursor='hand2',
                              activebackground='#1d4ed8', activeforeground='white')
        calc_btn.pack(fill='x', pady=(10, 4))

        pdf_btn = tk.Button(left, text="📄  Export PDF",
                             command=self.export_pdf,
                             bg='#166534', fg='#86efac',
                             font=('Consolas', 10, 'bold'),
                             relief='flat', padx=20, pady=8, cursor='hand2',
                             activebackground='#15803d', activeforeground='white')
        pdf_btn.pack(fill='x', pady=2)

        # ── OUTPUT PANEL ──
        out_frame = tk.Frame(right, bg='#0f172a')
        out_frame.pack(fill='both', expand=True)

        tk.Label(out_frame, text="ผลการออกแบบ  /  Design Output",
                  bg='#0f172a', fg='#60a5fa',
                  font=('Consolas', 11, 'bold')).pack(anchor='w', pady=(0,6))

        # Result canvas
        self.canvas = tk.Canvas(out_frame, bg='#0f172a', highlightthickness=0)
        self.canvas.pack(fill='both', expand=True)

        self._draw_placeholder()

    def _draw_placeholder(self):
        self.canvas.delete('all')
        w = self.canvas.winfo_width() or 550
        h = self.canvas.winfo_height() or 600
        self.canvas.create_text(w//2, h//2, text="กรอกข้อมูลแล้วกด\n▶  คำนวณ",
                                  fill='#334155', font=('Consolas', 14), justify='center')

    def _get_params(self):
        return {
            'aadt':        float(self.v_aadt.get()),
            'truck_pct':   float(self.v_truck_pct.get()),
            'growth_rate': float(self.v_growth.get()),
            'design_life': float(self.v_life.get()),
            'reliability': float(self.v_R.get()),
            'S0':          float(self.v_S0.get()),
            'pi':          float(self.v_pi.get()),
            'pt':          float(self.v_pt.get()),
            'Ec':          float(self.v_Ec.get()),
            'Sc':          float(self.v_Sc.get()),
            'Cd':          float(self.v_Cd.get()),
            'J':           float(self.v_J.get()),
            'k':           float(self.v_k.get()),
            'ldf':         float(self.v_ldf.get()),
            'tff':         float(self.v_tff.get()),
        }

    def run_design(self):
        try:
            params = self._get_params()
            self.result = design_pavement(params)
            self._draw_results(self.result)
        except Exception as e:
            messagebox.showerror("Error", f"ตรวจสอบค่าที่กรอก:\n{e}")

    def _draw_results(self, r):
        self.canvas.update_idletasks()
        self.canvas.delete('all')
        W = self.canvas.winfo_width()
        H = self.canvas.winfo_height()
        if W < 100:
            W, H = 550, 600

        pad = 24
        # ── Header ──
        self.canvas.create_text(W//2, pad + 10, text="DESIGN RESULTS",
                                  fill='#60a5fa', font=('Consolas', 13, 'bold'))

        # ── ESAL summary ──
        y = pad + 40
        self.canvas.create_text(pad, y, anchor='w',
            text=f"18-kip ESAL  =  {r['W18']:,.0f}",
            fill='#fbbf24', font=('Consolas', 10, 'bold'))
        y += 20
        self.canvas.create_text(pad, y, anchor='w',
            text=f"ZR = {r['ZR']:.3f}   |   ΔPsi = {r['delta_PSI']:.1f}   |   k = {r['k_pci']:.1f} pci",
            fill='#94a3b8', font=('Consolas', 9))

        y += 30
        # Divider
        self.canvas.create_line(pad, y, W - pad, y, fill='#1e3a5f', width=1)
        y += 16

        self.canvas.create_text(W//2, y, text="หน้าตัดโครงสร้างผิวทาง  (Cross Section)",
                                  fill='#e2e8f0', font=('Consolas', 10, 'bold'))
        y += 24

        # ── Pavement Cross Section Drawing ──
        total_mm = r['total_mm']
        layers = [
            ('Concrete Slab',  r['D_design_mm'],  '#bfdbfe', '#1e40af', '✦'),
            ('Subbase',        r['subbase_mm'],   '#fef3c7', '#92400e', '◆'),
            ('Subgrade Prep',  r['subgrade_mm'],  '#d1fae5', '#065f46', '●'),
        ]
        diagram_h = H - y - 130
        diagram_w = W - pad * 2 - 120
        x0 = pad + 110

        # Road surface
        self.canvas.create_rectangle(x0, y, x0 + diagram_w, y + 6,
                                       fill='#475569', outline='', tags='section')
        self.canvas.create_text(pad + 50, y + 3, text="ผิวจราจร", fill='#94a3b8',
                                  font=('Consolas', 8), anchor='e')
        y += 6

        for name, thick_mm, fill_color, text_color, sym in layers:
            lh = max(30, int((thick_mm / total_mm) * diagram_h))

            # Layer rect
            self.canvas.create_rectangle(x0, y, x0 + diagram_w, y + lh,
                                           fill=fill_color, outline='#0f172a', width=1)

            # Hatch pattern
            for hx in range(x0 + 10, x0 + diagram_w - 5, 18):
                self.canvas.create_line(hx, y, hx - 8, y + lh,
                                         fill=text_color, width=1, dash=(2,4))

            # Label inside
            mid_y = y + lh // 2
            self.canvas.create_text(x0 + diagram_w // 2, mid_y,
                                      text=f"{sym}  {name}",
                                      fill=text_color, font=('Consolas', 9, 'bold'))

            # Dimension arrow + label on left
            ax = pad + 5
            self.canvas.create_line(ax, y, ax, y + lh, fill='#475569', width=1,
                                     arrow='both', arrowshape=(6, 7, 3))
            t_in = thick_mm / 25.4
            self.canvas.create_text(ax + 4, mid_y, anchor='w',
                text=f"{thick_mm} mm\n({t_in:.1f}\")",
                fill='#e2e8f0', font=('Consolas', 8), justify='center')

            y += lh

        # Subgrade fill
        self.canvas.create_rectangle(x0, y, x0 + diagram_w, y + 20,
                                       fill='#7c3aed', outline='', stipple='gray25')
        self.canvas.create_text(x0 + diagram_w // 2, y + 10,
                                  text="Subgrade  ▼", fill='#c4b5fd',
                                  font=('Consolas', 8))
        y += 22

        # ── Summary Box ──
        y += 14
        box_x = pad
        bw = W - pad * 2
        bh = 70
        self.canvas.create_rectangle(box_x, y, box_x + bw, y + bh,
                                       fill='#0c1a2e', outline='#2563eb', width=2)
        self.canvas.create_text(box_x + 16, y + 12, anchor='w',
            text="► สรุปผลการออกแบบ / Design Summary",
            fill='#60a5fa', font=('Consolas', 9, 'bold'))

        col1 = box_x + 16
        col2 = box_x + bw // 2 + 10
        row1 = y + 28
        row2 = y + 46

        items = [
            (col1, row1, f"Concrete Slab  :  {r['D_design_mm']} mm  ({r['D_design_in']:.2f}\")"),
            (col1, row2, f"Subbase        :  {r['subbase_mm']} mm"),
            (col2, row1, f"Subgrade Prep  :  {r['subgrade_mm']} mm"),
            (col2, row2, f"Total Depth    :  {r['total_mm']} mm"),
        ]
        for cx, cy, txt in items:
            self.canvas.create_text(cx, cy, anchor='w', text=txt,
                                      fill='#e2e8f0', font=('Consolas', 9))

    def export_pdf(self):
        if self.result is None:
            messagebox.showwarning("แจ้งเตือน", "กรุณาคำนวณก่อนส่งออก PDF")
            return
        fp = filedialog.asksaveasfilename(
            defaultextension='.pdf',
            filetypes=[('PDF files', '*.pdf')],
            initialfile='AASHTO1993_PavementDesign.pdf')
        if not fp:
            return
        try:
            generate_pdf(self.result, fp)
            messagebox.showinfo("สำเร็จ", f"บันทึก PDF แล้วที่:\n{fp}")
        except Exception as e:
            messagebox.showerror("Error", f"ไม่สามารถสร้าง PDF:\n{e}")


if __name__ == '__main__':
    app = PavementApp()
    app.mainloop()
