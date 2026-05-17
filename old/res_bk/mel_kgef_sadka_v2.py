# =============================================================================
#
#   MEL-KGEF-SADKA: Proposed Algorithm
#   ────────────────────────────────────────────────────────────────────────
#   Full title (paper):
#   "Structure-aware Dynamic Knowledge Attenuation for Evolutionary
#    Feature Selection in High-dimensional Bioinformatics Data"
#
#   Method lineage (ablation table):
#   ┌─────────────────────┬──────┬─────────┬──────────┬─────────────────┐
#   │ Component           │ MEL  │ MEL_NHD │ MEL_KGEF │ MEL_KGEF_SADKA  │
#   ├─────────────────────┼──────┼─────────┼──────────┼─────────────────┤
#   │ Dual-subpop PSO     │  ✓   │    ✓    │    ✓     │       ✓         │
#   │ Weight-guided Sub2  │  ✓   │    ✓    │    ✓     │       ✓         │
#   │ EMDO (NHD select.)  │      │    ✓    │    ✓     │       ✓         │
#   │ KGEF elite flip     │      │         │    ✓     │       ✓         │
#   │ SA-DKA (proposed)   │      │         │          │       ✓         │
#   └─────────────────────┴──────┴─────────┴──────────┴─────────────────┘
#
#   SA-DKA = Structure-aware Dynamic Knowledge Attenuation
#   Two coupled components:
#     A) Dynamic Temporal Attenuation   — adaptive λ(t) based on search state
#     B) Structural Redundancy Penalty  — Pearson-based correlated weight decay
#
#   Evaluation protocol: StratifiedKFold(n_splits=5, shuffle=True, seed=42)
#   Comparison methods (existing data): BPSO, SaWDE, FWPSO, MEL, MEL_NHD, MEL_KGEF
#
# =============================================================================
# Cell: MEL_KGEF_SADKA (Proposed) — 8 standard datasets
# Stroke → run in separate cell (same CSV_PATH, same CURVES_DIR)
ONLY_DATASETS = [
    "Adenoma","ALL_AML","ALL3","ALL4","CNS","Colon","DLBCL","Lymphoma",
]
MAX_TASKS = 200   # re-run cell until all 80 tasks done
# =============================================================================

import os, csv, warnings
import numpy as np
from time import time
from sklearn.neighbors import KNeighborsClassifier
from sklearn.model_selection import StratifiedKFold

warnings.filterwarnings("ignore")
np.seterr(all="ignore")

# ── Paths ─────────────────────────────────────────────────────────────────
DATA_DIR   = "/kaggle/input/datasets/eminz132/dataset/Datasets_part1"
OUT_DIR    = "/kaggle/working"
CURVES_DIR = os.path.join(OUT_DIR, "curves_all_rerun_stratified")   # SAME dir as others
CSV_PATH   = os.path.join(OUT_DIR, "results_all_rerun_stratified.csv")  # SAME CSV
os.makedirs(CURVES_DIR, exist_ok=True)

# ── Config ────────────────────────────────────────────────────────────────
NUM_RUNS  = 10
SEED_BASE = 42

OPTS = {
    # ── Fitness evaluation
    "k": 3, "N": 20, "T": 100, "thres": 0.6,
    "ws": [0.9, 0.1],
    "cv_splits": 5, "cv_shuffle": True, "cv_random_state": 42,

    # ── SA-DKA: Component A — Dynamic Temporal Attenuation
    #    λ(t) = λ_base − γ_s·stag(t) − γ_d·max(0, θ_div − D(t)/D₁)
    #    λ(t) = clip(λ(t), λ_min, λ_base)
    "lambda_base": 0.99,    # base decay (same as original MEL_KGEF)
    "lambda_min":  0.90,    # floor — prevents catastrophic forgetting
    "tau":         10,      # stagnation window (iterations)
    "eps_stag":    1e-6,    # min improvement to reset stagnation counter
    "gamma_s":     0.04,    # stagnation penalty on λ
    "gamma_d":     0.03,    # diversity-collapse penalty on λ
    "theta_div":   0.60,    # diversity ratio threshold

    # ── SA-DKA: Component B — Structural Redundancy Penalty
    #    Every R iters: for top-K features, penalise lower-weight member
    #    of any pair with |Pearson| > ρ
    #    weight[j] *= (1 − α_red · (C[i,j] − ρ))  where w[i] > w[j]
    "rho":         0.70,    # correlation threshold
    "alpha_red":   0.20,    # penalty strength
    "K_top":       30,      # top-K features for correlation scan
    "R":           10,      # update frequency (iterations)

    # ── KGEF: Knowledge-Guided Elite Flip
    "weight_decay": 0.99,   # kept for reference; overridden by SA-DKA
    "flip_frac":    0.01,   # fraction of features to flip per elite
    "elite_k":      3,      # number of elite solutions perturbed
    "rand_flip_p":  0.10,   # probability of random (vs guided) flip
}

