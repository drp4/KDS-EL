"""
E0: Candidate Fast 3-NN Equivalence Verification & Decision Gate
===============================================================
Protocol Reference:
  - review_round_1/05_executable_experiment_plan.md, Section 3
  - review_round_1/04_detailed_supplementary_experiment_design.md, Section VIII

Objective:
  Evaluate numerical, prediction, and ranking equivalence between the
  authoritative Scikit-Learn 3-NN evaluator (code/utils.py) and the
  candidate vectorized Fast 3-NN implementation across 4 representative datasets
  (Colon, T1D, BASEHOCK, COIL20) and 800 random feature masks (200 per dataset)
  spanning sparse (5-30), medium (50-200), and dense (500-2000) feature tiers.

Acceptance Gate Criteria:
  1. Full prediction vector equality across all samples: 100% match (0 mismatches).
  2. Max absolute Accuracy diff < 1e-12.
  3. Max absolute Balanced Accuracy diff < 1e-12.
  4. Max absolute Macro-F1 diff < 1e-12.
  5. Kendall's tau == 1.0 and Spearman's rho == 1.0 on candidate fitness ranking.

Decision Gate:
  - PASS: All 800 masks across all 4 datasets satisfy criteria 1-5 -> Fast 3-NN admitted.
  - FAIL: Any prediction mismatch -> Candidate accelerator rejected; mandatory
    fallback to authoritative Scikit-Learn 3-NN evaluator triggered for all formal runs.
"""

import os
import sys
import time
import json
import argparse
from datetime import datetime
import numpy as np
from sklearn.model_selection import StratifiedKFold
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import balanced_accuracy_score, f1_score
from scipy.stats import kendalltau, spearmanr

# Ensure code/ is on path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
sys.path.insert(0, CURRENT_DIR)

# Force UTF-8 encoding on Windows to prevent GBK encoding errors
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

from utils import load_dataset
from config import DATA_DIR_TXT, DATA_DIR_MAT

E0_DATASETS = ["Colon", "T1D", "BASEHOCK", "COIL20"]


def sklearn_cv_evaluate(X, y, mask, k=3, cv_splits=5, random_state=42):
    """
    Authoritative Ground-Truth: Scikit-learn 3-NN across stratified folds.
    Strictly mirrors code/utils.py:evaluate_subset and jwrapper.
    """
    mask = np.asarray(mask, dtype=bool)
    X_sub = X[:, mask]
    N_samples = len(y)
    y_arr = np.asarray(y)

    min_class = int(np.min(np.bincount(y_arr)))
    n_splits = min(cv_splits, min_class)
    if n_splits < 2:
        return 0.0, 0.0, 0.0, np.zeros(N_samples, dtype=int)

    skf = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=random_state)
    y_pred = np.zeros(N_samples, dtype=int)

    for tr, te in skf.split(X_sub, y_arr):
        actual_k = min(k, len(tr))
        clf = KNeighborsClassifier(n_neighbors=actual_k)
        clf.fit(X_sub[tr], y_arr[tr])
        y_pred[te] = clf.predict(X_sub[te])

    acc = float(np.mean(y_pred == y_arr))
    bacc = float(balanced_accuracy_score(y_arr, y_pred))
    macro_f1 = float(f1_score(y_arr, y_pred, average="macro", zero_division=0))
    return acc, bacc, macro_f1, y_pred


def candidate_fast_cv_evaluate(X, y, mask, k=3, cv_splits=5, random_state=42):
    """
    Candidate Fast 3-NN:
    - Maintains native float64 precision
    - Dynamic actual_k guard
    - Vectorized Euclidean distance + local stable sort
    """
    mask = np.asarray(mask, dtype=bool)
    X_sub = np.ascontiguousarray(X[:, mask], dtype=X.dtype)
    N_samples = len(y)
    y_arr = np.asarray(y)

    min_class = int(np.min(np.bincount(y_arr)))
    n_splits = min(cv_splits, min_class)
    if n_splits < 2:
        return 0.0, 0.0, 0.0, np.zeros(N_samples, dtype=int)

    skf = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=random_state)
    y_pred = np.zeros(N_samples, dtype=int)

    for tr, te in skf.split(X_sub, y_arr):
        X_tr = X_sub[tr]
        y_tr = y_arr[tr]
        X_te = X_sub[te]

        actual_k = min(k, len(tr))
        if actual_k < 1:
            continue

        # Vectorized pairwise squared Euclidean distances (N_te x N_tr)
        dists = np.sum(X_te**2, axis=1, keepdims=True) + \
                np.sum(X_tr**2, axis=1, keepdims=True).T - \
                2.0 * np.dot(X_te, X_tr.T)
        dists = np.maximum(dists, 0.0)

        # Stable top-actual_k selection
        if actual_k < dists.shape[1]:
            top_k_part = np.argpartition(dists, actual_k - 1, axis=1)[:, :actual_k]
            part_dists = np.take_along_axis(dists, top_k_part, axis=1)
            local_sort = np.argsort(part_dists, axis=1, kind="stable")
            top_k_idx = np.take_along_axis(top_k_part, local_sort, axis=1)
        else:
            top_k_idx = np.argsort(dists, axis=1, kind="stable")[:, :actual_k]

        top_k_labels = y_tr[top_k_idx]

        # Majority voting with smallest-class tie-breaking
        for i in range(len(te)):
            counts = np.bincount(top_k_labels[i])
            y_pred[te[i]] = counts.argmax()

    acc = float(np.mean(y_pred == y_arr))
    bacc = float(balanced_accuracy_score(y_arr, y_pred))
    macro_f1 = float(f1_score(y_arr, y_pred, average="macro", zero_division=0))
    return acc, bacc, macro_f1, y_pred


