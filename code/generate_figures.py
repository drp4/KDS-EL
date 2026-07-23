"""
KDS-EL 图表生成脚本
===================
根据《图表规划.md》生成 F4-F7, F10-F12（共7张图）。
数据来源：四个正式实验目录的 results_detail.csv。

用法：
    python generate_figures.py
    python generate_figures.py --out figures/ --fig F4
"""
import os, sys, argparse
import numpy as np
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.ticker as mticker
from pathlib import Path

try:
    from scipy import stats as sp_stats
except ImportError:
    sp_stats = None

# ══════════════════════════════════════════════════════════════════════════════
# 路径 & 配置
# ══════════════════════════════════════════════════════════════════════════════

PROJ = Path(__file__).resolve().parent.parent
EXP1_DIR = PROJ / "output" / "formal_experiment_20260701_094943"   # SOTA 对比 (5方法)
EXP2_DIR = PROJ / "output" / "formal_experiment_20260628_205157"   # 旧消融 V1 (仅 MEL 有效)
EXP3_DIR = PROJ / "output" / "formal_experiment_20260702_145828"   # 最新消融 V2 (KDS-EL 三变体)
EXP4_DIR = PROJ / "output" / "formal_experiment_20260707_142018"   # MOFS 对比 (6方法)
MEL_MI_DIR = PROJ / "output" / "formal_experiment_mel_mi"            # MEL_MI 对照

# ── 全部15个方法（用于 F10 热图、附录等）──
ALL_VERSIONS = [
    "BPSO", "SaWDE", "FWPSO", "MEL", "MEL_MI",
    "KDS_EL_DRS", "KDS_EL_KER", "KDS_EL",
    "PSO_CSM", "IGPSO",
    "NSGA-II-FS", "MOPSO-FS", "MOEA-D-FS",
    "fMOPSO-FS", "VGS-MOEA", "W-MOPSO-FS",
]

# ── 主表10方法（用于 F4/F5/F7/F11/F12）──
MAIN_VERSIONS = [
    "KDS_EL", "KDS_EL_KER", "KDS_EL_DRS", "MEL",
    "FWPSO", "PSO_CSM", "SaWDE",
    "VGS-MOEA", "W-MOPSO-FS", "NSGA-II-FS",
]

ABL_VERSIONS = ["MEL", "MEL_MI", "KDS_EL_DRS", "KDS_EL_KER", "KDS_EL"]

V_LABELS = {
    "BPSO": "BPSO", "SaWDE": "SaWDE", "FWPSO": "FWPSO",
    "MEL": "MEL", "MEL_MI": "MEL+MI",
    "KDS_EL_DRS": "KDS-EL/DRS",
    "KDS_EL_KER": "KDS-EL/KER", "KDS_EL": "KDS-EL",
    "PSO_CSM": "PSO-CSM", "IGPSO": "IGPSO",
    "NSGA-II-FS": "NSGA-II-FS", "MOPSO-FS": "MOPSO-FS",
    "MOEA-D-FS": "MOEA-D-FS", "fMOPSO-FS": "fMOPSO-FS",
    "VGS-MOEA": "VGS-MOEA", "W-MOPSO-FS": "W-MOPSO-FS",
}
ABL_LABELS = {
    "MEL": "MEL (Baseline)", "MEL_MI": "MEL+MI (w/ reinit)",
    "KDS_EL_DRS": "KDS-EL/DRS",
    "KDS_EL_KER": "KDS-EL/KER", "KDS_EL": "KDS-EL (Proposed)",
}

