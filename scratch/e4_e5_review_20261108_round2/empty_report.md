# E5: Full Outer Nested Generalization Benchmark Report

- **Execution Timestamp**: 2026-11-08T14:15:27.927994
- **Protocol Reference**: `review_round_1/05_executable_experiment_plan.md` (Section 8)
- **Target Algorithms (1)**: KDS_EL_TwoPhase
- **Evaluated Datasets (1)**: toy_round2
- **Runs Status**: `0 / 5` completed (Tasks Execution Completed: `False`, Valid for Formal Claims: `False`)
- **Downstream Models (5)**: 3-NN, RBF-SVM, Random Forest, GaussianNB, LDA (Shrinkage / SVD-safeguarded)
- **Total Elapsed Time**: `0.00 s`

> [!WARNING] Incomplete / Diagnostic Execution Notice
> Only 0 of 5 planned runs finished (valid for formal claims: `False`). Incomplete outer folds (< 5), unverified audits, or incomplete seeds cannot serve as formal empirical claims in publication.

> **Formal Methodological Demarcation**:
> In strict adherence to rigorous Elsevier peer review standards, all evaluations in this report are conducted under complete outer test partition isolation. Mutual information estimation, population initialization, wrapper evolutionary search, preprocessing transformations, and model fitting are strictly confined within the training partition of each outer fold. Pooled out-of-fold predictions concatenated across the five outer test folds serve as the primary generalization metric, completely eliminating optimistic circular evaluation bias.

## 1. Primary Classification Generalization Matrix (3-NN Pooled OOF)

| Dataset | **KDS_EL_TwoPhase** (Acc / BAcc / Feats) |
| :--- | :---: |
| **`toy_round2`** | — |

## 2. Downstream Model Transferability Profile (Cross-Classifier Generalization)

The table below reports the average performance shift of alternative downstream inductive biases relative to the primary 3-NN classifier across all evaluated datasets.

| Algorithm | 3-NN Acc | RBF-SVM Acc ($\Delta$) | Random Forest Acc ($\Delta$) | GaussianNB Acc ($\Delta$) | LDA (Shrinkage/SVD) Acc ($\Delta$) |
| :--- | :---: | :---: | :---: | :---: | :---: |

## 3. Optimistic Search Bias Quantification

Internal search surrogate error rate versus held-out pooled out-of-fold generalization error:

| Algorithm | Internal Search Acc | Pooled OOF Acc | Optimistic Search Bias ($\Delta_{\mathrm{bias}}$) |
| :--- | :---: | :---: | :---: |
| **`KDS_EL_TwoPhase`** | — | — | — |

## 4. Key Academic Takeaways & Submission Protocol Alignment

> [!NOTE] Diagnostic Notice: Insufficient / Incomplete Data for Formal Claims
> The current execution is diagnostic, partial, or incomplete. In accordance with strict Elsevier submission protocols and AGENTS.md, formal academic takeaways regarding out-of-fold generalization, multi-objective trade-offs, and inductive bias transferability are withheld until full 5-fold evaluation with complete audit verification is executed.
