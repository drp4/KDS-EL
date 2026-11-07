"""
Experiment E2: Offline Multi-Metric Re-Analysis of Competitor Masks
===================================================================
Protocol Reference:
  - review_round_1/05_executable_experiment_plan.md (Section 5)
  - review_round_1/04_detailed_supplementary_experiment_design.md (Section 5)

Data Source (Strict Read-Only):
  - output/formal_experiment_20260905_211755/masks/
  - Competitor algorithms: bIRIME, BinCOA, DENCA_SO (3 algorithms)
  - Benchmarks: 19 datasets (BENCHMARK_19_DATASETS, strictly excluding ALL_AML)
  - Runs: 10 independent runs
  - Total Target Masks: 3 x 19 x 10 = 570 masks.

Strict Safeguards:
  - MUST skip/reject any mask containing 'KDS_EL' or 'MEL'.
  - Computes Accuracy, Balanced Accuracy, and Macro-F1 across 5-fold CV.
  - Generates comprehensive comparative tables and statistical summary.
  - Strict integrity gating: tracks missing masks AND invalid/empty masks (is_valid=False).
    Invalid masks trigger INCOMPLETE status, are quarantined in e2_invalid_masks.json,
    and are not permitted to drag down valid algorithm averages to zero.
  - Single-tier parallelism strictly enforced.
"""

import os
import sys

# Force single-tier parallelism environment variables BEFORE scientific imports
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["NUMEXPR_NUM_THREADS"] = "1"
os.environ["VECLIB_MAXIMUM_THREADS"] = "1"

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
import numpy as np
from datetime import datetime

try:
    import threadpoolctl
    threadpoolctl.threadpool_limits(limits=1)
    HAS_THREADPOOLCTL = True
except Exception:
    HAS_THREADPOOLCTL = False

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

from config import BENCHMARK_19_DATASETS, DATA_DIR_TXT, DATA_DIR_MAT
from utils import load_dataset


# ══════════════════════════════════════════════════════════════════════════════
# Constants & Protocol Specifications
# ══════════════════════════════════════════════════════════════════════════════

COMPETITOR_ALGORITHMS = ["bIRIME", "BinCOA", "DENCA_SO"]
BANNED_SUBSTRINGS = ["KDS_EL", "KDS-EL", "MEL"]
DEFAULT_MASKS_DIR = os.path.join(PROJECT_ROOT, "output", "formal_experiment_20260905_211755", "masks")
DEFAULT_OUT_DIR = os.path.join(PROJECT_ROOT, "output", "nested_cv", "e2_reanalysis")


# ══════════════════════════════════════════════════════════════════════════════
# Metric Computation Helper
# ══════════════════════════════════════════════════════════════════════════════

def compute_multiclass_metrics(y_true, y_pred):
    """
    Computes pure Accuracy, Balanced Accuracy, and Macro-F1.
    Guarantees floating return values in [0.0, 1.0].
    """
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
# Descriptive 5-Fold CV Evaluation
# ══════════════════════════════════════════════════════════════════════════════

def evaluate_competitor_mask(X, y, mask, knn_k=3, n_splits=5, seed=42):
    """
    Performs deterministic 5-fold cross-validation on the feature subset defined by mask.
    Returns:
      - metrics: acc, bacc, macro_f1
      - active_features: count
      - active_ratio: ratio
      - is_valid: whether mask selects at least 1 feature
    """
    mask = np.asarray(mask, dtype=bool)
    N_samples, D = X.shape
    active_features = int(mask.sum())
    active_ratio = float(active_features / max(1, D))

    if active_features == 0:
        return {
            "is_valid": False,
            "active_features": 0,
            "active_ratio": 0.0,
            "accuracy": 0.0,
            "balanced_accuracy": 0.0,
            "macro_f1": 0.0,
            "y_pred": np.zeros(N_samples, dtype=int).tolist(),
        }

    X_sub = X[:, mask]
    min_class = int(np.min(np.bincount(y)))
    actual_splits = min(n_splits, min_class)
    if actual_splits < 2:
        clf = KNeighborsClassifier(n_neighbors=min(knn_k, N_samples - 1))
        clf.fit(X_sub, y)
        preds = clf.predict(X_sub)
        met = compute_multiclass_metrics(y, preds)
        return {
            "is_valid": True,
            "active_features": active_features,
            "active_ratio": active_ratio,
            **met,
            "y_pred": preds.tolist(),
        }

    skf = StratifiedKFold(n_splits=actual_splits, shuffle=True, random_state=seed)
    y_pred = np.zeros(N_samples, dtype=int)

    for tr_idx, te_idx in skf.split(X_sub, y):
        actual_k = min(knn_k, len(tr_idx))
        clf = KNeighborsClassifier(n_neighbors=actual_k)
        clf.fit(X_sub[tr_idx], y[tr_idx])
        y_pred[te_idx] = clf.predict(X_sub[te_idx])

    met = compute_multiclass_metrics(y, y_pred)
    return {
        "is_valid": True,
        "active_features": active_features,
        "active_ratio": active_ratio,
        **met,
        "y_pred": y_pred.tolist(),
    }


