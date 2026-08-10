# EcoMD v1 M1 结果与停止决定（2026-08-11）

## 结论

M1 的 stationarity 部分通过，但 frozen stationary window 内的市场统计 fidelity 不通过。按结果前冻结
规则，EcoMD v1 的正面 model-paper 路线停止，不启动多训练 seed、强基线、消融或跨市场 production。

这不是“模型已经稳定但差一点”的结果。初始化瞬态已被控制，而长期生成分布仍系统性缺少厚尾、
波动聚集、长期波动记忆、leverage 和 volume--volatility coupling。增加更多相同模型的 rollout 或 GPU
不能修复这种结构缺口。

同时，`2/11` 只能作为预注册 operational kill switch，不能直接写成经过验证的“市场真实性分数”。
结果后的 reviewer-2 audit 发现 generic canonical bands 没有记录经验来源，而且 gain/loss band 与当前
skewness 指标的量纲明显不一致。正式冻结判定保持 FAIL，但论文级科学解释必须依赖有真实数据
self-coverage、同长度和同频率校准的 estimator，而不能包装这组 bands。

## 1. 可复现执行链

- 唯一 checkpoint：iter 600，SHA-256
  `7822c030b44aa8e18110d807d7a4bfc15dea5ebd0175c5bd0fa2d2a10f96f34a`；
- calibration execution Git：`a18d70c1c78e7072b2780c776b12de71570aacf1`；
- result-blind gate fitter Git：`179da420a65b69d6a677aff850f2fb37a827c4d7`；
- frozen gate commit：`3f1303b0421411f25ccc9f44dab61c71cf552bdb`；gate 文件 SHA
  `17ad4f26c5f5ce5040aba028e70bda711de0306620070be96d22c63bbb14ae55`；
- held-out binding/analysis Git：`80a3d61a547f91d893f25376b9bbb98e612f467d`；binding 的首次加入
  commit 与 execution commit 相同；
- A/B held-out manifest SHA：`ebda817f03c961c86a2fc4b8e3a0d81eeb3740a6d905b7ead4ec41661d8b8f3c`
  和 `9641cd8dbaf08529c45690a8b17c7d61c3603a0d2eaa5f39751548661331fe07`；
- held-out return/volume matrix SHA：`d26441929af009750e808fe5bf10438af36adaad7e96c149f839ef4261e405e9`
  和 `3d16a2b7c772cf60cf6934f0b5e75e3ebd2523481b3f93f97e6d46c6c8c2476a`；
- 正式分析 artifact：`release/verification/80a3d61a5-m1-heldout.json`，SHA
  `2d046ce38f5a78f35c3be952e53d81110d01d9c74f1eb0f809becf6635973846`。

两台 V100 分别生成八条 calibration 和八条 held-out trajectory。held-out 只在 W-star 文件 commit/push
以后运行；32 条轨迹都严格为 8,000 returns、无 shock、无 inference override。所有服务 exit 0，GPU
回到 8 MiB/0%。

## 2. Stationarity 结果

Calibration energy gate 的 tolerance 为 `0.019507027186009607`。W=0 的 median distance 为
`0.020421648813179982`，从 W=500 起连续三块通过，因此 frozen W-star 是 500；ADF/KPSS comparator
选择 W-star 0。

在 16 条 held-out 上，frozen W-star 500 原样 transfer 成功。候选块的 held-out median distances 为：

`[0.0193000, 0.0137467, 0.0143787, 0.0119311, 0.0125517, 0.0124236, 0.0134079,
0.0126854, 0.0128711]`。

九块全部低于 calibration tolerance。这个结果说明当前 rollout 的小幅初始化分布漂移可以用
calibration-only gate 稳定控制；它不说明生成过程与真实市场同分布。

## 3. 冻结 fidelity 结果

| Window | 11-band pass | Mean normalized distance | 角色 |
|---:|---:|---:|---|
| 0 | 2/11 | 0.244691 | early，必须报告 |
| 500 | 2/11 | 0.243187 | frozen post W-star |
| 4000 | 2/11 | 0.252227 | late，必须报告 |

其余七个固定窗口也全部为 2/11；distance 范围是 0.2375--0.2468。late/post ratio 为 1.03717，低于
1.10，但 post 和 late 都触发 `<=2/11` 的硬停止条款。只有以下两项在所有主要窗口通过 generic band：

