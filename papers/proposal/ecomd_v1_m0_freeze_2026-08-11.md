# EcoMD v1 M0 方法冻结（2026-08-11，预实现）

**状态：** implementation 前冻结；不含任何新 fidelity 结果。若实现门失败，先修复或显式撤销本
冻结，不得静默换配置。

## 1. 冻结目标

M0 只回答“EcoMD v1 到底是哪一个模型、训练时是否执行同一条状态/随机定律、改变计算规模是否
偷换物理”。它不回答模型是否拟合真实市场。S0 已可发布但尚未发布；checkpoint 与正面 model-paper
claim 仍由 M1 stationary-fidelity gate 阻断。

## 2. 唯一 canonical architecture

EcoMD v1 M0 是以下组合，其他已实现模块均不是 v1 的一部分：

1. (N) 个 (d=32) 连续状态 agent，Euler--Maruyama overdamped Langevin 更新；
2. 一个共享、对称的 `stochastic_mlp` pair potential，每个 agent 每步无放回均匀抽取 (k=50)
   个 partner；
3. full-pair potential 使用 Kac normalization (V_{pair}/(N-1))，使总能量与 (N) 同阶、单
   agent force 在 mean-field 极限不随 (N) 线性发散；
4. 一个 (d_u=16) 的完整状态 global GRU，同时进入 pair 与 external potential；
5. 四个固定、seeded agent 类型，只通过预先固定的 friction/temperature multipliers 表达异质性；
6. Gaussian bath；不使用 Student-t/Lévy bath、compound-Poisson jump、tail clamp、power-law
   external potential、AR whitening、Zumbach feedback 或任何 crash-specific forcing；
7. excess-demand price map 对 aggregate demand 除以 (sqrt{N})，使用固定 square-root impact
   exponent (delta=0.5)、一个固定时间尺度的 Hawkes memory 和 additive Gaussian price noise；
8. 不使用 edge gate、type-specific pair heads、agent GRU、regime GRU/Hopfield、MoE、ISAB、MACE、
   EcoMD-v2/Kyle head、neural-SDE volatility head 或 scheduled sampling。

选择理由是可解释、可识别和最小充分性，而不是旧结果排名。Gaussian bath 与 zero jumps 刻意阻止
模型通过外生重尾输入“复现”重尾；若 stationary heavy tails 不能从相互作用/状态/impact 产生，M1
必须失败并停止正面 claim。`MACE/equivariant`、order-book、真实市场物理和 universal crash precursor
均不属于 M0 claim。

## 3. 尺度、训练与状态合同

冻结 reference scale 为 (N=256)、`hidden=96`、`d_state=32`、`k=50`、FP32。训练使用
`chunk_steps=64`、`warmup_steps=16`、`max_lag=8`，因此每次损失至少有 47 个 usable returns，超过
(4\times max\_lag=32)。`n_iters=600` 使主损失看到约 28,200 个 usable returns，与历史配置中
短主窗口加 512-step regularizer 的总暴露量同量级，但不继承其状态错误。

Release contract v1 全部强制：`state_complete=true`、`persistent_state=true`、同一 generator stream、
`jump_legacy_train_proxy=false`、`bptt_checkpoint_every=0`、`bptt_custom_function=false`。gamma 与
temperature 固定为历史 scale anchors（10.0 与 0.05），不得解释为测量得到的市场物理常数。

M0 禁用 long-rollout regularizer。当前实现虽在 chunk 间 detach forward state，但把所有 chunk 的
return graphs 保存到最终 loss，峰值 activation memory 仍随总 regularizer horizon 增长；在有独立
memory-bound implementation 与等价性测试前，不得把它描述为“只占一个 chunk 显存”。

## 4. 数据切分

首次 reference 只用现有内部 SPX daily 数据，且原始数据不随 release 分发：

- calibration/train：2015--2018；
- model-selection validation：2019 vanilla period；
- 2020 COVID：封存 crash test，不参与任何选择；
- temporal test：2021--2024；
- 2025--2026（若 provenance 完整）：supplemental future holdout。

NDX、gold、EURUSD 与 BTCUSDT 不参与 M0 选择。它们在 M1 通过后才用于“同一模型规格、重新训练”的
cross-market evidence；不得把频率不同的 series 混成一个无条件 joint target。任何未来新数据都
必须有 license、download timestamp、raw/preprocess hash 与冻结时间切分。

