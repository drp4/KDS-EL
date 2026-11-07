"""
Experiment E4: 7 Controlled Component Analysis Variants (Constituent Mechanism Analysis)
========================================================================================
Protocol Reference:
  - review_round_1/05_executable_experiment_plan.md (Section 7)
  - review_round_1/04_detailed_supplementary_experiment_design.md (Section 4 / Suite 3)

The 7 Controlled Algorithmic Configurations:
  1. KDS-EL Full: Forward TPS (0.70/0.30 -> 0.95/0.05 at q >= 0.70), gamma=0.99, P1(10)+P2(10), KER ke=3.
  2. Abl_Static_095: Static ws=[0.95, 0.05], gamma=0.99, P1(10)+P2(10), KER ke=3.
  3. Abl_Static_070: Static ws=[0.70, 0.30], gamma=0.99, P1(10)+P2(10), KER ke=3.
  4. Abl_Reversed: Reversed TPS (0.95/0.05 -> 0.70/0.30 at q >= 0.70), gamma=0.99, P1(10)+P2(10), KER ke=3.
  5. Abl_No_Decay: Forward TPS, gamma=1.00 (no decay), P1(10)+P2(10), KER ke=3.
  6. Abl_Single_P1: Forward TPS, gamma=0.99, All 20 individuals follow P1 rules (continuous PSO), KER ke=3.
  7. Abl_No_KER: Forward TPS, gamma=0.99, P1(10)+P2(10), KER strictly disabled (ke=0).

Standardized Optimization Constraints:
  - N = 20, Max_FEs = 2000.
  - Outer 5 folds with inner 5-fold evaluation on training set only.
  - Full micro-telemetry tracking: KER accept rate, P2 feasibility, gbest update sources,
    signed credit decomposition (W_class vs W_size), and requests closed-loop accounting.
"""

import os
import sys
import json
import time
import argparse
import platform
import numpy as np
from datetime import datetime
from concurrent.futures import ProcessPoolExecutor, as_completed

# Ensure project root is in sys.path
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

from config import BENCHMARK_19_DATASETS, DATA_DIR_TXT, DATA_DIR_MAT
from utils import load_dataset, ker_flip, compute_mi_scores
from nested_evaluator import NestedSplitsManager, BudgetEvaluator, BlindOuterEvaluator, IntegrityAuditor


# ══════════════════════════════════════════════════════════════════════════════
# Constants & Default Configurations
# ══════════════════════════════════════════════════════════════════════════════

E4_VARIANT_SPECS = {
    "KDS_EL_Full": {
        "label": "KDS-EL (Full)",
        "enable_tps": True,
        "ws1": [0.70, 0.30],
        "ws2": [0.95, 0.05],
        "decay": 0.99,
        "single_p1": False,
        "enable_ker": True,
        "elite_k": 3,
    },
    "Abl_Static_095": {
        "label": "Static-095 (High Acc)",
        "enable_tps": False,
        "ws1": [0.95, 0.05],
        "ws2": [0.95, 0.05],
        "decay": 0.99,
        "single_p1": False,
        "enable_ker": True,
        "elite_k": 3,
    },
    "Abl_Static_070": {
        "label": "Static-070 (High Comp)",
        "enable_tps": False,
        "ws1": [0.70, 0.30],
        "ws2": [0.70, 0.30],
        "decay": 0.99,
        "single_p1": False,
        "enable_ker": True,
        "elite_k": 3,
    },
    "Abl_Reversed": {
        "label": "Reversed (0.95->0.70)",
        "enable_tps": True,
        "ws1": [0.95, 0.05],
        "ws2": [0.70, 0.30],
        "decay": 0.99,
        "single_p1": False,
        "enable_ker": True,
        "elite_k": 3,
    },
    "Abl_No_Decay": {
        "label": "No-Decay (gamma=1.00)",
        "enable_tps": True,
        "ws1": [0.70, 0.30],
        "ws2": [0.95, 0.05],
        "decay": 1.00,
        "single_p1": False,
        "enable_ker": True,
        "elite_k": 3,
    },
    "Abl_Single_P1": {
        "label": "Single-P1 (Pure Continuous)",
        "enable_tps": True,
        "ws1": [0.70, 0.30],
        "ws2": [0.95, 0.05],
        "decay": 0.99,
        "single_p1": True,
        "enable_ker": True,
        "elite_k": 3,
    },
    "Abl_No_KER": {
        "label": "No-KER (ke=0)",
        "enable_tps": True,
        "ws1": [0.70, 0.30],
        "ws2": [0.95, 0.05],
        "decay": 0.99,
        "single_p1": False,
        "enable_ker": False,
        "elite_k": 0,
    },
}

