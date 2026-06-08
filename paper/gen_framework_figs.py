"""
Generate publication-quality figures for KDS-EL paper.

Figure 1 : Overall Framework (flowchart, double-column 17.8 cm)
Figure 2 : DRS Mechanism — real Pareto data (double-column 17.8 cm)
Figure 3 : KER Mechanism — real convergence curves (double-column 17.8 cm)

Style: Times New Roman, 8 pt, 300 dpi
"""

import os
import numpy as np
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
from matplotlib.lines import Line2D

# ── Global style ──────────────────────────────────────────────────────
mpl.rcParams.update({
    "font.family":      "serif",
    "font.serif":       ["Times New Roman", "DejaVu Serif"],
    "font.size":        8,
    "axes.titlesize":   8,
    "axes.labelsize":   8,
    "xtick.labelsize":  7,
    "ytick.labelsize":  7,
    "legend.fontsize":  7,
    "figure.dpi":       300,
    "savefig.dpi":      300,
    "savefig.bbox":     "tight",
    "savefig.pad_inches": 0.02,
    "axes.linewidth":   0.6,
    "xtick.major.width": 0.5,
    "ytick.major.width": 0.5,
})

BASE    = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_CSV = os.path.join(BASE, "all_data", "all_data.csv")
NPY_DIR  = os.path.join(BASE, "all_data", "npy_2")
OUT_DIR  = os.path.join(BASE, "figures_new")
os.makedirs(OUT_DIR, exist_ok=True)

# Dataset name mapping (csv → paper)
DS_MAP = {
    "ALL_AML": "ALL-AML", "ALL4": "ALL4", "Adenoma": "Adenoma",
    "CNS": "CNS", "Colon": "Colon", "DLBCL": "DLBCL",
    "Leukaemia": "Leukaemia", "Lymphoma": "Lymphoma", "Stroke": "Stroke",
}
VER_MAP = {
    "MEL_KGEF": "KDS-EL", "MEL_KGEF_noNHD": "KDS-EL/KER",
    "MEL_NHD": "KDS-EL/DRS", "MEL": "MEL",
}
PAPER_DS = list(DS_MAP.keys())


# ══════════════════════════════════════════════════════════════════════
#  Helper functions
# ══════════════════════════════════════════════════════════════════════

def _box(ax, x, y, w, h, text, fc, ec="black", fs=8, bold=False,
         text_color="black", lw=0.8, zorder=2):
    """Draw a rounded box with centred text."""
    rect = FancyBboxPatch(
        (x, y), w, h,
        boxstyle="round,pad=0.04",
        linewidth=lw, edgecolor=ec, facecolor=fc, zorder=zorder,
    )
    ax.add_patch(rect)
    weight = "bold" if bold else "normal"
    ax.text(x + w / 2, y + h / 2, text,
            ha="center", va="center", fontsize=fs,
            fontweight=weight, color=text_color, zorder=zorder + 1)


def _arrow(ax, x1, y1, x2, y2, lw=0.8, color="black"):
    """Draw a straight arrow."""
    ax.annotate(
        "", (x2, y2), (x1, y1),
        arrowprops=dict(arrowstyle="-|>", lw=lw, color=color,
                        mutation_scale=8),
    )


def _curved_arrow(ax, x1, y1, x2, y2, rad=0.3, lw=0.8, color="black"):
    """Draw a curved arrow."""
    ax.annotate(
        "", (x2, y2), (x1, y1),
        arrowprops=dict(arrowstyle="-|>", lw=lw, color=color,
                        connectionstyle=f"arc3,rad={rad}", mutation_scale=8),
    )


def _load_curves(version_key, dataset):
    """Load 10-run convergence curves for a (version, dataset) pair."""
    curves = []
    for run in range(10):
        fpath = os.path.join(NPY_DIR,
                             f"curve_{version_key}_{dataset}_run{run}.npy")
        if os.path.exists(fpath):
            curves.append(np.load(fpath))
    return np.array(curves) if curves else None


# ══════════════════════════════════════════════════════════════════════
#  Figure 1 : Overall Framework  (17.8 cm × 9.0 cm)
# ══════════════════════════════════════════════════════════════════════

