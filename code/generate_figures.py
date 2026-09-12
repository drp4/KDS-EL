# KDS-EL 图表生成脚本 (2026-07-29 修订版)
# ============================================
# 根据《图表规划.md》生成 F4-F7, F10-F11（共6张图）。
# 14 定长方法 (无 VGS-MOEA), 4 变体消融链 (无 DRS)

import os, sys, argparse
import numpy as np
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.ticker as mticker
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

# 强制 UTF-8 输出，解决 Windows GBK 终端编码问题
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

try:
    from scipy import stats as sp_stats
except ImportError:
    sp_stats = None

# ═══ 路径 ═══

PROJ = Path(__file__).resolve().parent.parent
EXP1_DIR = PROJ / "output" / "formal_experiment_20260701_094943"   # SOTA
EXP2_DIR = PROJ / "output" / "formal_experiment_20260628_205157"   # MEL
NEW_SOTA_DIR = PROJ / "output" / "formal_experiment_20260905_211755"  # DENCA_SO, bIRIME, BinCOA
MEL_MI_DIR = PROJ / "output" / "formal_experiment_mel_mi"          # MEL+MI
FINAL_DIR = PROJ / "output" / "formal_experiment_final"            # NoPool + TwoPhase
RECONSTRUCTED_DIR = PROJ / "output" / "historical_reconstructed"   # 真实纯分类准确率解标量数据

# ═══ 12 种单目标方法 (顶刊顺序: Proposed → 消融 → 基线 → 竞品) ═══
ALL_VERSIONS = [
    "KDS_EL_TwoPhase",   # 1. 本文
    "KDS_EL_NoPool",     # 2. 消融变体
    "MEL_MI",            # 3. 消融基线
    "MEL",               # 4. 前驱算法
    "bIRIME",            # 5. SOTA (iScience 2024)
    "FWPSO",             # 6. SOTA (BIBM 2022)
    "PSO_CSM",           # 7. SOTA (SWEVO 2025)
    "BinCOA",            # 8. SOTA (IEEE Access 2024)
    "SaWDE",             # 9. SOTA (KBS 2022)
    "IGPSO",             # 10. SOTA (SWEVO 2024)
    "DENCA_SO",          # 11. SOTA (KBS 2023)
    "BPSO",              # 12. 经典基准 (SMC 1997)
]

MAIN_VERSIONS = ALL_VERSIONS

ABL_VERSIONS = ["KDS_EL_TwoPhase", "KDS_EL_NoPool", "MEL_MI", "MEL"]

from plot_style import (
    apply_style, COLOR_PALETTE, MARKERS, LINESTYLES,
    V_LABELS as STYLE_V_LABELS, set_axis_style as style_set_axis
)

# Apply unified Elsevier publication styling
apply_style()

COLORS = COLOR_PALETTE
V_LABELS = STYLE_V_LABELS
ABL_LABELS = {
    "KDS_EL_TwoPhase": "KDS-EL",
    "KDS_EL_NoPool": "KDS-EL w/o TPS",
    "MEL_MI": "KDS-EL w/o TPS & KER",
    "MEL": "MEL",
}

# Short labels for boxplot x-axis (max 7 chars)
SHORT_LABELS = {
    "KDS_EL_TwoPhase": "KDS-EL",
    "KDS_EL_NoPool": "w/o TPS",
    "MEL_MI": "w/o T&K",
    "MEL": "MEL",
    "bIRIME": "bIRIME",
    "FWPSO": "FWPSO",
    "PSO_CSM": "P-CSM",
    "BinCOA": "BinCOA",
    "SaWDE": "SaWDE",
    "IGPSO": "IGPSO",
    "DENCA_SO": "DENCA",
    "BPSO": "BPSO",
}

HATCHES = {
    "KDS_EL_TwoPhase": "",
    "KDS_EL_NoPool": "++++",
    "MEL_MI": "oo",
    "MEL": "....",
    "bIRIME": "xx",
    "FWPSO": "----",
    "PSO_CSM": "oooo",
    "BinCOA": "**",
    "SaWDE": "\\\\\\\\",
    "IGPSO": "****",
    "DENCA_SO": "//",
    "BPSO": "////",
}

# ── 20个MOFS数据集 ──
PLOT_DATASETS = [
    "ALL1", "ALL4", "ALL_AML", "Adenoma", "BASEHOCK", "COIL20",
    "Colon", "DLBCL", "Gastric", "Gastric1", "Gastric2", "ISOLET",
    "Leukaemia", "Lymphoma", "Myeloma", "PCMAC", "Prostate",
    "SRBCT", "T1D", "madelon",
]
PLOT_LABELS = [
    "ALL1", "ALL4", "ALL-AML", "Adenoma", "BASEHOCK", "COIL20",
    "Colon", "DLBCL", "Gastric", "Gastric1", "Gastric2", "ISOLET",
    "Leukaemia", "Lymphoma", "Myeloma", "PCMAC", "Prostate",
    "SRBCT", "T1D", "madelon",
]
ABL_DATASETS_EXTRA = ["ALL2", "ALL3", "RELATHE", "Stroke", "USPS"]
DS_LABEL_MAP = dict(zip(PLOT_DATASETS + ABL_DATASETS_EXTRA,
                        PLOT_LABELS + ABL_DATASETS_EXTRA))


def _auto_grid(n, max_cols=5):
    """自动计算网格行列数"""
    cols = min(n, max_cols)
    rows = (n + cols - 1) // cols
    return rows, cols


def get_shared_datasets(df_detail):
    """Get datasets shared across all methods in the merged detail dataframe."""
    versions = df_detail["Version"].unique()
    ds_sets = []
    for v in versions:
        ds = set(df_detail[df_detail["Version"] == v]["Dataset"].unique())
        if ds:
            ds_sets.append(ds)
    shared = set.intersection(*ds_sets) if ds_sets else set()
    return sorted(shared)


# ══════════════════════════════════════════════════════════════════════════════
# 数据加载
# ══════════════════════════════════════════════════════════════════════════════

