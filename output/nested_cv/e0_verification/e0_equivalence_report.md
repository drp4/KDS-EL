# E0: Candidate Fast 3-NN Equivalence Verification & Decision Gate Report

- **Execution Timestamp**: 2026-11-07T13:57:01.832664
- **Protocol Document**: `review_round_1/05_executable_experiment_plan.md` (Section 3)
- **Total Masks Evaluated**: 800
- **Total Predictions Evaluated**: 719200
- **Total Prediction Mismatches**: 116283
- **Decision Gate Status**: **`REJECTED_FALLBACK_TO_SKLEARN`**

> **GATE VERDICT: REJECTED (FALLBACK TO SCIKIT-LEARN TRIGGERED)** — Prediction divergences were detected on at least one benchmark dataset (e.g. zero-distance tie-breaking divergence on sparse bag-of-words text data). In strict adherence to Section 3.4 of the experiment plan, the candidate accelerator is rejected and all downstream experiments MUST fall back to the authoritative Scikit-Learn `KNeighborsClassifier` evaluator.

## Per-Dataset Verification Breakdown

| Dataset | Samples | Features | Classes | Masks | Mismatches | Max ΔAcc | Max ΔBAcc | Max ΔF1 | Kendall τ | Spearman ρ | Speedup | Status |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Colon** | 62 | 2000 | 2 | 200 | 0 | 0.0e+00 | 0.0e+00 | 0.0e+00 | 1.0000 | 1.0000 | 7.48x | **PASS** |
| **T1D** | 101 | 54675 | 2 | 200 | 0 | 0.0e+00 | 0.0e+00 | 0.0e+00 | 1.0000 | 1.0000 | 3.04x | **PASS** |
| **BASEHOCK** | 1993 | 4862 | 2 | 200 | 115970 | 6.0e-02 | 5.9e-02 | 1.7e-01 | 0.8673 | 0.9761 | 0.67x | **FAIL** |
| **COIL20** | 1440 | 1024 | 20 | 200 | 313 | 4.9e-03 | 4.9e-03 | 5.6e-03 | 0.9999 | 1.0000 | 1.03x | **FAIL** |

## Execution Wall-Clock Timing

- Authoritative Scikit-Learn 3-NN Total Time: `45.13 s`
- Candidate Fast 3-NN Total Time: `45.74 s`
- Empirical Acceleration Ratio: `0.99x`
