"""
Generate draft framework diagrams (Fig 1-3) for KDS-EL paper.
These are schematic drafts — user should refine in draw.io / PowerPoint.
"""
import os
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

BASE    = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(BASE, "figures_new")
os.makedirs(OUT_DIR, exist_ok=True)

mpl.rcParams.update({
    "font.family":"DejaVu Serif","font.size":9,
    "axes.titlesize":10,"axes.labelsize":9,
    "figure.dpi":300,"savefig.dpi":300,
    "savefig.bbox":"tight","savefig.pad_inches":0.05,
})

CLR = {
    "init":"#e3f2fd","pso":"#bbdefb","drs":"#c8e6c9","ker":"#fff9c4",
    "eval":"#f3e5f5","best":"#ffcdd2","out":"#e8f5e9",
    "arrow":"#37474f","text":"#212121","title":"#b71c1c",
}

def draw_box(ax, xy, w, h, text, color, fontsize=8, bold=False, alpha=0.85):
    box = FancyBboxPatch(xy, w, h, boxstyle="round,pad=0.15",
                         facecolor=color, edgecolor="#546e7a",
                         linewidth=0.8, alpha=alpha, zorder=2)
    ax.add_patch(box)
    fw = "bold" if bold else "normal"
    ax.text(xy[0]+w/2, xy[1]+h/2, text, ha="center", va="center",
            fontsize=fontsize, fontweight=fw, color=CLR["text"], zorder=3)

def draw_arrow(ax, start, end, color=None):
    color = color or CLR["arrow"]
    ax.annotate("", xy=end, xytext=start,
                arrowprops=dict(arrowstyle="->", color=color,
                                lw=1.2, connectionstyle="arc3,rad=0"))

def draw_arrow_curved(ax, start, end, rad=0.2, color=None):
    color = color or CLR["arrow"]
    ax.annotate("", xy=end, xytext=start,
                arrowprops=dict(arrowstyle="->", color=color,
                                lw=1.0, connectionstyle=f"arc3,rad={rad}"))


# ══════════════════════════════════════════════════════════════════════
# Fig 1: KDS-EL Overall Framework
# ══════════════════════════════════════════════════════════════════════
print("Fig 1: KDS-EL framework...")

fig, ax = plt.subplots(figsize=(7.16, 4.0))
ax.set_xlim(0, 10); ax.set_ylim(0, 6)
ax.axis("off")
ax.set_title("KDS-EL: Knowledge-guided Dual-Space Evolutionary Learning Framework",
             fontsize=10, fontweight="bold", color=CLR["title"], pad=8)

# Input
draw_box(ax, (0.2, 2.5), 1.4, 1.0, "Input\nDataset\n$(\\mathbf{F}, \\mathbf{y})$",
         CLR["init"], fontsize=8)

# Init
draw_box(ax, (2.0, 2.5), 1.4, 1.0, "Initialize\nPopulation\n$\\mathbf{X}, \\mathbf{V}, \\mathbf{w}$",
         CLR["init"], fontsize=7.5)

# Main loop box
loop_box = FancyBboxPatch((3.6, 0.3), 5.8, 5.2, boxstyle="round,pad=0.2",
                           facecolor="#fafafa", edgecolor="#b71c1c",
                           linewidth=1.5, linestyle="--", alpha=0.4, zorder=1)
ax.add_patch(loop_box)
ax.text(6.5, 5.2, "Main Loop  ($t = 1 \\to T$)", ha="center", va="center",
        fontsize=9, fontweight="bold", color="#b71c1c", zorder=3)

# Sub1 PSO
draw_box(ax, (3.9, 3.8), 2.3, 1.0,
         "Subpopulation 1\nPSO Exploration\n(Eq. 2)", CLR["pso"], fontsize=7.5)

# Sub2 Weight
draw_box(ax, (3.9, 2.4), 2.3, 1.0,
         "Subpopulation 2\nWeight-guided\nSampling", CLR["pso"], fontsize=7.5)

# Fitness eval
draw_box(ax, (3.9, 1.0), 2.3, 0.8, "Fitness Evaluation\n(Eq. 1)",
         CLR["eval"], fontsize=7.5)

# DRS
draw_box(ax, (6.6, 3.8), 2.5, 1.0,
         "DRS\nDiversity-regulated\nSelection", CLR["drs"], fontsize=8, bold=True)

# KER
draw_box(ax, (6.6, 2.4), 2.5, 1.0,
         "KER\nKnowledge-guided\nElite Refinement", CLR["ker"], fontsize=8, bold=True)

