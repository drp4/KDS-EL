"""
F8 + F9: 收敛曲线 & TwoPhase 消融收敛
=====================================
从 npy 文件读取迭代曲线数据，生成：
  F8 — 适应度/准确率收敛曲线 (爱斯维尔顶刊标准: 2×3 平衡网格，包含全局均值与5个典型数据集)
  F9 — TwoPhase vs NoPool 消融收敛对比 (全量 20 数据集网格)

数据来源：
  - Exp1: output/formal_experiment_20260701_094943/curves/
  - Exp2: output/formal_experiment_20260628_205157/curves/
  - Exp4: output/formal_experiment_20260707_142018/curves/
  - MEL_MI: output/formal_experiment_mel_mi/curves/
  - Final: output/formal_experiment_final/curves/

用法：python code/plot_convergence.py [--out output/figures/]
"""
import os, sys, argparse, re
from pathlib import Path
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from matplotlib.lines import Line2D

PROJ = Path(__file__).resolve().parent.parent
EXP1_CURVES = PROJ / "output" / "formal_experiment_20260701_094943" / "curves"
EXP2_CURVES = PROJ / "output" / "formal_experiment_20260628_205157" / "curves"
NEW_SOTA_CURVES = PROJ / "output" / "formal_experiment_20260905_211755" / "curves"
MEL_MI_CURVES = PROJ / "output" / "formal_experiment_mel_mi" / "curves"
FINAL_CURVES = PROJ / "output" / "formal_experiment_final" / "curves"

ALL_CURVE_DIRS = [EXP1_CURVES, EXP2_CURVES, NEW_SOTA_CURVES, MEL_MI_CURVES, FINAL_CURVES]

from plot_style import (
    apply_style, COLOR_PALETTE, MARKERS, LINESTYLES,
    V_LABELS as STYLE_V_LABELS
)

# Apply unified Elsevier publication styling
apply_style()

COLORS = COLOR_PALETTE
V_LABELS = STYLE_V_LABELS
LINE_STYLES = LINESTYLES


# 20 权威基准数据集
CORE_20 = [
    "ALL1", "ALL4", "ALL_AML", "Adenoma", "BASEHOCK", "COIL20",
    "Colon", "DLBCL", "Gastric", "Gastric1", "Gastric2", "ISOLET",
    "Leukaemia", "Lymphoma", "Myeloma", "PCMAC", "Prostate",
    "SRBCT", "T1D", "madelon"
]

# 4 变体消融链
F8_ABL_VERSIONS = ["KDS_EL_TwoPhase", "KDS_EL_NoPool", "MEL_MI", "MEL"]

# F9: TwoPhase vs NoPool 消融收敛对比
F9_VERSIONS = ["KDS_EL_NoPool", "KDS_EL_TwoPhase"]


def _get_curve_shared_datasets(versions, prefix="curve"):
    """Compute datasets that have curve data for all specified versions."""
    all_dirs = ALL_CURVE_DIRS
    ds_sets = []
    for v in versions:
        files = set()
        for d in all_dirs:
            if d.exists():
                pattern = re.compile(rf"{re.escape(prefix)}_{re.escape(v)}_(\w+)_run\d+\.npy")
                for f in d.iterdir():
                    m = pattern.match(f.name)
                    if m:
                        files.add(m.group(1))
        if files:
            ds_sets.append(files)
    shared = set.intersection(*ds_sets) if ds_sets else set()
    return sorted(shared)


def _auto_grid(n, max_cols=5):
    cols = min(n, max_cols)
    rows = (n + cols - 1) // cols
    return rows, cols


def load_curves(version, dataset, curves_dir, prefix="curve"):
    """加载某个 version+dataset 的所有 run 曲线，返回 (n_runs, T) 数组。"""
    pattern = re.compile(
        rf"{prefix}_{re.escape(version)}_{re.escape(dataset)}_run(\d+)\.npy"
    )
    runs = []
    if not curves_dir.exists():
        return None
    for fname in sorted(curves_dir.iterdir()):
        m = pattern.match(fname.name)
        if m:
            arr = np.load(fname, allow_pickle=True)
            runs.append(arr.astype(np.float64))
    if not runs:
        return None
    min_len = min(len(r) for r in runs)
    runs = np.array([r[:min_len] for r in runs])
    return runs


