# Evaluator v2 fresh-market 短块确认冻结（2026-08-11）

## 问题与边界

合成校准只证明 estimator 对强 fixture 有 power。现在用**从未进入 evaluator-v2 设计的 instruments**确认
短块测量合同，但沿用 2005--2024 calendar splits。因此这是 instrument holdout，不是独立宏观时间
holdout；通过也不能声称 time-independent universality，更不能直接授权模型训练。

当前 SPX、NDX、GLD、EURUSD 已经花掉，不进入 universe。新 universe 在任何新数据/metric 输出前固定：

- equity indices：DJI、Russell 2000、Nikkei 225、FTSE 100、DAX、Hang Seng；
- 有真实成交量的 ETF：SPY、EEM、TLT、EWJ。

选择依据只有 instrument class、跨地区/资产暴露和预期公开历史，不看任何新 metric。实际 coverage 或
volume 不合格时由机器规则标记 ineligible，不临时换 symbol。

## 为什么只确认短块候选

合成 floor 与 per-market `16N` 数据需求使 N500 约需 32 年、Fano N2000 约需 127 年。当前 P0 只包含：

- near-white autocorrelation sanity，N=120/240；
- squared-return memory，N=120/240；
- aggregational Gaussianity，N=180/240；
- ETF volume--volatility coupling，N=120/240。

conditional kurtosis 与 gain/loss skewness 在 N240 作为 secondary falsification；Zumbach N180/240 只诊断。
Hill、DFA、leverage 和 Fano 不在本实验，不能因结果好坏补回。

## Gate

每个 symbol/split/N 必须先有至少四个 non-overlapping blocks。reference median 与 calibration absolute
deviation 构造 alpha=0.2 finite-sample conformal interval；confirmation 与 temporal coverage 都至少 0.75。
每个 development block 有八个 deterministic primary controls；方向比例至少 0.75、effect 至少 0.5
pooled-IQR，equivalence 的绝对 effect 不超过 0.5。任一 original/control 非有限则 cell 失败。

all-symbol metrics 至少六个 instruments 合格，ETF volume 至少三个，index skew 至少四个。metric 必须
通过它所有预注册 N。最小 core suite 要求 autocorr sanity、acf-squared、aggregation 和 volume 四项全部
合格；secondary 不能补救 core failure。

## Split 与 sealed data

沿用 reference 2005--09、calibration 2010--14、confirmation 2015--18、report-only 2019、sealed 2020、
temporal 2021--24。2020 只允许 raw-byte hash，不解析 metric。由于 calendar 与 feasibility-v1 相同，
跨 instrument 的共同危机暴露会降低有效独立性，结果文档必须显式报告这一点。

## 停止规则

- acquisition/schema/coverage 失败：按预注册规则标记，不换 symbol；
- core suite 任一项失败：停止短块 evaluator，不训练 EcoMD v2；
- 通过最多允许写 evaluator specification；仍需未来时间或付费/独立数据确认后才能成为模型 gate；
- CPU-only、免费数据、禁止 GPU，V100 保持空闲。
