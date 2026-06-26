# =============================================================================
#  Cell: IGPSO — Importance-Guided Particle Swarm Optimization
#  Reference: (Applied Soft Computing, 2024)
#  Novel importance-guided PSO for large-scale feature selection.
#
#  Key idea: compute a two-stage feature importance vector that distinguishes
#  informative features (real labels) from noise features (shuffled labels),
#  then use it to modulate every particle's PSO parameters per-feature:
#    w_j  ∝ (1 − imp_j)   low inertia for important features → fast convergence
#    c1_j ∝ imp_j          strong personal guidance for important features
#    c2_j ∝ imp_j          strong social  guidance for important features
#  Importance estimation: f_classif(real labels) − f_classif(shuffled labels)
#  (F-score difference; O(n·d) per dataset, <<1s even for Stroke at d=26877)
# =============================================================================
ONLY_DATASETS = [
    "Adenoma","ALL_AML","ALL3","ALL4","CNS","Colon","DLBCL","Lymphoma","Stroke"
]
MAX_TASKS = 200   # re-run cell until all 90 tasks done
# =============================================================================

import os, csv, warnings
import numpy as np
from time import time
from sklearn.neighbors import KNeighborsClassifier
from sklearn.model_selection import StratifiedKFold
from sklearn.feature_selection import f_classif

warnings.filterwarnings("ignore")
np.seterr(all="ignore")

DATA_DIR   = "/kaggle/input/datasets/eminz132/dataset/Datasets_part1"
OUT_DIR    = "/kaggle/working"
CURVES_DIR = os.path.join(OUT_DIR, "curves_all_rerun_stratified")
CSV_PATH   = os.path.join(OUT_DIR, "results_igpso.csv")    # separate file
os.makedirs(CURVES_DIR, exist_ok=True)

NUM_RUNS  = 10
SEED_BASE = 42

OPTS = {
    "k": 3, "N": 20, "T": 100, "thres": 0.6,
    "ws": [0.9, 0.1],
    "cv_splits": 5, "cv_shuffle": True, "cv_random_state": 42,
}

CSV_FIELDS = ["Version","Dataset","Run","Accuracy","Num_Features","Avg_NHD","Time_sec"]

# ── Dataset loader ────────────────────────────────────────────────────────
LABEL_START_COL = {"CNS": 3, "MLL": 2}
DATA_START_COL  = {"CNS": 3, "MLL": 2}

def load_dataset(p_name):
    fp = os.path.join(DATA_DIR, f"{p_name}.txt")
    if not os.path.exists(fp): raise FileNotFoundError(fp)
    lines      = open(fp).read().splitlines()
    lbl_start  = LABEL_START_COL.get(p_name, 1)
    data_start = DATA_START_COL.get(p_name, 1)
    header     = lines[0].strip().split("\t")
    labels_raw = [h for h in header[lbl_start:] if h.strip()]
    classes    = sorted(set(labels_raw))
    cmap       = {c: i for i, c in enumerate(classes)}
    y          = np.array([cmap[s] for s in labels_raw], dtype=int)
    n          = len(y)
    rows       = []
    for line in lines[1:]:
        parts = line.rstrip("\n").split("\t")
        vals  = [p for p in parts[data_start:] if p.strip()]
        if len(vals) != n: continue
        try:    rows.append([float(x) for x in vals])
        except: continue
    X = np.array(rows, dtype=float).T
    assert X.shape[0] == n
    return X, y

# ── Fitness ───────────────────────────────────────────────────────────────
def jwrapper_KNN(X_sub, y, opts):
    skf = StratifiedKFold(
        n_splits=opts["cv_splits"],
        shuffle=opts["cv_shuffle"],
        random_state=opts["cv_random_state"],
    )
    acc = []
    for tr, te in skf.split(X_sub, y):
        clf = KNeighborsClassifier(n_neighbors=opts["k"])
        clf.fit(X_sub[tr], y[tr])
        acc.append((clf.predict(X_sub[te]) == y[te]).mean())
    return 1.0 - float(np.mean(acc))

def jFitness(X, y, mask, opts):
    nf = int(mask.sum())
    if nf < 3: return 1.0 + (3 - nf) * 0.1
    return (opts["ws"][0] * jwrapper_KNN(X[:, mask], y, opts)
            + opts["ws"][1] * (nf / X.shape[1]))

