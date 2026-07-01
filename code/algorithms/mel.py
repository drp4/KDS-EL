"""
MEL — Multi-task Ensemble Learning (baseline)
=============================================
双子群多任务 PSO：
  - 子群1: 标准 PSO 速度-位置更新（连续空间）
  - 子群2: 基于权重矩阵的概率采样（二进制特征选择）
无池选择，原地更新。权重对改进/未改进解均进行双向调整。

评估函数使用统一的 StratifiedKFold + jFitness（与其他算法一致）。
"""
import numpy as np
from sklearn.neighbors import KNeighborsClassifier
from utils import jFitness


# ════════════════════════════════════════════════════════════════════════
# MEL 主算法
# ════════════════════════════════════════════════════════════════════════

def run_MEL(X, y, opts):
    lb, ub = 0.0, 1.0
    thres = opts["thres"]
    c1 = c2 = c3 = 2.0
    w = 0.9
    N = opts["N"]
    T = opts["T"]
    dim = X.shape[1]

    Vmax = (ub - lb) / 2
    numSub = 2
    subSize = N // numSub

    # 特征权重矩阵
    weight = np.zeros(dim)

    # 初始化
    P = np.random.uniform(lb, ub, (N, dim))
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

    curve = np.zeros(T + 1)
    curve[0] = fitG

    for t in range(1, T + 1):
        k = 0
        for i in range(N):
            if k == 0:  # 子群1: PSO 速度-位置更新（逐维）
                for d in range(dim):
                    r1, r2, r3 = np.random.rand(), np.random.rand(), np.random.rand()
                    VB = (w * V[i, d]
                          + c1 * r1 * (Pbest[i, d] - P[i, d])
                          + c2 * r2 * (Gbest[d] - P[i, d])
                          + c3 * r3 * (Xsub[1, d] - P[i, d]))
                    V[i, d] = np.clip(VB, -Vmax, Vmax)
                    P[i, d] = np.clip(P[i, d] + V[i, d], lb, ub)
            else:  # 子群2: 权重概率采样（二进制）
                vf = np.maximum(weight, 0.0)
                sv = vf.sum()
                if sv > 0:
                    for d in range(dim):
                        P[i, d] = 1.0 if vf[d] / sv > np.random.rand() else 0.0
                else:
                    P[i] = (np.random.rand(dim) < 0.5).astype(float)

            # 适应度评估
            fv_n = P[i] > thres
            fit[i] = fun(X, y, fv_n, opts)
            fv_o = Pbest[i] > thres

            # Pbest 更新 + 权重调整
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

        curve[t] = fitG

    mask = (Gbest > thres)
    return {
        "fitG": fitG,
        "nf": int(mask.sum()),
        "curve": curve,
        "nhd_curve": np.zeros(T + 1),
    }
