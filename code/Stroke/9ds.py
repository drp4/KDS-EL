# =========================
# Cell 1: ALL 7 methods, 9 datasets (exclude Stroke), resume-only (skip done)
ONLY_DATASETS = ["Adenoma","ALL_AML","ALL3","ALL4","CNS","Colon","DLBCL","Leukaemia","Lymphoma"]
MAX_TASKS = 200
# =========================

import os, csv, warnings
import numpy as np
from time import time
from sklearn.neighbors import KNeighborsClassifier
from sklearn.model_selection import StratifiedKFold

warnings.filterwarnings("ignore")
np.seterr(all="ignore")

# ── Paths ───────────────────────────────────────────────────────────────────
DATA_DIR   = "/kaggle/input/datasets/eminz132/dataset/Datasets_part1"
OUT_DIR    = "/kaggle/working"
CURVES_DIR = os.path.join(OUT_DIR, "curves_all_rerun_stratified")
CSV_PATH   = os.path.join(OUT_DIR, "results_all_rerun_stratified.csv")
os.makedirs(CURVES_DIR, exist_ok=True)

# ── Config (MUST match Cell 2) ──────────────────────────────────────────────
NUM_RUNS  = 10
SEED_BASE = 42

OPTS = {
    "k": 3, "N": 20, "T": 100, "thres": 0.6,
    "ws": [0.9, 0.1], "weight_decay": 0.99,
    "cv_splits": 5, "cv_shuffle": True, "cv_random_state": 42
}
CSV_FIELDS = ["Version","Dataset","Run","Accuracy","Num_Features","Avg_NHD","Time_sec"]

# ── Loader ──────────────────────────────────────────────────────────────────
LABEL_START_COL = {"CNS": 3, "MLL": 2}
DATA_START_COL  = {"CNS": 3, "MLL": 2}

def _parse_srbct_label(s):
    for p in ["EWS","RMS","NB","BL"]:
        if s.startswith(p): return p
    return s

def _parse_mll_label(s):
    for p in ["ALL","MLL","AML"]:
        if s.startswith(p): return p
    return s

def load_dataset(p_name):
    fp = os.path.join(DATA_DIR, f"{p_name}.txt")
    if not os.path.exists(fp):
        raise FileNotFoundError(fp)
    lines = open(fp, "r").read().splitlines()
    lbl_start  = LABEL_START_COL.get(p_name, 1)
    data_start = DATA_START_COL.get(p_name, 1)

    header = lines[0].strip().split("\t")
    labels_raw = [h for h in header[lbl_start:] if h.strip() != ""]
    if p_name == "SRBCT":
        labels_raw = [_parse_srbct_label(s) for s in labels_raw]
    elif p_name == "MLL":
        labels_raw = [_parse_mll_label(s) for s in labels_raw]

    classes = sorted(set(labels_raw))
    cmap = {c:i for i,c in enumerate(classes)}
    y = np.array([cmap[s] for s in labels_raw], dtype=int)
    n = len(y)

    rows = []
    for line in lines[1:]:
        parts = line.rstrip("\n").split("\t")
        vals = [p for p in parts[data_start:] if p.strip() != ""]
        if len(vals) != n:
            continue
        try:
            rows.append([float(x) for x in vals])
        except ValueError:
            continue

    X = np.array(rows, dtype=float).T
    assert X.shape[0] == n
    return X, y

# ── Fitness (Stratified CV) ─────────────────────────────────────────────────
def jwrapper_KNN(sFeat, y, opts):
    k = opts.get("k", 3)
    skf = StratifiedKFold(
        n_splits=opts.get("cv_splits", 5),
        shuffle=opts.get("cv_shuffle", True),
        random_state=opts.get("cv_random_state", 42),
    )
    acc = []
    for tr, te in skf.split(sFeat, y):
        mdl = KNeighborsClassifier(n_neighbors=k)
        mdl.fit(sFeat[tr], y[tr])
        acc.append((mdl.predict(sFeat[te]) == y[te]).mean())
    return 1.0 - float(np.mean(acc))