def generate_tiered_masks(D, num_masks=200, seed=42):
    """
    Generate masks across 3 cardinality tiers as specified in Section 3.2:
      - Tier 1 (Sparse): 5 to 30 features (67 masks)
      - Tier 2 (Medium): 50 to 200 features (67 masks)
      - Tier 3 (Dense): 500 to 2000 features (66 masks, clipped to D)
    """
    rng = np.random.RandomState(seed)
    masks = []

    n_sparse = num_masks // 3
    n_medium = num_masks // 3
    n_dense = num_masks - n_sparse - n_medium

    # Tier 1: 5-30
    for _ in range(n_sparse):
        k_feats = rng.randint(min(5, D), min(31, D + 1))
        k_feats = max(1, k_feats)
        m = np.zeros(D, dtype=bool)
        m[rng.choice(D, k_feats, replace=False)] = True
        masks.append(m)

    # Tier 2: 50-200
    for _ in range(n_medium):
        low = min(50, D)
        high = min(201, D + 1)
        if low >= high:
            k_feats = D
        else:
            k_feats = rng.randint(low, high)
        k_feats = max(1, k_feats)
        m = np.zeros(D, dtype=bool)
        m[rng.choice(D, k_feats, replace=False)] = True
        masks.append(m)

    # Tier 3: 500-2000
    for _ in range(n_dense):
        low = min(500, D)
        high = min(2001, D + 1)
        if low >= high:
            k_feats = D
        else:
            k_feats = rng.randint(low, high)
        k_feats = max(1, k_feats)
        m = np.zeros(D, dtype=bool)
        m[rng.choice(D, k_feats, replace=False)] = True
        masks.append(m)

    return masks


