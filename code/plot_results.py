"""
KDS-EL 结果可视化（统一脚本）
================================
从运行结果 CSV 读取数据，生成论文所需的全部图表。
用法：
    python plot_results.py                          # 使用默认路径 (config.OUT_DIR)
    python plot_results.py --csv path/to/results.csv
    python plot_results.py --figures path/to/figures
    python plot_results.py --no-show                # 不显示图形，只保存
"""
import os, sys, argparse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.ticker as mticker
from matplotlib.lines import Line2D

try:
    from scipy import stats
except ImportError:
    stats = None

import config

# ══════════════════════════════════════════════════════════════════════
# 配置
# ══════════════════════════════════════════════════════════════════════

DATASETS = [
    "Adenoma", "ALL_AML", "ALL3", "ALL4", "CNS",
    "Colon", "DLBCL", "Leukaemia", "Lymphoma", "Stroke",
    "SRBCT", "Gastric", "Prostate", "BASEHOCK",
]
DS_LABELS = [
    "Adenoma", "ALL-AML", "ALL3", "ALL4", "CNS",
    "Colon", "DLBCL", "Leukaemia", "Lymphoma", "Stroke",
    "SRBCT", "Gastric", "Prostate", "BASEHOCK",
]

ALL_V = [
    "BPSO", "SaWDE", "FWPSO", "MEL",
    "KDS_EL_DRS", "KDS_EL_KER", "KDS_EL",
    "PSO_CSM", "IGPSO",
]
ABL_V = ["MEL", "KDS_EL_DRS", "KDS_EL_KER", "KDS_EL"]

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


def parse_args():
    p = argparse.ArgumentParser(description="KDS-EL Plot Results")
    p.add_argument("--csv", default=config.CSV_PATH, help="结果 CSV 路径")
    p.add_argument("--figures", default=os.path.join(config.OUT_DIR, "figures"),
                   help="图片输出目录")
    p.add_argument("--no-show", action="store_true", help="不显示图形")
    return p.parse_args()


def load_data(csv_path):
    df = pd.read_csv(csv_path)
    for col in ["Accuracy", "Num_Features", "Time_sec", "Avg_NHD"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df.dropna(subset=["Accuracy"])


def g(df, v, ds, metric="Accuracy"):
    s = df[(df.Version == v) & (df.Dataset == ds)][metric].values
    return s if len(s) > 0 else np.array([np.nan])


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
        fig.savefig(os.path.join(out_dir, name + ext))
    print(f"  saved: {name}")


# ══════════════════════════════════════════════════════════════════════
# 各图表
# ══════════════════════════════════════════════════════════════════════

def fig_accuracy(df, out_dir):
    """Fig 1: Accuracy comparison (3×3 bar charts)."""
    print("Fig 1: Accuracy...")
    n_plots = min(9, len(DATASETS))
    rows = (n_plots + 2) // 3
    fig, axes = plt.subplots(rows, 3, figsize=(7.16, 1.8 * rows))
    axes = axes.ravel()
    for i, (ds, lbl) in enumerate(zip(DATASETS[:n_plots], DS_LABELS[:n_plots])):
        ax = axes[i]
        n_v = len(ALL_V)
        x = np.arange(n_v)
        means = [g(df, v, ds).mean() for v in ALL_V]
        stds = [g(df, v, ds).std() for v in ALL_V]
        ax.bar(x, means, 0.62, color=[COLORS[v] for v in ALL_V],
               edgecolor="k", linewidth=0.4, yerr=stds,
               error_kw=dict(elinewidth=0.55, capsize=1.5, capthick=0.55, ecolor="0.35"))
        for bar, v in zip(ax.patches, ALL_V):
            if HATCHES[v]:
                bar.set_hatch(HATCHES[v])
        ax.set_title(lbl, fontsize=8, pad=2)
        ax.set_xticks([])
        ax.yaxis.set_major_formatter(mticker.FormatStrFormatter("%.2f"))
        ax.yaxis.set_major_locator(mticker.MaxNLocator(4, prune="lower"))
        ax.grid(axis="y", linestyle="--", alpha=0.45)
    for j in range(n_plots, len(axes)):
        axes[j].set_visible(False)
    handles = make_handles(ALL_V)
    fig.legend(handles=handles, loc="lower center", ncol=5,
               bbox_to_anchor=(0.5, -0.04), frameon=True,
               columnspacing=0.7, handlelength=1.1, handleheight=0.85)
    fig.text(0.025, 0.5, "Classification Accuracy", va="center",
             rotation="vertical", fontsize=8)
    fig.tight_layout(rect=[0.04, 0.07, 1, 1])
    save_fig(fig, "fig1_accuracy", out_dir)
    plt.close(fig)


def fig_features(df, out_dir):
    """Fig 2: Feature count (3×3 log-scale)."""
    print("Fig 2: Features...")
    n_plots = min(9, len(DATASETS))
    rows = (n_plots + 2) // 3
    fig, axes = plt.subplots(rows, 3, figsize=(7.16, 1.8 * rows))
    axes = axes.ravel()
    for i, (ds, lbl) in enumerate(zip(DATASETS[:n_plots], DS_LABELS[:n_plots])):
        ax = axes[i]
        n_v = len(ALL_V)
        x = np.arange(n_v)
        means = [g(df, v, ds, "Num_Features").mean() for v in ALL_V]
        stds = [g(df, v, ds, "Num_Features").std() for v in ALL_V]
        ax.bar(x, means, 0.62, color=[COLORS[v] for v in ALL_V],
               edgecolor="k", linewidth=0.4, yerr=stds,
               error_kw=dict(elinewidth=0.55, capsize=1.5, capthick=0.55, ecolor="0.35"))
        for bar, v in zip(ax.patches, ALL_V):
            if HATCHES[v]:
                bar.set_hatch(HATCHES[v])
        ax.set_title(lbl, fontsize=8, pad=2)
        ax.set_xticks([])
        ax.set_yscale("log")
        ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda y, _: f"{int(y):,}"))
        ax.grid(axis="y", linestyle="--", alpha=0.45, which="both")
    for j in range(n_plots, len(axes)):
        axes[j].set_visible(False)
    handles = make_handles(ALL_V)
    fig.legend(handles=handles, loc="lower center", ncol=5,
               bbox_to_anchor=(0.5, -0.04), frameon=True,
               columnspacing=0.7, handlelength=1.1, handleheight=0.85)
    fig.text(0.025, 0.5, "Number of Selected Features (log scale)",
             va="center", rotation="vertical", fontsize=8)
    fig.tight_layout(rect=[0.04, 0.07, 1, 1])
    save_fig(fig, "fig2_features", out_dir)
    plt.close(fig)


