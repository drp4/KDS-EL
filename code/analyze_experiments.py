"""
KDS-EL 三批实验综合分析
========================
合并三个实验文件夹的数据，生成：
  1. 汇总表（全部方法 × 全部数据集）
  2. 消融分析（DRS/KER 贡献度 + 协同效应）
  3. 统计检验（Friedman ranking）
  4. 跨数据集平均排名
"""
import os, csv, sys
import numpy as np
from collections import defaultdict

# 强制 UTF-8
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# ── 数据路径 ─────────────────────────────────────────────────────────
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIRS = {
    "ablation_v1":  os.path.join(BASE, "output", "formal_experiment_20260628_205157"),
    "sota":         os.path.join(BASE, "output", "formal_experiment_20260701_094943"),
    "ablation_v2":  os.path.join(BASE, "output", "formal_experiment_20260702_145828"),
}

# 使用 V2 的消融数据（更好），V1 的 MEL（V2 没跑 MEL）
ABLATION_PREFERENCE = {
    "KDS_EL":     "ablation_v2",
    "KDS_EL_DRS": "ablation_v2",
    "KDS_EL_KER": "ablation_v2",
    "MEL":        "ablation_v1",   # V2 没跑 MEL
}

SOTA_METHODS = ["BPSO", "SaWDE", "FWPSO", "PSO_CSM", "IGPSO"]
ABLATION_METHODS = ["MEL", "KDS_EL_DRS", "KDS_EL_KER", "KDS_EL"]

# ── 加载数据 ─────────────────────────────────────────────────────────
def load_summary(path):
    """加载 results_summary.csv，返回 {(method, dataset): stats_dict}"""
    data = {}
    fp = os.path.join(path, "results_summary.csv")
    if not os.path.exists(fp):
        return data
    with open(fp, "r", newline="") as f:
        for row in csv.DictReader(f):
            key = (row["Version"], row["Dataset"])
            data[key] = {
                "Mean_Acc": float(row["Mean_Acc"]),
                "Std_Acc":  float(row["Std_Acc"]),
                "Mean_Feat": float(row["Mean_Feat"]),
                "Std_Feat":  float(row["Std_Feat"]),
                "Mean_NHD":  float(row.get("Mean_NHD", 0)),
                "Mean_Time":  float(row.get("Mean_Time", 0)),
            }
    return data

all_data = {}  # {(method, dataset): stats}
for dir_name, dir_path in DIRS.items():
    d = load_summary(dir_path)
    for key, stats in d.items():
        all_data[key] = stats

# 收集所有方法名和数据集名
all_methods_set = set()
all_datasets_set = set()
for (m, ds) in all_data:
    all_methods_set.add(m)
    all_datasets_set.add(ds)

# ── 构建汇总表 ───────────────────────────────────────────────────────
print("=" * 100)
print("实验数据概览")
print("=" * 100)
print(f"方法数: {len(all_methods_set)} — {sorted(all_methods_set)}")
print(f"数据集数: {len(all_datasets_set)}")

# ── 确定使用的数据集列表 ─────────────────────────────────────────────
# 用 SOTA 实验的 17 个数据集作主对比（因为 SOTA 方法只在这 17 个上跑了）
sota_datasets = set()
for (m, ds) in all_data:
    if m in SOTA_METHODS:
        sota_datasets.add(ds)
sota_datasets = sorted(sota_datasets)
print(f"\nSOTA 对比数据集 ({len(sota_datasets)} 个): {sota_datasets}")

# 消融实验覆盖的数据集（V2）
ablation_datasets = set()
for (m, ds) in all_data:
    if m in ABLATION_METHODS and ds in all_datasets_set:
        ablation_datasets.add(ds)
ablation_datasets = sorted(ablation_datasets)
print(f"消融实验数据集 ({len(ablation_datasets)} 个): {ablation_datasets}")

# ── 共同数据集（SOTA 方法也跑了的消融数据集） ──────────────────────
common_datasets = sorted(set(sota_datasets) & set(ablation_datasets))
print(f"共同数据集 ({len(common_datasets)} 个): {common_datasets}")

# ══════════════════════════════════════════════════════════════════════
# 1. 汇总表：所有方法在 SOTA 17 数据集上的 Accuracy
# ══════════════════════════════════════════════════════════════════════
ALL_COMPARE = ABLATION_METHODS + SOTA_METHODS  # 9 methods total

print("\n" + "=" * 120)
print("表1: 全部方法在 SOTA 17 数据集上的 Accuracy (Mean ± Std)")
print("=" * 120)

header = f"{'Dataset':18s}"
for m in ALL_COMPARE:
    header += f"  {m:>10s}"
print(header)
print("-" * len(header))

table_data = defaultdict(dict)
for ds in common_datasets:
    row_str = f"{ds:18s}"
    for m in ALL_COMPARE:
        key = (m, ds)
        if key in all_data:
            stats = all_data[key]
            row_str += f"  {stats['Mean_Acc']:.4f}±{stats['Std_Acc']:.2f}"
            table_data[m][ds] = stats
        else:
            row_str += f"  {'N/A':>10s}"
    print(row_str)