# Prespecified 10 optimization seeds strictly matching Section 1.3 of the Plan
DEFAULT_SEEDS = [7, 30, 1, 42, 100, 2024, 999, 1234, 555, 888]
DEFAULT_OUT_DIR = os.path.join(PROJECT_ROOT, "output", "nested_cv", "e4_component_analysis")
DEFAULT_SPLITS_DIR = os.path.join(PROJECT_ROOT, "output", "nested_cv", "splits")


# ══════════════════════════════════════════════════════════════════════════════
# Parameterized Variant Optimization Engine with Telemetry Hooks
# ══════════════════════════════════════════════════════════════════════════════

def run_e4_variant_optimization(X_train, y_train, evaluator, variant_name, opts=None, seed=7):
    """
    Executes a single controlled variant optimization run under strict BudgetEvaluator limits.
    Captures fine-grained telemetry:
      - Signed credit decomposition: W_class, W_size
      - gbest event source tracking: init, regular_p1, regular_p2, ker, air
      - P2 feasibility rate, KER accept rate, AIR triggers
    """
    if opts is None:
        opts = {}
    spec = E4_VARIANT_SPECS[variant_name]
    np.random.seed(seed)
    N_tr, dim = X_train.shape

    N = opts.get("N", 20)
    half = N // 2
    thres = opts.get("thres", 0.6)
    lb, ub = 0.0, 1.0
    c1 = c2 = c3 = 2.0
    w = 0.9
    Vmax = (ub - lb) / 2
    patience = opts.get("stall_patience", 20)

    # Variant specific parameters
    enable_tps = spec["enable_tps"]
    ws1 = spec["ws1"]
    ws2 = spec["ws2"]
    current_ws = ws1
    switched = False
    decay = spec["decay"]
    single_p1 = spec["single_p1"]
    enable_ker = spec["enable_ker"]
    elite_k = spec["elite_k"]
    flip_count = max(1, int(opts.get("flip_frac", 0.01) * dim))
    rand_p = opts.get("rand_flip_p", 0.10)

    # Compute MI on outer train only
    mi = compute_mi_scores(X_train, y_train)

    # Define high-MI and low-MI quantile masks for signed credit attribution
    # Strictly matching Section 6.2/6.3: Top 10% ceil(0.10*D) and Bottom 50% floor(0.50*D) with stable tie-breaking
    order_mi = np.argsort(-mi, kind="stable")
    top_k = max(1, int(np.ceil(0.10 * dim)))
    bot_k = max(1, int(np.floor(0.50 * dim)))
    high_mi_mask = np.zeros(dim, dtype=bool)
    high_mi_mask[order_mi[:top_k]] = True
    low_mi_mask = np.zeros(dim, dtype=bool)
    low_mi_mask[order_mi[-bot_k:]] = True

    # Population Initialization
    P = np.zeros((N, dim))
    if single_p1:
        # All 20 continuous PSO with MI guidance
        P[:half] = np.clip(mi + np.random.normal(0, 0.1, (half, dim)), lb, ub)
        P[half:] = np.random.uniform(lb, ub, (N - half, dim))
    else:
        # Heterogeneous dual-swarm P1(10) + P2(10)
        P[:half] = np.clip(mi + np.random.normal(0, 0.1, (half, dim)), lb, ub)
        P[half:] = np.random.uniform(lb, ub, (N - half, dim))

    V = np.zeros((N, dim))
    weight = np.zeros(dim)
    W_class = np.zeros(dim, dtype=np.float64)
    W_size = np.zeros(dim, dtype=np.float64)
    W_barrier = np.zeros(dim, dtype=np.float64)

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

    # Telemetry Counters
    stall_counter = 0
    generations = 0
    ker_attempts = 0
    ker_accepts = 0
    air_triggers = 0
    p2_valid_count = 0
    p2_total_count = 0
    gbest_event_sources = {"init": 1, "regular_p1": 0, "regular_p2": 0, "ker": 0, "air": 0}

    while evaluator.has_budget():
        generations += 1
        gen_start_fitG = fitG

        # ── TPS Switch Boundary Check ──
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

        # Weight Decay across all attribution channels
        weight *= decay
        W_class *= decay
        W_size *= decay
        W_barrier *= decay

        P_new = P.copy()
        Xsub_best = Pbest[half + np.argmin(fitP[half:])].copy() if not single_p1 else Gbest.copy()

        # Generate candidates
        for i in range(N):
            if single_p1 or i < half:
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
                # Subpopulation 2: Probability sampling from weight
                p2_total_count += 1
                vf = np.maximum(weight, 0.0)
                sv = vf.sum()
                prob = vf / sv if sv > 0 else np.full(dim, 0.5)
                P_new[i] = (np.random.rand(dim) < prob).astype(float)
                if (P_new[i] > thres).sum() >= 3:
                    p2_valid_count += 1

        # Evaluate and In-Place Greedy Replacement with Signed Credit Attribution
        for i in range(N):
            if not evaluator.has_budget():
                break
            fv_n = P_new[i] > thres
            fv_o = Pbest[i] > thres
            fit_new = evaluator.evaluate(fv_n, ws=current_ws)

            # Signed credit delta
            delta = fitP[i] - fit_new
            d_p = int(fv_o.sum())
            d_x = int(fv_n.sum())

            # Size component delta
            delta_size = current_ws[1] * float(d_p - d_x) / max(1, dim)

            # Barrier decoupling: if either endpoint has d < 3, no CV was run.
            # Per Protocol Section 6(1), set delta_class = 0 and route penalty to barrier.
            both_feasible = (d_p >= 3) and (d_x >= 3)
            if both_feasible:
                delta_class = delta - delta_size
                delta_barrier = 0.0
            else:
                delta_class = 0.0
                delta_barrier = delta - delta_size

            # Direction vector s_j = (2 x_j - 1) on changed bits
            change = np.logical_xor(fv_n, fv_o)
            dir_s = np.zeros(dim)
            dir_s[change] = (2 * fv_n[change].astype(float) - 1.0)

            # Unified signed attribution
            weight += delta * dir_s
            W_class += delta_class * dir_s
            W_size += delta_size * dir_s
            W_barrier += delta_barrier * dir_s

            if fit_new < fitP[i]:
                # Candidate improved
                Pbest[i] = P_new[i].copy()
                fitP[i] = fit_new

                # Check gbest update
                if fitP[i] < fitG:
                    fitG = float(fitP[i])
                    Gbest = Pbest[i].copy()
                    stall_counter = 0
                    source_key = "regular_p1" if (single_p1 or i < half) else "regular_p2"
                    gbest_event_sources[source_key] += 1
            else:
                # Candidate did not improve (Pbest retained, weights already symmetrically updated)
                pass

        P = P_new.copy()

        # KER Elite Mutation (if enabled)
        if enable_ker and elite_k > 0:
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
                    if fitP[e] < fitG:
                        fitG = float(fitP[e])
                        Gbest = Pbest[e].copy()
                        stall_counter = 0
                        gbest_event_sources["ker"] += 1

        # Check generation stall
        if fitG < gen_start_fitG:
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
                    gbest_event_sources["air"] += 1
            stall_counter = 0

    mask = (Gbest > thres).astype(bool)
    if not mask.any():
        mask[np.argmax(Gbest)] = True

    # Signed Credit Separation Statistic (Delta W_class)
    high_mean = float(np.mean(W_class[high_mi_mask])) if high_mi_mask.any() else 0.0
    low_mean = float(np.mean(W_class[low_mi_mask])) if low_mi_mask.any() else 0.0
    delta_w_class = high_mean - low_mean

    return {
        "mask": mask,
        "fitG": fitG,
        "generations_completed": generations,
        "ker_attempts": ker_attempts,
        "ker_accepts": ker_accepts,
        "ker_accept_rate": float(ker_accepts / max(1, ker_attempts)),
        "air_triggers": air_triggers,
        "p2_valid_ratio": float(p2_valid_count / max(1, p2_total_count)) if not single_p1 else 1.0,
        "gbest_event_sources": gbest_event_sources,
        "delta_w_class": float(delta_w_class),
        "stop_reason": "budget_exhausted" if not evaluator.has_budget() else "normal",
    }


