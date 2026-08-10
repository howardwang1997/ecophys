# EcoMD v1 发布范围与硬门（2026-08-10）

**决策：** 先做无 checkpoint、无原始市场数据的 source research preview；只有重新训练的
state-complete 模型通过 stationary-fidelity gate 后，才发布模型 checkpoint 和正面 model-paper
claim。当前 research monorepo 不能直接打包成 release。

## 1. 为什么现在切换到这条主线

NCS invariant-calibration 路线没有通过 G0，通用 simulator-audit 论文也没有通过 F0 prior-art
novelty gate。Exp128--143 仍然有价值，但价值是 EcoMD 的语义 QA、失败披露和发布基础设施，
不是一篇独立通用审计论文。继续扩展 external adapters、购买数据或增加 GPU 都不能补上缺失的
方法新颖性。

EcoMD 首次正式方法发布仍有独立价值，但必须先解决旧 checkpoint 的 forward-law 和 state
continuation 不一致。代码现已支持完整 `SimulatorState`；2026-08-10 的进一步审计还发现，长时程
rollout regularizer 在主路径开启 `state_complete` 后仍走旧 `rollout_chunk`。该路径已修复并由
回归测试锁定。因此，历史 checkpoint 仍全部失效，只有新配置、新训练才可能进入发布候选。

## 2. 两级发布，而不是一次性包装

### S0：source research preview

允许发布：核心源码、模型/状态/观测契约、纯合成 CPU smoke、选择后的测试、构建脚本和 MIT
代码许可证。

明确不发布：任何 checkpoint、原始或衍生 vendor data、历史 experiment outputs、W&B/R2
信息，以及真实市场 fidelity/physics/order-level claim。

### S1：model release candidate

只有 M0/M1 通过后才能增加：冻结配置、从零重训 checkpoint、训练与 rollout manifests、固定
post-stationarity 结果、基线与消融结果。旧 checkpoint 不得重命名或补 metadata 后混入。

## 3. 发布门与当前状态

| Gate | 通过条件 | 2026-08-10 状态 | 失败后的动作 |
|---|---|---|---|
| R0 范围/许可 | allow-list artifact；无 `.pt`、vendor raw data、secret；逐数据源 provenance | **artifact PASS / monorepo FAIL**：commit `4b741d6692e9` 的 89-file 包两次构建同 hash，forbidden scan 为 0；整个仓库仍不可发布 | 只发布 synthetic/source artifact；另行处理历史 Git 数据 |
| R1 状态/定律 | 主训练、regularizer、inference 使用同一 forward law 和完整状态；exact resume 测试 | **代码 PASS，checkpoint FAIL**：仓库 76 tests、artifact 27 tests 均通过；旧 checkpoint 不合格 | 冻结新配置后从零重训 |
| R2 包安装 | committed tree 构建 wheel；隔离路径安装和 import/run 成功；core strict mypy | **PASS**：两个独立源码目录生成同一 wheel；隔离 import/smoke 通过；strict mypy 对 66 个模块为 0 errors | 保持回归；342 条全包 Ruff 历史债务单列，不伪装成新错误 |
| R3 数据无关 smoke | CPU 生成有限 trajectory、梯度、任意 chunk、checkpoint round trip | **PASS**：35 个 finite nonzero gradient params；chunk/resume bit-exact；报告已归档 | 保持回归测试 |
| R4 V100 reference | 冻结 config 在一张 V100 32 GB 训练/恢复/rollout；第二台独立复现 | **未启动**；旧 exp127 只证明容量足够 | R0--R3 与配置冻结后才排队 |
| R5 stationary fidelity | 预注册 gate 后固定窗口，early/post-gate/late 全报告，多 seed | **FAIL**：旧 exp127 late-time 约 1--2/11 | 若新模型仍失败，停止正面 model-paper claim |
| R6 论文证据 | 强基线、关键消融、时间外/市场外/频率外、梯度效用、规模曲线 | **未开始** | R5 通过后扩展数据和算力 |

