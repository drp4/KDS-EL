# ============================================================
# Cell B: Stroke | MEL only | ~7.2h
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

def run_MEL(X, y, opts):
    lb, ub, thres = 0.0, 1.0, opts["thres"]
    c1=c2=c3=2.0; w=0.9; Vmax=0.5
    N=opts["N"]; T=opts["T"]; dim=X.shape[1]
    weight=np.zeros(dim)
    P=np.random.uniform(lb,ub,(N,dim)); V=np.zeros((N,dim))
    subSize=N//2
    fit=np.array([jFitnessFunction(X,y,(P[i]>thres),opts) for i in range(N)])
    fitP=fit.copy(); Pbest=P.copy()
    Gbest=P[np.argmin(fit)].copy(); fitG=float(np.min(fit))
    curve=np.zeros(T+1); curve[0]=fitG
    for t in range(1,T+1):
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
        pool_bin=(pool>thres).astype(bool)
        pool_fit=np.array([jFitnessFunction(X,y,pool_bin[i],opts) for i in range(2*N)])
        idx=np.argsort(pool_fit)[:N]
        P=pool[idx]; fit_sel=pool_fit[idx]; bin_sel=pool_bin[idx]
        for i in range(N):
            fv_n=bin_sel[i]; fv_o=(Pbest[i]>thres)
            if fit_sel[i] < fitP[i]:
                inc=fitP[i]-fit_sel[i]; change=np.logical_xor(fv_n,fv_o)
                weight[change & (fv_n>fv_o)] += inc
                weight[change & (fv_n<fv_o)] -= inc
        improved=fit_sel<fitP
        Pbest=np.where(improved[:,None],P,Pbest)
        fitP=np.minimum(fit_sel,fitP)
        bi=np.argmin(fitP)
        if fitP[bi] < fitG: fitG=float(fitP[bi]); Gbest=Pbest[bi].copy()
        curve[t]=fitG
    return {"fitG": fitG, "nf": int((Gbest>thres).sum()), "curve": curve, "nhd_curve": np.zeros(T+1)}

RUNNERS = {"MEL": run_MEL}

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

print("\n✅ Cell B finished.")