COLORS = {
    # === KDS-EL family — Coral/Red (the ONE standout hue) ===
    "KDS_EL":     "#E8594A",  # Proposed — brightest coral
    "KDS_EL_KER": "#F09080",  # light coral
    "KDS_EL_DRS": "#D0685C",  # deep coral

    # === MEL baselines — Steel Blue ===
    "MEL":        "#6A94B2",  # MEL baseline
    "MEL_MI":     "#8BB3CC",  # MEL+MI (lighter)

    # === SOTA — Blue-Gray gradient (wide L spread) ===
    "FWPSO":      "#5D7E99",  # darkest blue-gray
    "IGPSO":      "#6C8BA3",  # dark blue-gray
    "PSO_CSM":    "#7F99AE",  # medium blue-gray
    "SaWDE":      "#94AABD",  # medium-light blue-gray
    "BPSO":       "#AABBC8",  # lightest blue-gray

    # === MOFS — Cool Gray gradient (wide L spread) ===
    "VGS-MOEA":   "#6B7B85",  # darkest cool gray
    "NSGA-II-FS": "#7E8D96",  # dark cool gray
    "W-MOPSO-FS": "#8F9DA4",  # medium-dark cool gray
    "fMOPSO-FS":  "#9FABB2",  # medium cool gray
    "MOEA-D-FS":  "#AEB8BD",  # medium-light cool gray
    "MOPSO-FS":   "#BCC4C8",  # lightest cool gray
}
HATCHES = {
    "BPSO": "////", "SaWDE": "\\\\\\\\", "FWPSO": "----",
    "MEL": "....", "MEL_MI": "oo",
    "KDS_EL_DRS": "xxxx", "KDS_EL_KER": "++++",
    "KDS_EL": "", "PSO_CSM": "oooo", "IGPSO": "****",
    "NSGA-II-FS": "///", "MOPSO-FS": "\\\\\\",
    "MOEA-D-FS": "---", "fMOPSO-FS": "+++",
    "VGS-MOEA": "xx", "W-MOPSO-FS": "oo",
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


# matplotlib 全局样式
mpl.rcParams.update({
    "font.family": "DejaVu Serif", "font.size": 8,
    "axes.titlesize": 8, "axes.labelsize": 8,
    "xtick.labelsize": 7, "ytick.labelsize": 7,
    "legend.fontsize": 6.0, "legend.framealpha": 0.92,
    "legend.edgecolor": "0.6", "legend.borderpad": 0.3,
    "axes.linewidth": 0.7, "grid.linewidth": 0.35,
    "lines.linewidth": 0.9, "patch.linewidth": 0.45,
    "xtick.major.width": 0.7, "ytick.major.width": 0.7,
    "xtick.major.size": 2.5, "ytick.major.size": 2.5,
    "axes.spines.top": False, "axes.spines.right": False,
    "figure.dpi": 300, "savefig.dpi": 300,
    "savefig.bbox": "tight", "savefig.pad_inches": 0.03,
})


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
    """合并四个实验的 detail 数据：各方法从各自有效来源加载"""
    SOTA_VERSIONS = ["BPSO", "SaWDE", "FWPSO", "PSO_CSM", "IGPSO"]
    KDS_VERSIONS = ["KDS_EL", "KDS_EL_DRS", "KDS_EL_KER"]
    MOFS_VERSIONS = ["NSGA-II-FS", "MOPSO-FS", "MOEA-D-FS",
                     "fMOPSO-FS", "VGS-MOEA", "W-MOPSO-FS"]

    dfs = []

    # Exp1: SOTA 方法
    df1 = load_detail(EXP1_DIR / "results_detail.csv")
    dfs.append(df1[df1["Version"].isin(SOTA_VERSIONS)])

    # Exp2: 仅 MEL 有效
    df2 = load_detail(EXP2_DIR / "results_detail.csv")
    dfs.append(df2[df2["Version"] == "MEL"])

    # Exp3: KDS-EL 三变体（已修复所有 bug）
    df3 = load_detail(EXP3_DIR / "results_detail.csv")
    dfs.append(df3[df3["Version"].isin(KDS_VERSIONS)])

    # Exp4: MOFS 方法
    df4 = load_detail(EXP4_DIR / "results_detail.csv")
    dfs.append(df4[df4["Version"].isin(MOFS_VERSIONS)])

    # MEL_MI: MI+Reinit 对照
    df_mel_mi = load_detail(MEL_MI_DIR / "results_detail.csv")
    dfs.append(df_mel_mi[df_mel_mi["Version"] == "MEL_MI"])

    # 取共有列并合并
    common_cols = None
    for d in dfs:
        if common_cols is None:
            common_cols = set(d.columns)
        else:
            common_cols &= set(d.columns)
    common_cols = list(common_cols) if common_cols else []
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
        fig.savefig(p)
    print(f"  [OK] {name}")


def set_axis_style(ax):
    ax.grid(axis="y", linestyle="--", alpha=0.45)
    ax.tick_params(axis="x", rotation=0)


# ══════════════════════════════════════════════════════════════════════════════
# F4: 准确率柱状图（主表10方法 × 20数据集）
# ══════════════════════════════════════════════════════════════════════════════

def fig_f4_accuracy(df_detail, out_dir):
    """F4: Accuracy bar chart — auto-grid, 20 datasets, 10 main methods."""
    print("F4: Accuracy bar chart (10 methods × 20 datasets)...")
    ds_list = [d for d in PLOT_DATASETS if d in df_detail.Dataset.unique()]
    n_ds = len(ds_list)
    rows, cols = _auto_grid(n_ds, max_cols=5)
    fig, axes = plt.subplots(rows, cols, figsize=(2.1 * cols, 1.7 * rows))
    axes = axes.ravel()

    versions = [v for v in MAIN_VERSIONS if v in df_detail.Version.unique()]

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
    """F5: Feature count bar chart — 20 datasets, log scale, 10 main methods."""
    print("F5: Feature count bar chart (10 methods × 20 datasets)...")
    ds_list = [d for d in PLOT_DATASETS if d in df_detail.Dataset.unique()]
    n_ds = len(ds_list)
    rows, cols = _auto_grid(n_ds, max_cols=5)
    fig, axes = plt.subplots(rows, cols, figsize=(2.1 * cols, 1.7 * rows))
    axes = axes.ravel()

    versions = [v for v in MAIN_VERSIONS if v in df_detail.Version.unique()]

    for i, ds in enumerate(ds_list):
        ax = axes[i]
        valid_v, means, stds = [], [], []
        for v in versions:
            arr = g(df_detail, v, ds, "Num_Features")
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
        ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda y, _: f"{int(y):,}"))
        set_axis_style(ax)

    for j in range(n_ds, len(axes)):
        axes[j].set_visible(False)

    handles = make_handles(versions)
    fig.legend(handles=handles, loc="lower center", ncol=5,
               bbox_to_anchor=(0.5, -0.03), frameon=True,
               columnspacing=0.5, handlelength=1.0, handleheight=0.8,
               fontsize=5.5)
    fig.text(0.02, 0.5, "Number of Selected Features (log scale)",
             va="center", rotation="vertical", fontsize=8)
    fig.tight_layout(rect=[0.04, 0.06, 1, 1])
    save_fig(fig, "F5_features_all", out_dir)
    plt.close(fig)


