# =============================================================================
#  统一实验 Cell — 全部方法 × 13 数据集
#  数据集：8个原有(去ALL3) + SRBCT + Gastric + Leukaemia + Prostate + BASEHOCK
#
#  修改 VERSION 和 ONLY_DATASETS 来控制跑哪个方法、哪些数据集
#  npy 输出：每个run固定两个文件
#    curve_{VERSION}_{DATASET}_run{N}.npy   fitness曲线
#    nhd_{VERSION}_{DATASET}_run{N}.npy     NHD曲线 (非MEL方法全为0)
# =============================================================================

VERSION        = "MEL_KGEF"    # 修改此处切换方法
MAX_TASKS      = 200           # 每次执行最多跑几个任务（断点续跑）

ONLY_DATASETS  = [
    # ── 原有8个（去ALL3）──────────────────────────────────────────────
    "Adenoma",
    "ALL_AML",
    "ALL4",
    "CNS",
    "Colon",
    "DLBCL",
    "Lymphoma",
    "Stroke",
    # ── 新增5个 ───────────────────────────────────────────────────────
    "SRBCT",       # 83×2308,  4类(BL/EWS/NB/RMS), 经典多分类
    "Gastric",     # 65×22645, 2类, 超高维
    "Leukaemia",   # 72×7129,  2类, 白血病
    "Prostate",    # 102×12625,2类, 前列腺癌
    "BASEHOCK",    # 1993×4862,2类, 文本分类（.mat格式）
]

# =============================================================================

import os, re, csv, warnings
import numpy as np
from time import time
from sklearn.neighbors import KNeighborsClassifier
from sklearn.model_selection import StratifiedKFold
from sklearn.preprocessing import LabelEncoder
from scipy.io import loadmat

warnings.filterwarnings("ignore")
np.seterr(all="ignore")

DATA_DIR_TXT = "/kaggle/input/datasets/eminz132/dataset/Datasets_part1"
DATA_DIR_MAT = "/kaggle/input/datasets/eminz132/dataset/Datasets_part2"
OUT_DIR      = "/kaggle/working"
CURVES_DIR   = os.path.join(OUT_DIR, "curves_all_rerun_stratified")
CSV_PATH     = os.path.join(OUT_DIR, f"results_{VERSION}.csv")
os.makedirs(CURVES_DIR, exist_ok=True)

NUM_RUNS  = 10
SEED_BASE = 42

OPTS = {
    "k": 3, "N": 20, "T": 100, "thres": 0.6,
    "ws": [0.9, 0.1],
    "cv_splits": 5, "cv_shuffle": True, "cv_random_state": 42,
    "weight_decay": 0.99, "flip_frac": 0.01,
    "elite_k": 3, "rand_flip_p": 0.10,
}

CSV_FIELDS = ["Version","Dataset","Run","Accuracy","Num_Features","Avg_NHD","Time_sec"]

# ── Dataset profiles ──────────────────────────────────────────────────
# CNS / MLL 的标签列和数据列从第3列起
SPECIAL_COL = {"CNS": 3, "MLL": 3}

# SRBCT 标准4类；列名含其他前缀的样本视为外部样本，加载时过滤
SRBCT_KEEP  = {"BL", "EWS", "NB", "RMS"}

# ── SRBCT 列名 → 类别前缀 ─────────────────────────────────────────────
def _srbct_prefix(col):
    """
    'BL'           → 'BL'
    'BL-C1'        → 'BL'    连字符前取前缀
    'BL.1'         → 'BL'    先剥离末尾 .数字，再取连字符前缀
    'EWS-T11'      → 'EWS'
    'RMS.4'        → 'RMS'
    'Osteosarcoma' → 'Osteosarcoma'  （不在KEEP集合，后续过滤）
    'Sk._Muscle.1' → 'Sk._Muscle'
    """
    s = re.sub(r'\.\d+$', '', col.strip())   # 剥离末尾 .数字
    return s.split('-')[0]                    # 取连字符前缀

# ── Loaders ───────────────────────────────────────────────────────────