def load_from_all(version, dataset, prefix="curve"):
    """从正确的实验目录加载曲线：
       - KDS-EL 变体 → FINAL_CURVES
       - MEL_MI → MEL_MI_CURVES
       - MEL → EXP2_CURVES / EXP1_CURVES
       - 新 SOTA (bIRIME, BinCOA, DENCA_SO) → NEW_SOTA_CURVES
       - 经典单目标 SOTA → EXP1_CURVES / EXP2_CURVES
    """
    KDS_VERSIONS = {"KDS_EL_NoPool", "KDS_EL_TwoPhase"}
    NEW_SOTA_NAMES = {"bIRIME", "BinCOA", "DENCA_SO"}

    if version in KDS_VERSIONS:
        data = load_curves(version, dataset, FINAL_CURVES, prefix)
    elif version == "MEL_MI":
        data = load_curves(version, dataset, MEL_MI_CURVES, prefix)
    elif version in NEW_SOTA_NAMES:
        data = load_curves(version, dataset, NEW_SOTA_CURVES, prefix)
    elif version == "MEL":
        data = load_curves(version, dataset, EXP2_CURVES, prefix)
        if data is None:
            data = load_curves(version, dataset, EXP1_CURVES, prefix)
    else:
        data = load_curves(version, dataset, EXP1_CURVES, prefix)
        if data is None:
            data = load_curves(version, dataset, EXP2_CURVES, prefix)
    return data


def plot_with_band(ax, data, color, label, linestyle, alpha_fill=0.12, linewidth=1.1):
    """绘制均值 ± 标准差曲线。"""
    if data is None or len(data) == 0:
        return
    T = data.shape[1]
    x = np.arange(T)
    mean = np.mean(data, axis=0)
    std = np.std(data, axis=0)
    ax.plot(x, mean, color=color, linestyle=linestyle, linewidth=linewidth, label=label)
    ax.fill_between(x, mean - std, mean + std, color=color, alpha=alpha_fill,
                    linewidth=0)
    return mean, std


def save_fig(fig, name, out_dir):
    for ext in (".pdf", ".png"):
        p = os.path.join(out_dir, name + ext)
        fig.savefig(p)
    print(f"  [OK] {name}")


# ══════════════════════════════════════════════════════════════════════════════
# F8_sota: SOTA 代表性单目标包装式算法收敛对比 (4×5 全量 20 数据集全景网格)
# ══════════════════════════════════════════════════════════════════════════════

def fig_sota_convergence(out_dir):
    """SOTA 5-algorithm convergence panorama across all 20 benchmark datasets (4x5 grid)."""
    SOTA_ALGOS = [
        ("KDS_EL_TwoPhase", "KDS-EL", "FINAL", "#C82423", "-", 1.5, "o", 10),
        ("FWPSO", "FWPSO", "SOTA", "#1E88E5", "--", 1.1, "s", 5),
        ("SaWDE", "SaWDE", "SOTA", "#00897B", "-.", 1.1, "^", 4),
        ("MEL", "MEL", "MEL", "#7E57C2", ":", 1.1, "v", 3),
        ("BPSO", "BPSO", "SOTA", "#475569", (0, (3, 1, 1, 1)), 1.0, "x", 2),
    ]

    display_names = {
        "ALL_AML": "ALL-AML",
        "madelon": "Madelon",
    }

    print("Generating SOTA 5-algorithm 4x5 convergence panorama across 20 datasets...")
    fig, axes = plt.subplots(4, 5, figsize=(10.5, 7.5))
    axes = axes.ravel()

    for i, ds in enumerate(CORE_20):
        ax = axes[i]
        dname = display_names.get(ds, ds)
        panel_label = chr(ord('a') + i)

        for key, label, dkey, color, ls, lw, marker, zorder in SOTA_ALGOS:
            data = load_from_all(key, ds, prefix="curve")
            if data is not None and len(data) > 0:
                mean_c = np.mean(data, axis=0)
                x = np.arange(len(mean_c))
                ax.plot(x, mean_c, color=color, linestyle=ls, linewidth=lw,
                        marker=marker, markevery=20, markersize=3.8,
                        label=label, zorder=zorder)

        ax.set_title(f"({panel_label}) {dname}", fontsize=10.0, fontweight="bold", pad=3.5)
        ax.set_xlabel("Iteration", fontsize=9.2, labelpad=2.0)
        ax.set_ylabel("Fitness", fontsize=9.2, labelpad=2.0)
        ax.set_xlim(0, 100)
        ax.set_xticks([0, 50, 100])
        ax.tick_params(axis='both', which='major', labelsize=8.2, pad=2)
        ax.yaxis.set_major_locator(mticker.MaxNLocator(4, prune="lower"))
        ax.yaxis.set_major_formatter(mticker.FormatStrFormatter("%.2f"))
        ax.grid(True, linestyle="--", alpha=0.6, color="#E2E8F0", linewidth=0.4)

    handles = [
        Line2D([0], [0], color=color, linestyle=ls, linewidth=lw * 1.2,
               marker=marker, markersize=4.8, label=label)
        for _, label, _, color, ls, lw, marker, _ in SOTA_ALGOS
    ]
    fig.legend(handles=handles, loc="lower center", bbox_to_anchor=(0.5, -0.010),
               ncol=5, frameon=True, facecolor="#ffffff", edgecolor="#CBD5E0",
               fontsize=9.5, handlelength=2.4, columnspacing=2.0, framealpha=0.95)

    plt.tight_layout(rect=[0, 0.042, 1, 1])
    save_fig(fig, "F8_sota_convergence", out_dir)
    plt.close(fig)
    print("  [OK] F8_sota_convergence")


