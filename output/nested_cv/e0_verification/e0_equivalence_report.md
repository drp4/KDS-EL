# E0: Candidate Fast 3-NN Equivalence Verification & Decision Gate Report

- **Execution Timestamp**: 2026-11-07T10:40:11.677288
- **Protocol Document**: `review_round_1/05_executable_experiment_plan.md` (Section 3)
- **Total Masks Evaluated**: 20
- **Total Predictions Evaluated**: 17980
- **Total Prediction Mismatches**: 2660
- **Decision Gate Status**: **`REJECTED_FALLBACK_TO_SKLEARN`**

> **GATE VERDICT: REJECTED (FALLBACK TO SCIKIT-LEARN TRIGGERED)** — Prediction divergences were detected on at least one benchmark dataset (e.g. zero-distance tie-breaking divergence on sparse bag-of-words text data). In strict adherence to Section 3.4 of the experiment plan, the candidate accelerator is rejected and all downstream experiments MUST fall back to the authoritative Scikit-Learn `KNeighborsClassifier` evaluator.

## Per-Dataset Verification Breakdown

| Dataset | Samples | Features | Classes | Masks | Mismatches | Max ΔAcc | Max ΔBAcc | Max ΔF1 | Kendall τ | Spearman ρ | Speedup | Status |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Colon** | 62 | 2000 | 2 | 5 | 0 | 0.0e+00 | 0.0e+00 | 0.0e+00 | 1.0000 | 1.0000 | 78.73x | **PASS** |
| **T1D** | 101 | 54675 | 2 | 5 | 0 | 0.0e+00 | 0.0e+00 | 0.0e+00 | 1.0000 | 1.0000 | 2.70x | **PASS** |
| **BASEHOCK** | 1993 | 4862 | 2 | 5 | 2660 | 3.0e-02 | 2.9e-02 | 8.7e-02 | 1.0000 | 1.0000 | 1.01x | **FAIL** |
| **COIL20** | 1440 | 1024 | 20 | 5 | 0 | 0.0e+00 | 0.0e+00 | 0.0e+00 | 1.0000 | 1.0000 | 1.07x | **PASS** |

## Execution Wall-Clock Timing

- Authoritative Scikit-Learn 3-NN Total Time: `3.36 s`
- Candidate Fast 3-NN Total Time: `1.27 s`
- Empirical Acceleration Ratio: `2.65x`