def fig_ablation(df, out_dir):
    """Fig 3: Ablation study (dual panel)."""
    print("Fig 3: Ablation...")
    fig, axes = plt.subplots(1, 2, figsize=(7.16, 3.1))
    n_ds = len(DATASETS)
    x = np.arange(n_ds)
    n_v = len(ABL_V)
    w = 0.68 / n_v
    offs = np.linspace(-(n_v - 1) / 2 * w, (n_v - 1) / 2 * w, n_v)

    for panel, (ax, metric, ylabel) in enumerate(zip(
        axes, ["Accuracy", "Num_Features"],
        ["Classification Accuracy", "Number of Selected Features"],
    )):
        for v, off in zip(ABL_V, offs):
            means = [g(df, v, ds, metric).mean() for ds in DATASETS[:n_ds]]
            stds = [g(df, v, ds, metric).std() for ds in DATASETS[:n_ds]]
            bars = ax.bar(x + off, means, w, color=COLORS[v],
                          edgecolor="k", linewidth=0.4, label=ABL_LABELS[v],
                          yerr=stds,
                          error_kw=dict(elinewidth=0.5, capsize=1.2,
                                        capthick=0.5, ecolor="0.35"))
            for bar in bars:
                if HATCHES[v]:
                    bar.set_hatch(HATCHES[v])
        ax.set_xticks(x)
        ax.set_xticklabels(DS_LABELS[:n_ds], rotation=40, ha="right", fontsize=7)
        ax.set_ylabel(ylabel, fontsize=8)
        ax.grid(axis="y", linestyle="--", alpha=0.45)
        if metric == "Num_Features":
            ax.set_yscale("log")
        if panel == 0:
            handles = make_handles(ABL_V, use_abl=True)
            ax.legend(handles=handles, fontsize=7, ncol=2,
                      loc="lower right", frameon=True,
                      handlelength=1.1, handleheight=0.85)
    fig.tight_layout(w_pad=2.5)
    save_fig(fig, "fig3_ablation", out_dir)
    plt.close(fig)


def fig_rank(df, out_dir):
    """Fig 6: Average Friedman rank."""
    print("Fig 6: Friedman rank...")
    ranks = {v: [] for v in ALL_V}
    for ds in DATASETS:
        if ds not in df.Dataset.values:
            continue
        means = {v: g(df, v, ds).mean() for v in ALL_V}
        for r, v in enumerate(sorted(means, key=means.get, reverse=True), 1):
            ranks[v].append(r)
    avg = {v: np.mean(ranks[v]) for v in ALL_V if ranks[v]}
    sv = sorted(avg, key=avg.get)

    fig, ax = plt.subplots(figsize=(3.54, 2.9))
    y = np.arange(len(sv))
    vals = [avg[v] for v in sv]
    bars = ax.barh(y, vals, 0.6, color=[COLORS[v] for v in sv],
                   edgecolor="k", linewidth=0.4)
    for bar, v in zip(bars, sv):
        if HATCHES[v]:
            bar.set_hatch(HATCHES[v])
    ki = sv.index("KDS_EL") if "KDS_EL" in sv else -1
    if ki >= 0:
        ax.annotate("KDS-EL\n(Proposed)", xy=(avg["KDS_EL"], ki),
                    xytext=(avg["KDS_EL"] + 1.1, ki),
                    arrowprops=dict(arrowstyle="->", lw=0.75, color="k"),
                    fontsize=6.5, va="center")
    ax.set_yticks(y)
    ax.set_yticklabels([V_LABELS[v] for v in sv], fontsize=7)
    ax.set_xlabel("Average Friedman Rank", fontsize=8)
    ax.set_xlim(0, max(vals) + 2.2)
    ax.grid(axis="x", linestyle="--", alpha=0.45)
    ax.invert_yaxis()
    fig.tight_layout()
    save_fig(fig, "fig6_rank", out_dir)
    plt.close(fig)