def make_fig1():
    print("Fig 1: KDS-EL framework ...")
    W_cm, H_cm = 17.8, 9.0
    fig, ax = plt.subplots(figsize=(W_cm / 2.54, H_cm / 2.54))
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 10)
    ax.axis("off")

    # ── Colours (muted, print-friendly) ──
    c_input  = "#d6e4f0"   # light blue
    c_init   = "#d6e4f0"
    c_pso    = "#b4d5e9"   # medium blue
    c_eval   = "#e8dff0"   # light purple
    c_drs    = "#c5e1a5"   # green
    c_ker    = "#fff9c4"   # yellow
    c_best   = "#ffcdd2"   # light red
    c_out    = "#c5e1a5"
    c_loop   = "#f5f5f5"

    # ── Dashed loop region ──
    loop = FancyBboxPatch(
        (3.3, 0.4), 12.2, 9.0,
        boxstyle="round,pad=0.15",
        linewidth=1.0, edgecolor="#9e9e9e",
        facecolor=c_loop, linestyle="--", alpha=0.5, zorder=0,
    )
    ax.add_patch(loop)
    ax.text(9.4, 9.0, "Main Iterative Loop  ($t = 1, \\ldots, T$)",
            ha="center", va="center", fontsize=8,
            fontweight="bold", color="#616161")

    # ── Input ──
    _box(ax, 0.3, 4.0, 2.4, 1.6,
         "Input\nDataset\n$(\\mathbf{X},\\, \\mathbf{y})$",
         c_input, fs=8)

    # ── Initialise ──
    _box(ax, 3.6, 4.0, 2.6, 1.6,
         "Initialise Population\n$\\mathbf{V},\\, P_{\\mathrm{best}},\\, \\mathbf{w}=\\mathbf{0}$",
         c_init, fs=7.5)

    # ── Sub1: PSO Exploration ──
    _box(ax, 6.8, 7.0, 3.0, 1.4,
         "Subpopulation 1\nPSO Exploration\n(Eq.\\ 2)",
         c_pso, fs=7.5, bold=True)

    # ── Sub2: Weight-guided Sampling ──
    _box(ax, 6.8, 5.0, 3.0, 1.4,
         "Subpopulation 2\nWeight-guided Sampling",
         c_pso, fs=7.5, bold=True)

    # ── Fitness Evaluation ──
    _box(ax, 6.8, 2.8, 3.0, 1.4,
         "Fitness Evaluation\n(Eq.\\ 1: KNN-CV)",
         c_eval, fs=7.5)

    # ── DRS (Structural Space) ──
    _box(ax, 10.6, 7.0, 4.2, 1.8,
         "DRS  (Structural Space)\nBi-criteria Pareto Selection\nFitness $+$ NHD  (Eqs.\\ 3–5)",
         c_drs, fs=7.5, bold=True, ec="#558b2f")

    # ── KER (Fitness Space) ──
    _box(ax, 10.6, 4.6, 4.2, 1.8,
         "KER  (Fitness Space)\nWeight Update $+$ Elite Perturbation\n(Eqs.\\ 6–7)",
         c_ker, fs=7.5, bold=True, ec="#f9a825")

    # ── Update Gbest ──
    _box(ax, 10.6, 2.4, 4.2, 1.4,
         "Update $G_{\\mathrm{best}}$\nand Decay $\\mathbf{w}$",
         c_best, fs=7.5)

    # ── Output ──
    _box(ax, 12.0, 0.5, 2.8, 1.2,
         "Output  $\\mathbf{s}^{*}$",
         c_out, fs=8, bold=True, ec="#558b2f")

    # ── Arrows ──
    _arrow(ax, 2.7, 4.8, 3.6, 4.8)          # input → init
    _arrow(ax, 6.2, 5.2, 6.8, 7.4)          # init → sub1
    _arrow(ax, 6.2, 4.4, 6.8, 5.6)          # init → sub2
    _arrow(ax, 8.3, 7.0, 8.3, 4.2)          # sub1 → eval
    _arrow(ax, 8.3, 5.0, 8.3, 4.2)          # sub2 → eval
    _arrow(ax, 9.8, 7.6, 10.6, 7.6)         # sub1 → DRS
    _arrow(ax, 9.8, 5.6, 10.6, 5.4)         # sub2 → KER
    _arrow(ax, 9.8, 3.4, 10.6, 3.0)         # eval → Gbest
    _arrow(ax, 12.7, 7.0, 12.7, 6.4)        # DRS → KER
    _arrow(ax, 12.7, 4.6, 12.7, 3.8)        # KER → Gbest
    _arrow(ax, 13.4, 2.4, 13.4, 1.7)        # Gbest → output

    # ── Synergy arrow ──
    _curved_arrow(ax, 14.8, 6.0, 14.8, 5.0, rad=-0.6, color="#c62828", lw=1.0)
    ax.text(15.4, 5.5, "Synergy", ha="center", va="center",
            fontsize=7, color="#c62828", fontstyle="italic")

    # ── Loop-back arrow ──
    _curved_arrow(ax, 12.7, 7.8, 8.3, 8.8, rad=-0.35, color="#c62828", lw=0.9)
    ax.text(10.5, 8.7, "Iterate", ha="center", va="center",
            fontsize=7, color="#c62828", fontstyle="italic")

    # ── Legend ──
    leg_y = 1.4
    for lbl, clr, dx in [("Structural Space", c_drs, 0),
                          ("Fitness Space", c_ker, 5.5)]:
        ax.add_patch(FancyBboxPatch((0.5 + dx, leg_y), 0.4, 0.35,
                     boxstyle="round,pad=0.03", facecolor=clr,
                     edgecolor="gray", linewidth=0.5))
        ax.text(1.05 + dx, leg_y + 0.17, lbl, fontsize=7, va="center")

    fig.tight_layout(pad=0.1)
    fig.savefig(os.path.join(OUT_DIR, "fig1_framework.png"))
    fig.savefig(os.path.join(OUT_DIR, "fig1_framework.pdf"))
    plt.close(fig)
    print("  → fig1_framework.png/pdf")


