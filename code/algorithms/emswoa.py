"""
EMSWOA — Dynamic Multi-Swarm Whale Optimization Algorithm based on Elite Tuning
================================================================================
Reference:
  Fahui Miao, Yong Wu, Guanjie Yan, Xiaomeng Si (2025).
  Dynamic multi-swarm whale optimization algorithm based on elite tuning
  for high-dimensional feature selection classification problems.
  Applied Soft Computing, Vol. 169, 112634.
  DOI: 10.1016/j.asoc.2024.112634

Exact Mathematical Formulation from 1-s2.0-S156849462401408X-main.pdf:
  1. Transfer function and discrete binarization (Eqs. 13-14):
     f(x) = 1 / (1 + exp(-2x))
     X_{i,j} = 1 if r < f(Delta X_{i,j}) else 0, where r ~ U(0, 1)

  2. Dynamic subpopulation grouping based on centroid distance (Algorithm 1):
     - groups(g) generated dynamically (Eq. 15), decreasing over iterations.
     - Subpopulation base size gnum_init = floor(N / groups) - 1 (Eq. 16).
     - Centroid distance dist_k = max_n || X_{k,n} - mean(X_k) ||_2 (Eq. 17).
       Remaining individuals assigned one-by-one to sub-swarms with larger dist_k.
     - Regrouping cycle R = 10.

  3. Local Sparsity Distance (LSD) diversity-preserving search (Eqs. 18-20):
     - Nearest neighbour fitness intervals l_{i,1}, l_{i,2} and maximum interval L.
     - con(i) = (l_{i,1} + l_{i,2}) / L (Eq. 18).
     - dis(i) = min(l_{i,1}, l_{i,2}) / max(l_{i,1}, l_{i,2}) (Eq. 19).
     - LSD(i) = (con(i) / max(con)) * (dis(i) / max(dis)) (Eq. 20).
     - Selective update: Individuals with ranking(i) <= N * rand are updated via
       X_{k,best} and X_{k,div} (having higher LSD). Others are directly inherited.

  4. Modified Whale Optimization movement (Eqs. 21-27):
     - Encircling prey (|A| < 1): X_new = X_{k,best} - A * D (Eqs. 21-22).
     - Search for prey (|A| >= 1): X_new = X_{k,div} - A * D (Eqs. 26-27).
     - Bubble-net attacking (p >= 0.5): X_new = D' * exp(b*l) * cos(2*pi*l) + X_{k,best} (Eqs. 23-25).

  5. Elite Tuning Strategy (Algorithm 2 & Eqs. 28-32):
     - Compares two consecutive generations of global elite solutions:
       X_{best}^{(t)} and X_{best}^{(t-1)} with flip probabilities FP^{(t)}, FP^{(t-1)}.
     - Consistency (X_{best}^{(t)}(j) == X_{best}^{(t-1)}(j)):
         * X_{best}=1, X_i=0: X_{i,j} = (r > alpha), alpha = 0.45 (Eq. 28).
         * X_{best}=0, X_i=1: X_{i,j} = (r > beta + #Selected / #All), beta = 0.2 (Eq. 29).
     - Inconsistency (X_{best}^{(t)}(j) != X_{best}^{(t-1)}(j) & X_{best}=1 & X_i=0):
         * If FP_{Xbest} < FP_{Xi}: FP updated via Eq. (30), X_{i,j} = (FP > lambda), lambda = 0.5 (Eq. 31).
         * Else: Delta X_{i,j} guided by Eq. (32).
"""
import numpy as np
from utils import jFitness, pairwise_nhd


def transfer_f(x):
    """Eq. (13): S-type discrete transfer function f(x) = 1 / (1 + exp(-2x))."""
    return 1.0 / (1.0 + np.exp(-2.0 * np.clip(x, -15.0, 15.0)))


def binarize(delta_x, dim):
    """Eq. (14): Discrete binarization using uniform random threshold."""
    prob = transfer_f(delta_x)
    r = np.random.rand(dim)
    mask = (r < prob)
    if mask.sum() < 3:
        # Guarantee minimum 3 features for k-NN classifier consistency
        top_idx = np.argsort(prob)[-3:]
        mask[top_idx] = True
    return mask