CSV_FIELDS = [
    "Version","Dataset","Run",
    "Accuracy","Num_Features","Avg_NHD","Avg_Lambda","Time_sec",
]


# ══════════════════════════════════════════════════════════════════════════
# §1  Dataset loader
# ══════════════════════════════════════════════════════════════════════════
LABEL_START_COL = {"CNS": 3, "MLL": 2}
DATA_START_COL  = {"CNS": 3, "MLL": 2}

def load_dataset(p_name):
    fp = os.path.join(DATA_DIR, f"{p_name}.txt")
    if not os.path.exists(fp):
        raise FileNotFoundError(fp)
    lines      = open(fp, "r").read().splitlines()
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


# ══════════════════════════════════════════════════════════════════════════
# §2  Fitness function  (stratified KNN-CV)
# ══════════════════════════════════════════════════════════════════════════
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
    """Weighted fitness: ws[0]·error + ws[1]·feature_ratio"""
    nf = int(np.sum(mask))
    if nf < 3:
        return 1.0 + (3 - nf) * 0.1       # penalty for near-empty subsets
    err = jwrapper_KNN(X[:, mask], y, opts)
    return opts["ws"][0] * err + opts["ws"][1] * (nf / X.shape[1])


# ══════════════════════════════════════════════════════════════════════════
# §3  NHD and EMDO  (Diversity-Aware Selection, from MEL_NHD)
#
#  EMDO: EMO-based Diversity-Oriented selection
#  Objective 1: fitness value (minimise)
#  Objective 2: −mean_NHD   (minimise → maximise diversity)
#  Selection: NSGA-II non-dominated sort + crowding distance
#  α_cd grows from 0 → 1 over iterations (shift from diversity to accuracy)
# ══════════════════════════════════════════════════════════════════════════
def pairwise_nhd(X_bin):
    """Normalised Hamming Distance averaged over all pairs."""
    X_bin  = X_bin.astype(np.float32)
    inter  = X_bin @ X_bin.T
    sums   = X_bin.sum(axis=1)
    union  = sums[:, None] + sums[None, :] - inter
    ahd    = sums[:, None] + sums[None, :] - 2.0 * inter
    return ahd / np.maximum(union, 1.0)

def fast_nds(obj):
    """Fast non-dominated sort. Returns list of fronts (index lists)."""
    N  = obj.shape[0]
    dc = np.zeros(N, dtype=int)
    ds = [[] for _ in range(N)]
    fronts = [[]]
    for i in range(N):
        for j in range(N):
            if i == j: continue
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
                if dc[j] == 0: nxt.append(j)
        cf += 1; fronts.append(nxt)
    if not fronts[-1]: fronts.pop()
    return fronts

def crowding_dist(obj, front):
    cd = {i: 0.0 for i in front}
    for m in range(obj.shape[1]):
        sf   = sorted(front, key=lambda i: obj[i, m])
        cd[sf[0]] = cd[sf[-1]] = np.inf
        span = obj[sf[-1], m] - obj[sf[0], m]
        if span == 0: continue
        for k in range(1, len(front) - 1):
            cd[sf[k]] += (obj[sf[k+1], m] - obj[sf[k-1], m]) / span
    return cd

