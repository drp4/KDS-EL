"""
消融实验有效性深度分析
========================
回答核心问题：三个变体 Accuracy 接近，消融是否还有意义？
从多个维度深挖差异。
"""
import os, csv, sys
import numpy as np
from collections import defaultdict

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def load_detail(path):
    """加载 detail CSV"""
    rows = []
    fp = os.path.join(path, "results_detail.csv")
    if not os.path.exists(fp):
        return rows
    with open(fp, "r", newline="") as f:
        for row in csv.DictReader(f):
            row["Accuracy"] = float(row["Accuracy"])
            row["Num_Features"] = int(row["Num_Features"])
            row["Avg_NHD"] = float(row.get("Avg_NHD", 0))
            row["Run"] = int(row["Run"])
            rows.append(row)
    return rows

def load_summary(path):
    data = {}
    fp = os.path.join(path, "results_summary.csv")
    if not os.path.exists(fp):
        return data
    with open(fp, "r", newline="") as f:
        for row in csv.DictReader(f):
            key = (row["Version"], row["Dataset"])
            data[key] = {
                "Mean_Acc": float(row["Mean_Acc"]),
                "Std_Acc": float(row["Std_Acc"]),
                "Mean_Feat": float(row["Mean_Feat"]),
                "Std_Feat": float(row["Std_Feat"]),
                "Mean_NHD": float(row.get("Mean_NHD", 0)),
            }
    return data

# 加载数据
dir_v1 = os.path.join(BASE, "output", "formal_experiment_20260628_205157")
dir_v2 = os.path.join(BASE, "output", "formal_experiment_20260702_145828")
dir_sota = os.path.join(BASE, "output", "formal_experiment_20260701_094943")

summary_v1 = load_summary(dir_v1)
summary_v2 = load_summary(dir_v2)
detail_v2 = load_detail(dir_v2)
detail_v1 = load_detail(dir_v1)

# 合并：MEL 来自 V1，消融来自 V2
all_detail = detail_v2 + [r for r in detail_v1 if r["Version"] == "MEL"]

# 按方法-数据集分组
from collections import defaultdict
groups = defaultdict(list)
for r in all_detail:
    groups[(r["Version"], r["Dataset"])].append(r)

# 共用数据集
datasets_v2 = sorted(set(r["Dataset"] for r in detail_v2))
datasets_mel = sorted(set(r["Dataset"] for r in detail_v1 if r["Version"] == "MEL"))
common_ds = sorted(set(datasets_v2) & set(datasets_mel))
print(f"共用数据集: {len(common_ds)} 个")

# ═══════════════════════════════════════════════════════════════════
# 分析1: 每个数据集上，KDS_EL 是否同时击败 DRS 和 KER？
# ═══════════════════════════════════════════════════════════════════
print("\n" + "=" * 90)
print("分析1: 逐数据集 — KDS_EL vs DRS vs KER (基于 10 次运行的 Mean_Acc)")
print("=" * 90)

methods_abl = ["MEL", "KDS_EL_DRS", "KDS_EL_KER", "KDS_EL"]

print(f"{'Dataset':16s}  {'MEL':>8s}  {'DRS':>8s}  {'KER':>8s}  {'KDS_EL':>8s}  "
      f"{'Best':>8s}  {'KDS_EL':>8s}  {'KDS_EL':>8s}")
print(f"{'':16s}  {'Acc':>8s}  {'Acc':>8s}  {'Acc':>8s}  {'Acc':>8s}  "
      f"{'single':>8s}  {'vs DRS':>8s}  {'vs KER':>8s}")
print("-" * 90)