- absence of raw-return autocorrelation；
- conditional kurtosis。

W=500 的关键 median estimates 与精确 training target 的诊断对比如下。真实 target 只有 1,005 returns，
不是与模型 L=4000 严格同长度的正式检验；它用于判断差异方向和 evaluator 健康度。

| Fact | EcoMD held-out W=500 | SPX 2015--2018 | 解释 |
|---|---:|---:|---|
| Hill tail index | 6.738 | 3.518 | 模型尾部明显过薄 |
| ACF of squared returns | 0.0108 | 0.1151 | 波动聚集约低一个数量级 |
| DFA H of absolute returns | 0.586 | 0.853 | 缺少慢波动记忆 |
| leverage sum | +0.017 | -1.066 | 符号/强度均缺失 |
| volume--volatility corr | -0.0003 | 0.409 | 几乎无 coupling |
| raw-return mean absolute ACF | 0.0123 | 0.0310 | 两者都接近白噪声，属于通过项 |

这些 target-matched 缺口不依赖可疑的 gain/loss band，足以阻止“复现市场统计”的正面 claim。

## 4. Evaluator audit：为什么不能过度解释 2/11

`canonical_bands.py` 首次加入于 commit `2734ee9351293bd72c1afe73bd5af2ef7c0a1e7e`，该提交和文件没有
给出 bands 的数据集、频率、样本长度、bootstrap coverage 或文献来源。更直接的问题是：

- `gain_loss_asymmetry` 自 commit `e7c282c2d2096979dc878eac2501863d173df234` 起返回 sample skewness；
- frozen band 却是 `[-30,-3]`；
- 精确 SPX train、2019 和 2021--2024 的 skewness 分别为 -0.495、-0.640 和 -0.266，全部被该 band
  排除。

同一 sanity check 中，三个真实 SPX split 都只通过 5/11 generic bands。2019 只有 251 returns，所有
split 都短于模型 L=4000，因此这些数字不能取代严格的 matched-length reference distribution；但它们
足以证明 generic band pass count 不是自验证的 realism metric。完整无原始价格值的诊断记录为
`release/verification/80a3d61a5-m1-target-sanity.json`。sealed 2020 未打开。

因此保留两层结论：

1. **协议结论：** frozen M1 tier 是 `stop_positive_model_paper`，不得结果后改 bands 救回 v1；
2. **科学结论：** 当前模型确实缺少多个 target-matched 核心动力学，但 `2/11` 本身不能进入论文标题、
   摘要或 realism claim。

## 5. 现在停止什么

- 不跑 EcoMD v1 的额外 training seeds、baselines、ablations 或 cross-market sweep；
- 不为 v1 购买数据或扩容 GPU；
- 不发布该 checkpoint 为 validated market simulator；
- 不把 stationarity transfer 写成真实市场物理；
- 不把 evaluator 的 band 缺陷包装成模拟器误差论文。

source research preview 仍可发布，但必须明确写“mechanically verified, empirically unvalidated”，并公开
这次失败记录。

## 6. 下一条可发表主线

先做真实市场物理，再让模拟器承担机制检验：

1. **修 evaluator，不看当前 held-out 调阈值。** 给 11 个 estimator 写清 estimand、单位、频率和样本
   长度；用 training-only real blocks 建立 matched-length reference distribution 和 bootstrap coverage；
   用独立时间/市场验证 self-coverage。2020 继续 sealed。
2. **把真实事实变成模型约束。** 优先修复厚尾、慢波动状态、return--future-volatility 非对称和可观测
   flow/volume coupling。不能只注入外生 heavy-tail noise；每个机制要有真实数据依据和消融可证伪性。
3. **新版本从新协议开始。** EcoMD v2 使用新 checkpoint、全新 calibration/held-out seeds 和独立时间/
   市场 test；当前 32 条 M1 输出只能做 development diagnostic，不能再次充当确认性 held-out。
4. **影响力路线以 empirical law 为主。** 在至少三类市场、多个尺度上先证明一个预注册、surrogate-
   resistant 的真实物理规律；EcoMD 只在真实规律成立后用于区分机制和反事实。没有这一步，不回到
   Nature Physics/NCS 叙事。

在 evaluator v2 和模型机制 v2 都有结果前，不再排 V100 production。CPU 上可以继续做免费的
real-data estimator audit、matched-length bootstrap 和 falsification design。
