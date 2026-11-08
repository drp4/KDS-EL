# E4 / E5 修改后复审（2026-11-08，第二轮）

## 结论与范围

当前仍有两个会阻止正式结果通过有效性检查的问题：E5 两处汇总读取了不存在的审计字段，DENCA 的 filter 请求未纳入审计计数等式。此外，E5 的有效数据报告仍有不依赖结果的跨分类器肯定性结论；LDA 的实际模型元数据没有持久化，是较低优先级的可追溯性缺口。

本轮仅审查当前工作区代码并在 scratch 中复现，没有修改生产实现，也没有写入正式实验输出目录。真实算法测试使用 60 个样本、6 个特征的合成二分类数据，N=20、每次运行 2000 次请求、一个随机种子、五个外折。该测试验证代码路径，不构成论文实证结果，也不能替代全部真实高维数据、所有种子与并行路径的正式运行。

## [P1] E5 审计字段读写不一致，正常完整运行也被判为无效

位置：code/run_experiment_e5.py:310–311、515；对应记录生产端为 225–228。

单次记录保存 audit.all_passed，但两处汇总读取顶层 audit_passed，并将缺失字段默认为 False。因此，无论单次审计是否通过，种子级 all_audits_passed 与全局 all_audits_passed 都会变成 False，最终 is_statistically_valid 和 valid_for_formal_claims 也无法为 True。这不是本轮测试数据质量问题，而是所有正常记录都能触发的字段契约错误。

复现：五种核心算法 × 五外折共 25 次真实合成数据运行全部完成，25 条记录的 audit.all_passed 均为 True；每种算法的 OOF 都覆盖全部样本、五折完整，但汇总的 all_audits_passed 和 valid_for_formal_claims 均为 False。

建议：两处统一读取生产端已有的嵌套审计字段，最好共用一个校验函数，并为“单次全通过、五折完整、全局有效”的正向路径增加回归断言。只改其中一处不足以恢复全局门禁。

## [P1] DENCA 预留最终请求后可返回，但 filter 请求仍导致审计恒不闭合

位置：code/algorithms_nested.py:1396、1419；审计等式在 code/nested_evaluator.py:575–583。

filter 搜索直接增加 candidate_eval_requests，而没有增加任何互斥请求分类计数。审计仍要求 candidate_eval_requests 等于 shortcut_eval_requests、cache_hit_count 和 cv_eval_calls 之和。新增的最终 wrapper 预留解决了预算耗尽异常，但没有解决 filter 请求的计数归属。

复现：默认 2000 预算下，DENCA 正常返回，candidate_eval_requests=2000，而三个分类计数之和仅为 1；1999 次 filter 请求未被计入等式，审计失败项为 9_requests_accounting_closed。修好 E5 的字段读取后，包含 DENCA 的全算法实验仍无法通过正式有效性检查。

建议：为 filter 目标评估增加明确的独立计数，并同步审计等式、记录字段和协议说明。不能为了让等式通过而把真正执行 filter 目标计算的请求重新冒充为 wrapper 快捷请求。

## [P2] 有效数据分支仍无条件宣称跨分类器表现一致

位置：code/run_experiment_e5.py:684–688。

空数据或无效数据的肯定性结论已被抑制，但有效数据分支只检查 KDS 结果存在，就固定输出 exhibit consistent generalization；实际 SVM / RF 指标的方向与幅度并未参与判断。

复现：向真实报告函数传入标记为有效的反例汇总，3-NN=0.95、SVM=0.10、RF=0.15，报告一边列出 -0.85 和 -0.80 的差值，一边仍宣称跨归纳偏好的一致泛化。这里的数值为专门构造的逻辑反例，不是实验测得性能。

建议：保留事实性指标陈述并根据实际结果描述取舍，不要仅凭流程完整就生成稳健迁移结论。跨分类器绝对准确率之间的比较也不能替代各分类器自身原始完整特征集的对照。

## [P3] LDA 新增模型元数据未被 E5 持久化

位置：code/run_experiment_e5.py:232–239；元数据生产端为 code/nested_evaluator.py:450–454。

BlindOuterEvaluator 已返回 model_variant，用以标明宽特征 SVD 与紧凑特征 shrinkage 路径，但 E5 重建 outer_metrics 时仅复制三个指标和 fallback_used，丢弃 model_variant。宽特征正常 SVD 与正常 shrinkage 的 fallback_used 都可能为 none，因此导出的分类器结果缺少直接的模型变体标签。现有维度和回退字段可辅助推断路径，该问题不改变预测或准确率，也不是本轮的运行阻断点。

建议：持久化 model_variant，并在模型回退后使其表示实际使用的模型；正式汇总同时提供各模型路径及回退的次数或比例，以便审查自适应分类器协议。

## 上轮主要问题已修复的验证

E4 七配置 × 五外折共 35 次真实合成数据运行全部完成并通过审计，全部使用 2000 次请求，全部持有 test_indices，顶层 valid_for_formal_claims=True。上一轮的指标导入、索引保存和 OOF 汇总故障链不再复现。零成功 KER 种子现在会纳入接受率：等尝试次数下，0 和 1 的接受率正确汇总为 0.5；单折结果也不会被判为正式有效。

bIRIME 使用相同随机种子、N=20、T=100 和同一个确定性替代目标，与仓库原实现前 2000 次候选掩码逐请求一致。该检查针对仓库内实现一致性，并未核验外部论文实现。

LDA 宽特征异常保护现在保持 SVD，不再回到 lsqr 的高维协方差路径。测试使用可记录构造参数的轻量 LDA 替身并注入一次失败，没有制造真实内存耗尽。E5 空结果报告也已正确抑制正式结论；剩余报告问题只针对有效数据分支的证据无关措辞。

## 复现材料

本目录 reproduce.py 为可执行回归脚本；results.json 保存机器可读结论；real_e4 和 real_e5 子目录保存真实合成数据运行产物；real_denca_record.json 为 DENCA 复现记录；adverse_report.md 和 empty_report.md 为报告函数的构造输入测试。所有这些产物都只能用于代码诊断。

从仓库根目录可运行 `python scratch/e4_e5_review_20261108_round2/reproduce.py`，建议先设置 PYTHONIOENCODING=utf-8。source_hashes.json 记录审查源文件 SHA256；脚本运行结束会校验这些生产文件未发生变化。