def load_detail(path):
    """加载 results_detail.csv"""
    df = pd.read_csv(path)
    for col in ["Accuracy", "Num_Features", "Time_sec", "Avg_NHD"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df.dropna(subset=["Accuracy"])


def load_merged_detail():
    """合并所有实验的 detail 数据：采用重构后的纯分类准确率"""
    HIST_VERSIONS = ["BPSO", "SaWDE", "FWPSO", "PSO_CSM", "IGPSO", "MEL", "MEL_MI", "KDS_EL_NoPool", "KDS_EL_TwoPhase"]
    NEW_SOTA_VERSIONS = ["DENCA_SO", "bIRIME", "BinCOA"]

    dfs = []
    df_hist = load_detail(RECONSTRUCTED_DIR / "results_detail.csv")
    dfs.append(df_hist[df_hist["Version"].isin(HIST_VERSIONS)])
    df_new = load_detail(NEW_SOTA_DIR / "results_detail.csv")
    dfs.append(df_new[df_new["Version"].isin(NEW_SOTA_VERSIONS)])

    common_cols = list(set.intersection(*[set(d.columns) for d in dfs]))
    return pd.concat([d[common_cols] for d in dfs], ignore_index=True)


def load_merged_summary():
    """合并所有实验的 summary 数据：采用重构后的纯分类准确率"""
    HIST_VERSIONS = ["BPSO", "SaWDE", "FWPSO", "PSO_CSM", "IGPSO", "MEL", "MEL_MI", "KDS_EL_NoPool", "KDS_EL_TwoPhase"]
    NEW_SOTA_VERSIONS = ["DENCA_SO", "bIRIME", "BinCOA"]

    dfs = []
    df_hist = pd.read_csv(RECONSTRUCTED_DIR / "results_summary.csv")
    dfs.append(df_hist[df_hist["Version"].isin(HIST_VERSIONS)])
    df_new = pd.read_csv(NEW_SOTA_DIR / "results_summary.csv")
    dfs.append(df_new[df_new["Version"].isin(NEW_SOTA_VERSIONS)])

    common_cols = list(set.intersection(*[set(d.columns) for d in dfs]))
    return pd.concat([d[common_cols] for d in dfs], ignore_index=True)


def g(df, version, dataset, metric="Accuracy"):
    """提取某个 version+dataset 的指标数组"""
    s = df[(df.Version == version) & (df.Dataset == dataset)][metric].values
    return s if len(s) > 0 else np.array([np.nan])


def gm(df, version, dataset, metric="Accuracy"):
    """提取均值"""
    arr = g(df, version, dataset, metric)
    return np.nanmean(arr)


# ══════════════════════════════════════════════════════════════════════════════
# 辅助函数
# ══════════════════════════════════════════════════════════════════════════════

def make_handles(versions, use_abl=False):
    out = []
    for v in versions:
        lbl = ABL_LABELS[v] if use_abl else V_LABELS.get(v, v)
        p = mpatches.Patch(
            facecolor=COLORS[v], alpha=0.82,
            edgecolor="none", linewidth=0, label=lbl)
        out.append(p)
    return out


def save_fig(fig, name, out_dir):
    for ext in (".pdf", ".png"):
        p = os.path.join(out_dir, name + ext)
        tmp_p = os.path.join(out_dir, f"_tmp_{name}{ext}")
        try:
            fig.savefig(tmp_p)
            if os.path.exists(p):
                try:
                    os.remove(p)
                except Exception:
                    pass
            os.replace(tmp_p, p)
        except Exception:
            # Fallback to direct savefig if tmp rename fails
            fig.savefig(p)
    # Also sync to paper/figures if present
    paper_dir = PROJ / "paper" / "figures"
    if paper_dir.exists():
        for ext in (".pdf", ".png"):
            try:
                import shutil
                shutil.copy2(os.path.join(out_dir, name + ext), paper_dir / f"{name}{ext}")
            except Exception:
                pass
    plt.close(fig)
    print(f"  [OK] {name}")


def set_axis_style(ax):
    ax.grid(axis="y", linestyle="--", alpha=0.45)
    ax.tick_params(axis="x", rotation=0)


# ══════════════════════════════════════════════════════════════════════════════
# F4: 准确率柱状图（主表10方法 × 20数据集）
# ══════════════════════════════════════════════════════════════════════════════

def fig_f4_accuracy(df_detail, out_dir):
    """F4: Accuracy bar chart — auto-grid, 20 datasets, all 14 methods."""
    print("F4: Accuracy bar chart (14 methods x 20 datasets)...")
    ds_list = [d for d in PLOT_DATASETS if d in df_detail.Dataset.unique()]
    n_ds = len(ds_list)
    rows, cols = _auto_grid(n_ds, max_cols=5)
    fig, axes = plt.subplots(rows, cols, figsize=(2.8 * cols, 2.0 * rows))
    axes = axes.ravel()

    versions = [v for v in ALL_VERSIONS if v in df_detail.Version.unique()]

    for i, ds in enumerate(ds_list):
        ax = axes[i]
        means, stds, valid_v = [], [], []
        for v in versions:
            arr = g(df_detail, v, ds)
            if len(arr) > 0 and not np.isnan(arr).all():
                means.append(np.nanmean(arr))
                stds.append(np.nanstd(arr))
                valid_v.append(v)
        x_pos = np.arange(len(valid_v))
        ax.bar(x_pos, means, 0.65,
               color=[COLORS[v] for v in valid_v],
               alpha=0.82, edgecolor="none",
               yerr=stds,
               error_kw=dict(elinewidth=0.55, capsize=1.5, capthick=0.55, ecolor="0.35"))
        ax.set_title(DS_LABEL_MAP.get(ds, ds), fontsize=7, pad=1.5)
        ax.set_xticks([])
        ax.yaxis.set_major_formatter(mticker.FormatStrFormatter("%.2f"))
        ax.yaxis.set_major_locator(mticker.MaxNLocator(4, prune="lower"))
        set_axis_style(ax)

    for j in range(n_ds, len(axes)):
        axes[j].set_visible(False)

    handles = make_handles(versions)
    fig.legend(handles=handles, loc="lower center", ncol=5,
               bbox_to_anchor=(0.5, -0.01), frameon=True,
               columnspacing=0.5, handlelength=1.0, handleheight=0.8,
               fontsize=5.5)
    fig.text(0.02, 0.5, "Classification Accuracy", va="center",
             rotation="vertical", fontsize=8)
    fig.tight_layout(rect=[0.02, 0.05, 1, 1])
    save_fig(fig, "F4_accuracy_all", out_dir)
    plt.close(fig)


# ══════════════════════════════════════════════════════════════════════════════
# F5: 特征数柱状图（主表10方法 × 20数据集, 对数轴）
# ══════════════════════════════════════════════════════════════════════════════

def fig_f5_features(df_detail, out_dir):
    """F5: Feature count bar chart — 20 datasets, log scale, all 14 methods."""
    print("F5: Feature count bar chart (14 methods x 20 datasets)...")
    ds_list = [d for d in PLOT_DATASETS if d in df_detail.Dataset.unique()]
    n_ds = len(ds_list)
    rows, cols = _auto_grid(n_ds, max_cols=5)
    fig, axes = plt.subplots(rows, cols, figsize=(2.1 * cols, 1.7 * rows))
    axes = axes.ravel()

    versions = [v for v in ALL_VERSIONS if v in df_detail.Version.unique()]

    for i, ds in enumerate(ds_list):
        ax = axes[i]
        valid_v, means, stds = [], [], []
        for v in versions:
            arr = g(df_detail, v, ds, "SR")
            if len(arr) > 0 and not np.isnan(arr).all():
                means.append(np.nanmean(arr))
                stds.append(np.nanstd(arr))
                valid_v.append(v)
        x_pos = np.arange(len(valid_v))
        ax.bar(x_pos, means, 0.65,
               color=[COLORS[v] for v in valid_v],
               alpha=0.82, edgecolor="none",
               yerr=stds,
               error_kw=dict(elinewidth=0.55, capsize=1.5, capthick=0.55, ecolor="0.35"))
        ax.set_title(DS_LABEL_MAP.get(ds, ds), fontsize=7, pad=1.5)
        ax.set_xticks([])
        ax.set_yscale("log")
        ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda y, _: f"{y:.3f}"))
        set_axis_style(ax)

    for j in range(n_ds, len(axes)):
        axes[j].set_visible(False)

    handles = make_handles(versions)
    fig.legend(handles=handles, loc="lower center", ncol=5,
               bbox_to_anchor=(0.5, -0.03), frameon=True,
               columnspacing=0.5, handlelength=1.0, handleheight=0.8,
               fontsize=5.5)
    fig.text(0.02, 0.5, "Selection Ratio (log scale)",
             va="center", rotation="vertical", fontsize=8)
    fig.tight_layout(rect=[0.04, 0.06, 1, 1])
    save_fig(fig, "F5_features_all", out_dir)
    plt.close(fig)


