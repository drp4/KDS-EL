"""
KDS-EL 共享工具函数
====================
包括：数据加载、KNN 适应度评估、种群多样性 (NHD)、
非支配排序 (EMDO/DRS)、精英翻转 (KGEF/KER)、断点续跑辅助。
"""
import os, re, csv, warnings
import numpy as np
from time import time
from sklearn.neighbors import KNeighborsClassifier
from sklearn.model_selection import StratifiedKFold
from sklearn.preprocessing import LabelEncoder
from scipy.io import loadmat

warnings.filterwarnings("ignore")
np.seterr(all="ignore")

# ════════════════════════════════════════════════════════════════════════
# 1) 数据加载
# ════════════════════════════════════════════════════════════════════════

def srbct_prefix(col):
    """SRBCT 列名前缀提取：'BL-C1' → 'BL', 'RMS.4' → 'RMS', 'EWS-T11' → 'EWS'"""
    s = re.sub(r'\.\d+$', '', col.strip())
    return s.split('-')[0]


def load_txt(name, data_dir):
    """加载 .txt 格式基因表达数据集。"""
    from config import SPECIAL_COL, SRBCT_KEEP
    fp = os.path.join(data_dir, f"{name}.txt")
    if not os.path.exists(fp):
        raise FileNotFoundError(f"Not found: {fp}")

    ls = ds = SPECIAL_COL.get(name, 1)
    lines = open(fp, encoding="utf-8", errors="replace").read().splitlines()
    header = lines[0].strip().split("\t")
    sample_names = [h for h in header[ls:] if h.strip()]

    if name == "SRBCT":
        raw_labels = [srbct_prefix(h) for h in sample_names]
        keep_mask  = [lb in SRBCT_KEEP for lb in raw_labels]
        labels_raw = [lb for lb, k in zip(raw_labels, keep_mask) if k]
    else:
        keep_mask  = [True] * len(sample_names)
        labels_raw = sample_names

    classes = sorted(set(labels_raw))
    cmap    = {c: i for i, c in enumerate(classes)}
    y       = np.array([cmap[s] for s in labels_raw], dtype=int)
    n       = len(y)
    keep_cols = [i for i, k in enumerate(keep_mask) if k]

    rows = []
    for line in lines[1:]:
        parts = line.rstrip("\n").split("\t")
        vals  = [p for p in parts[ds:] if p.strip()]
        if len(vals) != len(sample_names):
            continue
        try:
            rows.append([float(vals[i]) for i in keep_cols])
        except ValueError:
            continue

    X = np.array(rows, dtype=float).T
    assert X.shape[0] == n, f"{name}: X.shape={X.shape} but n={n}"
    return X, y


def load_mat(name, data_dirs):
    """加载 .mat 格式数据集（ASU 标准格式）。"""
    for folder in data_dirs:
        fp = os.path.join(folder, f"{name}.mat")
        if os.path.exists(fp):
            break
    else:
        raise FileNotFoundError(f"Not found: {name}.mat")

    data = loadmat(fp)
    X = next((data[k].astype(float)
              for k in ["X", "data", "fea", "features"]
              if k in data and isinstance(data[k], np.ndarray)), None)
    Y = next((data[k].ravel().astype(int)
              for k in ["Y", "label", "gnd", "labels", "targets"]
              if k in data and isinstance(data[k], np.ndarray)), None)

    if X is None or Y is None:
        raise ValueError(f"{name}.mat: cannot find X/Y. Keys={list(data.keys())}")

    from scipy.sparse import issparse
    if issparse(X):
        X = X.toarray()

    return X, Y - Y.min()


