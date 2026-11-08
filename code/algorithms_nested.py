"""
Nested CV Adapted Algorithms
============================
Protocol Reference:
  - review_round_1/05_executable_experiment_plan.md, Section 4 & 7
  - review_round_1/04_detailed_supplementary_experiment_design.md, Section II

Implements the 5 core configurations for E1 and E5 under the BudgetEvaluator
interface (Max_FEs = 2000 candidate fitness requests):
  1. KDS_EL_TwoPhase (Full KDS-EL with TPS, KER, AIR, MI)
  2. MEL (Backbone dual-subpopulation PSO)
  3. MEL_MI (MEL + MI Seeding + AIR)
  4. KDS_EL_NoPool (KDS-EL with fixed ws=[0.90, 0.10], w/o TPS)
  5. bIRIME (Su et al., iScience 2024)
"""

import hashlib
import numpy as np
from utils import ker_flip, compute_mi_scores


# ══════════════════════════════════════════════════════════════════════════════
# 1. KDS-EL TwoPhase (Full)
# ══════════════════════════════════════════════════════════════════════════════

def run_nested_KDS_EL_TwoPhase(X_train, y_train, evaluator, opts, seed=7, enable_tps=True):
    """
    KDS-EL TwoPhase under BudgetEvaluator:
      - If enable_tps is True:
          Phase 1: ws = [0.70, 0.30] (feature compression)
          Phase 2: ws = [0.95, 0.05] (accuracy refinement)
          Switched at dynamic progress q >= 0.70
          Rescores Pbest at switch boundary (counted in budget)
      - If enable_tps is False (Strict Static / NoPool Mode):
          Fixed ws throughout evolution (default: [0.90, 0.10])
          ZERO switch checks, ZERO rescore requests, ZERO stall_counter resets.
    """
    np.random.seed(seed)
    dim = X_train.shape[1]
    N = opts.get("N", 20)
    half = N // 2
    thres = opts.get("thres", 0.6)
    lb, ub = 0.0, 1.0
    c1 = c2 = c3 = 2.0
    w = 0.9
    Vmax = (ub - lb) / 2
    decay = opts.get("weight_decay", 0.99)
    flip_count = max(1, int(opts.get("flip_frac", 0.01) * dim))
    rand_p = opts.get("rand_flip_p", 0.10)
    patience = opts.get("stall_patience", 20)
    elite_k = opts.get("elite_k", 3)

    if enable_tps:
        ws1 = opts.get("ws_phase1", [0.70, 0.30])
        ws2 = opts.get("ws_phase2", [0.95, 0.05])
        current_ws = ws1
    else:
        # Strict static mode: invariant weights throughout search
        current_ws = opts.get("ws", [0.90, 0.10])
        ws1 = current_ws
        ws2 = current_ws

    switched = False

    # MI computed ONLY on outer training data
    mi = compute_mi_scores(X_train, y_train)

    # Initialization
    P = np.zeros((N, dim))
    P[:half] = np.clip(mi + np.random.normal(0, 0.1, (half, dim)), lb, ub)
    P[half:] = np.random.uniform(lb, ub, (N - half, dim))
    V = np.zeros((N, dim))
    weight = np.zeros(dim)

    # Initial Evaluation (N = 20 requests)
    fit = np.zeros(N)
    for i in range(N):
        if not evaluator.has_budget():
            break
        fit[i] = evaluator.evaluate(P[i] > thres, ws=current_ws)

    fitP = fit.copy()
    Pbest = P.copy()
    bi = np.argmin(fitP)
    Gbest = Pbest[bi].copy()
    fitG = float(fitP[bi])

    stall_counter = 0
    generations = 0
    ker_attempts = 0
    ker_accepts = 0
    air_triggers = 0
    p2_valid_count = 0
    p2_total_count = 0

    while evaluator.has_budget():
        generations += 1

        # ── TPS Switch Boundary Check (ONLY if enable_tps is True) ──
        if enable_tps and not switched and evaluator.progress_q >= 0.70:
            switched = True
            current_ws = ws2
            evaluator.tps_switch_q = float(evaluator.progress_q)
            evaluator.tps_switch_E = int(evaluator.candidate_eval_requests)

            # Re-score all Pbest under Phase 2 weights
            for i in range(N):
                if not evaluator.has_budget():
                    break
                fitP[i] = evaluator.evaluate(Pbest[i] > thres, ws=current_ws)
                evaluator.tps_rescore_requests += 1

            bi = np.argmin(fitP)
            Gbest = Pbest[bi].copy()
            fitG = float(fitP[bi])
            stall_counter = 0

        if not evaluator.has_budget():
            break

        weight *= decay
        P_new = P.copy()
        Xsub_best = Pbest[half + np.argmin(fitP[half:])].copy()

        # Generate candidates
        for i in range(N):
            if i < half:
                # Subpopulation 1: continuous PSO
                r1, r2, r3 = np.random.rand(dim), np.random.rand(dim), np.random.rand(dim)
                V[i] = np.clip(
                    w * V[i]
                    + c1 * r1 * (Pbest[i] - P[i])
                    + c2 * r2 * (Gbest - P[i])
                    + c3 * r3 * (Xsub_best - P[i]),
                    -Vmax,
                    Vmax,
                )
                P_new[i] = np.clip(P[i] + V[i], lb, ub)
            else:
                # Subpopulation 2: probability sampling from weight
                p2_total_count += 1
                vf = np.maximum(weight, 0.0)
                sv = vf.sum()
                prob = vf / sv if sv > 0 else np.full(dim, 0.5)
                P_new[i] = (np.random.rand(dim) < prob).astype(float)
                if (P_new[i] > thres).sum() >= 3:
                    p2_valid_count += 1

        # Evaluate and In-Place Greedy Replacement
        for i in range(N):
            if not evaluator.has_budget():
                break
            fv_n = P_new[i] > thres
            fv_o = Pbest[i] > thres
            fit_new = evaluator.evaluate(fv_n, ws=current_ws)

            if fit_new < fitP[i]:
                inc = fitP[i] - fit_new
                Pbest[i] = P_new[i].copy()
                fitP[i] = fit_new
                change = np.logical_xor(fv_n, fv_o)
                case_emerge = np.where(change & (fv_n > fv_o))[0]
                case_disappear = np.where(change & (fv_n < fv_o))[0]
                for j in case_emerge:
                    weight[j] += inc
                for j in case_disappear:
                    weight[j] -= inc
            else:
                dec = fit_new - fitP[i]
                change = np.logical_xor(fv_n, fv_o)
                # Feature added in new candidate degraded fitness -> Penalize
                for j in np.where(change & (fv_n > fv_o))[0]:
                    weight[j] -= dec
                # Feature removed in new candidate degraded fitness -> Reward
                for j in np.where(change & (fv_n < fv_o))[0]:
                    weight[j] += dec

        P = P_new.copy()

        # KER Elite Mutation
        for e in np.argsort(fitP)[:elite_k]:
            if not evaluator.has_budget():
                break
            ker_attempts += 1
            elite_bin = (Pbest[e] > thres).astype(int)
            mutant = ker_flip(weight, elite_bin, flip_count, rand_p)
            mfit = evaluator.evaluate(mutant.astype(bool), ws=current_ws)
            if mfit < fitP[e]:
                Pbest[e] = mutant
                fitP[e] = mfit
                ker_accepts += 1

        # Update Gbest
        bi = np.argmin(fitP)
        if fitP[bi] < fitG:
            fitG = float(fitP[bi])
            Gbest = Pbest[bi].copy()
            stall_counter = 0
        else:
            stall_counter += 1

        # AIR Adaptive Reinitialization
        if stall_counter >= patience:
            air_triggers += 1
            order = np.argsort(fitP)
            restart = order[half:]
            for idx in restart:
                if not evaluator.has_budget():
                    break
                Pbest[idx] = np.clip(mi + np.random.normal(0, 0.1, dim), lb, ub)
                P[idx] = Pbest[idx].copy()
                fitP[idx] = evaluator.evaluate(Pbest[idx] > thres, ws=current_ws)
                if fitP[idx] < fitG:
                    fitG = float(fitP[idx])
                    Gbest = Pbest[idx].copy()
            stall_counter = 0

    mask = (Gbest > thres).astype(bool)
    if not mask.any():
        mask[np.argmax(Gbest)] = True

    return {
        "mask": mask,
        "fitG": fitG,
        "generations_completed": generations,
        "ker_attempts": ker_attempts,
        "ker_accepts": ker_accepts,
        "ker_accept_rate": float(ker_accepts / max(1, ker_attempts)),
        "air_triggers": air_triggers,
        "p2_valid_ratio": float(p2_valid_count / max(1, p2_total_count)),
        "stop_reason": "budget_exhausted" if not evaluator.has_budget() else "normal",
    }