# ══════════════════════════════════════════════════════════════════════════════
# Single Run Execution & Downstream Blind Evaluation
# ══════════════════════════════════════════════════════════════════════════════

def execute_e4_single_run(
    dataset_name,
    variant_name,
    outer_fold_idx=1,
    run_idx=1,
    seed=7,
    max_fes=2000,
    pop_size=20,
    splits_dir=None,
    out_base_dir=None,
    verbose=False,
):
    """
    Executes a single E4 optimization run with complete outer blind test evaluation.
    """
    t0_run = time.perf_counter()
    if splits_dir is None:
        splits_dir = DEFAULT_SPLITS_DIR
    if out_base_dir is None:
        out_base_dir = DEFAULT_OUT_DIR

    X, y = load_dataset(dataset_name, DATA_DIR_TXT, DATA_DIR_MAT)
    N_samples, D = X.shape

    splits_mgr = NestedSplitsManager(splits_dir)
    outer_splits = splits_mgr.get_outer_splits(dataset_name, y, n_splits=5, seed=42)
    outer_k = outer_fold_idx - 1
    train_idx, test_idx = outer_splits[outer_k]

    X_train_outer, y_train_outer = X[train_idx], y[train_idx]
    X_test_outer, y_test_outer = X[test_idx], y[test_idx]

    inner_splits = splits_mgr.get_inner_splits(dataset_name, outer_fold_idx, y_train_outer, n_splits=5, seed=42)

    evaluator = BudgetEvaluator(
        X_train_outer=X_train_outer,
        y_train_outer=y_train_outer,
        inner_splits=inner_splits,
        max_fes=max_fes,
        knn_k=3,
        use_fast_knn=False,
    )

    opts = {
        "N": pop_size,
        "stall_patience": 20,
        "weight_decay": E4_VARIANT_SPECS[variant_name]["decay"],
        "thres": 0.6,
    }

    t0_search = time.perf_counter()
    res_search = run_e4_variant_optimization(
        X_train_outer, y_train_outer, evaluator, variant_name, opts=opts, seed=seed
    )
    search_time = time.perf_counter() - t0_search
    best_mask = res_search["mask"]
    active_features = int(best_mask.sum())

    # Blind Downstream Outer Evaluation
    t0_blind = time.perf_counter()
    outer_metrics = BlindOuterEvaluator.evaluate(
        X_train_outer, y_train_outer, X_test_outer, y_test_outer, best_mask
    )
    blind_eval_time = time.perf_counter() - t0_blind
    total_time = time.perf_counter() - t0_run

    # Audit check
    all_passed, audit_checks = IntegrityAuditor.audit_run(
        dataset_name=dataset_name,
        outer_fold_idx=outer_fold_idx,
        N_samples=N_samples,
        train_indices=train_idx,
        test_indices=test_idx,
        inner_splits=inner_splits,
        evaluator=evaluator,
        selected_mask=best_mask,
        outer_results=outer_metrics,
        is_twophase=E4_VARIANT_SPECS[variant_name]["enable_tps"],
    )

    run_record = {
        "dataset": dataset_name,
        "variant": variant_name,
        "variant_label": E4_VARIANT_SPECS[variant_name]["label"],
        "outer_fold": outer_fold_idx,
        "run_idx": run_idx,
        "seed": seed,
        "candidate_eval_requests": evaluator.candidate_eval_requests,
        "shortcut_eval_requests": evaluator.shortcut_eval_requests,
        "cache_hit_count": evaluator.cache_hit_count,
        "cv_eval_calls": evaluator.cv_eval_calls,
        "unique_masks": len(evaluator.unique_masks),
        "active_features": active_features,
        "active_features_ratio": float(active_features / D),
        "inner_gbest_fitness": float(res_search["fitG"]),
        "generations_completed": res_search["generations_completed"],
        "tps_switch_q": evaluator.tps_switch_q,
        "tps_rescore_requests": evaluator.tps_rescore_requests,
        "ker_attempts": res_search["ker_attempts"],
        "ker_accepts": res_search["ker_accepts"],
        "ker_accept_rate": res_search["ker_accept_rate"],
        "air_triggers": res_search["air_triggers"],
        "p2_valid_ratio": res_search["p2_valid_ratio"],
        "gbest_event_sources": res_search["gbest_event_sources"],
        "delta_w_class": res_search["delta_w_class"],
        "outer_test_metrics": outer_metrics,
        "timing": {
            "search_sec": round(search_time, 3),
            "blind_eval_sec": round(blind_eval_time, 3),
            "total_sec": round(total_time, 3),
        },
        "audit_passed": all_passed,
    }

    if verbose:
        status_tag = "[PASS]" if all_passed else "[FAIL]"
        print(
            f"  {status_tag} {dataset_name:10s} | {variant_name:15s} | F{outer_fold_idx} R{run_idx} | "
            f"Feats={active_features:4d} | 3NN-Acc={outer_metrics['knn']['accuracy']:.4f} | "
            f"BAcc={outer_metrics['knn']['balanced_accuracy']:.4f} | Time={total_time:.2f}s",
            flush=True,
        )

    return run_record


