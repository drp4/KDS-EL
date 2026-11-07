# E1-A: Nested Pipeline Flow Acceptance Report

- **Execution Timestamp**: 2026-11-07T16:15:36.904983
- **Protocol Reference**: `review_round_1/05_executable_experiment_plan.md` (Section 4)
- **Total Flow Acceptance Runs**: 20
- **Runs Passing All 12 Integrity Checks**: **20 / 20**
- **Total Elapsed Time**: `2569.84 s`
- **Gate Decision**: **`ACCEPTANCE_PASSED`**

> **GATE VERDICT: PASS** — All 20 flow acceptance runs across the 4 representative datasets and 5 core configurations completed without errors, strictly isolated the outer test set, satisfied request closed-loop accounting, strictly respected Max_FEs <= 2000, and persisted all reproducibility artifacts.

## 5-Fold Pooled OOF Partition Integrity Audit

| Dataset | Total Samples ($N$) | 5 Folds Mutually Disjoint & Complete | Status |
| :--- | :---: | :--- | :---: |
| **Colon** | 62 | 5-fold Pooled OOF partition is 100% complete, disjoint, and non-overlapping | **PASS** |
| **T1D** | 101 | 5-fold Pooled OOF partition is 100% complete, disjoint, and non-overlapping | **PASS** |
| **BASEHOCK** | 1993 | 5-fold Pooled OOF partition is 100% complete, disjoint, and non-overlapping | **PASS** |
| **COIL20** | 1440 | 5-fold Pooled OOF partition is 100% complete, disjoint, and non-overlapping | **PASS** |

## 20 Acceptance Runs Detail Table

| Dataset | Algorithm | Requests (<=2000) | Shortcuts | Cache Hits | CV Calls | Feats | 3-NN Acc | 3-NN BAcc | SVM Acc | RF Acc | Time (s) | Audit |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Colon** | `KDS_EL_TwoPhase` | 2000 | 821 | 35 | 1144 | 5 | 0.7692 | 0.7375 | 0.7692 | 0.7692 | 10.08s | **PASS** |
| **Colon** | `MEL` | 2000 | 984 | 3 | 1013 | 775 | 0.6923 | 0.6000 | 0.9231 | 0.9231 | 25.90s | **PASS** |
| **Colon** | `MEL_MI` | 2000 | 969 | 0 | 1031 | 102 | 0.8462 | 0.8375 | 0.9231 | 1.0000 | 7.66s | **PASS** |
| **Colon** | `KDS_EL_NoPool` | 2000 | 804 | 27 | 1169 | 19 | 1.0000 | 1.0000 | 0.9231 | 0.8462 | 8.56s | **PASS** |
| **Colon** | `bIRIME` | 2000 | 0 | 0 | 2000 | 126 | 0.7692 | 0.7000 | 0.9231 | 0.8462 | 11.43s | **PASS** |
| **T1D** | `KDS_EL_TwoPhase` | 2000 | 767 | 20 | 1213 | 104 | 0.5714 | 0.5694 | 0.6667 | 0.7143 | 97.29s | **PASS** |
| **T1D** | `MEL` | 2000 | 904 | 4 | 1092 | 108 | 0.6667 | 0.6806 | 0.7619 | 0.7619 | 583.16s | **PASS** |
| **T1D** | `MEL_MI` | 2000 | 897 | 0 | 1103 | 867 | 0.8095 | 0.7917 | 0.6190 | 0.6667 | 96.16s | **PASS** |
| **T1D** | `KDS_EL_NoPool` | 2000 | 787 | 0 | 1213 | 462 | 0.8095 | 0.7917 | 0.6190 | 0.6667 | 97.78s | **PASS** |
| **T1D** | `bIRIME` | 2000 | 0 | 0 | 2000 | 419 | 0.7143 | 0.7222 | 0.7143 | 0.6190 | 119.97s | **PASS** |
| **BASEHOCK** | `KDS_EL_TwoPhase` | 2000 | 782 | 28 | 1190 | 64 | 0.9073 | 0.9074 | 0.8897 | 0.9248 | 92.05s | **PASS** |
| **BASEHOCK** | `MEL` | 2000 | 980 | 2 | 1018 | 1900 | 0.8747 | 0.8748 | 0.9023 | 0.9524 | 398.76s | **PASS** |
| **BASEHOCK** | `MEL_MI` | 2000 | 979 | 11 | 1010 | 83 | 0.9123 | 0.9124 | 0.8747 | 0.9248 | 74.81s | **PASS** |
| **BASEHOCK** | `KDS_EL_NoPool` | 2000 | 808 | 32 | 1160 | 117 | 0.8672 | 0.8674 | 0.8546 | 0.8947 | 147.22s | **PASS** |
| **BASEHOCK** | `bIRIME` | 2000 | 0 | 0 | 2000 | 1529 | 0.8622 | 0.8622 | 0.9198 | 0.9449 | 572.94s | **PASS** |
| **COIL20** | `KDS_EL_TwoPhase` | 2000 | 788 | 41 | 1171 | 124 | 0.9965 | 0.9967 | 0.9965 | 1.0000 | 40.28s | **PASS** |
| **COIL20** | `MEL` | 2000 | 990 | 0 | 1010 | 319 | 0.9861 | 0.9864 | 0.9931 | 1.0000 | 53.52s | **PASS** |
| **COIL20** | `MEL_MI` | 2000 | 969 | 0 | 1031 | 323 | 1.0000 | 1.0000 | 0.9965 | 1.0000 | 58.96s | **PASS** |
| **COIL20** | `KDS_EL_NoPool` | 2000 | 812 | 29 | 1159 | 72 | 0.9965 | 0.9967 | 0.9965 | 1.0000 | 41.08s | **PASS** |
| **COIL20** | `bIRIME` | 2000 | 0 | 0 | 2000 | 44 | 0.9792 | 0.9786 | 0.9792 | 0.9965 | 31.95s | **PASS** |
