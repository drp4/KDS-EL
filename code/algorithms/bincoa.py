"""
BinCOA — Binary Crayfish Optimization Algorithm for Feature Selection
=====================================================================
Reference:
  Shikoun, N. H., Hassanien, A. E., et al. (2024).
  BinCOA: An Efficient Binary Crayfish Optimization Algorithm for Feature Selection.
  IEEE Access, 12, 28621–28635.
  DOI: 10.1109/ACCESS.2024.3366495

Algorithmic Core:
  1. Refracted Opposition-Based Learning (ROBL) Initialization:
     Extends candidate initialization via refraction inverse mapping (Eq. 15-16),
     selecting top N individuals from 2N candidates based on fitness.
  2. Sigmoid S-shaped Transfer Function (Eq. 17-18):
     T(x) = 1 / (1 + exp(-x)) centered at 0 with bounds [-3.0, 3.0].
     Ensures initial selection density naturally centers at 50%.
  3. Temperature-Driven Phase Switching:
     - High Temperature (>30°C): Summer Resort (Eq. 6) & Cave Competition (Eq. 8).
     - Moderate Temperature (<=30°C): Food Shredding (Eq. 12-13) & Direct Foraging (Eq. 14).
  4. Crisscross Strategy (CS):
     - Horizontal Crossover (HC, Eq. 19-20) across paired crayfish.
     - Vertical Crossover (VC, Eq. 21) across distinct feature dimensions.
"""
import numpy as np
from utils import jFitness


def sigmoid_transfer(x):
    """S-shaped sigmoid transfer function (Eq. 17 in paper)."""
    return 1.0 / (1.0 + np.exp(-np.clip(x, -15.0, 15.0)))


def binarize(x_cont, dim):
    """二值化算子 (Eq. 18: rand >= T(x) 则激活特征)。"""
    prob = sigmoid_transfer(x_cont)
    b = (np.random.rand(dim) >= prob)
    if not b.any():
        b[np.random.choice(dim, min(3, dim), replace=False)] = True
    return b