# ══════════════════════════════════════════════════════════════════════════════
# F6: 消融实验双面板（5变体 × 25数据集, CNS排除）
# ══════════════════════════════════════════════════════════════════════════════

def fig_f6_ablation(df_detail, out_dir):
    """F6: Ablation study — dual panel (Accuracy + Features), 5 variants × 25 datasets (CNS excluded)."""
    print("F6: Ablation dual panel (5-layer: MEL → MEL_MI → DRS → KER → Full)...")
    fig, axes = plt.subplots(1, 2, figsize=(9.5, 3.8))
    # Compute shared datasets across all 5 ablation variants
    abl_shared = get_shared_datasets(df_detail)
    # Filter to only ABL_VERSIONS
    abl_v_in_data = [v for v in ABL_VERSIONS if v in df_detail.Version.unique()]
    ds_sets = []
    for v in abl_v_in_data:
        ds = set(df_detail[df_detail.Version == v]["Dataset"].unique())
        if ds:
            ds_sets.append(ds)
    ds_list = sorted(set.intersection(*ds_sets)) if ds_sets else []
    # Exclude CNS if present
    ds_list = [d for d in ds_list if d != "CNS"]
    print(f"  Ablation datasets: {len(ds_list)}")
    n_ds = len(ds_list)
    n_v = len(ABL_VERSIONS)
    w = 0.7 / n_v
    offs = np.linspace(-(n_v - 1) / 2 * w, (n_v - 1) / 2 * w, n_v)

    for panel_idx, (ax, metric, ylabel) in enumerate(zip(
        axes, ["Accuracy", "Num_Features"],
        ["Classification Accuracy", "Number of Selected Features"],
    )):
        x = np.arange(n_ds)
        for v, off in zip(ABL_VERSIONS, offs):
            means = [gm(df_detail, v, ds, metric) for ds in ds_list]
            stds = [np.nanstd(g(df_detail, v, ds, metric)) for ds in ds_list]
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
            ax.legend(handles=handles, fontsize=6.0, ncol=3,
                      loc="lower right", frameon=True,
                      handlelength=1.1, handleheight=0.85)
    fig.tight_layout(w_pad=2.2)
    save_fig(fig, "F6_ablation", out_dir)
    plt.close(fig)


