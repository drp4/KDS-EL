"""
W-MOPSO-FS — Wrapper-Filter hybrid Multi-Objective PSO for Feature Selection
=============================================================================
Wrapper-Filter 混合 MOPSO：将 Filter 特征评分（MI / Fisher Score）注入速度更新，
使高评分特征更可能被选中，低评分特征更可能被排除。

关键特性：
  - 双目标：[分类错误率, 特征比例]
  - Filter 引导的速度偏置：v[j] += filter_bias * score[j]
  - 外部存档 + Pareto Pbest 更新
  - MI 引导初始化
"""
import numpy as np
from utils import jFitness, compute_mi_scores


def dominates(a, b):
    return np.all(a <= b) and np.any(a < b)


def run_W_MOPSO_FS(X, y, opts):
    N = opts["N"]
    T = opts["T"]
    dim = X.shape[1]
    w, c1, c2 = 0.9, 1.5, 1.5
    Vmax = 6.0
    filter_bias = 0.05  # 弱偏置：引导不主导 PSO 动力学
    archive_size = N

    # ── Filter 评分 (MI based) ────────────────────────────────────
    filter_score = compute_mi_scores(X, y)

    # ── MI 引导初始化 ─────────────────────────────────────────────
    init_prob = np.clip(0.15 + 0.7 * filter_score, 0.05, 0.95)
    P = (np.random.rand(N, dim) < init_prob[np.newaxis, :]).astype(float)
    V = np.zeros((N, dim))

    P_fit = np.zeros((N, 2))
    for i in range(N):
        mask = P[i].astype(bool)
        P_fit[i, 0] = jFitness(X, y, mask, opts)
        P_fit[i, 1] = mask.sum() / dim

    Pbest = P.copy()
    Pbest_fit = P_fit.copy()

    # ── 初始化 archive ────────────────────────────────────────────
    archive = []
    archive_fit = []
    for i in range(N):
        is_dominated = any(dominates(a_fit, P_fit[i]) for a_fit in archive_fit)
        if not is_dominated:
            archive = [a for a, a_fit in zip(archive, archive_fit)
                       if not dominates(P_fit[i], a_fit)]
            archive_fit = [a_fit for a_fit in archive_fit
                           if not dominates(P_fit[i], a_fit)]
            archive.append(P[i].copy())
            archive_fit.append(P_fit[i].copy())

    curve = np.zeros(T + 1)
    curve[0] = min(archive_fit, key=lambda x: x[0])[0] if archive_fit else np.min(P_fit[:, 0])

    for t in range(1, T + 1):
        for i in range(N):
            # ── Leader 选择 ───────────────────────────────────────
            if archive:
                arch_arr = np.array(archive_fit)
                # 轮盘赌（极低 error 高概率）
                inv_err = 1.0 / (arch_arr[:, 0] + 0.01)
                probs = inv_err / inv_err.sum()
                leader_idx = np.random.choice(len(archive), p=probs)
                leader = archive[leader_idx].copy()
            else:
                leader = Pbest[i].copy()

            # ── Filter 引导的速度更新 ─────────────────────────────
            r1, r2 = np.random.rand(dim), np.random.rand(dim)
            V[i] = (w * V[i]
                    + c1 * r1 * (Pbest[i] - P[i])
                    + c2 * r2 * (leader - P[i])
                    + filter_bias * (2 * filter_score - 1))  # Filter 偏置
            V[i] = np.clip(V[i], -Vmax, Vmax)

            prob = 1.0 / (1.0 + np.exp(-V[i]))
            P[i] = (np.random.rand(dim) < prob).astype(float)

            # ── 评估 ──────────────────────────────────────────────
            mask = P[i].astype(bool)
            P_fit[i, 0] = jFitness(X, y, mask, opts)
            P_fit[i, 1] = mask.sum() / dim

            # ── Pbest 更新 ────────────────────────────────────────
            if dominates(P_fit[i], Pbest_fit[i]):
                Pbest[i] = P[i].copy()
                Pbest_fit[i] = P_fit[i].copy()
            elif not dominates(Pbest_fit[i], P_fit[i]):
                if np.random.rand() < 0.5:
                    Pbest[i] = P[i].copy()
                    Pbest_fit[i] = P_fit[i].copy()

            # ── Archive 更新 ──────────────────────────────────────
            is_dominated = any(dominates(a_fit, P_fit[i]) for a_fit in archive_fit)
            if not is_dominated:
                archive = [a for a, a_fit in zip(archive, archive_fit)
                           if not dominates(P_fit[i], a_fit)]
                archive_fit = [a_fit for a_fit in archive_fit
                               if not dominates(P_fit[i], a_fit)]
                archive.append(P[i].copy())
                archive_fit.append(P_fit[i].copy())

            # ── Archive 裁剪（拥挤距离，保留边界解） ────────────
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

    # ── 最终选择 ──────────────────────────────────────────────────
    if archive_fit:
        best_idx = np.argmin(np.array(archive_fit)[:, 0])
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
