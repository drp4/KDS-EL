import os, sys
import numpy as np
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

PROJ = Path(r"e:\多目标优化\KDS-EL")
sys.path.insert(0, str(PROJ / "code"))

from generate_figures import load_merged_detail, ALL_VERSIONS, PLOT_DATASETS, g
from plot_style import apply_style

apply_style()

df = load_merged_detail()
versions = [v for v in ALL_VERSIONS if v in df.Version.unique()]
ds_list = [d for d in PLOT_DATASETS if d in df.Dataset.unique()]

ranks = {v: [] for v in versions}
for ds in ds_list:
    ds_means = {}
    for v in versions:
        arr = g(df, v, ds)
        if len(arr) > 0 and not np.isnan(arr).all():
            ds_means[v] = np.nanmean(arr)
    if ds_means:
        sorted_v = sorted(ds_means, key=ds_means.get, reverse=True)
        i = 0
        while i < len(sorted_v):
            j = i
            while (j + 1 < len(sorted_v) and ds_means[sorted_v[j + 1]] == ds_means[sorted_v[i]]):
                j += 1
            avg_rank = (i + 1 + j + 1) / 2.0
            for v in sorted_v[i:j + 1]:
                ranks[v].append(avg_rank)
            i = j + 1

avg_ranks = {v: np.mean(ranks[v]) for v in versions if ranks[v]}
sorted_methods = sorted(avg_ranks, key=avg_ranks.get)

# Label mapping
V_LABELS = {
    "KDS_EL_TwoPhase": "KDS-EL",
    "KDS_EL_NoPool": "KDS-EL w/o TPS",
    "MEL_MI": "KDS-EL w/o TPS & KER",
    "MEL": "MEL",
    "bIRIME": "bIRIME",
    "FWPSO": "FWPSO",
    "PSO_CSM": "PSO-CSM",
    "BinCOA": "BinCOA",
    "SaWDE": "SaWDE",
    "IGPSO": "IGPSO",
    "DENCA_SO": "DENCA-SO",
    "BPSO": "BPSO",
}

values = [avg_ranks[v] for v in sorted_methods]
labels = [V_LABELS.get(v, v) for v in sorted_methods]

out_dir = PROJ / "scratch"
out_dir.mkdir(exist_ok=True)

# ==============================================================================
# Design 1: Native Single-Column (3.45 in), Hero Vermilion + Cohesive Slate Progression + CD line
# ==============================================================================
fig, ax = plt.subplots(figsize=(3.45, 3.2), dpi=300)
y_pos = np.arange(len(sorted_methods))

# Colors: KDS-EL vermilion, ablations refined blue-slate, competitors clean slate
colors = []
edgecolors = []
for v in sorted_methods:
    if v == "KDS_EL_TwoPhase":
        colors.append("#C82423")
        edgecolors.append("#8B0000")
    elif v == "KDS_EL_NoPool":
        colors.append("#2B6CB0")
        edgecolors.append("#1A365D")
    elif v == "MEL_MI":
        colors.append("#4A5568")
        edgecolors.append("#2D3748")
    else:
        colors.append("#94A3B8")
        edgecolors.append("#64748B")

bars = ax.barh(y_pos, values, height=0.68, color=colors, edgecolor=edgecolors, linewidth=0.6, alpha=0.92)

# CD threshold (Demšar Bonferroni-Dunn at alpha=0.05, CD = 3.25, threshold = 1.75 + 3.25 = 5.00)
cd_val = 1.75 + 3.25
ax.axvline(x=cd_val, color="#E53E3E", linestyle="--", linewidth=0.8, alpha=0.85, zorder=2)
ax.text(cd_val + 0.12, 11.2, f"CD cutoff ({cd_val:.2f})", fontsize=6.2, color="#C53030", fontweight="bold", va="bottom")

for i, (v, bar) in enumerate(zip(sorted_methods, bars)):
    val_str = f"{values[i]:.2f}"
    is_kds = (v == "KDS_EL_TwoPhase")
    txt_col = "#C82423" if is_kds else "#334155"
    font_wt = "bold" if is_kds else "normal"
    ax.text(bar.get_width() + 0.18, bar.get_y() + bar.get_height() / 2,
            val_str, va="center", ha="left", fontsize=6.8,
            fontweight=font_wt, color=txt_col)

ax.set_yticks(y_pos)
ax.set_yticklabels(labels, fontsize=7.2)
for tick_label in ax.get_yticklabels():
    if tick_label.get_text() == "KDS-EL":
        tick_label.set_fontweight("bold")
        tick_label.set_color("#C82423")

ax.invert_yaxis()
ax.set_xlabel("Average Friedman Rank (lower is better)", fontsize=7.5, labelpad=3)
ax.grid(axis="x", linestyle="--", alpha=0.45, linewidth=0.4, color="#CBD5E0")
ax.set_xlim(0, 11.8)
ax.tick_params(axis="both", which="both", labelsize=6.8, length=2.0)
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.spines["left"].set_linewidth(0.6)
ax.spines["bottom"].set_linewidth(0.6)

plt.tight_layout(pad=0.3)
fig.savefig(out_dir / "test_fig6_design1.png", dpi=300)
plt.close(fig)