def emdo_select(pool_fit, nhd_mat, N, alpha_cd):
    """
    Select N individuals from pool using EMDO.
    alpha_cd ∈ [0,1]: weight of crowding distance vs NHD diversity.
    alpha_cd = (t/T)²  →  early: diversity-first; late: accuracy-first.
    """
    pool_nhd = nhd_mat.mean(axis=1)
    obj      = np.column_stack([pool_fit, -pool_nhd])
    fronts   = fast_nds(obj)
    selected = []
    for front in fronts:
        if len(selected) + len(front) <= N:
            selected.extend(front)
        else:
            needed = N - len(selected)
            cd     = crowding_dist(obj, front)
            cd_v   = np.array([cd[i] for i in front])
            fin    = cd_v[np.isfinite(cd_v)]
            mc     = np.max(fin) if len(fin) > 0 else 0.0
            cd_n   = np.where(np.isfinite(cd_v), (cd_v / mc if mc > 0 else 0.0), 1.0)
            hd_v   = np.array([pool_nhd[i] for i in front])
            mh     = np.max(hd_v)
            hd_n   = hd_v / mh if mh > 0 else np.zeros(len(front))
            score  = alpha_cd * cd_n + (1.0 - alpha_cd) * hd_n
            order  = np.argsort(-score)
            selected.extend([front[order[k]] for k in range(needed)])
            break
    return np.array(selected)


# ══════════════════════════════════════════════════════════════════════════
# §4  SA-DKA: Structure-aware Dynamic Knowledge Attenuation
#
#  MOTIVATION
#  ──────────
#  The original MEL_KGEF uses a fixed decay λ=0.99, which:
#   (a) ignores search state — applies identical attenuation regardless of
#       stagnation, causing weight drift toward noise (see ALL3: MEL median
#       feature count = 4, meaning 90% of runs degenerate to ≤3 features)
#   (b) ignores feature structure — correlated features accumulate redundant
#       knowledge, biasing Sub2 sampling toward structurally redundant subsets
#
#  COMPONENT A: Dynamic Temporal Attenuation
#  ──────────────────────────────────────────
#  Adaptive decay rate:
#    λ(t) = λ_base − γ_s·I_stag(t) − γ_d·max(0, θ_div − D(t)/D₁)
#    λ(t) = clip(λ(t), λ_min, λ_base)
#
#  I_stag(t) ∈ {0,1}: stagnation indicator
#    = 1  if  fitG(t) − fitG(t−τ) < ε    [no improvement in τ iters]
#    = 0  otherwise
#
#  D(t)/D₁: normalised population diversity (mean NHD)
#    when D(t)/D₁ < θ_div, diversity has collapsed → accelerate decay
#    to flush out stale high-weight features and encourage exploration
#
#  Effect:
#    · Stagnation phase  → λ drops by γ_s → stronger forgetting → exploration
#    · Diversity collapse → λ drops by γ_d → flush correlated weight clusters
#    · Active improvement → λ = λ_base → slow forgetting → preserve useful knowledge
#
#  COMPONENT B: Structural Redundancy Penalty
#  ────────────────────────────────────────────
#  Every R iterations, for the top-K features by |weight|:
#    1. Compute pairwise |Pearson correlation| C ∈ ℝ^{K×K}
#    2. For each pair (i,j) where C[i,j] > ρ and |w[i]| > |w[j]|:
#         w[j] *= (1 − α_red · (C[i,j] − ρ))
#  Interpretation: the lower-weight member of a highly correlated pair
#  is "structurally redundant" given the dominant member → attenuate faster.
#
#  CONVERGENCE NOTE
#  ─────────────────
#  SA-DKA preserves ergodicity because:
#   (1) weight vector is bounded: ||w(t)||_∞ ≤ ||w(0)||_∞ + Δmax/(1−λ_min)
#   (2) KGEF uses random flip with prob p=0.10 independent of w,
#       so any bit-string is reachable with positive probability.
#  Hence SA-DKA does not restrict the theoretical convergence guarantees
#  inherited from the underlying MEL framework.
# ══════════════════════════════════════════════════════════════════════════