def run_BinCOA(X, y, opts):
    """
    运行 BinCOA 算法。
    """
    N = opts["N"]
    T = opts["T"]
    dim = X.shape[1]

    lb, ub = -3.0, 3.0
    sigma_refract = 1.0  # 折射率 (Eq. 15-16)

    # ── 1. 折射对立学习 (ROBL) 初始化 (Eq. 15-16) ──
    Cr = np.random.uniform(lb, ub, (N, dim))

    # 折射反向种群 Cr_star
    mid = (lb + ub) / 2.0
    Cr_star = mid + mid / sigma_refract - Cr / sigma_refract
    Cr_star = np.clip(Cr_star, lb, ub)

    # 评估 2N 个候选个体
    candidates = np.vstack([Cr, Cr_star])
    cand_bin = np.zeros((2 * N, dim), dtype=bool)
    cand_fit = np.zeros(2 * N)

    for i in range(2 * N):
        cand_bin[i] = binarize(candidates[i], dim)
        cand_fit[i] = jFitness(X, y, cand_bin[i], opts)

    # 精英保留：选取前 N 个最优个体进入初始种群
    best_indices = np.argsort(cand_fit)[:N]
    Cr = candidates[best_indices].copy()
    Cr_bin = cand_bin[best_indices].copy()
    fit = cand_fit[best_indices].copy()

    # 全局最优 CrG 与种群局部最优 CrL
    CrG = Cr[0].copy()
    CrG_bin = Cr_bin[0].copy()
    fitG = float(fit[0])
    CrL = Cr[0].copy()

    curve = np.zeros(T + 1)
    curve[0] = fitG

    # ── 2. 演化主循环 ──
    for t in range(1, T + 1):
        temp = np.random.rand() * 15.0 + 20.0  # [20, 35] 摄氏度
        Cr_new = Cr.copy()

        if temp > 30.0:
            # ── 阶段 1: 避暑与洞穴竞争探索 (Summer Resort & Cave Competition) ──
            Cr_shade = (CrG + CrL) / 2.0  # Eq. 5
            for i in range(N):
                if np.random.rand() < 0.5:
                    S = 2.0 - (t / T)  # Eq. 7
                    Cr_new[i] = Cr[i] + S * np.random.rand() * (Cr_shade - Cr[i])
                else:
                    other_z = [idx for idx in range(N) if idx != i]
                    z = np.random.choice(other_z) if other_z else i
                    Cr_new[i] = Cr[i] - Cr[z] + Cr_shade
        else:
            # ── 阶段 2: 适温觅食利用 (Foraging Stage) ──
            mu, sigma_p, W_p = 25.0, 3.0, 1.0
            p = W_p * (1.0 / (np.sqrt(2.0 * np.pi) * sigma_p)) * np.exp(-((temp - mu) ** 2) / (sigma_p ** 2))

            for i in range(N):
                k_food = 3.0
                Q = k_food * np.random.rand() * (fit[i] / (fitG + 1e-12))

                if Q > 2.0:
                    Cr_food = np.exp(-1.0 / max(Q, 1e-6)) * CrG
                    angle = 2.0 * np.pi * np.random.rand()
                    Cr_new[i] = Cr[i] + Cr_food * p * (np.cos(angle) - np.sin(angle))
                else:
                    Cr_new[i] = (Cr[i] - CrG) * p + p * np.random.rand() * Cr[i]

        # 边界截断与贪婪选择
        Cr_new = np.clip(Cr_new, lb, ub)
        for i in range(N):
            cand_b = binarize(Cr_new[i], dim)
            cand_f = jFitness(X, y, cand_b, opts)
            if cand_f < fit[i]:
                Cr[i] = Cr_new[i].copy()
                Cr_bin[i] = cand_b.copy()
                fit[i] = cand_f

        # ── 3. 交错搜索策略 (Crisscross Strategy, CS) ──
        # 1) 横向交叉 (Horizontal Crossover, HC, Eq. 19-20)
        perm = np.random.permutation(N)
        for idx in range(0, N - 1, 2):
            i1, i2 = perm[idx], perm[idx + 1]
            r1, r2 = np.random.rand(), np.random.rand()
            c1, c2 = np.random.uniform(-1.0, 1.0), np.random.uniform(-1.0, 1.0)

            hc1 = r1 * Cr[i1] + (1.0 - r1) * Cr[i2] + c1 * (Cr[i1] - Cr[i2])
            hc2 = r2 * Cr[i2] + (1.0 - r2) * Cr[i1] + c2 * (Cr[i2] - Cr[i1])

            hc1 = np.clip(hc1, lb, ub)
            hc2 = np.clip(hc2, lb, ub)

            b_hc1 = binarize(hc1, dim)
            f_hc1 = jFitness(X, y, b_hc1, opts)
            if f_hc1 < fit[i1]:
                Cr[i1] = hc1
                Cr_bin[i1] = b_hc1
                fit[i1] = f_hc1

            b_hc2 = binarize(hc2, dim)
            f_hc2 = jFitness(X, y, b_hc2, opts)
            if f_hc2 < fit[i2]:
                Cr[i2] = hc2
                Cr_bin[i2] = b_hc2
                fit[i2] = f_hc2

        # 2) 纵向交叉 (Vertical Crossover, VC, Eq. 21)
        for i in range(N):
            if dim >= 2:
                d1, d2 = np.random.choice(dim, 2, replace=False)
                r_v = np.random.rand()
                vc = Cr[i].copy()
                vc[d1] = r_v * Cr[i, d1] + (1.0 - r_v) * Cr[i, d2]
                vc = np.clip(vc, lb, ub)

                b_vc = binarize(vc, dim)
                f_vc = jFitness(X, y, b_vc, opts)
                if f_vc < fit[i]:
                    Cr[i] = vc
                    Cr_bin[i] = b_vc
                    fit[i] = f_vc

        # 更新全局与局部最优
        cur_best_idx = np.argmin(fit)
        CrL = Cr[cur_best_idx].copy()
        if fit[cur_best_idx] < fitG:
            fitG = float(fit[cur_best_idx])
            CrG = Cr[cur_best_idx].copy()
            CrG_bin = Cr_bin[cur_best_idx].copy()

        curve[t] = fitG

    mask = CrG_bin.astype(bool)
    if not mask.any():
        mask[np.random.choice(dim, min(3, dim), replace=False)] = True

    return {
        "fitG": fitG,
        "nf": int(mask.sum()),
        "mask": mask,
        "curve": curve,
        "nhd_curve": np.zeros(T + 1),
    }