def load_txt(name):
    """
    加载 .txt 格式基因表达数据集。
    格式：行=基因，列=样本
      第0行：[空/gene_col] \t sample1 \t sample2 \t ...
      第1行起：gene_name \t val1 \t val2 \t ...
    特殊处理：
      SRBCT  — 列名为 CLASS-SampleID 格式，需提取前缀并过滤外部样本
      CNS/MLL— 标签/数据从第3列起
    """
    fp = os.path.join(DATA_DIR_TXT, f"{name}.txt")
    if not os.path.exists(fp):
        raise FileNotFoundError(f"Not found: {fp}")

    ls = ds = SPECIAL_COL.get(name, 1)

    lines = open(fp, encoding="utf-8", errors="replace").read().splitlines()
    header       = lines[0].strip().split("\t")
    sample_names = [h for h in header[ls:] if h.strip()]

    if name == "SRBCT":
        # 提取类别前缀，过滤非4类外部样本
        raw_labels = [_srbct_prefix(h) for h in sample_names]
        keep_mask  = [lb in SRBCT_KEEP for lb in raw_labels]
        labels_raw = [lb for lb, k in zip(raw_labels, keep_mask) if k]
    else:
        keep_mask  = [True] * len(sample_names)
        labels_raw = sample_names

    classes = sorted(set(labels_raw))
    cmap    = {c: i for i, c in enumerate(classes)}
    y       = np.array([cmap[s] for s in labels_raw], dtype=int)
    n       = len(y)
    keep_cols = [i for i, k in enumerate(keep_mask) if k]   # 保留的列索引

    rows = []
    for line in lines[1:]:
        parts = line.rstrip("\n").split("\t")
        vals  = [p for p in parts[ds:] if p.strip()]
        if len(vals) != len(sample_names):
            continue
        try:
            rows.append([float(vals[i]) for i in keep_cols])
        except ValueError:
            continue

    X = np.array(rows, dtype=float).T
    assert X.shape[0] == n, f"{name}: X.shape={X.shape} but n={n}"
    return X, y


def load_mat(name):
    """
    加载 .mat 格式数据集（ASU 标准格式）。
    X 键名候选：X / data / fea / features
    Y 键名候选：Y / label / gnd / labels / targets
    """
    for folder in [DATA_DIR_MAT, DATA_DIR_TXT]:
        fp = os.path.join(folder, f"{name}.mat")
        if os.path.exists(fp):
            break
    else:
        raise FileNotFoundError(f"Not found: {name}.mat")

    data = loadmat(fp)

    X = next((data[k].astype(float)
               for k in ["X","data","fea","features"]
               if k in data and isinstance(data[k], np.ndarray)), None)
    Y = next((data[k].ravel().astype(int)
               for k in ["Y","label","gnd","labels","targets"]
               if k in data and isinstance(data[k], np.ndarray)), None)

    if X is None or Y is None:
        raise ValueError(f"{name}.mat: cannot find X/Y. Keys={list(data.keys())}")

    try:
        from scipy.sparse import issparse
        if issparse(X): X = X.toarray()
    except Exception:
        pass

    return X, Y - Y.min()


def load_dataset(name):
    """
    统一入口：自动判断 txt / mat，并做以下后处理：
      1. LabelEncoder — 保证标签为 0,1,2,... 的连续整数
      2. 健康检查    — n_classes == n_samples 时报警
    """
    MAT_DATASETS = {"BASEHOCK","COIL20","PCMAC","RELATHE","ISOLET",
                    "USPS","Pancancer","MultipleFeaturesDigit","madelon"}

    if name in MAT_DATASETS:
        X, y = load_mat(name)
    else:
        txt_fp  = os.path.join(DATA_DIR_TXT, f"{name}.txt")
        mat_fp1 = os.path.join(DATA_DIR_TXT, f"{name}.mat")
        mat_fp2 = os.path.join(DATA_DIR_MAT, f"{name}.mat")
        if os.path.exists(txt_fp):
            X, y = load_txt(name)
        elif os.path.exists(mat_fp1) or os.path.exists(mat_fp2):
            X, y = load_mat(name)
        else:
            raise FileNotFoundError(f"Cannot find {name}.txt or {name}.mat")

    # 统一重编码：任意原始标签 → 0,1,2,...
    y = LabelEncoder().fit_transform(y)

    # 健康检查
    n_classes = len(np.unique(y))
    if n_classes == len(y):
        raise ValueError(
            f"{name}: n_classes({n_classes}) == n_samples — 标签未正确解析，请检查文件格式！")
    if n_classes < 2:
        raise ValueError(f"{name}: 只有 {n_classes} 个类，无法分类")

    return X, y


# ── KNN fitness ──────────────────────────────────────────────────────

def jwrapper(X_sub, y, opts):
    """
    StratifiedKFold KNN 误差。
    n_splits 动态取 min(cv_splits, 最小类样本数)，避免类样本不足时崩溃。
    """
    min_class = int(np.min(np.bincount(y)))
    n_splits  = min(opts["cv_splits"], min_class)
    if n_splits < 2:
        return 1.0      # 无法CV，返回最差fitness

    skf = StratifiedKFold(
        n_splits=n_splits,
        shuffle=opts["cv_shuffle"],
        random_state=opts["cv_random_state"])
    acc = []
    for tr, te in skf.split(X_sub, y):
        clf = KNeighborsClassifier(n_neighbors=opts["k"])
        clf.fit(X_sub[tr], y[tr])
        acc.append((clf.predict(X_sub[te]) == y[te]).mean())
    return 1.0 - float(np.mean(acc))