def verify_dataset(dataset_name, num_masks=200, seed=42, verbose=True):
    """Run full verification on a single dataset across num_masks."""
    if verbose:
        print(f"\n{'='*70}")
        print(f"[E0 Verification] Dataset: {dataset_name}")
        print(f"{'='*70}")

    X, y = load_dataset(dataset_name, DATA_DIR_TXT, DATA_DIR_MAT)
    N_samples, D = X.shape
    classes = np.unique(y)
    if verbose:
        print(f"  Samples: {N_samples}, Features: {D}, Classes: {len(classes)} ({dict(zip(*np.unique(y, return_counts=True)))})")

    masks = generate_tiered_masks(D, num_masks=num_masks, seed=seed)

    skl_accs, skl_baccs, skl_f1s, skl_fits = [], [], [], []
    fast_accs, fast_baccs, fast_f1s, fast_fits = [], [], [], []

    total_predictions = 0
    mismatched_predictions = 0

    t0_skl = time.perf_counter()
    for mask in masks:
        acc, bacc, f1, preds = sklearn_cv_evaluate(X, y, mask)
        skl_accs.append(acc)
        skl_baccs.append(bacc)
        skl_f1s.append(f1)
        fit = 0.90 * (1.0 - acc) + 0.10 * (mask.sum() / D)
        skl_fits.append(fit)
    t_skl_total = time.perf_counter() - t0_skl

    t0_fast = time.perf_counter()
    fast_preds_list = []
    for mask in masks:
        acc, bacc, f1, preds = candidate_fast_cv_evaluate(X, y, mask)
        fast_accs.append(acc)
        fast_baccs.append(bacc)
        fast_f1s.append(f1)
        fit = 0.90 * (1.0 - acc) + 0.10 * (mask.sum() / D)
        fast_fits.append(fit)
        fast_preds_list.append(preds)
    t_fast_total = time.perf_counter() - t0_fast

    # Compare sample predictions
    for idx, mask in enumerate(masks):
        _, _, _, skl_preds = sklearn_cv_evaluate(X, y, mask)
        fast_preds = fast_preds_list[idx]
        diff = int(np.sum(skl_preds != fast_preds))
        mismatched_predictions += diff
        total_predictions += N_samples

    max_acc_diff = float(np.max(np.abs(np.array(skl_accs) - np.array(fast_accs))))
    max_bacc_diff = float(np.max(np.abs(np.array(skl_baccs) - np.array(fast_baccs))))
    max_f1_diff = float(np.max(np.abs(np.array(skl_f1s) - np.array(fast_f1s))))

    # Ranking correlations
    if np.all(np.array(skl_fits) == skl_fits[0]) or np.all(np.array(fast_fits) == fast_fits[0]):
        tau, rho = 1.0, 1.0
    else:
        tau_val, _ = kendalltau(skl_fits, fast_fits)
        rho_val, _ = spearmanr(skl_fits, fast_fits)
        tau = float(tau_val) if not np.isnan(tau_val) else 1.0
        rho = float(rho_val) if not np.isnan(rho_val) else 1.0

    speedup = float(t_skl_total / max(1e-6, t_fast_total))

    # Pass condition
    is_passed = (
        mismatched_predictions == 0
        and max_acc_diff < 1e-12
        and max_bacc_diff < 1e-12
        and max_f1_diff < 1e-12
        and abs(tau - 1.0) < 1e-6
        and abs(rho - 1.0) < 1e-6
    )

    result = {
        "dataset": dataset_name,
        "n_samples": int(N_samples),
        "d_features": int(D),
        "n_classes": int(len(classes)),
        "num_masks_evaluated": int(num_masks),
        "total_sample_predictions": int(total_predictions),
        "mismatched_sample_predictions": int(mismatched_predictions),
        "mismatch_rate": float(mismatched_predictions / max(1, total_predictions)),
        "max_acc_diff": float(max_acc_diff),
        "max_bacc_diff": float(max_bacc_diff),
        "max_macro_f1_diff": float(max_f1_diff),
        "ranking_kendall_tau": float(tau),
        "ranking_spearman_rho": float(rho),
        "time_sklearn_sec": float(t_skl_total),
        "time_fast_sec": float(t_fast_total),
        "speedup_ratio": float(speedup),
        "status": "PASS" if is_passed else "FAIL",
    }

    if verbose:
        status_tag = "[PASS]" if is_passed else "[FAIL]"
        print(f"  {status_tag} Mismatches: {mismatched_predictions} / {total_predictions} ({result['mismatch_rate']*100:.4f}%)")
        print(f"  Max Absolute Differences: Acc={max_acc_diff:.2e}, BAcc={max_bacc_diff:.2e}, F1={max_f1_diff:.2e}")
        print(f"  Ranking Correlations: Kendall tau={tau:.6f}, Spearman rho={rho:.6f}")
        print(f"  Wall-Clock Time: Sklearn={t_skl_total:.2f}s, Fast={t_fast_total:.2f}s -> Speedup: {speedup:.2f}x")

    return result


