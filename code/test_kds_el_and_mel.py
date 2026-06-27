"""
测试 KDS-EL vs MEL on BASEHOCK
运行各 5 次，保存结果到新文件夹 test_results_BASEHOCK/
"""
import os, sys, csv, json
import numpy as np
from time import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from utils import load_dataset
from algorithms.mel import run_MEL
from algorithms.kds_el import run_KDS_EL

# ── 配置 ─────────────────────────────────────────────────────────────────
DATASET = "Colon"
NUM_RUNS = 5
SEED_BASE = 42

DATA_DIR_TXT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "datasets", "Datasets_part1")
DATA_DIR_MAT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "datasets", "Datasets_part2")

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

# ── 输出目录 ──────────────────────────────────────────────────────────────
OUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "test_results_Colon")
os.makedirs(OUT_DIR, exist_ok=True)

# ── 加载数据 ──────────────────────────────────────────────────────────────
print("=" * 60)
print(f"测试 KDS-EL vs MEL")
print(f"数据集: {DATASET}")
print(f"运行次数: {NUM_RUNS}")
print(f"输出目录: {OUT_DIR}")
print("=" * 60)

X, y = load_dataset(DATASET, DATA_DIR_TXT, DATA_DIR_MAT)
print(f"\n数据加载成功: shape={X.shape}, classes={len(np.unique(y))}\n")

# ── 运行 ──────────────────────────────────────────────────────────────────
results = []

for algo_name, algo_fn in [("MEL", run_MEL), ("KDS_EL", run_KDS_EL)]:
    print(f"\n{'─' * 50}")
    print(f"运行 {algo_name} ...")
    print(f"{'─' * 50}")

    for run in range(NUM_RUNS):
        np.random.seed(SEED_BASE + run * 37)
        t0 = time()
        res = algo_fn(X, y, OPTS)
        elapsed = time() - t0

        acc = 1.0 - float(res["fitG"])
        nf = int(res["nf"])
        nhd = res.get("nhd_curve", np.zeros(OPTS["T"] + 1))
        avg_nhd = float(np.mean(nhd[1:])) if np.any(nhd[1:]) else 0.0

        results.append({
            "Algorithm": algo_name,
            "Dataset": DATASET,
            "Run": run,
            "Accuracy": round(acc, 6),
            "Num_Features": nf,
            "Avg_NHD": round(avg_nhd, 6),
            "Time_sec": round(elapsed, 2),
        })

        # 保存 curve
        np.save(os.path.join(OUT_DIR, f"curve_{algo_name}_{DATASET}_run{run}.npy"), res["curve"])
        if "nhd_curve" in res:
            np.save(os.path.join(OUT_DIR, f"nhd_{algo_name}_{DATASET}_run{run}.npy"), res["nhd_curve"])

        print(f"  [OK] run {run} | Acc={acc:.4f} | Feat={nf:4d} | NHD={avg_nhd:.3f} | Time={elapsed:.1f}s")

# ── 汇总 ──────────────────────────────────────────────────────────────────
print(f"\n{'=' * 60}")
print(f"汇总")
print(f"{'=' * 60}")

for algo_name in ["MEL", "KDS_EL"]:
    algo_results = [r for r in results if r["Algorithm"] == algo_name]
    accs = [r["Accuracy"] for r in algo_results]
    feats = [r["Num_Features"] for r in algo_results]
    nhds = [r["Avg_NHD"] for r in algo_results]
    times = [r["Time_sec"] for r in algo_results]

    print(f"\n{algo_name}:")
    print(f"  Accuracy:      mean={np.mean(accs):.4f}  std={np.std(accs):.4f}  range=[{min(accs):.4f}, {max(accs):.4f}]")
    print(f"  Num_Features:  mean={np.mean(feats):.1f}  std={np.std(feats):.1f}")
    print(f"  Avg_NHD:       mean={np.mean(nhds):.4f}  std={np.std(nhds):.4f}")
    print(f"  Time_sec:      mean={np.mean(times):.2f}  std={np.std(times):.2f}")

# ── 写入 CSV ──────────────────────────────────────────────────────────────
csv_path = os.path.join(OUT_DIR, "results.csv")
fields = ["Algorithm", "Dataset", "Run", "Accuracy", "Num_Features", "Avg_NHD", "Time_sec"]
with open(csv_path, "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=fields)
    w.writeheader()
    w.writerows(results)
print(f"\n结果已保存: {csv_path}")