def jFitnessFunction(X, y, mask_bool, opts):
    ws = opts.get("ws", [0.9, 0.1])
    nf = int(np.sum(mask_bool))
    if nf < 3:
        return 1.0 + (3 - nf) * 0.1
    err = jwrapper_KNN(X[:, mask_bool], y, opts)
    return ws[0] * err + ws[1] * (nf / X.shape[1])

# ── NHD / EMDO ──────────────────────────────────────────────────────────────
def pairwise_nhd(X_bin):
    X_bin = X_bin.astype(np.float32)
    inter = X_bin @ X_bin.T
    sums  = X_bin.sum(axis=1)
    union = sums[:, None] + sums[None, :] - inter
    ahd   = sums[:, None] + sums[None, :] - 2.0 * inter
    return ahd / np.maximum(union, 1.0)

def fast_nds(objectives):
    N  = objectives.shape[0]
    dc = np.zeros(N, dtype=int)
    ds = [[] for _ in range(N)]
    fronts = [[]]
    for i in range(N):
        for j in range(N):
            if i == j:
                continue
            if np.all(objectives[i] <= objectives[j]) and np.any(objectives[i] < objectives[j]):
                ds[i].append(j)
            elif np.all(objectives[j] <= objectives[i]) and np.any(objectives[j] < objectives[i]):
                dc[i] += 1
        if dc[i] == 0:
            fronts[0].append(i)
    cf = 0
    while fronts[cf]:
        nf = []
        for i in fronts[cf]:
            for j in ds[i]:
                dc[j] -= 1
                if dc[j] == 0:
                    nf.append(j)
        cf += 1
        fronts.append(nf)
    if not fronts[-1]:
        fronts.pop()
    return fronts

def crowding_dist(objectives, front):
    l = len(front)
    cd = {idx: 0.0 for idx in front}
    for m in range(objectives.shape[1]):
        sf = sorted(front, key=lambda i: objectives[i, m])
        cd[sf[0]] = cd[sf[-1]] = np.inf
        span = objectives[sf[-1], m] - objectives[sf[0], m]
        if span == 0:
            continue
        for k in range(1, l - 1):
            cd[sf[k]] += (objectives[sf[k+1], m] - objectives[sf[k-1], m]) / span
    return cd

def emdo_select(pool_fit, nhd_matrix, N, alpha_cd):
    pool_nhd = nhd_matrix.mean(axis=1)
    objectives = np.column_stack([pool_fit, -pool_nhd])
    fronts = fast_nds(objectives)

    selected = []
    for front in fronts:
        if len(selected) + len(front) <= N:
            selected.extend(front)
        else:
            needed = N - len(selected)
            cd = crowding_dist(objectives, front)
            cd_v = np.array([cd[i] for i in front])

            fin = cd_v[np.isfinite(cd_v)]
            mc = np.max(fin) if len(fin) > 0 else 0.0
            cd_n = np.where(np.isfinite(cd_v), (cd_v / mc if mc > 0 else 0.0), 1.0)

            hd_v = np.array([pool_nhd[i] for i in front])
            mh = np.max(hd_v)
            hd_n = hd_v / mh if mh > 0 else np.zeros(len(front))

            comb = alpha_cd * cd_n + (1.0 - alpha_cd) * hd_n
            order = np.argsort(-comb)
            selected.extend([front[order[k]] for k in range(needed)])
            break
    return np.array(selected)

# ── 7 runners ───────────────────────────────────────────────────────────────
def run_BPSO(X, y, opts):
    N = opts["N"]; T = opts["T"]; dim = X.shape[1]
    w, c1, c2 = 0.9, 2.0, 2.0; Vmax = 6.0
    P = (np.random.rand(N, dim) < 0.5).astype(float)
    V = np.zeros((N, dim))
    fit = np.array([jFitnessFunction(X, y, (P[i] > 0.5), opts) for i in range(N)])
    Pbest, fitP = P.copy(), fit.copy()
    g = np.argmin(fitP); Gbest, fitG = Pbest[g].copy(), float(fitP[g])
    curve = np.zeros(T+1); curve[0] = fitG
    for t in range(1, T+1):
        r1, r2 = np.random.rand(N, dim), np.random.rand(N, dim)
        V = w*V + c1*r1*(Pbest-P) + c2*r2*(Gbest-P)
        V = np.clip(V, -Vmax, Vmax)
        prob = 1.0/(1.0+np.exp(-V))
        P = (np.random.rand(N, dim) < prob).astype(float)
        for i in range(N):
            f = jFitnessFunction(X, y, (P[i] > 0.5), opts)
            if f < fitP[i]:
                Pbest[i] = P[i].copy(); fitP[i] = f
            if f < fitG:
                fitG = float(f); Gbest = P[i].copy()
        curve[t] = fitG
    mask = (Gbest > 0.5)
    return {"fitG": fitG, "nf": int(mask.sum()), "curve": curve, "nhd_curve": np.zeros(T+1)}

