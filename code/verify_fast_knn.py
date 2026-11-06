"""
Equivalence Verification Script: Candidate Fast 3-NN vs Authoritative Scikit-Learn 3-NN
=====================================================================================
Evaluates 100% numerical and rank equivalence across diverse benchmark datasets:
- Prediction vectors (y_pred)
- Accuracy, Balanced Accuracy, Macro-F1
- Solution rank ordering (Kendall's tau, Spearman's rho)
"""

import os
import sys
import numpy as np
from sklearn.model_selection import StratifiedKFold
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import balanced_accuracy_score, f1_score
from scipy.stats import kendalltau, spearmanr

# Ensure code/ is on path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from utils import load_dataset
from config import DATA_DIR_TXT, DATA_DIR_MAT


def sklearn_cv_evaluate(X, y, mask, k=3, cv_splits=5, random_state=42):
    """Authoritative Ground-Truth: Scikit-learn 3-NN across stratified folds."""
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
    macro_f1 = float(f1_score(y_arr, y_pred, average='macro', zero_division=0))
    return acc, bacc, macro_f1, y_pred


def candidate_fast_cv_evaluate(X, y, mask, k=3, cv_splits=5, random_state=42):
    """
    Candidate Fast 3-NN:
    - Maintains native float64 precision
    - Dynamic actual_k guard
    - Stable top-k sort & tie-breaking aligned with sklearn
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
        # Vectorized pairwise squared Euclidean distances (N_te x N_tr)
        dists = np.sum(X_te**2, axis=1, keepdims=True) + \
                np.sum(X_tr**2, axis=1, keepdims=True).T - \
                2.0 * np.dot(X_te, X_tr.T)
        dists = np.maximum(dists, 0.0)
        
        # Partition top-actual_k
        top_k_part = np.argpartition(dists, actual_k, axis=1)[:, :actual_k]
        part_dists = np.take_along_axis(dists, top_k_part, axis=1)
        local_sort = np.argsort(part_dists, axis=1)
        top_k_idx = np.take_along_axis(top_k_part, local_sort, axis=1)
        top_k_labels = y_tr[top_k_idx]
        
        # Majority voting
        for i in range(len(te)):
            counts = np.bincount(top_k_labels[i])
            y_pred[te[i]] = counts.argmax()
            
    acc = float(np.mean(y_pred == y_arr))
    bacc = float(balanced_accuracy_score(y_arr, y_pred))
    macro_f1 = float(f1_score(y_arr, y_pred, average='macro', zero_division=0))
    return acc, bacc, macro_f1, y_pred


def run_verification(dataset_name, num_masks=20, seed=42):
    print(f"\n==========================================")
    print(f"Running Equivalence Verification on: {dataset_name}")
    print(f"==========================================")
    
    X, y = load_dataset(dataset_name, DATA_DIR_TXT, DATA_DIR_MAT)
    N, D = X.shape
    print(f"Dataset shape: N={N}, D={D}, Classes={len(np.unique(y))}")
    
    rng = np.random.RandomState(seed)
    
    # Generate masks across 3 cardinality tiers: sparse, medium, dense
    masks = []
    for _ in range(num_masks // 3):
        # Sparse: 5 to 30 features
        k_feats = rng.randint(5, min(31, D))
        m = np.zeros(D, dtype=bool)
        m[rng.choice(D, k_feats, replace=False)] = True
        masks.append(m)
    for _ in range(num_masks // 3):
        # Medium: 50 to 200 features
        k_feats = rng.randint(min(50, D), min(201, D))
        m = np.zeros(D, dtype=bool)
        m[rng.choice(D, k_feats, replace=False)] = True
        masks.append(m)
    while len(masks) < num_masks:
        # Dense: 300 to 1000 features
        k_feats = rng.randint(min(300, D), min(1001, D))
        m = np.zeros(D, dtype=bool)
        m[rng.choice(D, k_feats, replace=False)] = True
        masks.append(m)
        
    skl_accs, skl_baccs, skl_f1s = [], [], []
    fast_accs, fast_baccs, fast_f1s = [], [], []
    pred_mismatches = 0
    total_preds = 0
    
    for idx, mask in enumerate(masks):
        acc_s, bacc_s, f1_s, preds_s = sklearn_cv_evaluate(X, y, mask)
        acc_f, bacc_f, f1_f, preds_f = candidate_fast_cv_evaluate(X, y, mask)
        
        skl_accs.append(acc_s)
        skl_baccs.append(bacc_s)
        skl_f1s.append(f1_s)
        
        fast_accs.append(acc_f)
        fast_baccs.append(bacc_f)
        fast_f1s.append(f1_f)
        
        diff = np.sum(preds_s != preds_f)
        pred_mismatches += diff
        total_preds += len(y)
        
    max_acc_diff = np.max(np.abs(np.array(skl_accs) - np.array(fast_accs)))
    max_bacc_diff = np.max(np.abs(np.array(skl_baccs) - np.array(fast_baccs)))
    max_f1_diff = np.max(np.abs(np.array(skl_f1s) - np.array(fast_f1s)))
    
    tau, _ = kendalltau(skl_accs, fast_accs)
    rho, _ = spearmanr(skl_accs, fast_accs)
    
    print(f"Total Sample Predictions Evaluated: {total_preds}")
    print(f"Prediction Mismatches: {pred_mismatches} ({pred_mismatches / total_preds * 100:.4f}%)")
    print(f"Max Absolute Acc Difference:      {max_acc_diff:.2e}")
    print(f"Max Absolute BAcc Difference:     {max_bacc_diff:.2e}")
    print(f"Max Absolute Macro-F1 Difference: {max_f1_diff:.2e}")
    print(f"Candidate Ranking Kendall's tau:  {tau:.6f}")
    print(f"Candidate Ranking Spearman's rho: {rho:.6f}")
    
    if pred_mismatches == 0 and max_acc_diff < 1e-12:
        print("[PASS] 100% Exact Numerical & Prediction Equivalence!")
        return True
    else:
        print("[FAIL/DIVERGENCE] Discrepancies detected between implementations!")
        return False


if __name__ == "__main__":
    test_datasets = ["Colon", "COIL20"]
    for ds in test_datasets:
        run_verification(ds, num_masks=15)