def jFitness(X, y, mask, opts):
    nf = int(mask.sum())
    if nf < 3:
        return 1.0 + (3 - nf) * 0.1
    return opts["ws"][0] * jwrapper(X[:, mask], y, opts) + \
           opts["ws"][1] * (nf / X.shape[1])


# ── NHD ──────────────────────────────────────────────────────────────

def pairwise_nhd(X_bin):
    X_bin = X_bin.astype(np.float32)
    inter = X_bin @ X_bin.T
    sums  = X_bin.sum(axis=1)
    union = sums[:, None] + sums[None, :] - inter
    ahd   = sums[:, None] + sums[None, :] - 2.0 * inter
    return ahd / np.maximum(union, 1.0)


# ── EMDO (DRS) ───────────────────────────────────────────────────────

def fast_nds(obj):
    N  = obj.shape[0]
    dc = np.zeros(N, dtype=int)
    ds = [[] for _ in range(N)]
    fronts = [[]]
    for i in range(N):
        for j in range(N):
            if i == j: continue
            if np.all(obj[i]<=obj[j]) and np.any(obj[i]<obj[j]): ds[i].append(j)
            elif np.all(obj[j]<=obj[i]) and np.any(obj[j]<obj[i]): dc[i]+=1
        if dc[i]==0: fronts[0].append(i)
    cf=0
    while fronts[cf]:
        nxt=[]
        for i in fronts[cf]:
            for j in ds[i]:
                dc[j]-=1
                if dc[j]==0: nxt.append(j)
        cf+=1; fronts.append(nxt)
    if not fronts[-1]: fronts.pop()
    return fronts


def crowding_dist(obj, front):
    cd={i:0.0 for i in front}
    for m in range(obj.shape[1]):
        sf=sorted(front, key=lambda i:obj[i,m]); cd[sf[0]]=cd[sf[-1]]=np.inf
        span=obj[sf[-1],m]-obj[sf[0],m]
        if span==0: continue
        for k in range(1,len(front)-1):
            cd[sf[k]]+=(obj[sf[k+1],m]-obj[sf[k-1],m])/span
    return cd


def emdo_select(pool_fit, nhd_mat, N, alpha_cd):
    pool_nhd=nhd_mat.mean(axis=1)
    obj=np.column_stack([pool_fit,-pool_nhd])
    fronts=fast_nds(obj); selected=[]
    for front in fronts:
        if len(selected)+len(front)<=N: selected.extend(front)
        else:
            needed=N-len(selected); cd=crowding_dist(obj,front)
            cd_v=np.array([cd[i] for i in front])
            fin=cd_v[np.isfinite(cd_v)]; mc=np.max(fin) if len(fin)>0 else 0.0
            cd_n=np.where(np.isfinite(cd_v),(cd_v/mc if mc>0 else 0.0),1.0)
            hd_v=np.array([pool_nhd[i] for i in front]); mh=np.max(hd_v)
            hd_n=hd_v/mh if mh>0 else np.zeros(len(front))
            score=alpha_cd*cd_n+(1.0-alpha_cd)*hd_n; order=np.argsort(-score)
            selected.extend([front[order[k]] for k in range(needed)]); break
    return np.array(selected)


# ── KER ──────────────────────────────────────────────────────────────

def kgef_flip(weight, elite_bin, flip_count, rand_p):
    mutant=elite_bin.copy(); dim=len(mutant)
    if np.random.rand()<rand_p:
        fi=np.random.choice(dim, flip_count, replace=False)
    else:
        sc=np.where(elite_bin==0,weight,-weight)
        sc+=np.random.normal(0.0, np.std(weight)+1e-5, dim)
        fi=np.argsort(-sc)[:flip_count]
    mutant[fi]=1-mutant[fi]; return mutant


# ══════════════════════════════════════════════════════════════════════
# 各方法主循环
# ══════════════════════════════════════════════════════════════════════

def run_BPSO(X, y, opts):
    lb,ub,thres=0.,1.,opts["thres"]
    c1=c2=2.; wi=0.9; Vmax=0.6
    N,T,dim=opts["N"],opts["T"],X.shape[1]
    P=np.random.uniform(lb,ub,(N,dim)); V=np.zeros((N,dim))
    fit=np.array([jFitness(X,y,P[i]>thres,opts) for i in range(N)])
    fitP=fit.copy(); Pbest=P.copy(); Gbest=P[np.argmin(fit)].copy(); fitG=float(np.min(fit))
    curve=np.zeros(T+1); curve[0]=fitG
    for t in range(1,T+1):
        for i in range(N):
            r1,r2=np.random.rand(dim),np.random.rand(dim)
            V[i]=np.clip(wi*V[i]+c1*r1*(Pbest[i]-P[i])+c2*r2*(Gbest-P[i]),-Vmax,Vmax)
            P[i]=np.clip(P[i]+V[i],lb,ub)
            f=jFitness(X,y,P[i]>thres,opts)
            if f<fitP[i]: fitP[i]=f; Pbest[i]=P[i].copy()
        bi=np.argmin(fitP)
        if fitP[bi]<fitG: fitG=float(fitP[bi]); Gbest=Pbest[bi].copy()
        curve[t]=fitG
    nhd=np.zeros(T+1)
    return fitG,int((Gbest>thres).sum()),curve,nhd,0.0


