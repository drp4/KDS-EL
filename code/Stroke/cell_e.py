# ============================================================
# Cell E: Stroke | MEL_KGEF only | ~7.2h  (proposed method)
# ============================================================
ONLY_DATASETS = ["Stroke"]
MAX_TASKS = 10

import os, csv, warnings
import numpy as np
from time import time
from sklearn.neighbors import KNeighborsClassifier
from sklearn.model_selection import StratifiedKFold

warnings.filterwarnings("ignore")
np.seterr(all="ignore")

DATA_DIR   = "/kaggle/input/datasets/eminz132/dataset/Datasets_part1"
OUT_DIR    = "/kaggle/working"
CURVES_DIR = os.path.join(OUT_DIR, "curves_all_rerun_stratified")
CSV_PATH   = os.path.join(OUT_DIR, "results_all_rerun_stratified.csv")
os.makedirs(CURVES_DIR, exist_ok=True)

NUM_RUNS  = 10
SEED_BASE = 42
OPTS = {
    "k": 3, "N": 20, "T": 100, "thres": 0.6,
    "ws": [0.9, 0.1], "weight_decay": 0.99,
    "cv_splits": 5, "cv_shuffle": True, "cv_random_state": 42
}
CSV_FIELDS = ["Version","Dataset","Run","Accuracy","Num_Features","Avg_NHD","Time_sec"]
LABEL_START_COL = {"CNS": 3, "MLL": 2}
DATA_START_COL  = {"CNS": 3, "MLL": 2}

def _parse_srbct_label(s):
    for p in ["EWS","RMS","NB","BL"]:
        if s.startswith(p): return p
    return s

def _parse_mll_label(s):
    for p in ["ALL","MLL","AML"]:
        if s.startswith(p): return p
    return s

def load_dataset(p_name):
    fp = os.path.join(DATA_DIR, f"{p_name}.txt")
    if not os.path.exists(fp):
        raise FileNotFoundError(fp)
    lines = open(fp, "r").read().splitlines()
    lbl_start  = LABEL_START_COL.get(p_name, 1)
    data_start = DATA_START_COL.get(p_name, 1)
    header = lines[0].strip().split("\t")
    labels_raw = [h for h in header[lbl_start:] if h.strip() != ""]
    if p_name == "SRBCT":
        labels_raw = [_parse_srbct_label(s) for s in labels_raw]
    elif p_name == "MLL":
        labels_raw = [_parse_mll_label(s) for s in labels_raw]
    classes = sorted(set(labels_raw))
    cmap = {c:i for i,c in enumerate(classes)}
    y = np.array([cmap[s] for s in labels_raw], dtype=int)
    n = len(y)
    rows = []
    for line in lines[1:]:
        parts = line.rstrip("\n").split("\t")
        vals = [p for p in parts[data_start:] if p.strip() != ""]
        if len(vals) != n: continue
        try: rows.append([float(x) for x in vals])
        except ValueError: continue
    X = np.array(rows, dtype=float).T
    assert X.shape[0] == n
    return X, y

def jwrapper_KNN(sFeat, y, opts):
    k = opts.get("k", 3)
    skf = StratifiedKFold(
        n_splits=opts.get("cv_splits", 5),
        shuffle=opts.get("cv_shuffle", True),
        random_state=opts.get("cv_random_state", 42),
    )
    acc = []
    for tr, te in skf.split(sFeat, y):
        mdl = KNeighborsClassifier(n_neighbors=k)
        mdl.fit(sFeat[tr], y[tr])
        acc.append((mdl.predict(sFeat[te]) == y[te]).mean())
    return 1.0 - float(np.mean(acc))

def jFitnessFunction(X, y, mask_bool, opts):
    ws = opts.get("ws", [0.9, 0.1])
    nf = int(np.sum(mask_bool))
    if nf < 3: return 1.0 + (3 - nf) * 0.1
    err = jwrapper_KNN(X[:, mask_bool], y, opts)
    return ws[0] * err + ws[1] * (nf / X.shape[1])

def pairwise_nhd(X_bin):
    X_bin = X_bin.astype(np.float32)
    inter = X_bin @ X_bin.T
    sums  = X_bin.sum(axis=1)
    union = sums[:, None] + sums[None, :] - inter
    ahd   = sums[:, None] + sums[None, :] - 2.0 * inter
    return ahd / np.maximum(union, 1.0)

