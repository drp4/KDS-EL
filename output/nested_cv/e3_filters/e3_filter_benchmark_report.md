# E3: Classical Filter Fold-Internal Benchmark & Pareto Front Analysis

- **Execution Timestamp**: 2026-11-08T14:19:23.312068
- **Execution Status**: **COMPLETE**
- **Protocol Reference**: `review_round_1/05_executable_experiment_plan.md` (Section 6)
- **Evaluated Filters (4)**: `Top-k MI, Two-Stage mRMR, ReliefF, LASSO`
- **Target Benchmark Datasets (19)**: Outer 5 Folds, Pooled OOF
- **Common Completed Datasets**: **19 / 19**
- **Task Accounting**: 76 / 76 completed (0 failed)
- **Total Elapsed Time**: `3490.92 s`

> **Formal Methodological Demarcation**:
> In strict compliance with zero-leakage protocols, all filter algorithms were fitted exclusively on the outer training fold without any access to the outer test set. Performance metrics are reported via Pooled Out-Of-Fold (OOF) predictions across the 5 outer folds, providing a clean empirical baseline for fold-internal feature selection across candidate cardinality budgets.

## 1. Overall Aggregate Performance Comparison (across 19 Common Datasets)

| Filter Algorithm | Feature Budget ($k$) | Mean Accuracy | Mean Balanced Acc | Mean Macro-F1 | Datasets |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Top-k MI** | $k = 20$ | **0.8627** | 0.8512 | 0.8495 | 19 |
| **Top-k MI** | $k = 50$ | **0.8726** | 0.8608 | 0.8600 | 19 |
| **Top-k MI** | $k = 100$ | **0.8801** | 0.8680 | 0.8662 | 19 |
| **Two-Stage mRMR** | $k = 20$ | **0.8414** | 0.8276 | 0.8238 | 19 |
| **Two-Stage mRMR** | $k = 50$ | **0.8685** | 0.8597 | 0.8573 | 19 |
| **Two-Stage mRMR** | $k = 100$ | **0.8797** | 0.8701 | 0.8674 | 19 |
| **ReliefF** | $k = 20$ | **0.8456** | 0.8325 | 0.8201 | 19 |
| **ReliefF** | $k = 50$ | **0.8538** | 0.8379 | 0.8291 | 19 |
| **ReliefF** | $k = 100$ | **0.8672** | 0.8482 | 0.8460 | 19 |
| **LASSO** | $k = 20$ | **0.8754** | 0.8630 | 0.8635 | 19 |
| **LASSO** | $k = 50$ | **0.8824** | 0.8669 | 0.8685 | 19 |
| **LASSO** | $k = 100$ | **0.8943** | 0.8815 | 0.8818 | 19 |

## 2. Benchmark Primary Grid Breakdown ($k \in [20, 50, 100] $)

