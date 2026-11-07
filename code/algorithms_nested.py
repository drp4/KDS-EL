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
                change = np.logical_xor(fv_o, fv_n)
                case_emerge = np.where(change & (fv_o > fv_n))[0]
                case_disappear = np.where(change & (fv_o < fv_n))[0]
                for j in case_emerge:
                    weight[j] -= dec
                for j in case_disappear:
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
        RimeFactor = (
            (np.random.rand() - 0.5) * 2.0
            * np.cos(np.pi * (t % 10) / 10.0)
            * (1.0 - np.round((t % 50) * W_soft / 50.0) / W_soft)
        )
        E = np.sqrt(min(1.0, t / 100.0))
        c = 2.0 * (1.0 - min(1.0, t / 100.0))

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
                P_new[i] = P[rand_idx] - r * np.abs(P[rand_idx] - 2.0 * np.random.rand() * P[i])
            else:
                # Soft-rime / Hard-rime
                for j in range(dim):
                    r = np.random.rand()
                    if r < norm_rates[i]:
                        P_new[i, j] = Gbest[j] + RimeFactor * (
                            (ub - lb) * np.random.rand() + lb
                        )
                    elif r < E:
                        P_new[i, j] = P[i, j] + RimeFactor * (
                            (ub - lb) * np.random.rand() + lb
                        )

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

            # Restart Strategy (RS)
            if SalpTrial[i] >= Limits and evaluator.has_budget():
                P[i] = np.random.uniform(lb, ub, dim)
                P_bin[i] = bIRIME_binarize(P[i], dim)
                fit[i] = evaluator.evaluate(P_bin[i], ws=ws)
                SalpTrial[i] = 0
                if fit[i] < fitG:
                    Gbest = P[i].copy()
                    Gbest_bin = P_bin[i].copy()
                    fitG = float(fit[i])

    mask = Gbest_bin
    if not mask.any():
        mask[np.argmax(Gbest)] = True

    return {
        "mask": mask,
        "fitG": fitG,
        "generations_completed": generations,
        "stop_reason": "budget_exhausted" if not evaluator.has_budget() else "normal",
    }


NESTED_RUNNERS = {
    "KDS_EL_TwoPhase": run_nested_KDS_EL_TwoPhase,
    "MEL": run_nested_MEL,
    "MEL_MI": run_nested_MEL_MI,
    "KDS_EL_NoPool": run_nested_KDS_EL_NoPool,
    "bIRIME": run_nested_bIRIME,
}