# ══════════════════════════════════════════════════════════════════════════════
# 2. MEL (Backbone Algorithm)
# ══════════════════════════════════════════════════════════════════════════════

def run_nested_MEL(X_train, y_train, evaluator, opts, seed=7):
    """
    Original MEL Algorithm under BudgetEvaluator:
      - Dual-subpopulation PSO
      - Pure random initialization (no MI)
      - Fixed ws = [0.90, 0.10]
      - No KER, no AIR, no TPS
    """
    np.random.seed(seed)
    dim = X_train.shape[1]
    N = opts.get("N", 20)
    half = N // 2
    thres = opts.get("thres", 0.6)
    lb, ub = 0.0, 1.0
    c1 = c2 = c3 = 2.0
    w = 0.9
    Vmax = (ub - lb) / 2
    ws = opts.get("ws", [0.90, 0.10])

    weight = np.zeros(dim)
    P = np.random.uniform(lb, ub, (N, dim))
    V = np.zeros((N, dim))

    fit = np.zeros(N)
    for i in range(N):
        if not evaluator.has_budget():
            break
        fit[i] = evaluator.evaluate(P[i] > thres, ws=ws)

    fitP = fit.copy()
    Pbest = P.copy()
    bi = np.argmin(fitP)
    Gbest = P[bi].copy()
    fitG = float(fitP[bi])

    generations = 0

    while evaluator.has_budget():
        generations += 1
        Xsub_best = Pbest[half + np.argmin(fitP[half:])].copy()

        for i in range(N):
            if not evaluator.has_budget():
                break

            if i < half:
                for d in range(dim):
                    r1, r2, r3 = np.random.rand(), np.random.rand(), np.random.rand()
                    VB = (
                        w * V[i, d]
                        + c1 * r1 * (Pbest[i, d] - P[i, d])
                        + c2 * r2 * (Gbest[d] - P[i, d])
                        + c3 * r3 * (Xsub_best[d] - P[i, d])
                    )
                    V[i, d] = np.clip(VB, -Vmax, Vmax)
                    P[i, d] = np.clip(P[i, d] + V[i, d], lb, ub)
            else:
                vf = np.maximum(weight, 0.0)
                sv = vf.sum()
                if sv > 0:
                    for d in range(dim):
                        P[i, d] = 1.0 if vf[d] / sv > np.random.rand() else 0.0
                else:
                    P[i] = (np.random.rand(dim) < 0.5).astype(float)

            fv_n = P[i] > thres
            fit_i = evaluator.evaluate(fv_n, ws=ws)
            fv_o = Pbest[i] > thres

            if fit_i < fitP[i]:
                inc = fitP[i] - fit_i
                Pbest[i] = P[i].copy()
                fitP[i] = fit_i
                change = np.logical_xor(fv_n, fv_o)
                for j in np.where(change & (fv_n > fv_o))[0]:
                    weight[j] += inc
                for j in np.where(change & (fv_n < fv_o))[0]:
                    weight[j] -= inc
            else:
                dec = fit_i - fitP[i]
                change = np.logical_xor(fv_o, fv_n)
                for j in np.where(change & (fv_o > fv_n))[0]:
                    weight[j] -= dec
                for j in np.where(change & (fv_o < fv_n))[0]:
                    weight[j] += dec

            if fitP[i] < fitG:
                Gbest = Pbest[i].copy()
                fitG = float(fitP[i])

    mask = (Gbest > thres).astype(bool)
    if not mask.any():
        mask[np.argmax(Gbest)] = True

    return {
        "mask": mask,
        "fitG": fitG,
        "generations_completed": generations,
        "stop_reason": "budget_exhausted" if not evaluator.has_budget() else "normal",
    }


# ══════════════════════════════════════════════════════════════════════════════
# 3. MEL_MI (MEL + MI Seeding + AIR)
# ══════════════════════════════════════════════════════════════════════════════