def sadka_lambda(fitG, best_hist, cur_nhd, init_nhd, opts):
    """
    Compute adaptive attenuation rate λ(t) for Component A.

    Parameters
    ──────────
    fitG      : current global best fitness
    best_hist : deque of length τ — historical best fitness values
    cur_nhd   : current mean NHD of Pbest population
    init_nhd  : mean NHD at first iteration (normaliser)

    Returns
    ───────
    lam : float ∈ [λ_min, λ_base]
    """
    lam = opts["lambda_base"]

    # Stagnation: improvement in window [t-τ, t] < ε
    if (best_hist[0] - fitG) < opts["eps_stag"]:
        lam -= opts["gamma_s"]

    # Diversity collapse
    div_ratio  = cur_nhd / max(init_nhd, 1e-9)
    div_excess = max(0.0, opts["theta_div"] - div_ratio)
    lam -= opts["gamma_d"] * div_excess

    return float(np.clip(lam, opts["lambda_min"], opts["lambda_base"]))


def sadka_redundancy(weight, X_train, opts, cache, last_t, cur_t):
    """
    Apply Component B: Structural Redundancy Penalty.

    Parameters
    ──────────
    weight   : weight vector (modified in-place via numpy view)
    X_train  : training data for correlation computation
    opts     : options dict
    cache    : dict {'idx': top_idx, 'C': corr_matrix} — persists across calls
    last_t   : iteration of last cache update
    cur_t    : current iteration

    Returns
    ───────
    cache, last_t  (updated)
    """
    R       = opts["R"]
    K       = min(opts["K_top"], len(weight))
    rho     = opts["rho"]
    alpha_r = opts["alpha_red"]

    # Recompute correlation matrix every R iterations
    if (cur_t - last_t) >= R:
        top_idx = np.argsort(np.abs(weight))[-K:]
        if len(top_idx) >= 2:
            X_sub = X_train[:, top_idx].astype(np.float64)
            mu    = X_sub.mean(0, keepdims=True)
            std   = X_sub.std(0,  keepdims=True)
            std[std < 1e-10] = 1.0
            Xn    = (X_sub - mu) / std                   # (n, K)
            C     = np.abs(Xn.T @ Xn) / X_train.shape[0] # (K, K) |Pearson|
            np.fill_diagonal(C, 0.0)
            cache  = {"idx": top_idx, "C": C}
        last_t = cur_t

    if not cache:
        return cache, last_t

    top_idx = cache["idx"]
    C       = cache["C"]
    w_abs   = np.abs(weight[top_idx])    # (K,)
    K_act   = len(top_idx)

    # For each feature j, find the max excess correlation from any
    # stronger feature i  (w[i] > w[j] and C[i,j] > ρ)
    for lj in range(K_act):
        gj        = top_idx[lj]
        max_excess = 0.0
        for li in range(K_act):
            if li == lj: continue
            if w_abs[li] > w_abs[lj] and C[li, lj] > rho:
                exc = C[li, lj] - rho
                if exc > max_excess:
                    max_excess = exc
        if max_excess > 0.0:
            weight[gj] *= (1.0 - alpha_r * max_excess)

    return cache, last_t


# ══════════════════════════════════════════════════════════════════════════
# §5  KGEF: Knowledge-Guided Elite Flip  (unchanged from MEL_KGEF)
#
#  For each of the top-k elite solutions:
#    - With probability p_rand: flip random flip_count bits (exploration)
#    - Otherwise: compute knowledge score per feature
#        score[j] = weight[j]  if bit[j]=0  (candidate to add)
#               = −weight[j]  if bit[j]=1  (candidate to remove)
#      → flip top-flip_count bits by score (guided exploitation)
# ══════════════════════════════════════════════════════════════════════════
def kgef_elite_flip(weight, elite_bin, flip_count, rand_p):
    mutant = elite_bin.copy()
    dim    = len(mutant)
    if np.random.rand() < rand_p:
        fi = np.random.choice(dim, flip_count, replace=False)
    else:
        scores = np.where(elite_bin == 0, weight, -weight)
        scores += np.random.normal(0.0, np.std(weight) + 1e-5, dim)
        fi = np.argsort(-scores)[:flip_count]
    mutant[fi] = 1 - mutant[fi]
    return mutant


