# TODO

> 实验进行中，待处理事项

---

## 1. 排除 CNS 数据集

**问题**：CNS 类别分布 `[39, 21, 1]`，一个类仅 1 个样本。`StratifiedKFold(5)` 无法划分，所有方法 Acc 锁死在 ~10%。

**影响数据**：
```
Version            Dataset  Acc       Num_Features
MEL                CNS      0.099958  3  (10/10 运行相同)
KDS_EL_DRS         CNS      0.099958  3  (10/10 运行相同)
KDS_EL_KER         CNS      (待验证)
KDS_EL             CNS      (待验证)
```

**方案**：从最终实验中移除 CNS，在论文中说明排除原因（极端小样本类别导致 CV 不可用，同领域论文均未使用）。

**执行**：
- [ ] 修改 `config.py` ALL_DATASETS，移除 "CNS"
- [ ] 更新 `实验计划.md` 数据集清单
- [ ] 论文中记录排除理由

---

## 2. 消融完成 ✅ → SOTA 数据集已确定

> 消融实验已完成：4 方法 × 26 数据集 × 10 次 = 1040 次
> 结果文件：`output/formal_experiment_20260628_205157/results_detail.csv`

**最终分类**（详见 [实验计划.md](实验计划.md) 第 9 节）：

| 类别 | 数量 | 数据集 | SOTA |
|:----|:---:|------|:---:|
| WIN | 17 | madelon, Lymphoma, Gastric2, Gastric1, ALL4, Prostate, Gastric, Adenoma, ALL1, ALL_AML, Myeloma, T1D, Leukaemia, Colon, SRBCT, ISOLET, DLBCL | ✅ |
| TIE | 5 | COIL20, RELATHE, BASEHOCK, USPS, PCMAC | 部分 |
| LOSE | 3 | ALL2, Stroke, ALL3 | ❌ |
| BUG | 1 | CNS | ❌ |

**执行**：
- [x] 消融 10-run 完成
- [x] 更新 `实验计划.md` 第 9 节（3-seed → 10-run Mean ± Std）
- [ ] 跑 SOTA 第一阶段（10 数据集）
- [ ] 跑 SOTA 第二阶段（7 数据集）
- [ ] 跑 SOTA 第三阶段（2 数据集，COIL20+USPS）

---

## 3. 统计检验

- [ ] Wilcoxon 符号秩检验（KDS_EL vs 每个对比方法，成对）
- [ ] Friedman 检验（跨数据集整体排名）
- [ ] Cohen's d 效应量

---

## 4. 图表生成（详见 [图表规划.md](图表规划.md)）

> 总计: **8 Tables + 12 Figures = 20 个**

### Tables（8 个）

| # | 内容 | 状态 |
|---|------|:----:|
| T1 | 近 5 年 PSO-FS 文献对比 | ⚠ 需新写 |
| T2 | 数据集描述 | ⚠ 需新写 |
| T3 | 方法参数设置 | ⚠ 需新写 |
| T4 | 准确率 Mean ± Std | √ `generate_tables.py` |
| T5 | 特征数 Mean | √ `generate_tables.py` |
| T6 | Wilcoxon p 值矩阵 | √ `generate_tables.py` |
| T7 | 消融 ACC + Features | √ `generate_tables.py` |
| T8 | 时间复杂度 O() | ⚠ 需新写 |

### Figures（12 个）

| # | 内容 | 状态 |
|---|------|:----:|
| F1 | KDS-EL 整体框架图 | △ 需 draw.io 新画 |
| F2 | DRS 机制示意图 | △ 需 draw.io 新画 |
| F3 | KER 机制示意图 | △ 需 draw.io 新画 |
| F4 | 准确率柱状图（3×3） | √ `generate_figures.py` |
| F5 | 特征数柱状图（对数轴，3×3） | √ `generate_figures.py` |
| F6 | 消融双面板 | √ `generate_figures.py` |
| F7 | 稳定性箱线图（3×3） | √ `generate_figures.py` |
| F8 | 收敛曲线（2×3） | △ 需 npy 文件 |
| F9 | NHD 多样性曲线（2×3） | △ 需 npy 文件 |
| F10 | Wilcoxon 热图 | √ `generate_figures.py` |
| F11 | 运行时间对比 | √ `generate_figures.py` |
| F12 | 精度-特征-时间气泡图 | √ `generate_figures.py` |

### 状态图例

| 标记 | 含义 |
|:----:|------|
| ⚠ | 无脚本，需手动制作 |
| √ | 代码可自动生成，等新数据重跑 |
| △ | 需 npy 文件 或 draw.io 画新图 |

---

## 5. 论文写作

- [ ] Abstract
- [ ] Introduction
- [ ] Related Work
- [ ] Methodology（EMDO→DRS, KGEF→KER 命名统一）
- [ ] Experiments
- [ ] Conclusion
