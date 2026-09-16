# 🚀 多机部署与高并发多进程实验运行指南

本文档指导您如何将 **KDS-EL** 实验工程完整迁移到另一台专用计算设备（Windows 工作站 / Linux 服务器），并利用多核并行算力高速完成 **EMSWOA** 的 20 个高维基准数据集评测。

---

## 📁 一、 迁移到另一台机器所需文件

只需打包拷贝整个工程目录 `KDS-EL`：
- `code/`：核心算法库、评测工具集及并行调度器；
- `datasets/`：20 个基准数据集（`Datasets_part1` 与 `Datasets_part2`）；
- `run_emswoa_parallel.bat`（Windows 一键运行脚本）；
- `run_emswoa_parallel.sh`（Linux 一键运行脚本）；
- `requirements.txt`（基础环境依赖清单）。

> **无需拷贝**：`output/` 中的历史输出若不需要可不拷贝（保留即可用于断点续跑）。

---

## ⚙️ 二、 环境准备

新机器需安装 **Python 3.9+** 及以下核心库：

```bash
pip install numpy scipy scikit-learn pandas
```

---

## 🚀 三、 启动运行方式

### 方式 1：Windows 工作站（最简一键双击）
1. 在新机器上直接双击打开项目根目录下的 **`run_emswoa_parallel.bat`**；
2. 窗口会显示当前机器的 CPU 核心数并提示输入并发进程数；
3. **直接按回车**（自动使用 `CPU核心数 - 2`），或输入指定核心数（例如 `8` 或 `12`）；
4. 程序将自动进行调度并动态显示每个数据集的进度和预计剩余时间（ETA）。

### 方式 2：Linux / Ubuntu 服务器
在终端中进入项目根目录：
```bash
# 赋予执行权限
chmod +x run_emswoa_parallel.sh

# 默认并发（自动适配核心数 - 2）
./run_emswoa_parallel.sh

# 或指定并发数（例如 8 个进程）
./run_emswoa_parallel.sh 8
```

### 方式 3：Python 命令行原生调用（全平台通用）
```bash
# 默认配置运行 EMSWOA（20 个数据集 × 10 轮）
python code/run_parallel_experiment.py --methods EMSWOA --out-dir output/formal_experiment_emswoa

# 自定义 8 个并发进程
python code/run_parallel_experiment.py --methods EMSWOA --workers 8 --out-dir output/formal_experiment_emswoa
```

---

## 🛡️ 四、 并发设计与质量保障

1. **零文件锁风险**：采用“子进程负责计算、主进程独占写盘”的 Master-Worker 架构，彻底规避 Windows/Linux 下多进程同时写 CSV 导致的死锁或文件写坏。
2. **CPU 物理核争抢防护**：每个子进程启动时均自动锁死 `OMP_NUM_THREADS=1` 与 `MKL_NUM_THREADS=1`，杜绝底层 BLAS/OpenMP 抢夺 CPU 导致性能急剧下降。
3. **LPT 最长作业优先调度**：先跑大样本高负荷数据集（`BASEHOCK`, `PCMAC`, `T1D` 等），小数据集在后方自动填补空余核心，消灭分布式长尾等待。
4. **断点自动续跑**：任何时候按 `Ctrl+C` 退出或机器重启，重新执行上述命令，系统将自动读取已写入的 `results_detail.csv`，跳过所有已完成项，无缝接续。

---

## 📊 五、 结果文件说明

实验完成后，所有数据统一保存在指定的输出目录（默认为 `output/formal_experiment_emswoa/`）：
- `results_summary.csv`：包含各数据集 10 轮运行的平均准确率、标准差、特征数、耗时等指标汇总表；
- `results_detail.csv`：200 轮单次独立运行的完整明细记录（单次运行即刻刷盘，断点安全）；
- `masks/`：保存 200 轮实验最终选出的最优特征子集掩码（`.npy` 格式）；
- `predictions/`：保存 200 轮实验在 5 折测试集上的全体样本预测标签向量（`.npz` 格式）；
- `curves/`：保存 200 轮实验的收敛曲线与多样性曲线。

跑完后，只需将生成的 `output/formal_experiment_emswoa/` 目录拷回，即可一键替换原有表格与折线图！