def fast_nds(objectives):
    N  = objectives.shape[0]
    dc = np.zeros(N, dtype=int)
    ds = [[] for _ in range(N)]
    fronts = [[]]
    for i in range(N):
        for j in range(N):
            if i == j: continue
            if np.all(objectives[i] <= objectives[j]) and np.any(objectives[i] < objectives[j]):
                ds[i].append(j)
            elif np.all(objectives[j] <= objectives[i]) and np.any(objectives[j] < objectives[i]):
                dc[i] += 1
        if dc[i] == 0: fronts[0].append(i)
    cf = 0
    while fronts[cf]:
        nf = []
        for i in fronts[cf]:
            for j in ds[i]:
                dc[j] -= 1
                if dc[j] == 0: nf.append(j)
        cf += 1; fronts.append(nf)
    if not fronts[-1]: fronts.pop()
    return fronts

def crowding_dist(objectives, front):
    l = len(front)
    cd = {idx: 0.0 for idx in front}
    for m in range(objectives.shape[1]):
        sf = sorted(front, key=lambda i: objectives[i, m])
        cd[sf[0]] = cd[sf[-1]] = np.inf
        span = objectives[sf[-1], m] - objectives[sf[0], m]
        if span == 0: continue
        for k in range(1, l - 1):
            cd[sf[k]] += (objectives[sf[k+1], m] - objectives[sf[k-1], m]) / span
    return cd

def emdo_select(pool_fit, nhd_matrix, N, alpha_cd):
    pool_nhd = nhd_matrix.mean(axis=1)
    objectives = np.column_stack([pool_fit, -pool_nhd])
    fronts = fast_nds(objectives)
    selected = []
    for front in fronts:
        if len(selected) + len(front) <= N:
            selected.extend(front)
        else:
            needed = N - len(selected)
            cd = crowding_dist(objectives, front)
            cd_v = np.array([cd[i] for i in front])
            fin = cd_v[np.isfinite(cd_v)]
            mc = np.max(fin) if len(fin) > 0 else 0.0
            cd_n = np.where(np.isfinite(cd_v), (cd_v / mc if mc > 0 else 0.0), 1.0)
            hd_v = np.array([pool_nhd[i] for i in front])
            mh = np.max(hd_v)
            hd_n = hd_v / mh if mh > 0 else np.zeros(len(front))
            comb = alpha_cd * cd_n + (1.0 - alpha_cd) * hd_n
            order = np.argsort(-comb)
            selected.extend([front[order[k]] for k in range(needed)])
            break
    return np.array(selected)

def _kgef_elite_flip(weight, elite_bin, flip_count):
    mutant = elite_bin.copy()
    dim = len(mutant)
    if np.random.rand() < 0.10:
        fi = np.random.choice(dim, flip_count, replace=False)
        mutant[fi] = 1 - mutant[fi]
    else:
        scores = np.where(elite_bin == 0, weight, -weight)
        scores += np.random.normal(0, np.std(weight) + 1e-5, dim)
        fi = np.argsort(-scores)[:flip_count]
        mutant[fi] = 1 - mutant[fi]
    return mutant

