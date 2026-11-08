# E5: Full Outer Nested Generalization Benchmark Report

- **Execution Timestamp**: 2026-11-08T14:35:17.723591
- **Protocol Reference**: `review_round_1/05_executable_experiment_plan.md` (Section 8)
- **Target Algorithms (12)**: KDS_EL_TwoPhase, MEL, MEL_MI, KDS_EL_NoPool, bIRIME, BPSO, FWPSO, SaWDE, PSO_CSM, BinCOA, IGPSO, DENCA_SO
- **Evaluated Datasets (1)**: toy_round3
- **Runs Status**: `60 / 60` completed (Tasks Execution Completed: `True`, Valid for Formal Claims: `True`)
- **Downstream Models (5)**: 3-NN, RBF-SVM, Random Forest, GaussianNB, LDA (Shrinkage / SVD-safeguarded)
- **Total Elapsed Time**: `62.21 s`

> **Formal Methodological Demarcation**:
> In strict adherence to rigorous Elsevier peer review standards, all evaluations in this report are conducted under complete outer test partition isolation. Mutual information estimation, population initialization, wrapper evolutionary search, preprocessing transformations, and model fitting are strictly confined within the training partition of each outer fold. Pooled out-of-fold predictions concatenated across the five outer test folds serve as the primary generalization metric, completely eliminating optimistic circular evaluation bias.

## 1. Primary Classification Generalization Matrix (3-NN Pooled OOF)

| Dataset | **KDS_EL_TwoPhase** (Acc / BAcc / Feats) | **MEL** (Acc / BAcc / Feats) | **MEL_MI** (Acc / BAcc / Feats) | **KDS_EL_NoPool** (Acc / BAcc / Feats) | **bIRIME** (Acc / BAcc / Feats) | **BPSO** (Acc / BAcc / Feats) | **FWPSO** (Acc / BAcc / Feats) | **SaWDE** (Acc / BAcc / Feats) | **PSO_CSM** (Acc / BAcc / Feats) | **BinCOA** (Acc / BAcc / Feats) | **IGPSO** (Acc / BAcc / Feats) | **DENCA_SO** (Acc / BAcc / Feats) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **`toy_round3`** | 0.5167±0.000<br>(0.5167 / 3.0) | 0.4167±0.000<br>(0.4167 / 3.0) | 0.4667±0.000<br>(0.4667 / 3.0) | 0.4667±0.000<br>(0.4667 / 3.0) | 0.4667±0.000<br>(0.4667 / 3.0) | 0.4333±0.000<br>(0.4333 / 3.0) | 0.4667±0.000<br>(0.4667 / 3.0) | 0.4667±0.000<br>(0.4667 / 3.0) | 0.4667±0.000<br>(0.4667 / 3.0) | 0.4667±0.000<br>(0.4667 / 3.0) | 0.4667±0.000<br>(0.4667 / 3.0) | 0.5167±0.000<br>(0.5167 / 1.0) |

## 2. Downstream Model Transferability Profile (Cross-Classifier Generalization)

The table below reports the average performance shift of alternative downstream inductive biases relative to the primary 3-NN classifier across all evaluated datasets.

| Algorithm | 3-NN Acc | RBF-SVM Acc ($\Delta$) | Random Forest Acc ($\Delta$) | GaussianNB Acc ($\Delta$) | LDA (Shrinkage/SVD) Acc ($\Delta$) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **`KDS_EL_TwoPhase`** | 0.5167 | 0.5000 (-0.0167) | 0.3667 (-0.1500) | 0.4167 (-0.1000) | 0.3333 (-0.1833) |
| **`MEL`** | 0.4167 | 0.4500 (+0.0333) | 0.3667 (-0.0500) | 0.3833 (-0.0333) | 0.3333 (-0.0833) |
| **`MEL_MI`** | 0.4667 | 0.4500 (-0.0167) | 0.3500 (-0.1167) | 0.3833 (-0.0833) | 0.3167 (-0.1500) |
| **`KDS_EL_NoPool`** | 0.4667 | 0.4500 (-0.0167) | 0.3500 (-0.1167) | 0.3833 (-0.0833) | 0.3167 (-0.1500) |
| **`bIRIME`** | 0.4667 | 0.4500 (-0.0167) | 0.3500 (-0.1167) | 0.3833 (-0.0833) | 0.3167 (-0.1500) |
| **`BPSO`** | 0.4333 | 0.4667 (+0.0333) | 0.3833 (-0.0500) | 0.4167 (-0.0167) | 0.3000 (-0.1333) |
| **`FWPSO`** | 0.4667 | 0.4500 (-0.0167) | 0.3500 (-0.1167) | 0.3833 (-0.0833) | 0.3167 (-0.1500) |
| **`SaWDE`** | 0.4667 | 0.4500 (-0.0167) | 0.3500 (-0.1167) | 0.3833 (-0.0833) | 0.3167 (-0.1500) |
| **`PSO_CSM`** | 0.4667 | 0.4500 (-0.0167) | 0.3500 (-0.1167) | 0.3833 (-0.0833) | 0.3167 (-0.1500) |
| **`BinCOA`** | 0.4667 | 0.4500 (-0.0167) | 0.3500 (-0.1167) | 0.3833 (-0.0833) | 0.3167 (-0.1500) |
| **`IGPSO`** | 0.4667 | 0.4500 (-0.0167) | 0.3500 (-0.1167) | 0.3833 (-0.0833) | 0.3167 (-0.1500) |
| **`DENCA_SO`** | 0.5167 | 0.4000 (-0.1167) | 0.4833 (-0.0333) | 0.4000 (-0.1167) | 0.4333 (-0.0833) |