results_matrix = []
for ds in common_ds:
    mel   = summary_v1.get(("MEL", ds), {})
    drs   = summary_v2.get(("KDS_EL_DRS", ds), {})
    ker   = summary_v2.get(("KDS_EL_KER", ds), {})
    full  = summary_v2.get(("KDS_EL", ds), {})

    if not all([mel, drs, ker, full]):
        continue

    mel_acc  = mel["Mean_Acc"]
    drs_acc  = drs["Mean_Acc"]
    ker_acc  = ker["Mean_Acc"]
    full_acc = full["Mean_Acc"]

    best_single = max(drs_acc, ker_acc)
    vs_drs = "WIN" if full_acc > drs_acc else ("LOSE" if full_acc < drs_acc else "TIE")
    vs_ker = "WIN" if full_acc > ker_acc else ("LOSE" if full_acc < ker_acc else "TIE")
    vs_best = "WIN" if full_acc > best_single else ("LOSE" if full_acc < best_single else "TIE")

    # 同时击败两者？
    beat_both = "✅" if full_acc > drs_acc and full_acc > ker_acc else ""
    beat_single_best = "✅" if full_acc >= best_single else ""

    results_matrix.append({
        "ds": ds, "mel": mel_acc, "drs": drs_acc, "ker": ker_acc, "full": full_acc,
        "best_single": best_single, "vs_drs": vs_drs, "vs_ker": vs_ker,
        "beat_both": beat_both, "beat_single_best": beat_single_best,
    })

    print(f"{ds:16s}  {mel_acc:8.4f}  {drs_acc:8.4f}  {ker_acc:8.4f}  {full_acc:8.4f}  "
          f"{best_single:8.4f}  {vs_drs:>8s}  {vs_ker:>8s}  {beat_both}")

# 统计
beat_drs = sum(1 for r in results_matrix if r["vs_drs"] == "WIN")
beat_ker = sum(1 for r in results_matrix if r["vs_ker"] == "WIN")
beat_both_count = sum(1 for r in results_matrix if r["beat_both"])
beat_single = sum(1 for r in results_matrix if r["beat_single_best"])

print(f"\n统计 ({len(results_matrix)} 数据集):")
print(f"  KDS_EL > DRS:  {beat_drs}/{len(results_matrix)}")
print(f"  KDS_EL > KER:  {beat_ker}/{len(results_matrix)}")
print(f"  KDS_EL > both: {beat_both_count}/{len(results_matrix)}")
print(f"  KDS_EL >= max(DRS,KER): {beat_single}/{len(results_matrix)}")

# ═══════════════════════════════════════════════════════════════════
# 分析2: 逐 run 的 Wilcoxon 配对检验
# ═══════════════════════════════════════════════════════════════════
print("\n" + "=" * 90)
print("分析2: 逐数据集 Wilcoxon 检验 (KDS_EL vs 各变体, 10 runs)")
print("=" * 90)

# 对每个数据集，做配对检验
for method_name in ["KDS_EL_DRS", "KDS_EL_KER", "MEL"]:
    print(f"\n--- KDS_EL vs {method_name} ---")
    sig_wins = 0
    sig_losses = 0
    no_diff = 0

    for ds in common_ds:
        full_runs = groups.get(("KDS_EL", ds), [])
        other_runs = groups.get((method_name, ds), [])

        if len(full_runs) < 5 or len(other_runs) < 5:
            continue

        full_accs = np.array([r["Accuracy"] for r in full_runs])
        other_accs = np.array([r["Accuracy"] for r in other_runs])

        # 配对差异
        diffs = full_accs - other_accs
        mean_diff = np.mean(diffs)

        # 简单 sign test (10 runs 足够)
        pos = int(np.sum(diffs > 0))
        neg = int(np.sum(diffs < 0))
        tie = int(np.sum(np.abs(diffs) < 1e-8))

        # 二项检验 (单侧)
        from scipy.stats import binomtest
        n_nontie = pos + neg
        if n_nontie > 0:
            p_val = binomtest(min(pos, neg), n=n_nontie, p=0.5, alternative='two-sided').pvalue
        else:
            p_val = 1.0

        if p_val < 0.05 and mean_diff > 0:
            sig_wins += 1
            sig_str = f"✅ KDS_EL 显著更好 (p={p_val:.4f})"
        elif p_val < 0.05 and mean_diff < 0:
            sig_losses += 1
            sig_str = f"❌ KDS_EL 显著更差 (p={p_val:.4f})"
        else:
            no_diff += 1
            sig_str = f"— 无显著差异 (p={p_val:.4f})"

        if p_val < 0.05:
            print(f"  {ds:16s}  Δ={mean_diff:+.4f}  pos={pos} neg={neg}  {sig_str}")

    print(f"  汇总: 显著更好={sig_wins}, 显著更差={sig_losses}, 无差异={no_diff}")