def run_SaWDE(X, y, opts):
    N = opts["N"]; T = opts["T"]; thres = opts["thres"]; dim = X.shape[1]
    P = np.random.rand(N, dim)
    fit = np.array([jFitnessFunction(X, y, (P[i] > thres), opts) for i in range(N)])
    Gbest = P[np.argmin(fit)].copy(); fitG = float(np.min(fit))
    w_strat = np.ones(3)/3.0; F_hist=[0.5]*3; CR_hist=[0.5]*3
    curve = np.zeros(T+1); curve[0] = fitG
    for t in range(1, T+1):
        w_norm = w_strat/(w_strat.sum()+1e-12)
        success = np.zeros(3); count = np.zeros(3)
        P_new = P.copy()
        for i in range(N):
            s = np.random.choice(3, p=w_norm)
            F  = np.clip(np.random.normal(F_hist[s], 0.1), 0.1, 1.0)
            CR = np.clip(np.random.normal(CR_hist[s],0.1), 0.0, 1.0)
            idx = list(range(N)); idx.remove(i)
            r1,r2,r3 = np.random.choice(idx,3,replace=False)
            if s==0: mut = P[r1] + F*(P[r2]-P[r3])
            elif s==1: mut = P[i] + F*(Gbest-P[i]) + F*(P[r1]-P[r2])
            else: mut = Gbest + F*(P[r1]-P[r2])
            mut = np.clip(mut,0,1)
            cross = (np.random.rand(dim) < CR)
            if not cross.any(): cross[np.random.randint(dim)] = True
            trial = np.where(cross, mut, P[i])
            f_trial = jFitnessFunction(X, y, (trial > thres), opts)
            if f_trial <= fit[i]:
                P_new[i] = trial; fit[i] = f_trial
                success[s] += 1
                F_hist[s]  = 0.9*F_hist[s]  + 0.1*F
                CR_hist[s] = 0.9*CR_hist[s] + 0.1*CR
                if f_trial < fitG:
                    fitG = float(f_trial); Gbest = trial.copy()
            count[s] += 1
        sr = np.where(count>0, success/count, 0.0)
        w_strat = 0.9*w_strat + 0.1*(sr + 0.01)
        w_strat = w_strat/(w_strat.sum()+1e-12)
        P = P_new
        curve[t] = fitG
    mask = (Gbest > thres)
    return {"fitG": fitG, "nf": int(mask.sum()), "curve": curve, "nhd_curve": np.zeros(T+1)}

def run_FWPSO(X, y, opts):
    N = opts["N"]; T = opts["T"]; thres = opts["thres"]; dim = X.shape[1]
    c1=c2=2.0; w=0.9; Vmax=0.5
    weight = np.zeros(dim)
    P = np.random.rand(N, dim); V = np.zeros((N, dim))
    fitP = np.array([jFitnessFunction(X, y, (P[i] > thres), opts) for i in range(N)])
    Pbest = P.copy()
    g = np.argmin(fitP); Gbest, fitG = Pbest[g].copy(), float(fitP[g])
    curve = np.zeros(T+1); curve[0]=fitG
    for t in range(1, T+1):
        for i in range(N):
            r1,r2 = np.random.rand(dim), np.random.rand(dim)
            V[i] = w*V[i] + c1*r1*(Pbest[i]-P[i]) + c2*r2*(Gbest-P[i])
            V[i] = np.clip(V[i], -Vmax, Vmax)
            vf = np.maximum(weight,0.0); sv=vf.sum()
            if sv>0 and np.random.rand()<0.3:
                prob=vf/sv; P[i]=(np.random.rand(dim)<prob).astype(float)
            else:
                P[i]=np.clip(P[i]+V[i],0,1)
            f = jFitnessFunction(X, y, (P[i] > thres), opts)
            pb=(Pbest[i]>thres); pn=(P[i]>thres)
            if f < fitP[i]:
                inc=fitP[i]-f
                change=np.logical_xor(pb,pn)
                weight[change & pn & (~pb)] += inc
                weight[change & pb & (~pn)] -= inc
                Pbest[i]=P[i].copy(); fitP[i]=f
            if f < fitG:
                fitG=float(f); Gbest=P[i].copy()
        curve[t]=fitG
    mask=(Gbest>thres)
    return {"fitG": fitG, "nf": int(mask.sum()), "curve": curve, "nhd_curve": np.zeros(T+1)}