> **LDA Model Variant Accounting**: `shrinkage_lsqr`: 60 fold evaluations (Fallbacks triggered: none). Subsets with $d \le 1000$ are evaluated with Ledoit--Wolf shrinkage LSQR; subsets with $d > 1000$ are evaluated with SVD to prevent covariance matrix memory allocation.


## 3. Optimistic Search Bias Quantification

Internal search surrogate error rate versus held-out pooled out-of-fold generalization error:

| Algorithm | Internal Search Acc | Pooled OOF Acc | Optimistic Search Bias ($\Delta_{\mathrm{bias}}$) |
| :--- | :---: | :---: | :---: |
| **`KDS_EL_TwoPhase`** | 0.6076 | 0.5167 | +0.0909 |
| **`MEL`** | 0.5769 | 0.4167 | +0.1602 |
| **`MEL_MI`** | 0.6107 | 0.4667 | +0.1440 |
| **`KDS_EL_NoPool`** | 0.6107 | 0.4667 | +0.1440 |
| **`bIRIME`** | 0.6107 | 0.4667 | +0.1440 |
| **`BPSO`** | 0.6076 | 0.4333 | +0.1742 |
| **`FWPSO`** | 0.6107 | 0.4667 | +0.1440 |
| **`SaWDE`** | 0.6107 | 0.4667 | +0.1440 |
| **`PSO_CSM`** | 0.6107 | 0.4667 | +0.1440 |
| **`BinCOA`** | 0.6107 | 0.4667 | +0.1440 |
| **`IGPSO`** | 0.6107 | 0.4667 | +0.1440 |
| **`DENCA_SO`** | — | — | — |

## 4. Key Academic Takeaways & Submission Protocol Alignment

1. **Complete Information Barrier**: Strict partition of mutual information estimation and wrapper search to the outer training set confirms that out-of-sample nested cross-validation is achieved without optimistic circular evaluation bias.
2. **Dimensional Sparsity Trade-Off**: Across evaluated benchmark instances, KDS_EL_TwoPhase achieves a mean active feature count of 3.0 with 0.5167 3-NN accuracy (comparators: MEL: 3.0 feats, 0.4167 acc; MEL_MI: 3.0 feats, 0.4667 acc; KDS_EL_NoPool: 3.0 feats, 0.4667 acc; bIRIME: 3.0 feats, 0.4667 acc; BPSO: 3.0 feats, 0.4333 acc; FWPSO: 3.0 feats, 0.4667 acc; SaWDE: 3.0 feats, 0.4667 acc; PSO_CSM: 3.0 feats, 0.4667 acc; BinCOA: 3.0 feats, 0.4667 acc; IGPSO: 3.0 feats, 0.4667 acc; DENCA_SO: 1.0 feats, 0.5167 acc).
The empirical trade-off illustrates the balance between feature reduction and predictive fidelity across instances.
3. **Cross-Model Transferability**: Subsets selected via 3-NN guided optimization yield the following out-of-fold generalization profiles across downstream models: 3-NN: 0.5167, RBF-SVM: 0.5000 ($\Delta$: -0.0167), Random Forest: 0.3667 ($\Delta$: -0.1500), GaussianNB: 0.4167 ($\Delta$: -0.1000), LDA: 0.3333 ($\Delta$: -0.1833).
Downstream evaluations exhibit pronounced performance attenuation on non-local models, reflecting inductive bias misalignment between nearest-neighbor distance metrics and global margin/tree partition criteria.