def fig_runtime(df, out_dir):
    """Fig 8: Runtime comparison."""
    print("Fig 8: Runtime...")
    RT_V = [v for v in ALL_V if v != "KDS_EL_DRS" and v != "KDS_EL_KER"]
    fig, axes = plt.subplots(1, 2, figsize=(7.16, 2.7))
    # Panel A: non-Stroke
    ax = axes[0]
    non_stroke = [ds for ds in DATASETS if ds != "Stroke"]
    n_ds = len(non_stroke)
    n_v = len(RT_V)
    w = 0.68 / n_v
    x = np.arange(n_ds)
    offs = np.linspace(-(n_v - 1) / 2 * w, (n_v - 1) / 2 * w, n_v)
    for v, off in zip(RT_V, offs):
        means = [g(df, v, ds, "Time_sec").mean() for ds in non_stroke]
        if np.all(np.isnan(means)):
            continue
        bars = ax.bar(x + off, means, w, color=COLORS[v],
                      edgecolor="k", linewidth=0.35, label=V_LABELS[v])
        for bar in bars:
            if HATCHES[v]:
                bar.set_hatch(HATCHES[v])
    ax.set_xticks(x)
    lbls = [DS_LABELS[DATASETS.index(d)] for d in non_stroke]
    ax.set_xticklabels(lbls, rotation=38, ha="right", fontsize=7)
    ax.set_ylabel("Avg. Runtime (s)", fontsize=8)
    ax.set_yscale("log")
    ax.set_title("Datasets (excl. Stroke)", fontsize=8, pad=2)
    # Panel B: Stroke only
    ax = axes[1]
    x2 = np.arange(len(RT_V))
    means_s = [g(df, v, "Stroke", "Time_sec").mean() for v in RT_V]
    bars = ax.bar(x2, means_s, 0.58, color=[COLORS[v] for v in RT_V],
                  edgecolor="k", linewidth=0.4)
    for bar, v in zip(bars, RT_V):
        if HATCHES[v]:
            bar.set_hatch(HATCHES[v])
    ax.set_xticks(x2)
    ax.set_xticklabels([V_LABELS[v] for v in RT_V], rotation=38, ha="right", fontsize=7)
    ax.set_ylabel("Avg. Runtime (s)", fontsize=8)
    ax.set_title("Stroke (d=26,877)", fontsize=8, pad=2)
    handles = make_handles(RT_V)
    fig.legend(handles=handles, loc="lower center", ncol=4,
               bbox_to_anchor=(0.5, -0.08), frameon=True, fontsize=7,
               columnspacing=0.7, handlelength=1.1)
    fig.tight_layout(rect=[0, 0.1, 1, 1])
    save_fig(fig, "fig8_runtime", out_dir)
    plt.close(fig)


def summary_table(df, out_dir):
    """生成结果汇总表 (CSV)。"""
    print("Summary table...")
    rows = []
    for ds in DATASETS:
        for v in ALL_V:
            acc = g(df, v, ds).mean()
            nf = g(df, v, ds, "Num_Features").mean()
            t = g(df, v, ds, "Time_sec").mean()
            if not np.isnan(acc):
                rows.append({
                    "Dataset": ds, "Method": V_LABELS.get(v, v),
                    "Accuracy": f"{acc:.4f}",
                    "Features": f"{nf:.1f}",
                    "Time_s": f"{t:.1f}",
                })
    pd.DataFrame(rows).to_csv(os.path.join(out_dir, "summary.csv"), index=False)
    print(f"  summary.csv written")


def main():
    args = parse_args()
    os.makedirs(args.figures, exist_ok=True)

    print(f"Reading: {args.csv}")
    df = load_data(args.csv)
    print(f"  {len(df)} rows, {df.Version.nunique()} versions\n")

    figs = [
        fig_accuracy,
        fig_features,
        fig_ablation,
        fig_rank,
        fig_runtime,
        summary_table,
    ]
    for fn in figs:
        try:
            fn(df, args.figures)
        except Exception as e:
            print(f"  [SKIP] {fn.__name__}: {e}")

    print(f"\nAll figures → {args.figures}")


if __name__ == "__main__":
    main()