def compute_lsd(fitness_values):
    """
    Eqs. (18)-(20): Local Sparsity Distance (LSD) metric.
    Calculates con(i), dis(i), and LSD(i) based on fitness values.
    """
    n = len(fitness_values)
    if n <= 2:
        return np.ones(n)

    sorted_order = np.argsort(fitness_values)
    sorted_fits = fitness_values[sorted_order]

    intervals = np.diff(sorted_fits)
    L = float(np.max(intervals)) if len(intervals) > 0 and np.max(intervals) > 1e-12 else 1.0

    con = np.zeros(n)
    dis = np.zeros(n)

    # Internal individuals (excluding best and worst as in Section 3.2 Step 3)
    for rank in range(1, n - 1):
        l1 = sorted_fits[rank] - sorted_fits[rank - 1]
        l2 = sorted_fits[rank + 1] - sorted_fits[rank]
        con_val = (l1 + l2) / (L + 1e-12)
        dis_val = min(l1, l2) / (max(l1, l2) + 1e-12)
        idx = sorted_order[rank]
        con[idx] = con_val
        dis[idx] = dis_val

    max_con = np.max(con) if np.max(con) > 1e-12 else 1.0
    max_dis = np.max(dis) if np.max(dis) > 1e-12 else 1.0

    lsd = (con / max_con) * (dis / max_dis)
    return lsd


