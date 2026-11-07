"""
Experiment E3: Classical Filter Fold-Internal Benchmark & Pareto Front Analysis
=================================================================================
Protocol Reference:
  - review_round_1/05_executable_experiment_plan.md (Section 6)
  - review_round_1/04_detailed_supplementary_experiment_design.md (Section 6 / Suite 2)

Objective:
  - Benchmark classical feature filtering algorithms under strict fold-internal
    zero-leakage cross-validation conditions across varying feature cardinality budgets.
  - Establish a solid empirical reference baseline for univariate and multivariate filters
    (Top-k MI, Two-Stage Fast mRMR, ReliefF, and LASSO L1-OvR) to inform feature selection trade-offs.

Four Filter Methods:
  1. Top-k MI: Univariate mutual information ranking with class labels.
  2. Two-Stage Fast mRMR: Pre-screening top 1,000 features by MI, followed by
     greedy redundancy minimization using absolute Pearson correlation.
  3. ReliefF: Deterministic multi-class formulation traversing all N_train samples
     using standardized Manhattan distance (Kononenko 1994).
  4. LASSO (L1-OvR + Two-Tier MI Completion): L1-regularized Logistic Regression (C=0.1,
     class_weight='balanced', standardized on training fold only) wrapped in
     OneVsRestClassifier. Non-zero coefficients are ranked strictly ahead of zero-coefficient
     features by descending absolute weight across classes. If non-zero features < k,
     remaining slots are completed via training-fold univariate MI. Fitting errors raise
     an exception without silent fallback.

Strict Zero-Leakage & Integrity Protocols:
  - Outer splits pre-generated and verified for disjointness and complete coverage in the main process.
  - All feature ranking and fitting occur STRICTLY on the outer training fold.
  - Downstream 3-NN evaluated on the held-out outer test fold.
  - Concatenated into Pooled Out-Of-Fold (OOF) predictions over the 5 folds.
  - Single-tier parallelism strictly enforced across all worker processes.
"""

import os
import sys

# Force single-tier parallelism environment variables BEFORE scientific imports
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["NUMEXPR_NUM_THREADS"] = "1"
os.environ["VECLIB_MAXIMUM_THREADS"] = "1"

# Windows console encoding
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import json
import time
import argparse
import platform
import warnings
import traceback
import numpy as np
from datetime import datetime
from concurrent.futures import ProcessPoolExecutor, as_completed

try:
    import threadpoolctl
    threadpoolctl.threadpool_limits(limits=1)
    HAS_THREADPOOLCTL = True
except Exception:
    HAS_THREADPOOLCTL = False

from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.multiclass import OneVsRestClassifier
from sklearn.feature_selection import mutual_info_classif
from sklearn.neighbors import KNeighborsClassifier
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
from nested_evaluator import NestedSplitsManager


# ══════════════════════════════════════════════════════════════════════════════
# Constants & Default Configurations
# ══════════════════════════════════════════════════════════════════════════════

FILTER_METHODS = ["Top-k MI", "Two-Stage mRMR", "ReliefF", "LASSO"]
DEFAULT_PRIMARY_K_GRID = [20, 50, 100]
DEFAULT_PARETO_K_GRID = [10, 20, 50, 100, 200]
PARETO_DATASETS = ["Colon", "T1D", "BASEHOCK", "COIL20"]
DEFAULT_SPLITS_DIR = os.path.join(PROJECT_ROOT, "output", "nested_cv", "splits")
DEFAULT_OUT_DIR = os.path.join(PROJECT_ROOT, "output", "nested_cv", "e3_filters")


def _init_worker():
    """Worker process initializer to strictly enforce single-tier parallelism."""
    os.environ["OMP_NUM_THREADS"] = "1"
    os.environ["MKL_NUM_THREADS"] = "1"
    os.environ["OPENBLAS_NUM_THREADS"] = "1"
    os.environ["NUMEXPR_NUM_THREADS"] = "1"
    os.environ["VECLIB_MAXIMUM_THREADS"] = "1"
    try:
        import threadpoolctl
        threadpoolctl.threadpool_limits(limits=1)
    except Exception:
        pass


# ══════════════════════════════════════════════════════════════════════════════
# Metric Helper
# ══════════════════════════════════════════════════════════════════════════════

def compute_multiclass_metrics(y_true, y_pred):
    """Computes pure Accuracy, Balanced Accuracy, and Macro-F1."""
    y_true = np.asarray(y_true)
    y_pred = np.asarray(y_pred)
    if len(y_true) == 0 or len(y_pred) == 0:
        return {"accuracy": 0.0, "balanced_accuracy": 0.0, "macro_f1": 0.0}

    acc = float(accuracy_score(y_true, y_pred))
    try:
        bacc = float(balanced_accuracy_score(y_true, y_pred))
    except Exception:
        bacc = acc
    try:
        f1 = float(f1_score(y_true, y_pred, average="macro", zero_division=0))
    except Exception:
        f1 = 0.0

    return {
        "accuracy": round(acc, 6),
        "balanced_accuracy": round(bacc, 6),
        "macro_f1": round(f1, 6),
    }


# ══════════════════════════════════════════════════════════════════════════════
# Filter Algorithm Implementations (Strictly Fold-Internal)
# ══════════════════════════════════════════════════════════════════════════════

def select_topk_mi(X_tr, y_tr, k):
    """
    Filter 1: Top-k Mutual Information.
    Evaluated with n_neighbors=3, random_state=42.
    """
    D = X_tr.shape[1]
    k_actual = min(k, D)
    if k_actual == 0:
        return []

    scores = mutual_info_classif(X_tr, y_tr, n_neighbors=3, random_state=42)
    scores = np.nan_to_num(scores, nan=0.0)
    order = np.argsort(-scores, kind="mergesort")
    return order[:k_actual].tolist()


