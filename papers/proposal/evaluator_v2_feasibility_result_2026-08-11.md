# Evaluator v2 免费可行性结果（2026-08-11）

## 结论

冻结的 11-metric evaluator **不合格**。唯一满足跨市场、双 primary length、时间外 self-coverage 和
surrogate falsification 全部门槛的指标是 `autocorr_returns`；它只是“日收益近似无自相关”的 sanity
check，不能单独支持市场真实性、市场物理或 EcoMD v2。

因此不能用这套 evaluator 重新评分 EcoMD v1，也不能据此启动 EcoMD v2 GPU 训练。旧 canonical bands
继续停用；当前结果要求拆分“可定义性、时间稳定性、surrogate sensitivity”后逐项重建 estimator。

## 正式性与 provenance

- 唯一正式 artifact：`results/evaluator_v2/feasibility_v1.json`；
- 执行提交与 upstream：`c6c606485c2c4eec63528f3dc376dd6e7816ba0a`；
- artifact canonical payload SHA：`057946d365686cc4e63c13e8db3d547e83601560d701e3ac52e39f572438d25f`；
- artifact file SHA：`52814472321ae9dbc89b74b4eb73a0b5eac170b3d9fdb157d70699c506b1df02`；
- bound data manifest canonical SHA：`28560c599e9c63418732d34cee0ade29665e24eb75b5b5fc123435d0bc005666`；
- 运行时间 8.82 s；CPU-only，`gpu_used=false`；
- 2020 parquet 只做 raw-byte hash 验证，没有解析或用于任何 metric；
- artifact self-hash 已独立重算一致。第一次执行因 diagnostic relation dispatch bug 在写文件前停止；
  没有 artifact 或数值输出。execution-only 修复有回归测试，未改变 estimand 或 gate。

每个市场在 L=120/240 的 reference/calibration blocks 分别是 10/5，confirmation 与 temporal blocks
分别是 8/4。L=500 的 calibration 只有两个 blocks，有限样本 conformal 需要 `k=3`，所以按协议只能
诊断，不能评价 coverage。

## 逐项判定

| Metric | 合格市场 | primary cells 通过 | 主失败机制 | 决定 |
|---|---:|---:|---|---|
| autocorr_returns | SPX、GLD、EURUSD（3/4） | 6/8 | NDX L120 temporal coverage=0.625；L240 equivalence effect=0.587 IQR | 仅保留为 sanity check |
| acf_squared_returns | SPX、EURUSD（2/4） | 6/8 | GLD、NDX 的 L120 coverage 失败；surrogate 8/8 有效 | 候选，但不能形成 universal band |
| aggregational_gaussianity | 0/4 | 4/8 | L120 在四市场都只有一个有效 aggregation scale，因此非有限；L240 四市场全通过 | 只能在新协议中用解析上可容许的长度 |
| conditional_kurtosis | GLD（1/4） | 3/8 | surrogate 8/8 有效，但 5/8 cells 时间外 coverage 失败 | 明显 regime-dependent，不做静态 universal band |
| dfa_hurst_abs_r | 0/4 | 0/8 | L120 四市场不可定义；L240 四市场都未通过 permutation kill | 停用当前短块 DFA estimator |
| gain_loss_asymmetry | 0/2 | 0/4 | 3/4 coverage 失败且 4/4 sign-randomization effect 不足 | 停用 sample skewness 作为 gain/loss 指标 |
| hill_tail_index | 0/4 | 2/8 | 2 cells coverage 失败、4 cells surrogate 失败；无市场同时通过两长度 | 停用短块 Hill point estimate |
| intermittency_fano | 0/4 | 0/8 | 7/8 cells 出现非有限值；99% threshold 在 120/240 点 block 中事件数不足 | 当前定义失效，不能调低门槛补救 |
| leverage_effect | 0/2 | 2/4 | surrogate 4/4 有效；两指数 L120 通过、L240 confirmation coverage 都为 0.5 | 保留为 regime/length-conditioned 探索量 |
| volume_volatility_corr | NDX、GLD（2/3） | 5/6 | SPX L240 confirmation coverage=0.5；surrogate 6/6 有效 | 强候选，但尚未跨三市场稳定 |
| zumbach_asymmetry | diagnostic only | 不判定 | L120 不可定义；L240 有限但协议不允许 eligibility claim | 继续只诊断 |

失败计数允许重叠：一个 cell 可以同时 coverage 和 surrogate 失败。EURUSD volume 在所有 gating splits
为常数，因此按预注册 observable gate 不适用；SPX、NDX、GLD 适用。

## L=500 诊断告诉了什么

更长 block 消除了 aggregation、DFA、Fano 和 Zumbach 的纯可定义性问题，但没有给出可验证的
conformal coverage，因为每个 calibration split 只有两个 L=500 blocks。surrogate 在 L=500 对
acf-squared、conditional kurtosis、Hill、leverage、volume 全部适用市场有效；对 gain/loss skewness 和
Fano 则 0 个市场有效。由此：

1. 对 aggregation/DFA/Zumbach，下一步可以从 estimator 的解析最小样本量出发指定 metric-specific
   length，而不是强迫所有 metric 共用 L=120；
2. 对 L=500 coverage，必须扩展免费历史或采用新的、尚未看过的市场，不能把 `k=3` 改成 infinity；
3. gain/loss skewness 与 Fano 不是简单“多一点数据”就能恢复，需换 estimand 或删除；
4. Hill 在 L=500 的 surrogate 响应改善，但当前短块跨时期不稳定，不能据此事后升级为合格。

## 对主线的约束

- **模拟器主线继续停。** 现在没有足够可信的多事实 evaluator 来定义 EcoMD v2 的 realism loss 或
  confirmatory score；V100 production 不启动。
- **真实物理优先。** acf-squared、leverage、volume coupling 的 surrogate 响应真实存在，但 coverage
  明确随时期/长度变化。更有科学价值的问题是这种 regime dependence 本身，而不是把它压成 universal
  常数 band。
- **当前四市场的 2015--2024 已经用于本次正式判定。** 后续改 estimator 时，它们只能作 exploratory
  data；新的 confirmatory claim 必须先冻结，再用未看过的免费市场/更早历史或未来数据验证。
- **免费下一阶段。** 先做解析 sample-complexity audit，形成 metric-specific admissibility；再冻结一组
  新市场 holdout，验证 aggregation、volatility memory、leverage 与 volume coupling。Hill、skewness、
  Fano、短块 DFA 在重写 estimand 前不进入确认性实验。全阶段仍是 CPU-only、零付费、零 GPU。

这个结果本身是严谨的 evaluator negative，不足以独立成为高影响力论文 claim；它的价值是阻止再次用
无 provenance 的 11-fact score 训练或包装模型，并为真实市场 regime-dependent physics 选择测量工具。