def run_EMSWOA(X, y, opts):
    """
    Execute EMSWOA strictly conforming to Miao et al. (ASOC 2025).
    """
    N = opts["N"]
    T = opts["T"]
    dim = X.shape[1]

    # Parameters from Table 3 in Miao et al. (2025)
    b = 1.0
    R = 10                  # Population reconstruction period R = 10
    alpha = 0.45            # Elite tuning threshold alpha = 0.45 (Eq. 28)
    beta = 0.20             # Elite tuning threshold beta = 0.20 (Eq. 29)
    lambda_thresh = 0.50    # Elite tuning threshold lambda = 0.50 (Eq. 31)

    # Generate sequence of subpopulation counts for each cycle g (Eq. 15)
    num_cycles = max(1, int(np.round(T / R)))
    group_max = min(20, max(2, N // 2))
    group_min = 1
    # Random sequence sorted in descending order (Eq. 15)
    raw_groups = np.round(group_min + np.random.rand(num_cycles) * (group_max - group_min)).astype(int)
    groups_seq = np.sort(np.clip(raw_groups, 1, max(1, N // 2)))[::-1]
    groups_seq[-1] = 1  # Last cycle combines into single population (Section 3.2 Step 1)

    # Continuous coordinate bounds
    lb, ub = -5.0, 5.0

    # ── Initialization ───────────────────────────────────────────────────────
    Delta_X = np.random.uniform(lb, ub, (N, dim))
    X_bin = np.zeros((N, dim), dtype=bool)
    fit = np.zeros(N)

    for i in range(N):
        X_bin[i] = binarize(Delta_X[i], dim)
        fit[i] = jFitness(X, y, X_bin[i], opts)

    # Track personal and global best
    fitG = float(np.min(fit))
    g_best_idx = int(np.argmin(fit))
    X_best = X_bin[g_best_idx].copy()
    Delta_X_best = Delta_X[g_best_idx].copy()

    # History of elite solutions for 2-generation Elite Tuning (Algorithm 2)
    X_best_prev = X_best.copy()
    Delta_X_best_prev = Delta_X_best.copy()

    curve = np.zeros(T + 1)
    curve[0] = fitG

    sub_assignments = np.zeros(N, dtype=int)
    current_cycle_idx = -1

    # ── Iterative Optimization ───────────────────────────────────────────────
    for t in range(1, T + 1):
        # ── 1. Dynamic Multi-Swarm Construction (Section 3.2 Step 1 & 2) ─────
        if (t - 1) % R == 0:
            current_cycle_idx = min(num_cycles - 1, (t - 1) // R)
            num_groups = int(groups_seq[current_cycle_idx])

            if num_groups <= 1:
                sub_assignments = np.zeros(N, dtype=int)
            else:
                # Base number of individuals per subpopulation (Eq. 16)
                gnum_init = max(1, int(np.floor(N / num_groups)) - 1)
                
                # Initial random assignment of gnum_init individuals per group
                perm = np.random.permutation(N)
                sub_assignments.fill(-1)
                assigned_count = 0
                for k in range(num_groups):
                    group_members = perm[assigned_count:assigned_count + gnum_init]
                    sub_assignments[group_members] = k
                    assigned_count += gnum_init

                remaining = perm[assigned_count:]

                # Calculate centroid distance dist_k for each subpopulation (Eq. 17)
                dist_k = np.zeros(num_groups)
                for k in range(num_groups):
                    k_idx = np.where(sub_assignments == k)[0]
                    if len(k_idx) > 0:
                        centroid_k = np.mean(Delta_X[k_idx], axis=0)
                        diffs = np.linalg.norm(Delta_X[k_idx] - centroid_k, axis=1)
                        dist_k[k] = np.max(diffs) if len(diffs) > 0 else 0.0

                # Allocate remaining individuals one-by-one based on dist_k (Eq. 17)
                sorted_groups = np.argsort(dist_k)[::-1]
                for idx_rem, ind in enumerate(remaining):
                    target_k = sorted_groups[idx_rem % num_groups]
                    sub_assignments[ind] = target_k

        # ── 2. Local Sparsity Distance (LSD) & Selective Update (Section 3.2) ──
        lsd = compute_lsd(fit)
        ranking = np.argsort(np.argsort(lsd)) + 1  # 1-indexed rank in ascending order

        # Determine individuals to update: ranking(i) <= N * rand
        threshold_rank = N * np.random.rand()
        update_flags = (ranking <= threshold_rank)
        # Ensure at least 30% of the swarm updates to prevent total freeze
        if not np.any(update_flags):
            update_flags[np.random.choice(N, size=max(2, N // 3), replace=False)] = True

        # Compute subpopulation bests X_{k,best}
        unique_groups = np.unique(sub_assignments)
        sub_best_pos = {}
        for k in unique_groups:
            k_members = np.where(sub_assignments == k)[0]
            k_best_idx = k_members[np.argmin(fit[k_members])]
            sub_best_pos[k] = Delta_X[k_best_idx].copy()

        # ── 3. Whale Movement Updating (Section 3.2 Step 4 & Eqs. 21-27) ──────
        a = 2.0 - 2.0 * (t / T)  # Linear decay from 2 to 0

        for i in range(N):
            if not update_flags[i]:
                # Individuals with high LSD are directly inherited (diversity preservation)
                continue

            k = sub_assignments[i]
            X_k_best = sub_best_pos[k]

            # Select X_{k,div}: candidate in subpopulation k with LSD > LSD(i)
            k_members = np.where(sub_assignments == k)[0]
            higher_lsd_members = [m for m in k_members if lsd[m] > lsd[i]]
            if len(higher_lsd_members) > 0:
                X_k_div = Delta_X[np.random.choice(higher_lsd_members)]
            else:
                X_k_div = Delta_X[np.random.choice(k_members)]

            r1 = np.random.rand(dim)
            r2 = np.random.rand(dim)
            A = 2.0 * a * r1 - a
            C = 2.0 * r2
            p = np.random.rand()

            if p < 0.5:
                A_scalar = np.mean(np.abs(A))
                if A_scalar < 1.0:
                    # Encircling prey (Eqs. 21-22)
                    D = np.abs(C * X_k_best - Delta_X[i])
                    Delta_X[i] = X_k_best - A * D
                else:
                    # Search for prey (Eqs. 26-27) using X_{k,div}
                    D = np.abs(C * X_k_div - Delta_X[i])
                    Delta_X[i] = X_k_div - A * D
            else:
                # Bubble-net attack: spiral surround (Eqs. 23-25)
                D_prime = np.abs(X_k_best - Delta_X[i])
                l = np.random.uniform(-1.0, 1.0)
                Delta_X[i] = D_prime * np.exp(b * l) * np.cos(2.0 * np.pi * l) + X_k_best

            # Boundary checks
            Delta_X[i] = np.clip(Delta_X[i], lb, ub)
            X_bin[i] = binarize(Delta_X[i], dim)

        # ── 4. Elite Tuning Strategy (Algorithm 2 & Section 3.3, Vectorized) ──
        FP_Xbest_curr = transfer_f(Delta_X_best)
        FP_Xbest_prev = transfer_f(Delta_X_best_prev)

        # Boolean masks across all dimensions
        mask_consistent = (X_best == X_best_prev)
        mask_inconsistent = (~mask_consistent) & (X_best == 1)

        for i in range(N):
            num_selected = int(np.sum(X_bin[i]))
            FP_Xi = transfer_f(Delta_X[i])

            # Case 1: Consistency (Eqs. 28-29)
            # 1a: X_best == 1 and X_i == 0 -> Eq. (28)
            idx_1a = mask_consistent & (X_best == 1) & (~X_bin[i])
            if np.any(idx_1a):
                r_1a = np.random.rand(np.sum(idx_1a))
                flip_1a = (r_1a > alpha)
                if np.any(flip_1a):
                    selected_dims = np.where(idx_1a)[0][flip_1a]
                    X_bin[i, selected_dims] = True
                    Delta_X[i, selected_dims] = np.maximum(Delta_X[i, selected_dims], 0.5)

            # 1b: X_best == 0 and X_i == 1 -> Eq. (29)
            idx_1b = mask_consistent & (X_best == 0) & X_bin[i]
            if np.any(idx_1b):
                thresh_1b = beta + (num_selected / dim)
                r_1b = np.random.rand(np.sum(idx_1b))
                flip_1b = (r_1b > thresh_1b)
                if np.any(flip_1b):
                    cleared_dims = np.where(idx_1b)[0][flip_1b]
                    X_bin[i, cleared_dims] = False
                    Delta_X[i, cleared_dims] = np.minimum(Delta_X[i, cleared_dims], -0.5)

            # Case 2: Inconsistency (Eqs. 30-32)
            # Condition: X_best != X_best_prev & X_best == 1 & X_i == 0
            idx_2 = mask_inconsistent & (~X_bin[i])
            if np.any(idx_2):
                idx_2_dims = np.where(idx_2)[0]
                cond_2a = (FP_Xbest_curr[idx_2_dims] < FP_Xi[idx_2_dims])
                
                # 2a: Eqs. (30)-(31)
                if np.any(cond_2a):
                    dims_2a = idx_2_dims[cond_2a]
                    diff_fp = np.abs(FP_Xbest_curr[dims_2a] - FP_Xbest_prev[dims_2a])
                    updated_fp = FP_Xi[dims_2a] + np.random.rand(len(dims_2a)) * diff_fp
                    flip_2a = (updated_fp > lambda_thresh)
                    if np.any(flip_2a):
                        X_bin[i, dims_2a[flip_2a]] = True
                        Delta_X[i, dims_2a[flip_2a]] = np.maximum(Delta_X[i, dims_2a[flip_2a]], 0.5)

                # 2b: Eq. (32)
                cond_2b = ~cond_2a
                if np.any(cond_2b):
                    dims_2b = idx_2_dims[cond_2b]
                    damping = (1.0 - t / T) * (1.0 / (1.0 + np.exp(FP_Xbest_curr[dims_2b] - FP_Xi[dims_2b])))
                    diff_coord = np.abs(Delta_X_best[dims_2b] - Delta_X[i, dims_2b])
                    Delta_X[i, dims_2b] += np.random.rand(len(dims_2b)) * damping * diff_coord
                    # Re-binarize tuned dimension via transfer function
                    prob_2b = transfer_f(Delta_X[i, dims_2b])
                    flip_2b = (np.random.rand(len(dims_2b)) < prob_2b)
                    X_bin[i, dims_2b[flip_2b]] = True

            # Ensure minimum 3 features
            if X_bin[i].sum() < 3:
                top3 = np.argsort(transfer_f(Delta_X[i]))[-3:]
                X_bin[i, top3] = True

            # Evaluate fitness of candidate solution
            fit[i] = jFitness(X, y, X_bin[i], opts)

        # ── 5. Update Global Elite Records ───────────────────────────────────
        current_best_idx = int(np.argmin(fit))
        if fit[current_best_idx] < fitG:
            fitG = float(fit[current_best_idx])
            X_best_prev = X_best.copy()
            Delta_X_best_prev = Delta_X_best.copy()
            X_best = X_bin[current_best_idx].copy()
            Delta_X_best = Delta_X[current_best_idx].copy()

        curve[t] = fitG

    # ── Final Population Diversity Metric ────────────────────────────────────
    nhd_mat = pairwise_nhd(X_bin.astype(int))
    avg_nhd = float(nhd_mat.sum() / (N * (N - 1))) if N > 1 else 0.0

    return {
        "mask": X_best,
        "Gbest": Delta_X_best,
        "fitG": fitG,
        "nf": int(X_best.sum()),
        "curve": curve,
        "nhd_curve": np.zeros(T + 1),
    }

