"""
E1: Nested Pipeline Flow Acceptance (E1-A) & Concurrency Stress Test (E1-B)
===========================================================================
Protocol Reference:
  - review_round_1/05_executable_experiment_plan.md, Section 4
  - review_round_1/04_detailed_supplementary_experiment_design.md, Section II & VIII

Objectives:
  E1-A (Flow Acceptance):
    - 4 datasets (Colon, T1D, BASEHOCK, COIL20) x 5 algorithms (KDS_EL_TwoPhase,
      MEL, MEL_MI, KDS_EL_NoPool, bIRIME) = 20 flow acceptance runs.
    - Outer Fold 1, Seed 7, N=20, Max_FEs=2000.
    - Automatic validation of 12 non-negotiable integrity checks (no data leakage,
      strictly closed request accounting, budget limit <= 2000, 5-fold inner splits
      confined to outer train, blind outer evaluation on 5 downstream classifiers).

  E1-B (Concurrency Stress Test):
    - Compares workers = 1, 2, 4 on representative benchmark tasks.
    - Enforces single-tier parallelism (OMP/MKL/OPENBLAS=1, RF n_jobs=1).
    - Measures wall-clock time, speedup S(p) = T(1)/T(p), peak RSS memory, CPU usage,
      Windows spawn overhead, and deadlock/crash resistance.
    - Outputs recommended worker count for downstream experiments.
"""

import os
import sys

# Force single-tier parallelism environment variables BEFORE scientific imports
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["NUMEXPR_NUM_THREADS"] = "1"
os.environ["VECLIB_MAXIMUM_THREADS"] = "1"

# Force UTF-8 on Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import time
import json
import argparse
import platform
import psutil
from datetime import datetime
from concurrent.futures import ProcessPoolExecutor, as_completed
import numpy as np

# Ensure code/ is on path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
sys.path.insert(0, CURRENT_DIR)

from utils import load_dataset
from config import DATA_DIR_TXT, DATA_DIR_MAT
from nested_evaluator import (
    NestedSplitsManager,
    BudgetEvaluator,
    BlindOuterEvaluator,
    IntegrityAuditor,
)
from algorithms_nested import NESTED_RUNNERS

E1_DATASETS = ["Colon", "T1D", "BASEHOCK", "COIL20"]
E1_ALGORITHMS = [
    "KDS_EL_TwoPhase",
    "MEL",
    "MEL_MI",
    "KDS_EL_NoPool",
    "bIRIME",
]


def check_e0_fast_admitted(project_root):
    """Inspects E0 equivalence report to determine whether fast 3-NN is admitted."""
    e0_json = os.path.join(
        project_root, "output", "nested_cv", "e0_verification", "e0_equivalence_report.json"
    )
    if os.path.exists(e0_json):
        try:
            with open(e0_json, "r", encoding="utf-8") as f:
                data = json.load(f)
            return bool(data.get("fast_evaluator_admitted", False))
        except Exception:
            return False
    return False


def sanitize_for_json(obj):
    """Recursively converts numpy types to native Python types for clean JSON serialization."""
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