## 4. M0：要冻结的模型规格

2026-08-11 的 implementation 前冻结见 `ecomd_v1_m0_freeze_2026-08-11.md`；它先固定 Kac/需求
尺度归一化、唯一 active modules、数据切分、CPU/V100 gates 和停止规则，再允许实现或运行。

冻结前不再把历史配置中的模块并列写成“EcoMD v1”。候选方向是 exp127 使用的
`stochastic_mlp` 交互、两类 agent、global state 和 excess-demand price path，但它只是候选，不是
最终 canonical architecture。冻结配置必须：

1. 显式写 `release_contract_version: 1`、`state_complete: true`、
   `persistent_state: true`；
2. 显式关闭 `jump_legacy_train_proxy`、`bptt_custom_function` 和 grouped BPTT checkpointing；
3. 逐项列出启用模块，删除未启用的 MACE/equivariant 等叙事；
4. 固定 seed policy、dtype、chunk、绝对时钟、partner-cache refresh、jump law 和 checkpoint format；
5. 冻结训练/验证/测试时间切分；crash events 不参与模型选择；
6. 对论文公式、配置字段、实现入口和 loader 做四向 traceability 表。

## 5. 数据需求

### 现在即可完成（零购买）

- 纯合成 Student-t/Gaussian/control trajectories：安装、状态、梯度、resume 和 artifact smoke；
- 现有内部数据：仅用于不对外分发的 feasibility 与 pipeline 验证，并保持时间切分；
- 已生成的 Exp127--143 结果：用于失败复核和 release QA，不转化为正面 fidelity 证据。

### R5/R6 后续扩展

- 至少股票、外汇/商品、加密三类市场；
- 每类多个资产、多个非重叠时期和至少三个采样尺度；
- L2/event data 只在验证 order-book claim 时需要，不能由 aggregate-bin proxy 替代；
- 所有新增数据写 source、license、download time、raw hash、preprocess hash 和冻结 split manifest。

原始 Yahoo Finance 文件默认不发布；LOBSTER 文件需书面再分发许可；Binance 文件在找到适用的
明确许可前也不发布。公开复现包提供 provider 下载说明、hash 和 preprocessing，而非数据副本。

## 6. 算力需求

### 现在

- Mac/普通 CPU：R0--R3、单元测试、wheel/source artifact、tiny training smoke；
- 不占用 V100，不排 H20。

### 配置冻结后

- 第一张 V100 32 GB：单卡 fp32 reference、checkpoint/resume、长 rollout 和显存/吞吐记录；
- 第二张 V100 32 GB：独立 host/seed 复现；
- 两卡不做未经验证的长 sweep。先用短 pilot 得到每 iteration wall time，再据此冻结预算。

### R5 通过后

可以扩展到更多非 H20 GPU，用于多 seed、cross-market、ablation 和 scaling；算力增加只提升证据
覆盖，不能替代 state contract、数据许可或 held-out 设计。

## 7. 下一批实验顺序

1. **E-R0（完成）**：构建 allow-listed source preview，扫描 forbidden suffix/path，记录 SHA-256；
2. **E-R2（完成）**：从 wheel 隔离安装，运行 data-free CPU trajectory 与完整状态 checkpoint round trip；
3. **E-M0（当前）**：比较候选 canonical modules，产出唯一冻结 config，不做真实数据调参；
4. **E-M1-pilot**：CPU/tiny-N 只验证新训练路径、loss/gradient/stationarity 程序能跑通；
5. **E-M1-V100**：冻结后在一张 V100 做短 pilot，预算通过后再训练；第二张做独立复现；
6. 只有 stationary gate 通过，才启动基线、消融、跨市场和论文主结果。

停止规则：若 state-complete 重训在冻结 post-gate 指标上仍接近旧结果（约 1--2/11），EcoMD 可以
继续作为研究软件，但不写“成功复现市场统计”的正面模型论文。
