# NCS G0 新颖性审计：不变测度校准与长时程梯度

**审计日期：** 2026-08-09  
**状态：** **FAIL；当前 NCS 不变测度校准方法主线停止**
**适用计划：** `papers/proposal/plan_v4_ncs.md`  
**资源约束：** 当前阶段不采购数据、不扩容、不得使用 H20

**2026-08-10 最终更新：** exp131 已通过 E1 的已知 baseline/harness 门槛，但没有 candidate
estimator；exp132 的 v1 mixing diagnostic 因 easy resolved rate `78.125% < 80%` 按预注册判 FAIL。
`ncs_candidate_estimator_spec_v0.md` 已写出目标、混合梯度、随机 horizon、staleness bound 和误差账本，
但逐项红队结论是直接组合 PCD、pathwise/LR、Rhee--Glynn 与 StochasticAD/GGE；没有新的 stochastic
identity、coupling、residual theorem 或 variance result。v0 非等价性 FAIL，禁止命名和启动 E0--E3
candidate benchmark。随后完成的 33 篇一手文献 forward audit 发现：SOUL 已覆盖参数变化时的
warm-started Markov kernel，Jarzynski/JALA/SOSMC 已覆盖跨参数的加权粒子复用，2025 PCD 工作已给出
耦合参数--采样动力学的 uniform-in-time error，而经验 mixing diagnostics 不能在未知混合常数下提供
有限预算证书。三个 v1 出口均不成立，故 G0 正式 **FAIL**。完整证据与绑定决定见
`ncs_g0_forward_audit_2026-08-10.md`。

## 1. Gate 结论

下列说法均不能作为论文的新颖性 claim：

- 首次对随机模拟器的不变测度或稳态统计量求梯度；
- 首次在训练中持久化 Markov chain / simulator state；
- 首次对含离散随机事件或 jump 的模拟器做自动微分；
- 首次以常数内存或 adjoint 方式训练长时程 SDE；
- 首次用 simulation-based inference、surrogate 或分布距离校准 agent-based simulator；
- “state-complete rollout”“训练/推理动力学一致”或“自动选择 burn-in”本身。

这些方向已有直接先行工作。当前唯一可继续检验的候选贡献是一个更窄的组合问题：

> 对具有高维连续隐状态、离散 jump、随参数更新而滞后的 persistent ensemble，以及未知且可能很慢
> 的 mixing time 的可微模拟器，构造一个会在误差不可控时显式拒绝输出的、预算自适应的不变测度
> 梯度估计与校准协议；同时给出有限 ensemble、有限 horizon、state-bank staleness 和离散事件项的
> 可分解误差诊断。

这仍只是 **candidate estimator**，不是已经成立的方法贡献。它可以被 PCD、Rhee--Glynn
telescoping、已有 steady-state likelihood-ratio/pathwise estimator、StochasticAD 或 generator gradient
estimator 的直接拼装；forward audit 又排除了 v1 的三个候选出口，因此 G0 已判失败。

## 2. 主文献 claim matrix

| 文献簇 | 已有结果 | 对本项目的直接约束 | 当前未被证明的窄缺口 |
|---|---|---|---|
| Steady-state Markov sensitivity | Glynn--Olvera-Cravioto 对一般状态空间、几何遍历离散 Markov chain 给出稳态 expectation 的 likelihood-ratio 梯度及极限分析；Wang--Plecháč 给出 CTMC centered LR 与 Poisson-equation 方差分析 | 不能 claim “首次稳态梯度”或“首次处理慢 mixing” | 神经高维 simulator 中是否存在更好的等预算 Pareto 点尚需实证 |
| Invariant-measure diffusion sensitivity | Assaraf et al. 直接研究参数化 diffusion 的 invariant-measure average derivative，并分析长时程 tangent process | persistent pathwise derivative 和 invariant-average 目标均非新概念 | 非可逆、混合连续/离散、高维 learned simulator 的可诊断有限预算版本 |
| Persistent chains | Tieleman 的 PCD 以持续链近似模型分布；后续工作已讨论 chain lag、learning-rate 与 mixing 的偏差/稳定性 | “跨 batch 保存状态”不是算法创新 | 是否能给 state-bank staleness 一个可计算、可证伪的误差量 |
| Debiased equilibrium expectation | Glynn--Rhee 用随机 telescoping/coupling 构造 Markov equilibrium expectation 的无偏估计；unbiased MCMC 文献扩展 coupling 实现 | “随机化 horizon 消除初始化偏差”不是新颖性 | 在 learned simulator 参数持续变化时，coupling 成本是否可接受 |
| SDE adjoint / scalable gradient | Li et al. 给出 constant-memory stochastic adjoint；Wang--Blanchet--Glynn 的 generator gradient estimator 对高维参数保持近似常数计算时间，并明确覆盖带 jump 的一般 SDE | 不能 claim “首个 scalable SDE gradient”或“首个 jump gradient” | 目标为不变分布距离、状态库滞后且带 observation operator 时的端到端校准 |
| Discrete stochastic AD | Arya et al. 给出离散随机程序的无偏自动微分，并展示 Markov chain、ABM 和 particle filter | 不能把 Poisson jump 的可微处理写成首创 | 与连续 pathwise 项、mixing diagnostics 和大粒子系统的预算配平 |
| Long-horizon differentiable simulation | DiffTaichi、stochastic adjoint 和 differentiable-control 文献已系统讨论反向传播、内存与长时程梯度失效；Suh et al. 明确分析 stiffness/discontinuity 下的一阶估计偏差--方差 | “长 rollout 可微”与“checkpoint 降内存”不构成新意 | 校准 invariant statistics 而非 finite-horizon control 时，可否给 fail-visible certificate |
| Simulator / ABM calibration | kernel、surrogate、SBI、data-assimilation 和 differentiable-ABM 文献均已覆盖隐参数与部分隐状态校准 | 不能仅以 EcoMD+真实数据作为通用方法证明 | EcoMD 外至少两个模型族的相同预算对照与真实 observation bridge |