def run_nested_MEL_MI(X_train, y_train, evaluator, opts, seed=7):
    """MEL with MI-guided initialization and AIR, without KER or TPS."""
    np.random.seed(seed)
    dim = X_train.shape[1]
    N = opts.get("N", 20)
    half = N // 2
    thres = opts.get("thres", 0.6)
    lb, ub = 0.0, 1.0
    c1 = c2 = c3 = 2.0
    w = 0.9
    Vmax = (ub - lb) / 2
    patience = opts.get("stall_patience", 20)
    ws = opts.get("ws", [0.90, 0.10])

    mi = compute_mi_scores(X_train, y_train)
    P = np.zeros((N, dim))
    P[:half] = np.clip(mi + np.random.normal(0, 0.1, (half, dim)), lb, ub)
    P[half:] = np.random.uniform(lb, ub, (N - half, dim))
    V = np.zeros((N, dim))
    weight = np.zeros(dim)

    fit = np.zeros(N)
    for i in range(N):
        if not evaluator.has_budget():
            break
        fit[i] = evaluator.evaluate(P[i] > thres, ws=ws)

    fitP = fit.copy()
    Pbest = P.copy()
    bi = np.argmin(fitP)
    Gbest = P[bi].copy()
    fitG = float(fitP[bi])

    generations = 0
    stall_counter = 0
    air_triggers = 0

    while evaluator.has_budget():
        generations += 1
        prev_fitG = fitG
        Xsub_best = Pbest[half + np.argmin(fitP[half:])].copy()

        for i in range(N):
            if not evaluator.has_budget():
                break

            if i < half:
                r1, r2, r3 = np.random.rand(dim), np.random.rand(dim), np.random.rand(dim)
                V[i] = np.clip(
                    w * V[i]
                    + c1 * r1 * (Pbest[i] - P[i])
                    + c2 * r2 * (Gbest - P[i])
                    + c3 * r3 * (Xsub_best - P[i]),
                    -Vmax,
                    Vmax,
                )
                P[i] = np.clip(P[i] + V[i], lb, ub)
            else:
                vf = np.maximum(weight, 0.0)
                sv = vf.sum()
                prob = vf / sv if sv > 0 else np.full(dim, 0.5)
                P[i] = (np.random.rand(dim) < prob).astype(float)

            fv_n = P[i] > thres
            fit_i = evaluator.evaluate(fv_n, ws=ws)
            fv_o = Pbest[i] > thres

            if fit_i < fitP[i]:
                inc = fitP[i] - fit_i
                Pbest[i] = P[i].copy()
                fitP[i] = fit_i
                change = np.logical_xor(fv_n, fv_o)
                for j in np.where(change & (fv_n > fv_o))[0]:
                    weight[j] += inc
                for j in np.where(change & (fv_n < fv_o))[0]:
                    weight[j] -= inc
            else:
                dec = fit_i - fitP[i]
                change = np.logical_xor(fv_o, fv_n)
                for j in np.where(change & (fv_o > fv_n))[0]:
                    weight[j] -= dec
                for j in np.where(change & (fv_o < fv_n))[0]:
                    weight[j] += dec

            if fitP[i] < fitG:
                Gbest = Pbest[i].copy()
                fitG = float(fitP[i])

        if fitG < prev_fitG:
            stall_counter = 0
        else:
            stall_counter += 1

        if stall_counter >= patience:
            air_triggers += 1
            order = np.argsort(fitP)
            restart = order[half:]
            for idx in restart:
                if not evaluator.has_budget():
                    break
                Pbest[idx] = np.clip(mi + np.random.normal(0, 0.1, dim), lb, ub)
                P[idx] = Pbest[idx].copy()
                fitP[idx] = evaluator.evaluate(Pbest[idx] > thres, ws=ws)
                if fitP[idx] < fitG:
                    fitG = float(fitP[idx])
                    Gbest = Pbest[idx].copy()
            stall_counter = 0

    mask = (Gbest > thres).astype(bool)
    if not mask.any():
        mask[np.argmax(Gbest)] = True

    return {
        "mask": mask,
        "fitG": fitG,
        "generations_completed": generations,
        "air_triggers": air_triggers,
        "stop_reason": "budget_exhausted" if not evaluator.has_budget() else "normal",
    }


# ══════════════════════════════════════════════════════════════════════════════
# 4. KDS_EL_NoPool (Static ws=[0.90, 0.10], w/o TPS)
# ══════════════════════════════════════════════════════════════════════════════

def run_nested_KDS_EL_NoPool(X_train, y_train, evaluator, opts, seed=7):
    """
    KDS-EL without TwoPhase Strategy (fixed ws=[0.90, 0.10]):
      - Strict enable_tps=False: ZERO switch, ZERO rescore requests, ZERO stall reset.
    """
    opts_nopool = dict(opts)
    opts_nopool["ws"] = opts.get("ws", [0.90, 0.10])
    res = run_nested_KDS_EL_TwoPhase(
        X_train, y_train, evaluator, opts_nopool, seed=seed, enable_tps=False
    )
    return res


# ══════════════════════════════════════════════════════════════════════════════
# 5. bIRIME (Su et al., iScience 2024)
# ══════════════════════════════════════════════════════════════════════════════

def sigmf_transfer(x):
    return 1.0 / (1.0 + np.exp(-np.clip(10.0 * (x - 0.5), -15.0, 15.0)))


def bIRIME_binarize(x_cont, dim):
    prob = sigmf_transfer(x_cont)
    b = np.random.rand(dim) < prob
    if not b.any():
        b[np.random.choice(dim, min(3, dim), replace=False)] = True
    return b