# ══════════════════════════════════════════════════════════════════════════════
# F5_ablation: 消融收敛曲线 (3×3 矩阵: 全局均值 + 8 代表性数据集，阐释 TPS 机制)
# ══════════════════════════════════════════════════════════════════════════════

def fig_f8_convergence(out_dir):
    """Ablation convergence — Balanced 3×3 grid: (a) Overall Mean (20 DS) + (b)-(i) 8 representative datasets."""
    # 8 个代表性数据集（标题保持极简纯净，N/D 已在 Table 2 详述）
    REP_DS_CONFIGS = [
        ("Adenoma", "(b) Adenoma", (0.92, 1.005)),
        ("DLBCL", "(c) DLBCL", (0.90, 1.005)),
        ("Leukaemia", "(d) Leukaemia", (0.93, 1.005)),
        ("T1D", "(e) T1D", (0.65, 0.90)),
        ("BASEHOCK", "(f) BASEHOCK", (0.80, 0.94)),
        ("COIL20", "(g) COIL20", (0.87, 1.005)),
        ("ISOLET", "(h) ISOLET", (0.79, 0.93)),
        ("madelon", "(i) Madelon", (0.65, 0.92)),
    ]

    ABL_PLOT_COLORS = {
        "KDS_EL_TwoPhase": COLORS["KDS_EL_TwoPhase"],   # Nature Vermilion (#C82423)
        "KDS_EL_NoPool":   COLORS["KDS_EL_NoPool"],     # Professional Blue (#1E88E5)
        "MEL_MI":          COLORS["MEL_MI"],            # Jade Teal (#00897B)
        "MEL":             COLORS["MEL"],               # Slate Violet / Purple (#7E57C2)
    }
    ABL_PLOT_STYLES = {
        "KDS_EL_TwoPhase": "-",
        "KDS_EL_NoPool":   "--",
        "MEL_MI":          "-.",
        "MEL":             ":",
    }
    ABL_PLOT_MARKERS = {
        "KDS_EL_TwoPhase": "o",
        "KDS_EL_NoPool":   "s",
        "MEL_MI":          "^",
        "MEL":             "v",
    }
    ABL_PLOT_WIDTHS = {
        "KDS_EL_TwoPhase": 1.7,
        "KDS_EL_NoPool":   1.3,
        "MEL_MI":          1.2,
        "MEL":             1.1,
    }
    ABL_PLOT_LABELS = {
        "KDS_EL_TwoPhase": "KDS-EL",
        "KDS_EL_NoPool":   "w/o TPS",
        "MEL_MI":          "w/o TPS & KER",
        "MEL":             "MEL",
    }

    print("F5/F8: Convergence — Comprehensive 3x3 Grid (Clean Titles & Correct Limits)...")

    # ── 1. 全局 20 数据集均值预计算 ──
    all_curves = {v: [] for v in F8_ABL_VERSIONS}
    for v in F8_ABL_VERSIONS:
        for ds in CORE_20:
            data = load_from_all(v, ds, prefix="curve")
            if data is not None:
                all_curves[v].append(np.mean(1.0 - data, axis=0))

    fig, axes = plt.subplots(3, 3, figsize=(8.8, 6.4))
    axes = axes.ravel()

    # ── (a) Overall Mean Convergence (Top-Left Subplot) ──
    ax0 = axes[0]
    for v in F8_ABL_VERSIONS:
        if all_curves[v]:
            stacked = np.array(all_curves[v])
            mean_c = np.mean(stacked, axis=0)
            x = np.arange(len(mean_c))
            ax0.plot(x, mean_c, color=ABL_PLOT_COLORS[v], linestyle=ABL_PLOT_STYLES[v],
                     linewidth=ABL_PLOT_WIDTHS[v], marker=ABL_PLOT_MARKERS[v],
                     markevery=15, markersize=4.2)

    ax0.set_title("(a) Overall Mean", fontsize=9.2, fontweight="bold", pad=3.5)
    ax0.set_xlabel("Iteration", fontsize=8.5, labelpad=2.0)
    ax0.set_ylabel("Mean Accuracy", fontsize=8.5, labelpad=2.0)
    ax0.tick_params(axis='both', which='major', labelsize=7.8, pad=2)
    ax0.yaxis.set_major_formatter(mticker.FormatStrFormatter("%.2f"))
    ax0.set_xlim(0, 100)
    ax0.set_ylim(0.83, 0.97)
    ax0.grid(True, linestyle="--", alpha=0.6, color="#E2E8F0", linewidth=0.4)

    # ── (b)-(i) 8 个代表性数据集 ──
    for idx, (ds, title, ylim) in enumerate(REP_DS_CONFIGS, start=1):
        ax = axes[idx]
        for v in F8_ABL_VERSIONS:
            data = load_from_all(v, ds, prefix="curve")
            if data is not None:
                acc_data = 1.0 - data
                mean_c = np.mean(acc_data, axis=0)
                x = np.arange(len(mean_c))
                ax.plot(x, mean_c, color=ABL_PLOT_COLORS[v], linestyle=ABL_PLOT_STYLES[v],
                        linewidth=ABL_PLOT_WIDTHS[v], marker=ABL_PLOT_MARKERS[v],
                        markevery=15, markersize=4.2)

        ax.set_title(title, fontsize=9.2, fontweight="bold", pad=3.5)
        ax.set_xlabel("Iteration", fontsize=8.5, labelpad=2.0)
        ax.set_ylabel("Accuracy", fontsize=8.5, labelpad=2.0)
        ax.tick_params(axis='both', which='major', labelsize=7.8, pad=2)
        ax.yaxis.set_major_formatter(mticker.FormatStrFormatter("%.2f"))
        ax.set_xlim(0, 100)
        ax.set_ylim(ylim)
        ax.grid(True, linestyle="--", alpha=0.6, color="#E2E8F0", linewidth=0.4)

    # ── 全局统一底部图例 ──
    handles = [
        Line2D([0], [0], color=ABL_PLOT_COLORS[v], linestyle=ABL_PLOT_STYLES[v],
               linewidth=1.7 if "TwoPhase" in v else 1.3, marker=ABL_PLOT_MARKERS[v],
               markersize=4.8, label=ABL_PLOT_LABELS[v])
        for v in F8_ABL_VERSIONS
    ]
    fig.legend(handles=handles, loc="lower center", bbox_to_anchor=(0.5, -0.015),
               ncol=4, frameon=True, facecolor="#ffffff", edgecolor="#CBD5E0",
               fontsize=8.8, handlelength=2.4, columnspacing=1.8, framealpha=0.95)

    plt.tight_layout(rect=[0, 0.038, 1, 1])
    save_fig(fig, "F8_convergence", out_dir)
    save_fig(fig, "F5_ablation_convergence", out_dir)
    plt.close(fig)


