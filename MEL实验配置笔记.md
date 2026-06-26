# MEL 实验配置笔记

## 论文信息

- **标题**: MEL: Efficient Multi-Task Evolutionary Learning for High-Dimensional Feature Selection
- **arXiv**: 2402.08982v1
- **代码**: https://github.com/wangxb96/MEL

---

## 实验重复次数

**每个数据集独立重复 10 次。**

- "We performed each experiment **ten times** and averaged the data to make sure the experimental results were stable."（Section IV-C）
- "Each experiment was repeated **10 times**, and the average values (denoted as 'Mean') and standard deviations (denoted as 'Std') were calculated."（Section V）

所有结果表中的 `Mean ± Std` 均来自这 10 次重复实验。

---

## 随机种子（Seed）

**论文中未指定任何具体的随机种子值。**

文中仅提到粒子初始化是随机的（"initialize the particles randomly"），PSO 更新公式中使用均匀随机数 `r1, r2, r3 ~ U[0,1]`，但**没有说明**所使用的随机种子值（如 0、42、12345 等），也没有说明是否固定了随机种子。

因此，这 10 次重复实验的随机性来源是未固定的，结果表中的标准差反映了算法在默认随机状态下的稳定性。

---

## 算法参数配置

| 参数 | 值 | 说明 |
|------|-----|------|
| 种群大小（NP） | 20 | 分为两个等大小子种群（Sub1 和 Sub2），各 10 个粒子 |
| 最大迭代次数（T） | 100 | |
| 阈值（θ） | 0.6 | 用于将实数编码二值化，决定特征是否被选中 |
| 分类器 | KNN（k=3） | 评价特征子集的分类器 |
| 评估方式 | 5-fold 交叉验证 | 准确率取 5 折平均 |
| 适应度函数权重 α | 0.9 | 分类结果控制权重 |
| 适应度函数权重 β | 0.1 | 特征子集大小控制权重 |

---

## 数据集信息

### 12 个高维基因数据集（小样本，高维数）

| 数据集 | 样本数 | 特征数 | 类别数 |
|--------|--------|--------|--------|
| Adenoma | 36 | 7,457 | 2 |
| ALL AML | 72 | 7,129 | 2 |
| ALL3 | 125 | 12,625 | 2 |
| ALL4 | 93 | 12,625 | 2 |
| CNS | 60 | 7,129 | 2 |
| Colon | 62 | 2,000 | 2 |
| DLBCL | 77 | 7,129 | 2 |
| Gastric | 65 | 22,645 | 2 |
| Leukemia | 72 | 7,129 | 2 |
| Lymphoma | 45 | 4,026 | 2 |
| Prostate | 102 | 12,625 | 2 |
| Stroke | 40 | 54,675 | 2 |

### 10 个大样本高维数据集

| 数据集 | 样本数 | 特征数 | 类别数 |
|--------|--------|--------|--------|
| BASEHOCK | 1,993 | 4,862 | 2 |
| COIL20 | 1,440 | 1,024 | 20 |
| HAPTDataSet | 1,200 | 561 | 12 |
| Isolet | 1,560 | 617 | 26 |
| madelon | 2,600 | 500 | 2 |
| MultipleFeaturesDigit | 1,000 | 649 | 10 |
| Pancancer | 4,759 | 20,486 | 2 |
| PCMAC | 1,943 | 3,289 | 2 |
| RELATHE | 1,427 | 4,322 | 2 |
| USPS | 9,298 | 256 | 10 |

---

## 对比算法

共对比 **24 种 EC 算法**：

- **Swarm-based (4)**: ABC, ACO, PSO, MBO
- **Nature-inspired (4)**: BAT, CS, FA, FPA
- **Evolutionary (2)**: DE, GA（Roulette + Tournament）
- **Bio-stimulated (4)**: FOA, GWO, HHO, WOA
- **Physics-based (4)**: SA, HS, GSA, MVO
- **Recent EC methods (6)**: SaWDE, FWPSO, VGS-MOEA, MTPSO, PSO-EMT, DENCA

---

## 运行环境

| 实验部分 | 环境 |
|----------|------|
| Section V A–E | CentOS, Intel Xeon Silver 4215R @ 3.20GHz, 16GB RAM, MATLAB R2019b |
| Section V F–G | 13th Gen i7-13700KF, 64GB RAM, MATLAB R2023b |

---

## 要点总结

1. ✅ 每个实验重复 **10 次**，报告 `Mean ± Std`
2. ❌ **未指定随机种子**，无法精确复现随机过程
3. 五折交叉验证评估准确率
4. 种群大小 20，迭代 100 次
5. KNN (k=3) 作为基分类器