# 跨数据集平均
print("\n" + "-" * 120)
avg_row = f"{'Avg (n=' + str(len(common_datasets)) + ')':18s}"
for m in ALL_COMPARE:
    accs = [table_data[m][ds]["Mean_Acc"] for ds in common_datasets if ds in table_data[m]]
    if accs:
        avg_row += f"  {np.mean(accs):.4f}     "
    else:
        avg_row += f"  {'N/A':>10s}"
print(avg_row)

# ══════════════════════════════════════════════════════════════════════
# 2. 特征数对比
# ══════════════════════════════════════════════════════════════════════
print("\n" + "=" * 120)
print("表2: 全部方法在 SOTA 17 数据集上的特征数 (Mean ± Std)")
print("=" * 120)

print(header)
print("-" * len(header))
for ds in common_datasets:
    row_str = f"{ds:18s}"
    for m in ALL_COMPARE:
        if ds in table_data.get(m, {}):
            stats = table_data[m][ds]
            row_str += f"  {stats['Mean_Feat']:6.0f}±{stats['Std_Feat']:.0f}"
        else:
            row_str += f"  {'N/A':>10s}"
    print(row_str)

print("\n" + "-" * 120)
avg_row = f"{'Avg':18s}"
for m in ALL_COMPARE:
    feats = [table_data[m][ds]["Mean_Feat"] for ds in common_datasets if ds in table_data[m]]
    if feats:
        avg_row += f"  {np.mean(feats):6.0f}     "
    else:
        avg_row += f"  {'N/A':>10s}"
print(avg_row)

# ══════════════════════════════════════════════════════════════════════
# 3. Friedman Ranking (在 SOTA 17 数据集上)
# ══════════════════════════════════════════════════════════════════════
print("\n" + "=" * 120)
print("表3: Friedman 排名 (基于 Accuracy, 在 SOTA 17 数据集上)")
print("=" * 120)

# 收集每个方法在每个数据集上的 Mean_Acc
methods_for_friedman = [m for m in ALL_COMPARE if all((m, ds) in all_data for ds in common_datasets)]
print(f"参与排名的方法 ({len(methods_for_friedman)} 个): {methods_for_friedman}")

# 构建矩阵: datasets × methods
ranks_matrix = np.zeros((len(common_datasets), len(methods_for_friedman)))
for i, ds in enumerate(common_datasets):
    accs = [all_data[(m, ds)]["Mean_Acc"] for m in methods_for_friedman]
    # 排名: 1 = 最好（最高 acc）
    ranks_matrix[i] = len(methods_for_friedman) + 1 - np.argsort(np.argsort(accs))

avg_ranks = ranks_matrix.mean(axis=0)

# 排序输出
order = np.argsort(avg_ranks)
print(f"\n{'Method':15s}  {'Avg Rank':10s}  {'Distribution':s}")
print("-" * 50)
for idx in order:
    m = methods_for_friedman[idx]
    r = avg_ranks[idx]
    dist = ", ".join([f"{int(ranks_matrix[j, idx])}" for j in range(len(common_datasets))])
    print(f"{m:15s}  {r:.3f}        {dist}")

# Win counts: KDS_EL vs each
print("\n" + "-" * 120)
print("KDS-EL vs 各方法的 Win/Tie/Loss (基于 Mean_Acc):")
for m in methods_for_friedman:
    if m == "KDS_EL":
        continue
    wins, ties, losses = 0, 0, 0
    for ds in common_datasets:
        k_acc = all_data[("KDS_EL", ds)]["Mean_Acc"]
        o_acc = all_data[(m, ds)]["Mean_Acc"]
        if k_acc > o_acc:
            wins += 1
        elif abs(k_acc - o_acc) < 1e-6:
            ties += 1
        else:
            losses += 1
    print(f"  KDS_EL vs {m:12s}:  Win={wins}, Tie={ties}, Loss={losses}  ({wins}/{len(common_datasets)})")

# ══════════════════════════════════════════════════════════════════════
# 4. 消融分析：DRS 贡献、KER 贡献、协同效应
# ══════════════════════════════════════════════════════════════════════
print("\n" + "=" * 120)
print("表4: 消融分析 — 各模块贡献度 (在所有共同数据集上)")
print("=" * 120)

# 使用 V2 消融数据
ablation_ds_common = sorted(set(ablation_datasets))
print(f"消融数据集 ({len(ablation_ds_common)} 个)")

print(f"\n{'Dataset':18s}  {'MEL_Acc':>8s}  {'KDS_EL':>8s}  {'Δtotal':>8s}  "
      f"{'DRS_Acc':>8s}  {'ΔDRS':>8s}  {'KER_Acc':>8s}  {'ΔKER':>8s}  "
      f"{'ΔDRS+ΔKER':>10s}  {'Synergy':>8s}")
print("-" * 120)