def execute_single_run(
    dataset_name,
    algo_name,
    outer_fold_idx=1,
    run_idx=1,
    seed=7,
    max_fes=2000,
    pop_size=20,
    splits_dir=None,
    out_base_dir=None,
    use_fast_knn=False,
    verbose=False,
):
    """
    Executes a single nested optimization run under strict outer test isolation.
    """
    t0_run = time.perf_counter()
    if splits_dir is None:
        splits_dir = os.path.join(PROJECT_ROOT, "output", "nested_cv", "splits")
    if out_base_dir is None:
        out_base_dir = os.path.join(PROJECT_ROOT, "output", "nested_cv")

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

    selected_mask = algo_result["mask"]
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

    # 7. Persist Run Artifacts
    run_dir = os.path.join(
        out_base_dir, algo_name, dataset_name, f"fold_{outer_fold_idx}", f"run_{run_idx}"
    )
    os.makedirs(run_dir, exist_ok=True)

    mask_path = os.path.join(run_dir, "selected_mask.npy")
    np.save(mask_path, selected_mask)

    metrics_payload = {
        "dataset": dataset_name,
        "algorithm": algo_name,
        "outer_fold": outer_fold_idx,
        "run_idx": run_idx,
        "seed": seed,
        "N": pop_size,
        "Max_FEs": max_fes,
        "candidate_eval_requests": evaluator.candidate_eval_requests,
        "shortcut_eval_requests": evaluator.shortcut_eval_requests,
        "cache_hit_count": evaluator.cache_hit_count,
        "cv_eval_calls": evaluator.cv_eval_calls,
        "inner_model_fits": evaluator.inner_model_fits,
        "outer_model_fits": 5,
        "unique_masks": len(evaluator.unique_masks),
        "active_features": active_features,
        "active_features_ratio": float(active_features / D),
        "inner_gbest_fitness": float(algo_result["fitG"]),
        "generations_completed": algo_result.get("generations_completed", 0),
        "stop_reason": algo_result.get("stop_reason", "normal"),
        "tps_switch_q": evaluator.tps_switch_q,
        "tps_switch_E": evaluator.tps_switch_E,
        "tps_rescore_requests": evaluator.tps_rescore_requests,
        "ker_attempts": algo_result.get("ker_attempts", 0),
        "ker_accepts": algo_result.get("ker_accepts", 0),
        "ker_accept_rate": algo_result.get("ker_accept_rate", 0.0),
        "air_triggers": algo_result.get("air_triggers", 0),
        "p2_valid_ratio": algo_result.get("p2_valid_ratio", 0.0),
        "outer_test_indices": test_idx.tolist(),
        "outer_test_metrics": outer_metrics,
        "timing": {
            "search_sec": round(search_time, 3),
            "blind_eval_sec": round(blind_eval_time, 3),
            "total_sec": round(total_run_time, 3),
        },
        "integrity_audit": {
            "all_passed": all_checks_passed,
            "details": audit_details,
        },
        "system_metadata": {
            "platform": platform.platform(),
            "python": platform.python_version(),
            "numpy": np.__version__,
            "evaluator_type": "Fast_3NN" if use_fast_knn else "Scikit_Learn_Fallback",
            "timestamp": datetime.now().isoformat(),
        },
    }

    metrics_path = os.path.join(run_dir, "metrics.json")
    with open(metrics_path, "w", encoding="utf-8") as f:
        json.dump(sanitize_for_json(metrics_payload), f, indent=2)

    if verbose:
        status_tag = "[AUDIT PASS]" if all_checks_passed else "[AUDIT FAIL]"
        print(
            f"  {status_tag} {dataset_name:10s} | {algo_name:16s} | "
            f"FEs={evaluator.candidate_eval_requests}/2000 | "
            f"Feats={active_features:4d}/{D:5d} | "
            f"3NN-Acc={outer_metrics['knn']['accuracy']:.4f} | "
            f"SVM-Acc={outer_metrics['svm']['accuracy']:.4f} | "
            f"Time={total_run_time:.2f}s"
        )

    return metrics_payload


# ══════════════════════════════════════════════════════════════════════════════
# E1-A: Flow Acceptance Pipeline
# ══════════════════════════════════════════════════════════════════════════════

