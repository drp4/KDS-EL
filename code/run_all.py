"""
KDS-EL 全量实验 — 依次运行所有 9 种方法
=========================================
等价于 `python run.py`，按依赖顺序执行（从 baseline 到 proposed）。

依赖顺序：
  1. BPSO / SaWDE / FWPSO  — SOTA baseline（独立）
  2. MEL                   — 本框架 baseline
  3. MEL_NHD               — 消融：+DRS
  4. KDS_EL_KER            — 消融：+KER
  5. KDS_EL                — 完整 proposed 方法
  6. PSO_CSM / IGPSO       — 最新 SOTA 对比
"""
import os, sys
from time import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import config
from algorithms import RUNNERS
from utils import run_experiment, load_datasets

# ── 运行顺序（重要：MEL 系按依赖关系排列）────────────────────────────────
VERSION_ORDER = [
    "BPSO",
    "SaWDE",
    "FWPSO",
    "MEL",
    "MEL_NHD",
    "KDS_EL_KER",
    "KDS_EL",
    "PSO_CSM",
    "IGPSO",
]


def main():
    datasets = config.DATASETS
    csv_path = config.CSV_PATH
    curves_dir = config.CURVES_DIR
    num_runs = config.NUM_RUNS
    seed_base = config.SEED_BASE

    print(f"{'='*60}")
    print(f"KDS-EL 全量实验")
    print(f"  方法   : {len(VERSION_ORDER)} 种")
    print(f"  数据集 : {len(datasets)} 个 × {num_runs} runs = "
          f"{len(datasets) * num_runs} 任务/方法")
    print(f"  总计   : {len(VERSION_ORDER) * len(datasets) * num_runs} 个任务")
    print(f"{'='*60}\n")

    # ── 验证数据集可访问 ──────────────────────────────────────────────
    print("[诊断] 检查数据集加载...")
    loaded = load_datasets(datasets, config.DATA_DIR_TXT, config.DATA_DIR_MAT)
    available = list(loaded.keys())
    print(f"  可用: {len(available)}/{len(datasets)}\n")

    if not available:
        print("[ERROR] 没有可用的数据集，退出。")
        return

    # ── 逐个运行 ─────────────────────────────────────────────────────
    total_new = 0
    grand_start = time()

    for i, ver in enumerate(VERSION_ORDER):
        print(f"\n{'#'*60}")
        print(f"# [{i+1}/{len(VERSION_ORDER)}] {ver}")
        print(f"{'#'*60}")

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
            max_tasks=None,
        )
        elapsed = time() - t0
        total_new += n
        print(f"\n  [{ver}] {n} new tasks in {elapsed:.1f}s")

    grand_elapsed = time() - grand_start
    print(f"\n{'='*60}")
    print(f"✅ 全量实验完成！")
    print(f"   新增任务 : {total_new}")
    print(f"   总耗时   : {grand_elapsed:.1f}s ({grand_elapsed/3600:.1f}h)")
    print(f"   结果     : {csv_path}")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