def run_nested_bIRIME(X_train, y_train, evaluator, opts, seed=7):
    """
    bIRIME under BudgetEvaluator:
      - Logistic S-shaped transfer function
      - Soft-Besiege, Soft-rime search, CMS, and RS
      - Fixed ws = [0.90, 0.10]
    """
    np.random.seed(seed)
    dim = X_train.shape[1]
    N = opts.get("N", 20)
    T = opts.get("T", max(1, evaluator.max_fes // N))
    lb, ub = 0.0, 1.0
    W_soft = 5.0
    Limits = 50
    ws = opts.get("ws", [0.90, 0.10])

    P = np.random.uniform(lb, ub, (N, dim))
    P_bin = np.zeros((N, dim), dtype=bool)
    fit = np.zeros(N)

    for i in range(N):
        if not evaluator.has_budget():
            break
        P_bin[i] = bIRIME_binarize(P[i], dim)
        fit[i] = evaluator.evaluate(P_bin[i], ws=ws)

    g_idx = np.argmin(fit)
    Gbest = P[g_idx].copy()
    Gbest_bin = P_bin[g_idx].copy()
    fitG = float(fit[g_idx])

    SalpTrial = np.zeros(N, dtype=int)
    generations = 0

    while evaluator.has_budget():
        generations += 1
        t = generations
        t_ratio = min(1.0, t / float(T))
        RimeFactor = (
            (np.random.rand() - 0.5) * 2.0
            * np.cos(np.pi * t / (max(1.0, T / 10.0)))
            * (1.0 - np.round(t_ratio * W_soft) / W_soft)
        )
        E = np.sqrt(t_ratio)
        c = 2.0 * (1.0 - t_ratio)

        norm_val = np.sqrt(np.sum(fit**2)) + 1e-12
        norm_rates = fit / norm_val
        P_new = P.copy()

        for i in range(N):
            if not evaluator.has_budget():
                break

            Escaping_Energy = c * (2.0 * np.random.rand() - 1.0)
            if np.abs(Escaping_Energy) >= 1.0:
                # Soft-Besiege
                r = np.random.rand()
                rand_idx = np.random.randint(0, N)
                X_rand = P[rand_idx]
                if r < 0.5:
                    P_new[i] = X_rand - np.random.rand() * np.abs(X_rand - 2.0 * np.random.rand() * P[i])
                else:
                    P_new[i] = (Gbest - np.mean(P, axis=0)) - np.random.rand() * np.random.rand()
            else:
                # Soft-rime Search & Hard-rime Puncture
                for j in range(dim):
                    if np.random.rand() < E:
                        P_new[i, j] = Gbest[j] + RimeFactor * ((ub - lb) * np.random.rand() + lb)
                    if np.random.rand() < norm_rates[i]:
                        P_new[i, j] = Gbest[j]

            P_new[i] = np.clip(P_new[i], lb, ub)
            bin_cand = bIRIME_binarize(P_new[i], dim)
            f_cand = evaluator.evaluate(bin_cand, ws=ws)

            if f_cand < fit[i]:
                P[i] = P_new[i].copy()
                P_bin[i] = bin_cand.copy()
                fit[i] = f_cand
                SalpTrial[i] = 0
            else:
                SalpTrial[i] += 1

            if fit[i] < fitG:
                Gbest = P[i].copy()
                Gbest_bin = P_bin[i].copy()
                fitG = float(fit[i])

            # ── Composite Mutation Strategies (CMS: U1, U2, U3) ──
            other_indices = [idx for idx in range(N) if idx != i]
            if len(other_indices) >= 3 and evaluator.has_budget():
                # Strategy 1: DE/rand/1/bin (F1=1.0, Cr1=0.1)
                k1 = np.random.choice(other_indices, 3, replace=False)
                j_rand1 = np.random.randint(0, dim)
                u1 = P[i].copy()
                cross1 = (np.random.rand(dim) < 0.1)
                cross1[j_rand1] = True
                u1[cross1] = P[k1[0], cross1] + 1.0 * (P[k1[1], cross1] - P[k1[2], cross1])
                u1 = np.clip(u1, lb, ub)
                u1_bin = bIRIME_binarize(u1, dim)
                fit_u1 = evaluator.evaluate(u1_bin, ws=ws) if evaluator.has_budget() else float("inf")

                # Strategy 2: DE/rand/2/bin (F2=0.8, Cr2=0.2)
                if len(other_indices) >= 5:
                    k2 = np.random.choice(other_indices, 5, replace=False)
                    u2_diff = (P[k2[1]] - P[k2[2]]) + (P[k2[3]] - P[k2[4]])
                else:
                    k2 = np.random.choice(other_indices, 3, replace=False)
                    u2_diff = P[k2[1]] - P[k2[2]]
                j_rand2 = np.random.randint(0, dim)
                u2 = P[i].copy()
                cross2 = (np.random.rand(dim) < 0.2)
                cross2[j_rand2] = True
                u2[cross2] = P[k2[0], cross2] + 0.8 * u2_diff[cross2]
                u2 = np.clip(u2, lb, ub)
                u2_bin = bIRIME_binarize(u2, dim)
                fit_u2 = evaluator.evaluate(u2_bin, ws=ws) if evaluator.has_budget() else float("inf")

                # Strategy 3: current-to-rand/1/bin (F3=1.0, Cr3=0.9)
                k3 = np.random.choice(other_indices, 3, replace=False)
                j_rand3 = np.random.randint(0, dim)
                u3 = P[i].copy()
                cross3 = (np.random.rand(dim) < 0.9)
                cross3[j_rand3] = True
                u3[cross3] = (
                    P[i, cross3]
                    + np.random.rand() * (P[k3[0], cross3] - P[i, cross3])
                    + 1.0 * (P[k3[1], cross3] - P[k3[2], cross3])
                )
                u3 = np.clip(u3, lb, ub)
                u3_bin = bIRIME_binarize(u3, dim)
                fit_u3 = evaluator.evaluate(u3_bin, ws=ws) if evaluator.has_budget() else float("inf")

                com_fits = [fit_u1, fit_u2, fit_u3]
                best_com_idx = int(np.argmin(com_fits))
                com_poss = [u1, u2, u3]
                com_bins = [u1_bin, u2_bin, u3_bin]

                best_cms_fit = com_fits[best_com_idx]
                if best_cms_fit < fit[i]:
                    P[i] = com_poss[best_com_idx].copy()
                    P_bin[i] = com_bins[best_com_idx].copy()
                    fit[i] = best_cms_fit
                    SalpTrial[i] = 0
                    if best_cms_fit < fitG:
                        fitG = float(best_cms_fit)
                        Gbest = P[i].copy()
                        Gbest_bin = P_bin[i].copy()
                else:
                    SalpTrial[i] += 1

            # ── Restart Strategy (RS) ──
            if SalpTrial[i] >= Limits and evaluator.has_budget():
                T1 = np.random.uniform(lb, ub, dim)
                T2 = np.clip(np.random.uniform(lb, ub, dim) - P[i], lb, ub)

                T1_bin = bIRIME_binarize(T1, dim)
                fT1 = evaluator.evaluate(T1_bin, ws=ws) if evaluator.has_budget() else float("inf")
                T2_bin = bIRIME_binarize(T2, dim)
                fT2 = evaluator.evaluate(T2_bin, ws=ws) if evaluator.has_budget() else float("inf")

                if fT1 < fT2:
                    P[i] = T1.copy()
                    P_bin[i] = T1_bin.copy()
                    fit[i] = fT1
                else:
                    P[i] = T2.copy()
                    P_bin[i] = T2_bin.copy()
                    fit[i] = fT2

                SalpTrial[i] = 0
                if fit[i] < fitG:
                    fitG = float(fit[i])
                    Gbest = P[i].copy()
                    Gbest_bin = P_bin[i].copy()

    mask = Gbest_bin
    if not mask.any():
        mask[np.argmax(Gbest)] = True

    return {
        "mask": mask,
        "fitG": fitG,
        "generations_completed": generations,
        "stop_reason": "budget_exhausted" if not evaluator.has_budget() else "normal",
    }


# ══════════════════════════════════════════════════════════════════════════════
# 6. BPSO (Binary Particle Swarm Optimization - Kennedy & Eberhart 1997)
# ══════════════════════════════════════════════════════════════════════════════

def run_nested_BPSO(X_train, y_train, evaluator, opts, seed=7):
    """
    Standard Binary Particle Swarm Optimization under BudgetEvaluator.
    """
    np.random.seed(seed)
    dim = X_train.shape[1]
    N = opts.get("N", 20)
    ws = opts.get("ws", [0.90, 0.10])
    w, c1, c2 = 0.9, 2.0, 2.0
    Vmax = 6.0

    P = (np.random.rand(N, dim) < 0.5).astype(float)
    V = np.zeros((N, dim))

    fit = np.zeros(N)
    for i in range(N):
        if not evaluator.has_budget():
            break
        m = (P[i] > 0.5)
        if not m.any():
            m[np.random.randint(dim)] = True
        fit[i] = evaluator.evaluate(m, ws=ws)

    Pbest, fitP = P.copy(), fit.copy()
    bi = np.argmin(fitP)
    Gbest, fitG = Pbest[bi].copy(), float(fitP[bi])
    generations = 0

    while evaluator.has_budget():
        generations += 1
        r1, r2 = np.random.rand(N, dim), np.random.rand(N, dim)
        V = w * V + c1 * r1 * (Pbest - P) + c2 * r2 * (Gbest - P)
        V = np.clip(V, -Vmax, Vmax)

        prob = 1.0 / (1.0 + np.exp(-V))
        P = (np.random.rand(N, dim) < prob).astype(float)

        for i in range(N):
            if not evaluator.has_budget():
                break
            m = (P[i] > 0.5)
            if not m.any():
                m[np.random.randint(dim)] = True
            f = evaluator.evaluate(m, ws=ws)
            if f < fitP[i]:
                Pbest[i] = P[i].copy()
                fitP[i] = f
            if f < fitG:
                fitG = float(f)
                Gbest = P[i].copy()

    mask = (Gbest > 0.5)
    if not mask.any():
        mask[np.random.randint(dim)] = True

    return {
        "mask": mask,
        "fitG": fitG,
        "generations_completed": generations,
        "stop_reason": "budget_exhausted" if not evaluator.has_budget() else "normal",
    }


# ══════════════════════════════════════════════════════════════════════════════
# 7. FWPSO (Feature Weighting PSO - Wang & Jia 2022)
# ══════════════════════════════════════════════════════════════════════════════

def run_nested_FWPSO(X_train, y_train, evaluator, opts, seed=7):
    """
    Feature Weighting Particle Swarm Optimization under BudgetEvaluator.
    """
    np.random.seed(seed)
    dim = X_train.shape[1]
    N = opts.get("N", 20)
    thres = opts.get("thres", 0.6)
    ws = opts.get("ws", [0.90, 0.10])
    c1 = c2 = 2.0
    w = 0.9
    Vmax = 0.5

    weight = np.zeros(dim)
    P = np.random.rand(N, dim)
    V = np.zeros((N, dim))

    fitP = np.zeros(N)
    for i in range(N):
        if not evaluator.has_budget():
            break
        m = (P[i] > thres)
        if not m.any():
            m[np.random.randint(dim)] = True
        fitP[i] = evaluator.evaluate(m, ws=ws)

    Pbest = P.copy()
    bi = np.argmin(fitP)
    Gbest, fitG = Pbest[bi].copy(), float(fitP[bi])
    generations = 0

    while evaluator.has_budget():
        generations += 1
        for i in range(N):
            if not evaluator.has_budget():
                break
            r1, r2 = np.random.rand(dim), np.random.rand(dim)
            V[i] = w * V[i] + c1 * r1 * (Pbest[i] - P[i]) + c2 * r2 * (Gbest - P[i])
            V[i] = np.clip(V[i], -Vmax, Vmax)

            vf = np.maximum(weight, 0.0)
            sv = vf.sum()
            if sv > 0 and np.random.rand() < 0.3:
                prob = vf / sv
                P[i] = (np.random.rand(dim) < prob).astype(float)
            else:
                P[i] = np.clip(P[i] + V[i], 0.0, 1.0)

            m = (P[i] > thres)
            if not m.any():
                m[np.random.randint(dim)] = True
            f = evaluator.evaluate(m, ws=ws)
            pb = (Pbest[i] > thres)
            pn = m
            if f < fitP[i]:
                inc = fitP[i] - f
                change = np.logical_xor(pb, pn)
                weight[change & pn & (~pb)] += inc
                weight[change & pb & (~pn)] -= inc
                Pbest[i] = P[i].copy()
                fitP[i] = f
            if f < fitG:
                fitG = float(f)
                Gbest = P[i].copy()

    mask = (Gbest > thres)
    if not mask.any():
        mask[np.random.randint(dim)] = True

    return {
        "mask": mask,
        "fitG": fitG,
        "generations_completed": generations,
        "stop_reason": "budget_exhausted" if not evaluator.has_budget() else "normal",
    }


# ══════════════════════════════════════════════════════════════════════════════
# 8. SaWDE (Self-Adaptive Weighted DE - Wang et al. TEVC 2021)
# ══════════════════════════════════════════════════════════════════════════════

def run_nested_SaWDE(X_train, y_train, evaluator, opts, seed=7):
    """
    Self-Adaptive Weighted Differential Evolution under BudgetEvaluator.
    """
    np.random.seed(seed)
    dim = X_train.shape[1]
    N = opts.get("N", 20)
    thres = opts.get("thres", 0.6)
    ws = opts.get("ws", [0.90, 0.10])

    P = np.random.rand(N, dim)
    fit = np.zeros(N)
    for i in range(N):
        if not evaluator.has_budget():
            break
        m = (P[i] > thres)
        if not m.any():
            m[np.random.randint(dim)] = True
        fit[i] = evaluator.evaluate(m, ws=ws)

    bi = np.argmin(fit)
    Gbest = P[bi].copy()
    fitG = float(fit[bi])

    w_strat = np.ones(3) / 3.0
    F_hist = [0.5] * 3
    CR_hist = [0.5] * 3
    generations = 0

    while evaluator.has_budget():
        generations += 1
        w_norm = w_strat / (w_strat.sum() + 1e-12)
        success = np.zeros(3)
        count = np.zeros(3)
        P_new = P.copy()

        for i in range(N):
            if not evaluator.has_budget():
                break
            s = np.random.choice(3, p=w_norm)
            F = np.clip(np.random.normal(F_hist[s], 0.1), 0.1, 1.0)
            CR = np.clip(np.random.normal(CR_hist[s], 0.1), 0.0, 1.0)

            idx = list(range(N))
            idx.remove(i)
            r1, r2, r3 = np.random.choice(idx, 3, replace=False)

            if s == 0:
                mut = P[r1] + F * (P[r2] - P[r3])
            elif s == 1:
                mut = P[i] + F * (Gbest - P[i]) + F * (P[r1] - P[r2])
            else:
                mut = Gbest + F * (P[r1] - P[r2])

            mut = np.clip(mut, 0.0, 1.0)
            cross = np.random.rand(dim) < CR
            if not cross.any():
                cross[np.random.randint(dim)] = True
            trial = np.where(cross, mut, P[i])

            m = (trial > thres)
            if not m.any():
                m[np.random.randint(dim)] = True
            f_trial = evaluator.evaluate(m, ws=ws)
            if f_trial <= fit[i]:
                P_new[i] = trial
                fit[i] = f_trial
                success[s] += 1
                F_hist[s] = 0.9 * F_hist[s] + 0.1 * F
                CR_hist[s] = 0.9 * CR_hist[s] + 0.1 * CR
                if f_trial < fitG:
                    fitG = float(f_trial)
                    Gbest = trial.copy()
            count[s] += 1

        sr = np.where(count > 0, success / count, 0.0)
        w_strat = 0.9 * w_strat + 0.1 * (sr + 0.01)
        w_strat = w_strat / (w_strat.sum() + 1e-12)
        P = P_new

    mask = (Gbest > thres)
    if not mask.any():
        mask[np.random.randint(dim)] = True

    return {
        "mask": mask,
        "fitG": fitG,
        "generations_completed": generations,
        "stop_reason": "budget_exhausted" if not evaluator.has_budget() else "normal",
    }


# ══════════════════════════════════════════════════════════════════════════════
# 9. PSO_CSM (Comprehensive Scoring Framework PSO - Wei et al. 2025)
# ══════════════════════════════════════════════════════════════════════════════

def run_nested_PSO_CSM(X_train, y_train, evaluator, opts, seed=7):
    """
    PSO with Comprehensive Scoring Framework under BudgetEvaluator.
    """
    from sklearn.feature_selection import f_classif

    np.random.seed(seed)
    dim = X_train.shape[1]
    N = opts.get("N", 20)
    ws = opts.get("ws", [0.90, 0.10])
    Vmax = 0.5
    w_inertia = 0.9
    c1 = c2 = 2.0
    w_rel = opts.get("w_rel", 0.5)
    w_fb = opts.get("w_fb", 0.5)
    R_csm = opts.get("R_csm", 10)
    sigma = opts.get("sigma", 0.04)
    min_feats = max(10, dim // 100)

    # 1. Feature Relevance (F-score computed strictly on outer train)
    F, _ = f_classif(X_train, y_train)
    F = np.nan_to_num(F, nan=0.0, posinf=0.0, neginf=0.0)
    f_max = F.max()
    rel = F / (f_max + 1e-9) if f_max > 0 else np.full(dim, 0.5)

    # 2. Initialization
    init_prob = np.clip(0.1 + 0.8 * rel, 0.05, 0.95)
    P = (np.random.rand(N, dim) < init_prob).astype(float)
    V = np.zeros((N, dim))

    fit = np.zeros(N)
    for i in range(N):
        if not evaluator.has_budget():
            break
        m = P[i].astype(bool)
        if not m.any():
            m[np.random.randint(dim)] = True
        fit[i] = evaluator.evaluate(m, ws=ws)

    Pbest = P.copy()
    fitP = fit.copy()
    bi = np.argmin(fit)
    gbest = P[bi].copy()
    fitG = float(fit[bi])

    active = np.ones(dim, dtype=bool)
    generations = 0

    while evaluator.has_budget():
        generations += 1
        r1 = np.random.rand(N, dim)
        r2 = np.random.rand(N, dim)
        V = np.clip(w_inertia * V + c1 * r1 * (Pbest - P) + c2 * r2 * (gbest - P), -Vmax, Vmax)
        prob = 1.0 / (1.0 + np.exp(-V))
        P_new = (np.random.rand(N, dim) < prob).astype(float)
        P_new[:, ~active] = 0.0

        for i in range(N):
            if not evaluator.has_budget():
                break
            m = P_new[i].astype(bool)
            if not m.any():
                m[np.random.choice(np.where(active)[0] if active.any() else dim)] = True
            f_new = evaluator.evaluate(m, ws=ws)
            if f_new < fitP[i]:
                Pbest[i] = P_new[i].copy()
                fitP[i] = f_new
            if f_new < fitG:
                fitG = float(f_new)
                gbest = P_new[i].copy()

        P = P_new

        # Comprehensive scoring feature reduction
        if generations % R_csm == 0:
            pb_bin = (Pbest[:, active] > 0.5).astype(float)
            fb_active = pb_bin.mean(axis=0)
            fb_norm = fb_active / (fb_active.max() + 1e-9)
            rel_active = rel[active]
            score = w_rel * rel_active + w_fb * fb_norm

            n_remove = int(sigma * min(1.0, generations / 100.0) * active.sum())
            if n_remove > 0 and (active.sum() - n_remove) >= min_feats:
                local_low = np.argsort(score)[:n_remove]
                active_idx = np.where(active)[0]
                global_low = active_idx[local_low]
                active[global_low] = False
                P[:, global_low] = 0.0
                Pbest[:, global_low] = 0.0
                gbest[global_low] = 0.0

    mask = gbest.astype(bool)
    if not mask.any():
        mask[np.random.randint(dim)] = True

    return {
        "mask": mask,
        "fitG": fitG,
        "generations_completed": generations,
        "stop_reason": "budget_exhausted" if not evaluator.has_budget() else "normal",
    }


# ══════════════════════════════════════════════════════════════════════════════
# 10. BinCOA (Binary Crayfish Optimization Algorithm - Shikoun et al. 2024)
# ══════════════════════════════════════════════════════════════════════════════

def _bincoa_sigmoid(x):
    return 1.0 / (1.0 + np.exp(-np.clip(x, -15.0, 15.0)))


def _bincoa_binarize(x_cont, dim):
    prob = _bincoa_sigmoid(x_cont)
    b = (np.random.rand(dim) >= prob)
    if not b.any():
        b[np.random.choice(dim, min(3, dim), replace=False)] = True
    return b


def run_nested_BinCOA(X_train, y_train, evaluator, opts, seed=7):
    """
    Binary Crayfish Optimization Algorithm under BudgetEvaluator.
    """
    np.random.seed(seed)
    dim = X_train.shape[1]
    N = opts.get("N", 20)
    ws = opts.get("ws", [0.90, 0.10])
    lb, ub = -3.0, 3.0
    sigma_refract = 1.0

    Cr = np.random.uniform(lb, ub, (N, dim))
    mid = (lb + ub) / 2.0
    Cr_star = np.clip(mid + mid / sigma_refract - Cr / sigma_refract, lb, ub)

    candidates = np.vstack([Cr, Cr_star])
    cand_bin = np.zeros((2 * N, dim), dtype=bool)
    cand_fit = np.zeros(2 * N)

    for i in range(2 * N):
        if not evaluator.has_budget():
            break
        cand_bin[i] = _bincoa_binarize(candidates[i], dim)
        cand_fit[i] = evaluator.evaluate(cand_bin[i], ws=ws)

    best_indices = np.argsort(cand_fit)[:N]
    Cr = candidates[best_indices].copy()
    Cr_bin = cand_bin[best_indices].copy()
    fit = cand_fit[best_indices].copy()

    CrG = Cr[0].copy()
    CrG_bin = Cr_bin[0].copy()
    fitG = float(fit[0])
    CrL = Cr[0].copy()

    generations = 0

    while evaluator.has_budget():
        generations += 1
        t = generations
        temp = np.random.rand() * 15.0 + 20.0
        Cr_new = Cr.copy()

        if temp > 30.0:
            Cr_shade = (CrG + CrL) / 2.0
            for i in range(N):
                if np.random.rand() < 0.5:
                    S = 2.0 - min(1.0, t / 100.0)
                    Cr_new[i] = Cr[i] + S * np.random.rand() * (Cr_shade - Cr[i])
                else:
                    other_z = [idx for idx in range(N) if idx != i]
                    z = np.random.choice(other_z) if other_z else i
                    Cr_new[i] = Cr[i] - Cr[z] + Cr_shade
        else:
            mu, sigma_p, W_p = 25.0, 3.0, 1.0
            p = W_p * (1.0 / (np.sqrt(2.0 * np.pi) * sigma_p)) * np.exp(-((temp - mu) ** 2) / (sigma_p ** 2))
            for i in range(N):
                k_food = 3.0
                Q = k_food * np.random.rand() * (fit[i] / (fitG + 1e-12))
                if Q > 2.0:
                    Cr_food = np.exp(-1.0 / max(Q, 1e-6)) * CrG
                    angle = 2.0 * np.pi * np.random.rand()
                    Cr_new[i] = Cr[i] + Cr_food * p * (np.cos(angle) - np.sin(angle))
                else:
                    Cr_new[i] = (Cr[i] - CrG) * p + p * np.random.rand() * Cr[i]

        Cr_new = np.clip(Cr_new, lb, ub)
        for i in range(N):
            if not evaluator.has_budget():
                break
            cand_b = _bincoa_binarize(Cr_new[i], dim)
            cand_f = evaluator.evaluate(cand_b, ws=ws)
            if cand_f < fit[i]:
                Cr[i] = Cr_new[i].copy()
                Cr_bin[i] = cand_b.copy()
                fit[i] = cand_f

        # Crisscross HC
        perm = np.random.permutation(N)
        for idx in range(0, N - 1, 2):
            if not evaluator.has_budget():
                break
            i1, i2 = perm[idx], perm[idx + 1]
            r1, r2 = np.random.rand(), np.random.rand()
            c1, c2 = np.random.uniform(-1.0, 1.0), np.random.uniform(-1.0, 1.0)
            hc1 = np.clip(r1 * Cr[i1] + (1.0 - r1) * Cr[i2] + c1 * (Cr[i1] - Cr[i2]), lb, ub)
            b_hc1 = _bincoa_binarize(hc1, dim)
            f_hc1 = evaluator.evaluate(b_hc1, ws=ws)
            if f_hc1 < fit[i1]:
                Cr[i1] = hc1
                Cr_bin[i1] = b_hc1
                fit[i1] = f_hc1

            if not evaluator.has_budget():
                break
            hc2 = np.clip(r2 * Cr[i2] + (1.0 - r2) * Cr[i1] + c2 * (Cr[i2] - Cr[i1]), lb, ub)
            b_hc2 = _bincoa_binarize(hc2, dim)
            f_hc2 = evaluator.evaluate(b_hc2, ws=ws)
            if f_hc2 < fit[i2]:
                Cr[i2] = hc2
                Cr_bin[i2] = b_hc2
                fit[i2] = f_hc2

        # Crisscross VC
        for i in range(N):
            if not evaluator.has_budget():
                break
            if dim >= 2:
                d1, d2 = np.random.choice(dim, 2, replace=False)
                r_v = np.random.rand()
                vc = Cr[i].copy()
                vc[d1] = r_v * Cr[i, d1] + (1.0 - r_v) * Cr[i, d2]
                vc = np.clip(vc, lb, ub)
                b_vc = _bincoa_binarize(vc, dim)
                f_vc = evaluator.evaluate(b_vc, ws=ws)
                if f_vc < fit[i]:
                    Cr[i] = vc
                    Cr_bin[i] = b_vc
                    fit[i] = f_vc

        cur_best_idx = np.argmin(fit)
        CrL = Cr[cur_best_idx].copy()
        if fit[cur_best_idx] < fitG:
            fitG = float(fit[cur_best_idx])
            CrG = Cr[cur_best_idx].copy()
            CrG_bin = Cr_bin[cur_best_idx].copy()

    mask = CrG_bin.astype(bool)
    if not mask.any():
        mask[np.random.choice(dim, min(3, dim), replace=False)] = True

    return {
        "mask": mask,
        "fitG": fitG,
        "generations_completed": generations,
        "stop_reason": "budget_exhausted" if not evaluator.has_budget() else "normal",
    }


# ══════════════════════════════════════════════════════════════════════════════
# 11. IGPSO (Importance-Guided PSO - Applied Soft Computing 2024)
# ══════════════════════════════════════════════════════════════════════════════

def run_nested_IGPSO(X_train, y_train, evaluator, opts, seed=7):
    """
    Importance-Guided Particle Swarm Optimization under BudgetEvaluator.
    Two-stage importance estimation via ANOVA F-statistic permutation contrast.
    """
    from sklearn.feature_selection import f_classif

    np.random.seed(seed)
    dim = X_train.shape[1]
    N = opts.get("N", 20)
    thres = opts.get("thres", 0.6)
    ws = opts.get("ws", [0.90, 0.10])
    Vmax = 0.5
    W_max, W_min = 0.9, 0.1
    C_max, C_min = 2.0, 0.1

    # Two-stage importance estimation strictly on outer train
    F1, _ = f_classif(X_train, y_train)
    F1 = np.nan_to_num(F1, nan=0.0, posinf=0.0, neginf=0.0)

    rng = np.random.default_rng(seed=seed + 999)
    y_neg = rng.permutation(y_train)
    F2, _ = f_classif(X_train, y_neg)
    F2 = np.nan_to_num(F2, nan=0.0, posinf=0.0, neginf=0.0)

    imp = np.maximum(0.0, F1 - F2)
    imp_max = imp.max()
    if imp_max > 1e-9:
        imp = imp / imp_max
    else:
        imp = np.full(dim, 0.5)

    w_j = W_min + (W_max - W_min) * (1.0 - imp)
    c1_j = C_min + (C_max - C_min) * imp
    c2_j = C_min + (C_max - C_min) * imp

    init_prob = 0.2 + 0.6 * imp
    P = (np.random.rand(N, dim) < init_prob).astype(float)
    V = np.zeros((N, dim))

    fit = np.zeros(N)
    for i in range(N):
        if not evaluator.has_budget():
            break
        m = P[i].astype(bool)
        if not m.any():
            m[np.random.randint(dim)] = True
        fit[i] = evaluator.evaluate(m, ws=ws)

    Pbest = P.copy()
    fitP = fit.copy()
    bi = np.argmin(fit)
    gbest = P[bi].copy()
    fitG = float(fit[bi])
    generations = 0

    while evaluator.has_budget():
        generations += 1
        r1 = np.random.rand(N, dim)
        r2 = np.random.rand(N, dim)
        V = np.clip(w_j * V + c1_j * r1 * (Pbest - P) + c2_j * r2 * (gbest - P), -Vmax, Vmax)
        prob = 1.0 / (1.0 + np.exp(-V))
        P = (np.random.rand(N, dim) < prob).astype(float)

        for i in range(N):
            if not evaluator.has_budget():
                break
            m = P[i].astype(bool)
            if not m.any():
                m[np.random.randint(dim)] = True
            f = evaluator.evaluate(m, ws=ws)
            if f < fitP[i]:
                Pbest[i] = P[i].copy()
                fitP[i] = f
            if f < fitG:
                fitG = float(f)
                gbest = P[i].copy()

    mask = (gbest > thres).astype(bool)
    if not mask.any():
        mask[np.random.randint(dim)] = True

    return {
        "mask": mask,
        "fitG": fitG,
        "generations_completed": generations,
        "stop_reason": "budget_exhausted" if not evaluator.has_budget() else "normal",
    }


# ══════════════════════════════════════════════════════════════════════════════
# 12. DENCA_SO (Evolutionary Filter DE - Hancer et al. KBS 2023)
# ══════════════════════════════════════════════════════════════════════════════

def _compute_ncfs_weights_nested(X, y, lambd=0.01, max_iter=50):
    from scipy.optimize import minimize
    N_samp, D = X.shape
    std = np.std(X, axis=0)
    std[std == 0] = 1.0
    X_norm = ((X - np.mean(X, axis=0)) / std).astype(np.float32)

    mask_same = (y[:, None] == y[None, :])
    np.fill_diagonal(mask_same, False)
    mask_other = ~np.eye(N_samp, dtype=bool)
    X_sq = (X_norm ** 2).astype(np.float32)

    def loss_and_grad(w):
        w_vec = w.astype(np.float32)
        w2 = w_vec ** 2
        s = X_sq @ w2
        X_w = X_norm * w_vec
        d = np.maximum(s[:, None] + s[None, :] - 2.0 * (X_w @ X_w.T), 0.0)
        d_min = np.min(d, axis=1, keepdims=True)
        exp_d = np.exp(-(d - d_min)) * mask_other
        sum_exp = np.sum(exp_d, axis=1, keepdims=True) + 1e-12
        P = exp_d / sum_exp
        p_i = np.sum(P * mask_same, axis=1)
        obj = -(np.mean(p_i) - lambd * np.sum(w2))

        M = P * mask_same
        PX = P @ X_norm
        MX = M @ X_norm
        PX_sq = P @ X_sq
        MX_sq = M @ X_sq
        diff_terms = 2.0 * X_norm * (MX - p_i[:, None] * PX) + (p_i[:, None] * PX_sq - MX_sq)
        grad_p_i = 2.0 * w_vec[None, :] * diff_terms
        grad = -(np.mean(grad_p_i, axis=0) - 2.0 * lambd * w_vec)
        return float(obj), grad.astype(np.float64)

    w0 = np.ones(D, dtype=np.float64) / np.sqrt(max(D, 1))
    try:
        res = minimize(
            loss_and_grad,
            w0,
            method="L-BFGS-B",
            jac=True,
            bounds=[(0.0, None) for _ in range(D)],
            options={"maxiter": max_iter, "ftol": 1e-4, "gtol": 1e-4},
        )
        weights = np.abs(res.x)
    except Exception:
        weights = np.zeros(D)
        classes = np.unique(y)
        if len(classes) > 1:
            overall_mean = np.mean(X_norm, axis=0)
            for c in classes:
                mask_c = (y == c)
                nc = np.sum(mask_c)
                if nc > 0:
                    mean_c = np.mean(X_norm[mask_c], axis=0)
                    weights += nc * (mean_c - overall_mean) ** 2

    w_min, w_max = np.min(weights), np.max(weights)
    if w_max > w_min:
        H = (weights - w_min) / (w_max - w_min)
    else:
        H = np.ones(D) / D
    return H


_NCFS_CACHE_NESTED = {}


def run_nested_DENCA_SO(X_train, y_train, evaluator, opts, seed=7):
    """
    DENCA-SO (Evolutionary Filter DE) under BudgetEvaluator.
    Computes NCFS weights, runs DE on filter objective, and evaluates best candidate.
    """
    np.random.seed(seed)
    dim = X_train.shape[1]
    N = opts.get("N", 20)
    ws = opts.get("ws", [0.90, 0.10])
    lambd = opts.get("ncfs_lambda", 0.01)

    train_hash = hashlib.sha256(X_train.tobytes() + y_train.tobytes()).hexdigest()
    cache_key = (train_hash, lambd)
    if cache_key in _NCFS_CACHE_NESTED:
        H = _NCFS_CACHE_NESTED[cache_key]
    else:
        H = _compute_ncfs_weights_nested(X_train, y_train, lambd=lambd, max_iter=50)
        _NCFS_CACHE_NESTED[cache_key] = H

    W = 0.05 if dim > 60 else 0.10
    F = 0.5
    CR = 0.2

    def filter_cost(x_cont):
        mask = (x_cont > 0.5)
        sz = int(mask.sum())
        if sz == 0:
            return 1e9
        return -W * np.sum(H[mask]) + (1.0 - W) * (sz / dim)

    P = np.random.uniform(0.0, 1.0, (N, dim))
    fit = np.zeros(N)
    for i in range(N):
        if evaluator.candidate_eval_requests >= evaluator.max_fes - 1:
            break
        evaluator.candidate_eval_requests += 1
        evaluator.filter_eval_requests += 1
        fit[i] = filter_cost(P[i])

    bi = np.argmin(fit)
    Gbest = P[bi].copy()
    best_filter_fit = fit[bi]

    # DENCA performs evolutionary filter search reserving 1 final wrapper evaluation request
    generations = 0

    while evaluator.candidate_eval_requests < evaluator.max_fes - 1:
        generations += 1
        for i in range(N):
            if evaluator.candidate_eval_requests >= evaluator.max_fes - 1:
                break
            candidates = [idx for idx in range(N) if idx != i]
            r1, r2, r3 = np.random.choice(candidates, 3, replace=False)
            v = np.clip(P[r1] + F * (P[r2] - P[r3]), 0.0, 1.0)
            j_rand = np.random.randint(0, dim)
            cross_mask = (np.random.rand(dim) < CR)
            cross_mask[j_rand] = True
            u = np.where(cross_mask, v, P[i])

            evaluator.candidate_eval_requests += 1
            evaluator.filter_eval_requests += 1
            f_u = filter_cost(u)
            if f_u <= fit[i]:
                P[i] = u
                fit[i] = f_u
                if f_u < best_filter_fit:
                    best_filter_fit = f_u
                    Gbest = u.copy()

    final_mask = (Gbest > 0.5)
    if not final_mask.any():
        final_mask[np.argmax(H)] = True

    # Evaluates the final selected subset using the reserved wrapper evaluation (request == max_fes)
    fitG = evaluator.evaluate(final_mask, ws=ws)

    return {
        "mask": final_mask,
        "fitG": fitG,
        "generations_completed": generations,
        "stop_reason": "normal",
    }


# ══════════════════════════════════════════════════════════════════════════════
# Master Runner Registration
# ══════════════════════════════════════════════════════════════════════════════

NESTED_RUNNERS = {
    # 5 Core Configurations (Stage 1)
    "KDS_EL_TwoPhase": run_nested_KDS_EL_TwoPhase,
    "MEL": run_nested_MEL,
    "MEL_MI": run_nested_MEL_MI,
    "KDS_EL_NoPool": run_nested_KDS_EL_NoPool,
    "bIRIME": run_nested_bIRIME,
    # 7 Extended Competitors (Stage 2)
    "BPSO": run_nested_BPSO,
    "FWPSO": run_nested_FWPSO,
    "SaWDE": run_nested_SaWDE,
    "PSO_CSM": run_nested_PSO_CSM,
    "BinCOA": run_nested_BinCOA,
    "IGPSO": run_nested_IGPSO,
    "DENCA_SO": run_nested_DENCA_SO,
}