def select_twostage_mrmr(X_tr, y_tr, k, pool_size=1000):
    """
    Filter 2: Two-Stage Fast mRMR (Peng et al.).
      - Stage 1: Univariate MI pre-screening to pool_size (default 1000)
      - Stage 2: Fast incremental greedy selection maximizing:
        Score(j) = MI(j) - (1 / |S|) * sum_{s in S} |Pearson_corr(X_j, X_s)|
    """
    N_tr, D = X_tr.shape
    k_actual = min(k, D)
    if k_actual == 0:
        return []

    # Stage 1: Univariate MI pre-screening
    mi_scores = mutual_info_classif(X_tr, y_tr, n_neighbors=3, random_state=42)
    mi_scores = np.nan_to_num(mi_scores, nan=0.0)
    M = min(pool_size, D)
    pool_indices = np.argsort(-mi_scores, kind="mergesort")[:M]

    if k_actual >= M:
        return pool_indices[:k_actual].tolist()

    X_pool = X_tr[:, pool_indices]
    pool_mi = mi_scores[pool_indices]

    # Column-normalize for vectorized Pearson correlation
    X_centered = X_pool - np.mean(X_pool, axis=0, keepdims=True)
    norms = np.linalg.norm(X_centered, axis=0, keepdims=True)
    norms[norms < 1e-12] = 1.0
    X_norm = X_centered / norms

    # Stage 2: Incremental greedy selection
    selected_in_pool = [int(np.argmax(pool_mi))]
    corr_sum = np.zeros(M, dtype=float)

    # Initial vector correlation
    last_v = X_norm[:, selected_in_pool[0]]
    corr_sum += np.abs(np.dot(X_norm.T, last_v))

    for m in range(1, k_actual):
        redundancy = corr_sum / m
        scores = pool_mi - redundancy
        scores[selected_in_pool] = -np.inf
        best_cand = int(np.argmax(scores))
        selected_in_pool.append(best_cand)

        new_v = X_norm[:, best_cand]
        corr_sum += np.abs(np.dot(X_norm.T, new_v))

    return pool_indices[selected_in_pool].tolist()


def select_relieff(X_tr, y_tr, k, k_relief=5):
    """
    Filter 3: Deterministic Multi-Class ReliefF (Kononenko 1994).
      - Traverses all N_tr instances (zero sampling variance, 100% deterministic).
      - Standardized Manhattan distance normalized by feature range.
      - Exact multi-class miss probability weighting.
    """
    N_tr, D = X_tr.shape
    k_actual = min(k, D)
    if k_actual == 0:
        return []

    mins = np.min(X_tr, axis=0)
    maxs = np.max(X_tr, axis=0)
    ranges = maxs - mins
    ranges[ranges < 1e-12] = 1.0

    classes = np.unique(y_tr)
    class_priors = {c: float(np.sum(y_tr == c) / N_tr) for c in classes}
    class_indices = {c: np.where(y_tr == c)[0] for c in classes}

    W = np.zeros(D, dtype=float)

    for i in range(N_tr):
        xi = X_tr[i]
        yi = y_tr[i]

        diff = np.abs(X_tr - xi) / ranges
        dist = np.sum(diff, axis=1)
        dist[i] = np.inf

        # 1. Nearest hits in same class
        same_cls = class_indices[yi]
        same_candidates = same_cls[same_cls != i]
        if len(same_candidates) > 0:
            k_hit = min(k_relief, len(same_candidates))
            hits = same_candidates[np.argpartition(dist[same_candidates], k_hit - 1)[:k_hit]]
            diff_hits = np.sum(diff[hits], axis=0) / (N_tr * len(hits))
            W -= diff_hits

        # 2. Nearest misses in each other class
        denom = 1.0 - class_priors[yi]
        if denom > 1e-12:
            for c in classes:
                if c == yi:
                    continue
                diff_cls = class_indices[c]
                if len(diff_cls) == 0:
                    continue
                k_miss = min(k_relief, len(diff_cls))
                misses = diff_cls[np.argpartition(dist[diff_cls], k_miss - 1)[:k_miss]]
                diff_misses = np.sum(diff[misses], axis=0) / (N_tr * len(misses))
                W += (class_priors[c] / denom) * diff_misses

    order = np.argsort(-W, kind="mergesort")
    return order[:k_actual].tolist()