def run_MEL(X, y, opts):
    lb, ub, thres = 0.0, 1.0, opts["thres"]
    c1=c2=c3=2.0; w=0.9; Vmax=0.5
    N=opts["N"]; T=opts["T"]; dim=X.shape[1]
    weight=np.zeros(dim)
    P=np.random.uniform(lb,ub,(N,dim)); V=np.zeros((N,dim))
    subSize=N//2
    fit=np.array([jFitnessFunction(X,y,(P[i]>thres),opts) for i in range(N)])
    fitP=fit.copy(); Pbest=P.copy()
    Gbest=P[np.argmin(fit)].copy(); fitG=float(np.min(fit))
    curve=np.zeros(T+1); curve[0]=fitG
    for t in range(1,T+1):
        P_new=P.copy()
        Xsub_best = Pbest[subSize + np.argmin(fitP[subSize:])].copy()
        for i in range(N):
            if i < subSize:
                r1,r2,r3=np.random.rand(dim),np.random.rand(dim),np.random.rand(dim)
                V[i]=np.clip(w*V[i]+c1*r1*(Pbest[i]-P[i])+c2*r2*(Gbest-P[i])+c3*r3*(Xsub_best-P[i]),-Vmax,Vmax)
                P_new[i]=np.clip(P[i]+V[i],lb,ub)
            else:
                vf=np.maximum(weight,0.0); sv=vf.sum()
                prob=vf/sv if sv>0 else np.full(dim,0.5)
                P_new[i]=(np.random.rand(dim)<prob).astype(float)
        pool=np.vstack([Pbest,P_new])
        pool_bin=(pool>thres).astype(bool)
        pool_fit=np.array([jFitnessFunction(X,y,pool_bin[i],opts) for i in range(2*N)])
        idx=np.argsort(pool_fit)[:N]
        P=pool[idx]; fit_sel=pool_fit[idx]; bin_sel=pool_bin[idx]
        for i in range(N):
            fv_n=bin_sel[i]; fv_o=(Pbest[i]>thres)
            if fit_sel[i] < fitP[i]:
                inc=fitP[i]-fit_sel[i]; change=np.logical_xor(fv_n,fv_o)
                weight[change & (fv_n>fv_o)] += inc
                weight[change & (fv_n<fv_o)] -= inc
        improved=fit_sel<fitP
        Pbest=np.where(improved[:,None],P,Pbest)
        fitP=np.minimum(fit_sel,fitP)
        bi=np.argmin(fitP)
        if fitP[bi] < fitG:
            fitG=float(fitP[bi]); Gbest=Pbest[bi].copy()
        curve[t]=fitG
    return {"fitG": fitG, "nf": int((Gbest>thres).sum()), "curve": curve, "nhd_curve": np.zeros(T+1)}