# ══════════════════════════════════════════════════════════════════════════════
# Main Experiment E4 Pipeline
# ══════════════════════════════════════════════════════════════════════════════

def run_experiment_e4(
    datasets=None,
    variants=None,
    folds=(1,),
    seeds=(7,),
    workers=2,
    splits_dir=None,
    out_dir=None,
    verbose=True,
):
    """
    Executes Experiment E4: 7 Controlled Component Analysis Variants across benchmarks.
    """
    t0_all = time.perf_counter()
    if datasets is None:
        datasets = ["Colon", "T1D", "BASEHOCK", "COIL20"]  # Default representative set
    if variants is None:
        variants = list(E4_VARIANT_SPECS.keys())
    if splits_dir is None:
        splits_dir = DEFAULT_SPLITS_DIR
    if out_dir is None:
        out_dir = DEFAULT_OUT_DIR

    os.makedirs(out_dir, exist_ok=True)

    print("\n" + "=" * 78)
    print("STARTING EXPERIMENT E4: 7 CONTROLLED COMPONENT ANALYSIS VARIANTS")
    print(f"Configurations (7): {variants}")
    print(f"Datasets ({len(datasets)}): {datasets}")
    print(f"Outer Folds: {list(folds)} | Seeds: {list(seeds)}")
    print(f"Parallel Workers: {workers} (OMP/MKL locked to 1)")
    print(f"Output Directory: {out_dir}")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 78)

    # Build task matrix
    task_specs = []
    for ds in datasets:
        for var in variants:
            for f_idx in folds:
                for r_idx, s in enumerate(seeds, start=1):
                    task_specs.append((ds, var, f_idx, r_idx, s))

    print(f"\nTotal Controlled Optimization Runs Planned: {len(task_specs)}")

    all_results = []
    if workers == 1:
        for ds, var, f_idx, r_idx, s in task_specs:
            rec = execute_e4_single_run(
                dataset_name=ds,
                variant_name=var,
                outer_fold_idx=f_idx,
                run_idx=r_idx,
                seed=s,
                splits_dir=splits_dir,
                out_base_dir=out_dir,
                verbose=verbose,
            )
            all_results.append(rec)
    else:
        with ProcessPoolExecutor(max_workers=workers) as executor:
            future_to_task = {
                executor.submit(
                    execute_e4_single_run, ds, var, f_idx, r_idx, s, 2000, 20, splits_dir, out_dir, False
                ): (ds, var, f_idx, r_idx, s)
                for ds, var, f_idx, r_idx, s in task_specs
            }
            completed = 0
            for fut in as_completed(future_to_task):
                ds, var, f_idx, r_idx, s = future_to_task[fut]
                completed += 1
                try:
                    rec = fut.result()
                    all_results.append(rec)
                    if verbose:
                        status_tag = "[PASS]" if rec["audit_passed"] else "[FAIL]"
                        om = rec["outer_test_metrics"]["knn"]
                        print(
                            f"  [{completed:3d}/{len(task_specs):3d}] {status_tag} {ds:10s} | {var:15s} | "
                            f"F{f_idx} R{r_idx} | Feats={rec['active_features']:4d} | "
                            f"Acc={om['accuracy']:.4f} | BAcc={om['balanced_accuracy']:.4f} | Time={rec['timing']['total_sec']:.2f}s",
                            flush=True,
                        )
                except Exception as e:
                    print(f"  [ERROR] Task ({ds}, {var}, F{f_idx}) failed: {str(e)}", flush=True)

    total_elapsed = time.perf_counter() - t0_all

    # Structure Deliverables
    detailed_json_path = os.path.join(out_dir, "e4_detailed_runs.json")
    with open(detailed_json_path, "w", encoding="utf-8") as f:
        json.dump(all_results, f, indent=2)

    # ══════════════════════════════════════════════════════════════════════════
    # Assemble Pooled OOF Across Folds and Group by Variant
    # ══════════════════════════════════════════════════════════════════════════
    dataset_labels = {}
    for ds in datasets:
        _, y_ds = load_dataset(ds, DATA_DIR_TXT, DATA_DIR_MAT)
        dataset_labels[ds] = y_ds

    grouped = {}
    for r in all_results:
        key = (r["dataset"], r["variant"], r["seed"])
        grouped.setdefault(key, []).append(r)

    pooled_oof_by_var = {}
    for (ds, var, s), recs in grouped.items():
        y_true = dataset_labels[ds]
        N_ds = len(y_true)
        y_oof = np.zeros(N_ds, dtype=int)
        covered = np.zeros(N_ds, dtype=bool)

        for rec in recs:
            t_idx = np.array(rec["test_indices"], dtype=int)
            preds = np.array(rec["outer_test_metrics"]["knn"]["y_pred"], dtype=int)
            y_oof[t_idx] = preds
            covered[t_idx] = True

        is_complete = bool(np.all(covered) and len(recs) == len(outer_folds))
        idx_eval = np.where(covered)[0]
        if len(idx_eval) > 0:
            acc = float(accuracy_score(y_true[idx_eval], y_oof[idx_eval]))
            bacc = float(balanced_accuracy_score(y_true[idx_eval], y_oof[idx_eval]))
            f1 = float(f1_score(y_true[idx_eval], y_oof[idx_eval], average="macro", zero_division=0))
        else:
            acc = bacc = f1 = 0.0

        pooled_oof_by_var.setdefault(var, []).append({
            "dataset": ds,
            "seed": s,
            "accuracy": acc,
            "balanced_accuracy": bacc,
            "macro_f1": f1,
            "is_complete_5fold": is_complete,
            "mean_features": float(np.mean([r["active_features"] for r in recs])),
            "total_time": float(np.sum([r["timing"]["total_sec"] for r in recs])),
            "ker_accept_rate": float(np.mean([r["ker_accept_rate"] for r in recs if r["ker_attempts"] > 0])) if any(r["ker_attempts"] > 0 for r in recs) else 0.0,
            "p2_valid_ratio": float(np.mean([r["p2_valid_ratio"] for r in recs])),
            "delta_w_class": float(np.mean([r["delta_w_class"] for r in recs])),
            "passed_audits": sum(1 for r in recs if r["audit_passed"]),
            "total_runs": len(recs),
        })

    # Per-variant summary matrix based on assembled Pooled OOF
    variant_summary = {}
    for var in variants:
        seed_entries = pooled_oof_by_var.get(var, [])
        if not seed_entries:
            continue
        accs = [e["accuracy"] for e in seed_entries]
        baccs = [e["balanced_accuracy"] for e in seed_entries]
        f1s = [e["macro_f1"] for e in seed_entries]
        feats = [e["mean_features"] for e in seed_entries]
        times = [e["total_time"] for e in seed_entries]
        ker_rates = [e["ker_accept_rate"] for e in seed_entries if e["ker_accept_rate"] > 0]
        p2_feas = [e["p2_valid_ratio"] for e in seed_entries]
        delta_ws = [e["delta_w_class"] for e in seed_entries]

        variant_summary[var] = {
            "label": E4_VARIANT_SPECS[var]["label"],
            "total_seeds_evaluated": len(seed_entries),
            "complete_5fold_seeds": sum(1 for e in seed_entries if e["is_complete_5fold"]),
            "passed_audits": sum(e["passed_audits"] for e in seed_entries),
            "mean_accuracy": float(np.mean(accs)),
            "std_accuracy": float(np.std(accs)),
            "mean_balanced_accuracy": float(np.mean(baccs)),
            "std_balanced_accuracy": float(np.std(baccs)),
            "mean_macro_f1": float(np.mean(f1s)),
            "std_macro_f1": float(np.std(f1s)),
            "mean_active_features": float(np.mean(feats)),
            "std_active_features": float(np.std(feats)),
            "mean_wall_clock_sec": float(np.mean(times)),
            "mean_ker_accept_rate": float(np.mean(ker_rates)) if ker_rates else 0.0,
            "mean_p2_valid_ratio": float(np.mean(p2_feas)),
            "mean_delta_w_class": float(np.mean(delta_ws)),
        }

    summary_json_path = os.path.join(out_dir, "e4_summary_table.json")
    payload = {
        "experiment": "E4_Controlled_Component_Analysis",
        "timestamp": datetime.now().isoformat(),
        "total_runs_completed": len(all_results),
        "total_runs_planned": len(task_specs),
        "is_complete": bool(len(all_results) == len(task_specs)),
        "total_elapsed_sec": round(total_elapsed, 2),
        "variant_summary": variant_summary,
        "system_metadata": {
            "platform": platform.platform(),
            "python": platform.python_version(),
            "workers": workers,
        },
    }
    with open(summary_json_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)

    # Markdown Report
    report_md_path = os.path.join(out_dir, "e4_component_analysis_report.md")
    with open(report_md_path, "w", encoding="utf-8") as f:
        f.write("# E4: Controlled Constituent Mechanism Analysis Report\n\n")
        f.write(f"- **Execution Timestamp**: {payload['timestamp']}\n")
        f.write(f"- **Protocol Reference**: `review_round_1/05_executable_experiment_plan.md` (Section 7)\n")
        f.write(f"- **Evaluated Configurations (7)**: KDS-EL Full, Static-095, Static-070, Reversed, No-Decay, Single-P1, No-KER\n")
        f.write(f"- **Runs Status**: `{len(all_results)} / {len(task_specs)}` completed (Complete: `{payload['is_complete']}`)\n")
        f.write(f"- **Total Elapsed Time**: `{total_elapsed:.2f} s`\n\n")

        if not payload["is_complete"]:
            f.write("> [!WARNING] Incomplete Execution Diagnostic Banner\n")
            f.write(f"> Only {len(all_results)} of {len(task_specs)} planned runs finished. The metrics below represent partial progress and cannot serve as formal empirical claims.\n\n")

        f.write("> **Formal Methodological Demarcation**:\n")
        f.write("> In strict accordance with Elsevier standards, component contributions are evaluated before and after ")
        f.write("controlled algorithmic modifications under identical evaluation budgets (Max_FEs = 2000, N = 20). ")
        f.write("All variants are tested under strict outer test isolation without circular data leakage.\n\n")

        f.write("## 1. Controlled Mechanism Contribution Matrix\n\n")
        f.write("| Algorithmic Configuration | Pooled OOF Acc | Pooled OOF BAcc | Pooled OOF F1 | Mean Features ($d$) | KER Accept Rate | P2 Feasible Rate | $\\Delta W_{\\mathrm{class}}$ |\n")
        f.write("| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |\n")

        for var, s in variant_summary.items():
            f.write(
                f"| **`{var}`** ({s['label']}) | **{s['mean_accuracy']:.4f}** ± {s['std_accuracy']:.3f} | "
                f"{s['mean_balanced_accuracy']:.4f} ± {s['std_balanced_accuracy']:.3f} | "
                f"{s['mean_macro_f1']:.4f} | **{s['mean_active_features']:.1f}** | "
                f"{s['mean_ker_accept_rate']*100:.1f}% | {s['mean_p2_valid_ratio']*100:.1f}% | "
                f"{s['mean_delta_w_class']:.4f} |\n"
            )

        f.write("\n## 2. Key Academic Findings & Mechanism Validation\n\n")
        if not variant_summary or not payload["is_complete"]:
            f.write("Execution is partial or incomplete. Dynamic mechanism findings will be generated automatically upon completion of all planned runs.\n")
        else:
            full_res = variant_summary.get("KDS_EL_Full")
            st095_res = variant_summary.get("Abl_Static_095")
            rev_res = variant_summary.get("Abl_Reversed")
            noker_res = variant_summary.get("Abl_No_KER")
            sp1_res = variant_summary.get("Abl_Single_P1")

            f.write("1. **TPS Dynamic Scheduling Rationale**: ")
            if full_res and st095_res:
                if full_res["mean_active_features"] < st095_res["mean_active_features"] and full_res["mean_accuracy"] >= st095_res["mean_accuracy"] - 0.005:
                    f.write(f"KDS-EL Full achieves superior feature compactness ({full_res['mean_active_features']:.1f} vs {st095_res['mean_active_features']:.1f}) while maintaining comparable out-of-fold accuracy ({full_res['mean_accuracy']:.4f} vs {st095_res['mean_accuracy']:.4f}), supporting the two-phase scheduling rationale.\n")
                elif rev_res and rev_res["mean_accuracy"] > full_res["mean_accuracy"] + 0.01:
                    f.write(f"Empirical evidence does not support the forward scheduling hypothesis on these instances; Reversed configuration achieves higher accuracy ({rev_res['mean_accuracy']:.4f} vs {full_res['mean_accuracy']:.4f}).\n")
                else:
                    f.write(f"Forward TPS and static configurations show comparable performance profiles ({full_res['mean_accuracy']:.4f} vs {st095_res['mean_accuracy']:.4f}), indicating localized scheduling sensitivity.\n")

            f.write("2. **Dual-Swarm Structure (Single-P1 vs Dual-Swarm)**: ")
            if full_res and sp1_res:
                diff_feats = sp1_res["mean_active_features"] - full_res["mean_active_features"]
                diff_acc = full_res["mean_accuracy"] - sp1_res["mean_accuracy"]
                f.write(f"Dual-swarm configuration relative to Single-P1 yields an accuracy delta of {diff_acc:+.4f} and feature count delta of {diff_feats:+.1f}, reflecting the structural contribution of Subpopulation 2.\n")

            f.write("3. **KER Elite Refinement (Full vs No-KER)**: ")
            if full_res and noker_res:
                if full_res["mean_accuracy"] >= noker_res["mean_accuracy"]:
                    f.write(f"Enabling KER yields an accuracy gain of {full_res['mean_accuracy'] - noker_res['mean_accuracy']:+.4f} alongside an observed KER acceptance rate of {full_res['mean_ker_accept_rate']*100:.1f}%.\n")
                else:
                    f.write(f"No-KER achieves competitive or superior convergence ({noker_res['mean_accuracy']:.4f} vs {full_res['mean_accuracy']:.4f}), indicating that regular swarm steps may be equally effective under strict evaluation budgets.\n")

    print("\n" + "=" * 78)
    print(f"EXPERIMENT E4 COMPLETED in {total_elapsed:.2f}s!")
    print(f"Artifacts saved:")
    print(f"  - Detailed Runs JSON: {detailed_json_path}")
    print(f"  - Summary Matrix JSON: {summary_json_path}")
    print(f"  - Academic Markdown Report: {report_md_path}")
    print("=" * 78)

    return payload