def select_lasso(X_tr, y_tr, k, C=0.1, max_iter=2000, seed=42):
    """
    Filter 4: LASSO (L1-Penalized Logistic Regression via OneVsRestClassifier).
      - StandardScaler fitted on training fold only.
      - Base estimator: LogisticRegression(penalty='l1', solver='liblinear', C=C,
        max_iter=max_iter, tol=1e-4, class_weight='balanced', random_state=seed).
      - Explicitly wrapped in OneVsRestClassifier to support both binary and multi-class schemes.
      - Feature importance score = sum of absolute coefficients across all class estimators:
        Score_j = sum_{c} |beta_{c, j}|.
      - Two-Tier Deterministic Hybrid Selection:
        1. Features with non-zero coefficients (Score_j > 1e-12) are sorted descending
           strictly by Score_j.
        2. If non-zero features < k, remaining slots are completed by taking zero-coefficient
           features sorted descending by training-fold univariate Mutual Information (MI).
        3. Final ranking is the exact concatenation of sorted non-zero features followed
           by sorted zero-coefficient features. Non-zero features maintain absolute lexical priority.
      - Strict Error Policy: Fitting failures raise a RuntimeError immediately,
        preventing silent fallback to pure MI.
    """
    N_tr, D = X_tr.shape
    k_actual = min(k, D)
    if k_actual == 0:
        return []

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X_tr)

    try:
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", category=FutureWarning)
            warnings.filterwarnings("ignore", category=UserWarning)
            base_clf = LogisticRegression(
                penalty="l1",
                solver="liblinear",
                C=C,
                max_iter=max_iter,
                tol=1e-4,
                class_weight="balanced",
                random_state=seed,
            )
            clf = OneVsRestClassifier(base_clf)
            clf.fit(X_scaled, y_tr)
    except Exception as e:
        raise RuntimeError(f"LASSO OneVsRestClassifier fitting failed on fold: {str(e)}") from e

    coef_matrix = np.vstack([est.coef_ for est in clf.estimators_])
    scores = np.sum(np.abs(coef_matrix), axis=0)

    # Separate non-zero features and zero-coefficient features
    nonzero_indices = np.where(scores > 1e-12)[0]
    zero_indices = np.where(scores <= 1e-12)[0]

    # Tier 1: Rank non-zero features strictly by descending coefficient magnitude
    if len(nonzero_indices) > 0:
        order_nonzero = nonzero_indices[np.argsort(-scores[nonzero_indices], kind="mergesort")]
    else:
        order_nonzero = np.array([], dtype=int)

    if len(order_nonzero) >= k_actual:
        return order_nonzero[:k_actual].tolist()

    # Tier 2: Complete remaining slots using zero-coefficient features ranked by MI
    needed = k_actual - len(order_nonzero)
    mi_scores = mutual_info_classif(X_tr, y_tr, n_neighbors=3, random_state=42)
    mi_scores = np.nan_to_num(mi_scores, nan=0.0)

    order_zero = zero_indices[np.argsort(-mi_scores[zero_indices], kind="mergesort")]
    ranked = np.concatenate([order_nonzero, order_zero[:needed]])
    return ranked.tolist()


FILTER_DISPATCHER = {
    "Top-k MI": select_topk_mi,
    "Two-Stage mRMR": select_twostage_mrmr,
    "ReliefF": select_relieff,
    "LASSO": select_lasso,
}


# ══════════════════════════════════════════════════════════════════════════════
# Unified Filter Evaluation across k-Grid on 5 Outer Folds
# ══════════════════════════════════════════════════════════════════════════════

def evaluate_filter_on_dataset_grid(dataset_name, filter_name, k_list, splits_dir=None, verbose=False):
    """
    Evaluates a filter method across multiple target k values on a dataset.
    Features are ranked ONCE per outer training fold up to max(k), and downstream
    3-NN models are fitted for each k in k_list.

    Timings are strictly decoupled:
      - fold_ranking_sec: Time spent ranking features up to max(k) on outer training fold.
      - fold_eval_sec: Time spent fitting 3-NN and predicting test fold for a specific k.
      - shared_ranking_sec: Cumulative 5-fold feature ranking time.
      - k_eval_sec: Cumulative 5-fold 3-NN prediction time for that specific k.
      - k_standalone_pipeline_sec: Estimated standalone pipeline time (ranking + eval for that k).
      - grid_task_wall_sec: Total wall-clock time for the multi-k grid task.
    """
    t0_task = time.perf_counter()
    if splits_dir is None:
        splits_dir = DEFAULT_SPLITS_DIR

    X, y = load_dataset(dataset_name, DATA_DIR_TXT, DATA_DIR_MAT)
    N_samples, D = X.shape

    splits_mgr = NestedSplitsManager(splits_dir)
    # Ensure splits validity before evaluation
    is_valid, v_msg = splits_mgr.verify_5fold_pooled_oof(dataset_name, y)
    if not is_valid:
        raise RuntimeError(f"OOF partition integrity failure for dataset '{dataset_name}': {v_msg}")

    outer_splits = splits_mgr.get_outer_splits(dataset_name, y, n_splits=5, seed=42)

    filter_fn = FILTER_DISPATCHER[filter_name]
    k_sorted = sorted(list(set(k_list)))
    k_max = min(max(k_sorted), D)

    # Dictionary mapping each k to its pooled predictions array and fold records
    y_preds_pooled = {k: np.zeros(N_samples, dtype=int) for k in k_sorted}
    fold_records_by_k = {k: [] for k in k_sorted}

    for fold_idx, (train_idx, test_idx) in enumerate(outer_splits, start=1):
        X_tr, y_tr = X[train_idx], y[train_idx]
        X_te, y_te = X[test_idx], y[test_idx]

        # 1. Feature ranking fitted strictly on training fold only up to k_max
        t0_sel = time.perf_counter()
        ranked_features = filter_fn(X_tr, y_tr, k=k_max)
        t_sel = time.perf_counter() - t0_sel

        # 2. Downstream 3-NN evaluated for each target k
        for k in k_sorted:
            k_act = min(k, len(ranked_features))
            selected_k = ranked_features[:k_act]

            t0_eval = time.perf_counter()
            if len(selected_k) == 0:
                preds_te = np.full(len(test_idx), int(np.bincount(y_tr).argmax()))
            else:
                clf = KNeighborsClassifier(n_neighbors=min(3, len(train_idx)))
                clf.fit(X_tr[:, selected_k], y_tr)
                preds_te = clf.predict(X_te[:, selected_k])
            t_eval = time.perf_counter() - t0_eval

            y_preds_pooled[k][test_idx] = preds_te
            fold_met = compute_multiclass_metrics(y_te, preds_te)
            fold_records_by_k[k].append({
                "fold": fold_idx,
                "selected_features_count": len(selected_k),
                "ranking_sec": round(t_sel, 4),
                "eval_sec": round(t_eval, 4),
                "fold_pipeline_sec": round(t_sel + t_eval, 4),
                **fold_met,
            })

    total_task_sec = time.perf_counter() - t0_task
    results_per_k = []

    cumulative_ranking_sec = sum(rec["ranking_sec"] for rec in fold_records_by_k[k_sorted[0]])

    for k in k_sorted:
        pm = compute_multiclass_metrics(y, y_preds_pooled[k])
        cumulative_eval_sec = sum(rec["eval_sec"] for rec in fold_records_by_k[k])
        standalone_pipeline_sec = cumulative_ranking_sec + cumulative_eval_sec

        res_record = {
            "dataset": dataset_name,
            "filter": filter_name,
            "k": k,
            "pooled_metrics": pm,
            "fold_records": fold_records_by_k[k],
            "timing": {
                "shared_ranking_sec": round(cumulative_ranking_sec, 4),
                "k_eval_sec": round(cumulative_eval_sec, 4),
                "k_standalone_pipeline_sec": round(standalone_pipeline_sec, 4),
                "grid_task_wall_sec": round(total_task_sec, 4),
                "timing_semantics": "shared_ranking_sec is cumulative 5-fold feature ranking up to k_max; k_eval_sec is cumulative 5-fold 3-NN fit/prediction for this k; k_standalone_pipeline_sec = ranking + eval; grid_task_wall_sec is total multi-k task wall clock.",
            },
        }
        results_per_k.append(res_record)

        if verbose:
            print(
                f"  {dataset_name:12s} | {filter_name:15s} | k={k:3d} | "
                f"Pooled Acc={pm['accuracy']:.4f} | "
                f"BAcc={pm['balanced_accuracy']:.4f} | "
                f"Macro-F1={pm['macro_f1']:.4f} | "
                f"Rank={cumulative_ranking_sec:.2f}s | "
                f"Eval={cumulative_eval_sec:.2f}s",
                flush=True,
            )

    return results_per_k


