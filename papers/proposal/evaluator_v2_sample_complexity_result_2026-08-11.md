# Evaluator v2.1 合成 sample-complexity 结果（2026-08-11）

## 结论

当前十个 eligibility estimators 都能在预注册的**强、已知 signal DGP**上，从某个 N 开始同时通过
signal power、matched-null specificity、100% finite 和 suffix-stability。Zumbach 继续只诊断。

这个结果证明代码不是“无论输入都失败”的坏测量仪器，并给出本组冻结 fixtures 下的 detectability
floors；它**不证明**真实市场效应具有同样强度，不证明 estimator 跨 regime 稳定，也不推翻四市场
feasibility-v1 的正式 FAIL。特别是多个 signal effect 很大，所有 metric 最终通过并不意外。

## 正式性

- artifact：`results/evaluator_v2/sample_complexity_v1.json`；
- clean HEAD/upstream：`3fe5a5eed4de7d118912f428b2836b45def6185e`；
- canonical payload SHA：`376eeca24355e0d5ce1eebc0cb4b67ebcf3962019da651aa5de7c8a48881a183`；
- file SHA：`d1f920f300711bf5118c34de0c4f787f0cd79c2700dd0ab1c2a74e899f9ca73a`；
- runtime：129.90 s；CPU-only，`gpu_used=false`；
- source feasibility result hash、protocol hash、DGP/estimator/runner hashes 全部绑定；artifact self-hash 已
  独立重算一致。

每个正式 cell 有 64 条独立 real paths，每条八个 controls；所有 reported minima 在该 N 及所有更长
grid N 上同时通过。signal/null path seed 包含 metric、N、condition 和 replication；control seed 另外
包含 surrogate type 与 control index，因此 signal、null 和 controls 不共享随机路径。

## Detectability floors

| Metric | 冻结 fixture 下最小 N | signal 方向比例 | signal effect（IQR） | null effect（IQR） | 与真实数据结果的关系 |
|---|---:|---:|---:|---:|---|
| autocorr_returns | 120 | equivalence | +0.082 | +0.031 | 只做 near-white sanity check |
| acf_squared_returns | 120 | 0.859 | +1.589 | +0.035 | 短块可测；真实 6/8 cells 通过，优先新市场确认 |
| aggregational_gaussianity | 180 | 0.953 | +5.210 | -0.142 | 解释 L120 非有限；不能再给它 L120 gate |
| conditional_kurtosis | 240 | 1.000 | +3.593 | -0.157 | 工具有 power，但真实 coverage 仅 3/8，属于 regime 问题 |
| dfa_hurst_abs_r | 500 | 0.828 | +0.888 | -0.077 | N240 signal gate 失败；短块 DFA 不可用 |
| gain_loss_asymmetry | 240 | 1.000 | -1.604 | -0.054 | 能识别强负跳跃，但真实弱/不稳定 skew 仍不合格 |
| hill_tail_index | 500 | 1.000 | -2.135 | +0.043 | 短块 Hill 不再使用；N500 只获得新市场检验资格 |
| intermittency_fano | 2000 | 1.000 | +4.125 | 0.000 | N<2000 event count/power 不足；现实数据需求过高 |
| leverage_effect | 500 | 0.828 | -0.804 | -0.044 | N120/180/240 都未过 signal gate；真实 L120 偶然通过不能降 floor |
| volume_volatility_corr | 120 | 1.000 | +5.524 | -0.107 | 短块强候选；需要 fresh instruments 的真实 coverage |
| zumbach_asymmetry | 无 | 不判定 | 不判定 | null 均通过（N≥180） | 继续 diagnostic only |

所有 minima 的 signal/null complete fraction 都是 1.0。Fano 在 N120/180/240 的 complete fraction
分别只有 0.641/0.188/0.969，N500 虽 finite 但没有 signal power且 null IQR 退化；N1000 有 power但低于
冻结的 expected-extreme floor。DFA 在 N240 方向比例仅 0.563、effect 0.143；leverage 在 N120/180/240
方向比例 0.719/0.641/0.719，均低于 0.80。

## Reviewer-2 审计：为什么“十个都通过”不是市场成功

1. **DGP 是刻意强 signal。** Student-t3、3%×-6 jump、t5-GARCH、GJR 和直接 `V=|r|+noise` 都是
   estimator unit tests。aggregation、conditional-kurtosis、volume 的最小-N effect 已达 3.6--5.5 IQR；
   这不是 realistic effect-size calibration。
2. **每项只有一个 signal/null family。** 结果证明 targeted sensitivity/specificity，不证明对 stochastic
   volatility、jumps、trends、structural breaks、microstructure 或错误 observable 都稳健。
3. **floor 是本 fixture 的乐观 detectability floor。** 它不是通用 sample-complexity theorem，也不是
   “N 到了就能测真实市场”的保证；真实 effect 更弱时需要更多数据或直接不可识别。
4. **真实 negative 仍是 binding evidence。** gain/loss、conditional、Hill 等在合成 strong signal 上通过，
   反而说明 feasibility-v1 的失败不能简单归咎于代码完全没 power；主要问题是 effect 弱、regime 漂移、
   短样本和不适合的静态 band。

## 对新市场数据需求的约束

若继续使用每个 split 内 non-overlapping blocks 和 alpha=0.2 split conformal，calibration 至少要四个
blocks；若 reference、calibration、confirmation、temporal 各至少四块，则单市场大约需要 `16N` 个
交易日：

- N=120：1,920 日，约 7.6 年；
- N=180：2,880 日，约 11.4 年；
- N=240：3,840 日，约 15.2 年；
- N=500：8,000 日，约 31.7 年；
- N=2000：32,000 日，约 127 年。

因此免费 fresh-market confirmatory 的近程 P0 是 acf-squared、volume coupling 与 N≥180 aggregation；
conditional/skew 可在 N≥240 继续 falsification，但不预设能形成 universal band。Hill/DFA/leverage 的
N=500 需要三十年以上指数历史；Fano N=2000 在逐市场 non-overlap 设计下现实上不可行，应退出近期
确认集，除非先冻结一个新的跨市场层级 estimand。不能通过 overlapping windows 伪造独立样本量。

下一步必须先按**只看 coverage/schema、不看 metric**的规则冻结全新 instrument universe 和自动
eligibility，再获取免费数据。当前 SPX/NDX/GLD/EURUSD 的 2015--2024 仍只能作 exploratory evidence。
