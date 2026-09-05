"""
KDS-EL_TwoPhase — NoPool + 两阶段权重调度策略 (TPS)
===================================================
在 KDS-EL_NoPool (MI+KER+原地更新) 基础上加入:
  阶段 1 (前 70% 迭代): ws=[0.70, 0.30] 强力压缩特征维度
  阶段 2 (后 30% 迭代): ws=[0.95, 0.05] 精细提升分类精度
  边界处理: 阶段切换瞬间使用阶段 2 权重重新标定全部历史 Pbest，消除尺度割裂。
"""
import numpy as np
from sklearn.neighbors import KNeighborsClassifier
from sklearn.model_selection import StratifiedKFold
from utils import ker_flip, compute_mi_scores


def jFitness_raw(X, y, mask, opts):
    """纯 KNN 误差率，不含特征数惩罚（ws 加权在调用侧完成）。"""
    nf = int(mask.sum())
    if nf < 3:
        return 1.0

    min_class = int(np.min(np.bincount(y)))
    n_splits = min(opts["cv_splits"], min_class)
    if n_splits < 2:
        return 1.0

    skf = StratifiedKFold(
        n_splits=n_splits,
        shuffle=opts["cv_shuffle"],
        random_state=opts["cv_random_state"]
    )
    acc = []
    for tr, te in skf.split(X, y):
        clf = KNeighborsClassifier(n_neighbors=opts["k"])
        clf.fit(X[:, mask][tr], y[tr])
        acc.append((clf.predict(X[:, mask][te]) == y[te]).mean())
    return 1.0 - float(np.mean(acc))


def run_KDS_EL_TwoPhase(X, y, opts):
    lb, ub, thres = 0.0, 1.0, opts["thres"]
    c1 = c2 = c3 = 2.0
    w = 0.9
    Vmax = (ub - lb) / 2
    N = opts["N"]
    T = opts["T"]
    dim = X.shape[1]
    decay = opts.get("weight_decay", 0.99)
    flip_count = max(1, int(opts.get("flip_frac", 0.01) * dim))
    rand_p = opts.get("rand_flip_p", 0.10)
    patience = opts.get("stall_patience", 20)

    weight = np.zeros(dim)

    mi = compute_mi_scores(X, y)
    half = N // 2
    P = np.zeros((N, dim))
    P[:half] = np.clip(mi + np.random.normal(0, 0.1, (half, dim)), lb, ub)
    P[half:] = np.random.uniform(lb, ub, (N - half, dim))
    V = np.zeros((N, dim))

    subSize = N // 2

    # Phase 1 用偏特征压缩的 ws; Phase 2 用偏精度的 ws
    ws1 = opts.get("ws_phase1", [0.70, 0.30])
    ws2 = opts.get("ws_phase2", [0.95, 0.05])
    switch_t = int(opts.get("phase_switch", 0.7) * T)

    def eval_fitness_with_t(mask, current_t):
        nf = int(mask.sum())
        if nf < 3:
            return 1.0 + (3 - nf) * 0.1
        ws = ws2 if current_t > switch_t else ws1
        return ws[0] * jFitness_raw(X, y, mask, opts) + ws[1] * (nf / X.shape[1])

    # 初始评估 (Phase 1 权重)
    fit = np.array([eval_fitness_with_t(P[i] > thres, 0) for i in range(N)])
    fitP = fit.copy()
    Pbest = P.copy()
    Gbest = P[np.argmin(fit)].copy()
    fitG = float(np.min(fit))
    stall_counter = 0

    curve = np.zeros(T + 1)
    curve[0] = fitG

    for t in range(1, T + 1):
        # ── 阶段切换边界处理：统一以 Phase 2 权重重新评价所有 Pbest, fitP 与 Gbest ──
        if t == switch_t + 1:
            for i in range(N):
                fitP[i] = eval_fitness_with_t(Pbest[i] > thres, t)
            bi = np.argmin(fitP)
            Gbest = Pbest[bi].copy()
            fitG = float(fitP[bi])
            stall_counter = 0

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

        for i in range(N):
            fv_n = P_new[i] > thres
            fv_o = Pbest[i] > thres
            fit_new = eval_fitness_with_t(fv_n, t)

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

        # 精英变异 (KER)
        for e in np.argsort(fitP)[:opts.get("elite_k", 3)]:
            elite_bin = (Pbest[e] > thres).astype(int)
            mutant = ker_flip(weight, elite_bin, flip_count, rand_p)
            mfit = eval_fitness_with_t(mutant.astype(bool), t)
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

        # 停滞重启
        if stall_counter >= patience:
            order = np.argsort(fitP)
            keep = order[:half]
            restart = order[half:]
            for idx in restart:
                Pbest[idx] = np.clip(mi + np.random.normal(0, 0.1, dim), lb, ub)
                P[idx] = Pbest[idx].copy()
                fitP[idx] = eval_fitness_with_t(Pbest[idx] > thres, t)
            stall_counter = 0

        curve[t] = fitG

    mask = (Gbest > thres).astype(bool)
    if not mask.any():
        mask[np.argmax(Gbest)] = True

    return {
        "fitG": fitG,
        "nf": int(mask.sum()),
        "mask": mask,
        "curve": curve,
        "nhd_curve": np.zeros(T + 1),
    }
