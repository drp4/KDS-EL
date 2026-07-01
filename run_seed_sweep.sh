#!/bin/bash
# ============================================================================
# KDS-EL 种子扫描脚本
# 在 Colon 数据集上测试多组新种子，结果按批次存入 output/ 子目录
# ============================================================================
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
CODE_DIR="$SCRIPT_DIR/code"
OUTPUT_DIR="$SCRIPT_DIR/output"

# 生成时间戳批次名
BATCH_NAME="colon_seeds_$(date +%Y%m%d_%H%M%S)"
BATCH_DIR="$OUTPUT_DIR/$BATCH_NAME"

echo "============================================"
echo " KDS-EL 种子扫描"
echo " 批次: $BATCH_NAME"
echo " 输出: $BATCH_DIR"
echo "============================================"

cd "$CODE_DIR"

# ---------------------------------------------------------------------------
# 第1批: 经典小种子 (0, 1, 7) + 中等种子 (99, 123)
# ---------------------------------------------------------------------------
echo ""
echo ">>> 第1批: 小种子 + 中等种子 (0,1,7,99,123)"
python test_kds_el_and_mel.py \
    --dataset Colon \
    --seeds 0,1,7,99,123 \
    --out-dir "$BATCH_DIR"/batch1_small_medium

# ---------------------------------------------------------------------------
# 第2批: 2的幂种子 (256, 512, 1024) + 社区种子 (42) 做参照
# ---------------------------------------------------------------------------
echo ""
echo ">>> 第2批: 2的幂种子 (256,512,1024)"
python test_kds_el_and_mel.py \
    --dataset Colon \
    --seeds 256,512,1024 \
    --out-dir "$BATCH_DIR"/batch2_pow2

# ---------------------------------------------------------------------------
# 第3批: 年份种子 (2023, 2024) + 社区常用 (666, 1337)
# ---------------------------------------------------------------------------
echo ""
echo ">>> 第3批: 年份 + 社区种子 (2023,2024,666,1337)"
python test_kds_el_and_mel.py \
    --dataset Colon \
    --seeds 2023,2024,666,1337 \
    --out-dir "$BATCH_DIR"/batch3_year_community

# ---------------------------------------------------------------------------
# 汇总所有批次结果
# ---------------------------------------------------------------------------
echo ""
echo "============================================"
echo " 汇总所有批次结果"
echo "============================================"

# 合并所有子目录的 results.csv
SUMMARY="$BATCH_DIR/results_all.csv"
HEADER="Algorithm,Dataset,Run,Accuracy,Num_Features,Avg_NHD,Time_sec"
echo "$HEADER" > "$SUMMARY"

for sub in "$BATCH_DIR"/batch*/results.csv; do
    if [ -f "$sub" ]; then
        tail -n +2 "$sub" >> "$SUMMARY"
    fi
done

echo "合并结果: $SUMMARY"
echo "行数: $(wc -l < "$SUMMARY") (含表头)"

# 打印 Top 10
echo ""
echo "========== Top 10 (按 Accuracy 降序) =========="
python -c "
import csv
rows = []
with open('$SUMMARY') as f:
    for r in csv.DictReader(f):
        r['Accuracy'] = float(r['Accuracy'])
        rows.append(r)
rows.sort(key=lambda r: r['Accuracy'], reverse=True)
print(f\"{'Rank':<5} {'Algorithm':<12} {'Seed':<6} {'Accuracy':<10} {'Features':<9} {'Avg_NHD':<9} {'Time':<7}\")
print('-' * 65)
for i, r in enumerate(rows[:10]):
    print(f\"{i+1:<5} {r['Algorithm']:<12} {r['Run']:<6} {r['Accuracy']:<10.4f} {r['Num_Features']:<9} {r['Avg_NHD']:<9} {r['Time_sec']:<7}\")
print()
# 按算法汇总
from collections import defaultdict
algo = defaultdict(list)
for r in rows:
    algo[r['Algorithm']].append(r['Accuracy'])
print('========== 算法平均 Accuracy (新种子) ==========')
for a in ['KDS_EL','KDS_EL_KER','MEL_NHD','MEL']:
    if a in algo:
        accs = algo[a]
        print(f\"  {a:<12s}  mean={sum(accs)/len(accs):.4f}  best={max(accs):.4f}  worst={min(accs):.4f}  std={ (sum((x-sum(accs)/len(accs))**2 for x in accs)/len(accs))**0.5 :.4f}\")
"

echo ""
echo "Done! 结果保存在: $BATCH_DIR"
