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

DATASETS = [
    # 9 个原始数据集
    "Adenoma", "ALL_AML", "ALL3", "ALL4", "CNS",
    "Colon", "DLBCL", "Leukaemia", "Lymphoma", "Stroke",
    # 新增 5 个
    "SRBCT", "Gastric", "Prostate", "BASEHOCK",
]

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
