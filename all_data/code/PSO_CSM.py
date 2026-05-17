# =============================================================================
#  Cell: PSO-CSM — PSO with Comprehensive Scoring Framework
#  Reference: Wei et al., Journal of King Saud University CIS, 2025
#  https://doi.org/10.1016/j.jksuci.2024.102XXXX
#
#  Two-component comprehensive score drives progressive feature space reduction:
#
#  Component 1 — Feature Relevance (SU-proxy via F-score):
#    rel[j] = F(j) / max(F)     where F = f_classif(X, y)
#    Computed ONCE per dataset (O(n·d), <1s even for Stroke d=26877)
#    Cached across 10 runs of the same dataset.
#
#  Component 2 — Population Feedback (Pbest frequency):
#    fb[j](t) = (1/N) Σ_i 1[Pbest_i selects feature j]
#    Recomputed every R_csm iterations during evolution.
#
#  Comprehensive score:
#    score[j](t) = w_rel · rel[j] + w_fb · fb[j](t)
#
#  Scaling adjustment (progressive space reduction):
#    Every R_csm iters: remove bottom-frac of active features
#    bottom-frac(t) = sigma · (t / T)     (grows with iteration)
#    Guard: active.sum() − n_remove ≥ min_features = max(10, d/100)
#
#  Initialization: P(select j) = clip(0.1 + 0.8 · rel[j], 0, 1)
#  PSO update: standard binary PSO (sigmoid transfer function)
#  Inactive features: forced to 0, excluded from Sub2 sampling & PSO update
# =============================================================================
ONLY_DATASETS = [
    "Adenoma","ALL_AML","ALL3","ALL4","CNS","Colon","DLBCL","Lymphoma","Stroke"
]
MAX_TASKS = 200
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
CSV_PATH   = os.path.join(OUT_DIR, "results_pso_csm.csv")
os.makedirs(CURVES_DIR, exist_ok=True)

NUM_RUNS  = 10
SEED_BASE = 42

