"""
bIRIME — Improved Binary RIME Algorithm for Feature Selection
=============================================================
Reference:
  Su, T., Huang, J., et al. (2024).
  Mitigating exploitation-exploration imbalance in RIME optimization
  for feature selection.
  iScience (Cell Press), 27(8), 110561.
  DOI: 10.1016/j.isci.2024.110561

Official Repository:
  https://github.com/TingJin0/IRIME/blob/main/bIRIME.m

Algorithmic Core:
  1. Logistic S-shaped Transfer Function:
     T(x) = 1 / (1 + exp(-10 * (x - 0.5))) with continuous bounds [0, 1].
     Ensures initial selection density naturally centers at 50% without hyper-density bias.
  2. Soft-Besiege (SB) Mechanism:
     Driven by escaping energy |E_0| >= 1, enabling wide exploration via group perching.
  3. Soft-rime Search & Hard-rime Puncture:
     Governed by E = sqrt(t/T) and normalized fitness rating normr(fit).
  4. Composite Mutation Strategies (CMS):
     Applies CoDE-derived multi-candidate differential mutation (U1, U2, U3)
     to boost local exploitation and diversity.
  5. Restart Strategy (RS):
     Random + Opposition restart when individual stagnation exceeds Limits.
"""
import numpy as np
from utils import jFitness


def sigmf_transfer(x):
    """S-shaped transfer function: sigmf(x, [10, 0.5]) from official bIRIME.m."""
    return 1.0 / (1.0 + np.exp(-np.clip(10.0 * (x - 0.5), -15.0, 15.0)))


def binarize(x_cont, dim):
    """基于 S 型转换函数与伯努利随机抽样二值化。"""
    prob = sigmf_transfer(x_cont)
    b = (np.random.rand(dim) < prob)
    if not b.any():
        b[np.random.choice(dim, min(3, dim), replace=False)] = True
    return b