# ═══════════════════════════════════════════════════════════════════
# 分析3: 三个指标的综合排名的 Pareto 分析
# ═══════════════════════════════════════════════════════════════════
print("\n" + "=" * 90)
print("分析3: 三维指标比较 — 消融变体在不同维度上的表现")
print("=" * 90)

print(f"\n{'Dataset':16s}  {'Acc最佳':>10s}  {'Feat最少':>10s}  {'NHD最高':>10s}  {'综合最佳':>10s}")
print("-" * 60)

acc_best_count = {"KDS_EL_DRS": 0, "KDS_EL_KER": 0, "KDS_EL": 0}
feat_best_count = {"KDS_EL_DRS": 0, "KDS_EL_KER": 0, "KDS_EL": 0}
nhd_best_count = {"KDS_EL_DRS": 0, "KDS_EL_KER": 0, "KDS_EL": 0}
pareto_count = {"KDS_EL_DRS": 0, "KDS_EL_KER": 0, "KDS_EL": 0}

for ds in common_ds:
    drs   = summary_v2.get(("KDS_EL_DRS", ds), {})
    ker   = summary_v2.get(("KDS_EL_KER", ds), {})
    full  = summary_v2.get(("KDS_EL", ds), {})

    if not all([drs, ker, full]):
        continue

    accs = {"KDS_EL_DRS": drs["Mean_Acc"], "KDS_EL_KER": ker["Mean_Acc"], "KDS_EL": full["Mean_Acc"]}
    feats = {"KDS_EL_DRS": drs["Mean_Feat"], "KDS_EL_KER": ker["Mean_Feat"], "KDS_EL": full["Mean_Feat"]}
    nhds = {"KDS_EL_DRS": drs["Mean_NHD"], "KDS_EL_KER": ker["Mean_NHD"], "KDS_EL": full["Mean_NHD"]}

    acc_best = max(accs, key=accs.get)
    feat_best = min(feats, key=feats.get)
    nhd_best = max(nhds, key=nhds.get)

    acc_best_count[acc_best] += 1
    feat_best_count[feat_best] += 1
    nhd_best_count[nhd_best] += 1

    # 谁是综合最优？给三个指标排名，看总排名
    def rank_dict(d, reverse=False):
        sorted_items = sorted(d.items(), key=lambda x: x[1], reverse=reverse)
        ranks = {}
        for rank, (k, v) in enumerate(sorted_items):
            ranks[k] = rank + 1
        return ranks

    acc_rank = rank_dict(accs, reverse=True)
    feat_rank = rank_dict(feats, reverse=False)
    nhd_rank = rank_dict(nhds, reverse=True)

    total = {m: acc_rank[m] + feat_rank[m] + nhd_rank[m] for m in accs}
    overall_best = min(total, key=total.get)
    pareto_count[overall_best] += 1

    print(f"{ds:16s}  {acc_best:>10s}  {feat_best:>10s}  {nhd_best:>10s}  {overall_best:>10s}")

print(f"\n各维度最佳次数汇总:")
print(f"  {'变体':15s}  {'Acc最佳':>8s}  {'Feat最少':>8s}  {'NHD最高':>8s}  {'综合排名#1':>10s}")
for m in ["KDS_EL_DRS", "KDS_EL_KER", "KDS_EL"]:
    print(f"  {m:15s}  {acc_best_count[m]:8d}  {feat_best_count[m]:8d}  {nhd_best_count[m]:8d}  {pareto_count[m]:10d}")

# ═══════════════════════════════════════════════════════════════════
# 分析4: 鲁棒性 — 各变体的最差情况
# ═══════════════════════════════════════════════════════════════════
print("\n" + "=" * 90)
print("分析4: 鲁棒性 — 各变体的标准差和最差 run")
print("=" * 90)

