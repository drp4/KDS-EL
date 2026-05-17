# ════════════════════════════════════════════════════════════════════════════
# SOTA 对比实验：BPSO / SaWDE / FWPSO + MEL-KGEF（已有结果直接读取）
#
# 路径：
#   数据集 : /kaggle/input/datasets/eminz132/dataset/Datasets_part1/
#   已有结果: /kaggle/input/datasets/eminz132/resultds1/results/results_plan_b_merged.csv
#
# 输出：
#   /kaggle/working/results_sota.csv       (新跑方法的结果)
#   /kaggle/working/results_all_merged.csv (全部5个方法合并)
#
# 断点续跑：每个 run 跑完立即写入 CSV，重启后自动跳过已完成
# ════════════════════════════════════════════════════════════════════════════

import os, csv, warnings
import numpy as np
from time import time
from sklearn.neighbors import KNeighborsClassifier
from sklearn.model_selection import KFold
warnings.filterwarnings('ignore')
np.seterr(all='ignore')

# ── 路径 ────────────────────────────────────────────────────────────────────
DATA_DIR   = '/kaggle/input/datasets/eminz132/dataset/Datasets_part1'
MERGED_CSV = '/kaggle/input/datasets/eminz132/resultds1/results/results_plan_b_merged.csv'
OUT_DIR    = '/kaggle/working'
SOTA_CSV   = os.path.join(OUT_DIR, 'results_sota.csv')
ALL_CSV    = os.path.join(OUT_DIR, 'results_all_merged.csv')

# ── 配置 ────────────────────────────────────────────────────────────────────
NUM_RUNS  = 10
SEED_BASE = 42
DATASETS  = [
    'Adenoma','ALL_AML','ALL3','ALL4','CNS',
    'Colon','DLBCL','Leukaemia','Lymphoma','Stroke'
]
OPTS = {'k': 3, 'N': 20, 'T': 100, 'thres': 0.6, 'ws': [0.9, 0.1]}
CSV_FIELDS = ['Version','Dataset','Run','Accuracy','Num_Features','Avg_NHD','Time_sec']

# ── 数据加载（与你原来一致）─────────────────────────────────────────────────
LABEL_START_COL = {'CNS': 3, 'MLL': 2}
DATA_START_COL  = {'CNS': 3, 'MLL': 2}

def load_dataset(p_name):
    fp = os.path.join(DATA_DIR, f'{p_name}.txt')
    if not os.path.exists(fp):
        raise FileNotFoundError(f"找不到: {fp}")
    with open(fp, 'r') as f:
        lines = f.readlines()
    lbl_start  = LABEL_START_COL.get(p_name, 1)
    data_start = DATA_START_COL.get(p_name, 1)
    header = lines[0].strip().split('\t')
    sample_labels_raw = [h for h in header[lbl_start:] if h.strip() != '']
    unique_classes = sorted(set(sample_labels_raw))
    label_map = {cls: idx for idx, cls in enumerate(unique_classes)}
    label = np.array([label_map[s] for s in sample_labels_raw], dtype=float)
    n_samples = len(label)
    data_rows = []
    for line in lines[1:]:
        parts = line.rstrip('\n').split('\t')
        val_parts = [p for p in parts[data_start:] if p.strip() != '']
        if len(val_parts) != n_samples:
            continue
        try:
            data_rows.append([float(x) for x in val_parts])
        except ValueError:
            continue
    feat = np.array(data_rows, dtype=float).T
    assert feat.shape[0] == n_samples
    return feat, label

# ── KNN 5-fold（与你原来完全一致）───────────────────────────────────────────
def jwrapper_KNN(sFeat, label, opts):
    k  = opts.get('k', 3)
    kf = KFold(n_splits=5, shuffle=False)
    acc_list = []
    for tr, va in kf.split(sFeat):
        mdl = KNeighborsClassifier(n_neighbors=k)
        mdl.fit(sFeat[tr], label[tr])
        acc_list.append(np.mean(mdl.predict(sFeat[va]) == label[va]))
    return 1.0 - np.mean(acc_list)