| Dataset | Metric | Top-k MI (20/50/100) | Two-Stage mRMR (20/50/100) | ReliefF (20/50/100) | LASSO (20/50/100) |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **ALL1** | Accuracy | 1.000/1.000/1.000 | 1.000/1.000/1.000 | 1.000/1.000/1.000 | 1.000/1.000/1.000 |
| | Balanced Acc | 1.000/1.000/1.000 | 1.000/1.000/1.000 | 1.000/1.000/1.000 | 1.000/1.000/1.000 |
| | Macro-F1 | 1.000/1.000/1.000 | 1.000/1.000/1.000 | 1.000/1.000/1.000 | 1.000/1.000/1.000 |
| **ALL4** | Accuracy | 0.828/0.774/0.849 | 0.796/0.774/0.796 | 0.871/0.871/0.860 | 0.882/0.828/0.860 |
| | Balanced Acc | 0.822/0.761/0.837 | 0.729/0.773/0.823 | 0.852/0.863/0.809 | 0.859/0.810/0.844 |
| | Macro-F1 | 0.800/0.739/0.821 | 0.737/0.744/0.775 | 0.843/0.847/0.820 | 0.855/0.796/0.832 |
| **Adenoma** | Accuracy | 0.972/0.972/0.972 | 0.917/0.972/0.972 | 0.972/0.972/0.972 | 0.972/0.972/0.972 |
| | Balanced Acc | 0.972/0.972/0.972 | 0.917/0.972/0.972 | 0.972/0.972/0.972 | 0.972/0.972/0.972 |
| | Macro-F1 | 0.972/0.972/0.972 | 0.916/0.972/0.972 | 0.972/0.972/0.972 | 0.972/0.972/0.972 |
| **BASEHOCK** | Accuracy | 0.881/0.903/0.912 | 0.746/0.826/0.879 | 0.565/0.638/0.690 | 0.871/0.887/0.896 |
| | Balanced Acc | 0.881/0.903/0.912 | 0.747/0.827/0.879 | 0.566/0.639/0.690 | 0.871/0.887/0.896 |
| | Macro-F1 | 0.880/0.902/0.911 | 0.731/0.822/0.878 | 0.483/0.604/0.675 | 0.869/0.886/0.895 |
| **COIL20** | Accuracy | 0.881/0.938/0.968 | 0.947/0.986/0.990 | 0.772/0.824/0.914 | 0.976/0.991/0.994 |
| | Balanced Acc | 0.881/0.938/0.968 | 0.947/0.986/0.990 | 0.772/0.824/0.914 | 0.976/0.991/0.994 |
| | Macro-F1 | 0.876/0.937/0.968 | 0.946/0.986/0.990 | 0.755/0.812/0.912 | 0.976/0.991/0.994 |
| **Colon** | Accuracy | 0.855/0.887/0.887 | 0.871/0.823/0.871 | 0.887/0.871/0.855 | 0.855/0.887/0.887 |
| | Balanced Acc | 0.836/0.872/0.872 | 0.849/0.791/0.849 | 0.872/0.859/0.836 | 0.836/0.872/0.872 |
| | Macro-F1 | 0.840/0.875/0.875 | 0.856/0.800/0.856 | 0.875/0.859/0.840 | 0.840/0.875/0.875 |
| **DLBCL** | Accuracy | 0.935/0.974/0.961 | 0.909/0.961/0.961 | 0.948/0.961/0.948 | 0.935/0.935/0.974 |
| | Balanced Acc | 0.922/0.983/0.974 | 0.940/0.974/0.974 | 0.948/0.956/0.948 | 0.904/0.886/0.983 |
| | Macro-F1 | 0.914/0.966/0.950 | 0.890/0.950/0.950 | 0.932/0.948/0.932 | 0.911/0.908/0.966 |
| **Gastric** | Accuracy | 0.908/0.892/0.908 | 0.892/0.938/0.908 | 0.892/0.877/0.892 | 0.923/0.892/0.908 |
| | Balanced Acc | 0.903/0.889/0.907 | 0.889/0.938/0.903 | 0.893/0.875/0.889 | 0.917/0.889/0.907 |
| | Macro-F1 | 0.906/0.891/0.907 | 0.891/0.938/0.906 | 0.891/0.875/0.891 | 0.921/0.891/0.907 |
| **Gastric1** | Accuracy | 0.938/0.944/0.944 | 0.944/0.951/0.951 | 0.938/0.951/0.951 | 0.944/0.951/0.951 |
| | Balanced Acc | 0.938/0.944/0.944 | 0.944/0.951/0.951 | 0.938/0.951/0.951 | 0.944/0.951/0.951 |
| | Macro-F1 | 0.937/0.944/0.944 | 0.944/0.951/0.951 | 0.937/0.951/0.951 | 0.944/0.951/0.951 |
| **Gastric2** | Accuracy | 0.992/0.976/0.960 | 0.960/0.984/0.984 | 0.968/0.952/0.960 | 0.952/0.968/0.960 |
| | Balanced Acc | 0.992/0.976/0.960 | 0.960/0.984/0.984 | 0.968/0.952/0.960 | 0.952/0.968/0.960 |
| | Macro-F1 | 0.992/0.976/0.960 | 0.960/0.984/0.984 | 0.968/0.952/0.960 | 0.952/0.968/0.960 |
| **ISOLET** | Accuracy | 0.570/0.629/0.733 | 0.708/0.787/0.820 | 0.621/0.692/0.754 | 0.719/0.853/0.882 |
| | Balanced Acc | 0.570/0.629/0.733 | 0.708/0.787/0.820 | 0.621/0.692/0.754 | 0.719/0.853/0.882 |
| | Macro-F1 | 0.566/0.628/0.731 | 0.706/0.787/0.821 | 0.620/0.689/0.753 | 0.717/0.853/0.882 |
| **Leukaemia** | Accuracy | 0.958/0.944/0.944 | 0.958/0.972/0.958 | 0.944/0.931/0.944 | 0.958/0.944/0.944 |
| | Balanced Acc | 0.959/0.939/0.939 | 0.949/0.969/0.949 | 0.939/0.919/0.929 | 0.959/0.939/0.939 |
| | Macro-F1 | 0.954/0.939/0.939 | 0.954/0.969/0.954 | 0.939/0.923/0.938 | 0.954/0.939/0.939 |
| **Lymphoma** | Accuracy | 0.933/0.933/0.933 | 0.889/0.911/0.911 | 0.933/0.956/0.933 | 0.933/0.933/0.933 |
| | Balanced Acc | 0.932/0.932/0.932 | 0.888/0.910/0.910 | 0.932/0.955/0.932 | 0.932/0.932/0.932 |
| | Macro-F1 | 0.933/0.933/0.933 | 0.889/0.911/0.911 | 0.933/0.955/0.933 | 0.933/0.933/0.933 |
| **Myeloma** | Accuracy | 0.775/0.815/0.763 | 0.769/0.827/0.775 | 0.798/0.792/0.786 | 0.803/0.821/0.832 |
| | Balanced Acc | 0.612/0.637/0.574 | 0.578/0.686/0.591 | 0.606/0.551/0.537 | 0.651/0.641/0.638 |
| | Macro-F1 | 0.622/0.659/0.581 | 0.586/0.705/0.602 | 0.622/0.549/0.527 | 0.666/0.665/0.667 |
| **PCMAC** | Accuracy | 0.792/0.831/0.812 | 0.704/0.774/0.813 | 0.528/0.542/0.656 | 0.831/0.838/0.840 |
| | Balanced Acc | 0.790/0.830/0.811 | 0.700/0.772/0.811 | 0.523/0.538/0.653 | 0.829/0.837/0.839 |
| | Macro-F1 | 0.783/0.827/0.808 | 0.675/0.763/0.807 | 0.402/0.450/0.637 | 0.826/0.835/0.838 |
| **Prostate** | Accuracy | 0.922/0.922/0.922 | 0.941/0.931/0.922 | 0.922/0.931/0.912 | 0.912/0.931/0.941 |
| | Balanced Acc | 0.922/0.922/0.922 | 0.942/0.932/0.922 | 0.922/0.932/0.912 | 0.912/0.932/0.942 |
| | Macro-F1 | 0.922/0.922/0.922 | 0.941/0.931/0.922 | 0.922/0.931/0.912 | 0.912/0.931/0.941 |
| **SRBCT** | Accuracy | 0.976/0.976/0.976 | 0.928/0.964/0.976 | 0.952/0.976/0.976 | 0.964/0.988/0.988 |
| | Balanced Acc | 0.977/0.977/0.977 | 0.943/0.969/0.977 | 0.957/0.977/0.977 | 0.973/0.986/0.986 |
| | Macro-F1 | 0.979/0.979/0.979 | 0.938/0.963/0.979 | 0.948/0.973/0.973 | 0.968/0.988/0.988 |
| **T1D** | Accuracy | 0.653/0.604/0.614 | 0.574/0.574/0.653 | 0.673/0.634/0.653 | 0.624/0.574/0.673 |
| | Balanced Acc | 0.641/0.587/0.596 | 0.561/0.568/0.652 | 0.656/0.613/0.631 | 0.612/0.553/0.659 |
| | Macro-F1 | 0.642/0.586/0.595 | 0.560/0.568/0.650 | 0.657/0.612/0.629 | 0.613/0.549/0.660 |
| **madelon** | Accuracy | 0.623/0.664/0.664 | 0.534/0.544/0.574 | 0.882/0.851/0.820 | 0.578/0.571/0.554 |
| | Balanced Acc | 0.623/0.664/0.664 | 0.534/0.544/0.574 | 0.882/0.851/0.820 | 0.578/0.571/0.554 |
| | Macro-F1 | 0.623/0.664/0.664 | 0.534/0.544/0.574 | 0.882/0.851/0.820 | 0.578/0.571/0.554 |

