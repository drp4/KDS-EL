"""
KDS-EL 消融实验脚本
===================
默认比较 4 个方法：
  - MEL
  - KDS_EL_DRS
  - KDS_EL_KER
  - KDS_EL

支持多个数据集、可配置运行次数，并保存 CSV / 曲线 / NHD 曲线。
"""
import os, sys, csv, argparse
import numpy as np
from time import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config
from utils import load_dataset
from algorithms.mel import run_MEL
from algorithms.kds_el_drs import run_KDS_EL_DRS
from algorithms.kds_el_ker import run_KDS_EL_KER
from algorithms.kds_el import run_KDS_EL

METHODS = [
    ("MEL", run_MEL),
    ("KDS_EL_DRS", run_KDS_EL_DRS),
    ("KDS_EL_KER", run_KDS_EL_KER),
    ("KDS_EL", run_KDS_EL),
]


def parse_args():
    parser = argparse.ArgumentParser(description="KDS-EL ablation experiment runner")
    parser.add_argument("--dataset", type=str, default="Colon",
                        help="单个数据集名称，默认 Colon")
    parser.add_argument("--datasets", type=str, default=None,
                        help="多个数据集，逗号分隔；若设置则覆盖 --dataset")
    parser.add_argument("--seeds", type=str, default="42,43,44,45,46",
                        help="要测试的种子列表，逗号分隔；每个种子独立跑一次")
    parser.add_argument("--k", type=int, default=3,
                        help="KNN 邻居数，默认 3")
    parser.add_argument("--N", type=int, default=20,
                        help="粒子数，默认 20")
    parser.add_argument("--T", type=int, default=100,
                        help="迭代次数，默认 100")
    parser.add_argument("--thres", type=float, default=0.6,
                        help="二值化阈值，默认 0.6")
    parser.add_argument("--out-dir", type=str, default=None,
                        help="输出目录，默认 test_results_<dataset> 或 test_results_ablation")
    return parser.parse_args()


def summarize_rows(rows, label):
    accs = [r["Accuracy"] for r in rows]
    feats = [r["Num_Features"] for r in rows]
    nhds = [r["Avg_NHD"] for r in rows]
    times = [r["Time_sec"] for r in rows]
    print(f"\n{label}:")
    print(f"  Accuracy:     mean={np.mean(accs):.4f}  std={np.std(accs):.4f}  range=[{min(accs):.4f}, {max(accs):.4f}]")
    print(f"  Num_Features: mean={np.mean(feats):.1f}  std={np.std(feats):.1f}")
    print(f"  Avg_NHD:      mean={np.mean(nhds):.4f}  std={np.std(nhds):.4f}")
    print(f"  Time_sec:     mean={np.mean(times):.2f}  std={np.std(times):.2f}")


def main():
    args = parse_args()

    datasets = [d.strip() for d in args.datasets.split(",") if d.strip()] if args.datasets else [args.dataset]
    out_dir = args.out_dir
    if out_dir is None:
        out_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                               f"test_results_{datasets[0]}" if len(datasets) == 1 else "test_results_ablation")
    os.makedirs(out_dir, exist_ok=True)

    seeds = [int(s.strip()) for s in args.seeds.split(",") if s.strip()]

    print("=" * 72)
    print("KDS-EL 消融实验")
    print(f"数据集  : {', '.join(datasets)}")
    print(f"方法    : {', '.join(name for name, _ in METHODS)}")
    print(f"种子列表: {seeds}")
    print(f"输出目录: {out_dir}")
    print("=" * 72)

    opts = dict(config.OPTS)
    opts.update({
        "k": args.k,
        "N": args.N,
        "T": args.T,
        "thres": args.thres,
    })

    results = []
    fields = ["Algorithm", "Dataset", "Run", "Accuracy", "Num_Features", "Avg_NHD", "Time_sec"]

    for dataset in datasets:
        print(f"\n{'=' * 72}")
        print(f"数据集: {dataset}")
        print(f"{'=' * 72}")

        X, y = load_dataset(dataset, config.DATA_DIR_TXT, config.DATA_DIR_MAT)
        print(f"数据加载成功: shape={X.shape}, classes={len(np.unique(y))}")

        ds_dir = os.path.join(out_dir, dataset)
        os.makedirs(ds_dir, exist_ok=True)

        dataset_rows = []
        for algo_name, algo_fn in METHODS:
            print(f"\n{'─' * 54}")
            print(f"运行 {algo_name} ...")
            print(f"{'─' * 54}")

            for run_idx, seed in enumerate(seeds):
                np.random.seed(seed)
                t0 = time()
                res = algo_fn(X, y, opts)
                elapsed = time() - t0

                acc = 1.0 - float(res["fitG"])
                nf = int(res["nf"])
                nhd = res.get("nhd_curve", np.zeros(opts["T"] + 1))
                avg_nhd = float(np.mean(nhd[1:])) if np.any(nhd[1:]) else 0.0

                row = {
                    "Algorithm": algo_name,
                    "Dataset": dataset,
                    "Run": seed,
                    "Accuracy": round(acc, 6),
                    "Num_Features": nf,
                    "Avg_NHD": round(avg_nhd, 6),
                    "Time_sec": round(elapsed, 2),
                }
                results.append(row)
                dataset_rows.append(row)

                np.save(os.path.join(ds_dir, f"curve_{algo_name}_{dataset}_seed{seed}.npy"), res["curve"])
                np.save(os.path.join(ds_dir, f"nhd_{algo_name}_{dataset}_seed{seed}.npy"), nhd)

                print(f"  [OK] seed={seed} | Acc={acc:.4f} | Feat={nf:4d} | NHD={avg_nhd:.3f} | Time={elapsed:.1f}s")

        print(f"\n{'=' * 72}")
        print(f"数据集汇总: {dataset}")
        print(f"{'=' * 72}")
        for algo_name, _ in METHODS:
            algo_rows = [r for r in dataset_rows if r["Algorithm"] == algo_name]
            summarize_rows(algo_rows, algo_name)

        baseline_rows = [r for r in dataset_rows if r["Algorithm"] == "MEL"]
        if baseline_rows:
            base_acc = np.mean([r["Accuracy"] for r in baseline_rows])
            base_feat = np.mean([r["Num_Features"] for r in baseline_rows])
            print("\n相对 MEL 的平均变化:")
            for algo_name, _ in METHODS[1:]:
                algo_rows = [r for r in dataset_rows if r["Algorithm"] == algo_name]
                delta_acc = np.mean([r["Accuracy"] for r in algo_rows]) - base_acc
                delta_feat = np.mean([r["Num_Features"] for r in algo_rows]) - base_feat
                print(f"  {algo_name:<10s}  ΔAcc={delta_acc:+.4f}  ΔFeat={delta_feat:+.1f}")

    csv_path = os.path.join(out_dir, "results.csv")
    with open(csv_path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(results)

    print(f"\n结果已保存: {csv_path}")


if __name__ == "__main__":
    main()