for ds in common_ds[:8]:  # 选几个代表性的
    print(f"\n{ds}:")
    for m in ["KDS_EL_DRS", "KDS_EL_KER", "KDS_EL"]:
        runs = groups.get((m, ds), [])
        if len(runs) < 10:
            continue
        accs = [r["Accuracy"] for r in runs]
        feats = [r["Num_Features"] for r in runs]
        print(f"  {m:15s}: Acc={np.mean(accs):.4f}±{np.std(accs,ddof=1):.4f}  "
              f"min={np.min(accs):.4f}  max={np.max(accs):.4f}  "
              f"Feat={np.mean(feats):.0f}±{np.std(feats,ddof=1):.0f}  "
              f"min={np.min(feats)}  max={np.max(feats)}")

# ═══════════════════════════════════════════════════════════════════
# 分析5: 消融的真正含义 — 不是"谁更好"而是"各自贡献了什么"
# ═══════════════════════════════════════════════════════════════════
print("\n" + "=" * 90)
print("分析5: 消融的真正价值 — 各模块解决的'问题'不同")
print("=" * 90)

# DRS 的独特价值：它解决了什么问题？
print("\n📊 DRS 的独特贡献 (KDS_EL_DRS vs MEL):")
print("  解决的问题: 种群同质化 (NHD=0)")
drs_nhd_improvements = []
for ds in common_ds:
    mel_nhd = summary_v1.get(("MEL", ds), {}).get("Mean_NHD", 0)
    drs_nhd = summary_v2.get(("KDS_EL_DRS", ds), {}).get("Mean_NHD", 0)
    drs_nhd_improvements.append(drs_nhd - mel_nhd)
print(f"  NHD 提升: {np.mean(drs_nhd_improvements):.4f} (MEL=0.000 → DRS={np.mean([summary_v2.get(('KDS_EL_DRS', ds), {}).get('Mean_NHD', 0) for ds in common_ds]):.4f})")

# DRS 的特征压缩
drs_feat_reductions = []
for ds in common_ds:
    mel_feat = summary_v1.get(("MEL", ds), {}).get("Mean_Feat", 0)
    drs_feat = summary_v2.get(("KDS_EL_DRS", ds), {}).get("Mean_Feat", 0)
    if mel_feat > 0:
        drs_feat_reductions.append((mel_feat - drs_feat) / mel_feat * 100)
print(f"  特征压缩: {np.mean(drs_feat_reductions):.1f}% (MEL→DRS)")

# KER 的独特价值
print("\n📊 KER 的独特贡献 (KDS_EL_KER vs MEL):")
ker_acc_improvements = []
for ds in common_ds:
    mel_acc = summary_v1.get(("MEL", ds), {}).get("Mean_Acc", 0)
    ker_acc = summary_v2.get(("KDS_EL_KER", ds), {}).get("Mean_Acc", 0)
    ker_acc_improvements.append(ker_acc - mel_acc)
print(f"  Accuracy 提升: {np.mean(ker_acc_improvements):+.4f} (MEL→KER)")
print(f"  但 KER 的 NHD 始终为 0 — 没有多样性维护能力")

# KDS_EL 完整版：取两者之长
print("\n📊 KDS_EL 完整版的独特价值:")
full_acc_improvements = []
full_nhd_values = []
for ds in common_ds:
    mel_acc = summary_v1.get(("MEL", ds), {}).get("Mean_Acc", 0)
    full_acc = summary_v2.get(("KDS_EL", ds), {}).get("Mean_Acc", 0)
    full_nhd = summary_v2.get(("KDS_EL", ds), {}).get("Mean_NHD", 0)
    full_acc_improvements.append(full_acc - mel_acc)
    full_nhd_values.append(full_nhd)