def pairwise_nhd(X_bin):
    X_bin  = X_bin.astype(np.float32)
    inter  = X_bin @ X_bin.T
    sums   = X_bin.sum(axis=1)
    union  = sums[:, None] + sums[None, :] - inter
    ahd    = sums[:, None] + sums[None, :] - 2.0 * inter
    return ahd / np.maximum(union, 1.0)

# ── Importance vector (two-stage F-score) ────────────────────────────────
# Cache importance vectors so the 10 runs per dataset share the computation.
_IMP_CACHE = {}

def get_importance(X, y, ds_name):
    """
    Two-stage importance estimation:
      Stage 1: F-score of each feature vs. real class labels → informative signal
      Stage 2: F-score of each feature vs. shuffled labels   → noise baseline
      importance = max(0, F_real − F_noise), normalised to [0, 1]

    F-score (one-way ANOVA) is O(n·d) and runs in <1 s even for Stroke (d=26877).
    Fixed shuffle seed ensures all 10 runs per dataset use the same importance.
    """
    if ds_name in _IMP_CACHE:
        return _IMP_CACHE[ds_name]

    # Stage 1: real labels
    F1, _ = f_classif(X, y)
    F1    = np.nan_to_num(F1, nan=0.0, posinf=0.0, neginf=0.0)

    # Stage 2: shuffled labels (fixed seed for reproducibility)
    rng   = np.random.default_rng(seed=0)
    y_neg = rng.permutation(y)
    F2, _ = f_classif(X, y_neg)
    F2    = np.nan_to_num(F2, nan=0.0, posinf=0.0, neginf=0.0)

    # Combine: positive difference only
    imp = np.maximum(0.0, F1 - F2)

    # Normalise to [0, 1]
    imp_max = imp.max()
    if imp_max > 1e-9:
        imp = imp / imp_max
    else:
        imp = np.full(X.shape[1], 0.5)

    _IMP_CACHE[ds_name] = imp
    return imp

# ── IGPSO ─────────────────────────────────────────────────────────────────
def run_IGPSO(X, y, opts, imp):
    """
    IGPSO: Binary PSO with feature-importance-weighted parameters.

    For feature j, the velocity update rule becomes:
        V_j ← w_j·V_j + c1_j·r1·(Pbest_j − x_j) + c2_j·r2·(gbest_j − x_j)
    where:
        w_j  = W_min + (W_max − W_min) × (1 − imp_j)   [negatively correlated]
        c1_j = C_min + (C_max − C_min) × imp_j          [positively correlated]
        c2_j = C_min + (C_max − C_min) × imp_j

    Positions are binary; velocity→probability via sigmoid; initialisation
    is biased so important features are selected with higher probability.
    """
    lb, ub, thres = 0.0, 1.0, opts["thres"]
    N, T, dim     = opts["N"], opts["T"], X.shape[1]
    Vmax          = 0.5

    # Parameter bounds
    W_max = 0.9; W_min = 0.1
    C_max = 2.0; C_min = 0.1

    # Per-feature PSO parameters  (shape: (dim,))
    w_j  = W_min + (W_max - W_min) * (1.0 - imp)   # negatively correlated w/ imp
    c1_j = C_min + (C_max - C_min) * imp             # positively correlated
    c2_j = C_min + (C_max - C_min) * imp             # positively correlated

    # Importance-biased initialisation
    # P(select feature j) = 0.2 + 0.6 × imp_j  ∈ [0.2, 0.8]
    init_prob = 0.2 + 0.6 * imp                      # (dim,)
    P  = (np.random.rand(N, dim) < init_prob).astype(float)
    V  = np.zeros((N, dim))

    fit    = np.array([jFitness(X, y, P[i].astype(bool), opts) for i in range(N)])
    Pbest  = P.copy()
    fitP   = fit.copy()
    gbest  = P[np.argmin(fit)].copy()
    fitG   = float(np.min(fit))

    curve  = np.zeros(T + 1)
    curve[0] = fitG

    for t in range(1, T + 1):
        r1 = np.random.rand(N, dim)
        r2 = np.random.rand(N, dim)

        # Feature-importance-weighted velocity update
        # Broadcasting: w_j(dim,), V(N,dim), Pbest(N,dim), gbest(dim,)
        V = (w_j * V
             + c1_j * r1 * (Pbest - P)
             + c2_j * r2 * (gbest  - P))
        V = np.clip(V, -Vmax, Vmax)

        # Sigmoid transfer → flip probability → binary update
        prob  = 1.0 / (1.0 + np.exp(-V))          # (N, dim) ∈ (0, 1)
        P_new = (np.random.rand(N, dim) < prob).astype(float)

        fit_new  = np.array([jFitness(X, y, P_new[i].astype(bool), opts)
                             for i in range(N)])

        improved = fit_new < fitP
        Pbest    = np.where(improved[:, None], P_new, Pbest)
        fitP     = np.minimum(fit_new, fitP)
        P        = P_new

        bi = int(np.argmin(fitP))
        if fitP[bi] < fitG:
            fitG  = float(fitP[bi])
            gbest = Pbest[bi].copy()

        curve[t] = fitG

    # Average NHD of final Pbest
    sb      = Pbest.astype(int)          # already binary (0/1 floats)
    nhd_mat = pairwise_nhd(sb)
    avg_nhd = float(nhd_mat.sum() / (N * (N - 1))) if N > 1 else 0.0

    return {
        "fitG":    fitG,
        "nf":      int(gbest.sum()),     # gbest is binary (0/1)
        "curve":   curve,
        "avg_nhd": avg_nhd,
    }

