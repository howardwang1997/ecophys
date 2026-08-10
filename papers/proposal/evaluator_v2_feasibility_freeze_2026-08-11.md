# Evaluator v2 免费可行性协议（2026-08-11，任何新数据/指标输出前冻结）

## 1. 目的与不可越界事项

本实验只判断 EcoMD 下一版评价器中的 estimator 是否能在真实数据上自洽。它不重新评分 EcoMD v1，
不更改 M1 的正式 FAIL，也不产生市场物理或模型成功证据。

已经看过的 v1 calibration/held-out 输出不得用于选阈值、block length、metric scope、surrogate 或通过
规则。2020 crash split 继续 sealed。只有真实市场 reference/calibration split 能形成 interval；模型
输出永远不能定义“真实”的 acceptance region。

## 2. 为什么不能直接修 canonical bands

旧 bands 没有数据集、频率、样本长度和 coverage provenance，且至少 gain/loss 的 band 与当前 skewness
estimand 不一致。结果后把 `[-30,-3]` 换成能接纳 v1 的范围会构成明确 leakage。

Evaluator v2 因此从 estimator contract 开始：逐项固定 estimand、单位、适用市场和能杀死它的
surrogate。只有在真实数据的独立时间段 self-cover，并对相关 surrogate 有预期响应的 estimator，才
可能进入未来模型评价器。

## 3. 免费数据与时间隔离

从 Yahoo Finance 重新获取 `^GSPC`、`^NDX`、`GLD`、`EURUSD=X` 的 2005--2024 daily OHLCV；原始
文件只保存在内部临时目录，不提交、不公开再分发。时间角色固定为：

- 2005--2009：reference center；
- 2010--2014：conformal radius；
- 2015--2018：独立 confirmation；
- 2019：report-only guard；
- 2020：sealed crash，不读取；
- 2021--2024：temporal test。

所有 return blocks 都在单一 symbol/split 内按时间顺序形成，不跨边界。`L={120,240}` 是 primary；
`L=500` 只诊断数据量是否足够。丢弃每个 split 末尾不足一个 block 的 remainder，不能拼接。

## 4. Self-coverage

每个 symbol/fact/L 独立处理。center 是 reference blocks 的 median；calibration nonconformity 是到该
median 的绝对距离。使用有限样本 split-conformal order statistic：

`k = ceil((n_cal + 1) * 0.8)`。

若 `k > n_cal`，该 cell 是 insufficient，不用 infinity 假装可评价。confirmation 和 temporal test
coverage 都必须至少 0.75；两者缺一不可。这个门只判断 interval 的时间外可用性，不代表 universality。

## 5. Surrogate falsification

仅在 2005--2014 development 数据上，每个 real block 生成八个固定 seed replicates：

1. joint temporal permutation：保留 return/volume 边际和同步配对，破坏时间结构；
2. sign randomization：保留绝对收益与波动路径，破坏 skew/leverage sign；
3. volume circular shift：只破坏 contemporaneous volume alignment；
4. moment-matched Gaussian iid：破坏厚尾与时间结构。

每个 metric 的 primary surrogate、方向和市场 scope 已写入 YAML。例如 Hill 必须低于 Gaussian control；
squared-return ACF 和 DFA 必须高于 temporal permutation；leverage 只在两个 equity indices 上要求比
sign-randomized 更负；daily Zumbach 仅报告，不能决定 eligibility。

方向 cell 至少 75% paired blocks 同方向，且 median effect 至少 0.5 pooled-IQR units；equivalence cell
的绝对 effect 不得超过 0.5。all-symbol metric 至少三种市场合格，equity-only metric 两个指数都合格，
并且 L=120 与 240 都必须通过。

## 6. 停止规则

- acquisition/schema/hash 失败：不运行 estimator；
- block 数不足：报告 insufficient，先扩展免费历史/市场，不能降低规则；
- 真实数据不能 self-cover：停止构造 band，修 estimand 或明确 regime conditioning；
- surrogate 不响应：该 metric 不能进入 future confirmatory evaluator；
- feasibility PASS 最多允许写 evaluator-v2 specification，不允许恢复 v1 或启动 GPU production。

本阶段 CPU-only、零付费数据、禁止 GPU。只有数据 manifest 先提交、实现与 source hash 再提交以后，
才能产生第一份 feasibility 输出。

## 7. 实现绑定澄清（数据 manifest 之后、任何指标输出之前）

这一步不改变 metric、阈值、市场、时期或 block length，只消除第 5 节尚未写成机器语义的歧义：每个
paired effect 定义为“real block estimate 减去该 block 八个 surrogate estimate 的 median”；标准化分母
是所有 real estimates 与所有 surrogate replicate estimates 合并后的 NumPy-linear IQR。方向相等不算
同方向，IQR 非正时 fail closed。original-finiteness gate 只使用 reference、conformal calibration、
confirmation 和 temporal test；2019 仍只报告。volume metric 作为跨市场指标至少需要三个合格市场。

这些字段在查看任何价格、return 或 stylized-fact estimate 前写入 YAML 和测试；获取阶段只查看了清单的
文件数、行数、时间边界、重复数和 hash。
