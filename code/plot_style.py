"""
plot_style.py: Nature / Elsevier Top-Journal Scientific Plotting Style
======================================================================
Implements a restrained semantic hierarchy:
- Focus (Proposed KDS-EL): Nature Vermilion (#C82423)
- Ablation Variants: Cohesive Ocean/Slate Blue progression (#2B6CB0 -> #5C82A6 -> #718096)
- SOTA Competitors: Low-saturation warm slate gray progression (#64748B -> #B4BFC8)
- MOFS Competitors: Low-saturation cool slate gray progression (#5F7176 -> #B3C3C8)

Markers are applied ONLY to line/convergence plots and scatter plots,
keeping bar charts and heatmaps clean and free of chartjunk.
"""

import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import matplotlib.patches as mpatches

# ── 1. Elsevier / Nature Publication Typography & rcParams ──
ELSEVIER_RC_PARAMS = {
    "font.family": "DejaVu Serif",
    "font.size": 8.0,
    "axes.titlesize": 8.5,
    "axes.titleweight": "bold",
    "axes.labelsize": 8.0,
    "axes.labelweight": "normal",
    "xtick.labelsize": 7.0,
    "ytick.labelsize": 7.0,
    "legend.fontsize": 7.0,
    "legend.title_fontsize": 7.5,
    "legend.framealpha": 0.95,
    "legend.edgecolor": "#CBD5E0",
    "legend.borderpad": 0.35,
    "axes.linewidth": 0.7,
    "axes.edgecolor": "#4A5568",
    "grid.color": "#E2E8F0",
    "grid.linestyle": "--",
    "grid.linewidth": 0.4,
    "grid.alpha": 0.75,
    "lines.linewidth": 1.1,
    "lines.markersize": 4.5,
    "patch.linewidth": 0.5,
    "xtick.major.width": 0.7,
    "ytick.major.width": 0.7,
    "xtick.major.size": 2.5,
    "ytick.major.size": 2.5,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "figure.dpi": 300,
    "savefig.dpi": 300,
    "savefig.bbox": "tight",
    "savefig.pad_inches": 0.02,
    "pdf.fonttype": 42,
    "ps.fonttype": 42,
}


def apply_style():
    """Apply unified Elsevier/Nature publication styling."""
    mpl.rcParams.update(ELSEVIER_RC_PARAMS)


# ── 2. Nature/Elsevier Restrained Semantic Palette ──
COLOR_PALETTE = {
    # 🔴 Focus: Proposed KDS-EL
    "KDS_EL_TwoPhase": "#C82423",  # Nature Vermilion / Crimson

    # 🔵 Ablation Progression
    "KDS_EL_NoPool":   "#2B6CB0",  # Ocean Blue (KDS-EL w/o TPS)
    "MEL_MI":          "#5C82A6",  # Slate Blue (KDS-EL w/o TPS&KER)
    "MEL":             "#718096",  # Slate Gray (MEL Baseline)

    # ⚪ Single-Objective SOTA & Competitors
    "bIRIME":          "#D97706",  # Warm Amber (Top competitor)
    "FWPSO":           "#64748B",  # Slate 500
    "PSO_CSM":         "#788698",  # Slate Tint 1
    "BinCOA":          "#059669",  # Emerald Green
    "SaWDE":           "#8C99A8",  # Slate Tint 2
    "IGPSO":           "#A0ACB8",  # Slate Tint 3
    "DENCA_SO":        "#4F46E5",  # Indigo
    "BPSO":            "#B4BFC8",  # Slate Tint 4
}

# Distinct geometric markers for trajectories and scatter plots only
MARKERS = {
    "KDS_EL_TwoPhase": "o",   # Circle (Proposed)
    "KDS_EL_NoPool":   "s",   # Square
    "MEL_MI":          "^",   # Triangle Up
    "MEL":             "v",   # Triangle Down
    "bIRIME":          "P",   # Plus Filled
    "FWPSO":           "D",   # Diamond
    "PSO_CSM":         "p",   # Pentagon
    "BinCOA":          "h",   # Hexagon
    "SaWDE":           "<",   # Triangle Left
    "IGPSO":           ">",   # Triangle Right
    "DENCA_SO":        "d",   # Thin Diamond
    "BPSO":            "x",   # Cross
}

LINESTYLES = {
    "KDS_EL_TwoPhase": "-",
    "KDS_EL_NoPool":   "--",
    "MEL_MI":          "-.",
    "MEL":             ":",
    "bIRIME":          "-",
    "FWPSO":           "--",
    "PSO_CSM":         "-.",
    "BinCOA":          ":",
    "SaWDE":           "-",
    "IGPSO":           "--",
    "DENCA_SO":        "-.",
    "BPSO":            ":",
}

V_LABELS = {
    "KDS_EL_TwoPhase": "KDS-EL",
    "KDS_EL_NoPool":   "KDS-EL w/o TPS",
    "MEL_MI":          "KDS-EL w/o TPS\\&KER",
    "MEL":             "MEL",
    "bIRIME":          "bIRIME",
    "FWPSO":           "FWPSO",
    "PSO_CSM":         "PSO-CSM",
    "BinCOA":          "BinCOA",
    "SaWDE":           "SaWDE",
    "IGPSO":           "IGPSO",
    "DENCA_SO":        "DENCA-SO",
    "BPSO":            "BPSO",
}

ORDERED_METHODS = [
    "KDS_EL_TwoPhase",
    "KDS_EL_NoPool",
    "MEL_MI",
    "MEL",
    "bIRIME",
    "FWPSO",
    "PSO_CSM",
    "BinCOA",
    "SaWDE",
    "IGPSO",
    "DENCA_SO",
    "BPSO",
]


def set_axis_style(ax, title=None, xlabel=None, ylabel=None, grid=True):
    """Convenience helper to set standard axis styling."""
    if title:
        ax.set_title(title, fontsize=8.5, fontweight="bold", pad=4.0)
    if xlabel:
        ax.set_xlabel(xlabel, fontsize=8.0, labelpad=3.0)
    if ylabel:
        ax.set_ylabel(ylabel, fontsize=8.0, labelpad=3.0)
    if grid:
        ax.grid(True, linestyle="--", linewidth=0.4, color="#E2E8F0", alpha=0.75)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_linewidth(0.7)
    ax.spines["bottom"].set_linewidth(0.7)
    ax.spines["left"].set_color("#4A5568")
    ax.spines["bottom"].set_color("#4A5568")
    ax.tick_params(axis="both", which="both", labelsize=7.0, width=0.7, length=2.5)


def make_legend_handles(versions, mode="line"):
    """Create unified legend handles for a list of versions."""
    handles = []
    for v in versions:
        label = V_LABELS.get(v, v)
        color = COLOR_PALETTE.get(v, "#4A5568")
        if mode == "line":
            marker = MARKERS.get(v, "o")
            ls = LINESTYLES.get(v, "-")
            h = Line2D([0], [0], color=color, marker=marker, linestyle=ls,
                       linewidth=1.2, markersize=4.5, label=label)
        elif mode == "bar" or mode == "patch":
            h = mpatches.Patch(facecolor=color, edgecolor="none", label=label)
        elif mode == "scatter":
            marker = MARKERS.get(v, "o")
            h = Line2D([0], [0], color="none", marker=marker, markerfacecolor=color,
                       markeredgecolor="none", markersize=6.0, label=label)
        handles.append(h)
    return handles