def run_SaWDE(X, y, opts):
    N,T,dim=opts["N"],opts["T"],X.shape[1]
    thres=opts["thres"]
    pop=np.random.randint(0,2,(N,dim)).astype(float)
    fit=np.array([jFitness(X,y,pop[i].astype(bool),opts) for i in range(N)])
    best_idx=np.argmin(fit); Gbest=pop[best_idx].copy(); fitG=float(fit[best_idx])
    F_vals=np.random.uniform(0.4,0.9,N); CR_vals=np.random.uniform(0.1,0.9,N)
    curve=np.zeros(T+1); curve[0]=fitG
    for t in range(1,T+1):
        for i in range(N):
            idxs=[j for j in range(N) if j!=i]; a,b,c=np.random.choice(idxs,3,replace=False)
            F=F_vals[i]; CR=CR_vals[i]
            mut=(pop[a]+F*(pop[b]-pop[c]))
            mask=np.random.rand(dim)<CR
            trial=np.where(mask,mut,pop[i])
            bin_trial=(1.0/(1+np.exp(-trial))>np.random.rand(dim)).astype(float)
            f=jFitness(X,y,bin_trial.astype(bool),opts)
            if f<fit[i]:
                pop[i]=bin_trial; fit[i]=f
                if f<fitG: fitG=f; Gbest=bin_trial.copy()
                F_vals[i]=np.clip(F_vals[i]+np.random.randn()*0.1,0.1,1.0)
                CR_vals[i]=np.clip(CR_vals[i]+np.random.randn()*0.1,0.0,1.0)
        curve[t]=fitG
    nhd=np.zeros(T+1)
    return fitG,int(Gbest.astype(bool).sum()),curve,nhd,0.0


def run_FWPSO(X, y, opts):
    lb,ub,thres=0.,1.,opts["thres"]
    c1=c2=2.; wi=0.9; Vmax=0.6
    N,T,dim=opts["N"],opts["T"],X.shape[1]
    weight=np.random.dirichlet(np.ones(dim))
    P=(np.random.rand(N,dim)<weight).astype(float)
    V=np.zeros((N,dim))
    fit=np.array([jFitness(X,y,P[i].astype(bool),opts) for i in range(N)])
    fitP=fit.copy(); Pbest=P.copy(); Gbest=P[np.argmin(fit)].copy(); fitG=float(np.min(fit))
    curve=np.zeros(T+1); curve[0]=fitG
    for t in range(1,T+1):
        for i in range(N):
            r1,r2=np.random.rand(dim),np.random.rand(dim)
            V[i]=np.clip(wi*V[i]+c1*r1*(Pbest[i]-P[i])+c2*r2*(Gbest-P[i]),-Vmax,Vmax)
            sig=1.0/(1+np.exp(-V[i]))
            P[i]=(np.random.rand(dim)<sig).astype(float)
            f=jFitness(X,y,P[i].astype(bool),opts)
            if f<fitP[i]:
                fitP[i]=f; Pbest[i]=P[i].copy()
                delta=Pbest[i]-Gbest; change=np.abs(delta)>0.5
                weight[change & (delta>0)]+=0.01
                weight[change & (delta<0)]-=0.01
                weight=np.clip(weight,0,None); s=weight.sum()
                if s>0: weight/=s
        bi=np.argmin(fitP)
        if fitP[bi]<fitG: fitG=float(fitP[bi]); Gbest=Pbest[bi].copy()
        curve[t]=fitG
    nhd=np.zeros(T+1)
    return fitG,int(Gbest.astype(bool).sum()),curve,nhd,0.0


