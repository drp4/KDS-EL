"""
fMOPSO-FS — Fuzzy Multi-Objective PSO for Feature Selection
============================================================
基于 Han et al. (2024) Neural Processing Letters。
关键特性：
  - MI 引导初始化（利用 compute_mi_scores）
  - Pareto 非支配存档 + 拥挤距离管理
  - 逆误差加权 leader 选择（偏向 low-error 区域）
  - 探索突变（每粒子 5% 概率翻转子集）
  - 速度-位置 PSO 更新
双目标：[分类错误率, 特征比例]。
"""
import numpy as np
from utils import jFitness, compute_mi_scores, fast_nds, crowding_dist


def run_fMOPSO_FS(X, y, opts):
    N = opts["N"]
    T = opts["T"]
    dim = X.shape[1]
    w, c1, c2 = 0.9, 1.5, 1.5
    Vmax = 6.0
    archive_size = N

    # ── MI 引导初始化 ─────────────────────────────────────────────
    mi = compute_mi_scores(X, y)
    init_prob = np.clip(0.15 + 0.7 * mi, 0.05, 0.95)
    P = (np.random.rand(N, dim) < init_prob[np.newaxis, :]).astype(float)
    V = np.zeros((N, dim))

    P_fit = np.zeros((N, 2))
    for i in range(N):
        mask = P[i].astype(bool)
        P_fit[i, 0] = jFitness(X, y, mask, opts)
        P_fit[i, 1] = mask.sum() / dim

    Pbest = P.copy()
    Pbest_fit = P_fit.copy()

    # ── 初始化 archive（Pareto 非支配） ──────────────────────────
    fronts_init = fast_nds(P_fit)
    archive = [P[i].copy() for i in fronts_init[0]]
    archive_fit = [P_fit[i].copy() for i in fronts_init[0]]

    curve = np.zeros(T + 1)
    curve[0] = min(archive_fit, key=lambda x: x[0])[0] if archive_fit else np.min(P_fit[:, 0])

    for t in range(1, T + 1):
        for i in range(N):
            # ── Leader: 从 archive 按 error 加权选择 ──────────────
            # 不使用缓存（archive 在粒子间变化），每次实时计算
            if archive and len(archive) > 0:
                if len(archive) == 1:
                    leader = archive[0].copy()
                else:
                    # 按 error 的倒数加权（error 低 → 概率高）
                    errs = np.array([af[0] for af in archive_fit])
                    inv_err = 1.0 / (errs + 0.01)
                    probs = inv_err / inv_err.sum()
                    leader_idx = np.random.choice(len(archive), p=probs)
                    leader = archive[leader_idx].copy()
            else:
                leader = Pbest[i].copy()

            # ── 速度+位置更新 ─────────────────────────────────────
            r1, r2 = np.random.rand(dim), np.random.rand(dim)
            V[i] = w * V[i] + c1 * r1 * (Pbest[i] - P[i]) + c2 * r2 * (leader - P[i])
            V[i] = np.clip(V[i], -Vmax, Vmax)

            prob = 1.0 / (1.0 + np.exp(-V[i]))
            P[i] = (np.random.rand(dim) < prob).astype(float)

            # ── 探索突变（每粒子 5% 概率翻转子集） ─────────────────
            if np.random.rand() < 0.05:
                n_flip = max(1, int(dim * 0.01))
                flip_idx = np.random.choice(dim, n_flip, replace=False)
                P[i, flip_idx] = 1 - P[i, flip_idx]

            # ── 评估 ──────────────────────────────────────────────
            mask = P[i].astype(bool)
            P_fit[i, 0] = jFitness(X, y, mask, opts)
            P_fit[i, 1] = mask.sum() / dim

            # ── Pbest: Pareto 支配 ───────────────────────────────
            # 在当前存档参考下做支配判断
            if np.all(P_fit[i] <= Pbest_fit[i]) and np.any(P_fit[i] < Pbest_fit[i]):
                Pbest[i] = P[i].copy()
                Pbest_fit[i] = P_fit[i].copy()
            elif not (np.all(Pbest_fit[i] <= P_fit[i]) and np.any(Pbest_fit[i] < P_fit[i])):
                # 互不支配，随机选
                if np.random.rand() < 0.5:
                    Pbest[i] = P[i].copy()
                    Pbest_fit[i] = P_fit[i].copy()

            # ── Archive 更新 (Pareto 支配) ───────────────────────
            dominated_by_archive = False
            new_archive = []
            new_archive_fit = []
            for a, a_fit in zip(archive, archive_fit):
                if np.all(a_fit <= P_fit[i]) and np.any(a_fit < P_fit[i]):
                    # 存档中已有一个支配新解的，不添加
                    dominated_by_archive = True
                if not (np.all(P_fit[i] <= a_fit) and np.any(P_fit[i] < a_fit)):
                    # 保留不被新解支配的存档项
                    new_archive.append(a)
                    new_archive_fit.append(a_fit)
            if not dominated_by_archive:
                new_archive.append(P[i].copy())
                new_archive_fit.append(P_fit[i].copy())
            archive = new_archive
            archive_fit = new_archive_fit

        # ── Archive 裁剪（每代结束，拥挤距离） ────────────────────
        if len(archive) > archive_size:
            arch_arr = np.array(archive_fit)
            cd = np.zeros(len(archive))
            for m in range(2):
                order = np.argsort(arch_arr[:, m])
                cd[order[0]] = cd[order[-1]] = np.inf
                span = arch_arr[order[-1], m] - arch_arr[order[0], m]
                if span > 0:
                    for k in range(1, len(order) - 1):
                        cd[order[k]] += (arch_arr[order[k + 1], m] - arch_arr[order[k - 1], m]) / span
            n_remove = len(archive) - archive_size
            worst = np.argsort(cd)[:n_remove]
            archive = [a for j, a in enumerate(archive) if j not in worst]
            archive_fit = [a_fit for j, a_fit in enumerate(archive_fit) if j not in worst]

        curr_best = min(archive_fit, key=lambda x: x[0])[0] if archive_fit else np.min(P_fit[:, 0])
        curve[t] = curr_best

    # ── 最终从 archive 选最佳解 ──────────────────────────────────
    if archive_fit:
        arch_arr = np.array(archive_fit)
        best_idx = np.argmin(arch_arr[:, 0])
        Gbest = (archive[best_idx] > 0.5).astype(bool)
        fitG = float(archive_fit[best_idx][0])
    else:
        best_idx = np.argmin(Pbest_fit[:, 0])
        Gbest = (Pbest[best_idx] > 0.5).astype(bool)
        fitG = float(Pbest_fit[best_idx, 0])

    return {
        "fitG": fitG,
        "nf": int(Gbest.sum()),
        "curve": curve,
        "nhd_curve": np.zeros(T + 1),
    }