# ══════════════════════════════════════════════════════════════════════════
# §6  Proposed Algorithm: MEL-KGEF-SADKA
#
#  PSEUDO-CODE
#  ──────────────────────────────────────────────────────────────────────
#  Input : X (n×d), y, OPTS
#  Output: Gbest (best feature mask), fitG, convergence curve
#
#  Initialise:
#    P ← Uniform(0,1)^{N×d},  V ← 0^{N×d},  weight ← 0^d
#    Pbest ← P,  fitP ← fitness(P)
#    Gbest ← Pbest[argmin fitP],  fitG ← min(fitP)
#    D₁ ← mean_NHD(Pbest)
#    best_hist ← [fitG] × τ
#    SA-DKA cache ← ∅
#
#  For t = 1..T:
#    1. Compute D(t) = mean_NHD(Pbest)
#    2. [SA-DKA-A] λ(t) ← sadka_lambda(fitG, best_hist, D(t), D₁)
#    3. weight ← weight × λ(t)
#    4. [SA-DKA-B] Apply redundancy penalty (every R iters)
#    5. Update best_hist sliding window
#    6. Sub1 update (i < N/2): hybrid PSO with [Pbest_i, Gbest, SubBest]
#    7. Sub2 update (i ≥ N/2): sample from P(bit=1) ∝ max(weight,0)
#    8. Pool ← [Pbest; P_new];  pool_fit ← fitness(Pool)
#    9. EMDO: α_cd ← (t/T)²;  sel ← emdo_select(pool_fit, NHD_mat, N, α_cd)
#   10. P ← Pool[sel];  Update Pbest, fitP via improvement comparison
#   11. [Improvement feedback] Update weight ← weight ± Δfitness for
#       features added/removed upon improvement
#   12. [KGEF] For e in top-k elites: Pbest[e] ← kgef_elite_flip(weight, ...)
#   13. Update Gbest, fitG
#   14. Slide best_hist
#  Return Gbest, fitG, curve
# ══════════════════════════════════════════════════════════════════════════
def run_MEL_KGEF_SADKA(X, y, opts):
    lb, ub, thres = 0.0, 1.0, opts["thres"]
    c1 = c2 = c3  = 2.0
    w_inertia     = 0.9
    Vmax          = 0.5
    N, T, dim     = opts["N"], opts["T"], X.shape[1]
    subSize       = N // 2
    tau           = opts["tau"]
    flip_count    = max(1, int(opts["flip_frac"] * dim))
    rand_flip_p   = opts["rand_flip_p"]
    elite_k       = opts["elite_k"]

    # ── Initialise ────────────────────────────────────────────────────────
    weight = np.zeros(dim)
    P      = np.random.uniform(lb, ub, (N, dim))
    V      = np.zeros((N, dim))
    fit    = np.array([jFitness(X, y, P[i] > thres, opts) for i in range(N)])
    fitP   = fit.copy()
    Pbest  = P.copy()
    Gbest  = P[np.argmin(fit)].copy()
    fitG   = float(np.min(fit))

    # Curves & diagnostics
    curve     = np.zeros(T + 1);   curve[0]     = fitG
    nhd_curve = np.zeros(T + 1)
    lam_curve = np.zeros(T + 1);   lam_curve[0] = opts["lambda_base"]

    # SA-DKA state
    best_hist = [fitG] * tau        # sliding window of length τ
    init_nhd  = None                # set at first iteration
    sadka_cache   = {}              # correlation cache for Component B
    last_corr_t   = -opts["R"]     # force first computation at t=1

    for t in range(1, T + 1):

        # ── 1. Population diversity ───────────────────────────────────────
        sb = (Pbest > thres).astype(int)
        nm = pairwise_nhd(sb)
        cur_nhd = nm.sum() / (N * (N - 1)) if N > 1 else 0.0
        nhd_curve[t] = cur_nhd
        if init_nhd is None:
            init_nhd = max(cur_nhd, 1e-9)

        # ── 2-3. SA-DKA Component A: dynamic temporal attenuation ─────────
        lam        = sadka_lambda(fitG, best_hist, cur_nhd, init_nhd, opts)
        weight    *= lam
        lam_curve[t] = lam

        # ── 4. SA-DKA Component B: structural redundancy penalty ──────────
        sadka_cache, last_corr_t = sadka_redundancy(
            weight, X, opts, sadka_cache, last_corr_t, t)

        # ── 5. Slide stagnation history ───────────────────────────────────
        best_hist.pop(0)
        best_hist.append(fitG)

        # ── 6-7. Sub1 (PSO) + Sub2 (knowledge sampling) update ───────────
        P_new     = P.copy()
        Xsub_best = Pbest[subSize + np.argmin(fitP[subSize:])].copy()

        for i in range(N):
            if i < subSize:
                # Sub1: three-attractor PSO
                r1 = np.random.rand(dim)
                r2 = np.random.rand(dim)
                r3 = np.random.rand(dim)
                V[i] = np.clip(
                    w_inertia * V[i]
                    + c1 * r1 * (Pbest[i]    - P[i])
                    + c2 * r2 * (Gbest       - P[i])
                    + c3 * r3 * (Xsub_best   - P[i]),
                    -Vmax, Vmax)
                P_new[i] = np.clip(P[i] + V[i], lb, ub)
            else:
                # Sub2: SA-DKA-attenuated knowledge-guided sampling
                vf   = np.maximum(weight, 0.0)
                sv   = vf.sum()
                prob = vf / sv if sv > 0 else np.full(dim, 0.5)
                P_new[i] = (np.random.rand(dim) < prob).astype(float)

        # ── 8-9. Pool + EMDO selection ────────────────────────────────────
        pool     = np.vstack([Pbest, P_new])
        pool_bin = (pool > thres).astype(int)
        pool_fit = np.array([jFitness(X, y, pool_bin[i].astype(bool), opts)
                             for i in range(2 * N)])
        nhd_mat  = pairwise_nhd(pool_bin)
        alpha_cd = (t / T) ** 2                           # growing weight on crowding
        sel      = emdo_select(pool_fit, nhd_mat, N, alpha_cd)

        P       = pool[sel]
        fit_sel = pool_fit[sel]
        bin_sel = pool_bin[sel].astype(bool)

        # ── 10+11. Weight update FIRST (before Pbest/fitP), then update Pbest ──
        # CRITICAL ORDER: weight update must use OLD Pbest and OLD fitP.
        # If Pbest/fitP are updated first, fv_old==fv_new and delta==0,
        # making the weight update a no-op → SA-DKA and KGEF lose all signal.
        improved = fit_sel < fitP

        # ── 11. Improvement-feedback weight update (uses OLD Pbest, OLD fitP) ──
        for i in range(N):
            if improved[i]:
                delta  = fitP[i] - fit_sel[i]        # OLD fitP → delta > 0
                fv_new = bin_sel[i]
                fv_old = (Pbest[i] > thres)           # OLD Pbest → differs from fv_new
                change = np.logical_xor(fv_new, fv_old)
                weight[change & (fv_new > fv_old)] += delta   # newly added: reward
                weight[change & (fv_new < fv_old)] -= delta   # newly removed: penalise

        # ── 10. Update Pbest / fitP (AFTER weight update) ─────────────────
        Pbest = np.where(improved[:, None], P, Pbest)
        fitP  = np.minimum(fit_sel, fitP)

        # ── 12. KGEF elite perturbation ───────────────────────────────────
        for e in np.argsort(fitP)[:elite_k]:
            elite_bin = (Pbest[e] > thres).astype(int)
            mutant    = kgef_elite_flip(weight, elite_bin, flip_count, rand_flip_p)
            mfit      = jFitness(X, y, mutant.astype(bool), opts)
            if mfit < fitP[e]:
                Pbest[e] = mutant
                fitP[e]  = mfit

        # ── 13. Update Gbest ──────────────────────────────────────────────
        bi = np.argmin(fitP)
        if fitP[bi] < fitG:
            fitG  = float(fitP[bi])
            Gbest = Pbest[bi].copy()
        curve[t] = fitG

    return {
        "fitG":       fitG,
        "nf":         int((Gbest > thres).sum()),
        "curve":      curve,
        "nhd_curve":  nhd_curve,
        "lam_curve":  lam_curve,
        "avg_lambda": float(np.mean(lam_curve[1:])),
    }