def run_MEL_KGEF(X, y, opts):
    lb, ub, thres = 0.0, 1.0, opts["thres"]
    c1=c2=c3=2.0; w=0.9; Vmax=0.5
    N=opts["N"]; T=opts["T"]; dim=X.shape[1]
    decay=opts["weight_decay"]
    weight=np.zeros(dim)
    P=np.random.uniform(lb,ub,(N,dim)); V=np.zeros((N,dim))
    subSize=N//2
    fit=np.array([jFitnessFunction(X,y,(P[i]>thres),opts) for i in range(N)])
    fitP=fit.copy(); Pbest=P.copy()
    Gbest=P[np.argmin(fit)].copy(); fitG=float(np.min(fit))
    curve=np.zeros(T+1); nhd_curve=np.zeros(T+1); curve[0]=fitG
    for t in range(1,T+1):
        weight*=decay
        alpha_cd=(t/T)**2
        P_new=P.copy()
        Xsub_best = Pbest[subSize + np.argmin(fitP[subSize:])].copy()
        for i in range(N):
            if i < subSize:
                r1,r2,r3=np.random.rand(dim),np.random.rand(dim),np.random.rand(dim)
                V[i]=np.clip(w*V[i]+c1*r1*(Pbest[i]-P[i])+c2*r2*(Gbest-P[i])+c3*r3*(Xsub_best-P[i]),-Vmax,Vmax)
                P_new[i]=np.clip(P[i]+V[i],lb,ub)
            else:
                vf=np.maximum(weight,0.0); sv=vf.sum()
                prob=vf/sv if sv>0 else np.full(dim,0.5)
                P_new[i]=(np.random.rand(dim)<prob).astype(float)
        pool=np.vstack([Pbest,P_new])
        pool_bin=(pool>thres).astype(int)
        pool_fit=np.array([jFitnessFunction(X,y,pool_bin[i].astype(bool),opts) for i in range(2*N)])
        nhd_mat=pairwise_nhd(pool_bin)
        sel=emdo_select(pool_fit,nhd_mat,N,alpha_cd)
        P=pool[sel]; fit_sel=pool_fit[sel]
        improved=fit_sel<fitP
        Pbest=np.where(improved[:,None],P,Pbest)
        fitP=np.minimum(fit_sel,fitP)
        flip_count=max(1,int(0.01*dim))
        elites=np.argsort(fitP)[:3]
        for e in elites:
            elite_bin=(Pbest[e]>thres).astype(int)
            mutant=_kgef_elite_flip(weight, elite_bin, flip_count)
            mfit=jFitnessFunction(X,y,mutant.astype(bool),opts)
            if mfit < fitP[e]: Pbest[e]=mutant; fitP[e]=mfit
        bi=np.argmin(fitP)
        if fitP[bi] < fitG: fitG=float(fitP[bi]); Gbest=Pbest[bi].copy()
        sb=(Pbest>thres).astype(int); nm=pairwise_nhd(sb)
        nhd_curve[t]=nm.sum()/(N*(N-1)) if N>1 else 0.0
        curve[t]=fitG
    return {"fitG": fitG, "nf": int((Gbest>thres).sum()), "curve": curve, "nhd_curve": nhd_curve}

RUNNERS = {"MEL_KGEF": run_MEL_KGEF}

def ensure_csv_header():
    if not os.path.exists(CSV_PATH):
        with open(CSV_PATH, "w", newline="") as f:
            csv.DictWriter(f, fieldnames=CSV_FIELDS).writeheader()

def load_completed():
    done = set()
    if not os.path.exists(CSV_PATH): return done
    with open(CSV_PATH, "r", newline="") as f:
        for r in csv.DictReader(f):
            try: done.add((r["Version"], r["Dataset"], int(r["Run"])))
            except Exception: pass
    return done

def append_row(row):
    with open(CSV_PATH, "a", newline="") as f:
        csv.DictWriter(f, fieldnames=CSV_FIELDS).writerow(row)

ensure_csv_header()
done = load_completed()
tasks_done_this_run = 0
scope = len(ONLY_DATASETS) * len(RUNNERS) * NUM_RUNS
print(f"Already finished: {len(done)} | Scope: {scope} | MAX_TASKS: {MAX_TASKS}")

for ds in ONLY_DATASETS:
    X, y = load_dataset(ds)
    print(f"\n{'='*70}\nDataset: {ds} | X={X.shape} | class_counts={np.bincount(y)}\n{'='*70}")
    for ver, fn in RUNNERS.items():
        for run in range(NUM_RUNS):
            if (ver, ds, run) in done: continue
            if MAX_TASKS is not None and tasks_done_this_run >= MAX_TASKS:
                print(f"\nReached MAX_TASKS={MAX_TASKS}. Re-run to continue.")
                raise SystemExit(0)
            np.random.seed(SEED_BASE + run*37)
            t0 = time()
            res = fn(X, y, OPTS)
            elapsed = time() - t0
            acc = 1.0 - float(res["fitG"])
            nf  = int(res["nf"])
            nhd_curve = res.get("nhd_curve", np.zeros(OPTS["T"]+1))
            avg_nhd = float(np.mean(nhd_curve[1:])) if np.any(nhd_curve[1:]) else 0.0
            append_row({"Version": ver, "Dataset": ds, "Run": run,
                        "Accuracy": f"{acc:.6f}", "Num_Features": nf,
                        "Avg_NHD": f"{avg_nhd:.6f}", "Time_sec": f"{elapsed:.2f}"})
            np.save(os.path.join(CURVES_DIR, f"curve_{ver}_{ds}_run{run}.npy"), res["curve"])
            np.save(os.path.join(CURVES_DIR, f"nhd_{ver}_{ds}_run{run}.npy"), nhd_curve)
            tasks_done_this_run += 1
            print(f"  ✓ {ver:14s} | run {run:2d} | Acc={acc:.4f} | Feat={nf:6d} | t={elapsed:7.1f}s")

print("\n✅ Cell E finished.")
