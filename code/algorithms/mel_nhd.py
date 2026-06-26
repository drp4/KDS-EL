"""
MEL_NHD — MEL with Diversity-based Replacement Selection (DRS)
===============================================================
在 MEL 基础上，用 EMDO (Elite Multi-objective Diversity Optimization)
替代贪婪选择，联合优化适应度和种群多样性 (NHD)。
对应论文中的 KDS-EL/DRS。
"""
import numpy as np
from utils import jFitness, pairwise_nhd, emdo_select


def run_MEL_NHD(X, y, opts):
    lb, ub, thres = 0.0, 1.0, opts["thres"]
    c1 = c2 = c3 = 2.0
    w = 0.9
    Vmax = (ub - lb) / 2
    N = opts["N"]
    T = opts["T"]
    dim = X.shape[1]

    weight = np.zeros(dim)
    P = np.random.uniform(lb, ub, (N, dim))
    V = np.zeros((N, dim))

    subSize = N // 2

    fit = np.array([jFitness(X, y, (P[i] > thres).astype(bool), opts)
                    for i in range(N)])
    fitP = fit.copy()
    Pbest = P.copy()
    Gbest = P[np.argmin(fit)].copy()
    fitG = float(np.min(fit))

    curve = np.zeros(T + 1)
    nhd_curve = np.zeros(T + 1)
    curve[0] = fitG

    for t in range(1, T + 1):
        alpha_cd = (t / T) ** 2

        P_new = P.copy()
        Xsub_best = Pbest[subSize + np.argmin(fitP[subSize:])].copy()

        for i in range(N):
            if i < subSize:
                r1, r2, r3 = np.random.rand(dim), np.random.rand(dim), np.random.rand(dim)
                V[i] = np.clip(
                    w * V[i] + c1 * r1 * (Pbest[i] - P[i])
                    + c2 * r2 * (Gbest - P[i])
                    + c3 * r3 * (Xsub_best - P[i]),
                    -Vmax, Vmax,
                )
                P_new[i] = np.clip(P[i] + V[i], lb, ub)
            else:
                vf = np.maximum(weight, 0.0)
                sv = vf.sum()
                prob = vf / sv if sv > 0 else np.full(dim, 0.5)
                P_new[i] = (np.random.rand(dim) < prob).astype(float)

        # EMDO 选择（联合优化适应度 + 多样性）
        pool = np.vstack([Pbest, P_new])
        pool_bin = (pool > thres).astype(int)
        pool_fit = np.array([jFitness(X, y, pool_bin[i].astype(bool), opts)
                             for i in range(2 * N)])
        nhd_mat = pairwise_nhd(pool_bin)

        sel = emdo_select(pool_fit, nhd_mat, N, alpha_cd)
        P = pool[sel]
        fit_sel = pool_fit[sel]
        bin_sel = pool_bin[sel].astype(bool)

        # 权重更新
        for i in range(N):
            fv_n = bin_sel[i]
            fv_o = (Pbest[i] > thres)
            if fit_sel[i] < fitP[i]:
                inc = fitP[i] - fit_sel[i]
                change = np.logical_xor(fv_n, fv_o)
                weight[change & (fv_n > fv_o)] += inc
                weight[change & (fv_n < fv_o)] -= inc

        improved = fit_sel < fitP
        Pbest = np.where(improved[:, None], P, Pbest)
        fitP = np.minimum(fit_sel, fitP)

        bi = np.argmin(fitP)
        if fitP[bi] < fitG:
            fitG = float(fitP[bi])
            Gbest = Pbest[bi].copy()

        # 记录种群 NHD 多样性
        sb = (Pbest > thres).astype(int)
        nm = pairwise_nhd(sb)
        nhd_curve[t] = nm.sum() / (N * (N - 1)) if N > 1 else 0.0
        curve[t] = fitG

    mask = (Gbest > thres)
    return {
        "fitG": fitG,
        "nf": int(mask.sum()),
        "curve": curve,
        "nhd_curve": nhd_curve,
    }
