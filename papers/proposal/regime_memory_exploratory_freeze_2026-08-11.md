# 真实市场 lagged-regime volatility-memory 探索冻结（2026-08-11）

## 为什么做这个实验

Evaluator v2 在十个新 instruments 上只有 squared-return autocorrelation 通过，而且 return autocorrelation、
aggregation 与 volume coupling 的固定 band 大量出现时间 coverage failure。下一步不再调整 band，而是
检验一个更接近真实动力学的问题：**上一期的波动状态，能否预测下一期的 volatility-memory 强度？**

这是 evaluator 负结果之后提出的 hypothesis-selection experiment，所有可用 markets 都已用于设计，
因此结果只允许选择下一条预注册假设，不允许声称发现物理定律、写论文主 claim 或启动 EcoMD 训练。

## 数据与时间单位

使用两个已经 hash-bound 的免费 Yahoo 日频数据集，共 14 个 spent instruments。冻结前只查看 timestamp
coverage，不计算 return、volume 或 target statistic。每个非 2020 calendar half-year 需要至少 121 个
price rows，从中按时间取最早 121 行，构造恰好 120 个 log returns；剩余几天忽略，不跨半年拼接。

11 个 instruments 在全部 38 个非封存半年度都满足条件：GSPC、NDX、GLD、DJI、RUT、FTSE、DAX、
SPY、EEM、TLT、EWJ。EURUSD、HSI、N225 至少一个半年少于 120 returns，按 coverage-only 规则排除，
结果出来后不得替换。Volume secondary 只用真实交易产品 GLD、SPY、EEM、TLT、EWJ。

2020 继续完全封存。目标期与其 immediately previous half-year 配对：

- fit：2005H2--2014H2，共 19 个 calendar clusters；
- evaluation-1：2015H1--2019H2，共 10 个 clusters；
- evaluation-2：2021H2--2024H2，共 7 个 clusters；
- 2021H1 因 predecessor 是封存的 2020H2 而排除。

不同 instruments 共享宏观日历，统计推断单位是 17 个 evaluation half-years，不是 187 个
symbol-period cells。

## Predictor、targets 与模型

Previsible regime predictor 是前一个半年度 120-return block 的
`log(sqrt(mean(r^2)))`。每个 symbol 仅用 fit period 的 predictor median/IQR 标准化，evaluation 不重估。
这避免用 target block 本身的 volatility 定义 regime；若 fit IQR 非正或非有限则 fail closed。

Primary target 是 target half-year 的 mean ACF of squared returns at lags 1--20。该相关量对整块收益的
常数缩放不变，因此正 slope 不能由“高波动块只是数值更大”直接产生。Secondary 是五个 ETFs 的同期
volume--absolute-return correlation。Raw-return mean absolute ACF 只作 specificity diagnostic，不设方向或
通过门槛。

M0 用 fit 数据拟合 symbol fixed effects；M1 只多一个跨 symbol 共享的 lagged-regime slope。两者都是
OLS，evaluation 禁止 refit。Primary loss 是 MSE，MAE 作为 robustness。

## 相关性保护与 gate

Permutation null 有 999 个 replicates：在 fit、evaluation-1、evaluation-2 内分别置换 predictor 的
calendar labels，同一次 replicate 对所有 symbols 使用同一 calendar permutation，从而保留横截面共同
冲击；每次重新拟合 M1。P-value 是 `(1 + #null >= real)/(999 + 1)`。

另做 5,000 次 calendar-cluster bootstrap，每次把同一 half-year 的所有 symbols 一起重采样。Primary
只有同时满足以下条件才可 nominate：

1. fit common slope > 0；
2. pooled evaluation relative MSE reduction 至少 5%，且 MAE 改善为正；
3. 两个 evaluation eras 的 MSE 都改善；
4. 17 个 calendar clusters 至少 10 个改善，11 个 symbols 至少 7 个改善；
5. permutation p <= 0.05；
6. cluster-bootstrap 90% CI 下界 > 0。

任一条失败即 primary FAIL。Secondary/diagnostic 不能救回 primary，也不能单独成为论文结果。通过仅允许
冻结一个全新 macro-time 或 independent-data confirmation；失败则停止日频免费数据上的这条
lagged-regime memory claim。无论结果如何都不训练 EcoMD，不使用 GPU，不购买数据。

## 预先声明的局限

- 日频半年块只能测试慢状态依赖，无法辨认微观 liquidity mechanism；
- GSPC/SPY、NDX/DJI 等横截面高度相关，instrument 数不能当独立样本量；
- lagged volatility 是 state marker，不是外生干预，PASS 仍不证明因果；
- 这个实验由 evaluator failure 启发，所以必须永久标为 exploratory。
