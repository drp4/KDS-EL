# TODO

> 2026-07-13 更新：**P0叙事修正完成**。放弃"协同/synergy"作为卖点，重构为"互补/三轴平衡"框架。
> 数据不变，叙事匹配证据。paper_complete_logic.tex 已更新。
> 上一条：2026-07-09（15方法×20数据集实验全部完成）

---

## 0. P0 叙事修正（2026-07-13）✅

| 问题 | 证据 | 修正方案 | 状态 |
|------|------|----------|:--:|
| **C1 协同证伪** | Synergy=-3.76pp（25DS），正协同仅 6/25 (24%) | 放弃"协同"，改用"互补"——DRS/KER各解决一个困境 | ✅ |
| **C2 VGS-MOEA支配** | VGS-MOEA Acc=0.9463, Feat=51, Time=34.2s 三轴全胜 | 正面承认；区分单解vs Pareto前沿；额外优势：稳定性(12/20) | ✅ |
| **C3 DRS准确率≈0** | KER 0.9271 vs Full 0.9291, Δ=+0.0020, Fisher p=6.5e-4 | 统计显著但幅度小；DRS价值重定向为多样性(NHD>0)+压缩 | ✅ |
| **天花板辩护** | 9/25 Acc>0.99 压低差异；非饱和子集(n=13): ΔFull=+0.0404 | 已有非饱和子集重算 | ✅ |
| **Prop 2 proof sketch** | 仅为概率论证 | 补充形式化界：翻转概率≥(1/N)·(w_j/Σw)·p_mut | △ |

### 修正后的核心主张

> **KDS-EL = KER（有效在线知识引导增强，捕获几乎全部准确率收益）+ DRS（可证下界维持结构多样性 + 大幅特征压缩），代价为可忽略的准确率损失。** 两个模块互补而非协同增强：KER覆盖DRS的准确率弱点（困难数据集上DRS单独为负），DRS覆盖KER的多样性盲点（KER单独NHD≡0）。完整框架是唯一同时在Acc+NHD+Feat三轴上达到前沿水平的单解方法。

### 关键新增统计

- **KER vs Full 配对Wilcoxon**: Fisher combined p = 6.5e-4（统计显著）
- **非饱和子集** (Acc<0.95, n=13): Full vs KER ΔAcc=+0.44pp, Fisher p=0.0024
- **KDS-EL vs VGS-MOEA 稳定性**: KDS-EL std=0.0074 vs 0.0092, 12/20更稳定
- **combine_analysis.py Bug修复**: Exp2含全部4变体（非仅MEL），旧代码concat导致重复条目

### 新增/修改脚本

| 脚本 | 说明 |
|------|------|
| `analysis/critical_audit.py` | 🆕 完整审计：synergy验证 + KER vs Full Wilcoxon + 天花板过滤 + VGS-MOEA对比 |
| `analysis/combine_analysis.py` | 修复Exp2重复bug + 新增§10(KER vs Full Wilcoxon) + §11(天花板过滤) + §12(VGS-MOEA稳定性) |
| `paper_complete_logic.tex` | 重写§5.4消融、§5.5 MOFS、核心问题定义、审稿人Q&A、关键数字 |

---
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
| T4 | **主表**准确率 Mean ± Std（10 方法 × 20 数据集） | ✅ 已重生成（15方法完整版） |
| T5 | **主表**特征数 Mean（10 方法 × 20 数据集） | ✅ 已重生成 |
| T6 | Wilcoxon p 值矩阵（10 方法 × 20 数据集） | ✅ 已重生成 |
| T6b | Holm-Bonferroni 校正表 | 🆕 已新增 |
| T7 | 消融 ACC + Features（4 变体 × 25 数据集） | ✅ |
| T8 | MOFS 六方法单独对比 | ✅ 已生成 |
| T9 | 时间复杂度 O() | ⚠ 需新写 |

### Figures（12 个）

| # | 内容 | 状态 |
|---|------|:----:|
| F1 | KDS-EL 整体框架图 | △ 需 draw.io 新画 |
| F2 | DRS 机制示意图 | △ 需 draw.io 新画 |
| F3 | KER 机制示意图 | △ 需 draw.io 新画 |
| F4 | 准确率柱状图（10 方法，auto-grid，20 数据集） | ✅ 已重生成（15方法） |
| F5 | 特征数柱状图（对数轴，10 方法，20 数据集） | ✅ 已重生成 |
| F6 | 消融双面板（4 变体 × 25 数据集） | ✅ |
| F7 | 稳定性箱线图（10 方法，20 数据集） | ✅ 已重生成 |
| F8 | 收敛曲线（含 MOFS Top3，20 数据集） | ✅ 已重生成 |
| F9 | NHD 多样性曲线（KDS_EL + DRS，20 数据集） | ✅ 已重生成 |
| F10 | Wilcoxon 热图（10 方法 × 20 数据集） | ✅ 已重生成 |
| F11 | 运行时间对比（对数轴，10 方法，20 数据集） | ✅ 已重生成 |
| F12 | 精度-特征-时间气泡图（10 方法，20 数据集） | ✅ 已重生成 |

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
- [x] 生成 Holm-Bonferroni 校正表（T6b）
- [x] 生成收敛曲线图（`code/plot_convergence.py`）
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

1. ~~**更新生成脚本**~~ ✅（generate_figures.py + generate_tables.py + plot_convergence.py → 15 方法）
2. ~~**重生成 T4-T8 + F4-F12**~~ ✅（基于更新后的脚本）
3. **写 Experiments 正文**（数据图表就绪后最快完成）
4. **写 Related Work**（~1200 词全新写，含 MOFS 文献）
5. **画 F1-F3 框架图**（draw.io）
6. **T1-T3, T9 表格**（文献/数据集/参数/复杂度）