# ══════════════════════════════════════════════════════════════════════
#  Figure 2 : DRS Mechanism — Real Pareto Data  (17.8 cm × 7.0 cm)
# ══════════════════════════════════════════════════════════════════════

def make_fig2():
    print("Fig 2: DRS mechanism (real data) ...")
    df = pd.read_csv(DATA_CSV)
    df = df[df["Dataset"].isin(PAPER_DS)].copy()
    df["Version"] = df["Version"].map(VER_MAP).fillna(df["Version"])

    W_cm, H_cm = 17.8, 7.0
    fig, (ax1, ax2) = plt.subplots(
        1, 2, figsize=(W_cm / 2.54, H_cm / 2.54),
        gridspec_kw={"wspace": 0.35},
    )

    # ── (a) Pareto scatter: Accuracy vs NHD ──
    styles = {
        "KDS-EL":     {"c": "#c62828", "marker": "o",  "s": 28, "zorder": 4},
        "KDS-EL/DRS": {"c": "#2e7d32", "marker": "s",  "s": 24, "zorder": 3},
        "KDS-EL/KER": {"c": "#1565c0", "marker": "^",  "s": 24, "zorder": 3},
        "MEL":        {"c": "#9e9e9e", "marker": "D",  "s": 20, "zorder": 2},
    }
    for ver, st in styles.items():
        sub = df[df["Version"] == ver]
        ax1.scatter(
            sub["Accuracy"], sub["Avg_NHD"],
            c=st["c"], marker=st["marker"], s=st["s"],
            alpha=0.55, edgecolors="white", linewidths=0.3,
            label=ver, zorder=st["zorder"],
        )

    # Compute and draw Pareto front on KDS-EL points
    kds = df[df["Version"] == "KDS-EL"][["Accuracy", "Avg_NHD"]].values
    # Pareto front: maximise accuracy, maximise NHD
    is_dominated = np.zeros(len(kds), dtype=bool)
    for i in range(len(kds)):
        for j in range(len(kds)):
            if i != j:
                if (kds[j, 0] >= kds[i, 0] and kds[j, 1] >= kds[i, 1] and
                    (kds[j, 0] > kds[i, 0] or kds[j, 1] > kds[i, 1])):
                    is_dominated[i] = True
                    break
    front = kds[~is_dominated]
    order = np.argsort(front[:, 0])
    ax1.plot(front[order, 0], front[order, 1],
             "--", color="#c62828", lw=1.0, alpha=0.7, zorder=5,
             label="Pareto front")

    ax1.set_xlabel("Classification Accuracy")
    ax1.set_ylabel("Average NHD (population diversity)")
    ax1.set_title("(a) Bi-criteria Pareto Selection  (real experimental data)")
    ax1.legend(loc="lower right", framealpha=0.9, edgecolor="gray")
    ax1.grid(True, ls="--", alpha=0.3)

    # ── (b) Adaptive schedule ──
    t = np.linspace(0, 100, 300)
    alpha_cd = (t / 100) ** 2

    ax2.plot(t, alpha_cd, color="#c62828", lw=1.5,
             label=r"$\alpha_{\mathrm{cd}}(t)=(t/T)^2$")
    ax2.plot(t, 1 - alpha_cd, color="#2e7d32", lw=1.5, ls="--",
             label=r"$1-\alpha_{\mathrm{cd}}(t)$")

    ax2.fill_between(t, 0, alpha_cd, alpha=0.06, color="#2e7d32")
    ax2.fill_between(t, alpha_cd, 1, alpha=0.06, color="#c62828")

    ax2.annotate("Early: diversity\npriority",
                 xy=(15, (15 / 100) ** 2), xytext=(28, 0.78),
                 fontsize=7, color="#2e7d32",
                 arrowprops=dict(arrowstyle="->", color="#2e7d32", lw=0.7))
    ax2.annotate("Late: fitness\npriority",
                 xy=(85, (85 / 100) ** 2), xytext=(55, 0.18),
                 fontsize=7, color="#c62828",
                 arrowprops=dict(arrowstyle="->", color="#c62828", lw=0.7))

    ax2.set_xlabel("Iteration $t$")
    ax2.set_ylabel("Weight")
    ax2.set_title("(b) Adaptive Diversity--Fitness Schedule")
    ax2.legend(loc="center", framealpha=0.9, edgecolor="gray")
    ax2.grid(True, ls="--", alpha=0.3)

    fig.tight_layout(w_pad=3)
    fig.savefig(os.path.join(OUT_DIR, "fig2_drs_mechanism.png"))
    fig.savefig(os.path.join(OUT_DIR, "fig2_drs_mechanism.pdf"))
    plt.close(fig)
    print("  → fig2_drs_mechanism.png/pdf")


