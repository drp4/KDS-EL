"""
KDS-EL (Proposed)
===================
完整框架：MEL + DRS (EMDO多样性选择) + KER (KGEF精英微调)。
对应论文提出的 KDS-EL 方法。
"""
import numpy as np
from utils import jFitness, pairwise_nhd, emdo_select, kgef_flip, compute_mi_scores


def run_KDS_EL(X, y, opts):
    lb, ub, thres = 0.0, 1.0, opts["thres"]
    c1 = c2 = c3 = 2.0
    w = 0.9
    Vmax = (ub - lb) / 2
    N = opts["N"]
    T = opts["T"]
    dim = X.shape[1]
    decay = opts["weight_decay"]
    flip_count = max(1, int(opts["flip_frac"] * dim))
    rand_p = opts["rand_flip_p"]
    patience = opts.get("stall_patience", 20)

    weight = np.zeros(dim)

    # MI 引导初始化（一半 MI + 一半随机）
    mi = compute_mi_scores(X, y)
    half = N // 2
    P = np.zeros((N, dim))
    P[:half] = np.clip(mi + np.random.normal(0, 0.1, (half, dim)), lb, ub)
    P[half:] = np.random.uniform(lb, ub, (N - half, dim))
    V = np.zeros((N, dim))

    subSize = N // 2

    fit = np.array([jFitness(X, y, (P[i] > thres).astype(bool), opts)
                    for i in range(N)])
    fitP = fit.copy()
    Pbest = P.copy()
    Gbest = P[np.argmin(fit)].copy()
    fitG = float(np.min(fit))
    stall_counter = 0

    curve = np.zeros(T + 1)
    nhd_curve = np.zeros(T + 1)
    curve[0] = fitG

    for t in range(1, T + 1):
        weight *= decay
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

        # 权重更新（EMDO选择前，P_new[i] ↔ Pbest[i] 对应正确）
        for i in range(N):
            fv_n = (P_new[i] > thres)
            fv_o = (Pbest[i] > thres)
            fit_new = pool_fit[N + i]
            if fit_new < fitP[i]:
                inc = fitP[i] - fit_new
                change = np.logical_xor(fv_n, fv_o)
                weight[change & (fv_n > fv_o)] += inc
                weight[change & (fv_n < fv_o)] -= inc

        # EMDO 选择（联合优化适应度 + 多样性）
        sel = emdo_select(pool_fit, nhd_mat, N, alpha_cd)

        # 精英保护：池中纯 fitness 最好的个体必须存活
        elite_n = max(1, N // 4)
        top_fit = np.argsort(pool_fit)[:elite_n]
        missing = [e for e in top_fit if e not in sel]
        if missing:
            worst = np.argsort(-pool_fit[sel])[:len(missing)]
            sel[worst] = missing

        P = pool[sel]
        fit_sel = pool_fit[sel]

        improved = fit_sel < fitP
        Pbest = np.where(improved[:, None], P, Pbest)
        fitP = np.minimum(fit_sel, fitP)

        # KGEF 精英微调
        for e in np.argsort(fitP)[:opts["elite_k"]]:
            elite_bin = (Pbest[e] > thres).astype(int)
            mutant = kgef_flip(weight, elite_bin, flip_count, rand_p)
            mfit = jFitness(X, y, mutant.astype(bool), opts)
            if mfit < fitP[e]:
                Pbest[e] = mutant
                fitP[e] = mfit

        bi = np.argmin(fitP)
        if fitP[bi] < fitG:
            fitG = float(fitP[bi])
            Gbest = Pbest[bi].copy()
            stall_counter = 0
        else:
            stall_counter += 1

        # 自适应重初始化：long stall 时重启下半种群
        if stall_counter >= patience:
            order = np.argsort(fitP)
            keep = order[:half]
            restart = order[half:]
            for idx in restart:
                Pbest[idx] = np.clip(mi + np.random.normal(0, 0.1, dim), lb, ub)
                P[idx] = Pbest[idx].copy()
                fitP[idx] = jFitness(X, y, (Pbest[idx] > thres).astype(bool), opts)
            stall_counter = 0

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
