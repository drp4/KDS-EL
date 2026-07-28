"""
KDS-EL_NoPool — KDS-EL without pool selection (in-place update)
===============================================================
消融对照：评估池化选择 (pool selection) 的贡献。
在 KDS-EL (MI+KER) 基础上，将 2N 池化选择替换为逐对原地更新：
  P_new[i] 与 Pbest[i] 一对一比较，择优保留。
其他组件不变：MI 初始化、权重衰减、KER、自适应重初始化。
"""
import numpy as np
from utils import jFitness, ker_flip, compute_mi_scores


def run_KDS_EL_NoPool(X, y, opts):
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
    curve[0] = fitG

    for t in range(1, T + 1):
        weight *= decay

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

        # 逐对原地更新（替代池化选择）
        for i in range(N):
            fv_n = P_new[i] > thres
            fv_o = Pbest[i] > thres
            fit_new = jFitness(X, y, fv_n, opts)

            # MEL 原始双向权重更新
            if fit_new < fitP[i]:
                inc = fitP[i] - fit_new
                Pbest[i] = P_new[i].copy()
                fitP[i] = fit_new
                change = np.logical_xor(fv_n, fv_o)
                case_emerge = np.where(change & (fv_n > fv_o))[0]
                case_disappear = np.where(change & (fv_n < fv_o))[0]
                for j in case_emerge:
                    weight[j] += inc
                for j in case_disappear:
                    weight[j] -= inc
            else:
                dec = fit_new - fitP[i]
                change = np.logical_xor(fv_o, fv_n)
                case_emerge = np.where(change & (fv_o > fv_n))[0]
                case_disappear = np.where(change & (fv_o < fv_n))[0]
                for j in case_emerge:
                    weight[j] -= dec
                for j in case_disappear:
                    weight[j] += dec

        P = P_new.copy()

        # KER 精英翻转
        for e in np.argsort(fitP)[:opts["elite_k"]]:
            elite_bin = (Pbest[e] > thres).astype(int)
            mutant = ker_flip(weight, elite_bin, flip_count, rand_p)
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

        curve[t] = fitG

    mask = (Gbest > thres)
    return {
        "fitG": fitG,
        "nf": int(mask.sum()),
        "curve": curve,
        "nhd_curve": np.zeros(T + 1),
    }