# ── Resume helpers ────────────────────────────────────────────────────────
def ensure_header():
    if not os.path.exists(CSV_PATH):
        with open(CSV_PATH, "w", newline="") as f:
            csv.DictWriter(f, fieldnames=CSV_FIELDS).writeheader()

def load_done():
    done = set()
    if not os.path.exists(CSV_PATH): return done
    with open(CSV_PATH, newline="") as f:
        for r in csv.DictReader(f):
            try: done.add((r["Version"], r["Dataset"], int(r["Run"])))
            except: pass
    return done

def append_row(row):
    with open(CSV_PATH, "a", newline="") as f:
        csv.DictWriter(f, fieldnames=CSV_FIELDS).writerow(row)

# ── Main loop ─────────────────────────────────────────────────────────────
ensure_header()
done = load_done()
VER  = "IGPSO"
total_scope   = len(ONLY_DATASETS) * NUM_RUNS
done_this_ver = sum(1 for (v, _, _) in done if v == VER)

print(f"Version        : {VER}")
print(f"Tasks done     : {done_this_ver} / {total_scope}")
print(f"MAX_TASKS      : {MAX_TASKS}")
print(f"CSV  → {CSV_PATH}")
print(f"NPY  → {CURVES_DIR}\n")

tasks_run = 0
for ds in ONLY_DATASETS:
    X, y = load_dataset(ds)
    print(f"\n{'='*65}")
    print(f"Dataset: {ds}  shape={X.shape}  classes={np.bincount(y)}")
    print(f"{'='*65}")

    # Compute importance once per dataset (cached across runs)
    t_imp = time()
    imp = get_importance(X, y, ds)
    t_imp = time() - t_imp
    n_top = int((imp > 0.5).sum())
    print(f"  Importance computed in {t_imp:.1f}s  "
          f"| high-imp features (>0.5): {n_top}/{X.shape[1]}")

    for run in range(NUM_RUNS):
        if (VER, ds, run) in done:
            print(f"  [skip] {VER} | run {run}")
            continue
        if MAX_TASKS is not None and tasks_run >= MAX_TASKS:
            remaining = total_scope - done_this_ver - tasks_run
            print(f"\n[PAUSE] MAX_TASKS={MAX_TASKS} reached. "
                  f"~{remaining} tasks left. Re-run cell to continue.")
            raise SystemExit(0)

        np.random.seed(SEED_BASE + run * 37)
        t0  = time()
        res = run_IGPSO(X, y, OPTS, imp)
        elapsed = time() - t0

        acc = 1.0 - float(res["fitG"])
        nf  = int(res["nf"])

        append_row({
            "Version":      VER,       "Dataset":      ds,
            "Run":          run,       "Accuracy":     f"{acc:.6f}",
            "Num_Features": nf,        "Avg_NHD":      f"{res['avg_nhd']:.6f}",
            "Time_sec":     f"{elapsed:.2f}",
        })
        np.save(
            os.path.join(CURVES_DIR, f"curve_{VER}_{ds}_run{run}.npy"),
            res["curve"],
        )

        tasks_run += 1
        total_done = done_this_ver + tasks_run
        print(f"  ✓ {VER} | run {run:2d} | Acc={acc:.4f} | Feat={nf:5d} | "
              f"NHD={res['avg_nhd']:.3f} | t={elapsed:7.1f}s  "
              f"[{total_done}/{total_scope}]")

print(f"\n✅ {VER} — all {total_scope} tasks complete.")