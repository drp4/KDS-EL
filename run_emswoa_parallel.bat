@echo off
chcp 65001 >nul
title KDS-EL / EMSWOA 高并发多进程实验运行器

echo ==============================================================================
echo        KDS-EL 实验套件: EMSWOA 20 个高维基准数据集多进程加速运行器
echo ==============================================================================
echo.

:: 检查 Python 环境
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到 Python，请先安装 Python 3.9+ 并将其加入环境变量 PATH。
    pause
    exit /b 1
)

:: 检查依赖库
python -c "import numpy, scipy, sklearn, pandas" >nul 2>&1
if errorlevel 1 (
    echo [提示] 正在安装必要依赖 (numpy, scipy, scikit-learn, pandas)...
    pip install numpy scipy scikit-learn pandas
)

echo.
echo [提示] 默认并发进程数将自动匹配为 (CPU核心数 - 2)。
echo 如需自定义并发进程数（例如 8 个进程），请直接输入数字并回车；
echo 若直接按回车，则使用系统智能推荐的核心数。
echo.
set /p WORKER_INPUT="请输入并发工作进程数 [默认自动]: "

if "%WORKER_INPUT%"=="" (
    set WORKER_ARG=
) else (
    set WORKER_ARG=--workers %WORKER_INPUT%
)

set OUT_DIR=output\formal_experiment_emswoa

echo.
echo ==============================================================================
echo  启动实验: EMSWOA
echo  输出目录: %OUT_DIR%
echo  对标标准: 20 个高维基准数据集 x 10 次独立运行 (共 200 Runs)
echo  特性保障: 自动断点续跑、独立单核防护、主进程安全写盘
echo ==============================================================================
echo.

python code\run_parallel_experiment.py --methods EMSWOA %WORKER_ARG% --out-dir %OUT_DIR%

echo.
echo ==============================================================================
echo  实验执行结束！
echo  结果已保存至: %OUT_DIR%
echo ==============================================================================
pause