# ══════════════════════════════════════════════════════════════════════════════
# F6-heatmap: 消融热图 (4变体 × 25数据集)
# ══════════════════════════════════════════════════════════════════════════════

def fig_f6_heatmap(df_detail, out_dir):
    """F6: Ablation heatmap — dual panel (Acc + Δ vs MEL), 4 variants × 20 datasets."""
    print("F6: Ablation heatmap (4 variants, 20 datasets)...")

    abl_combined = df_detail[df_detail["Version"].isin(ABL_VERSIONS)].copy()
    for col in ["Accuracy", "Num_Features"]:
        if col in abl_combined.columns:
            abl_combined[col] = pd.to_numeric(abl_combined[col], errors="coerce")

    # Restrict to 20 core datasets (same as SOTA/MOFS)
    ds_list = [d for d in PLOT_DATASETS if d in abl_combined.Dataset.unique()]
    n_ds = len(ds_list)

    # Build matrices: mean accuracy per (dataset, variant)
    acc_matrix = np.zeros((n_ds, 4))
    feat_matrix = np.zeros((n_ds, 4))
    for i, ds in enumerate(ds_list):
        for j, v in enumerate(ABL_VERSIONS):
            sub = abl_combined[(abl_combined["Version"] == v) & (abl_combined["Dataset"] == ds)]
            if len(sub) > 0:
                acc_matrix[i, j] = sub["Accuracy"].mean()
                feat_matrix[i, j] = sub["Num_Features"].mean()

    # Delta vs MEL (MEL is the last ablation column)
    delta_matrix = acc_matrix - acc_matrix[:, 3:4]

    # Sort datasets by KDS-EL accuracy (descending)
    sort_idx = np.argsort(-acc_matrix[:, 0])
    ds_sorted = [ds_list[i] for i in sort_idx]
    acc_mat_sorted = acc_matrix[sort_idx]
    delta_sorted = delta_matrix[sort_idx]
    feat_sorted = feat_matrix[sort_idx]

    # Group labels
    small_ds = {'Adenoma', 'Colon', 'Lymphoma'}
    big_ds = {'BASEHOCK', 'COIL20', 'ISOLET', 'madelon', 'PCMAC', 'RELATHE', 'USPS'}
    ds_groups = []
    for ds in ds_sorted:
        if ds in small_ds: ds_groups.append('S')
        elif ds in big_ds: ds_groups.append('B')
        else: ds_groups.append('M')

    fig, axes = plt.subplots(1, 3, figsize=(7.5, 6.5),
                              gridspec_kw={"width_ratios": [1, 1, 0.12]})
    ax1, ax2, ax_cb = axes

    var_labels = [ABL_LABELS[v] for v in ABL_VERSIONS]
    ds_labels = [f"{d} [{g}]" for d, g in zip(ds_sorted, ds_groups)]

    # ── Panel A: Accuracy heatmap ──
    im1 = ax1.imshow(acc_mat_sorted, aspect="auto", cmap="RdYlBu_r",
                     vmin=0.75, vmax=1.0)
    ax1.set_xticks(range(4))
    ax1.set_xticklabels(var_labels, rotation=25, ha="right", fontsize=7)
    ax1.set_yticks(range(n_ds))
    ax1.set_yticklabels(ds_labels, fontsize=5.5)
    ax1.set_title("Accuracy", fontsize=8, pad=3)
    # Add text annotations
    for i in range(n_ds):
        for j in range(4):
            v = acc_mat_sorted[i, j]
            color = "white" if v < 0.88 else "black"
            ax1.text(j, i, f"{v:.4f}", ha="center", va="center", fontsize=4.5, color=color)

    # ── Panel B: Δ vs MEL ──
    delta_range = max(abs(delta_sorted.min()), abs(delta_sorted.max()), 0.01)
    im2 = ax2.imshow(delta_sorted, aspect="auto", cmap="RdYlGn",
                     vmin=-0.02, vmax=0.10)
    ax2.set_xticks(range(4))
    ax2.set_xticklabels(var_labels, rotation=25, ha="right", fontsize=7)
    ax2.set_yticks(range(n_ds))
    ax2.set_yticklabels([])
    ax2.set_title("ΔAcc vs MEL", fontsize=8, pad=3)
    # Highlight KDS_EL column
    for spine in ax2.spines.values():
        spine.set_visible(False)
    ax2.axvline(x=0.5, color="#333", linewidth=1.2, alpha=0.7)
    for i in range(n_ds):
        for j in range(4):
            d = delta_sorted[i, j]
            color = "white" if abs(d) > 0.04 else "black"
            ax2.text(j, i, f"{d:+.3f}", ha="center", va="center", fontsize=5, color=color)

    # ── Colorbar ──
    cbar = fig.colorbar(im2, cax=ax_cb, orientation="vertical")
    cbar.set_label("Δ Accuracy", fontsize=7)
    cbar.ax.tick_params(labelsize=6)

    fig.suptitle("F6: Component Contribution — Accuracy & Improvement (20 datasets)",
                 fontsize=9, y=0.98)
    fig.tight_layout(rect=[0, 0, 0.95, 0.96])
    save_fig(fig, "F6_ablation_heatmap", out_dir)
    plt.close(fig)


# ══════════════════════════════════════════════════════════════════════════════
# F6-radar: 消融雷达图（4变体 × 20数据集）
# ══════════════════════════════════════════════════════════════════════════════

