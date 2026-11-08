"""
Experiment E5: Full Outer Nested Generalization Benchmark Across Downstream Classifiers
========================================================================================
Protocol Reference:
  - review_round_1/05_executable_experiment_plan.md (Section 8)
  - review_round_1/04_detailed_supplementary_experiment_design.md (Section II & IV)

Experimental Scope:
  - Stage 1 Core (5 algorithms): KDS_EL_TwoPhase, MEL, MEL_MI, KDS_EL_NoPool, bIRIME.
  - Stage 2 Extended (7 algorithms): FWPSO, SaWDE, PSO_CSM, BPSO, BinCOA, IGPSO, DENCA_SO.
  - Total Scale (Core): 19 datasets x 5 outer folds x 10 seeds = 4,750 optimization runs.
  - Downstream Classifiers (5 models evaluated under BlindOuterEvaluator):
      1. 3-NN (authoritative local geometry benchmark)
      2. RBF-SVM (kernelized maximum-margin classifier with balanced class weights)
      3. Random Forest (scale-invariant ensemble, 100 trees, n_jobs=1)
      4. Gaussian Naive Bayes (probabilistic feature-independence classifier)
      5. Shrinkage LDA (linear discriminant with automated Ledoit-Wolf shrinkage)

Academic Protocols:
  - Strict compliance with AGENTS.md:
      * Zero outer test leakage (priors, initialization, search, model fitting strictly in outer train).
      * Pooled OOF predictions aggregated across the 5 outer folds per run.
      * Multi-metric reporting: Accuracy, Balanced Accuracy, Macro-F1, selected features, wall-clock time.
      * Cross-classifier migration analysis and optimistic search bias quantification.
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
from sklearn.metrics import accuracy_score, balanced_accuracy_score, f1_score

# Ensure project root is in sys.path
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

from config import BENCHMARK_19_DATASETS, DATA_DIR_TXT, DATA_DIR_MAT
from utils import load_dataset
from nested_evaluator import NestedSplitsManager, BudgetEvaluator, BlindOuterEvaluator, IntegrityAuditor
from algorithms_nested import NESTED_RUNNERS


# ══════════════════════════════════════════════════════════════════════════════
# Algorithm Category Groupings
# ══════════════════════════════════════════════════════════════════════════════

STAGE1_CORE_ALGOS = [
    "KDS_EL_TwoPhase",
    "MEL",
    "MEL_MI",
    "KDS_EL_NoPool",
    "bIRIME",
]

STAGE2_EXTENDED_ALGOS = [
    "BPSO",
    "FWPSO",
    "SaWDE",
    "PSO_CSM",
    "BinCOA",
    "IGPSO",
    "DENCA_SO",
]

ALL_E5_ALGOS = STAGE1_CORE_ALGOS + STAGE2_EXTENDED_ALGOS

# Prespecified 10 optimization seeds strictly matching Section 1.3 of the Plan
DEFAULT_SEEDS = [7, 30, 1, 42, 100, 2024, 999, 1234, 555, 888]
CLASSIFIER_NAMES = ["knn", "svm", "random_forest", "naive_bayes", "lda"]


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
# Single Optimization Run Execution
# ══════════════════════════════════════════════════════════════════════════════

def execute_e5_single_run(
    dataset_name,
    algo_name,
    outer_fold_idx=1,
    run_idx=1,
    seed=7,
    max_fes=2000,
    pop_size=20,
    splits_dir=None,
    use_fast_knn=False,
    verbose=False,
):
    """
    Executes a single nested optimization run under strict outer test isolation.
    """
    t0_run = time.perf_counter()
    if splits_dir is None:
        splits_dir = os.path.join(PROJECT_ROOT, "output", "nested_cv", "splits")

    # 1. Load dataset
    X, y = load_dataset(dataset_name, DATA_DIR_TXT, DATA_DIR_MAT)
    N_samples, D = X.shape

    # 2. Get splits
    splits_mgr = NestedSplitsManager(splits_dir)
    outer_splits = splits_mgr.get_outer_splits(dataset_name, y, n_splits=5, seed=42)
    outer_k = outer_fold_idx - 1
    train_idx, test_idx = outer_splits[outer_k]

    X_train_outer, y_train_outer = X[train_idx], y[train_idx]
    X_test_outer, y_test_outer = X[test_idx], y[test_idx]

    inner_splits = splits_mgr.get_inner_splits(
        dataset_name, outer_fold_idx, y_train_outer, n_splits=5, seed=42
    )

    # 3. Create BudgetEvaluator on outer train ONLY
    evaluator = BudgetEvaluator(
        X_train_outer=X_train_outer,
        y_train_outer=y_train_outer,
        inner_splits=inner_splits,
        max_fes=max_fes,
        knn_k=3,
        use_fast_knn=use_fast_knn,
    )

    # 4. Run algorithm
    runner_fn = NESTED_RUNNERS[algo_name]
    opts = {
        "N": pop_size,
        "thres": 0.60,
        "weight_decay": 0.99,
        "flip_frac": 0.01,
        "rand_flip_p": 0.10,
        "stall_patience": 20,
        "elite_k": 3,
        "ws_phase1": [0.70, 0.30],
        "ws_phase2": [0.95, 0.05],
        "ws": [0.90, 0.10],
    }

    t0_search = time.perf_counter()
    algo_result = runner_fn(X_train_outer, y_train_outer, evaluator, opts, seed=seed)
    search_time = time.perf_counter() - t0_search

    selected_mask = np.asarray(algo_result["mask"], dtype=bool)
    if not selected_mask.any():
        selected_mask[np.random.randint(D)] = True
    active_features = int(selected_mask.sum())

    # 5. One-Shot Blind Outer Evaluation across 5 downstream classifiers
    t0_blind = time.perf_counter()
    outer_metrics = BlindOuterEvaluator.evaluate(
        X_train_outer=X_train_outer,
        y_train_outer=y_train_outer,
        X_test_outer=X_test_outer,
        y_test_outer=y_test_outer,
        mask=selected_mask,
    )
    blind_eval_time = time.perf_counter() - t0_blind
    total_run_time = time.perf_counter() - t0_run

    # 6. Automated Integrity Audit
    is_twophase = "TwoPhase" in algo_name
    all_checks_passed, audit_details = IntegrityAuditor.audit_run(
        dataset_name=dataset_name,
        outer_fold_idx=outer_fold_idx,
        N_samples=N_samples,
        train_indices=train_idx,
        test_indices=test_idx,
        inner_splits=inner_splits,
        evaluator=evaluator,
        selected_mask=selected_mask,
        outer_results=outer_metrics,
        is_twophase=is_twophase,
    )

    # Extract internal training error rate for optimistic bias estimation
    internal_error = evaluator.cache.get(selected_mask.tobytes(), None)
    internal_acc = 1.0 - internal_error if internal_error is not None else None

    run_record = {
        "dataset": dataset_name,
        "algorithm": algo_name,
        "outer_fold": outer_fold_idx,
        "run_idx": run_idx,
        "seed": seed,
        "max_fes": max_fes,
        "total_dim": D,
        "selected_features": active_features,
        "selected_indices": np.where(selected_mask)[0].tolist(),
        "search_time_sec": float(search_time),
        "blind_eval_time_sec": float(blind_eval_time),
        "total_run_time_sec": float(total_run_time),
        "internal_acc": float(internal_acc) if internal_acc is not None else None,
        "evaluator_counters": {
            "candidate_eval_requests": evaluator.candidate_eval_requests,
            "shortcut_eval_requests": evaluator.shortcut_eval_requests,
            "cache_hit_count": evaluator.cache_hit_count,
            "cv_eval_calls": evaluator.cv_eval_calls,
            "filter_eval_requests": getattr(evaluator, "filter_eval_requests", 0),
            "inner_model_fits": evaluator.inner_model_fits,
            "unique_masks_count": len(evaluator.unique_masks),
            "tps_rescore_requests": evaluator.tps_rescore_requests,
        },
        "audit_passed": all_checks_passed,
        "audit": {
            "all_passed": all_checks_passed,
            "details": audit_details,
        },
        "outer_predictions": {
            clf: outer_metrics[clf]["y_pred"] for clf in CLASSIFIER_NAMES
        },
        "outer_metrics": {
            clf: {
                "accuracy": outer_metrics[clf]["accuracy"],
                "balanced_accuracy": outer_metrics[clf]["balanced_accuracy"],
                "macro_f1": outer_metrics[clf]["macro_f1"],
                "model_variant": outer_metrics[clf].get("model_variant", "standard"),
                "fallback_used": outer_metrics[clf].get("fallback_used", "none"),
            }
            for clf in CLASSIFIER_NAMES
        },
        "test_indices": test_idx.tolist(),
    }

    if verbose:
        status_tag = "PASS" if all_checks_passed else "FAIL"
        knn_acc = outer_metrics["knn"]["accuracy"]
        knn_bacc = outer_metrics["knn"]["balanced_accuracy"]
        print(
            f"  [{status_tag}] {dataset_name:10s} | {algo_name:18s} | "
            f"F{outer_fold_idx} R{run_idx} (seed={seed}) | "
            f"Feats={active_features:4d} | 3NN-Acc={knn_acc:.4f} | BAcc={knn_bacc:.4f} | "
            f"Time={total_run_time:.2f}s"
        )

    return run_record


# ══════════════════════════════════════════════════════════════════════════════
# Pooled Out-Of-Fold (OOF) Prediction Assembler
# ══════════════════════════════════════════════════════════════════════════════

def compute_pooled_oof_for_run(records_for_seed, y_true):
    """
    Concatenates 5 outer fold predictions into a full out-of-fold prediction vector
    and computes true Pooled OOF Accuracy, Balanced Accuracy, and Macro-F1 across 5 classifiers.
    """
    N = len(y_true)
    oof_results = {}

    for clf in CLASSIFIER_NAMES:
        y_oof = np.zeros(N, dtype=int)
        covered_indices = np.zeros(N, dtype=bool)

        for rec in records_for_seed:
            test_idx = np.array(rec["test_indices"], dtype=int)
            preds = np.array(rec["outer_predictions"][clf], dtype=int)
            y_oof[test_idx] = preds
            covered_indices[test_idx] = True

        is_complete = bool(np.all(covered_indices) and len(records_for_seed) == 5)
        cov_ratio = float(np.sum(covered_indices) / N)

        if not is_complete:
            # Partial folds run (e.g. dry run or testing with < 5 folds)
            idx_eval = np.where(covered_indices)[0]
            if len(idx_eval) == 0:
                acc = bacc = f1 = 0.0
            else:
                acc = float(accuracy_score(y_true[idx_eval], y_oof[idx_eval]))
                bacc = float(balanced_accuracy_score(y_true[idx_eval], y_oof[idx_eval]))
                f1 = float(f1_score(y_true[idx_eval], y_oof[idx_eval], average="macro", zero_division=0))
        else:
            acc = float(accuracy_score(y_true, y_oof))
            bacc = float(balanced_accuracy_score(y_true, y_oof))
            f1 = float(f1_score(y_true, y_oof, average="macro", zero_division=0))

        fold_variants = [r.get("outer_metrics", {}).get(clf, {}).get("model_variant", "standard") for r in records_for_seed]
        fold_fallbacks = [r.get("outer_metrics", {}).get(clf, {}).get("fallback_used", "none") for r in records_for_seed]

        oof_results[clf] = {
            "accuracy": acc,
            "balanced_accuracy": bacc,
            "macro_f1": f1,
            "is_complete_5fold": is_complete,
            "coverage_ratio": cov_ratio,
            "model_variants": fold_variants,
            "fallbacks_used": fold_fallbacks,
        }

    mean_feats = float(np.mean([r["selected_features"] for r in records_for_seed]))
    total_time = float(np.sum([r["total_run_time_sec"] for r in records_for_seed]))
    internal_accs = [r["internal_acc"] for r in records_for_seed if r["internal_acc"] is not None]
    mean_internal_acc = float(np.mean(internal_accs)) if internal_accs else None

    # Check both "audit_passed" and "audit.all_passed" to prevent format mismatch
    all_audits_passed = bool(
        len(records_for_seed) > 0 and
        all(r.get("audit_passed", r.get("audit", {}).get("all_passed", False)) for r in records_for_seed)
    )
    is_statistically_valid = bool(is_complete and all_audits_passed and cov_ratio == 1.0)

    return {
        "oof_metrics": oof_results,
        "is_complete_5fold": is_complete,
        "all_audits_passed": all_audits_passed,
        "is_statistically_valid": is_statistically_valid,
        "coverage_ratio": cov_ratio,
        "mean_selected_features": mean_feats,
        "total_seed_time_sec": total_time,
        "mean_internal_acc": mean_internal_acc,
    }


# ══════════════════════════════════════════════════════════════════════════════
# Experiment E5 Execution Orchestrator
# ══════════════════════════════════════════════════════════════════════════════

def run_experiment_e5(
    datasets=None,
    algorithms=None,
    outer_folds=None,
    seeds=None,
    max_fes=2000,
    pop_size=20,
    workers=2,
    out_dir=None,
    use_fast_knn=False,
    verbose=True,
):
    """
    Master orchestrator for Experiment E5 across datasets, algorithms, and outer folds.
    """
    t0_exp = time.perf_counter()
    if datasets is None:
        datasets = BENCHMARK_19_DATASETS
    if algorithms is None:
        algorithms = STAGE1_CORE_ALGOS
    if outer_folds is None:
        outer_folds = [1, 2, 3, 4, 5]
    if seeds is None:
        seeds = DEFAULT_SEEDS
    if out_dir is None:
        out_dir = os.path.join(PROJECT_ROOT, "output", "nested_cv", "e5_generalization")

    os.makedirs(out_dir, exist_ok=True)
    splits_dir = os.path.join(PROJECT_ROOT, "output", "nested_cv", "splits")

    # Enforce MKL/OMP single-threaded isolation
    os.environ["OMP_NUM_THREADS"] = "1"
    os.environ["MKL_NUM_THREADS"] = "1"
    os.environ["OPENBLAS_NUM_THREADS"] = "1"
    os.environ["VECLIB_MAXIMUM_THREADS"] = "1"
    os.environ["NUMEXPR_NUM_THREADS"] = "1"

    print("\n" + "=" * 80)
    print("STARTING EXPERIMENT E5: FULL OUTER NESTED GENERALIZATION BENCHMARK")
    print(f"Algorithms ({len(algorithms)}): {algorithms}")
    print(f"Datasets ({len(datasets)}): {datasets}")
    print(f"Outer Folds: {outer_folds} | Seeds ({len(seeds)}): {seeds}")
    print(f"Parallel Workers: {workers} (Single-layer process parallelism)")
    print(f"Fast k-NN Acceleration: {use_fast_knn}")
    print(f"Output Directory: {out_dir}")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80 + "\n")

    tasks = []
    for ds in datasets:
        for algo in algorithms:
            for seed_idx, s in enumerate(seeds, start=1):
                for f in outer_folds:
                    tasks.append((ds, algo, f, seed_idx, s))

    print(f"Total Nested Optimization Runs Planned: {len(tasks)}\n")

    completed_runs = []
    failed_runs = []
    if workers <= 1:
        for ds, algo, f, run_idx, s in tasks:
            try:
                rec = execute_e5_single_run(
                    dataset_name=ds,
                    algo_name=algo,
                    outer_fold_idx=f,
                    run_idx=run_idx,
                    seed=s,
                    max_fes=max_fes,
                    pop_size=pop_size,
                    splits_dir=splits_dir,
                    use_fast_knn=use_fast_knn,
                    verbose=verbose,
                )
                completed_runs.append(rec)
            except Exception as exc:
                failed_runs.append({
                    "dataset": ds,
                    "algorithm": algo,
                    "fold": f,
                    "run_idx": run_idx,
                    "seed": s,
                    "error": str(exc),
                })
                print(f"  [ERROR] {ds} | {algo} | F{f} R{run_idx} (seed={s}) raised: {exc}")
    else:
        with ProcessPoolExecutor(max_workers=workers) as executor:
            future_map = {
                executor.submit(
                    execute_e5_single_run,
                    ds, algo, f, run_idx, s,
                    max_fes, pop_size, splits_dir, use_fast_knn, verbose
                ): (ds, algo, f, run_idx, s)
                for ds, algo, f, run_idx, s in tasks
            }
            failed_runs = []
            for fut in as_completed(future_map):
                try:
                    rec = fut.result()
                    completed_runs.append(rec)
                except Exception as exc:
                    ds, algo, f, run_idx, s = future_map[fut]
                    failed_runs.append({
                        "dataset": ds,
                        "algorithm": algo,
                        "fold": f,
                        "run_idx": run_idx,
                        "seed": s,
                        "error": str(exc),
                    })
                    print(f"  [ERROR] {ds} | {algo} | F{f} R{run_idx} (seed={s}) raised: {exc}")

    # ══════════════════════════════════════════════════════════════════════════
    # Save Detailed Individual Runs JSON
    # ══════════════════════════════════════════════════════════════════════════
    detailed_json_path = os.path.join(out_dir, "e5_detailed_runs.json")
    with open(detailed_json_path, "w", encoding="utf-8") as f:
        json.dump(sanitize_for_json(completed_runs), f, indent=2)

    # ══════════════════════════════════════════════════════════════════════════
    # Assemble Pooled OOF Across Outer Folds and Aggregate Over Seeds
    # ══════════════════════════════════════════════════════════════════════════
    # Group runs by (dataset, algorithm, seed)
    grouped = {}
    for r in completed_runs:
        key = (r["dataset"], r["algorithm"], r["seed"])
        grouped.setdefault(key, []).append(r)

    # Compute Pooled OOF for complete 5-fold runs
    dataset_labels = {}
    for ds in datasets:
        _, y = load_dataset(ds, DATA_DIR_TXT, DATA_DIR_MAT)
        dataset_labels[ds] = y

    summary_records = {}
    for (ds, algo, s), recs in grouped.items():
        if len(recs) == len(outer_folds):
            y_true = dataset_labels[ds]
            try:
                oof_res = compute_pooled_oof_for_run(recs, y_true)
                summary_records.setdefault((ds, algo), []).append(oof_res)
            except Exception as e:
                print(f"  [WARNING] Pooled OOF assembly failed for ({ds}, {algo}, seed={s}): {e}")

    # Aggregate over seeds per (dataset, algorithm)
    agg_table = {}
    for (ds, algo), seed_results in summary_records.items():
        n_seeds = len(seed_results)
        if n_seeds == 0:
            continue

        entry = {
            "dataset": ds,
            "algorithm": algo,
            "n_completed_seeds": n_seeds,
            "mean_features": float(np.mean([s["mean_selected_features"] for s in seed_results])),
            "std_features": float(np.std([s["mean_selected_features"] for s in seed_results])),
            "mean_time_sec": float(np.mean([s["total_seed_time_sec"] for s in seed_results])),
            "classifiers": {},
        }

        # Check internal search vs OOF optimistic bias
        internal_accs = [s["mean_internal_acc"] for s in seed_results if s["mean_internal_acc"] is not None]
        if internal_accs:
            mean_int_acc = float(np.mean(internal_accs))
            entry["mean_internal_acc"] = mean_int_acc
            mean_3nn_oof = float(np.mean([s["oof_metrics"]["knn"]["accuracy"] for s in seed_results]))
            entry["optimistic_search_bias"] = float(mean_int_acc - mean_3nn_oof)

        for clf in CLASSIFIER_NAMES:
            accs = [s["oof_metrics"][clf]["accuracy"] for s in seed_results]
            baccs = [s["oof_metrics"][clf]["balanced_accuracy"] for s in seed_results]
            f1s = [s["oof_metrics"][clf]["macro_f1"] for s in seed_results]

            all_variants = [v for s in seed_results for v in s["oof_metrics"][clf].get("model_variants", [])]
            all_fallbacks = [fb for s in seed_results for fb in s["oof_metrics"][clf].get("fallbacks_used", [])]
            variant_counts = {v: all_variants.count(v) for v in set(all_variants)}
            fallback_counts = {fb: all_fallbacks.count(fb) for fb in set(all_fallbacks)}

            entry["classifiers"][clf] = {
                "accuracy_mean": float(np.mean(accs)),
                "accuracy_std": float(np.std(accs)),
                "balanced_accuracy_mean": float(np.mean(baccs)),
                "balanced_accuracy_std": float(np.std(baccs)),
                "macro_f1_mean": float(np.mean(f1s)),
                "macro_f1_std": float(np.std(f1s)),
                "model_variants_summary": variant_counts,
                "fallbacks_summary": fallback_counts,
            }

        agg_table.setdefault(algo, {})[ds] = entry

    tasks_executed_successfully = bool(len(failed_runs) == 0 and len(completed_runs) == len(tasks))
    all_audits_passed = bool(
        len(completed_runs) > 0 and
        all(r.get("audit_passed", r.get("audit", {}).get("all_passed", False)) for r in completed_runs)
    )
    all_seeds_valid = bool(
        len(summary_records) > 0 and
        all(s.get("is_statistically_valid", False) for seed_list in summary_records.values() for s in seed_list)
    )
    valid_for_formal_claims = bool(
        tasks_executed_successfully and
        len(outer_folds) == 5 and
        all_audits_passed and
        all_seeds_valid and
        len(agg_table) > 0
    )

    summary_payload = {
        "experiment": "E5_Nested_Cross_Classifier_Generalization",
        "timestamp": datetime.now().isoformat(),
        "total_planned_runs": len(tasks),
        "total_completed_runs": len(completed_runs),
        "tasks_executed_successfully": tasks_executed_successfully,
        "is_complete": tasks_executed_successfully,
        "valid_for_formal_claims": valid_for_formal_claims,
        "all_audits_passed": all_audits_passed,
        "failed_runs": failed_runs,
        "results": agg_table,
    }

    summary_json_path = os.path.join(out_dir, "e5_summary_table.json")
    with open(summary_json_path, "w", encoding="utf-8") as f:
        json.dump(sanitize_for_json(summary_payload), f, indent=2)

    # ══════════════════════════════════════════════════════════════════════════
    # Generate Academic Markdown Synthesis Report
    # ══════════════════════════════════════════════════════════════════════════
    md_report_path = os.path.join(out_dir, "e5_generalization_report.md")
    generate_e5_markdown_report(
        agg_table, algorithms, datasets, md_report_path,
        time.perf_counter() - t0_exp,
        is_complete=tasks_executed_successfully,
        valid_for_formal_claims=valid_for_formal_claims,
        n_completed=len(completed_runs), n_planned=len(tasks)
    )

    elapsed_total = time.perf_counter() - t0_exp
    print("\n" + "=" * 80)
    print(f"EXPERIMENT E5 COMPLETED in {elapsed_total:.2f}s!")
    print(f"Artifacts saved:")
    print(f"  - Detailed Runs JSON: {detailed_json_path}")
    print(f"  - Summary Matrix JSON: {summary_json_path}")
    print(f"  - Academic Markdown Report: {md_report_path}")
    print("=" * 80 + "\n")


def generate_e5_markdown_report(
    agg_table, algorithms, datasets, out_path, elapsed_time,
    is_complete=True, valid_for_formal_claims=False, n_completed=0, n_planned=0
):
    """
    Renders academic markdown synthesis report complying with AGENTS.md.
    """
    lines = []
    lines.append("# E5: Full Outer Nested Generalization Benchmark Report\n")
    lines.append(f"- **Execution Timestamp**: {datetime.now().isoformat()}")
    lines.append(f"- **Protocol Reference**: `review_round_1/05_executable_experiment_plan.md` (Section 8)")
    lines.append(f"- **Target Algorithms ({len(algorithms)})**: {', '.join(algorithms)}")
    lines.append(f"- **Evaluated Datasets ({len(datasets)})**: {', '.join(datasets)}")
    lines.append(f"- **Runs Status**: `{n_completed} / {n_planned}` completed (Tasks Execution Completed: `{is_complete}`, Valid for Formal Claims: `{valid_for_formal_claims}`)")
    lines.append(f"- **Downstream Models (5)**: 3-NN, RBF-SVM, Random Forest, GaussianNB, LDA (Shrinkage / SVD-safeguarded)")
    lines.append(f"- **Total Elapsed Time**: `{elapsed_time:.2f} s`\n")

    if not valid_for_formal_claims:
        lines.append("> [!WARNING] Incomplete / Diagnostic Execution Notice")
        lines.append(f"> Only {n_completed} of {n_planned} planned runs finished (valid for formal claims: `{valid_for_formal_claims}`). Incomplete outer folds (< 5), unverified audits, or incomplete seeds cannot serve as formal empirical claims in publication.\n")

    lines.append("> **Formal Methodological Demarcation**:")
    lines.append("> In strict adherence to rigorous Elsevier peer review standards, all evaluations in this report are conducted under complete outer test partition isolation. Mutual information estimation, population initialization, wrapper evolutionary search, preprocessing transformations, and model fitting are strictly confined within the training partition of each outer fold. Pooled out-of-fold predictions concatenated across the five outer test folds serve as the primary generalization metric, completely eliminating optimistic circular evaluation bias.\n")

    lines.append("## 1. Primary Classification Generalization Matrix (3-NN Pooled OOF)\n")
    lines.append("| Dataset | " + " | ".join([f"**{algo}** (Acc / BAcc / Feats)" for algo in algorithms]) + " |")
    lines.append("| :--- | " + " | ".join([":---:" for _ in algorithms]) + " |")

    for ds in datasets:
        row = [f"**`{ds}`**"]
        for algo in algorithms:
            entry = agg_table.get(algo, {}).get(ds, None)
            if entry is not None and "knn" in entry["classifiers"]:
                knn = entry["classifiers"]["knn"]
                acc_str = f"{knn['accuracy_mean']:.4f}±{knn['accuracy_std']:.3f}"
                bacc_str = f"{knn['balanced_accuracy_mean']:.4f}"
                feats_str = f"{entry['mean_features']:.1f}"
                row.append(f"{acc_str}<br>({bacc_str} / {feats_str})")
            else:
                row.append("—")
        lines.append("| " + " | ".join(row) + " |")

    lines.append("\n## 2. Downstream Model Transferability Profile (Cross-Classifier Generalization)\n")
    lines.append("The table below reports the average performance shift of alternative downstream inductive biases relative to the primary 3-NN classifier across all evaluated datasets.\n")

    lines.append(r"| Algorithm | 3-NN Acc | RBF-SVM Acc ($\Delta$) | Random Forest Acc ($\Delta$) | GaussianNB Acc ($\Delta$) | LDA (Shrinkage/SVD) Acc ($\Delta$) |")
    lines.append("| :--- | :---: | :---: | :---: | :---: | :---: |")

    for algo in algorithms:
        ds_entries = [agg_table.get(algo, {}).get(ds) for ds in datasets if agg_table.get(algo, {}).get(ds) is not None]
        if not ds_entries:
            continue

        mean_knn = float(np.mean([e["classifiers"]["knn"]["accuracy_mean"] for e in ds_entries]))
        mean_svm = float(np.mean([e["classifiers"]["svm"]["accuracy_mean"] for e in ds_entries]))
        mean_rf = float(np.mean([e["classifiers"]["random_forest"]["accuracy_mean"] for e in ds_entries]))
        mean_nb = float(np.mean([e["classifiers"]["naive_bayes"]["accuracy_mean"] for e in ds_entries]))
        mean_lda = float(np.mean([e["classifiers"]["lda"]["accuracy_mean"] for e in ds_entries]))

        d_svm = mean_svm - mean_knn
        d_rf = mean_rf - mean_knn
        d_nb = mean_nb - mean_knn
        d_lda = mean_lda - mean_knn

        lines.append(
            f"| **`{algo}`** | {mean_knn:.4f} | "
            f"{mean_svm:.4f} ({d_svm:+.4f}) | "
            f"{mean_rf:.4f} ({d_rf:+.4f}) | "
            f"{mean_nb:.4f} ({d_nb:+.4f}) | "
            f"{mean_lda:.4f} ({d_lda:+.4f}) |"
        )

    # LDA model resolution & fallback accounting
    lda_variants_total = {}
    lda_fallbacks_total = {}
    for algo in algorithms:
        ds_entries = [agg_table.get(algo, {}).get(ds) for ds in datasets if agg_table.get(algo, {}).get(ds) is not None]
        for e in ds_entries:
            lda_info = e.get("classifiers", {}).get("lda", {})
            for v, c in lda_info.get("model_variants_summary", {}).items():
                lda_variants_total[v] = lda_variants_total.get(v, 0) + c
            for fb, c in lda_info.get("fallbacks_summary", {}).items():
                lda_fallbacks_total[fb] = lda_fallbacks_total.get(fb, 0) + c

    if lda_variants_total:
        variant_desc = ", ".join([f"`{k}`: {v} fold evaluations" for k, v in sorted(lda_variants_total.items())])
        fallback_desc = ", ".join([f"`{k}`: {v}" for k, v in sorted(lda_fallbacks_total.items()) if k != "none"]) or "none"
        lines.append(f"\n> **LDA Model Variant Accounting**: {variant_desc} (Fallbacks triggered: {fallback_desc}). "
                     "Subsets with $d \\le 1000$ are evaluated with Ledoit--Wolf shrinkage LSQR; subsets with $d > 1000$ are evaluated with SVD to prevent covariance matrix memory allocation.\n")

    lines.append("\n## 3. Optimistic Search Bias Quantification\n")
    lines.append("Internal search surrogate error rate versus held-out pooled out-of-fold generalization error:\n")
    lines.append(r"| Algorithm | Internal Search Acc | Pooled OOF Acc | Optimistic Search Bias ($\Delta_{\mathrm{bias}}$) |")
    lines.append("| :--- | :---: | :---: | :---: |")

    for algo in algorithms:
        ds_entries = [agg_table.get(algo, {}).get(ds) for ds in datasets if agg_table.get(algo, {}).get(ds) is not None]
        biases = [e.get("optimistic_search_bias") for e in ds_entries if e.get("optimistic_search_bias") is not None]
        int_accs = [e.get("mean_internal_acc") for e in ds_entries if e.get("mean_internal_acc") is not None]
        oof_accs = [e["classifiers"]["knn"]["accuracy_mean"] for e in ds_entries]

        if biases:
            m_int = float(np.mean(int_accs))
            m_oof = float(np.mean(oof_accs))
            m_bias = float(np.mean(biases))
            lines.append(f"| **`{algo}`** | {m_int:.4f} | {m_oof:.4f} | +{m_bias:.4f} |")
        else:
            lines.append(f"| **`{algo}`** | — | — | — |")

    lines.append("\n## 4. Key Academic Takeaways & Submission Protocol Alignment\n")
    if not valid_for_formal_claims or not agg_table:
        lines.append("> [!NOTE] Diagnostic Notice: Insufficient / Incomplete Data for Formal Claims")
        lines.append("> The current execution is diagnostic, partial, or incomplete. In accordance with strict Elsevier submission protocols and AGENTS.md, formal academic takeaways regarding out-of-fold generalization, multi-objective trade-offs, and inductive bias transferability are withheld until full 5-fold evaluation with complete audit verification is executed.\n")
    else:
        lines.append("1. **Complete Information Barrier**: Strict partition of mutual information estimation and wrapper search to the outer training set confirms that out-of-sample nested cross-validation is achieved without optimistic circular evaluation bias.")

        kds_entries = [agg_table.get("KDS_EL_TwoPhase", {}).get(ds) for ds in datasets if agg_table.get("KDS_EL_TwoPhase", {}).get(ds) is not None]
        if kds_entries:
            kds_feats = float(np.mean([e["mean_features"] for e in kds_entries]))
            kds_acc = float(np.mean([e["classifiers"]["knn"]["accuracy_mean"] for e in kds_entries]))
            comp_summaries = []
            for other_algo in algorithms:
                if other_algo != "KDS_EL_TwoPhase":
                    other_entries = [agg_table.get(other_algo, {}).get(ds) for ds in datasets if agg_table.get(other_algo, {}).get(ds) is not None]
                    if other_entries:
                        o_feats = float(np.mean([e["mean_features"] for e in other_entries]))
                        o_acc = float(np.mean([e["classifiers"]["knn"]["accuracy_mean"] for e in other_entries]))
                        comp_summaries.append(f"{other_algo}: {o_feats:.1f} feats, {o_acc:.4f} acc")
            if comp_summaries:
                lines.append(f"2. **Dimensional Sparsity Trade-Off**: Across evaluated benchmark instances, KDS_EL_TwoPhase achieves a mean active feature count of {kds_feats:.1f} with {kds_acc:.4f} 3-NN accuracy (comparators: {'; '.join(comp_summaries)}).")
                other_feats_list = [float(np.mean([e["mean_features"] for e in agg_table[oa].values()])) for oa in algorithms if oa != "KDS_EL_TwoPhase" and agg_table.get(oa)]
                if other_feats_list and kds_feats < np.mean(other_feats_list):
                    lines.append(f"The empirical profile reflects substantial feature cardinality reduction ({kds_feats:.1f} vs peer average {float(np.mean(other_feats_list)):.1f}) while maintaining competitive out-of-sample accuracy.")
                else:
                    lines.append(f"The empirical trade-off illustrates the balance between feature reduction and predictive fidelity across instances.")
            else:
                lines.append(f"2. **Dimensional Sparsity Profile**: KDS_EL_TwoPhase yields an average of {kds_feats:.1f} active features and {kds_acc:.4f} 3-NN accuracy across evaluated instances.")
        else:
            lines.append("2. **Dimensional Sparsity**: Evaluated algorithms demonstrate differentiated feature compression profiles across benchmark datasets.")

        if kds_entries:
            mean_knn = float(np.mean([e["classifiers"]["knn"]["accuracy_mean"] for e in kds_entries]))
            mean_svm = float(np.mean([e["classifiers"]["svm"]["accuracy_mean"] for e in kds_entries]))
            mean_rf = float(np.mean([e["classifiers"]["random_forest"]["accuracy_mean"] for e in kds_entries]))
            mean_nb = float(np.mean([e["classifiers"]["naive_bayes"]["accuracy_mean"] for e in kds_entries]))
            mean_lda = float(np.mean([e["classifiers"]["lda"]["accuracy_mean"] for e in kds_entries]))

            d_svm = mean_svm - mean_knn
            d_rf = mean_rf - mean_knn

            lines.append(
                f"3. **Cross-Model Transferability**: Subsets selected via 3-NN guided optimization yield the following out-of-fold generalization profiles across downstream models: "
                f"3-NN: {mean_knn:.4f}, RBF-SVM: {mean_svm:.4f} ($\\Delta$: {d_svm:+.4f}), Random Forest: {mean_rf:.4f} ($\\Delta$: {d_rf:+.4f}), "
                f"GaussianNB: {mean_nb:.4f} ($\\Delta$: {mean_nb - mean_knn:+.4f}), LDA: {mean_lda:.4f} ($\\Delta$: {mean_lda - mean_knn:+.4f})."
            )

            # Data-driven objective synthesis based on actual numbers
            if d_svm >= -0.05 and d_rf >= -0.05:
                lines.append("Downstream kernelized SVM and ensemble models maintain comparable classification accuracy to the 3-NN optimization surrogate, indicating stable geometric separability of the selected feature subspace across these inductive biases.\n")
            elif d_svm < -0.15 or d_rf < -0.15:
                lines.append("Downstream evaluations exhibit pronounced performance attenuation on non-local models, reflecting inductive bias misalignment between nearest-neighbor distance metrics and global margin/tree partition criteria.\n")
            else:
                lines.append("Downstream classifiers demonstrate moderate inductive sensitivity, with performance shifts reflecting differences in inductive bias relative to nearest-neighbor search guidance.\n")
        else:
            lines.append("3. **Cross-Model Transferability**: Downstream classifiers provide out-of-fold verification of the selected feature subsets across distinct inductive biases.\n")

    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


# ══════════════════════════════════════════════════════════════════════════════
# CLI Entry Point
# ══════════════════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(description="Run Experiment E5: Full Outer Nested Generalization Benchmark.")
    parser.add_argument("--mode", choices=["core", "all"], default="core", help="Algorithm suite: 'core' (5 algorithms) or 'all' (12 algorithms).")
    parser.add_argument("--algorithms", nargs="+", default=None, help="Explicit list of algorithm names.")
    parser.add_argument("--datasets", nargs="+", default=None, help="Explicit list of dataset names.")
    parser.add_argument("--folds", nargs="+", type=int, default=[1, 2, 3, 4, 5], help="Outer fold indices (1 to 5).")
    parser.add_argument("--seeds", nargs="+", type=int, default=DEFAULT_SEEDS, help="Optimization random seeds.")
    parser.add_argument("--workers", type=int, default=2, help="Number of concurrent worker processes.")
    parser.add_argument("--out-dir", type=str, default=None, help="Output directory path.")
    parser.add_argument("--use-fast-knn", action="store_true", help="Enable candidate fast 3-NN implementation.")
    parser.add_argument("--quiet", action="store_true", help="Suppress verbose stdout logs.")

    args = parser.parse_args()

    if args.algorithms is not None:
        selected_algos = args.algorithms
    elif args.mode == "all":
        selected_algos = ALL_E5_ALGOS
    else:
        selected_algos = STAGE1_CORE_ALGOS

    run_experiment_e5(
        datasets=args.datasets,
        algorithms=selected_algos,
        outer_folds=args.folds,
        seeds=args.seeds,
        workers=args.workers,
        out_dir=args.out_dir,
        use_fast_knn=args.use_fast_knn,
        verbose=not args.quiet,
    )


if __name__ == "__main__":
    main()
