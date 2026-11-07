# E1-B: Concurrency Ladder Stress Test Report

- **Execution Timestamp**: 2026-11-07T13:44:06.354088
- **Protocol Reference**: `review_round_1/05_executable_experiment_plan.md` (Section 4.3)
- **CPU Physical Cores**: 6
- **CPU Logical Cores**: 6
- **Total System RAM**: `N/A GB`
- **Recommended Safe Concurrency**: **`workers = 4`**

## Concurrency Ladder Performance

| Workers | Tasks | Time (s) | Speedup | Peak RSS (MB) | CPU % | Status |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **1** | 4/4 | `548.46 s` | **1.00x** | N/A | N/A | **PASS** |
| **2** | 4/4 | `415.19 s` | **1.32x** | N/A | N/A | **PASS** |
| **4** | 4/4 | `407.80 s` | **1.34x** | N/A | N/A | **PASS** |

## Concurrency & Stability Decision

Based on empirical ladder benchmarking with single-tier thread locking (`OMP/MKL/OPENBLAS=1`, `RF n_jobs=1`), **`workers = 4`** achieved the optimal trade-off between throughput scaling and memory headroom without process deadlocks on Windows `spawn`.
