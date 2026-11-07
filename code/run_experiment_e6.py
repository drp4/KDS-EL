"""
Experiment E6: Label-Permutation Empirical Null Hypothesis Test
==============================================================
Protocol Reference:
  - review_round_1/05_executable_experiment_plan.md (Section 9)
  - review_round_1/04_detailed_supplementary_experiment_design.md (Section 5 / Suite 4)

Experimental Scope:
  - Datasets: Colon and SRBCT.
  - Number of Permutations: B = 100 (b = 1, ..., 100).
  - Real Condition: b = 0 with ground-truth labels y.
  - Independent Randomization:
      * Label permutation RNG seed: 10000 + b.
      * Optimizer seed: strictly fixed at seed = 7.
      * StratifiedKFold: fixed seed = 42 for both outer (5-fold) and inner (5-fold).
  - End-to-End Execution per Permutation Condition b:
      * Outer stratified splits re-derived under current y^(b).
      * Inner stratified splits re-derived under outer training y_train^(b).
      * Mutual Information re-estimated on X_train and y_train^(b).
      * Complete KDS-EL Full search under BudgetEvaluator (Max_FEs = 2000).
      * 3-NN fit only on outer training partition (X_train, y_train^(b)).
      * Pooled OOF predictions aggregated against y^(b).
  - Pre-Registered Test Statistics (4 tests in family F):
      1. Colon: 3-NN Pooled OOF Balanced Accuracy (T_BAcc)
      2. Colon: Termination Classification Credit Component (T_W)
      3. SRBCT: 3-NN Pooled OOF Balanced Accuracy (T_BAcc)
      4. SRBCT: Termination Classification Credit Component (T_W)
  - Statistical Decision:
      * Empirical upper-tail Monte Carlo p-value:
          p_emp = (1 + sum_{b=1}^B I(T_b >= T_0)) / (B + 1)
      * Family-wise error rate controlled via Holm-Bonferroni correction (alpha = 0.05).
      * Descriptive standardization: Z_desc = (T_0 - mu_perm) / s_perm.
"""

import os
import sys
import json
import time
import argparse
import numpy as np
from datetime import datetime
from concurrent.futures import ProcessPoolExecutor, as_completed
from sklearn.model_selection import StratifiedKFold
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import accuracy_score, balanced_accuracy_score, f1_score

# Ensure project root is in sys.path
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

from config import DATA_DIR_TXT, DATA_DIR_MAT
from utils import load_dataset, compute_mi_scores, ker_flip
from nested_evaluator import BudgetEvaluator, IntegrityAuditor