# ══════════════════════════════════════════════════════════════════════
#  Figure 3 : KER Mechanism — Real Convergence Data  (17.8 cm × 7.0 cm)
# ══════════════════════════════════════════════════════════════════════

def make_fig3():
    print("Fig 3: KER mechanism (real convergence data) ...")

    W_cm, H_cm = 17.8, 7.0
    fig, (ax1, ax2) = plt.subplots(
        1, 2, figsize=(W_cm / 2.54, H_cm / 2.54),
        gridspec_kw={"wspace": 0.35},
    )

    for ax in (ax1, ax2):
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)

    # ── (a) Convergence curves: real data from Colon ──
    dataset = "Colon"
    versions = [
        ("MEL_KGEF",      "KDS-EL\n(Proposed)", "#b71c1c", "-",  2.0),
        ("MEL_KGEF_noNHD", "KDS-EL/KER",        "#1565c0", "--", 1.4),
        ("MEL_NHD",        "KDS-EL/DRS",        "#2e7d32", "-.", 1.4),
        ("MEL",            "MEL\n(Baseline)",    "#9e9e9e", ":",  1.4),
    ]

    for vkey, vname, clr, ls, lw in versions:
        curves = _load_curves(vkey, dataset)
        if curves is None:
            continue
        mean = curves.mean(axis=0)
        std  = curves.std(axis=0)
        iters = np.arange(len(mean))
        ax1.plot(iters, mean, color=clr, ls=ls, lw=lw, label=vname,
                 markerfacecolor="none", markeredgecolor=clr,
                 markevery=max(1, len(mean) // 12), markersize=3.5)
        ax1.fill_between(iters, mean - std, mean + std,
                         color=clr, alpha=0.12, linewidth=0)

    ax1.set_xlabel("Iteration $t$")
    ax1.set_ylabel("Fitness  $f(\\mathbf{s})$")
    ax1.set_title("(a) Convergence Curves  (Colon, $d=2{,}000$)", pad=4)
    ax1.legend(loc="upper right", frameon=True, framealpha=0.92,
               edgecolor="0.6", fontsize=6.5,
               handlelength=1.5, handleheight=0.85)
    ax1.grid(True, ls="--", alpha=0.4, linewidth=0.35)

    # ── (b) NHD diversity curves: real data from Colon ──
    df = pd.read_csv(DATA_CSV)
    df = df[df["Dataset"].isin(PAPER_DS)].copy()
    df["Version"] = df["Version"].map(VER_MAP).fillna(df["Version"])

    # Show NHD comparison across datasets for ablation variants
    ablation_vers = ["MEL", "KDS-EL/KER", "KDS-EL/DRS", "KDS-EL"]
    colors_bars = ["#9e9e9e", "#1565c0", "#2e7d32", "#b71c1c"]
    hatch_pats = ["....", "++++", "xxxx", ""]
    ablation_labels = ["MEL (NHD$=0$)", "KDS-EL/KER (NHD$=0$)",
                       "KDS-EL/DRS", "KDS-EL (Proposed)"]

    rep_ds = ["Adenoma", "Colon", "Lymphoma", "Stroke"]
    rep_labels = ["Adenoma", "Colon", "Lymphoma", "Stroke"]
    x = np.arange(len(rep_ds))
    n_v = len(ablation_vers)
    width = 0.19
    gap = 0.01
    total = n_v * width + (n_v - 1) * gap
    offs = np.linspace(-(total - width) / 2, (total - width) / 2, n_v)

    for i, (ver, clr, ht, lbl) in enumerate(
            zip(ablation_vers, colors_bars, hatch_pats, ablation_labels)):
        vals = []
        errs = []
        for ds in rep_ds:
            sub = df[(df["Dataset"] == ds) & (df["Version"] == ver)]
            vals.append(sub["Avg_NHD"].mean())
            errs.append(sub["Avg_NHD"].std())
        bars = ax2.bar(x + offs[i], vals, width, color=clr, label=lbl,
                       edgecolor="k" if ht else clr, linewidth=0.4,
                       yerr=errs, error_kw=dict(elinewidth=0.5, capsize=1.2,
                                                 capthick=0.5, ecolor="0.35"))
        for bar in bars:
            if ht:
                bar.set_hatch(ht)
        # Highlight proposed method border
        if ver == "MEL_KGEF":
            for bar in bars:
                bar.set_edgecolor("#b71c1c")
                bar.set_linewidth(1.1)

    ax2.set_xticks(x)
    ax2.set_xticklabels(rep_labels)
    ax2.set_ylabel("Average NHD")
    ax2.set_title("(b) Population Diversity Across Datasets", pad=4)
    handles2 = [plt.Rectangle((0, 0), 1, 1, fc=clr, hatch=ht,
                 ec="k" if ht else clr, lw=0.4)
                for clr, ht in zip(colors_bars, hatch_pats)]
    ax2.legend(handles2, ablation_labels,
               loc="upper left", frameon=True, framealpha=0.92,
               edgecolor="0.6", fontsize=6.5, ncol=2,
               handlelength=1.1, handleheight=0.85)
    ax2.grid(axis="y", ls="--", alpha=0.4, linewidth=0.35)

    fig.tight_layout(w_pad=3)
    fig.savefig(os.path.join(OUT_DIR, "fig3_ker_mechanism.png"))
    fig.savefig(os.path.join(OUT_DIR, "fig3_ker_mechanism.pdf"))
    plt.close(fig)
    print("  → fig3_ker_mechanism.png/pdf")


# ══════════════════════════════════════════════════════════════════════
#  Main
# ══════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    make_fig1()
    make_fig2()
    make_fig3()
    print("\nAll figures saved to", OUT_DIR)