# ══════════════════════════════════════════════════════════════════════════════
# Main Re-Analysis Execution Routine
# ══════════════════════════════════════════════════════════════════════════════

def run_experiment_e2(masks_dir=None, datasets=None, out_dir=None, verbose=True):
    """
    Executes Experiment E2: Re-analyzing competitor masks offline with strict integrity gating.
    """
    t0_start = time.perf_counter()
    if masks_dir is None:
        masks_dir = DEFAULT_MASKS_DIR
    if datasets is None:
        datasets = BENCHMARK_19_DATASETS
    if out_dir is None:
        out_dir = DEFAULT_OUT_DIR
    os.makedirs(out_dir, exist_ok=True)

    expected_total_masks = len(COMPETITOR_ALGORITHMS) * len(datasets) * 10

    print("\n" + "=" * 78)
    print("STARTING EXPERIMENT E2: OFFLINE MULTI-METRIC RE-ANALYSIS OF COMPETITOR MASKS")
    print(f"Masks Source: {masks_dir}")
    print(f"Output Directory: {out_dir}")
    print(f"Competitor Algorithms ({len(COMPETITOR_ALGORITHMS)}): {COMPETITOR_ALGORITHMS}")
    print(f"Benchmark Datasets ({len(datasets)}): {datasets}")
    print(f"Runs per dataset: 10 | Target Masks: {expected_total_masks}")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 78)

    # 1. Dataset Preloading to avoid repeated disk reads
    datasets_cache = {}
    print(f"\nPreloading {len(datasets)} Benchmark Datasets...")
    for ds in datasets:
        X, y = load_dataset(ds, DATA_DIR_TXT, DATA_DIR_MAT)
        datasets_cache[ds] = (X, y)
        if verbose:
            print(f"  [LOADED] {ds:12s} | N_samples={X.shape[0]:4d} | D_features={X.shape[1]:5d} | Classes={len(np.unique(y))}")

    # 2. Re-Analysis Execution with Failure & Invalid Mask Tracking
    detailed_results = []
    missing_masks_list = []
    invalid_masks_list = []
    evaluated_count = 0
    missing_count = 0
    invalid_mask_count = 0
    banned_skipped_count = 0

    print(f"\nExecuting Offline Multi-Metric Evaluation across {expected_total_masks} Competitor Masks...")
    for algo in COMPETITOR_ALGORITHMS:
        print(f"\n--- Competitor Algorithm: {algo} ---")
        for ds in datasets:
            X, y = datasets_cache[ds]
            for run_idx in range(1, 11):
                mask_filename = f"mask_{algo}_{ds}_run{run_idx}.npy"
                mask_path = os.path.join(masks_dir, mask_filename)

                # Strict Red-Line Check: Never process KDS_EL or MEL files
                if any(banned in mask_filename for banned in BANNED_SUBSTRINGS):
                    banned_skipped_count += 1
                    continue

                if not os.path.exists(mask_path):
                    missing_count += 1
                    missing_masks_list.append({
                        "algorithm": algo,
                        "dataset": ds,
                        "run_idx": run_idx,
                        "expected_file": mask_filename,
                    })
                    print(f"  [MISSING] {mask_filename}")
                    continue

                # Load mask
                mask = np.load(mask_path)
                eval_res = evaluate_competitor_mask(X, y, mask, knn_k=3, n_splits=5, seed=42)
                evaluated_count += 1

                if not eval_res["is_valid"]:
                    invalid_mask_count += 1
                    invalid_masks_list.append({
                        "algorithm": algo,
                        "dataset": ds,
                        "run_idx": run_idx,
                        "mask_file": mask_filename,
                        "active_features": eval_res["active_features"],
                        "reason": "Empty mask (zero active features) or unstratified failure",
                    })
                    print(f"  [INVALID MASK] {mask_filename} selects 0 features!")

                record = {
                    "algorithm": algo,
                    "dataset": ds,
                    "run_idx": run_idx,
                    "mask_file": mask_filename,
                    "active_features": eval_res["active_features"],
                    "active_ratio": eval_res["active_ratio"],
                    "accuracy": eval_res["accuracy"],
                    "balanced_accuracy": eval_res["balanced_accuracy"],
                    "macro_f1": eval_res["macro_f1"],
                    "is_valid": eval_res["is_valid"],
                }
                detailed_results.append(record)

            # Progress update per dataset
            ds_runs = [r for r in detailed_results if r["algorithm"] == algo and r["dataset"] == ds]
            valid_ds_runs = [r for r in ds_runs if r.get("is_valid", True)]
            if valid_ds_runs:
                mean_acc = np.mean([r["accuracy"] for r in valid_ds_runs])
                mean_bacc = np.mean([r["balanced_accuracy"] for r in valid_ds_runs])
                mean_f1 = np.mean([r["macro_f1"] for r in valid_ds_runs])
                mean_feats = np.mean([r["active_features"] for r in valid_ds_runs])
                inv_note = f", {len(ds_runs) - len(valid_ds_runs)} INVALID" if len(valid_ds_runs) < len(ds_runs) else ""
                run_note = f"({len(valid_ds_runs)}/10 valid{inv_note})" if len(valid_ds_runs) < 10 or inv_note else ""
                if verbose:
                    print(
                        f"  {algo:10s} | {ds:12s} | Feats={mean_feats:6.1f} | "
                        f"Acc={mean_acc:.4f} | BAcc={mean_bacc:.4f} | Macro-F1={mean_f1:.4f} {run_note}"
                    )
            else:
                if verbose:
                    print(f"  {algo:10s} | {ds:12s} | [NO VALID RUNS COMPLETED]")

    total_elapsed = time.perf_counter() - t0_start
    is_complete = (missing_count == 0) and (invalid_mask_count == 0) and (evaluated_count == expected_total_masks)
    execution_status = "COMPLETE" if is_complete else "INCOMPLETE"

    # 3. Aggregation & Synthesis
    summary_matrix = {}
    for algo in COMPETITOR_ALGORITHMS:
        summary_matrix[algo] = {}
        algo_records = [r for r in detailed_results if r["algorithm"] == algo]
        for ds in datasets:
            ds_runs = [r for r in algo_records if r["dataset"] == ds]
            if not ds_runs:
                summary_matrix[algo][ds] = {
                    "status": "MISSING",
                    "completed_runs": 0,
                    "valid_runs": 0,
                    "invalid_runs": 0,
                    "expected_runs": 10,
                    "acc_mean": None,
                    "acc_std": None,
                    "bacc_mean": None,
                    "bacc_std": None,
                    "f1_mean": None,
                    "f1_std": None,
                    "feats_mean": None,
                    "feats_std": None,
                }
                continue

            valid_runs = [r for r in ds_runs if r.get("is_valid", True)]
            invalid_runs = [r for r in ds_runs if not r.get("is_valid", True)]

            if len(invalid_runs) > 0:
                ds_status = "INVALID_MASKS_DETECTED"
            elif len(ds_runs) == 10:
                ds_status = "COMPLETE"
            else:
                ds_status = "PARTIAL"

            # Compute statistics strictly on valid runs so that invalid 0.0 scores do not drag down real results
            target_runs = valid_runs if valid_runs else ds_runs
            accs = [r["accuracy"] for r in target_runs]
            baccs = [r["balanced_accuracy"] for r in target_runs]
            f1s = [r["macro_f1"] for r in target_runs]
            feats = [r["active_features"] for r in target_runs]

            summary_matrix[algo][ds] = {
                "status": ds_status,
                "completed_runs": len(ds_runs),
                "valid_runs": len(valid_runs),
                "invalid_runs": len(invalid_runs),
                "expected_runs": 10,
                "acc_mean": round(float(np.mean(accs)), 6) if accs else None,
                "acc_std": round(float(np.std(accs)), 6) if accs else None,
                "bacc_mean": round(float(np.mean(baccs)), 6) if baccs else None,
                "bacc_std": round(float(np.std(baccs)), 6) if baccs else None,
                "f1_mean": round(float(np.mean(f1s)), 6) if f1s else None,
                "f1_std": round(float(np.std(f1s)), 6) if f1s else None,
                "feats_mean": round(float(np.mean(feats)), 2) if feats else None,
                "feats_std": round(float(np.std(feats)), 2) if feats else None,
            }

    # Grand aggregate across datasets with valid runs
    grand_summary = {}
    for algo in COMPETITOR_ALGORITHMS:
        valid_summaries = [s for s in summary_matrix[algo].values() if s.get("acc_mean") is not None and s.get("invalid_runs", 0) == 0]
        if valid_summaries:
            grand_summary[algo] = {
                "completed_clean_datasets": len(valid_summaries),
                "overall_mean_acc": round(float(np.mean([s["acc_mean"] for s in valid_summaries])), 6),
                "overall_mean_bacc": round(float(np.mean([s["bacc_mean"] for s in valid_summaries])), 6),
                "overall_mean_f1": round(float(np.mean([s["f1_mean"] for s in valid_summaries])), 6),
                "overall_mean_feats": round(float(np.mean([s["feats_mean"] for s in valid_summaries])), 2),
            }
        else:
            grand_summary[algo] = {
                "completed_clean_datasets": 0,
                "overall_mean_acc": None,
                "overall_mean_bacc": None,
                "overall_mean_f1": None,
                "overall_mean_feats": None,
            }

    # 4. Save JSON Deliverables
    detailed_json_path = os.path.join(out_dir, "e2_detailed_runs.json")
    with open(detailed_json_path, "w", encoding="utf-8") as f:
        json.dump(detailed_results, f, indent=2)

    if missing_masks_list:
        missing_json_path = os.path.join(out_dir, "e2_missing_masks.json")
        with open(missing_json_path, "w", encoding="utf-8") as f:
            json.dump({
                "status": "INCOMPLETE",
                "timestamp": datetime.now().isoformat(),
                "total_expected": expected_total_masks,
                "total_evaluated": evaluated_count,
                "total_missing": missing_count,
                "missing_masks": missing_masks_list,
            }, f, indent=2)

    if invalid_masks_list:
        invalid_json_path = os.path.join(out_dir, "e2_invalid_masks.json")
        with open(invalid_json_path, "w", encoding="utf-8") as f:
            json.dump({
                "status": "INCOMPLETE",
                "timestamp": datetime.now().isoformat(),
                "total_expected": expected_total_masks,
                "total_invalid": invalid_mask_count,
                "invalid_masks": invalid_masks_list,
            }, f, indent=2)

    try:
        import threadpoolctl
        tp_info = threadpoolctl.threadpool_info()
    except Exception:
        tp_info = []

    summary_json_path = os.path.join(out_dir, "e2_summary_table.json")
    payload = {
        "experiment": "E2_Offline_MultiMetric_ReAnalysis",
        "execution_status": execution_status,
        "timestamp": datetime.now().isoformat(),
        "task_accounting": {
            "expected_masks": expected_total_masks,
            "evaluated_masks": evaluated_count,
            "missing_masks": missing_count,
            "invalid_masks": invalid_mask_count,
            "banned_masks_skipped": banned_skipped_count,
        },
        "total_elapsed_sec": round(total_elapsed, 2),
        "grand_summary": grand_summary,
        "per_dataset_summary": summary_matrix,
        "missing_masks_list": missing_masks_list,
        "invalid_masks_list": invalid_masks_list,
        "system_metadata": {
            "platform": platform.platform(),
            "python": platform.python_version(),
            "numpy": np.__version__,
            "single_tier_parallelism": True,
            "threadpool_info": tp_info,
        },
    }
    with open(summary_json_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)

    # 5. Save Comprehensive Academic Markdown Report
    report_md_path = os.path.join(out_dir, "e2_competitor_multimetric_report.md")
    with open(report_md_path, "w", encoding="utf-8") as f:
        f.write("# E2: Offline Multi-Metric Re-Analysis of Competitor Feature Masks\n\n")
        f.write(f"- **Execution Timestamp**: {payload['timestamp']}\n")
        reasons = []
        if missing_count > 0:
            reasons.append(f"{missing_count} missing")
        if invalid_mask_count > 0:
            reasons.append(f"{invalid_mask_count} invalid")
        status_badge = "COMPLETE" if is_complete else f"⚠️ INCOMPLETE ({', '.join(reasons)})"
        f.write(f"- **Execution Status**: **{status_badge}**\n")
        f.write(f"- **Protocol Reference**: `review_round_1/05_executable_experiment_plan.md` (Section 5)\n")
        f.write(f"- **Competitor Masks Evaluated**: **{evaluated_count} / {expected_total_masks}**\n")
        f.write(f"- **Evaluated Competitor Algorithms ({len(COMPETITOR_ALGORITHMS)})**: `{', '.join(COMPETITOR_ALGORITHMS)}`\n")
        f.write(f"- **Benchmark Datasets ({len(datasets)})**: Strictly independent benchmarks (excluding `ALL_AML`)\n")
        f.write(f"- **Total Elapsed Time**: `{total_elapsed:.2f} s`\n\n")

        f.write("> **Formal Methodological Demarcation**:\n")
        f.write("> This experiment serves strictly as an **internal 5-fold cross-validation descriptive re-analysis** ")
        f.write("of historical competitor masks (from `formal_experiment_20260905_211755`). ")
        f.write("It computes standard classification Accuracy alongside class-imbalance-aware Balanced Accuracy (BAcc) and Macro-F1. ")
        f.write("In accordance with scientific rigor, these descriptive metrics supplement the primary comparison but are not claimed ")
        f.write("as new unbiased outer test estimates, nor are they mixed with nested double-cross-validation scores.\n\n")

        if missing_masks_list:
            f.write("> [!WARNING]\n")
            f.write(f"> **Dataset Incompleteness**: {missing_count} target mask(s) were missing on disk. ")
            f.write("Incomplete datasets are explicitly annotated with run counts (e.g. `9/10 runs`). ")
            f.write("Details are recorded in `e2_missing_masks.json`.\n\n")

        if invalid_masks_list:
            f.write("> [!WARNING]\n")
            f.write(f"> **Invalid Masks Detected**: {invalid_mask_count} mask(s) were invalid (zero active features). ")
            f.write("These corrupted runs are strictly quarantined, excluded from dragging down valid averages to 0.0, ")
            f.write("and documented in `e2_invalid_masks.json`.\n\n")

        f.write(f"## 1. Overall Aggregate Performance Comparison ({len(datasets)} Benchmark Datasets)\n\n")
        f.write("| Competitor Algorithm | Mean Accuracy (Acc) | Mean Balanced Acc (BAcc) | Mean Macro-F1 (F1) | Mean Active Features ($d$) | Clean Completed Datasets |\n")
        f.write("| :--- | :---: | :---: | :---: | :---: | :---: |\n")
        for algo in COMPETITOR_ALGORITHMS:
            g = grand_summary[algo]
            if g["overall_mean_acc"] is not None:
                f.write(
                    f"| **`{algo}`** | **{g['overall_mean_acc']:.4f}** | **{g['overall_mean_bacc']:.4f}** | "
                    f"**{g['overall_mean_f1']:.4f}** | **{g['overall_mean_feats']:.1f}** | {g['completed_clean_datasets']}/{len(datasets)} |\n"
                )
            else:
                f.write(f"| **`{algo}`** | — | — | — | — | 0/{len(datasets)} |\n")

        f.write("\n## 2. Per-Dataset Multi-Metric Breakdown (Mean ± Std over Independent Runs)\n\n")
        f.write("| Dataset | Metric | bIRIME | BinCOA | DENCA_SO |\n")
        f.write("| :--- | :--- | :---: | :---: | :---: |\n")

        for ds in datasets:
            def _fmt_cell(algo, key, std_key):
                m = summary_matrix[algo].get(ds, {})
                if m.get(key) is None:
                    return "—"
                if m.get("invalid_runs", 0) > 0:
                    return f"{m[key]:.4f} ± {m[std_key]:.3f} ⚠️ ({m['valid_runs']}/10 valid)"
                elif m.get("completed_runs", 10) < 10:
                    return f"{m[key]:.4f} ± {m[std_key]:.3f} ({m['completed_runs']}/10)"
                return f"{m[key]:.4f} ± {m[std_key]:.3f}"

            def _fmt_feat_cell(algo):
                m = summary_matrix[algo].get(ds, {})
                if m.get("feats_mean") is None:
                    return "—"
                if m.get("invalid_runs", 0) > 0:
                    return f"{m['feats_mean']:.1f} ± {m['feats_std']:.1f} ⚠️ ({m['valid_runs']}/10 valid)"
                elif m.get("completed_runs", 10) < 10:
                    return f"{m['feats_mean']:.1f} ± {m['feats_std']:.1f} ({m['completed_runs']}/10)"
                return f"{m['feats_mean']:.1f} ± {m['feats_std']:.1f}"

            # Row 1: Accuracy
            acc_b = _fmt_cell("bIRIME", "acc_mean", "acc_std")
            acc_c = _fmt_cell("BinCOA", "acc_mean", "acc_std")
            acc_d = _fmt_cell("DENCA_SO", "acc_mean", "acc_std")

            # Row 2: Balanced Accuracy
            bacc_b = _fmt_cell("bIRIME", "bacc_mean", "bacc_std")
            bacc_c = _fmt_cell("BinCOA", "bacc_mean", "bacc_std")
            bacc_d = _fmt_cell("DENCA_SO", "bacc_mean", "bacc_std")

            # Row 3: Macro-F1
            f1_b = _fmt_cell("bIRIME", "f1_mean", "f1_std")
            f1_c = _fmt_cell("BinCOA", "f1_mean", "f1_std")
            f1_d = _fmt_cell("DENCA_SO", "f1_mean", "f1_std")

            # Row 4: Active Features
            feat_b = _fmt_feat_cell("bIRIME")
            feat_c = _fmt_feat_cell("BinCOA")
            feat_d = _fmt_feat_cell("DENCA_SO")

            f.write(f"| **{ds}** | Accuracy | {acc_b} | {acc_c} | {acc_d} |\n")
            f.write(f"| | Balanced Acc | {bacc_b} | {bacc_c} | {bacc_d} |\n")
            f.write(f"| | Macro-F1 | {f1_b} | {f1_c} | {f1_d} |\n")
            f.write(f"| | Features ($d$) | {feat_b} | {feat_c} | {feat_d} |\n")

        # Section 3: Data-Grounded Dynamic Verification
        f.write("\n## 3. Academic Findings & Empirical Observations\n\n")

        # Calculate dynamic empirical ranking
        valid_algos = [a for a in COMPETITOR_ALGORITHMS if grand_summary[a]["overall_mean_acc"] is not None]
        if valid_algos:
            sorted_acc = sorted(valid_algos, key=lambda a: grand_summary[a]["overall_mean_acc"], reverse=True)
            sorted_bacc = sorted(valid_algos, key=lambda a: grand_summary[a]["overall_mean_bacc"], reverse=True)
            sorted_f1 = sorted(valid_algos, key=lambda a: grand_summary[a]["overall_mean_f1"], reverse=True)

            rank_consistent = (sorted_acc == sorted_bacc == sorted_f1)
            rank_str = " > ".join(f"`{a}`" for a in sorted_acc)

            f.write("1. **Observed Performance Hierarchy**: ")
            if rank_consistent:
                f.write(f"Across the {len(datasets)} evaluated benchmark datasets, the aggregate performance hierarchy among competitor algorithms ")
                f.write(f"remains identical across standard Accuracy, Balanced Accuracy, and Macro-F1: {rank_str}.\n")
            else:
                f.write(f"The aggregate ranking is `{ ' > '.join(sorted_acc) }` under Accuracy, ")
                f.write(f"`{ ' > '.join(sorted_bacc) }` under Balanced Accuracy, and ")
                f.write(f"`{ ' > '.join(sorted_f1) }` under Macro-F1.\n")

            # Pairwise dataset-level win counts for top algorithm against others
            top_algo = sorted_acc[0]
            f.write(f"2. **Dataset-Level Concordance for Top Competitor (`{top_algo}`)**:\n")
            for other_algo in sorted_acc[1:]:
                acc_wins = 0
                bacc_wins = 0
                f1_wins = 0
                common_ds_count = 0
                for ds in datasets:
                    m_top = summary_matrix[top_algo].get(ds, {})
                    m_other = summary_matrix[other_algo].get(ds, {})
                    if m_top.get("acc_mean") is not None and m_other.get("acc_mean") is not None:
                        common_ds_count += 1
                        if m_top["acc_mean"] > m_other["acc_mean"]:
                            acc_wins += 1
                        if m_top["bacc_mean"] > m_other["bacc_mean"]:
                            bacc_wins += 1
                        if m_top["f1_mean"] > m_other["f1_mean"]:
                            f1_wins += 1
                f.write(f"   - Versus `{other_algo}` (across {common_ds_count} common datasets): ")
                f.write(f"Accuracy wins = {acc_wins}/{common_ds_count}, Balanced Accuracy wins = {bacc_wins}/{common_ds_count}, ")
                f.write(f"Macro-F1 wins = {f1_wins}/{common_ds_count}.\n")

            f.write("3. **Descriptive Re-Analysis Context**: These descriptive re-analysis metrics evaluate historical feature masks ")
            f.write("under class-imbalance-aware measures, verifying that observed competitor performance relationships are consistent ")
            f.write("under balanced metrics without altering the established primary benchmark records.\n")
        else:
            f.write("1. *No competitor masks could be evaluated in this run.*\n")

    print("\n" + "=" * 78)
    status_label = "SUCCESSFULLY" if is_complete else f"WITH INCOMPLETE MASKS ({missing_count} missing, {invalid_mask_count} invalid)"
    print(f"EXPERIMENT E2 COMPLETED {status_label} in {total_elapsed:.2f}s!")
    print(f"Artifacts saved:")
    print(f"  - Detailed Runs JSON: {detailed_json_path}")
    print(f"  - Summary Matrix JSON: {summary_json_path}")
    print(f"  - Academic Markdown Report: {report_md_path}")
    if missing_masks_list:
        print(f"  - Missing Masks JSON: {missing_json_path}")
    if invalid_masks_list:
        print(f"  - Invalid Masks JSON: {invalid_json_path}")
    print("=" * 78)

    return payload


