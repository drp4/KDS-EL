"""
BPSO — Binary Particle Swarm Optimization
==========================================
经典二值 PSO (Kennedy & Eberhart 1997)。
Sigmoid 传输函数将速度映射为选择概率，实现特征选择。
"""
import numpy as np
from utils import jFitness


def run_BPSO(X, y, opts):
    N = opts["N"]
    T = opts["T"]
    dim = X.shape[1]
    w, c1, c2 = 0.9, 2.0, 2.0
    Vmax = 6.0

    P = (np.random.rand(N, dim) < 0.5).astype(float)
    V = np.zeros((N, dim))

    fit = np.array([jFitness(X, y, (P[i] > 0.5).astype(bool), opts)
                    for i in range(N)])
    Pbest, fitP = P.copy(), fit.copy()
    g = np.argmin(fitP)
    Gbest, fitG = Pbest[g].copy(), float(fitP[g])

    curve = np.zeros(T + 1)
    curve[0] = fitG

    for t in range(1, T + 1):
        r1, r2 = np.random.rand(N, dim), np.random.rand(N, dim)
        V = w * V + c1 * r1 * (Pbest - P) + c2 * r2 * (Gbest - P)
        V = np.clip(V, -Vmax, Vmax)

        prob = 1.0 / (1.0 + np.exp(-V))
        P = (np.random.rand(N, dim) < prob).astype(float)

        for i in range(N):
            f = jFitness(X, y, (P[i] > 0.5).astype(bool), opts)
            if f < fitP[i]:
                Pbest[i] = P[i].copy()
                fitP[i] = f
            if f < fitG:
                fitG = float(f)
                Gbest = P[i].copy()

        curve[t] = fitG

    mask = (Gbest > 0.5)
    return {
        "fitG": fitG,
        "nf": int(mask.sum()),
        "curve": curve,
        "nhd_curve": np.zeros(T + 1),
    }