# ══════════════════════════════════════════════════════════════════════════════
# Main Experiment E3 Pipeline
# ══════════════════════════════════════════════════════════════════════════════

def run_experiment_e3(
    datasets=None,
    filters=None,
    primary_k_grid=None,
    pareto_k_grid=None,
    pareto_datasets=None,
    workers=2,
    splits_dir=None,
    out_dir=None,
    kdsel_results_path=None,
    verbose=True,
):
    """
    Executes Experiment E3: Comprehensive Filter Benchmarking & Pareto Front Analysis.
    Includes strict integrity gating, transparent timing accounting, dynamic filter support,
    and factual empirical observations without unverified pre-written claims.
    """
    t0_all = time.perf_counter()
    if datasets is None:
        datasets = BENCHMARK_19_DATASETS
    if filters is None:
        filters = FILTER_METHODS
    else:
        invalid = [f for f in filters if f not in FILTER_DISPATCHER]
        if invalid:
            raise ValueError(f"Unknown filter method(s): {invalid}. Supported methods: {list(FILTER_DISPATCHER.keys())}")

    if primary_k_grid is None:
        primary_k_grid = DEFAULT_PRIMARY_K_GRID
    if pareto_k_grid is None:
        pareto_k_grid = DEFAULT_PARETO_K_GRID
    if pareto_datasets is None:
        pareto_datasets = PARETO_DATASETS
    if splits_dir is None:
        splits_dir = DEFAULT_SPLITS_DIR
    if out_dir is None:
        out_dir = DEFAULT_OUT_DIR

    os.makedirs(out_dir, exist_ok=True)

    print("\n" + "=" * 78)
    print("STARTING EXPERIMENT E3: CLASSICAL FILTER BENCHMARK & PARETO CURVE ANALYSIS")
    print(f"Filter Methods ({len(filters)}): {filters}")
    print(f"Benchmark Datasets ({len(datasets)}): {datasets}")
    print(f"Primary k Grid: {primary_k_grid}")
    print(f"Pareto Extended k Grid: {pareto_k_grid} on {pareto_datasets}")
    print(f"Parallel Workers: {workers} (single-tier parallelism enforced)")
    print(f"Output Directory: {out_dir}")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 78)

    # 1. Main-Process Splits Pre-generation & Formal OOF Validation
    print("\nPre-generating & Validating Outer Splits (Zero-Leakage & Disjointness Check)...")
    splits_mgr = NestedSplitsManager(splits_dir)
    for ds in datasets:
        try:
            X_ds, y_ds = load_dataset(ds, DATA_DIR_TXT, DATA_DIR_MAT)
            # Sequential generation in main process guarantees atomic creation and avoids process race conditions
            splits_mgr.get_outer_splits(ds, y_ds, n_splits=5, seed=42)
            # Strict validation of 5-fold pooled OOF partition: completeness, disjointness, no overlap
            is_valid, v_msg = splits_mgr.verify_5fold_pooled_oof(ds, y_ds)
            if not is_valid:
                raise RuntimeError(f"Integrity Violation: Dataset '{ds}' outer splits failed OOF verification: {v_msg}")
            if verbose:
                print(f"  [VERIFIED] {ds:12s} | Outer 5-Fold Partition: Disjoint, Complete & Leakage-Free")
        except Exception as e:
            print(f"  [ALERT] Dataset '{ds}' split validation failed: {str(e)}")

    # 2. Build Unified Task Specs per (dataset, filter)
    task_specs = []
    for ds in datasets:
        if ds in pareto_datasets:
            k_grid_for_ds = sorted(list(set(primary_k_grid + pareto_k_grid)))
        else:
            k_grid_for_ds = sorted(list(set(primary_k_grid)))
        for f in filters:
            task_specs.append((ds, f, k_grid_for_ds))

    total_evals = sum(len(k_list) for _, _, k_list in task_specs)
    print(f"\nTotal Unified Tasks: {len(task_specs)} (covering {total_evals} evaluations across k-grids)")

    # 3. Execution Loop with Integrity Gate
    all_results = []
    failed_tasks = []
    completed_task_keys = set()

    if workers == 1:
        for ds, f, k_list in task_specs:
            try:
                res_list = evaluate_filter_on_dataset_grid(ds, f, k_list, splits_dir=splits_dir, verbose=verbose)
                all_results.extend(res_list)
                completed_task_keys.add((ds, f))
            except Exception as e:
                err_msg = str(e)
                tb = traceback.format_exc()
                print(f"  [ERROR] Task ({ds}, {f}) failed: {err_msg}", flush=True)
                failed_tasks.append({
                    "dataset": ds,
                    "filter": f,
                    "k_list": k_list,
                    "error": err_msg,
                    "traceback": tb,
                })
    else:
        with ProcessPoolExecutor(max_workers=workers, initializer=_init_worker) as executor:
            future_to_task = {
                executor.submit(evaluate_filter_on_dataset_grid, ds, f, k_list, splits_dir, False): (ds, f, k_list)
                for ds, f, k_list in task_specs
            }
            completed = 0
            for fut in as_completed(future_to_task):
                ds, f, k_list = future_to_task[fut]
                completed += 1
                try:
                    res_list = fut.result()
                    all_results.extend(res_list)
                    completed_task_keys.add((ds, f))
                    if verbose:
                        k_str = "/".join(str(k) for k in k_list)
                        acc_str = "/".join(f"{r['pooled_metrics']['accuracy']:.3f}" for r in res_list)
                        t_wall = res_list[0]['timing']['grid_task_wall_sec']
                        print(
                            f"  [{completed:2d}/{len(task_specs):2d}] {ds:12s} | {f:15s} | k=[{k_str}] | "
                            f"Acc=[{acc_str}] | Wall={t_wall:.2f}s",
                            flush=True,
                        )
                except Exception as e:
                    err_msg = str(e)
                    tb = traceback.format_exc()
                    print(f"  [ERROR] Task ({ds}, {f}) failed: {err_msg}", flush=True)
                    failed_tasks.append({
                        "dataset": ds,
                        "filter": f,
                        "k_list": k_list,
                        "error": err_msg,
                        "traceback": tb,
                    })

    total_elapsed = time.perf_counter() - t0_all
    is_complete = (len(failed_tasks) == 0) and (len(completed_task_keys) == len(task_specs))
    execution_status = "COMPLETE" if is_complete else "INCOMPLETE"

    # Save Failure Manifest if any task failed
    if failed_tasks:
        fail_json_path = os.path.join(out_dir, "e3_failures.json")
        with open(fail_json_path, "w", encoding="utf-8") as f:
            json.dump({
                "status": "INCOMPLETE",
                "timestamp": datetime.now().isoformat(),
                "total_expected": len(task_specs),
                "total_completed": len(completed_task_keys),
                "total_failed": len(failed_tasks),
                "failures": failed_tasks,
            }, f, indent=2)
        print(f"\n[ALERT] Integrity Gate: {len(failed_tasks)} / {len(task_specs)} tasks failed! Details in {fail_json_path}")

    # 4. Structure Deliverables
    # (a) Detailed runs JSON
    detailed_json_path = os.path.join(out_dir, "e3_detailed_runs.json")
    with open(detailed_json_path, "w", encoding="utf-8") as f:
        json.dump(all_results, f, indent=2)

    # (b) Summary Matrix for primary grid k in primary_k_grid
    summary_primary = {}
    for f in filters:
        summary_primary[f] = {}
        for k in primary_k_grid:
            summary_primary[f][k] = {}
            for ds in datasets:
                match = [r for r in all_results if r["dataset"] == ds and r["filter"] == f and r["k"] == k]
                if match:
                    summary_primary[f][k][ds] = match[0]["pooled_metrics"]

    # (c) Common Completed Datasets across all active filters
    common_completed_datasets = [
        ds for ds in datasets
        if all(ds in summary_primary.get(f, {}).get(k, {}) for f in filters for k in primary_k_grid)
    ]

    # (d) Pareto Trajectories for representative datasets actually evaluated
    pareto_trajectories = {}
    for ds in pareto_datasets:
        if ds not in datasets:
            continue
        pareto_trajectories[ds] = {}
        for f in filters:
            pareto_trajectories[ds][f] = []
            for k in pareto_k_grid:
                match = [r for r in all_results if r["dataset"] == ds and r["filter"] == f and r["k"] == k]
                if match:
                    pareto_trajectories[ds][f].append({
                        "k": k,
                        "accuracy": match[0]["pooled_metrics"]["accuracy"],
                        "balanced_accuracy": match[0]["pooled_metrics"]["balanced_accuracy"],
                        "macro_f1": match[0]["pooled_metrics"]["macro_f1"],
                        "shared_ranking_sec": match[0]["timing"]["shared_ranking_sec"],
                        "k_eval_sec": match[0]["timing"]["k_eval_sec"],
                        "k_standalone_pipeline_sec": match[0]["timing"]["k_standalone_pipeline_sec"],
                        "grid_task_wall_sec": match[0]["timing"]["grid_task_wall_sec"],
                    })

    pareto_json_path = os.path.join(out_dir, "e3_pareto_curves.json")
    with open(pareto_json_path, "w", encoding="utf-8") as f:
        json.dump(pareto_trajectories, f, indent=2)

    # (e) Grand Averages across Common Completed Datasets
    grand_primary_table = []
    for f in filters:
        for k in primary_k_grid:
            if common_completed_datasets:
                accs = [summary_primary[f][k][ds]["accuracy"] for ds in common_completed_datasets]
                baccs = [summary_primary[f][k][ds]["balanced_accuracy"] for ds in common_completed_datasets]
                f1s = [summary_primary[f][k][ds]["macro_f1"] for ds in common_completed_datasets]
                grand_primary_table.append({
                    "filter": f,
                    "k": k,
                    "evaluated_datasets_count": len(common_completed_datasets),
                    "mean_accuracy": round(float(np.mean(accs)), 6),
                    "mean_balanced_accuracy": round(float(np.mean(baccs)), 6),
                    "mean_macro_f1": round(float(np.mean(f1s)), 6),
                })
            else:
                grand_primary_table.append({
                    "filter": f,
                    "k": k,
                    "evaluated_datasets_count": 0,
                    "mean_accuracy": None,
                    "mean_balanced_accuracy": None,
                    "mean_macro_f1": None,
                })

    # Threadpool info for system metadata
    try:
        import threadpoolctl
        tp_info = threadpoolctl.threadpool_info()
    except Exception:
        tp_info = []

    summary_payload = {
        "experiment": "E3_Classical_Filter_Benchmark",
        "execution_status": execution_status,
        "timestamp": datetime.now().isoformat(),
        "task_accounting": {
            "expected_tasks": len(task_specs),
            "completed_tasks": len(completed_task_keys),
            "failed_tasks": len(failed_tasks),
        },
        "total_results_count": len(all_results),
        "total_elapsed_sec": round(total_elapsed, 2),
        "filters_evaluated": filters,
        "primary_k_grid": primary_k_grid,
        "common_completed_datasets": common_completed_datasets,
        "grand_primary_table": grand_primary_table,
        "pareto_trajectories": pareto_trajectories,
        "failed_tasks": failed_tasks,
        "system_metadata": {
            "platform": platform.platform(),
            "python": platform.python_version(),
            "workers": workers,
            "single_tier_parallelism": True,
            "threadpool_info": tp_info,
        },
    }
    summary_json_path = os.path.join(out_dir, "e3_summary_table.json")
    with open(summary_json_path, "w", encoding="utf-8") as f:
        json.dump(summary_payload, f, indent=2)

    # 5. Generate Comprehensive Academic Markdown Report
    report_md_path = os.path.join(out_dir, "e3_filter_benchmark_report.md")
    with open(report_md_path, "w", encoding="utf-8") as f:
        f.write("# E3: Classical Filter Fold-Internal Benchmark & Pareto Front Analysis\n\n")
        f.write(f"- **Execution Timestamp**: {summary_payload['timestamp']}\n")
        status_str = "COMPLETE" if is_complete else f"⚠️ INCOMPLETE ({len(failed_tasks)} / {len(task_specs)} tasks failed)"
        f.write(f"- **Execution Status**: **{status_str}**\n")
        f.write(f"- **Protocol Reference**: `review_round_1/05_executable_experiment_plan.md` (Section 6)\n")
        f.write(f"- **Evaluated Filters ({len(filters)})**: `{', '.join(filters)}`\n")
        f.write(f"- **Target Benchmark Datasets ({len(datasets)})**: Outer 5 Folds, Pooled OOF\n")
        f.write(f"- **Common Completed Datasets**: **{len(common_completed_datasets)} / {len(datasets)}**\n")
        f.write(f"- **Task Accounting**: {len(completed_task_keys)} / {len(task_specs)} completed ({len(failed_tasks)} failed)\n")
        f.write(f"- **Total Elapsed Time**: `{total_elapsed:.2f} s`\n\n")

        f.write("> **Formal Methodological Demarcation**:\n")
        f.write("> In strict compliance with zero-leakage protocols, all filter algorithms were fitted ")
        f.write("exclusively on the outer training fold without any access to the outer test set. ")
        f.write("Performance metrics are reported via Pooled Out-Of-Fold (OOF) predictions across the 5 outer folds, ")
        f.write("providing a clean empirical baseline for fold-internal feature selection across candidate cardinality budgets.\n\n")

        if failed_tasks:
            f.write("> [!WARNING]\n")
            f.write(f"> **Execution Incomplete**: {len(failed_tasks)} tasks failed. Missing values are marked as `—` (N/A) ")
            f.write("and strictly excluded from aggregate means. Full traceback logs are preserved in `e3_failures.json`.\n\n")
            f.write("### Failure Manifest\n\n")
            f.write("| Dataset | Filter | Target $k$-Grid | Error Summary |\n")
            f.write("| :--- | :--- | :---: | :--- |\n")
            for ft in failed_tasks:
                k_list_str = "/".join(str(k) for k in ft["k_list"])
                f.write(f"| **{ft['dataset']}** | `{ft['filter']}` | [{k_list_str}] | {ft['error'][:80]} |\n")
            f.write("\n")

        # Section 1: Aggregate Table
        f.write(f"## 1. Overall Aggregate Performance Comparison (across {len(common_completed_datasets)} Common Datasets)\n\n")
        if common_completed_datasets:
            f.write("| Filter Algorithm | Feature Budget ($k$) | Mean Accuracy | Mean Balanced Acc | Mean Macro-F1 | Datasets |\n")
            f.write("| :--- | :---: | :---: | :---: | :---: | :---: |\n")
            for row in grand_primary_table:
                acc_s = f"**{row['mean_accuracy']:.4f}**" if row['mean_accuracy'] is not None else "—"
                bacc_s = f"{row['mean_balanced_accuracy']:.4f}" if row['mean_balanced_accuracy'] is not None else "—"
                f1_s = f"{row['mean_macro_f1']:.4f}" if row['mean_macro_f1'] is not None else "—"
                f.write(f"| **{row['filter']}** | $k = {row['k']}$ | {acc_s} | {bacc_s} | {f1_s} | {row['evaluated_datasets_count']} |\n")
        else:
            f.write("*Aggregate comparison is not available because no dataset successfully completed all evaluated filters.*\n")

        # Section 2: Dynamic Primary Grid Breakdown
        f.write(f"\n## 2. Benchmark Primary Grid Breakdown ($k \\in [{', '.join(str(k) for k in primary_k_grid)}] $)\n\n")
        k_header_str = "/".join(str(k) for k in primary_k_grid)
        headers = ["Dataset", "Metric"] + [f"{f} ({k_header_str})" for f in filters]
        f.write("| " + " | ".join(headers) + " |\n")
        f.write("| " + " | ".join([":---" if i < 2 else ":---:" for i in range(len(headers))]) + " |\n")

        for ds in datasets:
            def _fmt_row(metric_key):
                cols = []
                for f_name in filters:
                    cell_vals = []
                    for k in primary_k_grid:
                        val = summary_primary.get(f_name, {}).get(k, {}).get(ds, {}).get(metric_key)
                        cell_vals.append(f"{val:.3f}" if val is not None else "—")
                    cols.append("/".join(cell_vals))
                return cols

            acc_cols = _fmt_row("accuracy")
            bacc_cols = _fmt_row("balanced_accuracy")
            f1_cols = _fmt_row("macro_f1")

            f.write(f"| **{ds}** | Accuracy | " + " | ".join(acc_cols) + " |\n")
            f.write(f"| | Balanced Acc | " + " | ".join(bacc_cols) + " |\n")
            f.write(f"| | Macro-F1 | " + " | ".join(f1_cols) + " |\n")

        # Section 3: Representative Pareto Trajectories
        f.write(f"\n## 3. Representative Pareto Trajectories ($k \\in [{', '.join(str(k) for k in pareto_k_grid)}] $)\n\n")
        for ds in pareto_datasets:
            if ds not in datasets:
                continue
            f.write(f"### Dataset: {ds}\n\n")
            has_records = any(len(pareto_trajectories.get(ds, {}).get(f_name, [])) > 0 for f_name in filters)
            if not has_records:
                f.write(f"*Dataset `{ds}` was not executed or yielded no valid results in this run.*\n\n")
                continue

            pareto_cols = [f"$k={k}$ Acc" for k in pareto_k_grid]
            f.write("| Filter Algorithm | " + " | ".join(pareto_cols) + " |\n")
            f.write("| :--- | " + " | ".join([":---:" for _ in pareto_cols]) + " |\n")

            for f_name in filters:
                trajs = {t["k"]: t["accuracy"] for t in pareto_trajectories.get(ds, {}).get(f_name, [])}
                row_str = " | ".join([f"{trajs[k]:.4f}" if k in trajs else "—" for k in pareto_k_grid])
                f.write(f"| **{f_name}** | {row_str} |\n")
            f.write("\n")

        # Section 4: Data-Grounded Empirical Observations
        f.write("## 4. Academic Insights & Empirical Filter Observations\n\n")
        f.write("### 4.1 Methodological Protocol & Selection Mechanisms\n\n")
        f.write("1. **Fold-Internal Zero-Leakage Protocol**: All feature selection, scaling, and ranking operations are ")
        f.write("performed strictly on each outer training fold, ensuring strict blind evaluation on held-out test folds.\n")
        f.write("2. **LASSO L1-OvR & Two-Tier Non-Zero Lexical Priority**: LASSO is formalized via OneVsRestClassifier with L1 regularized Logistic Regression ($C=0.1$). ")
        f.write("Features with non-zero coefficients are ranked strictly ahead of zero-coefficient features by cumulative absolute weight $\\sum_c |\\beta_{c,j}|$. ")
        f.write("When non-zero features are fewer than $k$, remaining slots are completed by sorting zero-coefficient features by training-fold Mutual Information (MI). ")
        f.write("Fitting failures strictly trigger exceptions without silent substitution.\n\n")

        f.write("### 4.2 Dynamic Empirical Observations from Current Execution\n\n")

        # Dynamic Point 1: Filter Hierarchy
        if common_completed_datasets and len(filters) > 1:
            filter_acc_means = {}
            for f_name in filters:
                f_accs = [
                    summary_primary[f_name][k][ds]["accuracy"]
                    for ds in common_completed_datasets
                    for k in primary_k_grid
                    if ds in summary_primary.get(f_name, {}).get(k, {})
                ]
                filter_acc_means[f_name] = float(np.mean(f_accs)) if f_accs else 0.0

            ranked_filters = sorted(filters, key=lambda fn: filter_acc_means[fn], reverse=True)
            rank_chain = " > ".join(f"`{fn}` ({filter_acc_means[fn]:.4f})" for fn in ranked_filters)
            f.write(f"1. **Observed Filter Performance Hierarchy**: Across the {len(common_completed_datasets)} common completed dataset(s) ")
            f.write(f"over the primary grid $k \\in [{', '.join(str(k) for k in primary_k_grid)}]$, the aggregate mean accuracy ranking is: {rank_chain}.\n")
        elif common_completed_datasets and len(filters) == 1:
            f_name = filters[0]
            all_accs = [
                summary_primary[f_name][k][ds]["accuracy"]
                for ds in common_completed_datasets
                for k in primary_k_grid
            ]
            f.write(f"1. **Single-Filter Benchmark Evaluation**: Evaluated `{f_name}` across {len(common_completed_datasets)} dataset(s), ")
            f.write(f"yielding an overall mean accuracy of {np.mean(all_accs):.4f} across the evaluated primary grid.\n")
        else:
            f.write("1. **Filter Performance Hierarchy**: Insufficient common completed datasets to establish aggregate filter ranking.\n")

        # Dynamic Point 2: Feature Budget Sensitivity
        if common_completed_datasets and len(primary_k_grid) > 1:
            k_means = {}
            for k in primary_k_grid:
                k_accs = [
                    summary_primary[f_name][k][ds]["accuracy"]
                    for f_name in filters
                    for ds in common_completed_datasets
                    if ds in summary_primary.get(f_name, {}).get(k, {})
                ]
                k_means[k] = float(np.mean(k_accs)) if k_accs else 0.0

            k_chain = " $\\to$ ".join(f"$k={k}$: **{k_means[k]:.4f}**" for k in primary_k_grid)
            f.write(f"2. **Feature Budget ($k$) Sensitivity**: Across the evaluated cardinality grid, aggregate mean accuracy progresses as follows: {k_chain}. ")

            k_vals = primary_k_grid
            is_monotonic_up = all(k_means[k_vals[i]] <= k_means[k_vals[i+1]] for i in range(len(k_vals)-1))
            is_monotonic_down = all(k_means[k_vals[i]] >= k_means[k_vals[i+1]] for i in range(len(k_vals)-1))

            if is_monotonic_up and k_means[k_vals[-1]] > k_means[k_vals[0]]:
                f.write(f"Performance increases monotonically from $k={k_vals[0]}$ to $k={k_vals[-1]}$.\n")
            elif is_monotonic_down and k_means[k_vals[0]] > k_means[k_vals[-1]]:
                f.write(f"Performance decreases as cardinality increases from $k={k_vals[0]}$ to $k={k_vals[-1]}$, indicating dimensionality penalties.\n")
            else:
                best_k = max(k_vals, key=lambda k: k_means[k])
                f.write(f"Performance peaks at $k={best_k}$ ({k_means[best_k]:.4f}), indicating non-monotonic saturation behavior over this range.\n")
        elif len(primary_k_grid) == 1:
            f.write(f"2. **Feature Budget ($k$) Sensitivity**: Single cardinality budget evaluated at $k={primary_k_grid[0]}$.\n")
        else:
            f.write("2. **Feature Budget Sensitivity**: Incomplete data to determine cardinality progression trend.\n")

        f.write("3. **Cross-Paradigm Comparison Alignment**: These measurements reflect fold-internal filter performance. ")
        f.write("Direct comparisons against wrapper or evolutionary algorithms require matched cardinality budgets ")
        f.write("and identical outer cross-validation fold partitions.\n")

        # Optional Section 5: Side-by-side comparison if verified KDS-EL results file provided
        if kdsel_results_path and os.path.exists(kdsel_results_path):
            try:
                with open(kdsel_results_path, "r", encoding="utf-8") as kf:
                    kdsel_data = json.load(kf)
                f.write("\n## 5. Side-by-Side Comparison against Verified KDS-EL Results\n\n")
                f.write(f"- Source: `{kdsel_results_path}`\n\n")
            except Exception as e:
                f.write(f"\n*Note: Could not parse KDS-EL comparison file: {str(e)}*\n")

    print("\n" + "=" * 78)
    status_label = "SUCCESSFULLY" if is_complete else "WITH INCOMPLETE TASKS"
    print(f"EXPERIMENT E3 COMPLETED {status_label} in {total_elapsed:.2f}s!")
    print(f"Artifacts saved:")
    print(f"  - Detailed Runs JSON: {detailed_json_path}")
    print(f"  - Summary Matrix JSON: {summary_json_path}")
    print(f"  - Pareto Curves JSON: {pareto_json_path}")
    print(f"  - Academic Markdown Report: {report_md_path}")
    if failed_tasks:
        print(f"  - Failures Manifest JSON: {fail_json_path}")
    print("=" * 78)

    return summary_payload


