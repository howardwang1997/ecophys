# Evaluator v2 新市场短块确认结果（2026-08-11）

## 结论

预注册的四项 core suite **FAIL**，因此 evaluator v2 不能用于 EcoMD v2 的模型评分或训练选择。
十个未参与设计的 instruments 中，只有 squared-return autocorrelation 达到市场数门槛，而且恰好是
最低要求的 6/10。return autocorrelation、aggregational Gaussianity 和 ETF volume--volatility coupling
分别只有 1/10、1/10 和 2/4 个 instruments 在所有预注册 N 上通过。

这个结果不是缺数据、代码产生 NaN 或 GPU 运行不稳定造成的。所有 symbol/N 都通过四个 non-overlapping
blocks 的前置门槛，所有 primary original/control estimates 都是有限值；失败来自预先固定的跨时间
conformal coverage 和 surrogate 区分门槛。不能通过删市场、删 N、降低 coverage 或改变 surrogate
阈值把结果改成 PASS。

## 正式性与 provenance

- artifact：`results/evaluator_v2/fresh_market_confirmation_v1.json`；
- clean HEAD/upstream：`31cddbfbeb9abe3c82805c1363137fad4deb6e3a`；
- canonical payload SHA：`8a946a32e6c77d784063e1f044f3bd2253b4bbf2cac9bf811cfd09cbda2654ac`；
- file SHA：`20871116e69dcce9249891658a0d4c70561fa9fdfeff9df3a8b99b328390d7be`；
- manifest canonical/file SHA：`e738e53e7ae74205f5d85fe16c070188bfa7d809df8420d2bf95391b8cd0ce0d` /
  `1e0393f8f803c104e0326225ebdee7c9443bcdf38132a2a0ff23ba1d82314cf0`；
- protocol SHA：`053ff907536d482ba72d368381e28381926421a031a547b493ebd59961997d85`；
- artifact 内部计时 8.18 s；CPU-only，`gpu_used=false`；
- 2020 sealed split 没有被加载或解析；正式输出的 self-hash 已独立重算一致。

该实验是 instrument holdout，但沿用 2005--2024 的共同 calendar splits。不同 instruments 同时经历
相同宏观冲击，所以它们不是十个独立的时间重复；即使结果通过，也不能推出 time-independent
universality。

## 预注册决策

一个 instrument 只有在该 metric 的**所有**预注册 N 上都通过，才计入 eligible-symbol 数。因此
cell pass 数不能替代 instrument-level 决策。

| Metric | Role | 通过 cells | 合格 instruments | 门槛 | 决策 |
|---|---|---:|---|---:|---|
| acf_squared_returns | core | 15/20 | DJI, RUT, N225, GDAXI, SPY, EWJ | 6/10 | PASS |
| aggregational_gaussianity | core | 6/20 | HSI | 6/10 | FAIL |
| autocorr_returns | required sanity | 8/20 | RUT | 6/10 | FAIL |
| volume_volatility_corr | core | 6/8 | EEM, EWJ | 3/4 | FAIL |
| conditional_kurtosis | secondary | 2/10 | EEM, EWJ | 6/10 | FAIL |
| gain_loss_asymmetry | secondary | 1/6 | GDAXI | 4/6 | FAIL |
| zumbach_asymmetry | diagnostic | 20 finite cells | 不作 eligibility 决策 | -- | diagnostic |

四项 core 中只有 acf-squared 通过，所以 `core_suite_qualified=false`，并且
`model_scoring_or_training_authorized=false`。Secondary metrics 不能补救 core failure。

## 失败来源审计

下表把失败 cell 互斥地分成 coverage-only、surrogate-only 和两者同时失败。所有非有限值计数均为 0。

| Metric | PASS | coverage-only | surrogate-only | both fail |
|---|---:|---:|---:|---:|
| acf_squared_returns | 15 | 3 | 2 | 0 |
| aggregational_gaussianity | 6 | 4 | 7 | 3 |
| autocorr_returns | 8 | 8 | 2 | 2 |
| volume_volatility_corr | 6 | 2 | 0 | 0 |
| conditional_kurtosis | 2 | 5 | 2 | 1 |
| gain_loss_asymmetry | 1 | 0 | 4 | 1 |

具体地，SPY 和 TLT 的 volume coupling 都只在 N120 coverage 失败、N240 通过；因此 6/8 cells 看似
接近，但按冻结的 all-N instrument rule 只有 EEM/EWJ 合格。acf-squared 的五个失败 cells 则分成
EEM/FTSE/HSI 的单一 N coverage failure 与 TLT 的两个 surrogate failures。它是目前最可信的短块
动态候选，但恰好卡在 6-instrument 门槛，不能称为 universal law。

aggregation 的失败同时来自时间 coverage 和 surrogate specificity；autocorr sanity 主要因时间
coverage 失败。conditional kurtosis 和 gain/loss skewness 的 secondary 结果进一步反对用固定、
per-symbol 静态 band 描述所有 regime，而不是支持继续调 band。

## 科学解释与停止规则

1. **保留的事实只有波动率记忆候选。** acf-squared 在新 instruments 上最稳定，值得进入下一阶段的
   regime-conditioned empirical analysis；它现在还不是跨时间、跨市场的普适定律。
2. **静态短块 evaluator 路线停止。** 一套 per-symbol fixed conformal band 无法同时稳定覆盖
   near-white returns、aggregation 和 volume coupling。继续改窗口或阈值会成为 post-hoc fitting。
3. **不把 evaluator failure 写成高影响论文。** 它是严谨的模型评估基础设施负结果，但没有独立
   macro-time holdout、机制或相对于已有 stylized-fact 文献的新物理定律，不能单独支撑高影响 claim。
4. **不启动 EcoMD v2。** 在真实市场 estimand 尚未稳定之前训练 simulator，只会让模型适配一个已经
   失败的测量合同。两张 V100 继续空闲。

下一步使用现有免费数据做**明确标注为 exploratory**的 regime-dependence 分解：检验 acf-squared、
volume coupling 和失败 coverage 是否随 volatility/liquidity regime 系统变化，并先冻结 estimand、
regime label、时间顺序和 surrogate。只有形成可证伪的 regime-conditioned law 后，才在新的时间段或
独立数据上预注册确认，再决定是否训练 EcoMD。当前十个 instruments 及原四市场均已用于设计，不能
再充当这一新 estimand 的最终确认集。