# ══════════════════════════════════════════════════════════════════════════════
# F7: 稳定性箱线图（主表10方法 × 20数据集）
# ══════════════════════════════════════════════════════════════════════════════

def fig_f7_boxplot(df_detail, out_dir):
    """F7: Stability boxplot — 20 datasets, auto-grid, 10 main methods."""
    print("F7: Stability boxplot (10 methods × 20 datasets)...")
    ds_list = [d for d in PLOT_DATASETS if d in df_detail.Dataset.unique()]
    n_ds = len(ds_list)
    rows, cols = _auto_grid(n_ds, max_cols=5)
    fig, axes = plt.subplots(rows, cols, figsize=(2.1 * cols, 1.7 * rows))
    axes = axes.ravel()

    versions = [v for v in MAIN_VERSIONS if v in df_detail.Version.unique()]

    for i, ds in enumerate(ds_list):
        ax = axes[i]
        data, labels, colors_list = [], [], []
        for v in versions:
            arr = g(df_detail, v, ds)
            if len(arr) > 0 and not np.isnan(arr).all():
                data.append(arr)
                labels.append(V_LABELS.get(v, v))
                colors_list.append(COLORS[v])
        if data:
            bp = ax.boxplot(data, tick_labels=labels, patch_artist=True,
                            widths=0.55,
                            flierprops=dict(marker='o', markersize=2.0,
                                            markerfacecolor='gray', alpha=0.4),
                            medianprops=dict(color='black', linewidth=0.7))
            for patch, color in zip(bp['boxes'], colors_list):
                patch.set_facecolor(color)
                patch.set_alpha(0.75)
        ax.set_title(DS_LABEL_MAP.get(ds, ds), fontsize=7, pad=1.5)
        ax.set_xticklabels(labels, rotation=60, ha="right", fontsize=5.0)
        ax.yaxis.set_major_formatter(mticker.FormatStrFormatter("%.2f"))
        ax.yaxis.set_major_locator(mticker.MaxNLocator(5, prune="lower"))
        set_axis_style(ax)

    for j in range(n_ds, len(axes)):
        axes[j].set_visible(False)

    fig.text(0.02, 0.5, "Classification Accuracy", va="center",
             rotation="vertical", fontsize=8)
    fig.tight_layout(rect=[0.04, 0.02, 1, 1])
    save_fig(fig, "F7_boxplot_all", out_dir)
    plt.close(fig)


# ══════════════════════════════════════════════════════════════════════════════
# F10: Wilcoxon 热图（全部15方法）
# ══════════════════════════════════════════════════════════════════════════════