def jFitnessFunction(feat, label, mask, opts):
    ws = opts.get('ws', [0.9, 0.1])
    nf = int(np.sum(mask))
    if nf < 3:
        return 1.0 + (3 - nf) * 0.1
    err = jwrapper_KNN(feat[:, mask], label, opts)
    return ws[0] * err + ws[1] * (nf / feat.shape[1])

# ════════════════════════════════════════════════════════════════════════════
# BPSO — Binary PSO (Kennedy & Eberhart 1997 经典版)
# ════════════════════════════════════════════════════════════════════════════
def run_BPSO(feat, label, opts):
    N = opts.get('N', 20); T = opts.get('T', 100)
    thres = opts.get('thres', 0.5); dim = feat.shape[1]
    w = 0.9; c1 = c2 = 2.0
    Vmax = 6.0   # sigmoid 饱和前的标准截断值

    X = (np.random.rand(N, dim) < 0.5).astype(float)
    V = np.zeros((N, dim))

    fit = np.array([jFitnessFunction(feat, label, X[i].astype(bool), opts) for i in range(N)])
    Xpb = X.copy(); fitP = fit.copy()
    gbest = np.argmin(fitP); Xgb = Xpb[gbest].copy(); fitG = fitP[gbest]

    curve = np.zeros(T + 1); curve[0] = fitG

    for t in range(1, T + 1):
        r1, r2 = np.random.rand(N, dim), np.random.rand(N, dim)
        V = w * V + c1 * r1 * (Xpb - X) + c2 * r2 * (Xgb - X)
        V = np.clip(V, -Vmax, Vmax)
        # S-shape transfer
        prob = 1.0 / (1.0 + np.exp(-V))
        X = (np.random.rand(N, dim) < prob).astype(float)

        for i in range(N):
            f = jFitnessFunction(feat, label, X[i].astype(bool), opts)
            if f < fitP[i]:
                Xpb[i] = X[i].copy(); fitP[i] = f
            if f < fitG:
                Xgb = X[i].copy(); fitG = f
        curve[t] = fitG

    nf = int(np.sum(Xgb))
    return {'fitG': fitG, 'nf': nf, 'curve': curve}

# ════════════════════════════════════════════════════════════════════════════
# SaWDE — Self-adaptive Weighted DE for FS
# 基于：Wang et al. IEEE TEVC 2021
# 核心：三种 DE 变异策略自适应加权，连续空间 sigmoid 二值化
# ════════════════════════════════════════════════════════════════════════════
def run_SaWDE(feat, label, opts):
    N = opts.get('N', 20); T = opts.get('T', 100)
    thres = opts.get('thres', 0.5); dim = feat.shape[1]

    # 初始种群（连续）
    X = np.random.uniform(0, 1, (N, dim))
    fit = np.array([jFitnessFunction(feat, label, X[i] > thres, opts) for i in range(N)])

    # 三种策略的初始权重（等权）
    w_strat = np.ones(3) / 3.0
    # 每个策略的 F 和 CR 历史（自适应）
    F_hist  = [0.5, 0.5, 0.5]
    CR_hist = [0.5, 0.5, 0.5]

    fitG = np.min(fit); Xgb = X[np.argmin(fit)].copy()
    curve = np.zeros(T + 1); curve[0] = fitG

    for t in range(1, T + 1):
        # 归一化权重
        w_norm = w_strat / (w_strat.sum() + 1e-12)
        success = np.zeros(3); count = np.zeros(3)

        X_new = X.copy()
        for i in range(N):
            # 按权重选策略
            s = np.random.choice(3, p=w_norm)
            F  = np.clip(np.random.normal(F_hist[s],  0.1), 0.1, 1.0)
            CR = np.clip(np.random.normal(CR_hist[s], 0.1), 0.0, 1.0)

            # 随机选 3 个不同个体
            idx = list(range(N)); idx.remove(i)
            r1, r2, r3 = np.random.choice(idx, 3, replace=False)

            # 三种变异策略
            if s == 0:   # DE/rand/1
                mutant = X[r1] + F * (X[r2] - X[r3])
            elif s == 1: # DE/current-to-best/1
                mutant = X[i] + F * (Xgb - X[i]) + F * (X[r1] - X[r2])
            else:        # DE/best/1
                mutant = Xgb + F * (X[r1] - X[r2])

            mutant = np.clip(mutant, 0, 1)

            # 二项交叉
            mask_cross = np.random.rand(dim) < CR
            if not mask_cross.any():
                mask_cross[np.random.randint(dim)] = True
            trial = np.where(mask_cross, mutant, X[i])

            # 选择
            f_trial = jFitnessFunction(feat, label, trial > thres, opts)
            if f_trial <= fit[i]:
                X_new[i] = trial; fit[i] = f_trial
                success[s] += 1
                # 更新历史 F/CR（简单移动平均）
                F_hist[s]  = 0.9 * F_hist[s]  + 0.1 * F
                CR_hist[s] = 0.9 * CR_hist[s] + 0.1 * CR
                if f_trial < fitG:
                    fitG = f_trial; Xgb = trial.copy()
            count[s] += 1

        # 更新策略权重（基于成功率）
        sr = np.where(count > 0, success / count, 0.0)
        w_strat = 0.9 * w_strat + 0.1 * (sr + 0.01)
        w_strat /= w_strat.sum()
        X = X_new
        curve[t] = fitG

    nf = int(np.sum(Xgb > thres))
    return {'fitG': fitG, 'nf': nf, 'curve': curve}

