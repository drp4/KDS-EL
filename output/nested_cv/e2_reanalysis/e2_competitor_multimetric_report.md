# E2: Offline Multi-Metric Re-Analysis of Competitor Feature Masks

- **Execution Timestamp**: 2026-11-08T13:19:52.338324
- **Execution Status**: **COMPLETE**
- **Protocol Reference**: `review_round_1/05_executable_experiment_plan.md` (Section 5)
- **Competitor Masks Evaluated**: **570 / 570**
- **Evaluated Competitor Algorithms (3)**: `bIRIME, BinCOA, DENCA_SO`
- **Benchmark Datasets (19)**: Strictly independent benchmarks (excluding `ALL_AML`)
- **Total Elapsed Time**: `62.14 s`

> **Formal Methodological Demarcation**:
> This experiment serves strictly as an **internal 5-fold cross-validation descriptive re-analysis** of historical competitor masks (from `formal_experiment_20260905_211755`). It computes standard classification Accuracy alongside class-imbalance-aware Balanced Accuracy (BAcc) and Macro-F1. In accordance with scientific rigor, these descriptive metrics supplement the primary comparison but are not claimed as new unbiased outer test estimates, nor are they mixed with nested double-cross-validation scores.

## 1. Overall Aggregate Performance Comparison (19 Benchmark Datasets)

| Competitor Algorithm | Mean Accuracy (Acc) | Mean Balanced Acc (BAcc) | Mean Macro-F1 (F1) | Mean Active Features ($d$) | Clean Completed Datasets |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **`bIRIME`** | **0.9426** | **0.9343** | **0.9360** | **422.9** | 19/19 |
| **`BinCOA`** | **0.8926** | **0.8802** | **0.8810** | **5526.1** | 19/19 |
| **`DENCA_SO`** | **0.8656** | **0.8505** | **0.8497** | **5432.5** | 19/19 |

## 2. Per-Dataset Multi-Metric Breakdown (Mean ± Std over Independent Runs)