def run_e0(num_masks=200, output_dir=None, verbose=True):
    """Run E0 across all 4 benchmark datasets and emit decision report."""
    if output_dir is None:
        output_dir = os.path.join(PROJECT_ROOT, "output", "nested_cv", "e0_verification")
    os.makedirs(output_dir, exist_ok=True)

    print("=" * 75)
    print("STARTING EXPERIMENT E0: CANDIDATE FAST 3-NN EQUIVALENCE VERIFICATION")
    print(f"Datasets: {E0_DATASETS} (4 datasets)")
    print(f"Masks per Dataset: {num_masks} (Total: {num_masks * len(E0_DATASETS)} masks)")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 75)

    dataset_results = []
    all_passed = True
    total_mismatches = 0
    total_predictions = 0
    total_time_skl = 0.0
    total_time_fast = 0.0

    for ds in E0_DATASETS:
        res = verify_dataset(ds, num_masks=num_masks, verbose=verbose)
        dataset_results.append(res)
        if res["status"] != "PASS":
            all_passed = False
        total_mismatches += res["mismatched_sample_predictions"]
        total_predictions += res["total_sample_predictions"]
        total_time_skl += res["time_sklearn_sec"]
        total_time_fast += res["time_fast_sec"]

    overall_speedup = total_time_skl / max(1e-6, total_time_fast)
    decision = "ADMITTED" if all_passed else "REJECTED_FALLBACK_TO_SKLEARN"

    summary = {
        "experiment": "E0_Fast_3NN_Equivalence_Verification",
        "protocol_version": "review_round_1_05_executable_experiment_plan",
        "timestamp": datetime.now().isoformat(),
        "datasets": E0_DATASETS,
        "num_masks_per_dataset": num_masks,
        "total_masks_evaluated": num_masks * len(E0_DATASETS),
        "total_predictions_evaluated": total_predictions,
        "total_mismatches": total_mismatches,
        "overall_mismatch_rate": total_mismatches / max(1, total_predictions),
        "total_time_sklearn_sec": round(total_time_skl, 3),
        "total_time_fast_sec": round(total_time_fast, 3),
        "overall_speedup_ratio": round(overall_speedup, 2),
        "decision_gate": decision,
        "fast_evaluator_admitted": all_passed,
        "fallback_activated": not all_passed,
        "dataset_results": dataset_results,
    }

    # Save JSON report
    json_path = os.path.join(output_dir, "e0_equivalence_report.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    # Save Markdown report
    md_path = os.path.join(output_dir, "e0_equivalence_report.md")
    with open(md_path, "w", encoding="utf-8") as f:
        f.write("# E0: Candidate Fast 3-NN Equivalence Verification & Decision Gate Report\n\n")
        f.write(f"- **Execution Timestamp**: {summary['timestamp']}\n")
        f.write(f"- **Protocol Document**: `review_round_1/05_executable_experiment_plan.md` (Section 3)\n")
        f.write(f"- **Total Masks Evaluated**: {summary['total_masks_evaluated']}\n")
        f.write(f"- **Total Predictions Evaluated**: {summary['total_predictions_evaluated']}\n")
        f.write(f"- **Total Prediction Mismatches**: {summary['total_mismatches']}\n")
        f.write(f"- **Decision Gate Status**: **`{decision}`**\n\n")

        if all_passed:
            f.write("> **GATE VERDICT: PASS** — The candidate fast 3-NN implementation achieved 100% exact numerical and prediction equivalence across all 800 masks and 4 datasets. It is officially permitted for deployment in surrogate evaluations.\n\n")
        else:
            f.write("> **GATE VERDICT: REJECTED (FALLBACK TO SCIKIT-LEARN TRIGGERED)** — Prediction divergences were detected on at least one benchmark dataset (e.g. zero-distance tie-breaking divergence on sparse bag-of-words text data). In strict adherence to Section 3.4 of the experiment plan, the candidate accelerator is rejected and all downstream experiments MUST fall back to the authoritative Scikit-Learn `KNeighborsClassifier` evaluator.\n\n")

        f.write("## Per-Dataset Verification Breakdown\n\n")
        f.write("| Dataset | Samples | Features | Classes | Masks | Mismatches | Max ΔAcc | Max ΔBAcc | Max ΔF1 | Kendall τ | Spearman ρ | Speedup | Status |\n")
        f.write("| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |\n")
        for r in dataset_results:
            f.write(f"| **{r['dataset']}** | {r['n_samples']} | {r['d_features']} | {r['n_classes']} | {r['num_masks_evaluated']} | {r['mismatched_sample_predictions']} | {r['max_acc_diff']:.1e} | {r['max_bacc_diff']:.1e} | {r['max_macro_f1_diff']:.1e} | {r['ranking_kendall_tau']:.4f} | {r['ranking_spearman_rho']:.4f} | {r['speedup_ratio']:.2f}x | **{r['status']}** |\n")

        f.write("\n## Execution Wall-Clock Timing\n\n")
        f.write(f"- Authoritative Scikit-Learn 3-NN Total Time: `{total_time_skl:.2f} s`\n")
        f.write(f"- Candidate Fast 3-NN Total Time: `{total_time_fast:.2f} s`\n")
        f.write(f"- Empirical Acceleration Ratio: `{overall_speedup:.2f}x`\n")

    print("\n" + "=" * 75)
    print(f"E0 VERIFICATION COMPLETED: Decision Gate = {decision}")
    print(f"Artifacts saved:")
    print(f"  - JSON Report: {json_path}")
    print(f"  - Markdown Report: {md_path}")
    print("=" * 75)

    return summary


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run Experiment E0: Fast 3-NN Equivalence Verification")
    parser.add_argument("--masks", type=int, default=200, help="Number of masks per dataset (default: 200, total 800)")
    parser.add_argument("--out-dir", type=str, default=None, help="Output directory for reports")
    parser.add_argument("--quiet", action="store_true", help="Suppress verbose stdout")
    args = parser.parse_args()

    run_e0(num_masks=args.masks, output_dir=args.out_dir, verbose=not args.quiet)