def run_MEL_NHD(X, y, opts):
    lb, ub, thres = 0.0, 1.0, opts["thres"]
    c1=c2=c3=2.0; w=0.9; Vmax=0.5
    N=opts["N"]; T=opts["T"]; dim=X.shape[1]
    weight=np.zeros(dim)
    P=np.random.uniform(lb,ub,(N,dim)); V=np.zeros((N,dim))
    subSize=N//2
    fit=np.array([jFitnessFunction(X,y,(P[i]>thres),opts) for i in range(N)])
    fitP=fit.copy(); Pbest=P.copy()
    Gbest=P[np.argmin(fit)].copy(); fitG=float(np.min(fit))
    curve=np.zeros(T+1); nhd_curve=np.zeros(T+1); curve[0]=fitG
    for t in range(1,T+1):
        alpha_cd=(t/T)**2
        P_new=P.copy()
        Xsub_best = Pbest[subSize + np.argmin(fitP[subSize:])].copy()
        for i in range(N):
            if i < subSize:
                r1,r2,r3=np.random.rand(dim),np.random.rand(dim),np.random.rand(dim)
                V[i]=np.clip(w*V[i]+c1*r1*(Pbest[i]-P[i])+c2*r2*(Gbest-P[i])+c3*r3*(Xsub_best-P[i]),-Vmax,Vmax)
                P_new[i]=np.clip(P[i]+V[i],lb,ub)
            else:
                vf=np.maximum(weight,0.0); sv=vf.sum()
                prob=vf/sv if sv>0 else np.full(dim,0.5)
                P_new[i]=(np.random.rand(dim)<prob).astype(float)
        pool=np.vstack([Pbest,P_new])
        pool_bin=(pool>thres).astype(int)
        pool_fit=np.array([jFitnessFunction(X,y,pool_bin[i].astype(bool),opts) for i in range(2*N)])
        nhd_mat=pairwise_nhd(pool_bin)
        sel=emdo_select(pool_fit,nhd_mat,N,alpha_cd)
        P=pool[sel]; fit_sel=pool_fit[sel]; bin_sel=pool_bin[sel].astype(bool)
        for i in range(N):
            fv_n=bin_sel[i]; fv_o=(Pbest[i]>thres)
            if fit_sel[i] < fitP[i]:
                inc=fitP[i]-fit_sel[i]; change=np.logical_xor(fv_n,fv_o)
                weight[change & (fv_n>fv_o)] += inc
                weight[change & (fv_n<fv_o)] -= inc
        improved=fit_sel<fitP
        Pbest=np.where(improved[:,None],P,Pbest)
        fitP=np.minimum(fit_sel,fitP)
        bi=np.argmin(fitP)
        if fitP[bi] < fitG:
            fitG=float(fitP[bi]); Gbest=Pbest[bi].copy()
        sb=(Pbest>thres).astype(int); nm=pairwise_nhd(sb)
        nhd_curve[t]=nm.sum()/(N*(N-1)) if N>1 else 0.0
        curve[t]=fitG
    return {"fitG": fitG, "nf": int((Gbest>thres).sum()), "curve": curve, "nhd_curve": nhd_curve}

def _kgef_elite_flip(weight, elite_bin, flip_count):
    mutant = elite_bin.copy()
    dim = len(mutant)
    if np.random.rand() < 0.10:
        fi = np.random.choice(dim, flip_count, replace=False)
        mutant[fi] = 1 - mutant[fi]
    else:
        scores = np.where(elite_bin == 0, weight, -weight)
        scores += np.random.normal(0, np.std(weight) + 1e-5, dim)
        fi = np.argsort(-scores)[:flip_count]
        mutant[fi] = 1 - mutant[fi]
    return mutant

