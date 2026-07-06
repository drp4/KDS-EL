"""
KDS-EL 图表生成脚本
===================
根据《图表规划.md》生成 F4-F7, F10-F12（共7张图）。
数据来源：两个正式实验目录的 results_detail.csv + results_summary.csv。

用法：
    python generate_figures.py
    python generate_figures.py --out figures/
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
EXP1_DIR = PROJ / "output" / "formal_experiment_20260701_094943"   # SOTA 对比 (5算法)
EXP2_DIR = PROJ / "output" / "formal_experiment_20260628_205157"   # 旧消融 V1 (仅 MEL 有效)
EXP3_DIR = PROJ / "output" / "formal_experiment_20260702_145828"   # 最新消融 V2 (KDS-EL 三变体)

# ── 所有9个算法（统一顺序） ──
ALL_VERSIONS = [
    "BPSO", "SaWDE", "FWPSO", "MEL",
    "KDS_EL_DRS", "KDS_EL_KER", "KDS_EL",
    "PSO_CSM", "IGPSO",
]
ABL_VERSIONS = ["MEL", "KDS_EL_DRS", "KDS_EL_KER", "KDS_EL"]

V_LABELS = {
    "BPSO": "BPSO", "SaWDE": "SaWDE", "FWPSO": "FWPSO",
    "MEL": "MEL", "KDS_EL_DRS": "KDS-EL/DRS",
    "KDS_EL_KER": "KDS-EL/KER", "KDS_EL": "KDS-EL",
    "PSO_CSM": "PSO-CSM", "IGPSO": "IGPSO",
}
ABL_LABELS = {
    "MEL": "MEL (Baseline)", "KDS_EL_DRS": "KDS-EL/DRS",
    "KDS_EL_KER": "KDS-EL/KER", "KDS_EL": "KDS-EL (Proposed)",
}

COLORS = {
    "BPSO": "#9e9e9e", "SaWDE": "#bdbdbd", "FWPSO": "#1565c0",
    "MEL": "#00838f", "KDS_EL_DRS": "#2e7d32",
    "KDS_EL_KER": "#f57f17", "KDS_EL": "#b71c1c",
    "PSO_CSM": "#6a1b9a", "IGPSO": "#e65100",
}
HATCHES = {
    "BPSO": "////", "SaWDE": "\\\\\\\\", "FWPSO": "----",
    "MEL": "....", "KDS_EL_DRS": "xxxx", "KDS_EL_KER": "++++",
    "KDS_EL": "", "PSO_CSM": "oooo", "IGPSO": "****",
}

# ── 图表数据集（取代表性的14个，对标 config.DATASETS） ──
PLOT_DATASETS = [
    "Adenoma", "ALL_AML", "ALL4", "ISOLET",
    "Colon", "DLBCL", "Leukaemia", "Lymphoma",
    "SRBCT", "Gastric", "Prostate", "BASEHOCK",
]
PLOT_LABELS = [
    "Adenoma", "ALL-AML", "ALL4", "ISOLET",
    "Colon", "DLBCL", "Leukaemia", "Lymphoma",
    "SRBCT", "Gastric", "Prostate", "BASEHOCK",
]

DS_LABEL_MAP = dict(zip(PLOT_DATASETS, PLOT_LABELS))

def _auto_grid(n, max_cols=5):
    """自动计算网格行列数"""
    cols = min(n, max_cols)
    rows = (n + cols - 1) // cols
    return rows, cols

# 共享数据集（9 方法全部有数据的 17 个）
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
    "legend.fontsize": 6.5, "legend.framealpha": 0.92,
    "legend.edgecolor": "0.6", "legend.borderpad": 0.4,
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
    """合并三个实验的 detail 数据：各方法从各自有效来源加载"""
    SOTA_VERSIONS = ["BPSO", "SaWDE", "FWPSO", "PSO_CSM", "IGPSO"]
    KDS_VERSIONS = ["KDS_EL", "KDS_EL_DRS", "KDS_EL_KER"]

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

    # 取共有列并合并
    common_cols = None
    for d in dfs:
        if common_cols is None:
            common_cols = set(d.columns)
        else:
            common_cols &= set(d.columns)
    common_cols = list(common_cols) if common_cols else []
    return pd.concat([d[common_cols] for d in dfs], ignore_index=True)


def load_merged_summary():
    """合并三个实验的 summary 数据：各方法从各自有效来源加载"""
    SOTA_VERSIONS = ["BPSO", "SaWDE", "FWPSO", "PSO_CSM", "IGPSO"]
    KDS_VERSIONS = ["KDS_EL", "KDS_EL_DRS", "KDS_EL_KER"]

    dfs = []
    df1 = pd.read_csv(EXP1_DIR / "results_summary.csv")
    dfs.append(df1[df1["Version"].isin(SOTA_VERSIONS)])
    df2 = pd.read_csv(EXP2_DIR / "results_summary.csv")
    dfs.append(df2[df2["Version"] == "MEL"])
    df3 = pd.read_csv(EXP3_DIR / "results_summary.csv")
    dfs.append(df3[df3["Version"].isin(KDS_VERSIONS)])

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
            facecolor=COLORS[v], hatch=HATCHES[v],
            edgecolor="k" if HATCHES[v] else COLORS[v],
            linewidth=0.4, label=lbl)
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
# F4: 准确率柱状图（全部 17 个共享数据集）
# ══════════════════════════════════════════════════════════════════════════════

def fig_f4_accuracy(df_detail, out_dir):
    """F4: Accuracy bar chart — auto-grid, 17 shared datasets, 9 algorithms."""
    print("F4: Accuracy bar chart (17 datasets)...")
    ds_list = get_shared_datasets(df_detail)
    n_ds = len(ds_list)
    rows, cols = _auto_grid(n_ds, max_cols=5)
    fig, axes = plt.subplots(rows, cols, figsize=(2.1 * cols, 1.7 * rows))
    axes = axes.ravel()

    for i, ds in enumerate(ds_list):
        ax = axes[i]
        n_v = len(ALL_VERSIONS)
        x = np.arange(n_v)
        means = []
        stds = []
        valid_v = []
        for v in ALL_VERSIONS:
            arr = g(df_detail, v, ds)
            if len(arr) > 0 and not np.isnan(arr).all():
                means.append(np.nanmean(arr))
                stds.append(np.nanstd(arr))
                valid_v.append(v)
        x_pos = np.arange(len(valid_v))
        ax.bar(x_pos, means, 0.65,
               color=[COLORS[v] for v in valid_v],
               edgecolor="k", linewidth=0.4,
               yerr=stds,
               error_kw=dict(elinewidth=0.55, capsize=1.5, capthick=0.55, ecolor="0.35"))
        for bar, v in zip(ax.patches, valid_v):
            if HATCHES[v]:
                bar.set_hatch(HATCHES[v])
        ax.set_title(ds, fontsize=7, pad=1.5)
        ax.set_xticks([])
        ax.yaxis.set_major_formatter(mticker.FormatStrFormatter("%.2f"))
        ax.yaxis.set_major_locator(mticker.MaxNLocator(4, prune="lower"))
        set_axis_style(ax)

    for j in range(n_ds, len(axes)):
        axes[j].set_visible(False)

    handles = make_handles(ALL_VERSIONS)
    fig.legend(handles=handles, loc="lower center", ncol=5,
               bbox_to_anchor=(0.5, -0.01), frameon=True,
               columnspacing=0.6, handlelength=1.1, handleheight=0.85,
               fontsize=6.5)
    fig.text(0.02, 0.5, "Classification Accuracy", va="center",
             rotation="vertical", fontsize=8)
    fig.tight_layout(rect=[0.02, 0.04, 1, 1])
    save_fig(fig, "F4_accuracy_all", out_dir)
    plt.close(fig)


# ══════════════════════════════════════════════════════════════════════════════
# F5: 特征数柱状图（全部 17 个共享数据集, 对数轴）
# ══════════════════════════════════════════════════════════════════════════════

def fig_f5_features(df_detail, out_dir):
    """F5: Feature count bar chart — 17 shared datasets, log scale."""
    print("F5: Feature count bar chart (17 datasets, log)...")
    ds_list = get_shared_datasets(df_detail)
    n_ds = len(ds_list)
    rows, cols = _auto_grid(n_ds, max_cols=5)
    fig, axes = plt.subplots(rows, cols, figsize=(2.1 * cols, 1.7 * rows))
    axes = axes.ravel()

    for i, ds in enumerate(ds_list):
        ax = axes[i]
        valid_v = []
        means = []
        stds = []
        for v in ALL_VERSIONS:
            arr = g(df_detail, v, ds, "Num_Features")
            if len(arr) > 0 and not np.isnan(arr).all():
                means.append(np.nanmean(arr))
                stds.append(np.nanstd(arr))
                valid_v.append(v)
        x_pos = np.arange(len(valid_v))
        ax.bar(x_pos, means, 0.65,
               color=[COLORS[v] for v in valid_v],
               edgecolor="k", linewidth=0.4,
               yerr=stds,
               error_kw=dict(elinewidth=0.55, capsize=1.5, capthick=0.55, ecolor="0.35"))
        for bar, v in zip(ax.patches, valid_v):
            if HATCHES[v]:
                bar.set_hatch(HATCHES[v])
        ax.set_title(DS_LABEL_MAP.get(ds, ds), fontsize=8, pad=2)
        ax.set_xticks([])
        ax.set_yscale("log")
        ax.yaxis.set_major_formatter(
            mticker.FuncFormatter(lambda y, _: f"{int(y):,}"))
        set_axis_style(ax)

    for j in range(len(ds_list), len(axes)):
        axes[j].set_visible(False)

    handles = make_handles(ALL_VERSIONS)
    fig.legend(handles=handles, loc="lower center", ncol=5,
               bbox_to_anchor=(0.5, -0.03), frameon=True,
               columnspacing=0.6, handlelength=1.1, handleheight=0.85,
               fontsize=6.5)
    fig.text(0.02, 0.5, "Number of Selected Features (log scale)",
             va="center", rotation="vertical", fontsize=8)
    fig.tight_layout(rect=[0.04, 0.06, 1, 1])
    save_fig(fig, "F5_features_all", out_dir)
    plt.close(fig)


# ══════════════════════════════════════════════════════════════════════════════
# F6: 消融实验双面板
# ══════════════════════════════════════════════════════════════════════════════

def fig_f6_ablation(df_detail, out_dir):
    """F6: Ablation study — dual panel (Accuracy + Features)."""
    print("F6: Ablation dual panel...")
    fig, axes = plt.subplots(1, 2, figsize=(7.5, 3.2))
    ds_list = [d for d in PLOT_DATASETS if d in df_detail.Dataset.unique()]
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
            bars = ax.bar(x + off, means, w, color=COLORS[v],
                          edgecolor="k", linewidth=0.4,
                          label=ABL_LABELS[v],
                          yerr=stds,
                          error_kw=dict(elinewidth=0.5, capsize=1.2,
                                        capthick=0.5, ecolor="0.35"))
            for bar in bars:
                if HATCHES[v]:
                    bar.set_hatch(HATCHES[v])
        ax.set_xticks(x)
        ax.set_xticklabels([DS_LABEL_MAP.get(d, d) for d in ds_list],
                           rotation=40, ha="right", fontsize=7)
        ax.set_ylabel(ylabel, fontsize=8)
        ax.grid(axis="y", linestyle="--", alpha=0.45)
        if metric == "Num_Features":
            ax.set_yscale("log")
        if panel_idx == 0:
            handles = make_handles(ABL_VERSIONS, use_abl=True)
            ax.legend(handles=handles, fontsize=7, ncol=2,
                      loc="lower right", frameon=True,
                      handlelength=1.1, handleheight=0.85)
    fig.tight_layout(w_pad=2.2)
    save_fig(fig, "F6_ablation", out_dir)
    plt.close(fig)


# ══════════════════════════════════════════════════════════════════════════════
# F7: 稳定性箱线图（全部 17 个共享数据集）
# ══════════════════════════════════════════════════════════════════════════════

def fig_f7_boxplot(df_detail, out_dir):
    """F7: Stability boxplot — 17 shared datasets, auto-grid."""
    print("F7: Stability boxplot (17 datasets)...")
    ds_list = get_shared_datasets(df_detail)
    n_ds = len(ds_list)
    rows, cols = _auto_grid(n_ds, max_cols=5)
    fig, axes = plt.subplots(rows, cols, figsize=(2.1 * cols, 1.7 * rows))
    axes = axes.ravel()

    for i, ds in enumerate(ds_list):
        ax = axes[i]
        data = []
        labels = []
        colors_list = []
        for v in ALL_VERSIONS:
            arr = g(df_detail, v, ds)
            if len(arr) > 0 and not np.isnan(arr).all():
                data.append(arr)
                labels.append(V_LABELS.get(v, v))
                colors_list.append(COLORS[v])
        if data:
            bp = ax.boxplot(data, tick_labels=labels, patch_artist=True,
                            widths=0.55,
                            flierprops=dict(marker='o', markersize=2.5,
                                            markerfacecolor='gray', alpha=0.5),
                            medianprops=dict(color='black', linewidth=0.8))
            for patch, color in zip(bp['boxes'], colors_list):
                patch.set_facecolor(color)
                patch.set_alpha(0.75)
        ax.set_title(DS_LABEL_MAP.get(ds, ds), fontsize=8, pad=2)
        ax.set_xticklabels(labels, rotation=60, ha="right", fontsize=5.5)
        ax.yaxis.set_major_formatter(mticker.FormatStrFormatter("%.2f"))
        ax.yaxis.set_major_locator(mticker.MaxNLocator(5, prune="lower"))
        set_axis_style(ax)

    for j in range(len(ds_list), len(axes)):
        axes[j].set_visible(False)

    fig.text(0.02, 0.5, "Classification Accuracy", va="center",
             rotation="vertical", fontsize=8)
    fig.tight_layout(rect=[0.04, 0.02, 1, 1])
    save_fig(fig, "F7_boxplot_all", out_dir)
    plt.close(fig)


# ══════════════════════════════════════════════════════════════════════════════
# F10: Wilcoxon 热图
# ══════════════════════════════════════════════════════════════════════════════

def fig_f10_wilcoxon(df_detail, out_dir):
    """F10: Wilcoxon signed-rank test heatmap on shared datasets."""
    print("F10: Wilcoxon heatmap...")
    if sp_stats is None:
        print("  [SKIP] scipy not available")
        return

    # 取 detail 数据中各版本在各数据集上的10次运行准确率
    versions_list = ALL_VERSIONS
    # 对每对算法，计算在多少数据集上显著优于/劣于对方
    alpha = 0.05
    n_v = len(versions_list)
    matrix = np.zeros((n_v, n_v))
    annot = np.empty((n_v, n_v), dtype=object)

    for i, v1 in enumerate(versions_list):
        for j, v2 in enumerate(versions_list):
            if i == j:
                matrix[i, j] = np.nan
                annot[i, j] = "-"
                continue
            wins = 0
            total = 0
            shared_ds = get_shared_datasets(df_detail)
            for ds in shared_ds:
                a1 = g(df_detail, v1, ds)
                a2 = g(df_detail, v2, ds)
                if len(a1) < 3 or len(a2) < 3:
                    continue
                # 用 paired Wilcoxon（同数据集不同run），如果不能配对就用 Mann-Whitney
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

    fig, ax = plt.subplots(figsize=(7.5, 6.5))
    im = ax.imshow(matrix, cmap="RdYlGn", vmin=0, vmax=1, aspect="auto")

    ax.set_xticks(range(n_v))
    ax.set_yticks(range(n_v))
    ax.set_xticklabels([V_LABELS[v] for v in versions_list],
                       rotation=45, ha="right", fontsize=7)
    ax.set_yticklabels([V_LABELS[v] for v in versions_list], fontsize=7)

    for i in range(n_v):
        for j in range(n_v):
            if i != j:
                val = matrix[i, j]
                color = "white" if (0.3 < val < 0.7) else "black"
                ax.text(j, i, annot[i, j], ha="center", va="center",
                        fontsize=6.5, color=color, fontweight="bold")

    ax.set_xlabel("Versus → (row beats column)", fontsize=8)
    ax.set_ylabel("Method", fontsize=8)
    ax.set_title("F10: Wilcoxon Test — Win Rate (significant, p<0.05)", fontsize=8, pad=5)

    cbar = fig.colorbar(im, ax=ax, shrink=0.82)
    cbar.set_label("Win Rate", fontsize=7)

    # 高亮 KDS_EL 行
    if "KDS_EL" in versions_list:
        ki = versions_list.index("KDS_EL")
        for spine in ["top", "bottom", "left", "right"]:
            pass
        ax.add_patch(plt.Rectangle((-0.5, ki - 0.5), n_v, 1,
                                    fill=False, edgecolor="red",
                                    linewidth=2, linestyle="-"))
        ax.text(n_v / 2, ki - 0.65, "KDS-EL (Proposed)", ha="center",
                fontsize=7, color="red", fontweight="bold")

    fig.tight_layout()
    save_fig(fig, "F10_wilcoxon_heatmap", out_dir)
    plt.close(fig)


# ══════════════════════════════════════════════════════════════════════════════
# F11: 运行时间对比
# ══════════════════════════════════════════════════════════════════════════════

def fig_f11_runtime(df_detail, out_dir):
    """F11: Runtime comparison — log scale bar chart."""
    print("F11: Runtime comparison...")
    ds_list = [d for d in PLOT_DATASETS if d in df_detail.Dataset.unique()]
    n_ds = len(ds_list)
    n_v = len(ALL_VERSIONS)
    w = 0.7 / n_v
    offs = np.linspace(-(n_v - 1) / 2 * w, (n_v - 1) / 2 * w, n_v)

    fig, ax = plt.subplots(figsize=(7.5, 3.5))
    x = np.arange(n_ds)

    for v, off in zip(ALL_VERSIONS, offs):
        means = [gm(df_detail, v, ds, "Time_sec") for ds in ds_list]
        bars = ax.bar(x + off, means, w, color=COLORS[v],
                      edgecolor="k", linewidth=0.35,
                      label=V_LABELS.get(v, v))
        for bar in bars:
            if HATCHES[v]:
                bar.set_hatch(HATCHES[v])

    ax.set_xticks(x)
    ax.set_xticklabels([DS_LABEL_MAP.get(d, d) for d in ds_list],
                       rotation=40, ha="right", fontsize=7)
    ax.set_ylabel("Average Runtime (seconds, log scale)", fontsize=8)
    ax.set_yscale("log")
    ax.grid(axis="y", linestyle="--", alpha=0.45, which="both")
    ax.yaxis.set_major_formatter(
        mticker.FuncFormatter(lambda y, _: f"{y:.0f}"))

    handles = make_handles(ALL_VERSIONS)
    ax.legend(handles=handles, loc="upper left", ncol=3,
              fontsize=6.5, frameon=True,
              columnspacing=0.6, handlelength=1.0, handleheight=0.8)
    fig.tight_layout()
    save_fig(fig, "F11_runtime", out_dir)
    plt.close(fig)


# ══════════════════════════════════════════════════════════════════════════════
# F12: 精度-特征-时间气泡图
# ══════════════════════════════════════════════════════════════════════════════

def fig_f12_bubble(df_detail, out_dir):
    """F12: Accuracy-Feature-Time bubble chart — 3D tradeoff."""
    print("F12: Accuracy-Features-Time bubble chart...")
    fig, ax = plt.subplots(figsize=(7.5, 5.5))

    for v in ALL_VERSIONS:
        xs, ys, sizes = [], [], []
        shared_ds = get_shared_datasets(df_detail)
        for ds in shared_ds:
            acc = gm(df_detail, v, ds, "Accuracy")
            feat = gm(df_detail, v, ds, "Num_Features")
            t = gm(df_detail, v, ds, "Time_sec")
            if not np.isnan(acc) and not np.isnan(feat) and not np.isnan(t):
                xs.append(feat)
                ys.append(acc)
                # 气泡大小 ≈ log(时间)，避免极端值
                sizes.append(max(15, np.log1p(t) * 30))

        if xs:
            ax.scatter(xs, ys, s=sizes, c=COLORS[v],
                       label=V_LABELS.get(v, v),
                       alpha=0.7, edgecolors="black", linewidth=0.3,
                       zorder=2 if v == "KDS_EL" else 1)

        # 高亮 KDS_EL
        if v == "KDS_EL" and xs and shared_ds:
            for xi, yi, ds in zip(xs, ys, shared_ds):
                if yi > 0.85:  # 只标注高准确率的
                    ax.annotate(ds, (xi, yi), fontsize=5.5, alpha=0.8,
                                textcoords="offset points", xytext=(4, 4))

    ax.set_xlabel("Number of Selected Features (log scale)", fontsize=8)
    ax.set_ylabel("Classification Accuracy", fontsize=8)
    ax.set_title("F12: Accuracy-Features-Time Tradeoff (bubble size = log time)",
                 fontsize=8, pad=4)
    ax.set_xscale("log")
    ax.grid(linestyle="--", alpha=0.4)
    ax.legend(fontsize=6.5, loc="lower right", ncol=2,
              frameon=True, handlelength=1.0)

    # 标注"理想区域"
    ax.annotate("Ideal Region\n(High Acc, Few Feat)",
                xy=(50, 0.97), fontsize=7, color="green",
                bbox=dict(boxstyle="round,pad=0.3", facecolor="lightgreen", alpha=0.3),
                ha="center")

    fig.tight_layout()
    save_fig(fig, "F12_bubble", out_dir)
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
    print(f"  Exp1 (SOTA): {EXP1_DIR}")
    print(f"  Exp2 (MEL only): {EXP2_DIR}")
    print(f"  Exp3 (KDS-EL): {EXP3_DIR}")
    df = load_merged_detail()
    shared = get_shared_datasets(df)
    print(f"  Merged: {len(df)} rows, datasets={df.Dataset.nunique()}, versions={df.Version.nunique()}")
    print(f"  Shared datasets: {len(shared)}")
    print(f"\nGenerating figures → {out_dir}\n")

    all_figs = {
        "F4": fig_f4_accuracy,
        "F5": fig_f5_features,
        "F6": fig_f6_ablation,
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