def sanitize_for_json(obj):
    if isinstance(obj, dict):
        return {k: sanitize_for_json(v) for k, v in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [sanitize_for_json(v) for v in obj]
    elif isinstance(obj, (np.bool_, np.bool)):
        return bool(obj)
    elif isinstance(obj, (np.integer,)):
        return int(obj)
    elif isinstance(obj, (np.floating,)):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return sanitize_for_json(obj.tolist())
    return obj


# ══════════════════════════════════════════════════════════════════════════════
# Full KDS-EL Search with Signed Credit Tracking for E6
# ══════════════════════════════════════════════════════════════════════════════

def run_e6_kdsel_search(X_train, y_train, evaluator, seed=7):
    """
    Executes full KDS-EL optimization while tracking W_class and W_size
    to compute the directional classification credit contrast Delta W_class.
    """
    np.random.seed(seed)
    N_tr, dim = X_train.shape
    N = 20
    half = N // 2
    thres = 0.60
    lb, ub = 0.0, 1.0
    c1 = c2 = c3 = 2.0
    w = 0.9
    Vmax = (ub - lb) / 2
    patience = 20
    decay = 0.99
    flip_count = max(1, int(0.01 * dim))
    rand_p = 0.10

    # 1. MI computed strictly on current condition training partition
    mi = compute_mi_scores(X_train, y_train)

    order_mi = np.argsort(-mi, kind="stable")
    top_k = max(1, int(np.ceil(0.10 * dim)))
    bot_k = max(1, int(np.floor(0.50 * dim)))
    high_mi_mask = np.zeros(dim, dtype=bool)
    high_mi_mask[order_mi[:top_k]] = True
    low_mi_mask = np.zeros(dim, dtype=bool)
    low_mi_mask[order_mi[-bot_k:]] = True

    # 2. Population Initialization
    P = np.zeros((N, dim))
    P[:half] = np.clip(mi + np.random.normal(0, 0.1, (half, dim)), lb, ub)
    P[half:] = np.random.uniform(lb, ub, (N - half, dim))
    V = np.zeros((N, dim))
    weight = np.zeros(dim)
    W_class = np.zeros(dim, dtype=np.float64)
    W_size = np.zeros(dim, dtype=np.float64)
    W_barrier = np.zeros(dim, dtype=np.float64)

    # Initial Phase 1 weights (ws1 = [0.70, 0.30])
    current_ws = [0.70, 0.30]
    switched = False

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

    while evaluator.has_budget():
        generations += 1
        gen_start_fitG = fitG

        # TPS dynamic switch at q >= 0.70
        if not switched and evaluator.progress_q >= 0.70:
            switched = True
            current_ws = [0.95, 0.05]
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

        # Weight Decay across entire population and attribution channels
        weight *= decay
        W_class *= decay
        W_size *= decay
        W_barrier *= decay

        P_new = P.copy()
        Xsub_best = Pbest[half + np.argmin(fitP[half:])].copy()

        # Regular Swarm Candidate Generation
        for i in range(N):
            if i < half:
                # Subpopulation 1: Continuous PSO
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
                # Subpopulation 2: Discrete sampling from weight vector
                vf = np.maximum(weight, 0.0)
                sv = vf.sum()
                prob = vf / sv if sv > 0 else np.full(dim, 0.5)
                P_new[i] = (np.random.rand(dim) < prob).astype(float)

        # Evaluate and In-Place Greedy Replacement with Signed Credit Attribution
        for i in range(N):
            if not evaluator.has_budget():
                break
            fv_n = P_new[i] > thres
            fv_o = Pbest[i] > thres
            fit_new = evaluator.evaluate(fv_n, ws=current_ws)

            delta = fitP[i] - fit_new
            d_p = int(fv_o.sum())
            d_x = int(fv_n.sum())
            delta_size = current_ws[1] * float(d_p - d_x) / max(1, dim)

            # Infeasibility barrier decoupling
            both_feasible = (d_p >= 3) and (d_x >= 3)
            if both_feasible:
                delta_class = delta - delta_size
                delta_barrier = 0.0
            else:
                delta_class = 0.0
                delta_barrier = delta - delta_size

            change = np.logical_xor(fv_n, fv_o)
            dir_s = np.zeros(dim)
            dir_s[change] = (2 * fv_n[change].astype(float) - 1.0)

            # Unified signed credit attribution
            weight += delta * dir_s
            W_class += delta_class * dir_s
            W_size += delta_size * dir_s
            W_barrier += delta_barrier * dir_s

            if fit_new < fitP[i]:
                Pbest[i] = P_new[i].copy()
                fitP[i] = fit_new

                if fitP[i] < fitG:
                    fitG = float(fitP[i])
                    Gbest = Pbest[i].copy()
            else:
                pass

        P = P_new.copy()

        # KER Elite Refinement
        if evaluator.has_budget():
            for e_idx in np.argsort(fitP)[:3]:
                if not evaluator.has_budget():
                    break
                elite_bin = (Pbest[e_idx] > thres).astype(int)
                mutant = ker_flip(weight, elite_bin, flip_count, rand_p)
                mfit = evaluator.evaluate(mutant.astype(bool), ws=current_ws)
                if mfit < fitP[e_idx]:
                    Pbest[e_idx] = mutant
                    fitP[e_idx] = mfit
                    if fitP[e_idx] < fitG:
                        fitG = float(fitP[e_idx])
                        Gbest = Pbest[e_idx].copy()

        # Check generation stall
        if fitG < gen_start_fitG:
            stall_counter = 0
        else:
            stall_counter += 1

        # AIR Adaptive Reinitialization
        if stall_counter >= patience and evaluator.has_budget():
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

    high_mean = float(np.mean(W_class[high_mi_mask])) if high_mi_mask.any() else 0.0
    low_mean = float(np.mean(W_class[low_mi_mask])) if low_mi_mask.any() else 0.0
    delta_w_class = high_mean - low_mean

    return {
        "mask": mask,
        "fitG": fitG,
        "delta_w_class": float(delta_w_class),
        "generations": generations,
    }


# ══════════════════════════════════════════════════════════════════════════════
# Single Permutation Condition (5 Outer Folds End-to-End)
# ══════════════════════════════════════════════════════════════════════════════

def execute_permutation_condition(dataset_name, b_idx, seed_optimizer=7, max_fes=2000, verbose=False):
    """
    Executes a complete 5-fold outer cross-validation run for permutation condition b.
    b = 0 is the real ground-truth label condition.
    b > 0 is the permuted label condition (seed = 10000 + b).
    """
    t0 = time.perf_counter()
    X, y_real = load_dataset(dataset_name, DATA_DIR_TXT, DATA_DIR_MAT)
    N_samples, D = X.shape

    # 1. Establish label condition
    if b_idx == 0:
        y_curr = y_real.copy()
        perm_seed = 0
    else:
        perm_seed = 10000 + b_idx
        rng = np.random.default_rng(seed=perm_seed)
        y_curr = rng.permutation(y_real)

    # 2. Re-derive outer splits dynamically on y_curr
    skf_outer = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    outer_splits = list(skf_outer.split(X, y_curr))

    y_oof_preds = np.zeros(N_samples, dtype=int)
    covered_test_indices = np.zeros(N_samples, dtype=bool)
    fold_delta_w = []
    fold_feats = []

    for fold_k, (train_idx, test_idx) in enumerate(outer_splits, start=1):
        X_train_outer = X[train_idx]
        y_train_outer = y_curr[train_idx]
        X_test_outer = X[test_idx]
        y_test_outer = y_curr[test_idx]

        # Inner splits dynamically formed on y_train_outer
        skf_inner = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
        inner_splits = list(skf_inner.split(X_train_outer, y_train_outer))

        evaluator = BudgetEvaluator(
            X_train_outer=X_train_outer,
            y_train_outer=y_train_outer,
            inner_splits=inner_splits,
            max_fes=max_fes,
            knn_k=3,
            use_fast_knn=False,
        )

        res = run_e6_kdsel_search(
            X_train_outer, y_train_outer, evaluator, seed=seed_optimizer
        )

        selected_mask = res["mask"]
        fold_delta_w.append(res["delta_w_class"])
        fold_feats.append(int(selected_mask.sum()))

        # Fit 3-NN strictly on outer training data
        actual_k = min(3, len(y_train_outer))
        clf = KNeighborsClassifier(n_neighbors=actual_k)
        clf.fit(X_train_outer[:, selected_mask], y_train_outer)

        preds = clf.predict(X_test_outer[:, selected_mask])
        y_oof_preds[test_idx] = preds
        covered_test_indices[test_idx] = True

    if not np.all(covered_test_indices):
        raise ValueError(f"Permutation b={b_idx} failed: Not all test indices were covered!")

    # Calculate pre-registered statistics against y_curr
    bacc = float(balanced_accuracy_score(y_curr, y_oof_preds))
    acc = float(accuracy_score(y_curr, y_oof_preds))
    macro_f1 = float(f1_score(y_curr, y_oof_preds, average="macro", zero_division=0))
    t_w = float(np.mean(fold_delta_w))
    mean_feats = float(np.mean(fold_feats))
    elapsed = time.perf_counter() - t0

    result = {
        "dataset": dataset_name,
        "b_idx": b_idx,
        "is_real": (b_idx == 0),
        "perm_seed": perm_seed,
        "optimizer_seed": seed_optimizer,
        "bacc": bacc,
        "acc": acc,
        "macro_f1": macro_f1,
        "T_W": t_w,
        "mean_features": mean_feats,
        "elapsed_sec": float(elapsed),
    }

    if verbose:
        cond_tag = "REAL [b=0]" if b_idx == 0 else f"PERM [b={b_idx:3d}]"
        print(
            f"  {dataset_name:6s} | {cond_tag} | "
            f"BAcc={bacc:.4f} | Acc={acc:.4f} | T_W={t_w:+.4f} | "
            f"Feats={mean_feats:4.1f} | Time={elapsed:.2f}s"
        )

    return result


# ══════════════════════════════════════════════════════════════════════════════
# Holm-Bonferroni Family-Wise Multiple Testing Procedure
# ══════════════════════════════════════════════════════════════════════════════

def apply_holm_bonferroni(hypotheses, alpha=0.05):
    """
    Applies Holm-Bonferroni step-down procedure to control FWER at level alpha.
    hypotheses: list of dicts with 'name', 'p_raw', 'T_0', 'Z_desc'.
    """
    m = len(hypotheses)
    # Sort hypotheses by p_raw ascending
    sorted_hyps = sorted(hypotheses, key=lambda h: h["p_raw"])

    corrected = []
    prev_adj_p = 0.0

    for i, hyp in enumerate(sorted_hyps, start=1):
        k = m - i + 1  # remaining hypotheses
        p_raw = hyp["p_raw"]
        nominal_threshold = alpha / k
        adj_p = min(1.0, max(prev_adj_p, k * p_raw))
        prev_adj_p = adj_p
        rejected = (p_raw <= nominal_threshold)

        corrected.append({
            **hyp,
            "rank": i,
            "nominal_threshold": float(nominal_threshold),
            "p_adj": float(adj_p),
            "rejected_null": bool(rejected),
        })

    # Ensure monotonic rejection: once an ordered hypothesis fails to reject, all subsequent fail
    rejection_broken = False
    for item in corrected:
        if rejection_broken:
            item["rejected_null"] = False
        elif not item["rejected_null"]:
            rejection_broken = True

    return corrected


# ══════════════════════════════════════════════════════════════════════════════
# Master Orchestrator for Experiment E6
# ══════════════════════════════════════════════════════════════════════════════

def run_experiment_e6(
    datasets=None,
    n_perms=100,
    seed_optimizer=7,
    max_fes=2000,
    workers=2,
    out_dir=None,
    verbose=True,
):
    """
    Executes label permutation test across specified datasets and computes empirical p-values.
    """
    t0_all = time.perf_counter()
    if datasets is None:
        datasets = ["Colon", "SRBCT"]
    if out_dir is None:
        out_dir = os.path.join(PROJECT_ROOT, "output", "nested_cv", "e6_permutation")

    os.makedirs(out_dir, exist_ok=True)

    os.environ["OMP_NUM_THREADS"] = "1"
    os.environ["MKL_NUM_THREADS"] = "1"
    os.environ["OPENBLAS_NUM_THREADS"] = "1"

    print("\n" + "=" * 80)
    print("STARTING EXPERIMENT E6: LABEL-PERMUTATION EMPIRICAL NULL HYPOTHESIS TEST")
    print(f"Datasets ({len(datasets)}): {datasets}")
    print(f"Permutations: B = {n_perms} (b = 1 to {n_perms}) + Real Condition (b = 0)")
    print(f"Optimizer Seed: {seed_optimizer} | Evaluation Budget: {max_fes}")
    print(f"Parallel Workers: {workers}")
    print(f"Output Directory: {out_dir}")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80 + "\n")

    # Generate task list: (dataset, b_idx)
    tasks = []
    for ds in datasets:
        tasks.append((ds, 0))  # Real condition
        for b in range(1, n_perms + 1):
            tasks.append((ds, b))

    print(f"Total Nested Cross-Validation Tasks: {len(tasks)} (5 outer folds per task = {len(tasks)*5} runs)\n")

    completed_results = []
    if workers <= 1:
        for ds, b in tasks:
            res = execute_permutation_condition(
                dataset_name=ds,
                b_idx=b,
                seed_optimizer=seed_optimizer,
                max_fes=max_fes,
                verbose=verbose,
            )
            completed_results.append(res)
    else:
        with ProcessPoolExecutor(max_workers=workers) as executor:
            future_map = {
                executor.submit(
                    execute_permutation_condition,
                    ds, b, seed_optimizer, max_fes, verbose
                ): (ds, b)
                for ds, b in tasks
            }
            for fut in as_completed(future_map):
                try:
                    res = fut.result()
                    completed_results.append(res)
                except Exception as exc:
                    ds, b = future_map[fut]
                    print(f"  [ERROR] Condition ({ds}, b={b}) failed with: {exc}")

    # Save detailed runs
    detailed_path = os.path.join(out_dir, "e6_detailed_permutations.json")
    with open(detailed_path, "w", encoding="utf-8") as f:
        json.dump(sanitize_for_json(completed_results), f, indent=2)

    # ══════════════════════════════════════════════════════════════════════════
    # Compute Empirical p-values and Holm-Bonferroni Correction
    # ══════════════════════════════════════════════════════════════════════════
    # Group results by dataset
    grouped = {ds: {} for ds in datasets}
    for r in completed_results:
        ds = r["dataset"]
        b = r["b_idx"]
        grouped[ds][b] = r

    hypotheses_pool = []
    summary_null_dist = {}

    for ds in datasets:
        ds_records = grouped[ds]
        if 0 not in ds_records:
            print(f"  [WARNING] Real condition b=0 missing for {ds}! Skipping testing.")
            continue

        real_rec = ds_records[0]
        perm_recs = [ds_records[b] for b in range(1, n_perms + 1) if b in ds_records]
        B_actual = len(perm_recs)

        if B_actual == 0:
            continue

        # 1. Balanced Accuracy Test
        t0_bacc = real_rec["bacc"]
        t_perm_bacc = np.array([r["bacc"] for r in perm_recs])
        count_bacc_ge = int(np.sum(t_perm_bacc >= t0_bacc))
        p_emp_bacc = float((1.0 + count_bacc_ge) / (B_actual + 1.0))
        mu_bacc = float(np.mean(t_perm_bacc))
        sd_bacc = float(np.std(t_perm_bacc))
        z_bacc = float((t0_bacc - mu_bacc) / sd_bacc) if sd_bacc > 1e-9 else 0.0

        hypotheses_pool.append({
            "name": f"{ds}-BAcc",
            "dataset": ds,
            "statistic": "Balanced_Accuracy",
            "T_0": t0_bacc,
            "T_perm_mean": mu_bacc,
            "T_perm_std": sd_bacc,
            "Z_desc": z_bacc,
            "count_ge": count_bacc_ge,
            "B": B_actual,
            "p_raw": p_emp_bacc,
        })

        # 2. Classification Credit Contrast Test (T_W)
        t0_tw = real_rec["T_W"]
        t_perm_tw = np.array([r["T_W"] for r in perm_recs])
        count_tw_ge = int(np.sum(t_perm_tw >= t0_tw))
        p_emp_tw = float((1.0 + count_tw_ge) / (B_actual + 1.0))
        mu_tw = float(np.mean(t_perm_tw))
        sd_tw = float(np.std(t_perm_tw))
        z_tw = float((t0_tw - mu_tw) / sd_tw) if sd_tw > 1e-9 else 0.0

        hypotheses_pool.append({
            "name": f"{ds}-T_W",
            "dataset": ds,
            "statistic": "Credit_Contrast_T_W",
            "T_0": t0_tw,
            "T_perm_mean": mu_tw,
            "T_perm_std": sd_tw,
            "Z_desc": z_tw,
            "count_ge": count_tw_ge,
            "B": B_actual,
            "p_raw": p_emp_tw,
        })

        summary_null_dist[ds] = {
            "B_actual": B_actual,
            "real": real_rec,
            "bacc_distribution": {
                "mean": mu_bacc,
                "std": sd_bacc,
                "quantiles": {
                    "p25": float(np.percentile(t_perm_bacc, 25)),
                    "p50": float(np.percentile(t_perm_bacc, 50)),
                    "p75": float(np.percentile(t_perm_bacc, 75)),
                    "p95": float(np.percentile(t_perm_bacc, 95)),
                },
            },
            "tw_distribution": {
                "mean": mu_tw,
                "std": sd_tw,
                "quantiles": {
                    "p25": float(np.percentile(t_perm_tw, 25)),
                    "p50": float(np.percentile(t_perm_tw, 50)),
                    "p75": float(np.percentile(t_perm_tw, 75)),
                    "p95": float(np.percentile(t_perm_tw, 95)),
                },
            },
        }

    # Apply Holm-Bonferroni correction
    test_results = apply_holm_bonferroni(hypotheses_pool, alpha=0.05)

    null_dist_path = os.path.join(out_dir, "e6_null_distributions.json")
    with open(null_dist_path, "w", encoding="utf-8") as f:
        json.dump(
            sanitize_for_json({
                "summary_null_dist": summary_null_dist,
                "holm_bonferroni_results": test_results,
            }),
            f,
            indent=2,
        )

    # Generate Markdown Report
    report_path = os.path.join(out_dir, "e6_permutation_report.md")
    generate_e6_markdown_report(test_results, summary_null_dist, report_path, time.perf_counter() - t0_all)

    elapsed_total = time.perf_counter() - t0_all
    print("\n" + "=" * 80)
    print(f"EXPERIMENT E6 COMPLETED in {elapsed_total:.2f}s!")
    print(f"Artifacts saved:")
    print(f"  - Detailed Permutations JSON: {detailed_path}")
    print(f"  - Null Distribution Summary JSON: {null_dist_path}")
    print(f"  - Academic Markdown Report: {report_path}")
    print("=" * 80 + "\n")