# ══════════════════════════════════════════════════════════════════════════════
# F9: TwoPhase vs NoPool 消融收敛对比
# ══════════════════════════════════════════════════════════════════════════════

def fig_f9_nhd(out_dir):
    """F9: TwoPhase vs NoPool convergence — fitness curves, all shared datasets."""
    ds_list = _get_curve_shared_datasets(F9_VERSIONS, prefix="curve")
    ds_list = [d for d in ds_list if d in CORE_20]
    n_ds = len(ds_list)
    rows, cols = _auto_grid(n_ds, max_cols=5)
    print(f"F9: TwoPhase vs NoPool convergence ({n_ds} datasets, {rows}x{cols})...")

    fig, axes = plt.subplots(rows, cols, figsize=(2.1 * cols, 1.8 * rows))
    if n_ds == 1:
        axes = np.array([axes])
    axes = axes.ravel()

    for i, ds in enumerate(ds_list):
        ax = axes[i]
        for v in F9_VERSIONS:
            data = load_from_all(v, ds, prefix="curve")
            if data is not None:
                acc_data = 1.0 - data  # fitness -> accuracy
                plot_with_band(ax, acc_data, COLORS.get(v, "#333333"),
                               V_LABELS.get(v, v),
                               LINE_STYLES.get(v, "-"), alpha_fill=0.15)

        ax.set_title(ds, fontsize=7, pad=1.5)
        ax.set_xlabel("Iteration", fontsize=6.5)
        ax.set_ylabel("Accuracy", fontsize=6.5)
        ax.yaxis.set_major_formatter(mticker.FormatStrFormatter("%.2f"))
        ax.yaxis.set_major_locator(mticker.MaxNLocator(4, prune="lower"))
        ax.grid(linestyle="--", alpha=0.4, which="both")
        ax.set_xlim(0, 100)

    for j in range(n_ds, len(axes)):
        axes[j].set_visible(False)

    handles = []
    for v in F9_VERSIONS:
        handles.append(Line2D([0], [0], color=COLORS.get(v, "#333333"),
                              linestyle=LINE_STYLES.get(v, "-"),
                              linewidth=1.3, label=V_LABELS.get(v, v)))
    fig.legend(handles=handles, loc="lower center", ncol=2,
               bbox_to_anchor=(0.5, -0.03), frameon=True,
               columnspacing=0.6, handlelength=1.2, fontsize=6)
    fig.suptitle("F9: Convergence of KDS-EL and KDS-EL w/o TPS (Mean Accuracy ± Std across 10 runs)",
                 fontsize=9, y=1.01)
    fig.tight_layout(rect=[0, 0.06, 1, 0.97])
    save_fig(fig, "F9_twophase_convergence", out_dir)
    plt.close(fig)


