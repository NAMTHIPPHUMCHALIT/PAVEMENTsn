import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
import pandas as pd

# =============================
# FLOWCHART DRAWING
# =============================
def draw_flowchart():
    fig, ax = plt.subplots(figsize=(8, 10))

    steps = [
        "Start",
        "Input Data\n(W18, R, Ec, Sc, k)",
        "Calculate ZR",
        "Compute ΔPSI",
        "Unit Conversion",
        "Assume D",
        "Calculate log(W18)",
        "Check Target",
        "Adjust D (Iteration)",
        "Final D",
        "Design Base/Subbase",
        "Design Dowel & Tie Bar",
        "End"
    ]

    y = 0
    for step in steps:
        box = FancyBboxPatch((0.2, y), 0.6, 0.6,
                             boxstyle="round,pad=0.02",
                             edgecolor="black")
        ax.add_patch(box)

        ax.text(0.5, y + 0.3, step,
                ha='center', va='center', fontsize=9)

        y += 1

    ax.set_xlim(0, 1)
    ax.set_ylim(0, y)
    ax.axis('off')

    plt.savefig("flowchart.png", dpi=150, bbox_inches="tight")
    plt.close()

# =============================
# STEP CALCULATION TABLE
# =============================
def create_step_table():

    data_input = {
        "Parameter": ["W18", "R", "Ec", "Sc", "k"],
        "Value": [15, 90, 27600, 4.8, 54],
        "Unit": ["Million ESAL", "%", "MPa", "MPa", "MN/m³"]
    }

    df_input = pd.DataFrame(data_input)

    data_step = {
        "Step": [
            "ΔPSI = p0 - pt",
            "W18 total",
            "log10(W18)",
            "Unit Conversion",
            "Iteration for D"
        ],
        "Result": [
            "2.0",
            "15,000,000",
            "7.176",
            "Converted to psi & pci",
            "D ≈ 248 mm"
        ]
    }

    df_step = pd.DataFrame(data_step)

    return df_input, df_step

# =============================
# EXPORT TABLE AS IMAGE
# =============================
def save_table_as_image(df, filename):
    fig, ax = plt.subplots(figsize=(8, 2))
    ax.axis('off')

    table = ax.table(
        cellText=df.values,
        colLabels=df.columns,
        loc='center'
    )

    table.auto_set_font_size(False)
    table.set_fontsize(9)
    table.scale(1, 1.5)

    plt.savefig(filename, bbox_inches='tight')
    plt.close()

# =============================
# RUN
# =============================
if __name__ == "__main__":

    # 1. Flowchart
    draw_flowchart()

    # 2. Tables
    df_input, df_step = create_step_table()

    print("\n=== INPUT TABLE ===")
    print(df_input)

    print("\n=== STEP TABLE ===")
    print(df_step)

    # 3. Save as images
    save_table_as_image(df_input, "input_table.png")
    save_table_as_image(df_step, "step_table.png")

    print("\n✅ Generated:")
    print("- flowchart.png")
    print("- input_table.png")
    print("- step_table.png")