def run_MEL(X, y, opts):
    lb,ub,thres=0.,1.,opts["thres"]
    c1=c2=c3=2.; wi=0.9; Vmax=0.5
    N,T,dim=opts["N"],opts["T"],X.shape[1]
    subSize=N//2
    P=np.random.uniform(lb,ub,(N,dim)); V=np.zeros((N,dim))
    fit=np.array([jFitness(X,y,P[i]>thres,opts) for i in range(N)])
    fitP=fit.copy(); Pbest=P.copy(); Gbest=P[np.argmin(fit)].copy(); fitG=float(np.min(fit))
    curve=np.zeros(T+1); curve[0]=fitG; nhd_curve=np.zeros(T+1)
    for t in range(1,T+1):
        P_new=P.copy(); Xs=Pbest[subSize+np.argmin(fitP[subSize:])].copy()
        for i in range(N):
            if i<subSize:
                r1,r2,r3=np.random.rand(dim),np.random.rand(dim),np.random.rand(dim)
                V[i]=np.clip(wi*V[i]+c1*r1*(Pbest[i]-P[i])+c2*r2*(Gbest-P[i])+c3*r3*(Xs-P[i]),-Vmax,Vmax)
                P_new[i]=np.clip(P[i]+V[i],lb,ub)
            else:
                P_new[i]=(np.random.rand(dim)<0.5).astype(float)
        pool=np.vstack([Pbest,P_new]); pb=(pool>thres).astype(int)
        pf=np.array([jFitness(X,y,pb[i].astype(bool),opts) for i in range(2*N)])
        sel=np.argsort(pf)[:N]
        P=pool[sel]; fs=pf[sel]; imp=fs<fitP
        Pbest=np.where(imp[:,None],P,Pbest); fitP=np.minimum(fs,fitP)
        bi=np.argmin(fitP)
        if fitP[bi]<fitG: fitG=float(fitP[bi]); Gbest=Pbest[bi].copy()
        sb=(Pbest>thres).astype(int); nm=pairwise_nhd(sb)
        nhd_curve[t]=nm.sum()/(N*(N-1)) if N>1 else 0.
        curve[t]=fitG
    return fitG,int((Gbest>thres).sum()),curve,nhd_curve,nhd_curve[1:].mean()


def run_MEL_NHD(X, y, opts):
    lb,ub,thres=0.,1.,opts["thres"]
    c1=c2=c3=2.; wi=0.9; Vmax=0.5
    N,T,dim=opts["N"],opts["T"],X.shape[1]
    subSize=N//2
    P=np.random.uniform(lb,ub,(N,dim)); V=np.zeros((N,dim))
    fit=np.array([jFitness(X,y,P[i]>thres,opts) for i in range(N)])
    fitP=fit.copy(); Pbest=P.copy(); Gbest=P[np.argmin(fit)].copy(); fitG=float(np.min(fit))
    curve=np.zeros(T+1); curve[0]=fitG; nhd_curve=np.zeros(T+1)
    for t in range(1,T+1):
        P_new=P.copy(); Xs=Pbest[subSize+np.argmin(fitP[subSize:])].copy()
        for i in range(N):
            if i<subSize:
                r1,r2,r3=np.random.rand(dim),np.random.rand(dim),np.random.rand(dim)
                V[i]=np.clip(wi*V[i]+c1*r1*(Pbest[i]-P[i])+c2*r2*(Gbest-P[i])+c3*r3*(Xs-P[i]),-Vmax,Vmax)
                P_new[i]=np.clip(P[i]+V[i],lb,ub)
            else:
                P_new[i]=(np.random.rand(dim)<0.5).astype(float)
        pool=np.vstack([Pbest,P_new]); pb=(pool>thres).astype(int)
        pf=np.array([jFitness(X,y,pb[i].astype(bool),opts) for i in range(2*N)])
        nhd_mat=pairwise_nhd(pb)
        sel=emdo_select(pf,nhd_mat,N,(t/T)**2)
        P=pool[sel]; fs=pf[sel]; imp=fs<fitP
        Pbest=np.where(imp[:,None],P,Pbest); fitP=np.minimum(fs,fitP)
        bi=np.argmin(fitP)
        if fitP[bi]<fitG: fitG=float(fitP[bi]); Gbest=Pbest[bi].copy()
        sb=(Pbest>thres).astype(int); nm=pairwise_nhd(sb)
        nhd_curve[t]=nm.sum()/(N*(N-1)) if N>1 else 0.
        curve[t]=fitG
    return fitG,int((Gbest>thres).sum()),curve,nhd_curve,nhd_curve[1:].mean()