## 5. 免费 implementation/CPU gates

在占用 V100 前必须全部通过：

1. YAML 只有 `EcoMDConfig` 合法字段，release contract 校验通过，active/disabled module audit 与本
   文逐项一致；
2. 当 (k=N-1) 时，stochastic full-neighbour energy 与 dense pair energy 在 Kac/legacy 两种模式
   精确一致；小 (N<k_{configured}) 使用实际 partner 数，不允许 estimator bias；
3. `ed_normalize=true`，Kac normalization 开启，配置 horizon 检查通过；
4. 同一 canonical architecture 只把 `n_agents` 临时降到 64，运行两次 synthetic-target CPU
   training iterations：loss、trajectory、所有已有梯度均 finite，至少一个非零梯度；
5. 中断/恢复后的第二 iteration 与不中断 reference bit-exact；输出 config hash、parameter count、
   wall time 和 peak RSS；
6. repository tests、strict mypy 与 commit-delta Ruff 均不得回归。

CPU smoke 唯一允许的 scientific-size override 是 `n_agents: 256 -> 64`；`n_iters` 可缩为 2。模型
模块、(d)、hidden、(k)、dt、loss、chunk、warmup、seed、dtype 与 transition law 不变。

## 6. V100 pilot 与停止规则

CPU gates 在 clean implementation SHA 上通过后：

1. 第一台 V100 32 GB 只跑 seed 0 的 10-iteration FP32 pilot，记录 GPU UUID、software、config/SHA、
   checkpoint、exact resume、iteration time、allocated/reserved HBM；
2. 接受门为 finite training、resume exact、peak reserved HBM <= 26 GiB，且 600 iterations 的线性
   wall-time projection <= 12 小时；
3. 第一台通过后，第二台用相同 seed 做独立 host reproduction。参数/trajectory hash 若因 deterministic
   kernel 限制不能 bit-exact，必须量化差异，不能只写“看起来一致”；
4. 若容量门失败，只允许显式 refreeze 到 (N=128) 后重跑 CPU gates；不允许临时打开 custom BPTT、
   mixed precision、H20 或改变模型机制；
5. 10-step pilot 绝不用于选择 loss、机制或超参数。完成 600-step reference 后按另行预注册的固定
   stationarity protocol 打分；若 late/post-gate fidelity 仍约为 1--2/11，则停止正面 model-paper
   claim，保留透明软件和负结果。

## 7. 实现前可追溯目标

| 概念 | 公式/合同 | 配置键 | 实现入口 | 必须测试 |
|---|---|---|---|---|
| pair energy | (V=(N-1)^{-1}\sum_{i<j}\phi_\theta) | `pairwise_kac_normalize` | `StochasticPairwisePotential.forward` | full-neighbour dense equality |
| conservative force | (F_i=-\partial V/\partial s_i) | `legacy_total_derivative_force=false` | `conservative_forces` | finite-difference/gradient path |
| Langevin step | (ds=(F_c+F_d)dt/\gamma+\sqrt{2Tdt/\gamma}dW) | `dt`, `gamma_init`, `temperature_init`, `noise_dist` | `OverdampedLangevin.step` | chunk/resume equality |
| heterogeneity | ((\gamma_i,T_i)=(\gamma g_{z_i},T t_{z_i})) | `twopop_*`, `v2_type_seed` | `EcoMDSimulator.step` | deterministic type assignment |
| global state | (u_{t+1}=GRU(x_t,u_t)) | `global_state_*` | `GlobalStateGRU` | full-state continuation |
| aggregate demand | (D_t=\kappa\sum_i\Delta s_{i0}/\sqrt N) | `ed_normalize`, `kappa` | `ExcessDemandPrice.step` | scale contract |
| price impact | (r_t=\beta\,sign(D_t)s(|D_t|/s)^{1/2}+\epsilon_t+H_t) | `impact_*`, `beta`, `sigma_price`, `hawkes_*` | `ExcessDemandPrice.step` | deterministic/noise split |
| checkpoint | complete state + RNG + optimizer + rank runtime | `state_complete`, `persistent_state` | `save_checkpoint`, `restore_rank_runtime` | exact interrupt/resume |