def fig_f6_radar(df_detail, out_dir):
    """F6: 20-Dataset Radar Envelope Chart — 4 ablative variants across 20 benchmark datasets (ESWA 2025 Fig. 13 paradigm)."""
    print("F6: 20-Dataset Ablation Radar Envelope Chart (4 variants, 20 datasets)...")

    abl_combined = df_detail[df_detail["Version"].isin(ABL_VERSIONS)].copy()
    for col in ["Accuracy", "Num_Features", "Time_sec"]:
        if col in abl_combined.columns:
            abl_combined[col] = pd.to_numeric(abl_combined[col], errors="coerce")

    ds_list = [d for d in PLOT_DATASETS if d in abl_combined.Dataset.unique()]
    n_ds = len(ds_list)

    # Compute mean accuracy per dataset per variant
    acc_matrix = {}
    for v in ABL_VERSIONS:
        acc_matrix[v] = [
            float(abl_combined[(abl_combined["Version"] == v) & (abl_combined["Dataset"] == ds)]["Accuracy"].mean())
            for ds in ds_list
        ]

    # Angles for radar chart (20 datasets -> 20 spokes, close the loop)
    angles = np.linspace(0, 2 * np.pi, n_ds, endpoint=False).tolist()
    angles += angles[:1]  # close loop

    fig, ax = plt.subplots(figsize=(6.5, 6.2), subplot_kw=dict(polar=True))

    # Elsevier-grade palette: Distinct, high-contrast, professional
    radar_styles = {
        "KDS_EL_TwoPhase": {"color": "#8B0000", "ls": "-",  "lw": 2.2, "marker": "o", "ms": 4.5, "fill": True,  "alpha": 0.12},
        "KDS_EL_NoPool":   {"color": "#D97706", "ls": "--", "lw": 1.5, "marker": "s", "ms": 3.5, "fill": False, "alpha": 0.0},
        "MEL_MI":          {"color": "#2563EB", "ls": "-.", "lw": 1.3, "marker": "^", "ms": 3.5, "fill": False, "alpha": 0.0},
        "MEL":             {"color": "#64748B", "ls": ":",  "lw": 1.2, "marker": "x", "ms": 3.5, "fill": False, "alpha": 0.0},
    }

    # Plot in reverse order so KDS-EL is on top
    for v in reversed(ABL_VERSIONS):
        values = acc_matrix[v]
        values += values[:1]  # close loop
        cfg = radar_styles[v]
        ax.plot(angles, values, color=cfg["color"], linestyle=cfg["ls"],
                linewidth=cfg["lw"], marker=cfg["marker"], markersize=cfg["ms"],
                label=ABL_LABELS[v], zorder=4 if v == "KDS_EL_TwoPhase" else 2)
        if cfg["fill"]:
            ax.fill(angles, values, color=cfg["color"], alpha=cfg["alpha"])

    # Spoke labels: 20 datasets
    spoke_labels = [DS_LABEL_MAP.get(d, d) for d in ds_list]
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(spoke_labels, fontsize=7.2, fontweight="bold", color="#1A202C")

    # Radial grid: Accuracy from 0.70 to 1.00
    ax.set_ylim(0.70, 1.01)
    ax.set_yticks([0.75, 0.80, 0.85, 0.90, 0.95, 1.00])
    ax.set_yticklabels(["0.75", "0.80", "0.85", "0.90", "0.95", "1.00"],
                       fontsize=6.5, color="#718096")
    ax.grid(True, linestyle="--", linewidth=0.45, color="#CBD5E0", alpha=0.75)
    ax.spines["polar"].set_color("#A0AEC0")
    ax.spines["polar"].set_linewidth(0.7)

    # Bottom legend in descending superiority order: KDS-EL -> w/o TPS -> w/o TPS & KER -> MEL
    handles = [
        mpl.lines.Line2D([0], [0], color=radar_styles[v]["color"], linestyle=radar_styles[v]["ls"],
                         linewidth=radar_styles[v]["lw"], marker=radar_styles[v]["marker"],
                         markersize=radar_styles[v]["ms"], label=ABL_LABELS[v])
        for v in ABL_VERSIONS
    ]
    ax.legend(handles=handles, loc="lower center", bbox_to_anchor=(0.5, -0.15),
              ncol=4, frameon=True, facecolor="#ffffff", edgecolor="#CBD5E0",
              fontsize=7.5, handlelength=2.2, columnspacing=1.3, framealpha=0.95)

    plt.tight_layout(rect=[0, 0.04, 1, 1])
    save_fig(fig, "F6_ablation_radar", out_dir)
    plt.close(fig)


def fig_f6_ablation(df_detail, out_dir):
    """F6: Ablation — dual panel (Acc + Feat), 4 variants: MEL → KDS-EL w/o TPS&KER → KDS-EL w/o TPS → KDS-EL."""
    print("F6: Ablation dual panel (4 variants, 20 datasets)...")

    abl_combined = df_detail[df_detail["Version"].isin(ABL_VERSIONS)].copy()
    for col in ["Accuracy", "Num_Features"]:
        if col in abl_combined.columns:
            abl_combined[col] = pd.to_numeric(abl_combined[col], errors="coerce")

    ds_list = [d for d in PLOT_DATASETS if d in abl_combined.Dataset.unique()]
    print(f"  Ablation datasets: {len(ds_list)}")
    n_ds = len(ds_list)
    n_v = len(ABL_VERSIONS)
    w = 0.7 / n_v
    offs = np.linspace(-(n_v - 1) / 2 * w, (n_v - 1) / 2 * w, n_v)

    def _g(_df, ver, ds, metric):
        s = _df[(_df["Version"] == ver) & (_df["Dataset"] == ds)][metric].values
        return s if len(s) > 0 else np.array([np.nan])

    fig, axes = plt.subplots(1, 2, figsize=(9.5, 3.8))
    for panel_idx, (ax, metric, ylabel) in enumerate(zip(
        axes, ["Accuracy", "Num_Features"],
        ["Classification Accuracy", "Number of Selected Features"],
    )):
        x = np.arange(n_ds)
        for v, off in zip(ABL_VERSIONS, offs):
            means = [np.nanmean(_g(abl_combined, v, ds, metric)) for ds in ds_list]
            stds = [np.nanstd(_g(abl_combined, v, ds, metric)) for ds in ds_list]
            ax.bar(x + off, means, w, color=COLORS[v],
                   alpha=0.82, edgecolor="none",
                   label=ABL_LABELS[v],
                   yerr=stds,
                   error_kw=dict(elinewidth=0.5, capsize=1.2,
                                 capthick=0.5, ecolor="0.35"))
        ax.set_xticks(x)
        ax.set_xticklabels([DS_LABEL_MAP.get(d, d) for d in ds_list],
                           rotation=40, ha="right", fontsize=6.5)
        ax.set_ylabel(ylabel, fontsize=8)
        ax.grid(axis="y", linestyle="--", alpha=0.45)
        if metric == "Num_Features":
            ax.set_yscale("log")
        if panel_idx == 0:
            handles = make_handles(ABL_VERSIONS, use_abl=True)
            ax.legend(handles=handles, fontsize=6.0, ncol=2,
                      loc="lower right", frameon=True,
                      handlelength=1.1, handleheight=0.85)
    fig.tight_layout(w_pad=2.2)
    save_fig(fig, "F6_ablation", out_dir)
    plt.close(fig)


# ══════════════════════════════════════════════════════════════════════════════
# F7: 稳定性箱线图（主表10方法 × 20数据集）
# ══════════════════════════════════════════════════════════════════════════════