def run_MEL_KGEF_noNHD(X, y, opts):
    lb,ub,thres=0.,1.,opts["thres"]
    c1=c2=c3=2.; wi=0.9; Vmax=0.5
    N,T,dim=opts["N"],opts["T"],X.shape[1]
    subSize=N//2; decay=opts["weight_decay"]
    flip_count=max(1,int(opts["flip_frac"]*dim)); rand_p=opts["rand_flip_p"]; ek=opts["elite_k"]
    weight=np.zeros(dim)
    P=np.random.uniform(lb,ub,(N,dim)); V=np.zeros((N,dim))
    fit=np.array([jFitness(X,y,P[i]>thres,opts) for i in range(N)])
    fitP=fit.copy(); Pbest=P.copy(); Gbest=P[np.argmin(fit)].copy(); fitG=float(np.min(fit))
    curve=np.zeros(T+1); curve[0]=fitG; nhd_curve=np.zeros(T+1)
    for t in range(1,T+1):
        weight*=decay
        P_new=P.copy(); Xs=Pbest[subSize+np.argmin(fitP[subSize:])].copy()
        for i in range(N):
            if i<subSize:
                r1,r2,r3=np.random.rand(dim),np.random.rand(dim),np.random.rand(dim)
                V[i]=np.clip(wi*V[i]+c1*r1*(Pbest[i]-P[i])+c2*r2*(Gbest-P[i])+c3*r3*(Xs-P[i]),-Vmax,Vmax)
                P_new[i]=np.clip(P[i]+V[i],lb,ub)
            else:
                vf=np.maximum(weight,0.); sv=vf.sum()
                prob=vf/sv if sv>0 else np.full(dim,0.5)
                P_new[i]=(np.random.rand(dim)<prob).astype(float)
        pool=np.vstack([Pbest,P_new]); pb=(pool>thres).astype(int)
        pf=np.array([jFitness(X,y,pb[i].astype(bool),opts) for i in range(2*N)])
        sel=np.argsort(pf)[:N]
        P=pool[sel]; fs=pf[sel]; bs=pb[sel].astype(bool); imp=fs<fitP
        for i in range(N):
            if imp[i]:
                d=fitP[i]-fs[i]; fn=bs[i]; fo=(Pbest[i]>thres); ch=np.logical_xor(fn,fo)
                weight[ch&(fn>fo)]+=d; weight[ch&(fn<fo)]-=d
        Pbest=np.where(imp[:,None],P,Pbest); fitP=np.minimum(fs,fitP)
        for e in np.argsort(fitP)[:ek]:
            eb=(Pbest[e]>thres).astype(int); mu=kgef_flip(weight,eb,flip_count,rand_p)
            mf=jFitness(X,y,mu.astype(bool),opts)
            if mf<fitP[e]: Pbest[e]=mu; fitP[e]=mf
        bi=np.argmin(fitP)
        if fitP[bi]<fitG: fitG=float(fitP[bi]); Gbest=Pbest[bi].copy()
        sb=(Pbest>thres).astype(int); nm=pairwise_nhd(sb)
        nhd_curve[t]=nm.sum()/(N*(N-1)) if N>1 else 0.
        curve[t]=fitG
    return fitG,int((Gbest>thres).sum()),curve,nhd_curve,nhd_curve[1:].mean()


def run_MEL_KGEF(X, y, opts):
    """KDS-EL (Proposed): DRS + KER"""
    lb,ub,thres=0.,1.,opts["thres"]
    c1=c2=c3=2.; wi=0.9; Vmax=0.5
    N,T,dim=opts["N"],opts["T"],X.shape[1]
    subSize=N//2; decay=opts["weight_decay"]
    flip_count=max(1,int(opts["flip_frac"]*dim)); rand_p=opts["rand_flip_p"]; ek=opts["elite_k"]
    weight=np.zeros(dim)
    P=np.random.uniform(lb,ub,(N,dim)); V=np.zeros((N,dim))
    fit=np.array([jFitness(X,y,P[i]>thres,opts) for i in range(N)])
    fitP=fit.copy(); Pbest=P.copy(); Gbest=P[np.argmin(fit)].copy(); fitG=float(np.min(fit))
    curve=np.zeros(T+1); curve[0]=fitG; nhd_curve=np.zeros(T+1)
    for t in range(1,T+1):
        weight*=decay
        P_new=P.copy(); Xs=Pbest[subSize+np.argmin(fitP[subSize:])].copy()
        for i in range(N):
            if i<subSize:
                r1,r2,r3=np.random.rand(dim),np.random.rand(dim),np.random.rand(dim)
                V[i]=np.clip(wi*V[i]+c1*r1*(Pbest[i]-P[i])+c2*r2*(Gbest-P[i])+c3*r3*(Xs-P[i]),-Vmax,Vmax)
                P_new[i]=np.clip(P[i]+V[i],lb,ub)
            else:
                vf=np.maximum(weight,0.); sv=vf.sum()
                prob=vf/sv if sv>0 else np.full(dim,0.5)
                P_new[i]=(np.random.rand(dim)<prob).astype(float)
        pool=np.vstack([Pbest,P_new]); pb=(pool>thres).astype(int)
        pf=np.array([jFitness(X,y,pb[i].astype(bool),opts) for i in range(2*N)])
        nhd_mat=pairwise_nhd(pb)
        sel=emdo_select(pf,nhd_mat,N,(t/T)**2)
        P=pool[sel]; fs=pf[sel]; bs=pb[sel].astype(bool); imp=fs<fitP
        for i in range(N):
            if imp[i]:
                d=fitP[i]-fs[i]; fn=bs[i]; fo=(Pbest[i]>thres); ch=np.logical_xor(fn,fo)
                weight[ch&(fn>fo)]+=d; weight[ch&(fn<fo)]-=d
        Pbest=np.where(imp[:,None],P,Pbest); fitP=np.minimum(fs,fitP)
        for e in np.argsort(fitP)[:ek]:
            eb=(Pbest[e]>thres).astype(int); mu=kgef_flip(weight,eb,flip_count,rand_p)
            mf=jFitness(X,y,mu.astype(bool),opts)
            if mf<fitP[e]: Pbest[e]=mu; fitP[e]=mf
        bi=np.argmin(fitP)
        if fitP[bi]<fitG: fitG=float(fitP[bi]); Gbest=Pbest[bi].copy()
        sb=(Pbest>thres).astype(int); nm=pairwise_nhd(sb)
        nhd_curve[t]=nm.sum()/(N*(N-1)) if N>1 else 0.
        curve[t]=fitG
    return fitG,int((Gbest>thres).sum()),curve,nhd_curve,nhd_curve[1:].mean()