# ════════════════════════════════════════════════════════════════════════════
# FWPSO — Feature Weighting PSO
# 基于：Wang et al. IEEE TCYB 2022
# 核心：用特征权重矩阵引导第二子群搜索（与 MEL 同类，但无多任务）
# ════════════════════════════════════════════════════════════════════════════
def run_FWPSO(feat, label, opts):
    N = opts.get('N', 20); T = opts.get('T', 100)
    thres = opts.get('thres', 0.5); dim = feat.shape[1]
    c1 = c2 = 2.0; w = 0.9; Vmax = 0.5

    weight = np.zeros(dim)
    X = np.random.uniform(0, 1, (N, dim))
    V = np.zeros((N, dim))

    fit = np.array([jFitnessFunction(feat, label, X[i] > thres, opts) for i in range(N)])
    Xpb = X.copy(); fitP = fit.copy()
    gbest = np.argmin(fitP); Xgb = Xpb[gbest].copy(); fitG = fitP[gbest]

    curve = np.zeros(T + 1); curve[0] = fitG

    for t in range(1, T + 1):
        for i in range(N):
            r1, r2 = np.random.rand(dim), np.random.rand(dim)
            V[i] = w * V[i] + c1 * r1 * (Xpb[i] - X[i]) + c2 * r2 * (Xgb - X[i])
            V[i] = np.clip(V[i], -Vmax, Vmax)

            # 用特征权重调整搜索方向（FWPSO 核心）
            vf = np.maximum(weight, 0); sv = vf.sum()
            if sv > 0 and np.random.rand() < 0.3:
                prob = vf / sv
                X[i] = (np.random.rand(dim) < prob).astype(float)
            else:
                X[i] = np.clip(X[i] + V[i], 0, 1)

            f = jFitnessFunction(feat, label, X[i] > thres, opts)
            fv_n = X[i] > thres; fv_o = Xpb[i] > thres
            if f < fitP[i]:
                inc = fitP[i] - f; change = np.logical_xor(fv_n, fv_o)
                weight[change & (fv_n > fv_o)] += inc
                weight[change & (fv_n < fv_o)] -= inc
                Xpb[i] = X[i].copy(); fitP[i] = f
            if f < fitG:
                Xgb = X[i].copy(); fitG = f
        curve[t] = fitG

    nf = int(np.sum(Xgb > thres))
    return {'fitG': fitG, 'nf': nf, 'curve': curve}

# ════════════════════════════════════════════════════════════════════════════
# 断点续跑工具
# ════════════════════════════════════════════════════════════════════════════
def ensure_header(path):
    if not os.path.exists(path):
        with open(path, 'w', newline='') as f:
            csv.DictWriter(f, fieldnames=CSV_FIELDS).writeheader()

def load_done(path):
    done = set()
    if not os.path.exists(path):
        return done
    with open(path, 'r', newline='') as f:
        for row in csv.DictReader(f):
            try:
                done.add((row['Version'], row['Dataset'], int(row['Run'])))
            except Exception:
                pass
    return done