# ==============================================================================
# Design 2: High-contrast Academic Palette (Hero Vermilion + Categorical Palette + Clean Annotations)
# ==============================================================================
fig, ax = plt.subplots(figsize=(3.45, 3.2), dpi=300)
colors2 = []
for v in sorted_methods:
    if v == "KDS_EL_TwoPhase":
        colors2.append("#C82423")
    elif v in {"KDS_EL_NoPool", "MEL_MI"}:
        colors2.append("#1E88E5")
    elif v == "bIRIME":
        colors2.append("#64748B")
    else:
        colors2.append("#94A3B8")

bars = ax.barh(y_pos, values, height=0.72, color=colors2, edgecolor="none", alpha=0.92)

# CD threshold
ax.axvline(x=5.00, color="#C82423", linestyle=":", linewidth=0.9, alpha=0.8, zorder=2)
ax.text(5.08, 0.2, r"Critical Diff. ($\alpha=0.05$)", fontsize=6.0, color="#C82423", fontstyle="italic")

for i, (v, bar) in enumerate(zip(sorted_methods, bars)):
    val_str = f"{values[i]:.2f}"
    is_kds = (v == "KDS_EL_TwoPhase")
    txt_col = "#C82423" if is_kds else "#1E293B"
    font_wt = "bold" if is_kds else "normal"
    ax.text(bar.get_width() + 0.18, bar.get_y() + bar.get_height() / 2,
            val_str, va="center", ha="left", fontsize=6.8,
            fontweight=font_wt, color=txt_col)

ax.set_yticks(y_pos)
ax.set_yticklabels(labels, fontsize=7.2)
for tick_label in ax.get_yticklabels():
    if tick_label.get_text() == "KDS-EL":
        tick_label.set_fontweight("bold")
        tick_label.set_color("#C82423")

ax.invert_yaxis()
ax.set_xlabel("Average Friedman Rank (lower is better)", fontsize=7.5, labelpad=3)
ax.grid(axis="x", linestyle="--", alpha=0.45, linewidth=0.4, color="#E2E8F0")
ax.set_xlim(0, 11.9)
ax.tick_params(axis="both", which="both", labelsize=6.8, length=2.0)
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)

plt.tight_layout(pad=0.3)
fig.savefig(out_dir / "test_fig6_design2.png", dpi=300)
plt.close(fig)

# ==============================================================================
# Design 3: Top-Journal Two-Tone (Proposed KDS-EL Family vs Competitor Suite)
# ==============================================================================
fig, ax = plt.subplots(figsize=(3.45, 3.2), dpi=300)
colors3 = []
edgecolors3 = []
for v in sorted_methods:
    if v == "KDS_EL_TwoPhase":
        colors3.append("#C82423")  # Nature Vermilion
        edgecolors3.append("#991B1B")
    elif v == "KDS_EL_NoPool":
        colors3.append("#3B82F6")  # Blue
        edgecolors3.append("#1D4ED8")
    elif v == "MEL_MI":
        colors3.append("#0D9488")  # Teal
        edgecolors3.append("#0F766E")
    elif v == "MEL":
        colors3.append("#8B5CF6")  # Violet
        edgecolors3.append("#6D28D9")
    else:
        colors3.append("#CBD5E1")  # Clean Slate Gray
        edgecolors3.append("#94A3B8")

bars = ax.barh(y_pos, values, height=0.68, color=colors3, edgecolor=edgecolors3, linewidth=0.5, alpha=0.92)

# CD threshold
ax.axvline(x=5.00, color="#64748B", linestyle="--", linewidth=0.8, alpha=0.85, zorder=2)
ax.text(5.12, 11.2, r"CD line ($p < 0.05$)", fontsize=6.2, color="#475569", fontweight="bold")

for i, (v, bar) in enumerate(zip(sorted_methods, bars)):
    val_str = f"{values[i]:.2f}"
    is_kds = (v == "KDS_EL_TwoPhase")
    txt_col = "#C82423" if is_kds else "#1E293B"
    font_wt = "bold" if is_kds else "normal"
    ax.text(bar.get_width() + 0.18, bar.get_y() + bar.get_height() / 2,
            val_str, va="center", ha="left", fontsize=6.8,
            fontweight=font_wt, color=txt_col)

ax.set_yticks(y_pos)
ax.set_yticklabels(labels, fontsize=7.2)
for tick_label in ax.get_yticklabels():
    if tick_label.get_text() == "KDS-EL":
        tick_label.set_fontweight("bold")
        tick_label.set_color("#C82423")

ax.invert_yaxis()
ax.set_xlabel("Average Friedman Rank (lower is better)", fontsize=7.5, labelpad=3)
ax.grid(axis="x", linestyle="--", alpha=0.45, linewidth=0.4, color="#E2E8F0")
ax.set_xlim(0, 11.8)
ax.tick_params(axis="both", which="both", labelsize=6.8, length=2.0)
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)

plt.tight_layout(pad=0.3)
fig.savefig(out_dir / "test_fig6_design3.png", dpi=300)
plt.close(fig)

print("Saved test designs to scratch!")