def fig_f10_wilcoxon(df_detail, out_dir):
    """F10: Wilcoxon signed-rank test heatmap — all 15 methods on shared datasets."""
    print("F10: Wilcoxon heatmap (15 methods)...")
    if sp_stats is None:
        print("  [SKIP] scipy not available")
        return

    versions_list = [v for v in ALL_VERSIONS if v in df_detail.Version.unique()]
    alpha = 0.05
    n_v = len(versions_list)
    matrix = np.zeros((n_v, n_v))
    annot = np.empty((n_v, n_v), dtype=object)

    shared_ds = get_shared_datasets(df_detail)
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
                if len(a1) == len(a2):
                    try:
                        _, p = sp_stats.wilcoxon(a1, a2)
                    except Exception:
                        try:
                            _, p = sp_stats.mannwhitneyu(a1, a2, alternative='two-sided')
                        except Exception:
                            continue
                else:
                    try:
                        _, p = sp_stats.mannwhitneyu(a1, a2, alternative='two-sided')
                    except Exception:
                        continue
                total += 1
                if p < alpha and np.mean(a1) > np.mean(a2):
                    wins += 1
            matrix[i, j] = wins / total if total > 0 else 0
            annot[i, j] = f"{wins}/{total}"

    fig, ax = plt.subplots(figsize=(9.0, 7.5))
    im = ax.imshow(matrix, cmap="RdYlGn", vmin=0, vmax=1, aspect="auto")

    ax.set_xticks(range(n_v))
    ax.set_yticks(range(n_v))
    ax.set_xticklabels([V_LABELS[v] for v in versions_list],
                       rotation=45, ha="right", fontsize=6.5)
    ax.set_yticklabels([V_LABELS[v] for v in versions_list], fontsize=6.5)

    for i in range(n_v):
        for j in range(n_v):
            if i != j:
                val = matrix[i, j]
                color = "white" if (0.3 < val < 0.7) else "black"
                ax.text(j, i, annot[i, j], ha="center", va="center",
                        fontsize=5.5, color=color, fontweight="bold")

    ax.set_xlabel("Versus → (row beats column)", fontsize=8)
    ax.set_ylabel("Method", fontsize=8)
    ax.set_title("F10: Wilcoxon Test — Win Rate (significant, p<0.05)", fontsize=8, pad=5)

    cbar = fig.colorbar(im, ax=ax, shrink=0.82)
    cbar.set_label("Win Rate", fontsize=7)

    # 高亮 KDS_EL 行
    if "KDS_EL" in versions_list:
        ki = versions_list.index("KDS_EL")
        ax.add_patch(plt.Rectangle((-0.5, ki - 0.5), n_v, 1,
                                    fill=False, edgecolor="red",
                                    linewidth=2, linestyle="-"))
        ax.text(n_v / 2, ki - 0.65, "KDS-EL (Proposed)", ha="center",
                fontsize=7, color="red", fontweight="bold")

    fig.tight_layout()
    save_fig(fig, "F10_wilcoxon_heatmap", out_dir)
    plt.close(fig)


# ══════════════════════════════════════════════════════════════════════════════
# F11: 运行时间对比（主表10方法 × 20数据集, 对数轴）
# ══════════════════════════════════════════════════════════════════════════════

def fig_f11_runtime(df_detail, out_dir):
    """F11: Runtime comparison — 20 datasets, 10 main methods, log scale."""
    print("F11: Runtime comparison (10 methods × 20 datasets)...")
    ds_list = [d for d in PLOT_DATASETS if d in df_detail.Dataset.unique()]
    n_ds = len(ds_list)
    versions = [v for v in MAIN_VERSIONS if v in df_detail.Version.unique()]
    n_v = len(versions)
    w = 0.7 / n_v
    offs = np.linspace(-(n_v - 1) / 2 * w, (n_v - 1) / 2 * w, n_v)

    fig, ax = plt.subplots(figsize=(9.0, 4.0))
    x = np.arange(n_ds)

    for v, off in zip(versions, offs):
        means = [gm(df_detail, v, ds, "Time_sec") for ds in ds_list]
        ax.bar(x + off, means, w, color=COLORS[v],
               alpha=0.82, edgecolor="none",
               label=V_LABELS.get(v, v))

    ax.set_xticks(x)
    ax.set_xticklabels([DS_LABEL_MAP.get(d, d) for d in ds_list],
                       rotation=40, ha="right", fontsize=6.5)
    ax.set_ylabel("Average Runtime (seconds, log scale)", fontsize=8)
    ax.set_yscale("log")
    ax.grid(axis="y", linestyle="--", alpha=0.45, which="both")
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda y, _: f"{y:.0f}"))

    handles = make_handles(versions)
    ax.legend(handles=handles, loc="upper left", ncol=5,
              fontsize=5.5, frameon=True,
              columnspacing=0.5, handlelength=1.0, handleheight=0.8)
    fig.tight_layout()
    save_fig(fig, "F11_runtime", out_dir)
    plt.close(fig)