def load_dataset(name, data_dir_txt, data_dir_mat):
    """统一数据加载入口：自动判断 txt/mat 格式，标签重编码 + 健康检查。"""
    from config import MAT_DATASETS
    if name in MAT_DATASETS:
        X, y = load_mat(name, [data_dir_mat, data_dir_txt])
    else:
        txt_fp  = os.path.join(data_dir_txt, f"{name}.txt")
        mat_fp1 = os.path.join(data_dir_txt, f"{name}.mat")
        mat_fp2 = os.path.join(data_dir_mat, f"{name}.mat")
        if os.path.exists(txt_fp):
            X, y = load_txt(name, data_dir_txt)
        elif os.path.exists(mat_fp1) or os.path.exists(mat_fp2):
            X, y = load_mat(name, [data_dir_mat, data_dir_txt])
        else:
            raise FileNotFoundError(f"Cannot find {name}.txt or {name}.mat")

    y = LabelEncoder().fit_transform(y)

    n_classes = len(np.unique(y))
    if n_classes == len(y):
        raise ValueError(
            f"{name}: n_classes({n_classes}) == n_samples — 标签未正确解析！")
    if n_classes < 2:
        raise ValueError(f"{name}: 只有 {n_classes} 个类，无法分类")

    return X, y


def load_datasets(datasets, data_dir_txt, data_dir_mat, verbose=True):
    """批量加载数据集，返回 {name: (X, y)} 字典。"""
    loaded = {}
    for ds in datasets:
        try:
            X, y = load_dataset(ds, data_dir_txt, data_dir_mat)
            loaded[ds] = (X, y)
            if verbose:
                uc, cc = np.unique(y, return_counts=True)
                print(f"  ✓ {ds:12s}: shape={X.shape}  n_classes={len(uc)}")
        except Exception as e:
            print(f"  ✗ {ds:12s}: {e}")
    return loaded


# ════════════════════════════════════════════════════════════════════════
# 1.5) 互信息初始化辅助
# ════════════════════════════════════════════════════════════════════════

def compute_mi_scores(X, y):
    """计算每个特征与标签的互信息，归一化到 [0, 1]。

    用于种群初始化引导：高 MI 特征更可能被初始化为选中状态，
    解决知识权重冷启动问题。
    """
    from sklearn.feature_selection import mutual_info_classif
    mi = mutual_info_classif(X, y, random_state=42)
    mi = np.nan_to_num(mi, nan=0.0)
    if mi.max() > mi.min():
        mi = (mi - mi.min()) / (mi.max() - mi.min())
    return mi


# ════════════════════════════════════════════════════════════════════════

def jwrapper(X_sub, y, opts):
    """StratifiedKFold KNN 误差率。n_splits 动态调整防止小样本崩溃。"""
    min_class = int(np.min(np.bincount(y)))
    n_splits  = min(opts["cv_splits"], min_class)
    if n_splits < 2:
        return 1.0

    skf = StratifiedKFold(
        n_splits=n_splits,
        shuffle=opts["cv_shuffle"],
        random_state=opts["cv_random_state"])
    acc = []
    for tr, te in skf.split(X_sub, y):
        clf = KNeighborsClassifier(n_neighbors=opts["k"])
        clf.fit(X_sub[tr], y[tr])
        acc.append((clf.predict(X_sub[te]) == y[te]).mean())
    return 1.0 - float(np.mean(acc))


def jFitness(X, y, mask, opts):
    """综合适应度 = w_err × error + w_feat × (nf / n_total)。"""
    nf = int(mask.sum())
    if nf < 3:
        return 1.0 + (3 - nf) * 0.1
    return opts["ws"][0] * jwrapper(X[:, mask], y, opts) \
           + opts["ws"][1] * (nf / X.shape[1])


# ════════════════════════════════════════════════════════════════════════
# 3) 种群多样性指标 (NHD)
# ════════════════════════════════════════════════════════════════════════

def pairwise_nhd(X_bin):
    """计算种群内所有个体对的归一化汉明距离 (NHD)。"""
    X_bin = X_bin.astype(np.float32)
    inter = X_bin @ X_bin.T
    sums  = X_bin.sum(axis=1)
    union = sums[:, None] + sums[None, :] - inter
    ahd   = sums[:, None] + sums[None, :] - 2.0 * inter
    return ahd / np.maximum(union, 1.0)


# ════════════════════════════════════════════════════════════════════════
# 4) EMDO — 基于非支配排序的多样性保持选择 (DRS)
# ════════════════════════════════════════════════════════════════════════