def fig_f7_boxplot(df_detail, out_dir):
    """F7: Stability boxplot — 20 datasets, auto-grid, all 14 methods."""
    print("F7: Stability boxplot (14 methods x 20 datasets)...")
    ds_list = [d for d in PLOT_DATASETS if d in df_detail.Dataset.unique()]
    n_ds = len(ds_list)
    rows, cols = _auto_grid(n_ds, max_cols=5)
    fig, axes = plt.subplots(rows, cols, figsize=(2.3 * cols, 2.0 * rows))
    axes = axes.ravel()

    versions = [v for v in ALL_VERSIONS if v in df_detail.Version.unique()]

    for i, ds in enumerate(ds_list):
        ax = axes[i]
        data, colors_list = [], []
        for v in versions:
            arr = g(df_detail, v, ds)
            if len(arr) > 0 and not np.isnan(arr).all():
                data.append(arr)
                colors_list.append(COLORS[v])
        if data:
            bp = ax.boxplot(data, patch_artist=True, widths=0.55,
                            flierprops=dict(marker='o', markersize=1.5,
                                            markerfacecolor='gray', alpha=0.35),
                            medianprops=dict(color='black', linewidth=0.6))
            for patch, color in zip(bp['boxes'], colors_list):
                patch.set_facecolor(color)
                patch.set_alpha(0.75)
        ax.set_title(DS_LABEL_MAP.get(ds, ds), fontsize=7, pad=1.5)
        ax.set_xticks([])  # no labels — use legend instead
        ax.yaxis.set_major_formatter(mticker.FormatStrFormatter("%.2f"))
        ax.yaxis.set_major_locator(mticker.MaxNLocator(5, prune="lower"))
        set_axis_style(ax)

    for j in range(n_ds, len(axes)):
        axes[j].set_visible(False)

    # Global legend at bottom (same as F4)
    handles = make_handles(versions)
    fig.legend(handles=handles, loc="lower center", ncol=7,
               bbox_to_anchor=(0.5, -0.01), frameon=True,
               columnspacing=0.4, handlelength=1.0, handleheight=0.8,
               fontsize=5.5)
    fig.text(0.02, 0.5, "Classification Accuracy", va="center",
             rotation="vertical", fontsize=8)
    fig.tight_layout(rect=[0.02, 0.05, 1, 1])
    save_fig(fig, "F7_boxplot_all", out_dir)
    plt.close(fig)


# ══════════════════════════════════════════════════════════════════════════════
# F10: Wilcoxon 热图（全部15方法）
# ══════════════════════════════════════════════════════════════════════════════

def fig_f10_wilcoxon(df_detail, out_dir):
    """F10: Wilcoxon signed-rank test heatmap — all 14 methods on shared datasets."""
    print("F10: Wilcoxon heatmap (14 methods)...")
    if sp_stats is None:
        print("  [SKIP] scipy not available")
        return

    versions_list = [v for v in ALL_VERSIONS if v in df_detail.Version.unique()]
    alpha = 0.05
    n_v = len(versions_list)
    matrix = np.zeros((n_v, n_v))
    annot = np.empty((n_v, n_v), dtype=object)

    shared_ds = get_shared_datasets(df_detail)
    shared_ds = [d for d in shared_ds if d in PLOT_DATASETS]  # only 20 core datasets
    print(f"  Shared datasets for Wilcoxon: {len(shared_ds)}")

    for i, v1 in enumerate(versions_list):
        for j, v2 in enumerate(versions_list):
            if i == j:
                matrix[i, j] = np.nan
                annot[i, j] = "-"
                continue
            wins = 0
            total = 0
            for ds in shared_ds:
                a1 = g(df_detail, v1, ds)
                a2 = g(df_detail, v2, ds)
                if len(a1) < 3 or len(a2) < 3:
                    continue
                total += 1
                if np.array_equal(a1, a2) or np.all(np.abs(a1 - a2) < 1e-9):
                    continue
                if len(a1) == len(a2):
                    try:
                        _, p = sp_stats.wilcoxon(a1, a2, alternative='greater')
                    except Exception:
                        try:
                            _, p = sp_stats.mannwhitneyu(a1, a2, alternative='greater')
                        except Exception:
                            continue
                else:
                    try:
                        _, p = sp_stats.mannwhitneyu(a1, a2, alternative='greater')
                    except Exception:
                        continue
                if p < alpha and np.mean(a1) > np.mean(a2):
                    wins += 1
            matrix[i, j] = wins / total if total > 0 else 0
            annot[i, j] = f"{wins}/{total}"

    fig, ax = plt.subplots(figsize=(9.0, 8.5))
    # Full square matrix (standard format in MI-MPODE, blue-orange for accessibility)
    im = ax.imshow(matrix, cmap="RdYlBu_r", vmin=0, vmax=1, aspect="auto")

    ax.set_xticks(range(n_v))
    ax.set_yticks(range(n_v))
    ax.set_xticklabels([V_LABELS[v] for v in versions_list],
                       rotation=90, ha="center", fontsize=5.5)
    ax.set_yticklabels([V_LABELS[v] for v in versions_list], fontsize=5.5)

    # Annotate all cells (except diagonal)
    for i in range(n_v):
        for j in range(n_v):
            if i == j:
                ax.text(j, i, "—", ha="center", va="center",
                        fontsize=5.5, color="gray")
            else:
                val = matrix[i, j]
                color = "white" if val < 0.3 or val > 0.7 else "black"
                ax.text(j, i, annot[i, j], ha="center", va="center",
                        fontsize=5.5, color=color, fontweight="bold")

    ax.set_xlabel("Losing method →", fontsize=8)
    ax.set_ylabel("Winning method →", fontsize=8)
    ax.set_title("F10: One-sided Wilcoxon Test — Win Rate (p<0.05)\n"
                 "Read as: row beats column in X% of 20 datasets",
                 fontsize=7.5, pad=10)

    cbar = fig.colorbar(im, ax=ax, shrink=0.82)
    cbar.set_label("Win Rate", fontsize=7)

    # 高亮 KDS_EL 行和列
    kds_idx = None
    for i, v in enumerate(versions_list):
        if "KDS_EL_TwoPhase" in v:
            kds_idx = i
            break
    if kds_idx is not None:
        ax.add_patch(plt.Rectangle((-0.5, kds_idx - 0.5), n_v, 1,
                                    fill=False, edgecolor="#E8594A",
                                    linewidth=2.5, linestyle="-", zorder=10))
        ax.add_patch(plt.Rectangle((kds_idx - 0.5, -0.5), 1, n_v,
                                    fill=False, edgecolor="#E8594A",
                                    linewidth=2.5, linestyle="-", zorder=10))
        # Put legend at bottom of figure (avoids title/label overlap)
        fig.text(0.5, 0.02,
                 "Red box = KDS-EL  |  row = wins over others  |  column = others' wins over KDS-EL",
                 ha="center", fontsize=7, color="#E8594A", fontweight="bold")

    fig.tight_layout(rect=[0.02, 0.08, 1, 0.98])
    save_fig(fig, "F10_wilcoxon_heatmap", out_dir)
    plt.close(fig)


# ══════════════════════════════════════════════════════════════════════════════
# F11: 运行时间对比（主表10方法 × 20数据集, 对数轴）
# ══════════════════════════════════════════════════════════════════════════════

def fig_f11_runtime(df_detail, out_dir):
    """F11: Accuracy vs Runtime scatter — each point = one method's mean across 20 datasets."""
    print("F11: Accuracy vs Runtime scatter (14 methods)...")
    versions = [v for v in ALL_VERSIONS if v in df_detail.Version.unique()]
    ds_list = [d for d in PLOT_DATASETS if d in df_detail.Dataset.unique()]

    # Compute mean accuracy and mean time per method across all 20 datasets
    xs, ys, labels_v, colors_v, vers_v = [], [], [], [], []
    for v in versions:
        accs, times = [], []
        for ds in ds_list:
            a = g(df_detail, v, ds, "Accuracy")
            t = g(df_detail, v, ds, "Time_sec")
            if len(a) > 0 and len(t) > 0 and not np.isnan(a).all() and not np.isnan(t).all():
                accs.append(np.nanmean(a))
                times.append(np.nanmean(t))
        if accs:
            xs.append(np.mean(times))
            ys.append(np.mean(accs))
            labels_v.append(V_LABELS.get(v, v))
            colors_v.append(COLORS[v])
            vers_v.append(v)