def run_MEL_KGEF_noNHD(X, y, opts):
    lb, ub, thres = 0.0, 1.0, opts["thres"]
    c1=c2=c3=2.0; w=0.9; Vmax=0.5
    N=opts["N"]; T=opts["T"]; dim=X.shape[1]
    decay=opts["weight_decay"]
    weight=np.zeros(dim)
    P=np.random.uniform(lb,ub,(N,dim)); V=np.zeros((N,dim))
    subSize=N//2
    fit=np.array([jFitnessFunction(X,y,(P[i]>thres),opts) for i in range(N)])
    fitP=fit.copy(); Pbest=P.copy()
    Gbest=P[np.argmin(fit)].copy(); fitG=float(np.min(fit))
    curve=np.zeros(T+1); curve[0]=fitG
    for t in range(1,T+1):
        weight*=decay
        P_new=P.copy()
        Xsub_best = Pbest[subSize + np.argmin(fitP[subSize:])].copy()
        for i in range(N):
            if i < subSize:
                r1,r2,r3=np.random.rand(dim),np.random.rand(dim),np.random.rand(dim)
                V[i]=np.clip(w*V[i]+c1*r1*(Pbest[i]-P[i])+c2*r2*(Gbest-P[i])+c3*r3*(Xsub_best-P[i]),-Vmax,Vmax)
                P_new[i]=np.clip(P[i]+V[i],lb,ub)
            else:
                vf=np.maximum(weight,0.0); sv=vf.sum()
                prob=vf/sv if sv>0 else np.full(dim,0.5)
                P_new[i]=(np.random.rand(dim)<prob).astype(float)
        pool=np.vstack([Pbest,P_new])
        pool_bin=(pool>thres).astype(bool)
        pool_fit=np.array([jFitnessFunction(X,y,pool_bin[i],opts) for i in range(2*N)])
        idx=np.argsort(pool_fit)[:N]
        P=pool[idx]; fit_sel=pool_fit[idx]; bin_sel=pool_bin[idx]
        improved=fit_sel<fitP
        Pbest=np.where(improved[:,None],P,Pbest)
        fitP=np.minimum(fit_sel,fitP)
        flip_count=max(1,int(0.01*dim))
        elites=np.argsort(fitP)[:3]
        for e in elites:
            elite_bin=(Pbest[e]>thres).astype(int)
            mutant=_kgef_elite_flip(weight, elite_bin, flip_count)
            mfit=jFitnessFunction(X,y,mutant.astype(bool),opts)
            if mfit < fitP[e]:
                Pbest[e]=mutant; fitP[e]=mfit
        bi=np.argmin(fitP)
        if fitP[bi] < fitG:
            fitG=float(fitP[bi]); Gbest=Pbest[bi].copy()
        curve[t]=fitG
    return {"fitG": fitG, "nf": int((Gbest>thres).sum()), "curve": curve, "nhd_curve": np.zeros(T+1)}

def run_MEL_KGEF(X, y, opts):
    lb, ub, thres = 0.0, 1.0, opts["thres"]
    c1=c2=c3=2.0; w=0.9; Vmax=0.5
    N=opts["N"]; T=opts["T"]; dim=X.shape[1]
    decay=opts["weight_decay"]
    weight=np.zeros(dim)
    P=np.random.uniform(lb,ub,(N,dim)); V=np.zeros((N,dim))
    subSize=N//2
    fit=np.array([jFitnessFunction(X,y,(P[i]>thres),opts) for i in range(N)])
    fitP=fit.copy(); Pbest=P.copy()
    Gbest=P[np.argmin(fit)].copy(); fitG=float(np.min(fit))
    curve=np.zeros(T+1); nhd_curve=np.zeros(T+1); curve[0]=fitG
    for t in range(1,T+1):
        weight*=decay
        alpha_cd=(t/T)**2
        P_new=P.copy()
        Xsub_best = Pbest[subSize + np.argmin(fitP[subSize:])].copy()
        for i in range(N):
            if i < subSize:
                r1,r2,r3=np.random.rand(dim),np.random.rand(dim),np.random.rand(dim)
                V[i]=np.clip(w*V[i]+c1*r1*(Pbest[i]-P[i])+c2*r2*(Gbest-P[i])+c3*r3*(Xsub_best-P[i]),-Vmax,Vmax)
                P_new[i]=np.clip(P[i]+V[i],lb,ub)
            else:
                vf=np.maximum(weight,0.0); sv=vf.sum()
                prob=vf/sv if sv>0 else np.full(dim,0.5)
                P_new[i]=(np.random.rand(dim)<prob).astype(float)
        pool=np.vstack([Pbest,P_new])
        pool_bin=(pool>thres).astype(int)
        pool_fit=np.array([jFitnessFunction(X,y,pool_bin[i].astype(bool),opts) for i in range(2*N)])
        nhd_mat=pairwise_nhd(pool_bin)
        sel=emdo_select(pool_fit,nhd_mat,N,alpha_cd)
        P=pool[sel]; fit_sel=pool_fit[sel]
        improved=fit_sel<fitP
        Pbest=np.where(improved[:,None],P,Pbest)
        fitP=np.minimum(fit_sel,fitP)
        flip_count=max(1,int(0.01*dim))
        elites=np.argsort(fitP)[:3]
        for e in elites:
            elite_bin=(Pbest[e]>thres).astype(int)
            mutant=_kgef_elite_flip(weight, elite_bin, flip_count)
            mfit=jFitnessFunction(X,y,mutant.astype(bool),opts)
            if mfit < fitP[e]:
                Pbest[e]=mutant; fitP[e]=mfit
        bi=np.argmin(fitP)
        if fitP[bi] < fitG:
            fitG=float(fitP[bi]); Gbest=Pbest[bi].copy()
        sb=(Pbest>thres).astype(int); nm=pairwise_nhd(sb)
        nhd_curve[t]=nm.sum()/(N*(N-1)) if N>1 else 0.0
        curve[t]=fitG
    return {"fitG": fitG, "nf": int((Gbest>thres).sum()), "curve": curve, "nhd_curve": nhd_curve}