# Gbest
draw_box(ax, (6.6, 1.0), 2.5, 0.8, "Update $G_{\\mathrm{best}}$",
         CLR["best"], fontsize=8)

# Output
draw_box(ax, (6.6, -0.3), 2.5, 0.8, "Output: $\\mathbf{s}^*$",
         CLR["out"], fontsize=8, bold=True)

# Arrows
draw_arrow(ax, (1.6, 3.0), (2.0, 3.0))
draw_arrow(ax, (3.4, 3.0), (3.9, 3.3))  # init -> sub1
draw_arrow(ax, (3.4, 3.0), (3.9, 2.9))  # init -> sub2
draw_arrow(ax, (5.05, 3.8), (5.05, 3.2))  # sub1 -> eval
draw_arrow(ax, (5.05, 2.4), (5.05, 1.8))  # sub2 -> eval
draw_arrow(ax, (6.2, 3.3), (6.6, 3.3))   # sub1 -> DRS (via eval)
draw_arrow(ax, (6.2, 2.9), (6.6, 2.9))   # sub2 -> KER
draw_arrow(ax, (6.2, 1.4), (6.6, 1.4))   # eval -> Gbest
draw_arrow(ax, (7.85, 3.8), (7.85, 3.4))  # DRS -> KER
draw_arrow(ax, (7.85, 1.0), (7.85, 0.5))  # Gbest -> Output

# Synergy arrow
draw_arrow_curved(ax, (9.1, 3.3), (9.1, 2.9), rad=-0.5, color="#b71c1c")
ax.text(9.35, 3.1, "Synergy", fontsize=7, color="#b71c1c",
        fontstyle="italic", ha="left", va="center")

# Loop back arrow
draw_arrow_curved(ax, (7.85, 3.8), (5.05, 4.8), rad=-0.3, color="#b71c1c")
ax.text(6.5, 4.9, "Iterate", fontsize=7, color="#b71c1c",
        fontstyle="italic", ha="center", va="center")

# Legend for spaces
ax.text(0.5, 0.8, "Structural Space:", fontsize=7, fontweight="bold",
        color=CLR["drs"], va="center")
ax.add_patch(FancyBboxPatch((0.5, 0.4), 0.4, 0.3, boxstyle="round,pad=0.05",
             facecolor=CLR["drs"], edgecolor="none", alpha=0.8))
ax.text(1.0, 0.55, "DRS (Pareto selection)", fontsize=6.5, va="center")

ax.text(0.5, -0.0, "Fitness Space:", fontsize=7, fontweight="bold",
        color=CLR["ker"], va="center")
ax.add_patch(FancyBboxPatch((0.5, -0.4), 0.4, 0.3, boxstyle="round,pad=0.05",
             facecolor=CLR["ker"], edgecolor="none", alpha=0.8))
ax.text(1.0, -0.25, "KER (elite refinement)", fontsize=6.5, va="center")

fig.tight_layout()
for ext in (".pdf", ".png"):
    fig.savefig(os.path.join(OUT_DIR, f"fig1_framework{ext}"))
plt.close(fig)
print("  saved: fig1_framework")


# ══════════════════════════════════════════════════════════════════════
# Fig 2: DRS Mechanism
# ══════════════════════════════════════════════════════════════════════
print("Fig 2: DRS mechanism...")

fig, axes = plt.subplots(1, 2, figsize=(7.16, 3.2))

# Left: Pareto front illustration
ax = axes[0]
ax.set_xlim(0, 1); ax.set_ylim(0, 1)
ax.set_xlabel("Fitness (minimise)", fontsize=8)
ax.set_ylabel("NHD (maximise)", fontsize=8)
ax.set_title("(a) Bi-objective Pareto Selection", fontsize=8.5, pad=4)

# Simulated points
np.random.seed(42)
n_pts = 20
fit_vals = np.random.beta(2, 5, n_pts)
nhd_vals = np.random.beta(3, 2, n_pts)

# Pareto front (approximate)
front_mask = np.zeros(n_pts, dtype=bool)
for i in range(n_pts):
    dominated = False
    for j in range(n_pts):
        if i != j and fit_vals[j] <= fit_vals[i] and nhd_vals[j] >= nhd_vals[i]:
            if fit_vals[j] < fit_vals[i] or nhd_vals[j] > nhd_vals[i]:
                dominated = True
                break
    if not dominated:
        front_mask[i] = True

# Non-front
ax.scatter(fit_vals[~front_mask], nhd_vals[~front_mask],
           c="#9e9e9e", s=30, alpha=0.5, edgecolors="white", linewidths=0.5,
           zorder=2, label="Dominated")