drs_contribs, ker_contribs, synergies, delta_totals = [], [], [], []
for ds in ablation_ds_common:
    mel   = all_data.get(("MEL", ds), {})
    drs   = all_data.get(("KDS_EL_DRS", ds), {})
    ker   = all_data.get(("KDS_EL_KER", ds), {})
    full  = all_data.get(("KDS_EL", ds), {})

    if not all([mel, drs, ker, full]):
        continue

    mel_acc  = mel["Mean_Acc"]
    drs_acc  = drs["Mean_Acc"]
    ker_acc  = ker["Mean_Acc"]
    full_acc = full["Mean_Acc"]

    delta_total = full_acc - mel_acc
    delta_drs   = drs_acc - mel_acc
    delta_ker   = ker_acc - mel_acc
    synergy     = delta_total - (delta_drs + delta_ker)

    drs_contribs.append(delta_drs)
    ker_contribs.append(delta_ker)
    synergies.append(synergy)
    delta_totals.append(delta_total)

    print(f"{ds:18s}  {mel_acc:8.4f}  {full_acc:8.4f}  {delta_total:+8.4f}  "
          f"{drs_acc:8.4f}  {delta_drs:+8.4f}  {ker_acc:8.4f}  {delta_ker:+8.4f}  "
          f"{delta_drs+delta_ker:+10.4f}  {synergy:+8.4f}")

print("\n" + "-" * 120)
print(f"{'Mean':18s}  {'':8s}  {'':8s}  {np.mean(delta_totals):+8.4f}  "
      f"{'':8s}  {np.mean(drs_contribs):+8.4f}  {'':8s}  {np.mean(ker_contribs):+8.4f}  "
      f"{np.mean(drs_contribs)+np.mean(ker_contribs):+10.4f}  {np.mean(synergies):+8.4f}")

pos_syn = sum(1 for s in synergies if s > 0)
print(f"\n正协同数据集: {pos_syn}/{len(synergies)}")

# 特征数消融
print(f"\n{'Dataset':18s}  {'MEL_Feat':>10s}  {'DRS_Feat':>10s}  {'KER_Feat':>10s}  {'KDS_EL_Feat':>10s}  {'feat_reduction':>15s}")
print("-" * 80)
for ds in ablation_ds_common:
    mel   = all_data.get(("MEL", ds), {})
    drs   = all_data.get(("KDS_EL_DRS", ds), {})
    ker   = all_data.get(("KDS_EL_KER", ds), {})
    full  = all_data.get(("KDS_EL", ds), {})

    if not all([mel, drs, ker, full]):
        continue

    red = (1 - full["Mean_Feat"] / max(mel["Mean_Feat"], 1)) * 100
    print(f"{ds:18s}  {mel['Mean_Feat']:10.0f}  {drs['Mean_Feat']:10.0f}  "
          f"{ker['Mean_Feat']:10.0f}  {full['Mean_Feat']:10.0f}  {red:+14.1f}%")

# ══════════════════════════════════════════════════════════════════════
# 5. NHD 多样性分析
# ══════════════════════════════════════════════════════════════════════
print("\n" + "=" * 120)
print("表5: NHD 结构多样性分析")
print("=" * 120)
print(f"\n{'Dataset':18s}  {'MEL':>8s}  {'KDS_EL_DRS':>10s}  {'KDS_EL_KER':>10s}  {'KDS_EL':>8s}")
print("-" * 60)
nhd_list = {"MEL": [], "KDS_EL_DRS": [], "KDS_EL_KER": [], "KDS_EL": []}
for ds in ablation_ds_common:
    vals = {}
    for m in ["MEL", "KDS_EL_DRS", "KDS_EL_KER", "KDS_EL"]:
        key = (m, ds)
        if key in all_data:
            vals[m] = all_data[key]["Mean_NHD"]
            nhd_list[m].append(all_data[key]["Mean_NHD"])
        else:
            vals[m] = float('nan')
    print(f"{ds:18s}  {vals.get('MEL', 0):8.4f}  {vals.get('KDS_EL_DRS', 0):10.4f}  "
          f"{vals.get('KDS_EL_KER', 0):10.4f}  {vals.get('KDS_EL', 0):8.4f}")

print("\n" + "-" * 60)
for m in ["MEL", "KDS_EL_DRS", "KDS_EL_KER", "KDS_EL"]:
    if nhd_list[m]:
        print(f"  {m:15s}  Mean NHD = {np.mean(nhd_list[m]):.4f}")

# ══════════════════════════════════════════════════════════════════════
# 6. 运行时间对比
# ══════════════════════════════════════════════════════════════════════
print("\n" + "=" * 120)
print("表6: 运行时间对比 (秒)")
print("=" * 120)
print(f"\n{'Method':15s}  {'Mean Time':>10s}")
print("-" * 30)
for m in ALL_COMPARE:
    times = [all_data[(m, ds)]["Mean_Time"] for ds in common_datasets if (m, ds) in all_data]
    if times:
        print(f"{m:15s}  {np.mean(times):8.1f}s")

print("\n" + "=" * 120)
print("分析完成")
print("=" * 120)