# ══════════════════════════════════════════════════════════════════════════════
# F12: 精度-特征-时间气泡图（主表10方法）
# ══════════════════════════════════════════════════════════════════════════════

def fig_f12_bubble(df_detail, out_dir):
    """F12: Accuracy-Feature-Time bubble chart — 3D tradeoff, 10 main methods."""
    print("F12: Accuracy-Features-Time bubble chart (10 methods)...")
    fig, ax = plt.subplots(figsize=(7.5, 5.5))

    versions = [v for v in MAIN_VERSIONS if v in df_detail.Version.unique()]
    shared_ds = get_shared_datasets(df_detail)

    for v in versions:
        xs, ys, sizes = [], [], []
        for ds in shared_ds:
            acc = gm(df_detail, v, ds, "Accuracy")
            feat = gm(df_detail, v, ds, "Num_Features")
            t = gm(df_detail, v, ds, "Time_sec")
            if not np.isnan(acc) and not np.isnan(feat) and not np.isnan(t):
                xs.append(feat)
                ys.append(acc)
                sizes.append(max(15, np.log1p(t) * 30))

        if xs:
            is_kds = (v == "KDS_EL")
            ax.scatter(xs, ys, s=sizes, c=COLORS[v],
                       label=V_LABELS.get(v, v),
                       alpha=0.85,
                       edgecolors="#333333", linewidth=0.8 if is_kds else 0.5,
                       zorder=3 if is_kds else 1)

        # 高亮 KDS_EL
        if v == "KDS_EL" and xs and shared_ds:
            for xi, yi, ds in zip(xs, ys, shared_ds):
                if yi > 0.85:
                    ax.annotate(ds, (xi, yi), fontsize=5.5, alpha=0.8,
                                textcoords="offset points", xytext=(4, 4))

    ax.set_xlabel("Number of Selected Features (log scale)", fontsize=8)
    ax.set_ylabel("Classification Accuracy", fontsize=8)
    ax.set_title("F12: Accuracy-Features-Time Tradeoff (bubble size = log time)",
                 fontsize=8, pad=4)
    ax.set_xscale("log")
    ax.grid(linestyle="--", alpha=0.4)
    ax.legend(fontsize=5.5, loc="lower right", ncol=2,
              frameon=True, handlelength=1.0)

    ax.annotate("Ideal Region\n(High Acc, Few Feat)",
                xy=(50, 0.97), fontsize=7, color="green",
                bbox=dict(boxstyle="round,pad=0.3", facecolor="lightgreen", alpha=0.3),
                ha="center")

    fig.tight_layout()
    save_fig(fig, "F12_bubble", out_dir)
    plt.close(fig)


# ══════════════════════════════════════════════════════════════════════════════
# F4-alt: Performance Profile（替代 F4 柱状图）
# ══════════════════════════════════════════════════════════════════════════════

def fig_f4_performance_profile(df_detail, out_dir):
    """F4-alt: Performance profile — cumulative fraction of datasets where each
    method's mean accuracy reaches at least ratio τ of the best method on that dataset.
    (Dolan & Moré 2002 style, standard in IEEE TEVC.)"""
    print("F4-alt: Performance Profile (accuracy ratios)...")

    versions = [v for v in MAIN_VERSIONS if v in df_detail.Version.unique()]
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
        lw = 2.2 if v == "KDS_EL" else 1.0
        ls = "-" if v in {"KDS_EL", "KDS_EL_KER", "KDS_EL_DRS", "MEL"} else "--"
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
        kds_val = np.mean(np.array(ratios["KDS_EL"]) >= ref_tau)
        ax.annotate(f"{kds_val:.2f}", xy=(ref_tau, kds_val),
                    xytext=(8, 8), textcoords="offset points",
                    fontsize=7, color=COLORS["KDS_EL"], fontweight="bold",
                    arrowprops=dict(arrowstyle="->", color=COLORS["KDS_EL"], lw=0.6))

    fig.tight_layout()
    save_fig(fig, "F4_accuracy_performance_profile", out_dir)
    plt.close(fig)