# Front
ax.scatter(fit_vals[front_mask], nhd_vals[front_mask],
           c="#b71c1c", s=50, alpha=0.9, edgecolors="#7f0000", linewidths=1.0,
           marker="D", zorder=3, label="Pareto front $\\mathcal{F}_1$")

# Draw front line
front_fit = fit_vals[front_mask]
front_nhd = nhd_vals[front_mask]
order = np.argsort(front_fit)
ax.plot(front_fit[order], front_nhd[order], "--", color="#b71c1c",
        lw=1.0, alpha=0.6, zorder=1)

ax.legend(fontsize=7, loc="upper right", frameon=True)
ax.grid(linestyle="--", alpha=0.3)

# Right: Adaptive schedule
ax = axes[1]
ax.set_xlim(0, 100); ax.set_ylim(0, 1.05)
ax.set_xlabel("Iteration $t$", fontsize=8)
ax.set_ylabel("Weight", fontsize=8)
ax.set_title("(b) Adaptive Schedule $\\alpha_{\\mathrm{cd}}(t)$", fontsize=8.5, pad=4)

t = np.linspace(0, 100, 200)
alpha_cd = (t / 100) ** 2
ax.plot(t, alpha_cd, color="#b71c1c", lw=2, label="$\\alpha_{\\mathrm{cd}} = (t/T)^2$")
ax.plot(t, 1 - alpha_cd, color="#2e7d32", lw=2, ls="--",
        label="$1 - \\alpha_{\\mathrm{cd}}$")

# Annotations
ax.annotate("Early: diversity\npriority", xy=(15, (15/100)**2),
            xytext=(25, 0.75), fontsize=7, color="#2e7d32",
            arrowprops=dict(arrowstyle="->", color="#2e7d32", lw=0.8))
ax.annotate("Late: fitness\npriority", xy=(85, (85/100)**2),
            xytext=(60, 0.25), fontsize=7, color="#b71c1c",
            arrowprops=dict(arrowstyle="->", color="#b71c1c", lw=0.8))

ax.fill_between(t, 0, alpha_cd, alpha=0.08, color="#b71c1c")
ax.fill_between(t, alpha_cd, 1, alpha=0.08, color="#2e7d32")
ax.legend(fontsize=7, loc="center", frameon=True)
ax.grid(linestyle="--", alpha=0.3)

fig.tight_layout(w_pad=3)
for ext in (".pdf", ".png"):
    fig.savefig(os.path.join(OUT_DIR, f"fig2_drs_mechanism{ext}"))
plt.close(fig)
print("  saved: fig2_drs_mechanism")


# ══════════════════════════════════════════════════════════════════════
# Fig 3: KER Mechanism
# ══════════════════════════════════════════════════════════════════════
print("Fig 3: KER mechanism...")

fig, axes = plt.subplots(1, 2, figsize=(7.16, 3.2))

# Left: Weight update flowchart
ax = axes[0]
ax.set_xlim(0, 6); ax.set_ylim(0, 6)
ax.axis("off")
ax.set_title("(a) Improvement-Feedback Weight Update", fontsize=8.5, pad=4)

boxes = [
    ((1.5, 4.8), 3.0, 0.7, "New solution $\\mathbf{x}_i^{(t)}$", CLR["eval"]),
    ((1.5, 3.7), 3.0, 0.7, "$\\Delta = f(P_{\\mathrm{best}}) - f(\\mathbf{x}_i)$", CLR["ker"]),
    ((0.3, 2.4), 2.3, 0.7, "Feature added\n(0$\\to$1): $w_j += \\Delta$", CLR["drs"]),
    ((3.4, 2.4), 2.3, 0.7, "Feature removed\n(1$\\to$0): $w_j -= \\Delta$", CLR["best"]),
    ((1.5, 1.1), 3.0, 0.7, "Update $P_{\\mathrm{best}}$", CLR["pso"]),
]
for xy, w, h, txt, clr in boxes:
    draw_box(ax, xy, w, h, txt, clr, fontsize=7.5)

# Decision diamond
diamond = plt.Polygon([(3, 3.5), (3.7, 3.15), (3, 2.8), (2.3, 3.15)],
                       facecolor="#fff3e0", edgecolor="#e65100",
                       linewidth=1.0, zorder=2)
ax.add_patch(diamond)
ax.text(3, 3.15, "$\\Delta>0$?", ha="center", va="center",
        fontsize=7, fontweight="bold", zorder=3)

