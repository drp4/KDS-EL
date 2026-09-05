"""
DENCA-SO — Evolutionary Filter Approach to Feature Selection (Single-Objective)
================================================================================
Reference:
  Hancer, E., Xue, B., & Zhang, M. (2023).
  An evolutionary filter approach to feature selection in classification
  for both single- and multi-objective scenarios.
  Knowledge-Based Systems, 280, 111008.
  DOI: 10.1016/j.knosys.2023.111008

Official Repository:
  https://github.com/ehancer06/DENCA (single_objective_scenario/derun.m)

Algorithmic Core:
  1. Feature Weighting via NCFS (Neighborhood Component Feature Selection):
     Learns continuous weights w via L-BFGS optimization of regularized leave-one-out
     classification accuracy, then normalizes weights via Min-Max to H in [0, 1].
  2. Filter Objective Function (Eq. 12 in paper):
     Cost(x) = -W * sum_{j in S} H_j + (1 - W) * (|S| / D),
     where S = {j | x_j > 0.5}, W = 0.05 if D > 60 else 0.10.
  3. Continuous Differential Evolution (DE/rand/1/bin):
     F = 0.5, CR = 0.2, pop_size = N, continuous variables in [0, 1]^D.
"""
import numpy as np
from scipy.optimize import minimize
from utils import jFitness


def compute_ncfs_weights(X, y, lambd=0.01, max_iter=50):
    """
    通过 Neighborhood Component Analysis (NCFS) 计算特征权重。
    利用 L-BFGS-B 优化留一法期望分类精度，辅以 L2 正则化。
    """
    N_samp, D = X.shape

    # 样本特征标准化
    std = np.std(X, axis=0)
    std[std == 0] = 1.0
    X_norm = ((X - np.mean(X, axis=0)) / std).astype(np.float32)

    # 类别掩码
    mask_same = (y[:, None] == y[None, :])
    np.fill_diagonal(mask_same, False)
    mask_other = ~np.eye(N_samp, dtype=bool)

    # 计算逐特征样本间平方差 (N_samp, N_samp, D)
    diff_sq = (X_norm[:, None, :] - X_norm[None, :, :]) ** 2  # (N, N, D)

    def loss_and_grad(w):
        w_vec = w.astype(np.float32)
        w2 = w_vec ** 2

        # 距离矩阵 d_ij = sum_k w_k^2 (x_ik - x_jk)^2
        d = np.tensordot(diff_sq, w2, axes=([2], [0]))  # (N, N)

        # 数值稳定性平移
        d_min = np.min(d, axis=1, keepdims=True)
        exp_d = np.exp(-(d - d_min)) * mask_other
        sum_exp = np.sum(exp_d, axis=1, keepdims=True) + 1e-12
        P = exp_d / sum_exp  # (N, N)

        # 期望同类留一法概率
        p_i = np.sum(P * mask_same, axis=1)  # (N,)
        obj = -(np.mean(p_i) - lambd * np.sum(w2))

        # 梯度计算
        sum_P_diff = np.einsum('ij,ijk->ik', P, diff_sq)
        sum_P_same_diff = np.einsum('ij,ijk->ik', P * mask_same, diff_sq)
        grad_p_i = 2.0 * w_vec[None, :] * (p_i[:, None] * sum_P_diff - sum_P_same_diff)
        grad = -(np.mean(grad_p_i, axis=0) - 2.0 * lambd * w_vec)

        return float(obj), grad.astype(np.float64)

    w0 = np.ones(D, dtype=np.float64) / np.sqrt(max(D, 1))
    try:
        res = minimize(
            loss_and_grad,
            w0,
            method='L-BFGS-B',
            jac=True,
            bounds=[(0.0, None) for _ in range(D)],
            options={'maxiter': max_iter, 'ftol': 1e-4, 'gtol': 1e-4}
        )
        weights = np.abs(res.x)
    except Exception:
        # 若数值求解异常，使用 F-score 作为稳健回退
        weights = np.zeros(D)
        classes = np.unique(y)
        if len(classes) > 1:
            overall_mean = np.mean(X_norm, axis=0)
            for c in classes:
                mask_c = (y == c)
                nc = np.sum(mask_c)
                if nc > 0:
                    mean_c = np.mean(X_norm[mask_c], axis=0)
                    weights += nc * (mean_c - overall_mean) ** 2

    # Min-max 归一化至 [0, 1] (式 11)
    w_min, w_max = np.min(weights), np.max(weights)
    if w_max > w_min:
        H = (weights - w_min) / (w_max - w_min)
    else:
        H = np.ones(D) / D

    return H


def filter_sz(x_cont, H, W, D):
    """DENCA 过滤式目标函数 (Eq. 12)。"""
    mask = (x_cont > 0.5)
    s_size = int(mask.sum())
    if s_size == 0:
        return 1e9  # 空特征集严重惩罚
    return -W * np.sum(H[mask]) + (1.0 - W) * (s_size / D)


def run_DENCA_SO(X, y, opts):
    """
    运行 DENCA-SO 算法。
    """
    N = opts["N"]
    T = opts["T"]
    D = X.shape[1]

    # 1. 预计算 NCFS 归一化特征重要性权重 H
    H = compute_ncfs_weights(X, y, lambd=opts.get("ncfs_lambda", 0.01), max_iter=50)

    # 依据数据维度确定权衡参数 W (式 12, 论文第 4.2 节)
    W = 0.05 if D > 60 else 0.10
    F = 0.5
    CR = 0.2

    # 2. 初始化种群 (式 1)
    P = np.random.uniform(0.0, 1.0, (N, D))

    # 计算初始种群的过滤式适应度
    fit = np.array([filter_sz(P[i], H, W, D) for i in range(N)])

    best_idx = np.argmin(fit)
    Gbest = P[best_idx].copy()
    best_filter_fit = fit[best_idx]

    curve = np.zeros(T + 1)

    # 初始评估全局最优解的包装式适应度
    best_mask = (Gbest > 0.5)
    if not best_mask.any():
        best_mask[np.argmax(H)] = True
    fitG = float(jFitness(X, y, best_mask, opts))
    curve[0] = fitG

    # 3. 差分进化搜索主循环 (DE/rand/1/bin)
    for t in range(1, T + 1):
        for i in range(N):
            candidates = [idx for idx in range(N) if idx != i]
            r1, r2, r3 = np.random.choice(candidates, 3, replace=False)

            # 变异 (式 2)
            v = np.clip(P[r1] + F * (P[r2] - P[r3]), 0.0, 1.0)

            # 二项式交叉 (式 3)
            j_rand = np.random.randint(0, D)
            cross_mask = (np.random.rand(D) < CR)
            cross_mask[j_rand] = True
            u = np.where(cross_mask, v, P[i])

            # 评价试验向量
            f_u = filter_sz(u, H, W, D)

            # 贪婪选择保留
            if f_u <= fit[i]:
                P[i] = u
                fit[i] = f_u
                if f_u < best_filter_fit:
                    best_filter_fit = f_u
                    Gbest = u.copy()

        # 每代更新最优解并评估其实际包装分类适应度
        best_mask = (Gbest > 0.5)
        if not best_mask.any():
            best_mask[np.argmax(H)] = True
        fitG = float(jFitness(X, y, best_mask, opts))
        curve[t] = fitG

    final_mask = (Gbest > 0.5)
    if not final_mask.any():
        final_mask[np.argmax(H)] = True

    return {
        "fitG": fitG,
        "nf": int(final_mask.sum()),
        "mask": final_mask,
        "curve": curve,
        "nhd_curve": np.zeros(T + 1),
    }
