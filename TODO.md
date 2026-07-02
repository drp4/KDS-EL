# TODO

> 2026-07-02 更新：17 数据集 × 9 方法实验已完成，核心统计已计算。待完成：图表重生成、论文写作。

---

## 1. 排除数据集 ✅ 已完成

| 数据集 | 原因 | 状态 |
|--------|------|:----:|
| CNS | 类别分布 [39,21,1]，一个类仅 1 样本，StratifiedKFold(5) 不可用，所有方法 ~10% | ✅ 已移除 |
| Stroke | d=26877, n=2500，耗时极端。已有 T1D(d=54675) 覆盖大样本+高维场景 | ✅ 已移除 |
| ALL3 | n=36, d=9999。极端小样本，5折每折7个训练样本，KER 不可靠 | ✅ 已移除 |

**最终数据集：17 个**（见 `kdsol_memory.md` §三）

---

## 2. 实验状态

### 已完成
- [x] KDS-EL 家族消融（4 变体 × 25 数据集 × 10 runs）→ `output/formal_experiment_20260628_205157/`
- [x] 外部对比方法（5 方法 × 17 数据集 × 10 runs）→ `output/formal_experiment_20260701_094943/`
- [x] 合并分析脚本 → `analysis/combine_analysis.py`
- [x] 核心统计计算（Friedman, rankings, synergy, 特征减少率）

### 统计概览

| 指标 | 数值 |
|------|------|
| 规模 | 9 方法 × 17 数据集 × 10 runs |
| Friedman χ² | 94.23, p=6.43×10⁻¹⁷ |
| KDS-EL rank | 1.059 (17×#1) |
| vs 外部分法 | 17/17 BPSO, 16/17 SaWDE, 17/17 FWPSO, 17/17 PSO-CSM, 17/17 IGPSO |
| 特征减少 vs MEL | -83.6% (2989→491) |
| 消融正协同 | 16/17, mean +3.02pp |

---

## 3. 统计检验

- [ ] Wilcoxon 符号秩检验（KDS-EL vs 每个对比方法，per-dataset，基于 10-run detail）
- [ ] Holm-Bonferroni 校正（多重比较校正表）
- [ ] Cohen's d 效应量

---

## 4. 图表生成

> 总计: **8 Tables + 12 Figures = 20 个**。需要基于新的 17 数据集数据重新生成。

### Tables（8 个）

| # | 内容 | 状态 |
|---|------|:----:|
| T1 | 近 5 年 PSO-FS 文献对比 | ⚠ 需新写 |
| T2 | 17 数据集描述（n, d, classes, source） | ⚠ 需新写 |
| T3 | 9 方法参数设置 | ⚠ 需新写 |
| T4 | 准确率 Mean ± Std（17 DS × 9 methods） | ⚠ 需重新生成（读两份 CSV 合并） |
| T5 | 特征数 Mean | ⚠ 需重新生成 |
| T6 | Wilcoxon p 值矩阵 | ⚠ 需重新生成 |
| T7 | 消融 ACC + Features（17 DS × 4 variants） | ⚠ 需重新生成 |
| T8 | 时间复杂度 O() | ✓ 已有（`complexity_section.tex`），需更新运行时间数字 |

### Figures（12 个）

| # | 内容 | 状态 |
|---|------|:----:|
| F1 | KDS-EL 整体框架图 | △ 需 draw.io 新画 |
| F2 | DRS 机制示意图 | △ 需 draw.io 新画 |
| F3 | KER 机制示意图 | △ 需 draw.io 新画 |
| F4 | 准确率柱状图 | △ 需重生成（17 DS 版，布局可能改 4×4+1 或 5×4） |
| F5 | 特征数柱状图（对数轴） | △ 需重生成 |
| F6 | 消融双面板 | △ 需重生成 |
| F7 | 稳定性箱线图 | △ 需重生成 |
| F8 | 收敛曲线 | △ 需 npy 文件（位于 `output/*/curves/`） |
| F9 | NHD 多样性曲线 | △ 需 npy 文件 |
| F10 | Wilcoxon 热图 | △ 需重生成 |
| F11 | 运行时间对比 | △ 需重生成 |
| F12 | 精度-特征-时间气泡图 | △ 需重生成 |

### 状态图例

| 标记 | 含义 |
|:----:|------|
| ⚠ | 无脚本，需手动制作 |
| ✓ | 已完成 |
| △ | 需重新生成或补充数据文件 |

---

## 5. 论文写作

### 草稿状态
- [ ] Abstract（框架已有，更新数值至 17 DS 版）
- [ ] Introduction（框架已有）
- [ ] Related Work（全新写，~1200 词，3 小节）
- [x] Methodology（主体完成，命名已统一 DRS/KER）
- [ ] Experiments
  - [ ] §5.1 Setup（17DS, 9 methods）
  - [ ] §5.2 Accuracy
  - [ ] §5.3 Feature Size
  - [ ] §5.4 Ablation
  - [ ] §5.5 Stability
  - [ ] §5.6 Trade-off
  - [ ] §5.7 Convergence
  - [ ] §5.8 NHD Analysis
  - [ ] §5.9 Runtime
  - [ ] §5.10 Discussion (ISOLET limitation, n<40 boundary)
- [ ] Conclusion

### LaTeX 文件状态
- `kdsol_packaging.tex` — Abstract + Introduction 框架，需更新数值
- `methodology_section.tex` — 主体完成
- `complexity_section.tex` — 时间复杂度完成
- `paper_complete_logic.tex` — ✅ 已更新至 17 DS 数据
- 主 paper.tex — 待组装

---

## 6. 投稿前 Checklist

- [ ] 替换所有 `[CITE_X]` 占位符
- [ ] 生成 Holm-Bonferroni 校正表
- [ ] 生成收敛曲线图（`code/plot_convergence.py`，从 npy 文件）
- [ ] ISOLET 讨论段落（~400 词）
- [ ] 核实 Proposition labels
- [ ] 命名统一：全文 EMDO→DRS, KGEF→KER, 无 "w/o"
- [ ] Abstract ≤ 250 words
- [ ] 同机重跑所有 9 方法获得可比的运行时间数据
- [ ] 格式：ESWA 模板

---

## 7. 当前优先级

1. **重生成 T4-T7 + F4-F7, F10-F12**（读两份 CSV，合并后生成 17DS 版本图表）
2. **写 Experiments 正文**（数据图表就绪后最快完成）
3. **写 Related Work**（~1200 词全新写）
4. **画 F1-F3 框架图**（draw.io）
5. **T1-T3 表格**（文献/数据集/参数）
6. **收敛图 F8-F9**（需本地 npy 文件）
