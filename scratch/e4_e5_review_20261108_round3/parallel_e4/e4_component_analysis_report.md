# E4: Controlled Constituent Mechanism Analysis Report

- **Execution Timestamp**: 2026-11-08T14:36:54.702876
- **Protocol Reference**: `review_round_1/05_executable_experiment_plan.md` (Section 7)
- **Evaluated Configurations (7)**: KDS-EL Full, Static-095, Static-070, Reversed, No-Decay, Single-P1, No-KER
- **Runs Status**: `4 / 4` completed (Tasks Execution Completed: `True`, Valid for Formal Claims: `False`)
- **Total Elapsed Time**: `9.19 s`

> [!WARNING] Incomplete / Diagnostic Execution Notice
> Execution did not meet formal protocol requirements (5 folds required, executed folds=[1, 2], tasks=4/4, all audits passed=True). The metrics below represent partial or diagnostic progress and CANNOT serve as formal empirical claims in publication.

> **Formal Methodological Demarcation**:
> In strict accordance with Elsevier standards, component contributions are evaluated before and after controlled algorithmic modifications under identical evaluation budgets (Max_FEs = 2000, N = 20). All variants are tested under strict outer test isolation without circular data leakage.

## 1. Controlled Mechanism Contribution Matrix

| Algorithmic Configuration | Pooled OOF Acc | Pooled OOF BAcc | Pooled OOF F1 | Mean Features ($d$) | KER Accept Rate | P2 Feasible Rate | $\Delta W_{\mathrm{class}}$ |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **`KDS_EL_Full`** (KDS-EL (Full)) | **0.5833** ± 0.000 | 0.5833 ± 0.000 | 0.5833 | **3.0** | 0.0% | 5.6% | -4.0746 |
| **`Abl_Static_095`** (Static-095 (High Acc)) | **0.5833** ± 0.000 | 0.5833 ± 0.000 | 0.5833 | **3.0** | 0.2% | 6.1% | -2.9385 |

## 2. Key Academic Findings & Mechanism Validation

Execution is partial, diagnostic, or incomplete. Formal academic mechanism findings require complete 5-fold evaluation with passed audits for all variants.