def append_row(path, row):
    with open(path, 'a', newline='') as f:
        csv.DictWriter(f, fieldnames=CSV_FIELDS).writerow(row)

# ════════════════════════════════════════════════════════════════════════════
# 主循环：跑 BPSO / SaWDE / FWPSO
# ════════════════════════════════════════════════════════════════════════════
RUNNERS = {
    'BPSO':  run_BPSO,
    'SaWDE': run_SaWDE,
    'FWPSO': run_FWPSO,
}

ensure_header(SOTA_CSV)
done = load_done(SOTA_CSV)

total = len(RUNNERS) * len(DATASETS) * NUM_RUNS
print(f"总任务数：{total}，已完成：{len(done)}，剩余：{total - len(done)}\n")

for ver, runner in RUNNERS.items():
    for ds in DATASETS:
        fp = os.path.join(DATA_DIR, f'{ds}.txt')
        if not os.path.exists(fp):
            print(f"⚠️ 跳过 {ds}（文件不存在）")
            continue
        feat_label = None
        for run in range(NUM_RUNS):
            if (ver, ds, run) in done:
                print(f"  ⏭ {ver:8s} | {ds:12s} | run {run:2d} — 跳过")
                continue
            if feat_label is None:
                feat, label = load_dataset(ds)
                feat_label = (feat, label)
                print(f"\n{'='*65}\n{ver} | {ds} (n={feat.shape[0]}, d={feat.shape[1]})\n{'='*65}")
            else:
                feat, label = feat_label

            np.random.seed(SEED_BASE + run * 37)
            t0 = time()
            res = runner(feat, label, OPTS)
            elapsed = time() - t0

            acc = 1.0 - res['fitG']
            nf  = res['nf']

            append_row(SOTA_CSV, {
                'Version': ver, 'Dataset': ds, 'Run': run,
                'Accuracy': f"{acc:.6f}",
                'Num_Features': nf,
                'Avg_NHD': f"{0.0:.6f}",
                'Time_sec': f"{elapsed:.2f}",
            })
            print(f"  ✓ {ver:8s} | {ds:12s} | run {run:2d} | "
                  f"Acc={acc:.4f}  Feat={nf:5d}  t={elapsed:.1f}s")

print(f"\n✅ SOTA 新方法运行完成：{SOTA_CSV}")

# ════════════════════════════════════════════════════════════════════════════
# 合并：已有结果 + SOTA 新结果
# ════════════════════════════════════════════════════════════════════════════
def read_csv_rows(path):
    rows = []
    if not os.path.exists(path):
        print(f"⚠️ 找不到：{path}")
        return rows
    with open(path, 'r', newline='') as f:
        for row in csv.DictReader(f):
            try:
                rows.append({
                    'Version': row['Version'],
                    'Dataset': row['Dataset'],
                    'Run': int(row['Run']),
                    'Accuracy': float(row['Accuracy']),
                    'Num_Features': float(row['Num_Features']),
                    'Avg_NHD': float(row['Avg_NHD']),
                    'Time_sec': float(row['Time_sec']),
                })
            except Exception:
                pass
    return rows

base_rows = read_csv_rows(MERGED_CSV)
sota_rows = read_csv_rows(SOTA_CSV)

seen = set(); merged = []
for row in base_rows + sota_rows:
    key = (row['Version'], row['Dataset'], row['Run'])
    if key in seen:
        continue
    seen.add(key); merged.append(row)

with open(ALL_CSV, 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=CSV_FIELDS)
    w.writeheader()
    for r in merged:
        w.writerow({
            'Version': r['Version'], 'Dataset': r['Dataset'], 'Run': r['Run'],
            'Accuracy': f"{r['Accuracy']:.6f}",
            'Num_Features': int(r['Num_Features']),
            'Avg_NHD': f"{r['Avg_NHD']:.6f}",
            'Time_sec': f"{r['Time_sec']:.2f}",
        })

print(f"🎉 最终合并文件：{ALL_CSV}")
print(f"包含版本：{sorted(set(r['Version'] for r in merged))}")
print(f"总行数（runs）：{len(merged)}")