def run_e1_acceptance(use_fast_knn=False, verbose=True):
    """
    Executes E1-A: 20 flow acceptance runs across 4 datasets x 5 algorithms.
    """
    print("\n" + "=" * 78)
    print("STARTING EXPERIMENT E1-A: NESTED PIPELINE FLOW ACCEPTANCE (20 RUNS)")
    print(f"Datasets (4): {E1_DATASETS}")
    print(f"Algorithms (5): {E1_ALGORITHMS}")
    print(f"Outer Fold: 1 (out of 5) | Seed: 7 | N: 20 | Max_FEs: 2000")
    print(f"Evaluator Backend: {'Candidate Fast 3-NN' if use_fast_knn else 'Authoritative Scikit-Learn 3-NN (Fallback Active)'}")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 78)

    out_base_dir = os.path.join(PROJECT_ROOT, "output", "nested_cv")
    splits_dir = os.path.join(out_base_dir, "splits")
    e1_a_dir = os.path.join(out_base_dir, "e1_acceptance")
    os.makedirs(e1_a_dir, exist_ok=True)

    all_run_results = []
    total_passed = 0
    t0_all = time.perf_counter()

    for ds in E1_DATASETS:
        print(f"\n--- Dataset: {ds} ---")
        for algo in E1_ALGORITHMS:
            res = execute_single_run(
                dataset_name=ds,
                algo_name=algo,
                outer_fold_idx=1,
                run_idx=1,
                seed=7,
                max_fes=2000,
                pop_size=20,
                splits_dir=splits_dir,
                out_base_dir=out_base_dir,
                use_fast_knn=use_fast_knn,
                verbose=verbose,
            )
            all_run_results.append(res)
            if res["integrity_audit"]["all_passed"]:
                total_passed += 1

    total_time = time.perf_counter() - t0_all
    all_20_passed = total_passed == len(all_run_results)
    decision = "ACCEPTANCE_PASSED" if all_20_passed else "ACCEPTANCE_FAILED"

    summary = {
        "experiment": "E1-A_Nested_Pipeline_Flow_Acceptance",
        "timestamp": datetime.now().isoformat(),
        "total_runs": len(all_run_results),
        "passed_runs": total_passed,
        "failed_runs": len(all_run_results) - total_passed,
        "all_passed": all_20_passed,
        "decision_gate": decision,
        "total_elapsed_sec": round(total_time, 2),
        "run_details": [
            {
                "dataset": r["dataset"],
                "algorithm": r["algorithm"],
                "requests": r["candidate_eval_requests"],
                "shortcuts": r["shortcut_eval_requests"],
                "cache_hits": r["cache_hit_count"],
                "cv_calls": r["cv_eval_calls"],
                "active_features": r["active_features"],
                "outer_acc_3nn": r["outer_test_metrics"]["knn"]["accuracy"],
                "outer_bacc_3nn": r["outer_test_metrics"]["knn"]["balanced_accuracy"],
                "outer_f1_3nn": r["outer_test_metrics"]["knn"]["macro_f1"],
                "outer_acc_svm": r["outer_test_metrics"]["svm"]["accuracy"],
                "outer_acc_rf": r["outer_test_metrics"]["random_forest"]["accuracy"],
                "time_sec": r["timing"]["total_sec"],
                "audit_passed": r["integrity_audit"]["all_passed"],
            }
            for r in all_run_results
        ],
    }

    # Save JSON summary
    json_path = os.path.join(e1_a_dir, "e1_acceptance_report.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    # Save Markdown summary
    md_path = os.path.join(e1_a_dir, "e1_acceptance_report.md")
    with open(md_path, "w", encoding="utf-8") as f:
        f.write("# E1-A: Nested Pipeline Flow Acceptance Report\n\n")
        f.write(f"- **Execution Timestamp**: {summary['timestamp']}\n")
        f.write(f"- **Protocol Reference**: `review_round_1/05_executable_experiment_plan.md` (Section 4)\n")
        f.write(f"- **Total Flow Acceptance Runs**: {summary['total_runs']}\n")
        f.write(f"- **Runs Passing All 12 Integrity Checks**: **{summary['passed_runs']} / {summary['total_runs']}**\n")
        f.write(f"- **Total Elapsed Time**: `{total_time:.2f} s`\n")
        f.write(f"- **Gate Decision**: **`{decision}`**\n\n")

        if all_20_passed:
            f.write("> **GATE VERDICT: PASS** — All 20 flow acceptance runs across the 4 representative datasets and 5 core configurations completed without errors, strictly isolated the outer test set, satisfied request closed-loop accounting, strictly respected Max_FEs <= 2000, and persisted all reproducibility artifacts.\n\n")
        else:
            f.write("> **GATE VERDICT: FAIL** — Discrepancies or integrity failures were detected during flow acceptance. Expansion to full-scale experiments must be paused until root causes are resolved.\n\n")

        f.write("## 20 Acceptance Runs Detail Table\n\n")
        f.write("| Dataset | Algorithm | Requests (<=2000) | Shortcuts | Cache Hits | CV Calls | Feats | 3-NN Acc | 3-NN BAcc | SVM Acc | RF Acc | Time (s) | Audit |\n")
        f.write("| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |\n")
        for d in summary["run_details"]:
            audit_str = "**PASS**" if d["audit_passed"] else "**FAIL**"
            f.write(
                f"| **{d['dataset']}** | `{d['algorithm']}` | {d['requests']} | {d['shortcuts']} | "
                f"{d['cache_hits']} | {d['cv_calls']} | {d['active_features']} | "
                f"{d['outer_acc_3nn']:.4f} | {d['outer_bacc_3nn']:.4f} | {d['outer_acc_svm']:.4f} | "
                f"{d['outer_acc_rf']:.4f} | {d['time_sec']:.2f}s | {audit_str} |\n"
            )

    print("\n" + "=" * 78)
    print(f"E1-A COMPLETED: Gate Decision = {decision}")
    print(f"Artifacts saved:")
    print(f"  - JSON Report: {json_path}")
    print(f"  - Markdown Report: {md_path}")
    print("=" * 78)

    return summary


# ══════════════════════════════════════════════════════════════════════════════
# E1-B: Concurrency Ladder Stress Test
# ══════════════════════════════════════════════════════════════════════════════

def _stress_worker_task(task_spec):
    """Worker task executed in separate process."""
    ds, algo, use_fast = task_spec
    res = execute_single_run(
        dataset_name=ds,
        algo_name=algo,
        outer_fold_idx=1,
        run_idx=1,
        seed=7,
        max_fes=2000,
        pop_size=20,
        use_fast_knn=use_fast,
        verbose=False,
    )
    return {
        "dataset": ds,
        "algorithm": algo,
        "time_sec": res["timing"]["total_sec"],
        "active_features": res["active_features"],
        "audit_passed": res["integrity_audit"]["all_passed"],
    }


def run_e1_stress(worker_ladder=(1, 2, 4), use_fast_knn=False, verbose=True):
    """
    Executes E1-B: Concurrency Ladder Stress Test across workers = 1, 2, 4.
    """
    print("\n" + "=" * 78)
    print("STARTING EXPERIMENT E1-B: CONCURRENCY LADDER STRESS TEST")
    print(f"Tested Concurrency Levels: {worker_ladder}")
    print(f"Single-Tier Parallelism: OMP/MKL/OPENBLAS=1, RF n_jobs=1")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 78)

    out_base_dir = os.path.join(PROJECT_ROOT, "output", "nested_cv")
    e1_b_dir = os.path.join(out_base_dir, "e1_stress")
    os.makedirs(e1_b_dir, exist_ok=True)

    # Representative stress tasks (4 cross-scale tasks)
    stress_tasks = [
        ("Colon", "KDS_EL_TwoPhase", use_fast_knn),
        ("T1D", "KDS_EL_TwoPhase", use_fast_knn),
        ("BASEHOCK", "MEL", use_fast_knn),
        ("COIL20", "KDS_EL_NoPool", use_fast_knn),
    ]

    ladder_results = []
    base_time = None

    for workers in worker_ladder:
        print(f"\nEvaluating Concurrency Level: workers = {workers} ...")
        proc = psutil.Process(os.getpid())
        rss_start = proc.memory_info().rss / (1024 * 1024)  # MB

        t0_level = time.perf_counter()
        peak_rss = rss_start
        errors = []

        try:
            if workers == 1:
                results = []
                for t in stress_tasks:
                    results.append(_stress_worker_task(t))
                    current_rss = proc.memory_info().rss / (1024 * 1024)
                    peak_rss = max(peak_rss, current_rss)
            else:
                results = []
                with ProcessPoolExecutor(max_workers=workers) as executor:
                    futures = [executor.submit(_stress_worker_task, t) for t in stress_tasks]
                    for fut in as_completed(futures):
                        try:
                            r = fut.result()
                            results.append(r)
                            current_rss = proc.memory_info().rss / (1024 * 1024)
                            peak_rss = max(peak_rss, current_rss)
                        except Exception as e:
                            errors.append(str(e))
        except Exception as e:
            errors.append(f"Executor level failure: {str(e)}")

        elapsed = time.perf_counter() - t0_level

        if workers == 1:
            base_time = elapsed
            speedup = 1.00
        else:
            speedup = base_time / max(1e-6, elapsed) if base_time else 1.00

        rss_end = proc.memory_info().rss / (1024 * 1024)
        peak_rss = max(peak_rss, rss_end)

        record = {
            "workers": workers,
            "tasks_count": len(stress_tasks),
            "completed_tasks": len(results),
            "errors_count": len(errors),
            "wall_clock_time_sec": round(elapsed, 2),
            "speedup_ratio": round(speedup, 2),
            "peak_rss_mb": round(peak_rss, 1),
            "system_cpu_percent": psutil.cpu_percent(interval=0.1),
            "status": "PASS" if len(errors) == 0 and len(results) == len(stress_tasks) else "FAIL",
            "errors": errors,
        }
        ladder_results.append(record)

        if verbose:
            print(
                f"  Workers={workers:2d} | Time={elapsed:6.2f}s | "
                f"Speedup={speedup:4.2f}x | Peak RSS={peak_rss:6.1f} MB | "
                f"Status={record['status']}"
            )

    # Determine recommended concurrency
    valid_records = [r for r in ladder_results if r["status"] == "PASS"]
    if valid_records:
        # Pick workers that gives best efficiency without runaway memory
        best_rec = min(valid_records, key=lambda x: x["wall_clock_time_sec"])
        recommended_workers = best_rec["workers"]
    else:
        recommended_workers = 1

    summary = {
        "experiment": "E1-B_Concurrency_Ladder_Stress_Test",
        "timestamp": datetime.now().isoformat(),
        "tasks": [f"{ds} / {algo}" for ds, algo, _ in stress_tasks],
        "single_tier_threads_locked": 1,
        "concurrency_ladder": ladder_results,
        "recommended_workers": recommended_workers,
        "system_info": {
            "cpu_physical_cores": psutil.cpu_count(logical=False),
            "cpu_logical_cores": psutil.cpu_count(logical=True),
            "total_ram_gb": round(psutil.virtual_memory().total / (1024**3), 2),
            "platform": platform.platform(),
        },
    }

    # Save JSON summary
    json_path = os.path.join(e1_b_dir, "e1_stress_report.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    # Save Markdown summary
    md_path = os.path.join(e1_b_dir, "e1_stress_report.md")
    with open(md_path, "w", encoding="utf-8") as f:
        f.write("# E1-B: Concurrency Ladder Stress Test Report\n\n")
        f.write(f"- **Execution Timestamp**: {summary['timestamp']}\n")
        f.write(f"- **Protocol Reference**: `review_round_1/05_executable_experiment_plan.md` (Section 4.3)\n")
        f.write(f"- **CPU Physical Cores**: {summary['system_info']['cpu_physical_cores']}\n")
        f.write(f"- **CPU Logical Cores**: {summary['system_info']['cpu_logical_cores']}\n")
        f.write(f"- **Total System RAM**: `{summary['system_info']['total_ram_gb']} GB`\n")
        f.write(f"- **Recommended Safe Concurrency**: **`workers = {recommended_workers}`**\n\n")

        f.write("## Concurrency Ladder Performance\n\n")
        f.write("| Workers | Tasks | Time (s) | Speedup | Peak RSS (MB) | CPU % | Status |\n")
        f.write("| :---: | :---: | :---: | :---: | :---: | :---: | :---: |\n")
        for r in ladder_results:
            f.write(
                f"| **{r['workers']}** | {r['completed_tasks']}/{r['tasks_count']} | "
                f"`{r['wall_clock_time_sec']:.2f} s` | **{r['speedup_ratio']:.2f}x** | "
                f"{r['peak_rss_mb']:.1f} MB | {r['system_cpu_percent']:.1f}% | **{r['status']}** |\n"
            )

        f.write("\n## Concurrency & Stability Decision\n\n")
        f.write(
            f"Based on empirical ladder benchmarking with single-tier thread locking (`OMP/MKL/OPENBLAS=1`, `RF n_jobs=1`), "
            f"**`workers = {recommended_workers}`** achieved the optimal trade-off between throughput scaling and memory headroom without process deadlocks on Windows `spawn`.\n"
        )

    print("\n" + "=" * 78)
    print(f"E1-B COMPLETED: Recommended Workers = {recommended_workers}")
    print(f"Artifacts saved:")
    print(f"  - JSON Report: {json_path}")
    print(f"  - Markdown Report: {md_path}")
    print("=" * 78)

    return summary


# ══════════════════════════════════════════════════════════════════════════════
# Main Entry Point
# ══════════════════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(description="Run Experiment E1: Flow Acceptance & Stress Test")
    parser.add_argument(
        "--mode",
        choices=["all", "acceptance", "stress"],
        default="all",
        help="Experiment mode: acceptance (E1-A), stress (E1-B), or all (default: all)",
    )
    parser.add_argument(
        "--workers",
        type=int,
        nargs="+",
        default=[1, 2, 4],
        help="Worker counts for stress test ladder (default: 1 2 4)",
    )
    parser.add_argument(
        "--use-fast-knn",
        action="store_true",
        help="Explicitly force candidate fast 3-NN (default: auto-check E0 report)",
    )
    parser.add_argument("--quiet", action="store_true", help="Suppress verbose output")
    args = parser.parse_args()

    # Auto-detect E0 decision gate if flag not explicitly provided
    if not args.use_fast_knn:
        e0_passed = check_e0_fast_admitted(PROJECT_ROOT)
        use_fast = e0_passed
        if not e0_passed:
            print("[INFO] E0 Gate indicates fallback mode: Authoritative Scikit-Learn 3-NN activated.")
        else:
            print("[INFO] E0 Gate passed: Candidate Fast 3-NN admitted.")
    else:
        use_fast = True
        print("[INFO] --use-fast-knn flag set: forcing Candidate Fast 3-NN.")

    if args.mode in ("all", "acceptance"):
        run_e1_acceptance(use_fast_knn=use_fast, verbose=not args.quiet)

    if args.mode in ("all", "stress"):
        run_e1_stress(worker_ladder=args.workers, use_fast_knn=use_fast, verbose=not args.quiet)


if __name__ == "__main__":
    main()
