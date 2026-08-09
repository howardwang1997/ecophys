# NCS WP1：EcoMD 状态、力与随机动力学语义

**日期：** 2026-08-09  
**状态：** 单机 CPU 实现与回归测试通过；单卡 V100 probe 待记录；DDP 生产 checkpoint 尚未接入  
**适用分支：** `ncs-invariant-calibration-v4`

## 1. 本轮解决的问题

历史 `rollout_chunk` 接口只显式返回粒子状态、价格状态和 regime hidden state。它没有把 agent/global
hidden state、绝对时钟、积分器的路径依赖缓冲、邻接缓存、shock 状态和 RNG 状态作为一个整体交给
调用者。因此，训练 chunk 边界与 checkpoint 边界可能改变科学动力学。

实现 checkpoint-resume 测试时还发现两个独立问题：

1. 当当前粒子状态与 price/global context 共享 autograd 历史时，历史 force helper 会对共享图取总导数；
   detach 或序列化后却变为固定 context 的偏导数。同一数值状态因图拓扑不同而得到不同的力。
2. compound-Poisson jump 在 `create_graph=True` 时使用确定性 `tanh` drift proxy，而推理时抽样离散
   jump；autodiff 开关因而改变 transition kernel。

这些是模拟器语义缺陷，不是市场物理发现，也不能单独构成 NCS 方法贡献。

## 2. 状态完整 API

新增 `SimulatorState`，其最小完整状态为：

| 类别 | 字段 |
|---|---|
| 粒子 | `s`, `s_prev` |
| 价格 | `PriceState` 全部字段，包括 Hawkes memory 与 stochastic-vol latent |
| 隐状态 | `h_regime`, `h_agent`, `h_global` |
| 时钟/外生过程 | `step_idx`, `fundamental`, pending exogenous return, shock schedule/dynamics |
| 积分器历史 | memory EMA、上一期 price delta/noise、drift EMA、Zumbach EMA |
| 图结构 | MACE kNN 或 stochastic-pair edge cache 及 refresh clock |
| 随机性 | 显式 `torch.Generator` 的完整 RNG state |

接口契约：

- `init_simulator_state(seed=... | generator=...)` 只建立一次初始状态并捕获初始抽样后的 RNG；
- `rollout_state(state, n_steps, ...)` 以传入状态为唯一权威，恢复所有 mutable state 和 RNG，使用绝对
  `step_idx`，并返回下一份完整状态；
- `state.detached()` 是唯一显式的 truncated-BPTT 截断点；未调用时，跨 chunk 的 hidden-state 梯度保留；
- `to_checkpoint()` / `from_checkpoint()` 使用带 `format_version=1` 的普通 payload；模型参数仍由相邻的
  `state_dict` 保存；
- `step_idx != price_state.step` 时 hard fail，避免静默重置多时间尺度更新、regime schedule 或 shock clock。

旧 `rollout_chunk` 暂时保留，以便历史实验复现；它不满足新的完整状态契约。

## 3. 力与 jump 定义

`conservative_forces` 和 `dissipative_forces` 默认对一个与历史图相连、但独立的当前状态节点求导。
这实现了“对当前坐标求偏导、固定 context”的力定义，同时允许后续 BPTT 对状态历史和 context
传播梯度。`legacy_total_derivative_force=True` 仅用于 exp128 历史控制臂。

jump 默认在训练和推理中使用完全相同的 compound-Poisson transition law。当前 `jump_lambda` 与
`jump_scale` 是配置标量，因此没有声称对离散事件参数提供 pathwise gradient；若未来学习它们，必须
使用 score-function、StochasticAD 或 generator-based estimator。`jump_legacy_train_proxy=True` 仅用于
历史控制臂，不得用于科学生产模型。

## 4. 已冻结的回归证据

`tests/test_simulator_state.py` 当前覆盖六条性质：

1. 单段 rollout 与任意 chunk partition 的轨迹及最终完整状态 bit-exact；
2. 序列化 checkpoint-resume 与 uninterrupted rollout bit-exact；
3. 显式 detach 只截断梯度，不改变后续前向动力学；
4. 不显式 detach 时，分块与单段 rollout 的参数梯度一致；
5. `create_graph=True/False` 的 jump 路径与最终状态 bit-exact，且模型参数梯度仍有限；
6. 绝对时钟不一致时 hard fail。

`experiments/128_state_semantics_preflight/` 另用五个控制臂确认 force、state/clock 与 jump 三个因素都
是数值活跃的，并能在现有 SPX/BTC 数据目标上完成端到端训练。该实验只验证 mechanics，不评价哪一臂
更接近真实市场。

## 5. 尚未完成的生产集成

以下工作不能被本轮单机测试冒充为已完成：

- `train_ecomd(..., state_complete=True)` 已提供单 GPU 入口，但既有配置默认仍走 legacy path；
- `train_distributed.py` 尚未把 `SimulatorState`、optimizer、scheduler、AMP scaler 和各 rank RNG 合并为
  一个原子 checkpoint，也未做 preemption/restart 的跨进程 bit-exact 测试；
- DDP sampler/data cursor 与 W&B resume metadata 尚未纳入状态契约；
- 正式 WP2 的五臂多 seed、长时程冻结指标和 compute matching 尚未开始；
- 这套状态修复没有解决“不变测度梯度估计器是否新颖、正确和可扩展”的 G0/G2 问题。

因此，WP1 当前只能标记为“单机语义通过，生产续跑待完成”。在 distributed exact-resume 完成前，
任何长训练都必须保留旧路径标签，不能作为状态完整方法的 confirmatory run。
