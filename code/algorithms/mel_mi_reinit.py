"""
MEL_MI — MEL + MI 引导初始化 + 自适应重初始化（无 DRS，无 KER）
=============================================================================
消融对照：量化 MI 初始化 + 自适应重初始化的基础贡献。
在原始 MEL 双子群 PSO 基础上，只加入：
  - MI 引导初始化（一半 MI + 一半随机）
  - 自适应重初始化（stall 时重启下半种群，MI 引导）
不含 DRS 和 KER。
"""
import numpy as np
from utils import jFitness, compute_mi_scores


def run_MEL_MI(X, y, opts):
    lb, ub = 0.0, 1.0
    thres = opts["thres"]
    c1 = c2 = c3 = 2.0
    w = 0.9
    N = opts["N"]
    T = opts["T"]
    dim = X.shape[1]
    patience = opts.get("stall_patience", 20)

    Vmax = (ub - lb) / 2
    numSub = 2
    subSize = N // numSub
    half = N // 2

    # 特征权重矩阵（MEL 原始逻辑）
    weight = np.zeros(dim)

    # ── MI 引导初始化（一半 MI + 一半随机，与 KDS-EL 变体一致）──
    mi = compute_mi_scores(X, y)
    P = np.zeros((N, dim))
    P[:half] = np.clip(mi + np.random.normal(0, 0.1, (half, dim)), lb, ub)
    P[half:] = np.random.uniform(lb, ub, (N - half, dim))
    V = np.zeros((N, dim))

    fit = np.zeros(N)
    fitG = np.inf
    fitSub = np.ones(numSub) * np.inf
    Xsub = np.zeros((numSub, dim))

    fun = jFitness

    # 初始评估 + 子群最优 & 全局最优
    k = 0
    for i in range(N):
        fit[i] = fun(X, y, P[i] > thres, opts)
        if fit[i] < fitSub[k]:
            Xsub[k] = P[i].copy()
            fitSub[k] = fit[i]
        if (i + 1) % subSize == 0:
            k += 1
        if fit[i] < fitG:
            Gbest = P[i].copy()
            fitG = float(fit[i])

    Pbest = P.copy()
    fitP = fit.copy()
    stall_counter = 0

    curve = np.zeros(T + 1)
    curve[0] = fitG

    for t in range(1, T + 1):
        prev_fitG = fitG  # 记录本轮开始前的全局最优

        k = 0
        for i in range(N):
            if k == 0:  # 子群1: PSO 速度-位置更新
                r1 = np.random.rand(dim)
                r2 = np.random.rand(dim)
                r3 = np.random.rand(dim)
                V[i] = np.clip(
                    w * V[i]
                    + c1 * r1 * (Pbest[i] - P[i])
                    + c2 * r2 * (Gbest - P[i])
                    + c3 * r3 * (Xsub[1] - P[i]),
                    -Vmax, Vmax,
                )
                P[i] = np.clip(P[i] + V[i], lb, ub)
            else:  # 子群2: 权重概率采样
                vf = np.maximum(weight, 0.0)
                sv = vf.sum()
                if sv > 0:
                    prob = vf / sv
                    P[i] = (np.random.rand(dim) < prob).astype(float)
                else:
                    P[i] = (np.random.rand(dim) < 0.5).astype(float)

            # 适应度评估
            fv_n = P[i] > thres
            fit[i] = fun(X, y, fv_n, opts)
            fv_o = Pbest[i] > thres

            # ── Pbest 更新 + MEL 原始双向权重调整 ──
            if fit[i] < fitP[i]:
                inc = fitP[i] - fit[i]
                Pbest[i] = P[i].copy()
                fitP[i] = fit[i]
                change = np.logical_xor(fv_n, fv_o)
                case_emerge = np.where(change & (fv_n > fv_o))[0]
                case_disappear = np.where(change & (fv_n < fv_o))[0]
                for j in case_emerge:
                    weight[j] += inc
                for j in case_disappear:
                    weight[j] -= inc
            else:
                dec = fit[i] - fitP[i]
                change = np.logical_xor(fv_o, fv_n)
                case_emerge = np.where(change & (fv_o > fv_n))[0]
                case_disappear = np.where(change & (fv_o < fv_n))[0]
                for j in case_emerge:
                    weight[j] -= dec
                for j in case_disappear:
                    weight[j] += dec

            # 子群最优更新
            if fit[i] < fitSub[k]:
                Xsub[k] = P[i].copy()
                fitSub[k] = fit[i]

            # 子群切换
            if (i + 1) % subSize == 0:
                k += 1

            # 全局最优更新（基于 Pbest）
            if fitP[i] < fitG:
                Gbest = Pbest[i].copy()
                fitG = float(fitP[i])

        # ── 自适应重初始化（与 KDS-EL 变体逻辑一致）──
        if fitG < prev_fitG:
            stall_counter = 0
        else:
            stall_counter += 1

        if stall_counter >= patience:
            order = np.argsort(fitP)
            keep = order[:half]
            restart = order[half:]
            for idx in restart:
                Pbest[idx] = np.clip(
                    mi + np.random.normal(0, 0.1, dim), lb, ub
                )
                P[idx] = Pbest[idx].copy()
                fitP[idx] = jFitness(X, y, (Pbest[idx] > thres).astype(bool), opts)
            stall_counter = 0

        curve[t] = fitG

    mask = Gbest > thres
    return {
        "fitG": fitG,
        "nf": int(mask.sum()),
        "curve": curve,
        "nhd_curve": np.zeros(T + 1),
    }