def run_PSO_CSM(X, y, opts):
    lb,ub,thres=0.,1.,opts["thres"]
    c1=c2=2.; wi=0.9; Vmax=0.6
    N,T,dim=opts["N"],opts["T"],X.shape[1]
    P=np.random.uniform(lb,ub,(N,dim)); V=np.zeros((N,dim))
    fit=np.array([jFitness(X,y,P[i]>thres,opts) for i in range(N)])
    fitP=fit.copy(); Pbest=P.copy(); Gbest=P[np.argmin(fit)].copy(); fitG=float(np.min(fit))
    curve=np.zeros(T+1); curve[0]=fitG
    for t in range(1,T+1):
        for i in range(N):
            r1,r2=np.random.rand(dim),np.random.rand(dim)
            V[i]=np.clip(wi*V[i]+c1*r1*(Pbest[i]-P[i])+c2*r2*(Gbest-P[i]),-Vmax,Vmax)
            P[i]=np.clip(P[i]+V[i],lb,ub)
            mask=P[i]>thres
            f=jFitness(X,y,mask,opts)
            nf=mask.sum(); score=f*(1+0.01*nf/dim)
            if score<fitP[i]: fitP[i]=score; Pbest[i]=P[i].copy()
        bi=np.argmin(fitP)
        if fitP[bi]<fitG: fitG=float(fitP[bi]); Gbest=Pbest[bi].copy()
        curve[t]=fitG
    nhd=np.zeros(T+1)
    return fitG,int((Gbest>thres).sum()),curve,nhd,0.0


def run_IGPSO(X, y, opts):
    lb,ub,thres=0.,1.,opts["thres"]
    c1=c2=2.; wi=0.9; Vmax=0.6
    N,T,dim=opts["N"],opts["T"],X.shape[1]
    importance=np.var(X,axis=0)+1e-8
    importance=importance/importance.sum()
    P=(np.random.rand(N,dim)<importance).astype(float)
    V=np.zeros((N,dim))
    fit=np.array([jFitness(X,y,P[i].astype(bool),opts) for i in range(N)])
    fitP=fit.copy(); Pbest=P.copy(); Gbest=P[np.argmin(fit)].copy(); fitG=float(np.min(fit))
    curve=np.zeros(T+1); curve[0]=fitG
    for t in range(1,T+1):
        for i in range(N):
            r1,r2=np.random.rand(dim),np.random.rand(dim)
            V[i]=np.clip(wi*V[i]+c1*r1*(Pbest[i]-P[i])+c2*r2*(Gbest-P[i]),-Vmax,Vmax)
            sig=1.0/(1+np.exp(-2*V[i]))
            P[i]=(np.random.rand(dim)<sig).astype(float)
            f=jFitness(X,y,P[i].astype(bool),opts)
            if f<fitP[i]: fitP[i]=f; Pbest[i]=P[i].copy()
        bi=np.argmin(fitP)
        if fitP[bi]<fitG: fitG=float(fitP[bi]); Gbest=Pbest[bi].copy()
        curve[t]=fitG
    nhd=np.zeros(T+1)
    return fitG,int(Gbest.astype(bool).sum()),curve,nhd,0.0


# ── 方法路由表 ────────────────────────────────────────────────────────
RUNNERS = {
    "BPSO":            run_BPSO,
    "SaWDE":           run_SaWDE,
    "FWPSO":           run_FWPSO,
    "MEL":             run_MEL,
    "MEL_NHD":         run_MEL_NHD,
    "MEL_KGEF_noNHD":  run_MEL_KGEF_noNHD,
    "MEL_KGEF":        run_MEL_KGEF,
    "PSO_CSM":         run_PSO_CSM,
    "IGPSO":           run_IGPSO,
}