# ══════════════════════════════════════════════════════════════════════════
# §7  Resume helpers
# ══════════════════════════════════════════════════════════════════════════
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


# ══════════════════════════════════════════════════════════════════════════
# §8  Main experiment loop
# ══════════════════════════════════════════════════════════════════════════
ensure_header()
done = load_done()

VER         = "MEL_KGEF_SADKA"
total_scope = len(ONLY_DATASETS) * NUM_RUNS          # 8 × 10 = 80

done_this_ver = sum(1 for (v, _, _) in done if v == VER)
print(f"Version        : {VER}")
print(f"Tasks done     : {done_this_ver} / {total_scope}")
print(f"MAX_TASKS      : {MAX_TASKS}")
print(f"CSV  → {CSV_PATH}")
print(f"NPY  → {CURVES_DIR}\n")

tasks_run = 0
for ds in ONLY_DATASETS:
    X, y = load_dataset(ds)
    print(f"\n{'='*70}")
    print(f"Dataset: {ds}  shape={X.shape}  classes={np.bincount(y)}")
    print(f"{'='*70}")

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
        res = run_MEL_KGEF_SADKA(X, y, OPTS)
        elapsed = time() - t0

        acc     = 1.0 - float(res["fitG"])
        nf      = int(res["nf"])
        nhd_c   = res["nhd_curve"]
        avg_nhd = float(np.mean(nhd_c[1:])) if np.any(nhd_c[1:]) else 0.0
        avg_lam = float(res["avg_lambda"])

        append_row({
            "Version":      VER,
            "Dataset":      ds,
            "Run":          run,
            "Accuracy":     f"{acc:.6f}",
            "Num_Features": nf,
            "Avg_NHD":      f"{avg_nhd:.6f}",
            "Avg_Lambda":   f"{avg_lam:.6f}",
            "Time_sec":     f"{elapsed:.2f}",
        })
        np.save(os.path.join(CURVES_DIR, f"curve_{VER}_{ds}_run{run}.npy"), res["curve"])
        np.save(os.path.join(CURVES_DIR, f"nhd_{VER}_{ds}_run{run}.npy"),   nhd_c)
        np.save(os.path.join(CURVES_DIR, f"lam_{VER}_{ds}_run{run}.npy"),   res["lam_curve"])

        tasks_run += 1
        total_done = done_this_ver + tasks_run
        print(f"  ✓ {VER} | run {run:2d} | Acc={acc:.4f} | Feat={nf:5d} | "
              f"λ_avg={avg_lam:.4f} | NHD={avg_nhd:.3f} | t={elapsed:7.1f}s  "
              f"[{total_done}/{total_scope}]")