# ══════════════════════════════════════════════════════════════════════════════
# F6-alt: Waterfall / Delta 贡献图（替代 F6 分组柱状图）
# ══════════════════════════════════════════════════════════════════════════════

def fig_f6_delta_waterfall(df_detail, out_dir):
    """F6-alt: Two-panel waterfall showing incremental component contributions.
    Left: cumulative waterfall — MEL baseline → +MI → +DRS → +KER → Full.
    Right: per-dataset delta (each variant vs MEL), showing consistency."""
    print("F6-alt: Waterfall — ablation component contributions...")

    abl_v = [v for v in ABL_VERSIONS if v in df_detail.Version.unique()]
    if len(abl_v) < 3:
        print("  [SKIP] too few ablation variants"); return

    # Shared datasets (exclude CNS)
    ds_sets = [set(df_detail[df_detail.Version == v]["Dataset"].unique()) for v in abl_v]
    ds_sets = [s for s in ds_sets if s]
    ds_list = sorted(set.intersection(*ds_sets)) if ds_sets else []
    ds_list = [d for d in ds_list if d != "CNS"]

    if len(ds_list) < 2:
        print("  [SKIP] too few shared datasets"); return

    # Per-variant × per-dataset means
    pds = {}  # pds[variant][dataset] = mean_acc
    for v in abl_v:
        pds[v] = {}
        for ds in ds_list:
            arr = g(df_detail, v, ds)
            if len(arr) and not np.isnan(arr).all():
                pds[v][ds] = np.nanmean(arr)

    # Across-dataset mean per variant
    means = [np.mean(list(pds[v].values())) for v in abl_v]

    # Deltas from previous variant: MEL (baseline), MEL_MI-MEL, DRS-MEL_MI, KER-DRS, Full-KER
    deltas = [means[0]] + [means[i] - means[i-1] for i in range(1, len(means))]

    # ── figure ──
    fig, axes = plt.subplots(1, 2, figsize=(10.5, 4.2),
                             gridspec_kw={"width_ratios": [1.1, 1]})
    # ────── Left: Waterfall ──────
    ax1 = axes[0]
    n = len(abl_v)
    x = np.arange(n)

    # Bar bottoms & heights
    bottoms = [0.0] + means[:-1]          # [0, m0, m1, m2, m3]
    heights = [means[0]] + deltas[1:]     # [m0, d1, d2, d3, d4]

    bar_colors = [COLORS[v] for v in abl_v]
    bars = ax1.bar(x, heights, bottom=bottoms, width=0.55,
                   color=bar_colors, alpha=0.82, edgecolor="none")

    # Connecting lines
    cum = means[0]
    for i in range(1, n):
        ax1.plot([i - 0.275, i + 0.275], [cum, cum],
                 color="gray", linewidth=0.6, alpha=0.5)
        cum += deltas[i]

    # Labels inside / on top of bars
    for i in range(n):
        if i == 0:
            ax1.text(0, means[0] / 2, f"{means[0]:.3f}",
                     ha="center", va="center", fontsize=8, fontweight="bold",
                     color="white" if means[0] > 0.3 else "black")
        else:
            delta = deltas[i]
            mid = bottoms[i] + delta / 2
            sign = "+" if delta >= 0 else ""
            clr = "#2a6b2a" if delta >= 0 else "#cc3333"
            ax1.text(i, mid, f"{sign}{delta:.4f}",
                     ha="center", va="center", fontsize=7.5, fontweight="bold", color=clr)

    ax1.set_xticks(x)
    ax1.set_xticklabels(["MEL\n(Baseline)", "MEL\n+MI", "+DRS", "+KER",
                         "KDS-EL\n(Full)"], fontsize=7, ha="center")
    ax1.set_ylabel("Mean Classification Accuracy", fontsize=9)
    ax1.set_title("Cumulative Ablation Contribution", fontsize=9, pad=5)
    ax1.grid(axis="y", linestyle="--", alpha=0.35)
    ax1.yaxis.set_major_formatter(mticker.FormatStrFormatter("%.3f"))
    ax1.yaxis.set_major_locator(mticker.MaxNLocator(6, prune="lower"))

    # Final value callout
    ax1.annotate(f"KDS-EL\n{means[-1]:.4f}", xy=(n-1, means[-1]),
                 xytext=(n-1 + 0.35, means[-1] + 0.01),
                 fontsize=7.5, color=COLORS["KDS_EL"], fontweight="bold",
                 ha="left",
                 arrowprops=dict(arrowstyle="->", color=COLORS["KDS_EL"], lw=0.7))

    # ────── Right: Per-dataset delta strip ──────
    ax2 = axes[1]
    mel_vals = pds["MEL"]

    for vi, v in enumerate(abl_v[1:], start=1):
        ds_deltas = []
        for ds in ds_list:
            if ds in pds[v] and ds in mel_vals:
                ds_deltas.append(pds[v][ds] - mel_vals[ds])
        jitter = np.random.default_rng(42).uniform(-0.15, 0.15, len(ds_deltas))
        ax2.scatter(ds_deltas, vi + jitter, s=14, color=COLORS[v],
                    alpha=0.55, edgecolors="none", zorder=2)
        # Mean delta marker
        mean_d = np.mean(ds_deltas)
        ax2.scatter(mean_d, vi, s=60, color=COLORS[v], edgecolors="#222",
                    linewidth=0.8, zorder=3, marker="D")
        ax2.text(mean_d, vi + 0.3, f"{mean_d:+.4f}",
                 ha="center", fontsize=6.5, color=COLORS[v], fontweight="bold")

    ax2.axvline(0, color="gray", linewidth=0.7, linestyle="--", alpha=0.5)
    ax2.set_yticks(range(1, len(abl_v)))
    ax2.set_yticklabels(["+MI", "+DRS", "+KER", "Full"][:len(abl_v)-1], fontsize=7.5)
    ax2.set_xlabel("Δ Accuracy vs MEL Baseline", fontsize=9)
    ax2.set_title("Per-Dataset Improvement Consistency", fontsize=9, pad=5)
    ax2.grid(axis="x", linestyle="--", alpha=0.3)
    ax2.xaxis.set_major_formatter(mticker.FormatStrFormatter("%+.3f"))

    fig.suptitle("F6-alt: Ablation Component Contribution (Waterfall + Δ Strip)", fontsize=10, y=1.01)
    fig.tight_layout()
    save_fig(fig, "F6_ablation_delta_waterfall", out_dir)
    plt.close(fig)