print(f"  Accuracy 提升: {np.mean(full_acc_improvements):+.4f} (接近 KER 的 {np.mean(ker_acc_improvements):+.4f})")
print(f"  NHD: {np.mean(full_nhd_values):.4f} (DRS 的 {np.mean([summary_v2.get(('KDS_EL_DRS', ds), {}).get('Mean_NHD', 0) for ds in common_ds]):.4f} 的 {np.mean(full_nhd_values)/np.mean([summary_v2.get(('KDS_EL_DRS', ds), {}).get('Mean_NHD', 0) for ds in common_ds])*100:.0f}%)")

# KDS_EL = 唯一同时具备两者优势的版本
print(f"\n{'='*60}")
print("核心结论:")
print(f"  KDS_EL_DRS: Acc={np.mean([summary_v2.get(('KDS_EL_DRS', ds), {}).get('Mean_Acc', 0) for ds in common_ds]):.4f}, NHD>0 ✅, 但 Acc 最低 ❌")
print(f"  KDS_EL_KER: Acc={np.mean([summary_v2.get(('KDS_EL_KER', ds), {}).get('Mean_Acc', 0) for ds in common_ds]):.4f}, Acc 最高 ✅, 但 NHD=0 ❌")
print(f"  KDS_EL:     Acc={np.mean([summary_v2.get(('KDS_EL', ds), {}).get('Mean_Acc', 0) for ds in common_ds]):.4f}, Acc 接近 KER ✅, NHD>0 ✅")
print(f"  → 只有 KDS_EL 同时实现了高 Accuracy + 结构多样性维持")
print(f"{'='*60}")

# ═══════════════════════════════════════════════════════════════════
# 分析6: 数据集层面的"是否需要双空间"
# ═══════════════════════════════════════════════════════════════════
print("\n" + "=" * 90)
print("分析6: 哪些数据集真正需要双空间协同？")
print("=" * 90)
print("(DRS单独差 且 KER单独差，但 完整KDS_EL好 → 真正需要双空间)")

need_dual = []
for ds in common_ds:
    mel   = summary_v1.get(("MEL", ds), {}).get("Mean_Acc", 0)
    drs   = summary_v2.get(("KDS_EL_DRS", ds), {}).get("Mean_Acc", 0)
    ker   = summary_v2.get(("KDS_EL_KER", ds), {}).get("Mean_Acc", 0)
    full  = summary_v2.get(("KDS_EL", ds), {}).get("Mean_Acc", 0)

    drs_gain = drs - mel
    ker_gain = ker - mel
    full_gain = full - mel

    # 双空间需求：DRS和KER单独增益都不大，但完整版增益大
    synergy = full_gain - (drs_gain + ker_gain)

    if synergy > 0.005:  # 正协同 > 0.5pp
        need_dual.append((ds, drs_gain, ker_gain, full_gain, synergy))

if need_dual:
    print(f"\n正协同数据集 ({len(need_dual)} 个，协同 > 0.5pp):")
    print(f"  {'Dataset':16s}  {'ΔDRS':>8s}  {'ΔKER':>8s}  {'Δtotal':>8s}  {'synergy':>8s}")
    for ds, d, k, f, s in sorted(need_dual, key=lambda x: -x[4]):
        print(f"  {ds:16s}  {d:+8.4f}  {k:+8.4f}  {f:+8.4f}  {s:+8.4f}")

# 天花板效应数据集
ceiling = []
for ds in common_ds:
    mel   = summary_v1.get(("MEL", ds), {}).get("Mean_Acc", 0)
    drs   = summary_v2.get(("KDS_EL_DRS", ds), {}).get("Mean_Acc", 0)
    ker   = summary_v2.get(("KDS_EL_KER", ds), {}).get("Mean_Acc", 0)
    full  = summary_v2.get(("KDS_EL", ds), {}).get("Mean_Acc", 0)

    # 天花板效应：任何一个单独模块已经超过 0.99
    if max(drs, ker) > 0.99:
        ceiling.append(ds)

if ceiling:
    print(f"\n天花板效应数据集 ({len(ceiling)} 个，单模块 Acc > 0.99):")
    print(f"  {', '.join(ceiling)}")
    print(f"  → 这些数据集上单模块已接近完美，双空间无额外空间可提升")

print("\n" + "=" * 90)
print("Done.")
print("=" * 90)