print(f"\n✅ {VER} — 8 standard datasets complete.")
print(f"   Stroke: run Cell_Stroke with ONLY_DATASETS=['Stroke'], same CSV/CURVES_DIR.")


# ══════════════════════════════════════════════════════════════════════════
# §9  Paper notes: what each output field supports
#
#  Accuracy     → Table 1 (main comparison), Table 3 (ablation)
#  Num_Features → Table 2 (feature count), Fig 4 (boxplot stability)
#  Avg_NHD      → Fig 6 (diversity comparison: SA-DKA vs NHD-only vs KGEF)
#  Avg_Lambda   → Fig NEW (λ(t) trajectory: direct evidence of SA-DKA adapting)
#                 Key claim: "SA-DKA activates stronger attenuation during stagnation"
#  lam_curve    → Fig NEW iteration-level λ trace (supplement or Fig 9)
#  Time_sec     → Table 4 / Fig 7 (computational cost)
#
#  The Avg_Lambda field is the distinguishing diagnostic of SA-DKA:
#  If SA-DKA adapts to search state, datasets with difficult landscapes
#  (ALL3, Stroke) should show lower Avg_Lambda than stable datasets,
#  providing direct mechanistic evidence beyond accuracy improvement.
# ══════════════════════════════════════════════════════════════════════════
