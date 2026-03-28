import matplotlib
matplotlib.use("Agg")  # สำคัญมาก
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

# =============================
# FLOWCHART
# =============================
def draw_flowchart():
    fig, ax = plt.subplots(figsize=(6, 10))

    steps = [
        "Start",
        "Input Data\n(W18, R, Ec, Sc, k)",
        "Calculate ZR",
        "Compute ΔPSI",
        "Unit Conversion",
        "Assume D",
        "Calculate log(W18)",
        "Check Target",
        "Adjust D",
        "Final D",
        "Design Layers",
        "Dowel & Tie Bar",
        "End"
    ]

    y = 0
    for step in steps:
        rect = FancyBboxPatch((0.2, y), 0.6, 0.6,
                              boxstyle="round",
                              edgecolor="black")
        ax.add_patch(rect)

        ax.text(0.5, y + 0.3, step,
                ha='center', va='center', fontsize=9)

        y += 1

    ax.set_xlim(0, 1)
    ax.set_ylim(0, y)
    ax.axis('off')

    plt.savefig("flowchart.png", dpi=150, bbox_inches="tight")
    plt.close()

# =============================
# SIMPLE TABLE DRAW (NO PANDAS)
# =============================
def draw_table():

    fig, ax = plt.subplots(figsize=(8, 3))
    ax.axis('off')

    data = [
        ["Parameter", "Value", "Unit"],
        ["W18", "15", "Million ESAL"],
        ["R", "90", "%"],
        ["Ec", "27600", "MPa"],
        ["Sc", "4.8", "MPa"],
        ["k", "54", "MN/m³"]
    ]

    table = ax.table(cellText=data, loc='center')
    table.scale(1, 1.5)

    plt.savefig("input_table.png", bbox_inches='tight')
    plt.close()

# =============================
# STEP TABLE
# =============================
def draw_step_table():

    fig, ax = plt.subplots(figsize=(8, 3))
    ax.axis('off')

    data = [
        ["Step", "Result"],
        ["ΔPSI", "2.0"],
        ["W18 total", "15,000,000"],
        ["log10(W18)", "7.176"],
        ["Iteration", "D ≈ 248 mm"]
    ]

    table = ax.table(cellText=data, loc='center')
    table.scale(1, 1.5)

    plt.savefig("step_table.png", bbox_inches='tight')
    plt.close()

# =============================
# RUN
# =============================
if __name__ == "__main__":
    draw_flowchart()
    draw_table()
    draw_step_table()

    print("✅ สร้างไฟล์เรียบร้อย:")
    print("flowchart.png")
    print("input_table.png")
    print("step_table.png")
