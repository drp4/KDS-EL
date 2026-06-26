"""
KDS-EL 实验运行器
==================
支持运行单个或全部算法。

用法：
    python run.py                          # 运行全部 9 种方法
    python run.py --version KDS_EL       # 只运行指定方法
    python run.py --version BPSO,MEL       # 运行多个方法（逗号分隔）
    python run.py --datasets Stroke        # 只运行指定数据集
    python run.py --max-tasks 50           # 每次最多跑 50 个任务（断点续跑）
    python run.py --csv results_test.csv   # 自定义输出路径
"""
import os, sys, argparse
from time import time

# 确保当前目录在 path 中
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import config
from algorithms import RUNNERS
from utils import run_experiment, load_datasets


def parse_args():
    parser = argparse.ArgumentParser(description="KDS-EL Experiment Runner")
    parser.add_argument("--version", type=str, default=None,
                        help="算法名称或逗号分隔列表（默认：全部）")
    parser.add_argument("--datasets", type=str, default=None,
                        help="数据集名称或逗号分隔列表（默认：全部）")
    parser.add_argument("--max-tasks", type=int, default=None,
                        help="每次最多跑多少任务")
    parser.add_argument("--csv", type=str, default=None,
                        help="结果 CSV 路径（默认：config.CSV_PATH）")
    parser.add_argument("--num-runs", type=int, default=None,
                        help="每个数据集运行次数（默认：config.NUM_RUNS）")
    parser.add_argument("--seed", type=int, default=None,
                        help="随机种子基值（默认：config.SEED_BASE）")
    return parser.parse_args()


def main():
    args = parse_args()

    # ── 确定运行范围 ──────────────────────────────────────────────────
    versions = args.version.split(",") if args.version else list(RUNNERS.keys())
    for v in versions:
        if v not in RUNNERS:
            print(f"[ERROR] 未知方法: {v}，可选: {list(RUNNERS.keys())}")
            return

    datasets = args.datasets.split(",") if args.datasets else config.DATASETS
    csv_path = args.csv or config.CSV_PATH
    num_runs = args.num_runs or config.NUM_RUNS
    seed_base = args.seed or config.SEED_BASE

    # ── 输出路径 ──────────────────────────────────────────────────────
    curves_dir = os.path.join(os.path.dirname(csv_path), "curves")
    os.makedirs(curves_dir, exist_ok=True)

    print(f"{'='*60}")
    print(f"KDS-EL 实验运行器")
    print(f"{'='*60}")
    print(f"方法     : {', '.join(versions)}")
    print(f"数据集   : {len(datasets)} 个")
    print(f"运行次数 : {num_runs} runs / dataset")
    print(f"输出 CSV : {csv_path}")
    print(f"输出 NPY : {curves_dir}")
    print(f"数据 TXT : {config.DATA_DIR_TXT}")
    print(f"数据 MAT : {config.DATA_DIR_MAT}")
    print(f"{'='*60}\n")

    # ── 验证数据集可加载 ──────────────────────────────────────────────
    print("[诊断] 检查数据集...")
    loaded = load_datasets(datasets, config.DATA_DIR_TXT, config.DATA_DIR_MAT)
    available = list(loaded.keys())
    if not available:
        print("[ERROR] 无可用的数据集，请检查路径。")
        return
    print(f"  可用: {len(available)}/{len(datasets)}\n")

    # ── 逐一运行 ─────────────────────────────────────────────────────
    total_new = 0
    for ver in versions:
        t0 = time()
        n = run_experiment(
            version=ver,
            runner_fn=RUNNERS[ver],
            datasets=available,
            opts=config.OPTS,
            num_runs=num_runs,
            seed_base=seed_base,
            csv_path=csv_path,
            curves_dir=curves_dir,
            csv_fields=config.CSV_FIELDS,
            data_dir_txt=config.DATA_DIR_TXT,
            data_dir_mat=config.DATA_DIR_MAT,
            max_tasks=args.max_tasks,
        )
        elapsed = time() - t0
        total_new += n
        print(f"  [{ver}] 完成 {n} 个新任务，耗时 {elapsed:.1f}s\n")

    print(f"{'='*60}")
    print(f"  全部完成！本次共运行 {total_new} 个新任务")
    print(f"  结果 → {csv_path}")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