draw_arrow(ax, (3, 4.8), (3, 4.4))
draw_arrow(ax, (3, 3.7), (3, 3.5))
draw_arrow(ax, (2.3, 3.15), (1.45, 3.1))  # Yes -> left
draw_arrow(ax, (3.7, 3.15), (4.55, 3.1))  # Yes -> right
draw_arrow(ax, (1.45, 2.4), (3, 1.8))     # left -> update
draw_arrow(ax, (4.55, 2.4), (3, 1.8))     # right -> update

ax.text(1.8, 3.4, "Yes", fontsize=6.5, color="#2e7d32", fontweight="bold")
ax.text(3.9, 3.4, "Yes", fontsize=6.5, color="#b71c1c", fontweight="bold")

# Right: Elite perturbation
ax = axes[1]
ax.set_xlim(0, 6); ax.set_ylim(0, 6)
ax.axis("off")
ax.set_title("(b) Elite Perturbation with Ergodicity", fontsize=8.5, pad=4)

# Binary vector visualization
np.random.seed(7)
bits_orig = np.array([1,0,1,1,0,0,1,0,1,0,0,1,1,0,1])
bits_mut  = bits_orig.copy()
flip_idx  = [1, 4, 7, 12]
bits_mut[flip_idx] = 1 - bits_mut[flip_idx]
bits_w    = np.random.rand(15) * 0.8

y_base = 3.8
cell_w = 0.33
for i in range(15):
    x = 0.5 + i * cell_w
    # Original
    clr = "#2e7d32" if bits_orig[i] else "#e0e0e0"
    ax.add_patch(plt.Rectangle((x, y_base), cell_w-0.02, 0.35,
                                facecolor=clr, edgecolor="white", lw=0.5))
    # Mutant
    clr2 = "#b71c1c" if bits_mut[i] != bits_orig[i] else ("#2e7d32" if bits_mut[i] else "#e0e0e0")
    ax.add_patch(plt.Rectangle((x, y_base-0.5), cell_w-0.02, 0.35,
                                facecolor=clr2, edgecolor="white", lw=0.5))
    if bits_mut[i] != bits_orig[i]:
        ax.annotate("", xy=(x+cell_w/2, y_base-0.12), xytext=(x+cell_w/2, y_base+0.02),
                    arrowprops=dict(arrowstyle="->", color="#b71c1c", lw=1.2))

ax.text(0.3, y_base+0.17, "Elite:", fontsize=7.5, fontweight="bold", va="center")
ax.text(0.3, y_base-0.33, "Mutant:", fontsize=7.5, fontweight="bold", va="center",
        color="#b71c1c")

# Weight bar chart below
y_w = 2.2
for i in range(15):
    x = 0.5 + i * cell_w
    h = bits_w[i] * 1.2
    clr = "#b71c1c" if bits_w[i] > 0.5 else "#9e9e9e"
    ax.bar(x + cell_w/2, h, width=cell_w-0.04, bottom=y_w,
           color=clr, alpha=0.7, edgecolor="white", lw=0.3)
ax.text(0.3, y_w+0.6, "$|w_j|$", fontsize=7.5, fontweight="bold", va="center")
ax.set_xlim(0, 6)

# Probability annotation
ax.text(3, 1.5, "$p_j^{\\mathrm{flip}} \\propto |w_j|$",
        ha="center", fontsize=9, fontweight="bold", color="#b71c1c")
ax.text(3, 0.9, "With $p_r = 0.10$: random flip (ergodicity)",
        ha="center", fontsize=7.5, color="#546e7a", fontstyle="italic")

# Legend
ax.add_patch(plt.Rectangle((0.5, 0.1), 0.3, 0.25,
             facecolor="#2e7d32", edgecolor="none", alpha=0.8))
ax.text(0.9, 0.22, "= 1 (selected)", fontsize=6.5, va="center")
ax.add_patch(plt.Rectangle((2.5, 0.1), 0.3, 0.25,
             facecolor="#e0e0e0", edgecolor="none", alpha=0.8))
ax.text(2.9, 0.22, "= 0 (not selected)", fontsize=6.5, va="center")
ax.add_patch(plt.Rectangle((4.5, 0.1), 0.3, 0.25,
             facecolor="#b71c1c", edgecolor="none", alpha=0.8))
ax.text(4.9, 0.22, "= flipped", fontsize=6.5, va="center")

fig.tight_layout(w_pad=3)
for ext in (".pdf", ".png"):
    fig.savefig(os.path.join(OUT_DIR, f"fig3_ker_mechanism{ext}"))
plt.close(fig)
print("  saved: fig3_ker_mechanism")

print("\nAll framework figures done.")