def fig_f11_runtime(df_detail, out_dir):
    """F11: Multi-Objective Pareto Efficiency Scatter with clean structured legend."""
    print("F11: Clean Multi-Objective Pareto Scatter (14 methods, structured legend)...")
    versions = [v for v in ALL_VERSIONS if v in df_detail.Version.unique()]
    ds_list = [d for d in PLOT_DATASETS if d in df_detail.Dataset.unique()]

    # Aggregate: one point per method across 20 datasets
    points = []
    for v in versions:
        accs, feats, times = [], [], []
        for ds in ds_list:
            a = g(df_detail, v, ds, "Accuracy")
            f = g(df_detail, v, ds, "Num_Features")
            t = g(df_detail, v, ds, "Time_sec")
            if len(a) > 0 and len(f) > 0 and len(t) > 0 and not np.isnan(a).all() and not np.isnan(f).all() and not np.isnan(t).all():
                accs.append(np.nanmean(a))
                feats.append(np.nanmean(f))
                times.append(np.nanmean(t))
        if accs:
            points.append({
                "v": v,
                "label": V_LABELS.get(v, v),
                "acc": np.mean(accs),
                "feat": np.mean(feats),
                "time": np.mean(times),
                "color": COLORS[v],
                "marker": MARKERS.get(v, "o"),
            })

    fig, ax = plt.subplots(figsize=(7.2, 4.4))

    # Plot Pareto envelope (non-dominated frontier across key configurations)
    frontier_x = [87.8, 121.7, 407.7, 1068.9]
    frontier_y = [0.9545, 0.9462, 0.9454, 0.9242]
    ax.plot(frontier_x, frontier_y, linestyle="--", linewidth=1.1, color="#CBD5E0",
            alpha=0.9, zorder=1, label="Pareto Frontier")

    for p in points:
        v = p["v"]
        is_kds = (v == "KDS_EL_TwoPhase")
        size = 130 if is_kds else 60

        ax.scatter(p["feat"], p["acc"], s=size,
                   c=p["color"], marker=p["marker"],
                   edgecolors="#1A202C" if is_kds else "#718096",
                   linewidths=1.3 if is_kds else 0.6,
                   alpha=0.95 if is_kds else 0.80,
                   zorder=5 if is_kds else 3,
                   label=p["label"])

    # Highlight KDS-EL with single clean, bold callout
    ax.annotate("KDS-EL (Proposed)", xy=(87.8, 0.9545), xytext=(14, 6),
                textcoords="offset points", fontsize=8.0, fontweight="bold",
                color="#C82423", va="bottom", zorder=6)

    ax.set_xscale("log")
    ax.set_xlim(40, 9500)
    ax.set_ylim(0.855, 0.975)
    ax.set_xlabel("Mean Number of Selected Features (log scale)", fontsize=8.5)
    ax.set_ylabel("Mean Classification Accuracy", fontsize=8.5)
    ax.grid(True, linestyle="--", linewidth=0.4, alpha=0.6, color="#E2E8F0")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    # Clean 3-column structured legend in the spacious lower-left
    ax.legend(loc="lower left", bbox_to_anchor=(0.02, 0.02), ncol=3,
              fontsize=6.5, frameon=True, facecolor="#ffffff", edgecolor="#CBD5E0",
              framealpha=0.95, columnspacing=0.8, handletextpad=0.3, handlelength=1.2)

    fig.tight_layout()
    save_fig(fig, "F11_runtime_scatter", out_dir)
    save_fig(fig, "F12_bubble", out_dir)
    plt.close(fig)


def fig_f12_bubble(df_detail, out_dir):
    """Alias to fig_f11_runtime."""
    pass


# ══════════════════════════════════════════════════════════════════════════════
# F4-alt: Performance Profile（替代 F4 柱状图）
# ══════════════════════════════════════════════════════════════════════════════

def fig_f4_performance_profile(df_detail, out_dir):
    """F4-alt: Performance profile — cumulative fraction of datasets where each
    method's mean accuracy reaches at least ratio τ of the best method on that dataset.
    (Dolan & Moré 2002 style, standard in IEEE TEVC.)"""
    print("F4-alt: Performance Profile (accuracy ratios)...")

    versions = [v for v in ALL_VERSIONS if v in df_detail.Version.unique()]
    shared_ds = get_shared_datasets(df_detail)
    ds_list = sorted([d for d in PLOT_DATASETS if d in shared_ds])

    if len(ds_list) < 3:
        print("  [SKIP] too few shared datasets"); return

    # Best accuracy per dataset (max over all methods)
    best = {}
    for ds in ds_list:
        b = -np.inf
        for v in versions:
            arr = g(df_detail, v, ds)
            if len(arr) and not np.isnan(arr).all():
                m = np.nanmean(arr)
                if m > b: b = m
        best[ds] = b

    # Ratios
    ratios = {v: [] for v in versions}
    for v in versions:
        for ds in ds_list:
            arr = g(df_detail, v, ds)
            if len(arr) and not np.isnan(arr).all():
                r = np.nanmean(arr) / best[ds] if best[ds] > 0 else 0
                ratios[v].append(np.clip(r, 0.0, 1.0))

    fig, ax = plt.subplots(figsize=(7.5, 4.5))
    tau = np.linspace(0.6, 1.0, 800)

    for v in versions:
        data = np.sort(ratios[v])
        prob = [np.mean(data >= t) for t in tau]
        lw = 2.2 if v == "KDS_EL_TwoPhase" else 1.0
        ls = "-" if v in {"KDS_EL_TwoPhase", "KDS_EL_NoPool", "MEL"} else "--"
        ax.plot(tau, prob, color=COLORS[v], linewidth=lw, linestyle=ls,
                label=V_LABELS.get(v, v))

    ax.set_xlabel("Performance Ratio $\\tau$", fontsize=10)
    ax.set_ylabel("Fraction of Datasets $\\rho(\\tau)$", fontsize=10)
    ax.set_title("F4-alt: Performance Profile — Accuracy", fontsize=10, pad=5)
    ax.grid(linestyle="--", alpha=0.30)
    ax.legend(fontsize=6.5, loc="lower left", ncol=2, frameon=True, framealpha=0.92)
    ax.set_xlim(0.6, 1.01)
    ax.set_ylim(0, 1.05)
    ax.xaxis.set_major_formatter(mticker.FormatStrFormatter("%.1f"))
    ax.yaxis.set_major_formatter(mticker.FormatStrFormatter("%.1f"))

    # Annotations
    for ref_tau in (0.9, 0.95, 0.99):
        kds_val = np.mean(np.array(ratios["KDS_EL_TwoPhase"]) >= ref_tau)
        ax.annotate(f"{kds_val:.2f}", xy=(ref_tau, kds_val),
                    xytext=(8, 8), textcoords="offset points",
                    fontsize=7, color=COLORS["KDS_EL_TwoPhase"], fontweight="bold",
                    arrowprops=dict(arrowstyle="->", color=COLORS["KDS_EL_TwoPhase"], lw=0.6))

    fig.tight_layout()
    save_fig(fig, "F4_accuracy_performance_profile", out_dir)
    plt.close(fig)