| Dataset | Metric | bIRIME | BinCOA | DENCA_SO |
| :--- | :--- | :---: | :---: | :---: |
| **ALL1** | Accuracy | 1.0000 ± 0.000 | 1.0000 ± 0.000 | 1.0000 ± 0.000 |
| | Balanced Acc | 1.0000 ± 0.000 | 1.0000 ± 0.000 | 1.0000 ± 0.000 |
| | Macro-F1 | 1.0000 ± 0.000 | 1.0000 ± 0.000 | 1.0000 ± 0.000 |
| | Features ($d$) | 64.6 ± 6.4 | 6120.3 ± 32.6 | 5877.1 ± 33.6 |
| **ALL4** | Accuracy | 0.9140 ± 0.012 | 0.7634 ± 0.008 | 0.7043 ± 0.013 |
| | Balanced Acc | 0.9026 ± 0.021 | 0.7334 ± 0.016 | 0.6642 ± 0.016 |
| | Macro-F1 | 0.8950 ± 0.015 | 0.7204 ± 0.011 | 0.6531 ± 0.015 |
| | Features ($d$) | 393.4 ± 94.4 | 6300.9 ± 70.3 | 6111.0 ± 49.2 |
| **Adenoma** | Accuracy | 1.0000 ± 0.000 | 0.9722 ± 0.000 | 0.9611 ± 0.014 |
| | Balanced Acc | 1.0000 ± 0.000 | 0.9722 ± 0.000 | 0.9611 ± 0.014 |
| | Macro-F1 | 1.0000 ± 0.000 | 0.9722 ± 0.000 | 0.9611 ± 0.014 |
| | Features ($d$) | 39.6 ± 4.8 | 3553.5 ± 9.5 | 3397.2 ± 40.4 |
| **BASEHOCK** | Accuracy | 0.9082 ± 0.004 | 0.8889 ± 0.005 | 0.8612 ± 0.009 |
| | Balanced Acc | 0.9083 ± 0.004 | 0.8890 ± 0.005 | 0.8613 ± 0.009 |
| | Macro-F1 | 0.9080 ± 0.004 | 0.8889 ± 0.005 | 0.8604 ± 0.009 |
| | Features ($d$) | 1720.6 ± 247.6 | 2445.2 ± 34.8 | 2358.7 ± 30.3 |
| **COIL20** | Accuracy | 0.9991 ± 0.001 | 0.9953 ± 0.000 | 0.9942 ± 0.001 |
| | Balanced Acc | 0.9991 ± 0.001 | 0.9953 ± 0.000 | 0.9942 ± 0.001 |
| | Macro-F1 | 0.9991 ± 0.001 | 0.9954 ± 0.000 | 0.9943 ± 0.001 |
| | Features ($d$) | 54.3 ± 5.8 | 453.8 ± 9.9 | 634.5 ± 12.8 |
| **Colon** | Accuracy | 0.9468 ± 0.007 | 0.8694 ± 0.005 | 0.8048 ± 0.020 |
| | Balanced Acc | 0.9485 ± 0.011 | 0.8466 ± 0.007 | 0.7751 ± 0.022 |
| | Macro-F1 | 0.9426 ± 0.008 | 0.8540 ± 0.006 | 0.7812 ± 0.022 |
| | Features ($d$) | 113.3 ± 38.4 | 960.2 ± 17.4 | 845.1 ± 16.6 |
| **DLBCL** | Accuracy | 1.0000 ± 0.000 | 0.9883 ± 0.004 | 0.9675 ± 0.010 |
| | Balanced Acc | 1.0000 ± 0.000 | 0.9922 ± 0.003 | 0.9731 ± 0.014 |
| | Macro-F1 | 1.0000 ± 0.000 | 0.9845 ± 0.005 | 0.9577 ± 0.014 |
| | Features ($d$) | 246.6 ± 52.1 | 3514.0 ± 54.1 | 3784.3 ± 25.7 |
| **Gastric** | Accuracy | 0.9569 ± 0.015 | 0.8231 ± 0.008 | 0.7769 ± 0.017 |
| | Balanced Acc | 0.9571 ± 0.017 | 0.8084 ± 0.009 | 0.7567 ± 0.019 |
| | Macro-F1 | 0.9564 ± 0.015 | 0.8138 ± 0.009 | 0.7592 ± 0.021 |
| | Features ($d$) | 258.3 ± 48.3 | 11157.1 ± 113.5 | 10624.9 ± 54.1 |
| **Gastric1** | Accuracy | 0.9722 ± 0.000 | 0.9583 ± 0.000 | 0.9500 ± 0.007 |
| | Balanced Acc | 0.9722 ± 0.000 | 0.9583 ± 0.000 | 0.9500 ± 0.007 |
| | Macro-F1 | 0.9722 ± 0.000 | 0.9583 ± 0.000 | 0.9500 ± 0.007 |
| | Features ($d$) | 213.0 ± 30.1 | 10936.6 ± 44.0 | 10911.0 ± 38.9 |
| **Gastric2** | Accuracy | 0.9952 ± 0.004 | 0.9823 ± 0.003 | 0.9750 ± 0.002 |
| | Balanced Acc | 0.9952 ± 0.004 | 0.9823 ± 0.003 | 0.9750 ± 0.002 |
| | Macro-F1 | 0.9952 ± 0.004 | 0.9823 ± 0.003 | 0.9750 ± 0.002 |
| | Features ($d$) | 348.2 ± 135.0 | 11040.8 ± 136.4 | 10971.3 ± 92.3 |
| **ISOLET** | Accuracy | 0.9112 ± 0.008 | 0.8763 ± 0.004 | 0.8760 ± 0.005 |
| | Balanced Acc | 0.9112 ± 0.008 | 0.8763 ± 0.004 | 0.8760 ± 0.005 |
| | Macro-F1 | 0.9111 ± 0.008 | 0.8759 ± 0.004 | 0.8757 ± 0.005 |
| | Features ($d$) | 132.6 ± 14.7 | 297.9 ± 12.7 | 373.8 ± 15.1 |
| **Leukaemia** | Accuracy | 1.0000 ± 0.000 | 0.9861 ± 0.000 | 0.9764 ± 0.009 |
| | Balanced Acc | 1.0000 ± 0.000 | 0.9800 ± 0.000 | 0.9679 ± 0.011 |
| | Macro-F1 | 1.0000 ± 0.000 | 0.9845 ± 0.000 | 0.9736 ± 0.010 |
| | Features ($d$) | 131.9 ± 16.6 | 3406.3 ± 22.5 | 3217.7 ± 28.1 |
| **Lymphoma** | Accuracy | 0.9978 ± 0.007 | 0.8889 ± 0.000 | 0.8400 ± 0.022 |
| | Balanced Acc | 0.9977 ± 0.007 | 0.8893 ± 0.000 | 0.8415 ± 0.021 |
| | Macro-F1 | 0.9978 ± 0.007 | 0.8889 ± 0.000 | 0.8395 ± 0.022 |
| | Features ($d$) | 136.6 ± 55.2 | 1933.9 ± 19.7 | 1764.9 ± 30.8 |
| **Myeloma** | Accuracy | 0.8884 ± 0.009 | 0.8387 ± 0.008 | 0.8012 ± 0.012 |
| | Balanced Acc | 0.7524 ± 0.021 | 0.6780 ± 0.022 | 0.6082 ± 0.023 |
| | Macro-F1 | 0.7960 ± 0.020 | 0.7057 ± 0.022 | 0.6241 ± 0.027 |
| | Features ($d$) | 1160.3 ± 209.9 | 6277.5 ± 37.8 | 6595.8 ± 55.1 |
| **PCMAC** | Accuracy | 0.8410 ± 0.004 | 0.8161 ± 0.006 | 0.7596 ± 0.018 |
| | Balanced Acc | 0.8403 ± 0.004 | 0.8157 ± 0.006 | 0.7587 ± 0.018 |
| | Macro-F1 | 0.8399 ± 0.004 | 0.8157 ± 0.006 | 0.7563 ± 0.019 |
| | Features ($d$) | 928.2 ± 230.6 | 1621.4 ± 29.4 | 1590.3 ± 22.6 |
| **Prostate** | Accuracy | 0.9353 ± 0.007 | 0.8686 ± 0.005 | 0.8235 ± 0.009 |
| | Balanced Acc | 0.9360 ± 0.006 | 0.8691 ± 0.005 | 0.8233 ± 0.009 |
| | Macro-F1 | 0.9353 ± 0.007 | 0.8686 ± 0.005 | 0.8234 ± 0.009 |
| | Features ($d$) | 417.5 ± 161.2 | 6281.9 ± 65.2 | 5836.8 ± 38.6 |
| **SRBCT** | Accuracy | 1.0000 ± 0.000 | 0.9663 ± 0.005 | 0.9325 ± 0.022 |
| | Balanced Acc | 1.0000 ± 0.000 | 0.9739 ± 0.004 | 0.9456 ± 0.019 |
| | Macro-F1 | 1.0000 ± 0.000 | 0.9649 ± 0.006 | 0.9313 ± 0.023 |
| | Features ($d$) | 171.7 ± 45.8 | 1135.9 ± 26.5 | 1056.1 ± 18.7 |
| **T1D** | Accuracy | 0.7752 ± 0.011 | 0.7178 ± 0.005 | 0.6723 ± 0.010 |
| | Balanced Acc | 0.7638 ± 0.012 | 0.7036 ± 0.006 | 0.6576 ± 0.010 |
| | Macro-F1 | 0.7671 ± 0.012 | 0.7059 ± 0.006 | 0.6587 ± 0.010 |
| | Features ($d$) | 1459.4 ± 637.5 | 27318.5 ± 93.3 | 27144.9 ± 141.3 |
| **madelon** | Accuracy | 0.8677 ± 0.016 | 0.7598 ± 0.006 | 0.7695 ± 0.012 |
| | Balanced Acc | 0.8677 ± 0.016 | 0.7598 ± 0.006 | 0.7695 ± 0.012 |
| | Macro-F1 | 0.8676 ± 0.016 | 0.7598 ± 0.006 | 0.7695 ± 0.012 |
| | Features ($d$) | 45.8 ± 16.8 | 239.5 ± 6.7 | 122.5 ± 6.0 |

## 3. Academic Findings & Empirical Observations

1. **Observed Performance Hierarchy**: Across the 19 evaluated benchmark datasets, the aggregate performance hierarchy among competitor algorithms remains identical across standard Accuracy, Balanced Accuracy, and Macro-F1: `bIRIME` > `BinCOA` > `DENCA_SO`.
2. **Dataset-Level Concordance for Top Competitor (`bIRIME`)**:
   - Versus `BinCOA` (across 19 common datasets): Accuracy wins = 18/19, Balanced Accuracy wins = 18/19, Macro-F1 wins = 18/19.
   - Versus `DENCA_SO` (across 19 common datasets): Accuracy wins = 18/19, Balanced Accuracy wins = 18/19, Macro-F1 wins = 18/19.
3. **Descriptive Re-Analysis Context**: These descriptive re-analysis metrics evaluate historical feature masks under class-imbalance-aware measures, verifying that observed competitor performance relationships are consistent under balanced metrics without altering the established primary benchmark records.
