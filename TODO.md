# TODO

> 2026-07-09 更新：15 方法 × 20 数据集实验全部完成（SOTA + MOFS + 消融）。待完成：图表重生成、论文写作。

---

## 1. 实验状态

### ✅ 已完成

| 实验 | 目录 | 方法 | 数据集 | 状态 |
|------|------|------|:---:|:---:|
| SOTA | `output/formal_experiment_20260701_094943/` | BPSO, FWPSO, IGPSO, PSO_CSM, SaWDE | 20 | ✅ |
| 消融 V1（仅 MEL） | `output/formal_experiment_20260628_205157/` | MEL | 26 | ✅ |
| 消融 V2 | `output/formal_experiment_20260702_145828/` | KDS_EL, KDS_EL_DRS, KDS_EL_KER | 26 | ✅ |
| MOFS | `output/formal_experiment_20260707_142018/` | NSGA-II-FS, MOPSO-FS, MOEA-D-FS, fMOPSO-FS, VGS-MOEA, W-MOPSO-FS | 20 | ✅ |

### 统计概览

| 指标 | 数值 |
|------|------|
| 规模 | 15 方法 × 20 数据集 × 10 runs |
| KDS_EL Acc | 0.9450（#2 overall，仅次 VGS-MOEA 0.9463） |
| KDS-EL 三变体 Friedman rank | 3.0-3.6（包揽前三） |
| vs 所有 SOTA 单目标方法 | 胜率 ≥ 90%（67W/0T/3L） |
| vs 基线 MEL | 20/20 wins，ΔAcc +0.058 |
| 特征减少 vs MEL（消融 26DS） | -93.4%（2989→198） |
| KDS_EL NHD | 0.324（vs MEL/KER/SOTA 全部 = 0.000） |

---

## 2. 图表生成

> 总计: **9 Tables + 12 Figures = 21 个**。需要基于 15 方法 × 20 数据集更新。

### Tables（9 个）

| # | 内容 | 状态 |
|---|------|:----:|
| T1 | 近 5 年 PSO-FS 文献对比 | ⚠ 需新写 |
| T2 | 20 数据集描述 | ⚠ 需新写 |
| T3 | 方法参数设置 | ⚠ 需新写 |
| T4 | **主表**准确率 Mean ± Std（10 方法 × 20 数据集） | 🔄 需适配 15 方法后重生成 |
| T5 | **主表**特征数 Mean（10 方法 × 20 数据集） | 🔄 需重生成 |
| T6 | Wilcoxon p 值矩阵（10 方法 × 20 数据集） | 🔄 需重生成 |
| T7 | 消融 ACC + Features（4 变体 × 26 数据集） | ✅ 不受 MOFS 影响 |
| T8 | MOFS 六方法单独对比 | 🆕 需新建 |
| T9 | 时间复杂度 O() | ⚠ 需新写 |

### Figures（12 个）

| # | 内容 | 状态 |
|---|------|:----:|
| F1 | KDS-EL 整体框架图 | △ 需 draw.io 新画 |
| F2 | DRS 机制示意图 | △ 需 draw.io 新画 |
| F3 | KER 机制示意图 | △ 需 draw.io 新画 |
| F4 | 准确率柱状图（10 方法，auto-grid，20 数据集） | 🔄 需适配 15 方法后重生成 |
| F5 | 特征数柱状图（对数轴，10 方法，20 数据集） | 🔄 需重生成 |
| F6 | 消融双面板（4 变体 × 26 数据集） | ✅ 不受 MOFS 影响 |
| F7 | 稳定性箱线图（10 方法，20 数据集） | 🔄 需重生成 |
| F8 | 收敛曲线（含 MOFS Top3，20 数据集） | 🔄 需重生成（需 npy） |
| F9 | NHD 多样性曲线（KDS_EL + DRS，20 数据集） | 🔄 需重生成（需 npy） |
| F10 | Wilcoxon 热图（10 方法 × 20 数据集） | 🔄 需重生成 |
| F11 | 运行时间对比（对数轴，10 方法，20 数据集） | 🔄 需重生成 |
| F12 | 精度-特征-时间气泡图（10 方法，20 数据集） | 🔄 需重生成 |

---

## 3. 论文写作

### 草稿状态
- [ ] Abstract（框架已有，更新至 20 DS 版）
- [ ] Introduction（框架已有）
- [ ] Related Work（全新写，~1200 词，3 小节，含 MOFS）
- [x] Methodology（主体完成，命名已统一 DRS/KER）
- [ ] Experiments
  - [ ] §5.1 Setup（20DS, 15 methods）
  - [ ] §5.2 Accuracy
  - [ ] §5.3 Feature Size
  - [ ] §5.4 Ablation
  - [ ] §5.5 MOFS Comparison（🆕 新增）
  - [ ] §5.6 Stability
  - [ ] §5.7 Trade-off
  - [ ] §5.8 Convergence
  - [ ] §5.9 NHD Analysis
  - [ ] §5.10 Runtime
  - [ ] §5.11 Discussion (ISOLET, COIL20 ceiling, VGS-MOEA)
- [ ] Conclusion

### LaTeX 文件状态
- `kdsol_packaging.tex` — Abstract + Introduction 框架，需更新数值
- `methodology_section.tex` — 主体完成
- `complexity_section.tex` — 时间复杂度完成
- `paper_complete_logic.tex` — ✅ 已更新至 15方法×20数据集
- 主 paper.tex — 待组装

---

## 4. 脚本更新

| 脚本 | 当前状态 | 需要 |
|------|:---:|------|
| `code/generate_figures.py` | 9 方法 × 14 数据集 | 扩至 15 方法 × 20 数据集，主图 10 方法 |
| `code/generate_tables.py` | 9 方法，T4-T7 | 扩至 15 方法，新增 T8 MOFS 表 |
| `code/plot_convergence.py` | 9 方法 | 新增 MOFS 曲线目录 + MOFS 方法 |
| `analysis/combine_analysis.py` | 2 实验目录 | 扩至 4 实验目录 |

---

## 5. 投稿前 Checklist

- [ ] 替换所有 `[CITE_X]` 占位符
- [ ] 生成 Holm-Bonferroni 校正表
- [ ] 生成收敛曲线图（`code/plot_convergence.py`，从 npy 文件）
- [ ] ISOLET/COIL20/VGS-MOEA 讨论段落（~500 词）
- [ ] MOFS 对比讨论段落（~400 词）
- [ ] 核实 Proposition labels
- [ ] 命名统一：全文 EMDO→DRS, KGEF→KER, 无 "w/o"/"SAR-MTPSO"
- [ ] Abstract ≤ 250 words
- [ ] 所有 Acc 标注为真实分类准确率（非 jFitness）
- [ ] 主表放 10 方法，完整 15 方法放附录
- [ ] 格式：期刊模板

---

## 6. 当前优先级

1. **更新生成脚本**（generate_figures.py + generate_tables.py + plot_convergence.py → 15 方法）
2. **重生成 T4-T8 + F4-F12**（基于更新后的脚本）
3. **写 Experiments 正文**（数据图表就绪后最快完成）
4. **写 Related Work**（~1200 词全新写，含 MOFS 文献）
5. **画 F1-F3 框架图**（draw.io）
6. **T1-T3, T9 表格**（文献/数据集/参数/复杂度）
7. **收敛图 F8-F9**（需本地 npy 文件）