def fast_nds(obj):
    """快速非支配排序 (Fast Non-Dominated Sorting)。"""
    N = obj.shape[0]
    dc = np.zeros(N, dtype=int)
    ds = [[] for _ in range(N)]
    fronts = [[]]
    for i in range(N):
        for j in range(N):
            if i == j:
                continue
            if np.all(obj[i] <= obj[j]) and np.any(obj[i] < obj[j]):
                ds[i].append(j)
            elif np.all(obj[j] <= obj[i]) and np.any(obj[j] < obj[i]):
                dc[i] += 1
        if dc[i] == 0:
            fronts[0].append(i)
    cf = 0
    while fronts[cf]:
        nxt = []
        for i in fronts[cf]:
            for j in ds[i]:
                dc[j] -= 1
                if dc[j] == 0:
                    nxt.append(j)
        cf += 1
        fronts.append(nxt)
    if not fronts[-1]:
        fronts.pop()
    return fronts


def crowding_dist(obj, front):
    """计算拥挤距离。"""
    cd = {i: 0.0 for i in front}
    for m in range(obj.shape[1]):
        sf = sorted(front, key=lambda i: obj[i, m])
        cd[sf[0]] = cd[sf[-1]] = np.inf
        span = obj[sf[-1], m] - obj[sf[0], m]
        if span == 0:
            continue
        for k in range(1, len(front) - 1):
            cd[sf[k]] += (obj[sf[k+1], m] - obj[sf[k-1], m]) / span
    return cd


def emdo_select(pool_fit, nhd_matrix, N, alpha_cd):
    """
    EMDO 选择：基于非支配排序 + 拥挤距离 + NHD 的混合选择。
    alpha_cd 控制拥挤距离 vs NHD 的权重，随时间变化。
    """
    pool_nhd = nhd_matrix.mean(axis=1)
    obj = np.column_stack([pool_fit, -pool_nhd])
    fronts = fast_nds(obj)
    selected = []
    for front in fronts:
        if len(selected) + len(front) <= N:
            selected.extend(front)
        else:
            needed = N - len(selected)
            cd = crowding_dist(obj, front)
            cd_v = np.array([cd[i] for i in front])
            fin = cd_v[np.isfinite(cd_v)]
            mc = np.max(fin) if len(fin) > 0 else 0.0
            cd_n = np.where(np.isfinite(cd_v), (cd_v / mc if mc > 0 else 0.0), 1.0)
            hd_v = np.array([pool_nhd[i] for i in front])
            mh = np.max(hd_v)
            hd_n = hd_v / mh if mh > 0 else np.zeros(len(front))
            score = alpha_cd * cd_n + (1.0 - alpha_cd) * hd_n
            order = np.argsort(-score)
            selected.extend([front[order[k]] for k in range(needed)])
            break
    return np.array(selected)


# ════════════════════════════════════════════════════════════════════════
# 5) KGEF — 知识引导的精英微调 (KER)
# ════════════════════════════════════════════════════════════════════════

def kgef_flip(weight, elite_bin, flip_count, rand_p):
    """
    KGEF 精英翻转：10% 概率随机翻转，90% 概率基于权重得分选择翻转特征。
    """
    mutant = elite_bin.copy()
    dim = len(mutant)
    if np.random.rand() < rand_p:
        fi = np.random.choice(dim, flip_count, replace=False)
    else:
        sc = np.where(elite_bin == 0, weight, -weight)
        sc += np.random.normal(0.0, np.std(weight) + 1e-5, dim)
        fi = np.argsort(-sc)[:flip_count]
    mutant[fi] = 1 - mutant[fi]
    return mutant


# ════════════════════════════════════════════════════════════════════════
# 6) 断点续跑辅助
# ════════════════════════════════════════════════════════════════════════