RUNNERS = {
    "BPSO": run_BPSO,
    "SaWDE": run_SaWDE,
    "FWPSO": run_FWPSO,
    "MEL": run_MEL,
    "MEL_NHD": run_MEL_NHD,
    "MEL_KGEF_noNHD": run_MEL_KGEF_noNHD,
    "MEL_KGEF": run_MEL_KGEF,
}

# ── Resume helpers ──────────────────────────────────────────────────────────
def ensure_csv_header():
    if not os.path.exists(CSV_PATH):
        with open(CSV_PATH, "w", newline="") as f:
            csv.DictWriter(f, fieldnames=CSV_FIELDS).writeheader()

def load_completed():
    done=set()
    if not os.path.exists(CSV_PATH):
        return done
    with open(CSV_PATH, "r", newline="") as f:
        for r in csv.DictReader(f):
            try:
                done.add((r["Version"], r["Dataset"], int(r["Run"])))
            except Exception:
                pass
    return done

def append_row(row):
    with open(CSV_PATH, "a", newline="") as f:
        csv.DictWriter(f, fieldnames=CSV_FIELDS).writerow(row)

# ── Run ─────────────────────────────────────────────────────────────────────
ensure_csv_header()
done = load_completed()
print("Already finished tasks:", len(done))
print("Example finished keys:", list(done)[:5])
print("CSV:", CSV_PATH)
print("Curves:", CURVES_DIR)

tasks_done_this_run = 0
scope_tasks = len(ONLY_DATASETS) * len(RUNNERS) * NUM_RUNS
print(f"\nScope tasks: {scope_tasks} | MAX_TASKS this cell: {MAX_TASKS}\n")

for ds in ONLY_DATASETS:
    X, y = load_dataset(ds)
    print(f"\n{'='*70}\nDataset: {ds} | X={X.shape} | class_counts={np.bincount(y)}\n{'='*70}")
    for ver, fn in RUNNERS.items():
        for run in range(NUM_RUNS):
            if (ver, ds, run) in done:
                continue
            if MAX_TASKS is not None and tasks_done_this_run >= MAX_TASKS:
                print(f"\nReached MAX_TASKS={MAX_TASKS}. Exiting. Re-run this cell to continue.")
                raise SystemExit(0)

            np.random.seed(SEED_BASE + run*37)
            t0=time()
            res=fn(X, y, OPTS)
            elapsed=time()-t0

            acc = 1.0 - float(res["fitG"])
            nf  = int(res["nf"])
            nhd_curve = res.get("nhd_curve", np.zeros(OPTS["T"]+1))
            avg_nhd = float(np.mean(nhd_curve[1:])) if np.any(nhd_curve[1:]) else 0.0

            append_row({
                "Version": ver, "Dataset": ds, "Run": run,
                "Accuracy": f"{acc:.6f}",
                "Num_Features": nf,
                "Avg_NHD": f"{avg_nhd:.6f}",
                "Time_sec": f"{elapsed:.2f}",
            })
            np.save(os.path.join(CURVES_DIR, f"curve_{ver}_{ds}_run{run}.npy"), res["curve"])
            np.save(os.path.join(CURVES_DIR, f"nhd_{ver}_{ds}_run{run}.npy"), nhd_curve)

            tasks_done_this_run += 1
            print(f"  ✓ {ver:14s} | run {run:2d} | Acc={acc:.4f} | Feat={nf:6d} | t={elapsed:7.1f}s")

print("\n✅ Cell 1 finished (scope or MAX_TASKS reached).")