## 3. Representative Pareto Trajectories ($k \in [10, 20, 50, 100, 200] $)

### Dataset: Colon

| Filter Algorithm | $k=10$ Acc | $k=20$ Acc | $k=50$ Acc | $k=100$ Acc | $k=200$ Acc |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Top-k MI** | 0.8387 | 0.8548 | 0.8871 | 0.8871 | 0.8871 |
| **Two-Stage mRMR** | 0.8548 | 0.8710 | 0.8226 | 0.8710 | 0.8871 |
| **ReliefF** | 0.8710 | 0.8871 | 0.8710 | 0.8548 | 0.8710 |
| **LASSO** | 0.8710 | 0.8548 | 0.8871 | 0.8871 | 0.8871 |

### Dataset: T1D

| Filter Algorithm | $k=10$ Acc | $k=20$ Acc | $k=50$ Acc | $k=100$ Acc | $k=200$ Acc |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Top-k MI** | 0.6337 | 0.6535 | 0.6040 | 0.6139 | 0.6931 |
| **Two-Stage mRMR** | 0.5545 | 0.5743 | 0.5743 | 0.6535 | 0.6436 |
| **ReliefF** | 0.6832 | 0.6733 | 0.6337 | 0.6535 | 0.6832 |
| **LASSO** | 0.6238 | 0.6238 | 0.5743 | 0.6733 | 0.6535 |