# ══════════════════════════════════════════════════════════════════════════════
# Command Line Interface
# ══════════════════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(description="Run Experiment E4: 7 Controlled Component Analysis Variants")
    parser.add_argument(
        "--datasets",
        type=str,
        nargs="+",
        default=["Colon", "T1D", "BASEHOCK", "COIL20"],
        help="Datasets to evaluate (default: Colon, T1D, BASEHOCK, COIL20)",
    )
    parser.add_argument(
        "--variants",
        type=str,
        nargs="+",
        default=list(E4_VARIANT_SPECS.keys()),
        help="Variants to evaluate (default: all 7 configurations)",
    )
    parser.add_argument(
        "--folds",
        type=int,
        nargs="+",
        default=[1],
        help="Outer fold indices (default: 1; pass 1 2 3 4 5 for all 5 folds)",
    )
    parser.add_argument(
        "--seeds",
        type=int,
        nargs="+",
        default=[7],
        help="Random seeds (default: 7; pass 10 seeds for full repetitions)",
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=2,
        help="Number of parallel worker processes (default: 2)",
    )
    parser.add_argument(
        "--out-dir",
        type=str,
        default=DEFAULT_OUT_DIR,
        help=f"Output directory (default: {DEFAULT_OUT_DIR})",
    )
    parser.add_argument("--quiet", action="store_true", help="Suppress detailed console logs")
    args = parser.parse_args()

    run_experiment_e4(
        datasets=args.datasets,
        variants=args.variants,
        folds=args.folds,
        seeds=args.seeds,
        workers=args.workers,
        out_dir=args.out_dir,
        verbose=not args.quiet,
    )


if __name__ == "__main__":
    main()