OPTS = {
    "k": 3, "N": 20, "T": 100, "thres": 0.6,
    "ws": [0.9, 0.1],
    "cv_splits": 5, "cv_shuffle": True, "cv_random_state": 42,
    # PSO-CSM specific
    "w_rel":   0.5,    # weight for relevance score
    "w_fb":    0.5,    # weight for population feedback
    "R_csm":   10,     # scoring update frequency (iterations)
    "sigma":   0.04,   # removal rate coefficient (removes sigma*(t/T)*active each step)
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
    return opts["ws"][0] * jwrapper_KNN(X[:, mask], y, opts) + opts["ws"][1] * (nf / X.shape[1])

def pairwise_nhd(X_bin):
    X_bin  = X_bin.astype(np.float32)
    inter  = X_bin @ X_bin.T
    sums   = X_bin.sum(axis=1)
    union  = sums[:, None] + sums[None, :] - inter
    ahd    = sums[:, None] + sums[None, :] - 2.0 * inter
    return ahd / np.maximum(union, 1.0)

# ── Feature relevance score (cached per dataset) ──────────────────────────
_REL_CACHE = {}

def get_relevance(X, y, ds_name):
    """
    Compute normalised F-score (ANOVA) as feature relevance proxy for SU.
    F-score is O(n·d) and runs in <1s even for Stroke (d=26877).
    Cached across runs: computed once per dataset, reused for all 10 runs.
    """
    if ds_name in _REL_CACHE:
        return _REL_CACHE[ds_name]
    F, _ = f_classif(X, y)
    F    = np.nan_to_num(F, nan=0.0, posinf=0.0, neginf=0.0)
    rel  = F / (F.max() + 1e-9)                # normalise to [0, 1]
    _REL_CACHE[ds_name] = rel
    return rel

# ── PSO-CSM ───────────────────────────────────────────────────────────────
def run_PSO_CSM(X, y, opts, rel):
    """
    PSO with Comprehensive Scoring Framework.

    Algorithm flow
    ──────────────
    Init:
      P(select j) = clip(0.1 + 0.8·rel[j], 0.05, 0.95)   [importance-biased]
      active[j] = True for all j                            [all features active]

    Each iteration t:
      Standard binary PSO update (sigmoid transfer):
        V ← w·V + c1·r1·(Pbest−P) + c2·r2·(gbest−P)
        prob = sigmoid(V)
        P_new[j] = Bernoulli(prob[j])
        Inactive features: P_new[j] = 0 (excluded)
      Update Pbest / gbest

      Every R_csm iterations:
        fb[j]    = mean_{i} 1[Pbest_i selects j]           [population feedback]
        score[j] = w_rel·rel[j] + w_fb·fb_norm[j]
        n_remove = int(sigma · (t/T) · active.sum())
        Remove n_remove features with lowest score
        (guard: keep ≥ max(10, d/100) features active)
        Inactive features zeroed in P, Pbest, gbest
    """
    N, T, dim = opts["N"], opts["T"], X.shape[1]
    Vmax      = 0.5
    w_inertia = 0.9
    c1 = c2   = 2.0
    w_rel     = opts["w_rel"]
    w_fb      = opts["w_fb"]
    R_csm     = opts["R_csm"]
    sigma     = opts["sigma"]
    min_feats = max(10, dim // 100)

    # ── Importance-biased initialisation ──────────────────────────────────
    init_prob = np.clip(0.1 + 0.8 * rel, 0.05, 0.95)     # (dim,) ∈ [0.05, 0.95]
    P  = (np.random.rand(N, dim) < init_prob).astype(float)
    V  = np.zeros((N, dim))

    fit   = np.array([jFitness(X, y, P[i].astype(bool), opts) for i in range(N)])
    Pbest = P.copy()
    fitP  = fit.copy()
    gbest = P[np.argmin(fit)].copy()
    fitG  = float(np.min(fit))

    # Feature activity mask (all active initially)
    active = np.ones(dim, dtype=bool)

    curve    = np.zeros(T + 1)
    curve[0] = fitG

    for t in range(1, T + 1):

        # ── Standard binary PSO update ────────────────────────────────────
        r1 = np.random.rand(N, dim)
        r2 = np.random.rand(N, dim)
        V  = np.clip(
            w_inertia * V
            + c1 * r1 * (Pbest - P)
            + c2 * r2 * (gbest - P),
            -Vmax, Vmax,
        )
        # Sigmoid transfer → binary
        prob  = 1.0 / (1.0 + np.exp(-V))                   # (N, dim)
        P_new = (np.random.rand(N, dim) < prob).astype(float)

        # Inactive features forced to 0
        P_new[:, ~active] = 0.0

        # Evaluate + update Pbest / gbest
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

        # ── Comprehensive scoring + progressive feature removal ────────────
        if t % R_csm == 0:

            # Population feedback for active features
            pb_bin     = (Pbest[:, active] > 0.5).astype(float)   # (N, K_active)
            fb_active  = pb_bin.mean(axis=0)                        # (K_active,)
            fb_max     = fb_active.max()
            fb_norm    = fb_active / (fb_max + 1e-9)

            # Comprehensive score for active features
            rel_active = rel[active]                                # (K_active,)
            score      = w_rel * rel_active + w_fb * fb_norm       # (K_active,)

            # Number to remove (grows with iteration)
            n_remove = int(sigma * (t / T) * active.sum())

            if n_remove > 0 and (active.sum() - n_remove) >= min_feats:
                # Indices within active-feature sub-space (local)
                local_low  = np.argsort(score)[:n_remove]
                # Map to global feature indices
                active_idx = np.where(active)[0]
                global_low = active_idx[local_low]

                # Deactivate
                active[global_low]     = False
                # Zero out in all populations
                P[:, global_low]       = 0.0
                Pbest[:, global_low]   = 0.0
                gbest[global_low]      = 0.0

    # ── Final diagnostics ─────────────────────────────────────────────────
    nhd_mat = pairwise_nhd((Pbest > 0.5).astype(int))
    avg_nhd = float(nhd_mat.sum() / (N * (N - 1))) if N > 1 else 0.0

    return {
        "fitG":    fitG,
        "nf":      int(gbest.sum()),
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
VER  = "PSO_CSM"
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

    # Compute relevance once per dataset (cached)
    t_rel = time()
    rel   = get_relevance(X, y, ds)
    t_rel = time() - t_rel
    n_high = int((rel > 0.5).sum())
    print(f"  Relevance computed in {t_rel:.1f}s  "
          f"| high-relevance (>0.5): {n_high}/{X.shape[1]}")

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
        res = run_PSO_CSM(X, y, OPTS, rel)
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