#!/usr/bin/env bash
# ==============================================================================
#  KDS-EL 实验套件: EMSWOA 20 个高维基准数据集多进程加速运行器 (Linux / Shell)
# ==============================================================================

set -e

# 自动切换到脚本所在项目根目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "=============================================================================="
echo "       KDS-EL 实验套件: EMSWOA 20 个高维基准数据集多进程加速运行器"
echo "=============================================================================="
echo ""

# 检查 Python
if ! command -v python3 &> /dev/null; then
    if ! command -v python &> /dev/null; then
        echo "[错误] 未检测到 Python，请先安装 Python 3.9+。"
        exit 1
    else
        PY_BIN="python"
    fi
else
    PY_BIN="python3"
fi

# 检查依赖库
$PY_BIN -c "import numpy, scipy, sklearn, pandas" &> /dev/null || {
    echo "[提示] 检测到缺失依赖，正在安装 (numpy, scipy, scikit-learn, pandas)..."
    pip install numpy scipy scikit-learn pandas
}

# 并发配置（可通过第一个参数传入，如 ./run_emswoa_parallel.sh 8）
if [ -n "$1" ]; then
    WORKER_ARG="--workers $1"
    echo "[配置] 已指定并发工作进程数: $1"
else
    WORKER_ARG=""
    echo "[配置] 使用系统智能推荐并发数 (CPU核心数 - 2)"
fi

OUT_DIR="output/formal_experiment_emswoa"

echo ""
echo "=============================================================================="
echo " 启动实验: EMSWOA"
echo " 输出目录: $OUT_DIR"
echo " 评测范围: 20 个高维基准数据集 × 10 次独立运行 (共 200 Runs)"
echo " 核心保障: 自动断点续跑、独立单核防护、主进程安全写盘"
echo "=============================================================================="
echo ""

$PY_BIN code/run_parallel_experiment.py --methods EMSWOA $WORKER_ARG --out-dir "$OUT_DIR"

echo ""
echo "=============================================================================="
echo " ✅ 实验执行结束！结果已保存至: $OUT_DIR"
echo "=============================================================================="