## 3. 本轮核验的锚点文献

以下只列用于决定 claim 边界的主文献或正式会议页面；后续系统综述仍需沿引用网络补齐。

1. Glynn, P. W. and Olvera-Cravioto, M. (2019),
   [Likelihood Ratio Gradient Estimation for Steady-State Parameters](https://doi.org/10.1287/stsy.2018.0023),
   *Stochastic Systems* 9(2), 83--100.
2. Wang, T. and Plecháč, P. (2019),
   [Steady-State Sensitivity Analysis of Continuous Time Markov Chains](https://doi.org/10.1137/18M119402X),
   *SIAM Journal on Numerical Analysis* 57(1), 192--217.
3. Assaraf, R., Jourdain, B., Lelièvre, T. and Roux, R.,
   [Computation of sensitivities for the invariant measure of a parameter dependent diffusion](https://arxiv.org/abs/1509.01348).
4. Tieleman, T. (2008),
   [Training Restricted Boltzmann Machines Using Approximations to the Likelihood Gradient](https://doi.org/10.1145/1390156.1390290),
   ICML 2008, 1064--1071.
5. Glynn, P. W. and Rhee, C.-H. (2014),
   [Exact Estimation for Markov Chain Equilibrium Expectations](https://doi.org/10.1239/jap/1417528487),
   *Journal of Applied Probability* 51A, 377--389.
6. Jacob, P. E., O'Leary, J. and Atchadé, Y. F.,
   [Unbiased Markov chain Monte Carlo with couplings](https://arxiv.org/abs/1708.03625).
7. Li, X., Wong, T.-K. L., Chen, R. T. Q. and Duvenaud, D. (2020),
   [Scalable Gradients for Stochastic Differential Equations](https://proceedings.mlr.press/v108/li20i.html),
   AISTATS 2020.
8. Arya, G., Schauer, M., Schäfer, F. and Rackauckas, C. (2022),
   [Automatic Differentiation of Programs with Discrete Randomness](https://proceedings.neurips.cc/paper_files/paper/2022/hash/43d8e5fc816c692f342493331d5e98fc-Abstract-Conference.html),
   NeurIPS 2022.
9. Wang, S., Blanchet, J. and Glynn, P. (2024),
   [An Efficient High-dimensional Gradient Estimator for Stochastic Differential Equations](https://proceedings.neurips.cc/paper_files/paper/2024/hash/a0cd56b91305239e2580dd9440b2e155-Abstract-Conference.html),
   NeurIPS 2024. 该工作明确包含一般 jump SDE。
10. Suh, H. J. T., Simchowitz, M., Zhang, K. and Tedrake, R.,
    [Do Differentiable Simulators Give Better Policy Gradients?](https://arxiv.org/abs/2202.00817).

## 4. Candidate estimator：已冻结的失败规格

完整数学规格与非等价表见 `ncs_candidate_estimator_spec_v0.md`。该 v0 已在编码前判定为直接组合；
本节只保留为失败记录和已知 baseline 接口，不再授权当前分支实现 v1 或启动 candidate benchmark。

本阶段不命名算法。实现必须拆成四个可独立消融的模块：

1. **State-complete ensemble。** 每条 chain 保存完整 simulator state、绝对时钟、RNG 和参数版本；
   缺任一项时实验 hard fail。
2. **Mixing diagnostic。** 用 integrated autocorrelation time、split-chain discrepancy 与 coupling
   distance 中至少两项估计有效 horizon；诊断不一致时返回 `unresolved`。
3. **Randomized multilevel correction。** 在受控系统上以随机 truncation / coupling correction
   估计 finite-horizon bias；必须与标准 Rhee--Glynn estimator 做同预算比较。
4. **Hybrid event gradient。** 连续状态参数使用 pathwise/tangent 项；离散 jump-rate 参数以
   StochasticAD、likelihood-ratio 或 generator estimator 之一作为已知基线。若没有新的耦合或
   方差缩减结果，不得把 hybrid 本身列为贡献。

输出不能只是一个 gradient tensor；必须同时给出：simulator steps、wall time、peak memory、gradient
variance/ESS、mixing diagnostic、估计的 truncation residual，以及是否拒绝输出。

## 5. 零成本可行性实验与预注册阈值

### E0：可解 OU / AR(1)

- 真值：stationary mean、variance 及其参数梯度解析可得；
- regimes：fast / medium / slow mixing，各至少 32 个 Monte Carlo seeds；
- baselines：fresh short BPTT、persistent truncated BPTT、long BPTT、finite difference；
- 通过：candidate 在至少 medium/slow 两档上，相同 simulator-step 预算下 gradient RMSE 下降
  `>=25%`，并且 90% interval coverage 不低于 `85%`；fast mixing 不得严重退化（RMSE 不超过最强
  baseline 的 `1.10x`）。

### E1：两状态 chain 与 compound-Poisson OU

- 两状态 chain 提供离散 transition-rate 的精确 stationary gradient；jump-OU 提供连续状态和
  jump-rate 的有限差分高精度 reference；
- 通过：`create_graph=True/False` 前向分布 parity 先成立；再要求 jump-rate gradient 的相对偏差
  `<10%` 或可信区间覆盖 reference；
- 若只能对 state pathwise parameter 求导而不能对 jump rate 求导，必须缩小 claim。

### E2：双稳态慢混合系统

- 不把单条 trajectory 的稳定 loss 当作正确性；以高预算 reference 和 mode occupancy 为真值；
- 通过：candidate 能在诊断未混合时拒绝输出，且 false-safe rate `<5%`；在可解决预算内，gradient
  sign accuracy `>=90%`；
- 如果 persistent chain 看似低方差但停在单一 mode，判失败。

### E3：可扩展性 microbenchmark

- 参数维度和状态维度分别扩展，报告 wall time、steps/s、peak RAM/VRAM；
- 与 NeurIPS 2024 generator-gradient 的公开实现或忠实复现比较；
- candidate 若没有准确度--成本 Pareto 改善，不进入 EcoMD 正式训练。

所有阈值在查看 candidate 结果前冻结。E0--E2 可在 CPU 完成；E3 最多使用空闲 V100 做短 probe，
不启动多卡生产任务。

### E1/E2 baseline 执行结论（2026-08-10）

- exp131 在两状态 chain 与 compound-Poisson AR/OU 上通过公式、前向/RNG parity 和已知基线门槛。
  慢 jump cell 的 coupled finite difference 相对偏差为 `+5.64%`、90% coverage 为 `92.19%`；
  persistent-detached LR 为 `-31.63%`。这确认问题与 controls，不是方法改进。
- exp132 在 hard regime 将 64/64 batch 全部判为 unresolved，false-safe 为零；但 easy regime 只
  resolve 50/64 batch，即 `78.125%`，低于冻结的 `80%`。v1 overall FAIL，阈值不后改。
- 当前仍没有 candidate estimator，E3 的 candidate-vs-GGE Pareto benchmark 因而没有科学比较对象。
  数学 spec 已完成但非等价性失败；下一步若继续，必须先提出可写成 theorem 或 estimator identity
  的不可约 primitive，而不是继续累计 baseline smoke。

## 6. G0 的最终判定

当前判定为 **FAIL**，理由是必要的非等价性条件已失败：

- 33 篇一手文献 backward/forward audit 已覆盖 2024--2026 最近邻；
- v0 数学式可以被完整复述为 PCD + hybrid pathwise/LR + Rhee--Glynn + diagnostics；
- v1 的 cross-parameter coupling、weaker-assumption residual 和 variance--cost 三个出口均无新定理或
  estimator identity；
- 因此在运行 E0--E3 之前就没有可比较的 candidate，继续跑 toy benchmark 不会修复 novelty。

当前 NCS 方法主线停止。state-complete EcoMD、免费 L2 重建和 simulator audit 仍作为独立且有价值
的工程/科学交付继续，但不能用于掩盖方法新颖性失败。若未来重新开启，必须先在新分支写出未被
`ncs_g0_forward_audit_2026-08-10.md` 覆盖的数学原语并重新审计，而不是改写本次 FAIL。
