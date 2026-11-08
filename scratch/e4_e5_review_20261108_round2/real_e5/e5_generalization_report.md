# E5: Full Outer Nested Generalization Benchmark Report

- **Execution Timestamp**: 2026-11-08T14:15:26.847567
- **Protocol Reference**: `review_round_1/05_executable_experiment_plan.md` (Section 8)
- **Target Algorithms (5)**: KDS_EL_TwoPhase, MEL, MEL_MI, KDS_EL_NoPool, bIRIME
- **Evaluated Datasets (1)**: toy_round2
- **Runs Status**: `25 / 25` completed (Tasks Execution Completed: `True`, Valid for Formal Claims: `False`)
- **Downstream Models (5)**: 3-NN, RBF-SVM, Random Forest, GaussianNB, LDA (Shrinkage / SVD-safeguarded)
- **Total Elapsed Time**: `13.38 s`

> [!WARNING] Incomplete / Diagnostic Execution Notice
> Only 25 of 25 planned runs finished (valid for formal claims: `False`). Incomplete outer folds (< 5), unverified audits, or incomplete seeds cannot serve as formal empirical claims in publication.

> **Formal Methodological Demarcation**:
> In strict adherence to rigorous Elsevier peer review standards, all evaluations in this report are conducted under complete outer test partition isolation. Mutual information estimation, population initialization, wrapper evolutionary search, preprocessing transformations, and model fitting are strictly confined within the training partition of each outer fold. Pooled out-of-fold predictions concatenated across the five outer test folds serve as the primary generalization metric, completely eliminating optimistic circular evaluation bias.

## 1. Primary Classification Generalization Matrix (3-NN Pooled OOF)

| Dataset | **KDS_EL_TwoPhase** (Acc / BAcc / Feats) | **MEL** (Acc / BAcc / Feats) | **MEL_MI** (Acc / BAcc / Feats) | **KDS_EL_NoPool** (Acc / BAcc / Feats) | **bIRIME** (Acc / BAcc / Feats) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **`toy_round2`** | 0.5167±0.000<br>(0.5167 / 3.0) | 0.4167±0.000<br>(0.4167 / 3.0) | 0.4667±0.000<br>(0.4667 / 3.0) | 0.4667±0.000<br>(0.4667 / 3.0) | 0.4667±0.000<br>(0.4667 / 3.0) |

## 2. Downstream Model Transferability Profile (Cross-Classifier Generalization)

The table below reports the average performance shift of alternative downstream inductive biases relative to the primary 3-NN classifier across all evaluated datasets.

| Algorithm | 3-NN Acc | RBF-SVM Acc ($\Delta$) | Random Forest Acc ($\Delta$) | GaussianNB Acc ($\Delta$) | LDA (Shrinkage/SVD) Acc ($\Delta$) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **`KDS_EL_TwoPhase`** | 0.5167 | 0.5000 (-0.0167) | 0.3667 (-0.1500) | 0.4167 (-0.1000) | 0.3333 (-0.1833) |
| **`MEL`** | 0.4167 | 0.4500 (+0.0333) | 0.3667 (-0.0500) | 0.3833 (-0.0333) | 0.3333 (-0.0833) |
| **`MEL_MI`** | 0.4667 | 0.4500 (-0.0167) | 0.3500 (-0.1167) | 0.3833 (-0.0833) | 0.3167 (-0.1500) |
| **`KDS_EL_NoPool`** | 0.4667 | 0.4500 (-0.0167) | 0.3500 (-0.1167) | 0.3833 (-0.0833) | 0.3167 (-0.1500) |
| **`bIRIME`** | 0.4667 | 0.4500 (-0.0167) | 0.3500 (-0.1167) | 0.3833 (-0.0833) | 0.3167 (-0.1500) |

## 3. Optimistic Search Bias Quantification

Internal search surrogate error rate versus held-out pooled out-of-fold generalization error:

| Algorithm | Internal Search Acc | Pooled OOF Acc | Optimistic Search Bias ($\Delta_{\mathrm{bias}}$) |
| :--- | :---: | :---: | :---: |
| **`KDS_EL_TwoPhase`** | 0.6076 | 0.5167 | +0.0909 |
| **`MEL`** | 0.5769 | 0.4167 | +0.1602 |
| **`MEL_MI`** | 0.6107 | 0.4667 | +0.1440 |
| **`KDS_EL_NoPool`** | 0.6107 | 0.4667 | +0.1440 |
| **`bIRIME`** | 0.6107 | 0.4667 | +0.1440 |

## 4. Key Academic Takeaways & Submission Protocol Alignment

> [!NOTE] Diagnostic Notice: Insufficient / Incomplete Data for Formal Claims
> The current execution is diagnostic, partial, or incomplete. In accordance with strict Elsevier submission protocols and AGENTS.md, formal academic takeaways regarding out-of-fold generalization, multi-objective trade-offs, and inductive bias transferability are withheld until full 5-fold evaluation with complete audit verification is executed.