def generate_e6_markdown_report(test_results, null_dist, out_path, elapsed_time):
    """
    Renders academic report conforming to AGENTS.md.
    """
    lines = []
    lines.append("# E6: Label-Permutation Empirical Null Hypothesis Test Report\n")
    lines.append(f"- **Execution Timestamp**: {datetime.now().isoformat()}")
    lines.append(f"- **Protocol Reference**: `review_round_1/05_executable_experiment_plan.md` (Section 9)")
    lines.append(f"- **Pre-Registered Family of Hypotheses**: 4 tests (Colon-BAcc, Colon-T_W, SRBCT-BAcc, SRBCT-T_W)")
    lines.append(f"- **Family-Wise Error Rate (FWER) Control**: Holm-Bonferroni Step-Down ($\alpha = 0.05$)")
    lines.append(f"- **Total Elapsed Time**: `{elapsed_time:.2f} s`\n")

    lines.append("> **Formal Methodological Demarcation**:")
    lines.append("> The null hypothesis posited in this investigation states that, under the label exchangeability constraint, there is no detectable predictive association between the feature matrix and class labels. Empirical p-values are derived via full end-to-end re-execution under permuted labels, ensuring that prior calculation, initialization, wrapper search, and classifier fitting are subjected to identical empirical constraints without cached information reuse.\n")

    lines.append("## 1. Family-Wise Hypothesis Testing Matrix (Holm-Bonferroni Correction)\n")
    lines.append(r"| Rank ($i$) | Hypothesis Test | Ground Truth ($T_0$) | Permutation Null ($\mu_{\mathrm{perm}} \pm \sigma$) | $Z_{\mathrm{desc}}$ | Raw $p$-value ($p_{\mathrm{emp}}$) | Adjusted Threshold ($\alpha / k$) | Adjusted $p$-value ($p_{\mathrm{adj}}$) | Reject $H_0$? |")
    lines.append("| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |")

    for item in test_results:
        t0_str = f"{item['T_0']:.4f}"
        null_str = f"{item['T_perm_mean']:.4f} ± {item['T_perm_std']:.3f}"
        z_str = f"{item['Z_desc']:+.2f}"
        p_raw_str = f"{item['p_raw']:.4f}"
        thresh_str = f"{item['nominal_threshold']:.4f}"
        p_adj_str = f"{item['p_adj']:.4f}"
        reject_str = "**REJECT (Significant)**" if item["rejected_null"] else "Fail to Reject"

        lines.append(
            f"| {item['rank']} | **`{item['name']}`** | {t0_str} | {null_str} | {z_str} | "
            f"{p_raw_str} | {thresh_str} | {p_adj_str} | {reject_str} |"
        )

    lines.append("\n## 2. Empirical Null Distribution Profiles\n")
    for ds, info in null_dist.items():
        b_cnt = info["B_actual"]
        lines.append(f"### {ds} Microarray Benchmark ($B = {b_cnt}$ Permutations)\n")
        real_info = info["real"]
        bacc_dist = info["bacc_distribution"]
        tw_dist = info["tw_distribution"]

        lines.append(f"- **Observed Real Generalization**: Balanced Accuracy = `{real_info['bacc']:.4f}`, Accuracy = `{real_info['acc']:.4f}`, Macro-F1 = `{real_info['macro_f1']:.4f}`, Features = `{real_info['mean_features']:.1f}`")
        lines.append(f"- **Observed Real Credit Contrast ($T_W$)**: `{real_info['T_W']:+.4f}`")
        lines.append(f"- **Balanced Accuracy Null Distribution**: Mean = `{bacc_dist['mean']:.4f}`, Std = `{bacc_dist['std']:.4f}`, Median = `{bacc_dist['quantiles']['p50']:.4f}`, 95th Percentile = `{bacc_dist['quantiles']['p95']:.4f}`")
        lines.append(f"- **Credit Contrast Null Distribution ($T_W$)**: Mean = `{tw_dist['mean']:+.4f}`, Std = `{tw_dist['std']:+.4f}`, Median = `{tw_dist['quantiles']['p50']:+.4f}`, 95th Percentile = `{tw_dist['quantiles']['p95']:+.4f}`\n")

    lines.append("## 3. Academic Findings & Submission Defensibility\n")
    sig_count = sum(1 for item in test_results if item["rejected_null"])
    total_tests = len(test_results)

    lines.append(f"1. **Multiple Testing Decision**: Across the {total_tests} pre-registered tests with Holm-Bonferroni step-down correction at family-wise $\\alpha = 0.05$, **{sig_count} of {total_tests}** null hypotheses were formally rejected.")
    for item in test_results:
        dec_str = "statistically significant (reject H0)" if item["rejected_null"] else "not statistically significant (fail to reject H0)"
        lines.append(f"   - **`{item['name']}`**: Raw $p = {item['p_raw']:.4f}$, Adjusted $p = {item['p_adj']:.4f}$ -> {dec_str}.")

    lines.append("\n2. **Empirical Interpretation & Methodological Boundaries**:")
    if sig_count == total_tests:
        lines.append("   - Real-condition generalization metrics and classifier credit contrast metrics are significantly higher than the permutation null distributions, indicating that the observed performance does not arise merely from random label structure or heuristic search artifacts.")
    elif sig_count > 0:
        lines.append("   - Partial significance was observed: certain pre-registered metrics exceeded the empirical null, while others did not achieve family-wise significance after Holm-Bonferroni correction. Claims must be carefully qualified to reflect only the supported hypotheses.")
    else:
        lines.append("   - The pre-registered tests did not reject the null hypotheses at the family-wise $\\alpha = 0.05$ level. Per protocol, no post-hoc metric replacement is permitted, and empirical conclusions must honestly report that predictive signal was not distinguishable from the permutation null under the current sample size.")

    lines.append("3. **Conservative Demarcation**: Significant results confirm empirical association above label exchangeability, but do not imply biological causality, clinical validation, or deterministic gene identity.\n")

    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


# ══════════════════════════════════════════════════════════════════════════════
# CLI Entry Point
# ══════════════════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(description="Run Experiment E6: Label-Permutation Empirical Null Hypothesis Test.")
    parser.add_argument("--datasets", nargs="+", default=["Colon", "SRBCT"], help="Target datasets.")
    parser.add_argument("--n-perms", type=int, default=100, help="Number of label permutations (B).")
    parser.add_argument("--seed-optimizer", type=int, default=7, help="Fixed optimizer random seed.")
    parser.add_argument("--max-fes", type=int, default=2000, help="Candidate fitness evaluation budget.")
    parser.add_argument("--workers", type=int, default=2, help="Number of concurrent worker processes.")
    parser.add_argument("--out-dir", type=str, default=None, help="Output directory path.")
    parser.add_argument("--quiet", action="store_true", help="Suppress verbose stdout logs.")

    args = parser.parse_args()

    run_experiment_e6(
        datasets=args.datasets,
        n_perms=args.n_perms,
        seed_optimizer=args.seed_optimizer,
        max_fes=args.max_fes,
        workers=args.workers,
        out_dir=args.out_dir,
        verbose=not args.quiet,
    )


if __name__ == "__main__":
    main()