### Dataset: BASEHOCK

| Filter Algorithm | $k=10$ Acc | $k=20$ Acc | $k=50$ Acc | $k=100$ Acc | $k=200$ Acc |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Top-k MI** | 0.8490 | 0.8811 | 0.9027 | 0.9117 | 0.8966 |
| **Two-Stage mRMR** | 0.7195 | 0.7461 | 0.8264 | 0.8791 | 0.8981 |
| **ReliefF** | 0.5349 | 0.5655 | 0.6382 | 0.6899 | 0.7587 |
| **LASSO** | 0.8495 | 0.8710 | 0.8871 | 0.8961 | 0.9017 |

### Dataset: COIL20

| Filter Algorithm | $k=10$ Acc | $k=20$ Acc | $k=50$ Acc | $k=100$ Acc | $k=200$ Acc |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Top-k MI** | 0.7764 | 0.8812 | 0.9382 | 0.9681 | 0.9882 |
| **Two-Stage mRMR** | 0.9201 | 0.9472 | 0.9861 | 0.9903 | 0.9951 |
| **ReliefF** | 0.6986 | 0.7722 | 0.8243 | 0.9139 | 0.9708 |
| **LASSO** | 0.9292 | 0.9757 | 0.9910 | 0.9938 | 0.9951 |

## 4. Academic Insights & Empirical Filter Observations

### 4.1 Methodological Protocol & Selection Mechanisms

1. **Fold-Internal Zero-Leakage Protocol**: All feature selection, scaling, and ranking operations are performed strictly on each outer training fold, ensuring strict blind evaluation on held-out test folds.
2. **LASSO L1-OvR & Two-Tier Non-Zero Lexical Priority**: LASSO is formalized via OneVsRestClassifier with L1 regularized Logistic Regression ($C=0.1$). Features with non-zero coefficients are ranked strictly ahead of zero-coefficient features by cumulative absolute weight $\sum_c |\beta_{c,j}|$. When non-zero features are fewer than $k$, remaining slots are completed by sorting zero-coefficient features by training-fold Mutual Information (MI). Fitting failures strictly trigger exceptions without silent substitution.

### 4.2 Dynamic Empirical Observations from Current Execution

1. **Observed Filter Performance Hierarchy**: Across the 19 common completed dataset(s) over the primary grid $k \in [20, 50, 100]$, the aggregate mean accuracy ranking is: `LASSO` (0.8840) > `Top-k MI` (0.8718) > `Two-Stage mRMR` (0.8632) > `ReliefF` (0.8556).
2. **Feature Budget ($k$) Sensitivity**: Across the evaluated cardinality grid, aggregate mean accuracy progresses as follows: $k=20$: **0.8563** $\to$ $k=50$: **0.8693** $\to$ $k=100$: **0.8803**. Performance increases monotonically from $k=20$ to $k=100$.
3. **Cross-Paradigm Comparison Alignment**: These measurements reflect fold-internal filter performance. Direct comparisons against wrapper or evolutionary algorithms require matched cardinality budgets and identical outer cross-validation fold partitions.