# ══════════════════════════════════════════════════════════════════════════════
# Main
# ══════════════════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(description="KDS-EL Convergence Plotter")
    parser.add_argument("--out", default=None,
                        help="Output directory (default: output/figures/)")
    parser.add_argument("--fig", nargs="*", default=None,
                        help="Specific figures: F8 F9")
    args = parser.parse_args()

    out_dir = args.out or str(PROJ / "output" / "figures")
    os.makedirs(out_dir, exist_ok=True)

    print("Curve data sources:")
    print(f"  Exp1 (SOTA):     {EXP1_CURVES}")
    print(f"  Exp2 (MEL):      {EXP2_CURVES}")
    print(f"  New SOTA:        {NEW_SOTA_CURVES}")
    print(f"  MEL+MI:          {MEL_MI_CURVES}")
    print(f"  Final (TwoPhase):{FINAL_CURVES}")
    print(f"\nGenerating -> {out_dir}\n")

    all_figs = {
        "F8": fig_sota_convergence,
        "F8_sota": fig_sota_convergence,
        "F5_ablation": fig_f8_convergence,
        "F8_ablation": fig_f8_convergence,
        "F9": fig_f9_nhd,
    }
    requested = args.fig if args.fig else list(all_figs.keys())

    for key in requested:
        if key in all_figs:
            try:
                all_figs[key](out_dir)
            except Exception as e:
                print(f"  [FAIL] {key}: {e}")
                import traceback
                traceback.print_exc()
        else:
            print(f"  [SKIP] Unknown figure: {key}")

    print(f"\nDone! -> {out_dir}")


if __name__ == "__main__":
    main()