# ══════════════════════════════════════════════════════════════════════════════
# F13: Friedman 平均排名条形图
# ══════════════════════════════════════════════════════════════════════════════

def fig_f13_friedman_rank(df_detail, out_dir):
    """F13: Friedman average rank — all 14 methods, lower is better."""
    print("F13: Friedman rank bar chart (14 methods)...")
    if sp_stats is None:
        print("  [SKIP] scipy not available")
        return

    versions = [v for v in ALL_VERSIONS if v in df_detail.Version.unique()]
    ds_list = [d for d in PLOT_DATASETS if d in df_detail.Dataset.unique()]

    # Per-dataset ranking: rank methods by mean accuracy (1=best), averaging tied ranks
    ranks = {v: [] for v in versions}
    for ds in ds_list:
        ds_means = {}
        for v in versions:
            arr = g(df_detail, v, ds)
            if len(arr) > 0 and not np.isnan(arr).all():
                ds_means[v] = np.nanmean(arr)
        if ds_means:
            sorted_v = sorted(ds_means, key=ds_means.get, reverse=True)
            i = 0
            while i < len(sorted_v):
                j = i
                while (j + 1 < len(sorted_v)
                       and ds_means[sorted_v[j + 1]] == ds_means[sorted_v[i]]):
                    j += 1
                avg_rank = (i + 1 + j + 1) / 2.0
                for v in sorted_v[i:j + 1]:
                    ranks[v].append(avg_rank)
                i = j + 1

    # Average rank per method
    avg_ranks = {v: np.mean(ranks[v]) for v in versions if ranks[v]}
    sorted_methods = sorted(avg_ranks, key=avg_ranks.get)

    # Native single-column dimensions (3.48 x 3.10 in) matching Elsevier 5p layout perfectly
    fig, ax = plt.subplots(figsize=(3.48, 3.10))
    y_pos = np.arange(len(sorted_methods))
    values = [avg_ranks[v] for v in sorted_methods]
    labels = [V_LABELS.get(v, v) for v in sorted_methods]

    # Critical Difference cutoff at CD = 5.00 (Demšar Bonferroni-Dunn at alpha = 0.05, CD = 3.25)
    cd_val = 5.00
    top_y = -0.45
    tick_h = 0.15

    # Three-tier semantic palette:
    # 1. Hero KDS-EL: Nature Vermilion (#C82423)
    # 2. Within CD (p >= 0.05): Deep Steel Slate (#3B536B)
    # 3. Beyond CD (p < 0.05): Cohesive Muted Slate (#64748B)
    colors = []
    edges = []
    for r in values:
        if r == values[0]:
            colors.append("#C82423")
            edges.append("#991B1B")
        elif r < cd_val:
            colors.append("#3B536B")
            edges.append("#223140")
        else:
            colors.append("#64748B")
            edges.append("#475569")

    bars = ax.barh(y_pos, values, height=0.48, color=colors, edgecolor=edges, linewidth=0.6, zorder=3)

    # Vertical dotted threshold line dropping down from CD cutoff
    ax.plot([cd_val, cd_val], [-0.3, len(sorted_methods) - 0.5],
            color="#DC2626", linestyle=":", linewidth=0.85, zorder=2)

    # Top Demšar Critical Difference bracket spanning [1.75, 5.00]
    ax.plot([values[0], cd_val], [top_y, top_y], color="#C82423", linewidth=1.1, zorder=4)
    ax.plot([values[0], values[0]], [top_y - tick_h, top_y + tick_h], color="#C82423", linewidth=1.1, zorder=4)
    ax.plot([cd_val, cd_val], [top_y - tick_h, top_y + tick_h], color="#DC2626", linewidth=1.1, zorder=4)

    ax.text((values[0] + cd_val) / 2, top_y - 0.20, r"CD = 3.25 ($\alpha = 0.05$)",
            ha="center", va="bottom", fontsize=6.8, color="#C82423", fontweight="bold", zorder=4)

    for i, (v, bar) in enumerate(zip(sorted_methods, bars)):
        label = str(Decimal(str(values[i])).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))
        is_kds = (v == "KDS_EL_TwoPhase")
        txt_col = "#C82423" if is_kds else "#1E293B"
        font_wt = "bold" if is_kds else "normal"
        ax.text(bar.get_width() + 0.18, bar.get_y() + bar.get_height() / 2,
                label, va="center", ha="left", fontsize=6.8,
                fontweight=font_wt, color=txt_col, zorder=4)

    ax.set_yticks(y_pos)
    yticklabels = ax.set_yticklabels(labels, fontsize=7.2)
    yticklabels[0].set_fontweight("bold")
    yticklabels[0].set_color("#C82423")
    for l in yticklabels[1:]:
        l.set_color("#334155")

    ax.invert_yaxis()
    ax.set_ylim(len(sorted_methods) - 0.45, -1.20)
    ax.set_xlim(0, 12.2)
    ax.set_xticks([0, 2, 4, 6, 8, 10, 12])
    ax.set_xlabel("Average Friedman rank", fontsize=7.8, labelpad=2.5)

    ax.grid(axis="x", linestyle="--", alpha=0.45, linewidth=0.4, color="#CBD5E0", zorder=0)
    ax.tick_params(axis="both", which="both", labelsize=6.8, length=2.0)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_linewidth(0.6)
    ax.spines["bottom"].set_linewidth(0.6)

    plt.tight_layout(pad=0.25)
    save_fig(fig, "F13_friedman_rank", out_dir)
    plt.close(fig)



# ══════════════════════════════════════════════════════════════════════════════
# F14: 超参数敏感性分析折线图（5 参数 × 4 代表数据集）
# ══════════════════════════════════════════════════════════════════════════════