# ══════════════════════════════════════════════════════════════════════════════
# Command Line Interface
# ══════════════════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(description="Run Experiment E3: Classical Filter Benchmark & Pareto Analysis")
    parser.add_argument(
        "--workers",
        type=int,
        default=2,
        help="Number of parallel worker processes (default: 2, matching E1 safety recommendation)",
    )
    parser.add_argument(
        "--datasets",
        type=str,
        nargs="+",
        default=None,
        help="Datasets to evaluate (default: all 19 benchmark datasets)",
    )
    parser.add_argument(
        "--filters",
        type=str,
        nargs="+",
        default=None,
        help="Filter algorithms to evaluate (default: Top-k MI, Two-Stage mRMR, ReliefF, LASSO)",
    )
    parser.add_argument(
        "--primary-k",
        type=int,
        nargs="+",
        default=None,
        help="Primary k grid to evaluate (default: [20, 50, 100])",
    )
    parser.add_argument(
        "--out-dir",
        type=str,
        default=DEFAULT_OUT_DIR,
        help=f"Output directory (default: {DEFAULT_OUT_DIR})",
    )
    parser.add_argument(
        "--kdsel-results",
        type=str,
        default=None,
        help="Optional path to verified KDS-EL outer-fold results JSON for side-by-side comparison",
    )
    parser.add_argument("--quiet", action="store_true", help="Suppress detailed console logs")
    args = parser.parse_args()

    payload = run_experiment_e3(
        datasets=args.datasets,
        filters=args.filters,
        primary_k_grid=args.primary_k,
        workers=args.workers,
        out_dir=args.out_dir,
        kdsel_results_path=args.kdsel_results,
        verbose=not args.quiet,
    )

    if payload["execution_status"] != "COMPLETE":
        print(f"\n[EXIT] Process exiting with status 1 due to incomplete/failed tasks.")
        sys.exit(1)


if __name__ == "__main__":
    main()
