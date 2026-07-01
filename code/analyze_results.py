"""分析消融实验结果，判断新增算子是否有效"""
import csv

with open(r'F:\zym\KDS-EL\output\formal_experiment_20260627_211133\results_detail.csv') as f:
    rows = list(csv.DictReader(f))

for r in rows:
    r['Accuracy'] = float(r['Accuracy'])
    r['Num_Features'] = int(r['Num_Features'])
    r['Time_sec'] = float(r.get('Time_sec', 0))

datasets = sorted(set(r['Dataset'] for r in rows))
methods = ['MEL', 'KDS_EL_DRS', 'KDS_EL_KER', 'KDS_EL']
short = {'MEL': 'MEL', 'KDS_EL_DRS': 'DRS', 'KDS_EL_KER': 'KER', 'KDS_EL': 'KDS'}

# Per dataset: best across seeds for each method
header = f"{'Dataset':<12s}"
for m in methods:
    header += f" {short[m]+'_Acc':>8s}"
header += " |"
for m in methods:
    header += f" {short[m]+'_Ft':>6s}"
print(header)
print('-' * 95)

all_best = {}
for ds in datasets:
    best = {}
    for m in methods:
        mrows = [r for r in rows if r['Method'] == m and r['Dataset'] == ds]
        best[m] = max(mrows, key=lambda x: (x['Accuracy'], -x['Num_Features']))
    all_best[ds] = best
    
    line = f"{ds:<12s}"
    for m in methods:
        line += f" {best[m]['Accuracy']:>8.4f}"
    line += " |"
    for m in methods:
        line += f" {best[m]['Num_Features']:>6d}"
    print(line)

print()

# Win / tie / loss vs MEL
for label, target in [('KDS_EL_KER', 'KDS_EL_KER'), ('KDS_EL', 'KDS_EL'), ('KDS_EL_DRS', 'KDS_EL_DRS')]:
    w = sum(1 for ds in datasets if all_best[ds][target]['Accuracy'] > all_best[ds]['MEL']['Accuracy'] + 0.005)
    t = sum(1 for ds in datasets if abs(all_best[ds][target]['Accuracy'] - all_best[ds]['MEL']['Accuracy']) <= 0.005)
    l = sum(1 for ds in datasets if all_best[ds][target]['Accuracy'] < all_best[ds]['MEL']['Accuracy'] - 0.005)
    print(f'{label} vs MEL (阈值0.005):  胜 {w:2d} / 18   平 {t:2d} / 18   负 {l:2d} / 18')

# Mean accuracy delta
print()
for label, target in [('KDS_EL_KER', 'KDS_EL_KER'), ('KDS_EL', 'KDS_EL'), ('KDS_EL_DRS', 'KDS_EL_DRS')]:
    deltas = [all_best[ds][target]['Accuracy'] - all_best[ds]['MEL']['Accuracy'] for ds in datasets]
    avg_delta = sum(deltas) / len(deltas)
    print(f'{label}: 平均 Acc 提升 = {avg_delta:+.4f}')

# Feature reduction
print()
for label, target in [('KDS_EL_KER', 'KDS_EL_KER'), ('KDS_EL', 'KDS_EL'), ('KDS_EL_DRS', 'KDS_EL_DRS')]:
    abs_deltas = []
    mel_large = []  # MEL选>100个特征的数据集
    mel_small = []  # MEL选≤100个特征的数据集
    for ds in datasets:
        mf = all_best[ds]['MEL']['Num_Features']
        tf = all_best[ds][target]['Num_Features']
        abs_deltas.append(mf - tf)
        if mf > 100:
            mel_large.append((ds, mf, tf))
        else:
            mel_small.append((ds, mf, tf))
    avg_reduction = sum(abs_deltas) / len(abs_deltas)
    print(f'{label}:')
    print(f'  全量:   平均特征减少={avg_reduction:.0f} | 减少的数据集: {sum(1 for d in abs_deltas if d>0)}/18')
    if mel_large:
        ratios_large = [tf/mf for _, mf, tf in mel_large]
        print(f'  MEL特征>100: 平均特征比={sum(ratios_large)/len(ratios_large):.2%} (n={len(mel_large)})')
    if mel_small:
        print(f'  MEL特征≤100: 特征变化:')
        for ds, mf, tf in mel_small:
            print(f'    {ds:<12s} {mf:>5d}→{tf:<5d} ({tf/mf*100-100:+.0f}%)')

# 各方法在哪些数据集上失败
print()
for label, target in [('KDS_EL_KER', 'KDS_EL_KER'), ('KDS_EL', 'KDS_EL'), ('KDS_EL_DRS', 'KDS_EL_DRS')]:
    losses = [(ds, all_best[ds][target]['Accuracy'], all_best[ds]['MEL']['Accuracy'])
              for ds in datasets if all_best[ds][target]['Accuracy'] < all_best[ds]['MEL']['Accuracy'] - 0.005]
    print(f'{label} 负于 MEL 的数据集:')
    for ds, tacc, macc in losses:
        print(f'  {ds:<12s} {label}={tacc:.4f}  MEL={macc:.4f}  Δ={tacc-macc:+.4f}')

# 按 MEL 特征数分群
print()
print("=== 按 MEL 特征数分层分析 ===")
mel_feat_sorted = sorted([(ds, all_best[ds]['MEL']['Num_Features']) for ds in datasets], key=lambda x: x[1])
print("MEL 特征数排序:", ', '.join(f'{ds}={nf}' for ds, nf in mel_feat_sorted))

print()
for group_name, threshold in [('MEL选择>100特征(高维)', 100), ('MEL选择≤100特征(低维)', 0)]:
    group = [ds for ds in datasets if all_best[ds]['MEL']['Num_Features'] > threshold] if threshold > 0 else \
            [ds for ds in datasets if all_best[ds]['MEL']['Num_Features'] <= 100]
    if not group:
        continue
    print(f'--- {group_name} (n={len(group)}) ---')
    for label, target in [('KDS_EL_KER', 'KDS_EL_KER'), ('KDS_EL', 'KDS_EL'), ('KDS_EL_DRS', 'KDS_EL_DRS')]:
        w = sum(1 for ds in group if all_best[ds][target]['Accuracy'] > all_best[ds]['MEL']['Accuracy'] + 0.005)
        l = sum(1 for ds in group if all_best[ds][target]['Accuracy'] < all_best[ds]['MEL']['Accuracy'] - 0.005)
        deltas = [all_best[ds][target]['Accuracy'] - all_best[ds]['MEL']['Accuracy'] for ds in group]
        avg = sum(deltas)/len(deltas)
        feat_ratios = [all_best[ds][target]['Num_Features'] / max(all_best[ds]['MEL']['Num_Features'], 1) for ds in group]
        avg_fr = sum(feat_ratios)/len(feat_ratios)
        print(f'  {label:<12s}: 胜{w:2d}/负{l:2d}  ΔAcc={avg:+.4f}  特征比={avg_fr:.2%}')

# Time comparison
print()
for label, target in [('KDS_EL_KER', 'KDS_EL_KER'), ('KDS_EL', 'KDS_EL'), ('KDS_EL_DRS', 'KDS_EL_DRS')]:
    ratios = []
    for ds in datasets:
        mt = float(all_best[ds]['MEL'].get('Time_sec', 0))
        tt = float(all_best[ds][target].get('Time_sec', 0))
        ratios.append(tt / mt if mt > 0 else 1.0)
    print(f'{label}: 平均耗时比={sum(ratios)/len(ratios):.2%}')