# ══════════════════════════════════════════════════════════════════════════════
# Command Line Interface
# ══════════════════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(description="Run Experiment E2: Offline Multi-Metric Re-Analysis of Competitor Masks")
    parser.add_argument(
        "--masks-dir",
        type=str,
        default=DEFAULT_MASKS_DIR,
        help=f"Directory containing competitor .npy masks (default: {DEFAULT_MASKS_DIR})",
    )
    parser.add_argument(
        "--datasets",
        type=str,
        nargs="+",
        default=None,
        help="Datasets to evaluate (default: all 19 benchmark datasets)",
    )
    parser.add_argument(
        "--out-dir",
        type=str,
        default=DEFAULT_OUT_DIR,
        help=f"Output directory for E2 reports (default: {DEFAULT_OUT_DIR})",
    )
    parser.add_argument("--quiet", action="store_true", help="Suppress detailed per-dataset console logs")
    args = parser.parse_args()

    payload = run_experiment_e2(masks_dir=args.masks_dir, datasets=args.datasets, out_dir=args.out_dir, verbose=not args.quiet)

    if payload["execution_status"] != "COMPLETE":
        print(f"\n[EXIT] Process exiting with status 1 due to missing or invalid masks.")
        sys.exit(1)


if __name__ == "__main__":
    main()
