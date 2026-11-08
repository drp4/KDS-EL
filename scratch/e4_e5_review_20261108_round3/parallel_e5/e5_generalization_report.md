# E5: Full Outer Nested Generalization Benchmark Report

- **Execution Timestamp**: 2026-11-08T14:37:01.478513
- **Protocol Reference**: `review_round_1/05_executable_experiment_plan.md` (Section 8)
- **Target Algorithms (2)**: KDS_EL_TwoPhase, DENCA_SO
- **Evaluated Datasets (1)**: toy_parallel
- **Runs Status**: `4 / 4` completed (Tasks Execution Completed: `True`, Valid for Formal Claims: `False`)
- **Downstream Models (5)**: 3-NN, RBF-SVM, Random Forest, GaussianNB, LDA (Shrinkage / SVD-safeguarded)
- **Total Elapsed Time**: `6.65 s`

> [!WARNING] Incomplete / Diagnostic Execution Notice
> Only 4 of 4 planned runs finished (valid for formal claims: `False`). Incomplete outer folds (< 5), unverified audits, or incomplete seeds cannot serve as formal empirical claims in publication.

> **Formal Methodological Demarcation**:
> In strict adherence to rigorous Elsevier peer review standards, all evaluations in this report are conducted under complete outer test partition isolation. Mutual information estimation, population initialization, wrapper evolutionary search, preprocessing transformations, and model fitting are strictly confined within the training partition of each outer fold. Pooled out-of-fold predictions concatenated across the five outer test folds serve as the primary generalization metric, completely eliminating optimistic circular evaluation bias.

## 1. Primary Classification Generalization Matrix (3-NN Pooled OOF)

| Dataset | **KDS_EL_TwoPhase** (Acc / BAcc / Feats) | **DENCA_SO** (Acc / BAcc / Feats) |
| :--- | :---: | :---: |
| **`toy_parallel`** | 0.5833±0.000<br>(0.5833 / 3.0) | 0.4583±0.000<br>(0.4583 / 1.0) |

## 2. Downstream Model Transferability Profile (Cross-Classifier Generalization)

The table below reports the average performance shift of alternative downstream inductive biases relative to the primary 3-NN classifier across all evaluated datasets.

| Algorithm | 3-NN Acc | RBF-SVM Acc ($\Delta$) | Random Forest Acc ($\Delta$) | GaussianNB Acc ($\Delta$) | LDA (Shrinkage/SVD) Acc ($\Delta$) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **`KDS_EL_TwoPhase`** | 0.5833 | 0.5000 (-0.0833) | 0.3750 (-0.2083) | 0.2917 (-0.2917) | 0.2917 (-0.2917) |
| **`DENCA_SO`** | 0.4583 | 0.3750 (-0.0833) | 0.3750 (-0.0833) | 0.2500 (-0.2083) | 0.3333 (-0.1250) |

> **LDA Model Variant Accounting**: `shrinkage_lsqr`: 4 fold evaluations (Fallbacks triggered: none). Subsets with $d \le 1000$ are evaluated with Ledoit--Wolf shrinkage LSQR; subsets with $d > 1000$ are evaluated with SVD to prevent covariance matrix memory allocation.


## 3. Optimistic Search Bias Quantification

Internal search surrogate error rate versus held-out pooled out-of-fold generalization error:

| Algorithm | Internal Search Acc | Pooled OOF Acc | Optimistic Search Bias ($\Delta_{\mathrm{bias}}$) |
| :--- | :---: | :---: | :---: |
| **`KDS_EL_TwoPhase`** | 0.6133 | 0.5833 | +0.0300 |
| **`DENCA_SO`** | — | — | — |

## 4. Key Academic Takeaways & Submission Protocol Alignment

> [!NOTE] Diagnostic Notice: Insufficient / Incomplete Data for Formal Claims
> The current execution is diagnostic, partial, or incomplete. In accordance with strict Elsevier submission protocols and AGENTS.md, formal academic takeaways regarding out-of-fold generalization, multi-objective trade-offs, and inductive bias transferability are withheld until full 5-fold evaluation with complete audit verification is executed.
