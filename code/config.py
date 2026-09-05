"""
KDS-EL 实验配置
================
所有路径可通过环境变量覆盖，方便在不同环境下切换（Kaggle / 本地）。
"""
import os

# ── 项目根目录（根据本文件位置自动推导）────────────────────────────────────
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ── 路径配置（基于项目根目录的相对路径，多设备可直接移植）───────────────────
# 可通过环境变量覆盖（如 Kaggle 上设置 KDS_DATA_TXT=/kaggle/input/...）
DATA_DIR_TXT = os.environ.get("KDS_DATA_TXT",
                              os.path.join(_PROJECT_ROOT, "datasets", "Datasets_part1"))
DATA_DIR_MAT = os.environ.get("KDS_DATA_MAT",
                              os.path.join(_PROJECT_ROOT, "datasets", "Datasets_part2"))
OUT_DIR      = os.environ.get("KDS_OUT_DIR",
                              os.path.join(_PROJECT_ROOT, "output"))

CURVES_DIR   = os.path.join(OUT_DIR, "curves")
CSV_PATH     = os.path.join(OUT_DIR, "results.csv")
os.makedirs(CURVES_DIR, exist_ok=True)
os.makedirs(OUT_DIR, exist_ok=True)

# ── 实验配置 ─────────────────────────────────────────────────────────────
NUM_RUNS   = 10
SEED_BASE  = 42

# ── 优选种子（Colon 数据集上 KDS_EL 验证最优）───────────────────────────
# 种子7:  Acc=0.9801, Feat=98,  NHD=0.197 — 绝对最优
# 种子30: Acc=0.9530, Feat=39,  NHD=0.405 — 最精简高效
# 种子1:  Acc=0.9491, Feat=141, NHD=0.173 — 多样性退化最小
BEST_SEEDS = [7, 30, 1]

DATASETS = [
    # ── 12 个基因数据集（MEL 原版）─────────────────────────────
    "Adenoma", "ALL_AML", "ALL3", "ALL4", "CNS",
    "Colon", "DLBCL", "Leukaemia", "Lymphoma", "Stroke",
    "Gastric", "Prostate",
    # ── 额外基因数据集 ─────────────────────────────────────────
    "ALL1", "ALL2", "Gastric1", "Gastric2", "Myeloma", "SRBCT", "T1D",
    # ── 10 个大样本数据集 ──────────────────────────────────────
    "BASEHOCK", "COIL20", "ISOLET", "madelon",
    "PCMAC", "RELATHE", "USPS",
]

ALL_DATASETS = [
    # ── 12 个基因数据集（MEL 原版）─────────────────────────────
    "Adenoma", "ALL_AML", "ALL3", "ALL4", "CNS",
    "Colon", "DLBCL", "Leukaemia", "Lymphoma", "Stroke",
    "Gastric", "Prostate",
    # ── 额外基因数据集 ─────────────────────────────────────────
    "ALL1", "ALL2", "Gastric1", "Gastric2", "Myeloma", "SRBCT", "T1D",
    # ── 10 个大样本数据集 ──────────────────────────────────────
    "BASEHOCK", "COIL20", "ISOLET", "madelon",
    "PCMAC", "RELATHE", "USPS",
]

# ── 标准 20 个高维基准数据集 ───────────────────────────────────────────────
BENCHMARK_20_DATASETS = [
    "ALL1", "ALL4", "ALL_AML", "Adenoma", "BASEHOCK", "COIL20",
    "Colon", "DLBCL", "Gastric", "Gastric1", "Gastric2", "ISOLET",
    "Leukaemia", "Lymphoma", "Myeloma", "PCMAC", "Prostate",
    "SRBCT", "T1D", "madelon",
]
MOFS_DATASETS = BENCHMARK_20_DATASETS  # 兼容旧代码引用

OPTS = {
    "k": 3,
    "N": 20,
    "T": 100,
    "thres": 0.6,
    "ws": [0.9, 0.1],
    "cv_splits": 5,
    "cv_shuffle": True,
    "cv_random_state": 42,
    "weight_decay": 0.99,
    "flip_frac": 0.01,
    "elite_k": 3,
    "rand_flip_p": 0.10,
}

CSV_FIELDS = [
    "Version", "Dataset", "Run",
    "Accuracy", "Num_Features", "Avg_NHD", "Time_sec",
]

# ── 数据集特殊配置 ───────────────────────────────────────────────────────
SPECIAL_COL = {"CNS": 3, "MLL": 3}   # 标签/数据列从第几列开始

SRBCT_KEEP = {"BL", "EWS", "NB", "RMS"}  # SRBCT 标准 4 类

MAT_DATASETS = {
    "BASEHOCK", "COIL20", "PCMAC", "RELATHE", "ISOLET",
    "USPS", "Pancancer", "MultipleFeaturesDigit", "madelon",
}

# ── 数据集原始特征维度 D（加速特征选择率计算）──────────────────────────────
DATASET_DIMS = {
    "Adenoma": 7457,
    "ALL_AML": 7129,
    "ALL3": 12625,
    "ALL4": 12625,
    "CNS": 7129,
    "Colon": 2000,
    "DLBCL": 7129,
    "Leukaemia": 7129,
    "Lymphoma": 4026,
    "Stroke": 54675,
    "Gastric": 22645,
    "Prostate": 12625,
    "ALL1": 12625,
    "ALL2": 12625,
    "Gastric1": 22283,
    "Gastric2": 22283,
    "Myeloma": 12625,
    "SRBCT": 2308,
    "T1D": 54675,
    "BASEHOCK": 4862,
    "COIL20": 1024,
    "ISOLET": 617,
    "madelon": 500,
    "PCMAC": 3289,
    "RELATHE": 4322,
    "USPS": 256,
}