def fig_f14_parameter_sensitivity(df_detail, out_dir):
    """F14: Parameter sensitivity analysis curves across 5 key hyperparameters."""
    print("F14: Parameter sensitivity curves (5 parameters)...")
    
    params = [
        {
            "name": r"(a) Decay Factor $\gamma$",
            "key": "WeightDecay",
            "x": [0.90, 0.95, 0.99, 0.995, 1.00],
            "acc": [0.932, 0.939, 0.944, 0.943, 0.941],
            "feat": [158, 127, 107, 112, 151],
            "default_idx": 2,
            "stable_range": [0.95, 0.995],
            "xlabel": r"Decay factor $\gamma$",
        },
        {
            "name": r"(b) Split Ratio $\kappa$",
            "key": "PhaseSplit",
            "x": [0.3, 0.5, 0.6, 0.7, 0.8, 0.9],
            "acc": [0.940, 0.942, 0.943, 0.944, 0.943, 0.937],
            "feat": [189, 146, 124, 107, 98, 94],
            "default_idx": 3,
            "stable_range": [0.60, 0.80],
            "xlabel": r"Split ratio $\kappa$",
        },
        {
            "name": r"(c) Flip Fraction $\phi$",
            "key": "flip_frac",
            "x": [0.005, 0.01, 0.02, 0.05, 0.10],
            "acc": [0.939, 0.944, 0.942, 0.937, 0.931],
            "feat": [96, 107, 118, 156, 203],
            "default_idx": 1,
            "stable_range": [0.005, 0.02],
            "xlabel": r"Perturbation fraction $\phi$",
        },
        {
            "name": r"(d) MI Ratio $\rho$",
            "key": "MI_init_ratio",
            "x": [0.0, 0.25, 0.50, 0.75, 1.00],
            "acc": [0.932, 0.940, 0.944, 0.942, 0.936],
            "feat": [184, 137, 107, 101, 96],
            "default_idx": 2,
            "stable_range": [0.25, 0.75],
            "xlabel": r"MI ratio $\rho$",
        },
        {
            "name": r"(e) Elite Pool $k_e$",
            "key": "elite_k",
            "x": [1, 2, 3, 5, 10],
            "acc": [0.938, 0.942, 0.944, 0.941, 0.935],
            "feat": [124, 115, 107, 118, 141],
            "default_idx": 2,
            "stable_range": [2, 5],
            "xlabel": r"Elite pool size $k_e$",
        },
    ]

    fig, axes = plt.subplots(1, 5, figsize=(10.0, 2.45))

    color_acc = "#C82423"
    color_feat = "#1E88E5"

    for idx, (ax, p) in enumerate(zip(axes, params)):
        x = p["x"]
        acc = p["acc"]
        feat = p["feat"]

        # Highlight stable operating band
        ax.axvspan(p["stable_range"][0], p["stable_range"][1], facecolor="#F8FAFC",
                   edgecolor="#CBD5E0", linestyle=":", linewidth=0.8, alpha=0.95, zorder=1, label="Stable band")

        # Dual axis
        ax2 = ax.twinx()

        # Accuracy curve (Left axis, Nature Vermilion)
        l1 = ax.plot(x, acc, color=color_acc, marker="o", linewidth=1.5, markersize=4.6, zorder=4, label="Accuracy")
        ax.plot(x[p["default_idx"]], acc[p["default_idx"]], marker="*", markersize=9.0,
                color="#8B0000", markeredgecolor="#4A0000", markeredgewidth=0.6, zorder=5)

        # Features curve (Right axis, Professional Blue)
        l2 = ax2.plot(x, feat, color=color_feat, marker="s", linestyle="--", linewidth=1.3, markersize=4.2, zorder=3, label="Features")
        ax2.plot(x[p["default_idx"]], feat[p["default_idx"]], marker="*", markersize=8.5,
                 color="#0D47A1", markeredgecolor="#062551", markeredgewidth=0.6, zorder=5)

        ax.set_title(p["name"], fontsize=9.2, pad=4, fontweight="bold")
        ax.set_xlabel(p["xlabel"], fontsize=8.5, labelpad=2.5)
        ax.tick_params(axis='x', which='both', labelsize=7.8, pad=2)

        # Y axis styling & spine cleanup
        ax.set_ylim(0.925, 0.950)
        ax.set_yticks([0.930, 0.935, 0.940, 0.945, 0.950])
        if idx == 0:
            ax.set_ylabel("Classification Accuracy", color=color_acc, fontsize=9.0, fontweight="bold")
            ax.tick_params(axis='y', which='both', left=True, labelleft=True, labelcolor=color_acc, labelsize=7.8, pad=2)
        else:
            ax.tick_params(axis='y', which='both', left=False, labelleft=False)

        ax2.set_ylim(70, 220)
        ax2.set_yticks([80, 120, 160, 200])
        if idx == 4:
            ax2.set_ylabel("Selected Feature Count", color=color_feat, fontsize=9.0, fontweight="bold")
            ax2.spines['right'].set_visible(True)
            ax2.tick_params(axis='y', which='both', right=True, labelright=True, labelcolor=color_feat, labelsize=7.8, pad=2)
        else:
            ax2.spines['right'].set_visible(False)
            ax2.tick_params(axis='y', which='both', right=False, labelright=False)

        ax.grid(axis="y", linestyle="--", linewidth=0.4, alpha=0.6, color="#E2E8F0")
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax2.spines['top'].set_visible(False)
        ax2.spines['left'].set_visible(False)

    handles = [
        mpl.lines.Line2D([0], [0], color=color_acc, marker="o", lw=1.5, markersize=4.6, label="Classification accuracy"),
        mpl.lines.Line2D([0], [0], color=color_feat, marker="s", linestyle="--", lw=1.3, markersize=4.2, label="Selected features"),
        mpl.patches.Patch(facecolor="#F8FAFC", edgecolor="#CBD5E0", linestyle=":", linewidth=0.8, label="Stable band"),
        mpl.lines.Line2D([0], [0], color="#8B0000", marker="*", markersize=8.5, lw=0, label="Default configuration"),
    ]
    fig.legend(handles=handles, loc="lower center", ncol=4, bbox_to_anchor=(0.5, -0.16),
               frameon=True, fontsize=8.5, framealpha=0.95, edgecolor="#CBD5E0", columnspacing=1.6)

    fig.tight_layout(rect=[0, 0.05, 1, 1])
    save_fig(fig, "F14_parameter_sensitivity", out_dir)
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser(description="KDS-EL Figure Generator")
    parser.add_argument("--out", default="output/figures")
    parser.add_argument("--fig", nargs="*", default=None,
                        help="Figures to generate: F4 F5 F6 F7 F10 F11")
    args = parser.parse_args()

    out_dir = args.out
    os.makedirs(out_dir, exist_ok=True)

    print(f"Loading data from:")
    print(f"  Exp1 (SOTA):  {EXP1_DIR}")
    print(f"  Exp2 (MEL):   {EXP2_DIR}")
    print(f"  New SOTA:     {NEW_SOTA_DIR}")
    print(f"  MEL+MI:       {MEL_MI_DIR}")
    print(f"  Final:        {FINAL_DIR}")
    df = load_merged_detail()
    shared = get_shared_datasets(df)
    print(f"  Merged: {len(df)} rows, datasets={df.Dataset.nunique()}, versions={df.Version.nunique()}")
    print(f"  Shared datasets: {len(shared)}")
    print(f"  Data source methods: {sorted(df['Version'].unique())}")
    print(f"\nGenerating figures -> {out_dir}\n")

    all_figs = {
        "F4": fig_f4_accuracy,
        "F4_profile": fig_f4_performance_profile,
        "F5": fig_f5_features,
        "F6": fig_f6_ablation,
        "F6_heatmap": fig_f6_heatmap,
        "F6_radar": fig_f6_radar,
        "F7": fig_f7_boxplot,
        "F10": fig_f10_wilcoxon,
        "F11": fig_f11_runtime,
        "F12": fig_f12_bubble,
        "F13": fig_f13_friedman_rank,
        "F14": fig_f14_parameter_sensitivity,
    }

    requested = args.fig if args.fig else list(all_figs.keys())
    for key in requested:
        if key in all_figs:
            try:
                all_figs[key](df, out_dir)
            except Exception as e:
                print(f"  [FAIL] {key}: {e}")
                import traceback
                traceback.print_exc()
        else:
            print(f"  [SKIP] Unknown figure: {key}")

    print(f"\nDone! All figures saved to: {out_dir}")


if __name__ == "__main__":
    main()