def run_bIRIME(X, y, opts):
    """
    运行 bIRIME 算法。
    """
    N = opts["N"]
    T = opts["T"]
    dim = X.shape[1]

    lb, ub = 0.0, 1.0
    W_soft = 5.0
    Limits = min(50, max(10, T // 2))

    # 1. 种群初始化：连续空间 [0, 1]^D，期望选择率严格居中在 50%
    P = np.random.uniform(lb, ub, (N, dim))
    P_bin = np.zeros((N, dim), dtype=bool)
    fit = np.zeros(N)

    for i in range(N):
        P_bin[i] = binarize(P[i], dim)
        fit[i] = jFitness(X, y, P_bin[i], opts)

    g_idx = np.argmin(fit)
    Gbest = P[g_idx].copy()
    Gbest_bin = P_bin[g_idx].copy()
    fitG = float(fit[g_idx])

    SalpTrial = np.zeros(N, dtype=int)

    curve = np.zeros(T + 1)
    curve[0] = fitG

    # 2. 演化主循环
    for t in range(1, T + 1):
        RimeFactor = (
            (np.random.rand() - 0.5) * 2.0
            * np.cos(np.pi * t / (max(1.0, T / 10.0)))
            * (1.0 - np.round(t * W_soft / T) / W_soft)
        )
        E = np.sqrt(t / T)
        c = 2.0 * (1.0 - t / T)

        # 归一化评级：基于欧氏范数归一化（原作者 normr 逻辑）
        norm_val = np.sqrt(np.sum(fit ** 2)) + 1e-12
        norm_rates = fit / norm_val

        P_new = P.copy()

        for i in range(N):
            # 逃逸能量
            Escaping_Energy = c * (2.0 * np.random.rand() - 1.0)

            if np.abs(Escaping_Energy) >= 1.0:
                # ── 软围攻机制 (Soft-Besiege, SB) ──
                r = np.random.rand()
                rand_idx = np.random.randint(0, N)
                X_rand = P[rand_idx]
                if r < 0.5:
                    P_new[i] = X_rand - np.random.rand() * np.abs(X_rand - 2.0 * np.random.rand() * P[i])
                else:
                    P_new[i] = (Gbest - np.mean(P, axis=0)) - np.random.rand() * np.random.rand()
            else:
                # ── 软霜搜索与硬霜穿刺机制 ──
                for j in range(dim):
                    if np.random.rand() < E:
                        P_new[i, j] = Gbest[j] + RimeFactor * ((ub - lb) * np.random.rand() + lb)
                    if np.random.rand() < norm_rates[i]:
                        P_new[i, j] = Gbest[j]

            # 边界吸附
            P_new[i] = np.clip(P_new[i], lb, ub)

            # 二值化与评价
            cand_bin = binarize(P_new[i], dim)
            cand_fit = jFitness(X, y, cand_bin, opts)

            # 正向贪婪选择 (Positive greedy selection)
            if cand_fit < fit[i]:
                fit[i] = cand_fit
                P[i] = P_new[i].copy()
                P_bin[i] = cand_bin.copy()
                SalpTrial[i] = 0
                if cand_fit < fitG:
                    fitG = float(cand_fit)
                    Gbest = P[i].copy()
                    Gbest_bin = cand_bin.copy()
            else:
                SalpTrial[i] += 1

            # ── 复合变异策略 (Composite Mutation Strategies, CMS) ──
            other_indices = [idx for idx in range(N) if idx != i]
            if len(other_indices) >= 3:
                # 策略 1: DE/rand/1/bin (F1=1.0, Cr1=0.1)
                k1 = np.random.choice(other_indices, 3, replace=False)
                j_rand1 = np.random.randint(0, dim)
                u1 = P[i].copy()
                cross1 = (np.random.rand(dim) < 0.1)
                cross1[j_rand1] = True
                u1[cross1] = P[k1[0], cross1] + 1.0 * (P[k1[1], cross1] - P[k1[2], cross1])
                u1 = np.clip(u1, lb, ub)
                u1_bin = binarize(u1, dim)
                fit_u1 = jFitness(X, y, u1_bin, opts)

                # 策略 2: DE/rand/2/bin (F2=0.8, Cr2=0.2)
                if len(other_indices) >= 5:
                    k2 = np.random.choice(other_indices, 5, replace=False)
                    u2_diff = (P[k2[1]] - P[k2[2]]) + (P[k2[3]] - P[k2[4]])
                else:
                    k2 = np.random.choice(other_indices, 3, replace=False)
                    u2_diff = P[k2[1]] - P[k2[2]]
                j_rand2 = np.random.randint(0, dim)
                u2 = P[i].copy()
                cross2 = (np.random.rand(dim) < 0.2)
                cross2[j_rand2] = True
                u2[cross2] = P[k2[0], cross2] + 0.8 * u2_diff[cross2]
                u2 = np.clip(u2, lb, ub)
                u2_bin = binarize(u2, dim)
                fit_u2 = jFitness(X, y, u2_bin, opts)

                # 策略 3: current-to-rand/1/bin (F3=1.0, Cr3=0.9)
                k3 = np.random.choice(other_indices, 3, replace=False)
                j_rand3 = np.random.randint(0, dim)
                u3 = P[i].copy()
                cross3 = (np.random.rand(dim) < 0.9)
                cross3[j_rand3] = True
                u3[cross3] = (
                    P[i, cross3]
                    + np.random.rand() * (P[k3[0], cross3] - P[i, cross3])
                    + 1.0 * (P[k3[1], cross3] - P[k3[2], cross3])
                )
                u3 = np.clip(u3, lb, ub)
                u3_bin = binarize(u3, dim)
                fit_u3 = jFitness(X, y, u3_bin, opts)

                com_fits = [fit_u1, fit_u2, fit_u3]
                best_com_idx = int(np.argmin(com_fits))
                com_poss = [u1, u2, u3]
                com_bins = [u1_bin, u2_bin, u3_bin]

                best_cms_fit = com_fits[best_com_idx]
                if best_cms_fit < fit[i]:
                    P[i] = com_poss[best_com_idx].copy()
                    P_bin[i] = com_bins[best_com_idx].copy()
                    fit[i] = best_cms_fit
                    SalpTrial[i] = 0
                    if best_cms_fit < fitG:
                        fitG = float(best_cms_fit)
                        Gbest = P[i].copy()
                        Gbest_bin = P_bin[i].copy()
                else:
                    SalpTrial[i] += 1

            # ── 重启机制 (Restart Strategy, RS) ──
            if SalpTrial[i] >= Limits:
                T1 = np.random.uniform(lb, ub, dim)
                T2 = np.clip(np.random.uniform(lb, ub, dim) - P[i], lb, ub)

                T1_bin = binarize(T1, dim)
                T2_bin = binarize(T2, dim)

                fT1 = jFitness(X, y, T1_bin, opts)
                fT2 = jFitness(X, y, T2_bin, opts)

                if fT1 < fT2:
                    P[i] = T1.copy()
                    P_bin[i] = T1_bin.copy()
                    fit[i] = fT1
                else:
                    P[i] = T2.copy()
                    P_bin[i] = T2_bin.copy()
                    fit[i] = fT2

                SalpTrial[i] = 0
                if fit[i] < fitG:
                    fitG = float(fit[i])
                    Gbest = P[i].copy()
                    Gbest_bin = P_bin[i].copy()

        curve[t] = fitG

    mask = Gbest_bin.astype(bool)
    if not mask.any():
        mask[np.random.choice(dim, min(3, dim), replace=False)] = True

    return {
        "fitG": fitG,
        "nf": int(mask.sum()),
        "mask": mask,
        "curve": curve,
        "nhd_curve": np.zeros(T + 1),
    }
