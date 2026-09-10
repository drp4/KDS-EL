import os, sys
import numpy as np
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
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
n_m = len(sorted_methods)
y_pos = np.arange(n_m)

out_dir = PROJ / "scratch"
out_dir.mkdir(exist_ok=True)

# ------------------------------------------------------------------------------
# Candidate A: "Hero + Monochromatic Slate Progression" (Top Journal Elegance)
# KDS-EL in vivid Nature Vermilion, all others in a smooth, unified slate ramp
# ------------------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(3.45, 3.2), dpi=300)

# Colors: KDS-EL Vermilion; all competitors smooth cohesive slate from 0.45 to 0.85
colors_a = []
edgecolors_a = []
for i, v in enumerate(sorted_methods):
    if v == "KDS_EL_TwoPhase":
        colors_a.append("#C82423")
        edgecolors_a.append("#8B0000")
    elif "KDS" in v:
        colors_a.append("#3B82F6")
        edgecolors_a.append("#1D4ED8")
    elif v == "MEL":
        colors_a.append("#64748B")
        edgecolors_a.append("#475569")
    else:
        # Monochromatic slate
        colors_a.append("#64748B")
        edgecolors_a.append("#475569")

bars = ax.barh(y_pos, values, height=0.66, color=colors_a, edgecolor=edgecolors_a, linewidth=0.6)

# CD threshold (Demšar Bonferroni-Dunn cutoff = 5.00)
ax.axvline(x=5.00, color="#DC2626", linestyle="--", linewidth=0.8, alpha=0.75, zorder=1)
ax.text(5.08, 11.2, r"CD cutoff ($p < 0.05$)", fontsize=6.2, color="#DC2626", fontweight="bold", va="bottom")

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
ax.set_xlabel("Average Friedman rank (lower is better)", fontsize=7.5, labelpad=3)
ax.grid(axis="x", linestyle="--", alpha=0.4, linewidth=0.4, color="#CBD5E0")
ax.set_xlim(0, 11.9)
ax.tick_params(axis="both", which="both", labelsize=6.8, length=2.0)
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.spines["left"].set_linewidth(0.6)
ax.spines["bottom"].set_linewidth(0.6)

plt.tight_layout(pad=0.25)
fig.savefig(out_dir / "cand_a.png", dpi=300)
plt.close(fig)

# ------------------------------------------------------------------------------
# Candidate B: Pure Unified Slate (ONLY KDS-EL is Vermilion, ALL 11 others uniform Slate)
# This is the gold-standard "The Economist" style
# ------------------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(3.45, 3.2), dpi=300)

colors_b = ["#C82423" if v == "KDS_EL_TwoPhase" else "#64748B" for v in sorted_methods]
edges_b = ["#8B0000" if v == "KDS_EL_TwoPhase" else "#475569" for v in sorted_methods]

bars = ax.barh(y_pos, values, height=0.66, color=colors_b, edgecolor=edges_b, linewidth=0.6)

# CD threshold
ax.axvline(x=5.00, color="#C82423", linestyle="--", linewidth=0.8, alpha=0.75, zorder=1)
ax.text(5.08, 11.2, r"CD cutoff ($p < 0.05$)", fontsize=6.2, color="#C82423", fontweight="bold", va="bottom")

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
ax.set_xlabel("Average Friedman rank (lower is better)", fontsize=7.5, labelpad=3)
ax.grid(axis="x", linestyle="--", alpha=0.4, linewidth=0.4, color="#CBD5E0")
ax.set_xlim(0, 11.9)
ax.tick_params(axis="both", which="both", labelsize=6.8, length=2.0)
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.spines["left"].set_linewidth(0.6)
ax.spines["bottom"].set_linewidth(0.6)

plt.tight_layout(pad=0.25)
fig.savefig(out_dir / "cand_b.png", dpi=300)
plt.close(fig)

# ------------------------------------------------------------------------------
# Candidate C: Figure 5 exact colors for the 5 Figure-5 methods, unified slate for all others
# In Fig 5: KDS-EL (#C82423), FWPSO (#1E88E5), SaWDE (#00897B), MEL (#7E57C2), BPSO (#475569)
# BUT wait, that creates the rainbow. Let's see: what if the 3 categories are:
# Proposed (Vermilion), Ablation (Steel Blue #4682B4), SOTA Competitors (#94A3B8)
# ------------------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(3.45, 3.2), dpi=300)

colors_c = []
edges_c = []
for v in sorted_methods:
    if v == "KDS_EL_TwoPhase":
        colors_c.append("#C82423")
        edges_c.append("#8B0000")
    elif v in {"KDS_EL_NoPool", "MEL_MI"}:
        colors_c.append("#3B82F6")
        edges_c.append("#1D4ED8")
    elif v == "MEL":
        colors_c.append("#6B7280")
        edges_c.append("#4B5563")
    else:
        colors_c.append("#94A3B8")
        edges_c.append("#64748B")

bars = ax.barh(y_pos, values, height=0.66, color=colors_c, edgecolor=edges_c, linewidth=0.6)

# CD threshold
ax.axvline(x=5.00, color="#C82423", linestyle="--", linewidth=0.8, alpha=0.75, zorder=1)
ax.text(5.08, 11.2, r"CD cutoff ($p < 0.05$)", fontsize=6.2, color="#C82423", fontweight="bold", va="bottom")

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
ax.set_xlabel("Average Friedman rank (lower is better)", fontsize=7.5, labelpad=3)
ax.grid(axis="x", linestyle="--", alpha=0.4, linewidth=0.4, color="#CBD5E0")
ax.set_xlim(0, 11.9)
ax.tick_params(axis="both", which="both", labelsize=6.8, length=2.0)
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.spines["left"].set_linewidth(0.6)
ax.spines["bottom"].set_linewidth(0.6)

plt.tight_layout(pad=0.25)
fig.savefig(out_dir / "cand_c.png", dpi=300)
plt.close(fig)

print("Saved cand_a, cand_b, cand_c!")