# ══════════════════════════════════════════════════════════════════════════════
# Main
# ══════════════════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(description="KDS-EL Figure Generator")
    parser.add_argument("--out", default=None,
                        help="Output directory (default: output/figures/)")
    parser.add_argument("--fig", nargs="*", default=None,
                        help="Specific figures to generate (F4 F5 F6 F7 F10 F11 F12)")
    args = parser.parse_args()

    out_dir = args.out or str(PROJ / "output" / "figures")
    os.makedirs(out_dir, exist_ok=True)

    print(f"Loading data from:")
    print(f"  Exp1 (SOTA):  {EXP1_DIR}")
    print(f"  Exp2 (MEL):   {EXP2_DIR}")
    print(f"  Exp3 (KDS-EL): {EXP3_DIR}")
    print(f"  Exp4 (MOFS):  {EXP4_DIR}")
    df = load_merged_detail()
    shared = get_shared_datasets(df)
    print(f"  Merged: {len(df)} rows, datasets={df.Dataset.nunique()}, versions={df.Version.nunique()}")
    print(f"  Shared datasets: {len(shared)}")
    print(f"  Data source methods: {sorted(df['Version'].unique())}")
    print(f"\nGenerating figures → {out_dir}\n")

    all_figs = {
        "F4": fig_f4_accuracy,
        "F4_profile": fig_f4_performance_profile,
        "F5": fig_f5_features,
        "F6": fig_f6_ablation,
        "F6_delta": fig_f6_delta_waterfall,
        "F7": fig_f7_boxplot,
        "F10": fig_f10_wilcoxon,
        "F11": fig_f11_runtime,
        "F12": fig_f12_bubble,
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
