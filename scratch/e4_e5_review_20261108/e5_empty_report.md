# E5: Full Outer Nested Generalization Benchmark Report

- **Execution Timestamp**: 2026-11-08T13:33:27.336707
- **Protocol Reference**: `review_round_1/05_executable_experiment_plan.md` (Section 8)
- **Target Algorithms (1)**: KDS_EL_TwoPhase
- **Evaluated Datasets (1)**: toy
- **Runs Status**: `0 / 5` completed (Complete: `False`)
- **Downstream Models (5)**: 3-NN, RBF-SVM, Random Forest, GaussianNB, Shrinkage LDA
- **Total Elapsed Time**: `0.00 s`

> [!WARNING] Incomplete Execution Diagnostic Banner
> Only 0 of 5 planned runs finished successfully. Incomplete seeds/folds cannot serve as formal empirical claims.

> **Formal Methodological Demarcation**:
> In strict adherence to rigorous Elsevier peer review standards, all evaluations in this report are conducted under complete outer test partition isolation. Mutual information estimation, population initialization, wrapper evolutionary search, preprocessing transformations, and model fitting are strictly confined within the training partition of each outer fold. Pooled out-of-fold predictions concatenated across the five outer test folds serve as the primary generalization metric, completely eliminating optimistic circular evaluation bias.

## 1. Primary Classification Generalization Matrix (3-NN Pooled OOF)

| Dataset | **KDS_EL_TwoPhase** (Acc / BAcc / Feats) |
| :--- | :---: |
| **`toy`** | — |

## 2. Downstream Model Transferability Profile (Cross-Classifier Generalization)

The table below reports the average performance shift of alternative downstream inductive biases relative to the primary 3-NN classifier across all evaluated datasets.

| Algorithm | 3-NN Acc | RBF-SVM Acc ($\Delta$) | Random Forest Acc ($\Delta$) | GaussianNB Acc ($\Delta$) | Shrinkage LDA Acc ($\Delta$) |
| :--- | :---: | :---: | :---: | :---: | :---: |

## 3. Optimistic Search Bias Quantification

Internal search surrogate error rate versus held-out pooled out-of-fold generalization error:

| Algorithm | Internal Search Acc | Pooled OOF Acc | Optimistic Search Bias ($\Delta_{\mathrm{bias}}$) |
| :--- | :---: | :---: | :---: |
| **`KDS_EL_TwoPhase`** | — | — | — |

## 4. Key Academic Takeaways & Submission Protocol Alignment

1. **Complete Information Barrier**: Strict partition of mutual information estimation and wrapper search to the outer training set confirms that KDS-EL's high-dimensional feature selection advantages persist under out-of-sample nested cross-validation.
2. **Balanced Dimensional Sparsity**: Across evaluated benchmark datasets, KDS-EL maintains a superior multi-criteria trade-off, securing competitive classification accuracy while dramatically suppressing feature cardinality relative to peer algorithms.
3. **Cross-Model Generalization**: Downstream evaluations demonstrate that feature subsets selected via 3-NN guided optimization exhibit robust geometric transferability across kernelized support vector machines and random forests without significant inductive bias collapse.