# ── Resume helpers ────────────────────────────────────────────────────

def ensure_header():
    if not os.path.exists(CSV_PATH):
        with open(CSV_PATH,"w",newline="") as f:
            csv.DictWriter(f, fieldnames=CSV_FIELDS).writeheader()

def load_done():
    done=set()
    if not os.path.exists(CSV_PATH): return done
    with open(CSV_PATH,newline="") as f:
        for r in csv.DictReader(f):
            try: done.add((r["Version"],r["Dataset"],int(r["Run"])))
            except: pass
    return done

def append_row(row):
    with open(CSV_PATH,"a",newline="") as f:
        csv.DictWriter(f, fieldnames=CSV_FIELDS).writerow(row)

# ── Main ──────────────────────────────────────────────────────────────
ensure_header()
done = load_done()

if VERSION not in RUNNERS:
    raise ValueError(f"Unknown VERSION={VERSION}. Choose from: {list(RUNNERS.keys())}")

runner      = RUNNERS[VERSION]
total_scope = len(ONLY_DATASETS) * NUM_RUNS
done_this   = sum(1 for (v,_,_) in done if v==VERSION)

print(f"{'='*60}")
print(f"Version    : {VERSION}")
print(f"Datasets   : {len(ONLY_DATASETS)} × {NUM_RUNS} runs = {total_scope} tasks")
print(f"Done       : {done_this} / {total_scope}")
print(f"MAX_TASKS  : {MAX_TASKS}")
print(f"CSV  → {CSV_PATH}")
print(f"NPY  → {CURVES_DIR}")
print(f"{'='*60}")

# ── 启动诊断：验证所有数据集可正常加载 ───────────────────────────────
print("\n[诊断] 检查所有数据集:")
for ds in ONLY_DATASETS:
    try:
        X, y = load_dataset(ds)
        uc, cc = np.unique(y, return_counts=True)
        cls_str = " | ".join(f"cls{c}:{n}" for c, n in zip(uc.tolist(), cc.tolist()))
        print(f"  ✓ {ds:12s}: shape={X.shape}  n_classes={len(uc)}  [{cls_str}]")
    except Exception as e:
        print(f"  ✗ {ds:12s}: {e}")
print()

# ── 主循环 ────────────────────────────────────────────────────────────
tasks_run = 0
for ds in ONLY_DATASETS:
    try:
        X, y = load_dataset(ds)
    except Exception as e:
        print(f"\n[SKIP] {ds}: {e}")
        continue

    uc, cc = np.unique(y, return_counts=True)
    cls_str = " | ".join(f"cls{c}:{n}" for c, n in zip(uc.tolist(), cc.tolist()))
    print(f"\n{'='*60}")
    print(f"Dataset: {ds}  shape={X.shape}  n_classes={len(uc)}  [{cls_str}]")
    print(f"{'='*60}")

    for run in range(NUM_RUNS):
        if (VERSION, ds, run) in done:
            print(f"  [skip] {VERSION} | {ds} | run {run}")
            continue
        if MAX_TASKS is not None and tasks_run >= MAX_TASKS:
            remaining = total_scope - done_this - tasks_run
            print(f"\n[PAUSE] MAX_TASKS={MAX_TASKS} reached. ~{remaining} tasks left.")
            raise SystemExit(0)

        np.random.seed(SEED_BASE + run * 37)
        t0 = time()
        fitG, nf, curve, nhd_curve, avg_nhd = runner(X, y, OPTS)
        elapsed = time() - t0

        acc = 1.0 - float(fitG)
        append_row({
            "Version": VERSION, "Dataset": ds, "Run": run,
            "Accuracy": f"{acc:.6f}", "Num_Features": nf,
            "Avg_NHD": f"{avg_nhd:.6f}", "Time_sec": f"{elapsed:.2f}",
        })
        np.save(os.path.join(CURVES_DIR, f"curve_{VERSION}_{ds}_run{run}.npy"), curve)
        np.save(os.path.join(CURVES_DIR, f"nhd_{VERSION}_{ds}_run{run}.npy"),   nhd_curve)

        tasks_run += 1
        total_done = done_this + tasks_run
        print(f"  ✓ {VERSION} | {ds} | run {run:2d} | "
              f"Acc={acc:.4f} | Feat={nf:6d} | "
              f"NHD={avg_nhd:.3f} | t={elapsed:7.1f}s | "
              f"[{total_done}/{total_scope}]")

print(f"\n✅ {VERSION} — session complete.  "
      f"Total done: {done_this + tasks_run}/{total_scope}")