def ensure_csv_header(path, fields):
    """确保 CSV 文件存在并包含表头。"""
    if not os.path.exists(path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", newline="") as f:
            csv.DictWriter(f, fieldnames=fields).writeheader()


def load_completed(path):
    """读取已完成任务集合 {(Version, Dataset, Run)}。"""
    done = set()
    if not os.path.exists(path):
        return done
    with open(path, newline="") as f:
        for r in csv.DictReader(f):
            try:
                done.add((r["Version"], r["Dataset"], int(r["Run"])))
            except Exception:
                pass
    return done


def append_row(path, fields, row):
    """追加一行结果到 CSV。"""
    with open(path, "a", newline="") as f:
        csv.DictWriter(f, fieldnames=fields).writerow(row)


def run_experiment(
    version, runner_fn, datasets, opts, num_runs, seed_base,
    csv_path, curves_dir, csv_fields, data_dir_txt, data_dir_mat,
    max_tasks=None, post_process=None,
):
    """
    通用实验运行器。

    Parameters
    ----------
    version : str               方法名称
    runner_fn : callable       算法函数，签名: fn(X, y, opts) -> dict
    datasets : list[str]       数据集名称列表
    opts : dict                算法参数
    num_runs : int             每个数据集运行次数
    seed_base : int            随机种子基值
    csv_path : str             结果 CSV 路径
    curves_dir : str           npy 曲线输出目录
    csv_fields : list[str]     CSV 字段名
    data_dir_txt : str         txt 数据目录
    data_dir_mat : str         mat 数据目录
    max_tasks : int or None    每次最多跑多少任务（断点续跑）
    post_process : callable or None
        后处理函数，签名: fn(res, X, y, opts) -> dict
        可用于在算法返回结果后附加额外指标

    Returns
    -------
    int    本次新运行的任务数
    """
    ensure_csv_header(csv_path, csv_fields)
    done = load_completed(csv_path)

    total_scope = len(datasets) * num_runs
    done_this   = sum(1 for (v, _, _) in done if v == version)
    tasks_run   = 0

    print(f"\n{'='*60}")
    print(f"Version    : {version}")
    print(f"Datasets   : {len(datasets)} × {num_runs} runs = {total_scope} tasks")
    print(f"Completed  : {done_this} / {total_scope}")
    print(f"CSV  → {csv_path}")
    print(f"NPY  → {curves_dir}")
    print(f"{'='*60}\n")

    for ds in datasets:
        try:
            X, y = load_dataset(ds, data_dir_txt, data_dir_mat)
        except Exception as e:
            print(f"  [SKIP] {ds}: {e}")
            continue

        uc, cc = np.unique(y, return_counts=True)
        print(f"\n  Dataset: {ds}  shape={X.shape}")

        for run in range(num_runs):
            if (version, ds, run) in done:
                print(f"    [skip] run {run}")
                continue
            if max_tasks is not None and tasks_run >= max_tasks:
                remaining = total_scope - done_this - tasks_run
                print(f"\n  [PAUSE] max_tasks={max_tasks}, ~{remaining} remaining")
                return tasks_run

            np.random.seed(seed_base + run * 37)
            t0 = time()
            res = runner_fn(X, y, opts)
            elapsed = time() - t0

            if post_process is not None:
                res = {**res, **post_process(res, X, y, opts)}

            acc = 1.0 - float(res["fitG"])
            nf  = int(res["nf"])
            nhd = res.get("nhd_curve", np.zeros(opts["T"] + 1))
            avg_nhd = float(np.mean(nhd[1:])) if np.any(nhd[1:]) else 0.0

            append_row(csv_path, csv_fields, {
                "Version": version, "Dataset": ds, "Run": run,
                "Accuracy": f"{acc:.6f}", "Num_Features": nf,
                "Avg_NHD": f"{avg_nhd:.6f}", "Time_sec": f"{elapsed:.2f}",
            })

            np.save(os.path.join(curves_dir, f"curve_{version}_{ds}_run{run}.npy"),
                    res.get("curve", np.zeros(opts["T"] + 1)))
            np.save(os.path.join(curves_dir, f"nhd_{version}_{ds}_run{run}.npy"),
                    nhd)

            tasks_run += 1
            total_done = done_this + tasks_run
            print(f"    ✓ run {run:2d} | Acc={acc:.4f} | Feat={nf:6d} | "
                  f"NHD={avg_nhd:.3f} | t={elapsed:7.1f}s  [{total_done}/{total_scope}]")

    print(f"\n  ✅ {version} complete ({tasks_run} new tasks)")
    return tasks_run
