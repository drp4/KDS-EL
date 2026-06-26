# ============================================================
# Cell A: Stroke | BPSO + SaWDE + FWPSO | ~10.7h
# ============================================================
ONLY_DATASETS = ["Stroke"]
TARGET_VERSIONS = ["BPSO", "SaWDE", "FWPSO"]
MAX_TASKS = 30  # 3 methods × 10 runs，全跑完无需重入

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
    if nf < 3:
        return 1.0 + (3 - nf) * 0.1
    err = jwrapper_KNN(X[:, mask_bool], y, opts)
    return ws[0] * err + ws[1] * (nf / X.shape[1])

def pairwise_nhd(X_bin):
    X_bin = X_bin.astype(np.float32)
    inter = X_bin @ X_bin.T
    sums  = X_bin.sum(axis=1)
    union = sums[:, None] + sums[None, :] - inter
    ahd   = sums[:, None] + sums[None, :] - 2.0 * inter
    return ahd / np.maximum(union, 1.0)

def run_BPSO(X, y, opts):
    N = opts["N"]; T = opts["T"]; dim = X.shape[1]
    w, c1, c2 = 0.9, 2.0, 2.0; Vmax = 6.0
    P = (np.random.rand(N, dim) < 0.5).astype(float)
    V = np.zeros((N, dim))
    fit = np.array([jFitnessFunction(X, y, (P[i] > 0.5), opts) for i in range(N)])
    Pbest, fitP = P.copy(), fit.copy()
    g = np.argmin(fitP); Gbest, fitG = Pbest[g].copy(), float(fitP[g])
    curve = np.zeros(T+1); curve[0] = fitG
    for t in range(1, T+1):
        r1, r2 = np.random.rand(N, dim), np.random.rand(N, dim)
        V = w*V + c1*r1*(Pbest-P) + c2*r2*(Gbest-P)
        V = np.clip(V, -Vmax, Vmax)
        prob = 1.0/(1.0+np.exp(-V))
        P = (np.random.rand(N, dim) < prob).astype(float)
        for i in range(N):
            f = jFitnessFunction(X, y, (P[i] > 0.5), opts)
            if f < fitP[i]: Pbest[i] = P[i].copy(); fitP[i] = f
            if f < fitG: fitG = float(f); Gbest = P[i].copy()
        curve[t] = fitG
    mask = (Gbest > 0.5)
    return {"fitG": fitG, "nf": int(mask.sum()), "curve": curve, "nhd_curve": np.zeros(T+1)}

def run_SaWDE(X, y, opts):
    N = opts["N"]; T = opts["T"]; thres = opts["thres"]; dim = X.shape[1]
    P = np.random.rand(N, dim)
    fit = np.array([jFitnessFunction(X, y, (P[i] > thres), opts) for i in range(N)])
    Gbest = P[np.argmin(fit)].copy(); fitG = float(np.min(fit))
    w_strat = np.ones(3)/3.0; F_hist=[0.5]*3; CR_hist=[0.5]*3
    curve = np.zeros(T+1); curve[0] = fitG
    for t in range(1, T+1):
        w_norm = w_strat/(w_strat.sum()+1e-12)
        success = np.zeros(3); count = np.zeros(3)
        P_new = P.copy()
        for i in range(N):
            s = np.random.choice(3, p=w_norm)
            F  = np.clip(np.random.normal(F_hist[s], 0.1), 0.1, 1.0)
            CR = np.clip(np.random.normal(CR_hist[s],0.1), 0.0, 1.0)
            idx = list(range(N)); idx.remove(i)
            r1,r2,r3 = np.random.choice(idx,3,replace=False)
            if s==0: mut = P[r1] + F*(P[r2]-P[r3])
            elif s==1: mut = P[i] + F*(Gbest-P[i]) + F*(P[r1]-P[r2])
            else: mut = Gbest + F*(P[r1]-P[r2])
            mut = np.clip(mut,0,1)
            cross = (np.random.rand(dim) < CR)
            if not cross.any(): cross[np.random.randint(dim)] = True
            trial = np.where(cross, mut, P[i])
            f_trial = jFitnessFunction(X, y, (trial > thres), opts)
            if f_trial <= fit[i]:
                P_new[i] = trial; fit[i] = f_trial
                success[s] += 1
                F_hist[s]  = 0.9*F_hist[s]  + 0.1*F
                CR_hist[s] = 0.9*CR_hist[s] + 0.1*CR
                if f_trial < fitG: fitG = float(f_trial); Gbest = trial.copy()
            count[s] += 1
        sr = np.where(count>0, success/count, 0.0)
        w_strat = 0.9*w_strat + 0.1*(sr + 0.01)
        w_strat = w_strat/(w_strat.sum()+1e-12)
        P = P_new; curve[t] = fitG
    mask = (Gbest > thres)
    return {"fitG": fitG, "nf": int(mask.sum()), "curve": curve, "nhd_curve": np.zeros(T+1)}

def run_FWPSO(X, y, opts):
    N = opts["N"]; T = opts["T"]; thres = opts["thres"]; dim = X.shape[1]
    c1=c2=2.0; w=0.9; Vmax=0.5
    weight = np.zeros(dim)
    P = np.random.rand(N, dim); V = np.zeros((N, dim))
    fitP = np.array([jFitnessFunction(X, y, (P[i] > thres), opts) for i in range(N)])
    Pbest = P.copy()
    g = np.argmin(fitP); Gbest, fitG = Pbest[g].copy(), float(fitP[g])
    curve = np.zeros(T+1); curve[0]=fitG
    for t in range(1, T+1):
        for i in range(N):
            r1,r2 = np.random.rand(dim), np.random.rand(dim)
            V[i] = w*V[i] + c1*r1*(Pbest[i]-P[i]) + c2*r2*(Gbest-P[i])
            V[i] = np.clip(V[i], -Vmax, Vmax)
            vf = np.maximum(weight,0.0); sv=vf.sum()
            if sv>0 and np.random.rand()<0.3:
                prob=vf/sv; P[i]=(np.random.rand(dim)<prob).astype(float)
            else:
                P[i]=np.clip(P[i]+V[i],0,1)
            f = jFitnessFunction(X, y, (P[i] > thres), opts)
            pb=(Pbest[i]>thres); pn=(P[i]>thres)
            if f < fitP[i]:
                inc=fitP[i]-f; change=np.logical_xor(pb,pn)
                weight[change & pn & (~pb)] += inc
                weight[change & pb & (~pn)] -= inc
                Pbest[i]=P[i].copy(); fitP[i]=f
            if f < fitG: fitG=float(f); Gbest=P[i].copy()
        curve[t]=fitG
    mask=(Gbest>thres)
    return {"fitG": fitG, "nf": int(mask.sum()), "curve": curve, "nhd_curve": np.zeros(T+1)}

RUNNERS = {
    "BPSO":  run_BPSO,
    "SaWDE": run_SaWDE,
    "FWPSO": run_FWPSO,
}

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

print("\n✅ Cell A finished.")