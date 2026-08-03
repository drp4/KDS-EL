# KDS-EL 论文模拟同行评审报告 (Simulated Peer Review)

> 评审对象: `paper/sections/` 9 个章节 + `paper/abstract.md`（Phase 5 交付）
> 目标期刊: Applied Soft Computing (Elsevier)
> 评审日期: 2026-08-01 | 评审视角: 领域审稿人（进化计算 × 特征选择）
> 结论: **Major Revision**（无致命缺陷；5 条主要意见 + 5 条次要意见）

---

## 一、总体评价 (Summary)

论文以"通用 PSO 在高维特征选择上的三个结构性不适配"为主线，逐一引出三个互补机制（MI 引导初始化 / KER 知识引导精英精化 / 两阶段权重调度），在 MEL 多任务 PSO 骨架上做增量构建并消融验证。叙事问题驱动、数字口径统一（20-DS：0.9574 Acc / 88 特征）、统计检验规范（Friedman → Wilcoxon → Holm）、对天花板数据集与非最优数据集做了诚实讨论。方法新颖性主要来自 KER 的"零额外评估开销"设计与两阶段调度的"先粗后精"结构洞察。总体达到 ASOC 可送审水准，但存在若干需在修回阶段澄清/加强之处。

**已核实的质量保障（本轮 Phase 5/6 完成）**：
- ✅ 19 个 `\cite` 键全部可解析，无编造文献（全部 WebSearch 核实或来自 MEL [1]-[68] 保留块）
- ✅ 7 条 2023–2026 近年文献已补引（weil2025/chen2025/liang2025/xia2026/ye2026/liu2024/lin2025）
- ✅ 正文所有聚合数字与 `output/实验数据汇总.md` 一致；25-DS 数字已按用户决策全部清除（严格 20-DS only）
- ✅ 命名纪律（KER strategy、Two-Phase Weight Scheduling strategy、Component Contribution Analysis、complementary）统一
- ✅ 正文词数 ~8410，符合 8000–10000 预算；第 4 章略超（2025 vs 1700）由其余章节富余吸收

---

## 二、主要意见 (Major Concerns)

### M1. KER 的"知识"与 MEL 双群权重的关系需更明确（已修正）
审稿人会问：MEL 本身就有连续权重子群在学特征重要性，KER 的累积权重矩阵 W 与它有何本质区别？
- **回应**：已在 §4.3 补一句——W 是"改进反馈的信用分配累积器"（Pbest-improvement 驱动、指数衰减、仅供 KER 翻转使用），而 MEL 的权重群是"直接以 fitness 为目标的搜索表示"。二者角色不同。
- **待办**：审稿人可能仍追问 W 与 MEL 权重群的信息是否重复。建议修回时在 §7.1 消融处再点一句"MEL+MI→KER 的 +1.63pp 是在 MEL 已有权重群之上额外获得的"，强调增量。

### M2. 统计检验方向需与 Demsar 规程对齐（待验证）
- §5 P4 描述 Friedman → Wilcoxon → Holm；§6.3 称 Wilcoxon 为 *two-sided*。Demsar (2006) 对"方法 A 优于 B"的裁决推荐 **one-sided** Wilcoxon + Holm。
- **待办**：核对分析代码中 Wilcoxon 实际采用的方向；若为单边，将 §6.3 "two-sided" 改为 "one-sided (superiority)" 以与规程一致；若为双边，则在正文说明双边更保守并保持统一。

### M3. 参数敏感性聚合口径需与全局口径区分（已修正）
§8 的四数据集默认聚合（0.944 / 107 特征 / 51.3s）与 20-DS 全局（0.9574 / 88）不同，易让审稿人困惑。
- **回应**：已补一句"四数据集聚合是自洽基线，用于隔离单参数效应，不与 §6 的 20-DS 均值直接比较"。
- **待办**：无。

### M4. "adjusted p-value" 表述与极值报告（已修正）
§6.3 "combined p-values ranging from p<1e-15 to 1.02e-14" 措辞含糊，且极值过小。
- **回应**：已改为 "Holm-adjusted p-values"。
- **待办**：建议在表 T6b 中同时给 raw Wilcoxon p 与 Holm-adjusted p 两列，增强透明度。

### M5. 复现性声明缺失（待 Phase 7 补）
- **待办**：在 main.tex 正文末尾加 **Data availability / Code availability** 声明（ASOC 要求/鼓励）。如实写明：20 个数据集来源公开（UCI / 基因表达常用库），实验代码与超参配置随文提供或按要求提供。

---

## 三、次要意见 (Minor Concerns)

- **m1. 伪代码中的等式引用是脆弱占位**：Algorithm 1 注释 "Eqs. (4.5)-(4.6)"、"Eqs. (4.2)-(4.3)"、"Eq. (4.4)"、"Eq. (1)" 在组装后编号会变。→ Phase 7 统一改为 `\eqref{eq:...}`。
- **m2. §1 P3 阶段区间记号边界**："[0, 0.7T]" vs "(0.7T, T]" 与 §4.5 的 $t<\alpha T$ / $t\ge\alpha T$ 在边界处不完全一致（0.7T 归属）。→ 建议 §1 改用 "$[0,\,0.7T)$" 与 "$[0.7T,\,T]$" 对齐。
- **m3. §4 内部用字面 "Section 4.2 / 4.3 / 4.4 / 4.5"**：若章节编号稳定则可，但用 `\ref{sec:...}` 更稳妥。→ Phase 7 统一。
- **m4. §7 脚注（池化/DRS 变体已弃用）**：保留，符合大纲建议；但"DRS"未在前文出现，建议脚注里用一句话说明 DRS 全称（Dual Representation? 如实核对代码中的缩写）。
- **m5. W-MOPSO-FS 为自建基线**：正文已明确标注"self-built"，但建议在 §5 方法表 T1 中对其注明"（authors' implementation, no external baseline）"，避免审稿人按已发表算法检索。

---

## 四、需 Phase 7 完成的关键项（评审强依赖）

1. **图表/T 表全部落地**：T1/T2/T3/T4/T5/T6/T6b/T7/T8 + F1/F4/F5/F6/F7/F8/F9/F10/F11/F12/F13 + Algorithm 1；所有 `\ref{Fx}`/`\ref{Tx}` 标签必须存在（Phase 7 生成时定义）。
2. **等式 `\eqref` 统一**（见 m1）。
3. **Holm 表含 raw+adjusted 双列**（见 M4）。
4. **Data/Code availability 声明**（见 M5）。
5. **Highlights（ASOC 要求 3–5 条）** 与关键词。
6. **双盲版式**：移除作者信息，双栏/单栏按 ASOC 模板。

---

## 五、审稿结论

**Major Revision**。主要意见中 M1/M3/M4 已在正文就地修正；M2 需核对代码后定夺措辞；M5 与 Phase 7 组装项按清单落实即可送审。无数据矛盾、无编造文献、无过时口径，方法论与实验体量符合 ASOC 定位。
