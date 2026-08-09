# Workshop 双稿 Claim 验证、保留与合并计划（2026-08-07）

> **2026-08-09 终局判定（覆盖下文尚未执行的 Paper S 与双稿任务）：** Paper E 已冻结在
> **E-B**；Paper S 没有通过 S0 加任一 S1--S4 独立成文门，因此 **STODY 路线终止**。不再运行
> shock rescue、trained-Lévy 或新的跨架构 STODY 实验。唯一 workshop 稿是 Sim2Science 的
> simulator-specific stationarity audit。由于 EcoMD 此前未发表，Paper E 必须在正文加模型框、在
> Appendix A 给出完整 audit-object 规格，并在 Appendix B 披露复现边界。匿名 artifact 仅含审计
> 代码和冻结 synthetic trajectories；EcoMD 核心源码、训练代码和 checkpoints 留给修复稳态 fidelity
> 后的独立模型论文。以下门槛与时间线保留为预注册决策记录，不再构成当前任务列表。

> **执行更新（2026-08-07）：** 当前机器分配、checkpoint 恢复分支、exp108 的架构分类和
> 写作排期以 `workshop_completion_2xv100_plan_2026-08-07.md` 为准。本文保留 claim gates 与
> 合并原则。exp108 `sv_d3_both` 是 EcoMD 内部架构变体，不是独立生成器家族。

**状态：** 已完成终局判定；仅 Paper E 继续，Paper S 已取消。

**投稿截止：** STODY 与 Sim2Science 均为 2026-08-29 23:59 AoE，即 2026-08-30 23:59 Auckland time。

**内部硬节点：** 2026-08-15 决定保留两篇还是合并；2026-08-24 冻结；2026-08-27 内部提交。

**与旧计划的关系：** 本文取代 `workshop_revision_plan_2026-07-22.md` 的投稿优先级、claim 边界和时间线；旧计划中的 W0--W4 技术协议、统计单位、provenance 要求和 exp 126 预注册约束继续有效。不得倒改 `experiments/126_strengthen_workshops/PREREG.md`。

## 1. 执行摘要

默认只保证完成一篇强稿：**Sim2Science 的 stationarity-aware evaluation paper**。STODY 是条件性第二篇，不再因为已有 shock atlas 就自动保留。

两篇的科学问题必须正交：

- **Paper E（Evaluation，Sim2Science 主投）：** 什么时候对有内部状态的科学生成器评分才可信？
- **Paper S（Stochastic dynamics，STODY 条件投稿）：** 结构化驱动在 learned Langevin simulator 内产生什么可复现的非平衡响应？

当前重尾瞬态的正确定位是“EcoMD 内部可复现的模型动力学”，不是已验证的市场物理。若 Paper S 到 8 月 15 日仍只有 EcoMD 单一模型中的现象、没有跨架构证据、因果定位、理论结果或实证对应，则取消独立投稿，把它降为 Paper E 的 intentional-nonstationarity stress test/positive control。

执行优先级：

1. 先完成 Paper E 的固定长度评分、held-out gate、neural-SDE 迁移和 GARCH specificity；
2. 再运行 Paper S 的恢复估计审计和最小跨架构 shock stress test；
3. 只有 Paper S 通过独立成文门槛后，才补 trained-Lévy Pareto 和第二份完整 PDF；
4. 不采购新数据，不为 workshop 临时开启 L2 清洗或真实市场 universality 搜索。

## 2. 当前证据与解释边界

### 已经成立

- exp 126 的 5 资产 atlas 显示：`state_kick` 与 temporary reduced friction 会明显加深重尾瞬态；temperature spike 接近 control；EURUSD 是弱响应边界案例。
- 5 资产 dense-dose 结果支持 dip amplitude 的饱和响应，单资产拟合 R² 为 0.962--0.983。
- 冲击后的尾指数会回升，因此可以报告有限恢复；不同恢复估计器尚未审计一致性。
- warm-up/burn-in 会显著影响 EcoMD 的 tail scoring；固定长度、calibration/held-out 的正式重算尚未完成。

### 尚未成立

- 没有证据证明该重尾瞬态是普适市场物理、crash precursor 或真实 order-flow law。
- `state_kick` 的瞬时 coherence 是干预构造，不是涌现；涌现内容仅包括响应幅度、跨 channel 差异、dose response 和恢复。
- 不支持 `tau(dose)` 定律；SPX 的新估计器在八个 dose 上都给出 350 steps。
- trained-Lévy 的 12 个 checkpoint 尚未得到可比较的 raw-ED/return Pareto 结果。
- neural-SDE 迁移和正确初始化 GARCH 的 specificity 均未运行。
- 现有真实 crash pilot 没有显示系统性的 crash-associated tail thickening，因此不能把模型响应外推到真实市场。

### 必须统一的实现表述

- 产生这些结果的是 `pairwise_kind: stochastic_mlp` 的 permutation-symmetrized stochastic pair-sampling potential，不是 MACE-lite，也不是 E(3)-equivariant message passing。
- raw ED 与 `rho` 是模拟 latent-flow proxies，不是已经验证的 empirical OFI。
- `liquidity_drop` 在代码中是 temporary reduced friction；market depth/liquidity 只是待验证的解释映射。
- Hill alpha 约 0.5 是估计器 floor/censoring，不能据此推断矩不存在。

## 3. Paper E：Stationarity-aware evaluation

### 3.1 唯一 headline claim

> 对具有 persistent internal state 的科学生成器，在确认 rollout 达到可验证稳态之前直接评分，会把初始化松弛误认为模型的稳态性质；model-agnostic stationarity gate 加固定长度 post-gate scoring 可以检测并避免这一混淆。

模型排名是否翻转不是通过条件。论文的核心是估计量和评价协议是否被系统性污染，而不是制造更戏剧化的排行榜变化。

### 3.2 Claim tiers

#### E-A：可推广的方法学 claim

只有同时满足以下条件才能使用 “stateful scientific generators” 的复数表述：

1. EcoMD held-out trajectories 显示预先规定的 warm-up effect；
2. frozen gate 在正确初始化/long-burn GARCH 上保持预注册的 nominal false-positive calibration；
3. frozen gate 对错误初始化 GARCH 的检测率显著高于 nominal false-positive rate；
4. neural-SDE 预选 seeds `{0,1,2}` 使用相同 protocol 后，至少 2/3 checkpoints 在 held-out split
   满足预注册的 early-vs-late detection 与 late-vs-late calibration 条件，且 aggregate effect 的
   不确定性支持迁移；
5. threshold、W-star 和主指标没有使用 held-out results 或 empirical targets 调参。

允许的措辞：`the protocol transfers across two learned dynamical variants and an independent analytic control`。neural-SDE 与 EcoMD 共享部分 simulator code，不能称为完全独立的生成器家族。

#### E-B：EcoMD case study

若 EcoMD effect 与 GARCH specificity 成立，但 neural-SDE 不迁移或 checkpoint 无法恢复，则保留论文，但题目和摘要限定为 learned Langevin market simulator case study。完整报告 transfer null，不把 null 藏入 appendix。

#### E-C：停止方法学投稿

满足任一条件即停止当前 gate claim：

- frozen gate 在 long-burn GARCH 上明显高于 nominal rate 误报；
- held-out EcoMD 上 full-rollout 与 post-gate fixed-length scoring 没有可重复差异；
- 主要结论依赖经验 target 调 threshold、改变 W grid 或选择性挑 checkpoint；
- fixed-length 原则无法实现，只能比较不同有效样本长度。

E-C 时不得继续调参直到出现正结果。可以保留完整 negative record，但本轮不以该方法学 claim 投稿。

### 3.3 必做实验

#### E0：完整性和冻结协议

- 沿用旧计划 W3 的 `L=4000`、候选 W、calibration/held-out split 和 energy-distance gate；
- 生成显式 seed manifest；记录 checkpoint、config、data、代码和 estimator hash；
- `shock_step=null` 表示 no-shock，不允许用数值型默认 shock step 截断 steady window；
- 在查看 held-out 结果前，把 nominal false-positive rate、GARCH 检测判据和 aggregate effect test 写入 `PREREG.md`；
- paired/hierarchical bootstrap 以 checkpoint/trajectory 层次正确重采样，不把 rollout 当训练 seed。

#### E1：EcoMD fixed-length held-out scoring

- 5 个 `concave_d050` 资产 checkpoint，加 SPX/BTC baseline-family 两个 checkpoint；
- 每 checkpoint 32 条无冲击 rollout，`T=8000`；16 calibration、16 held-out；
- primary：`Hill(W-star) - Hill(W=0)` 的 paired effect 与区间；
- secondary：11 facts 的 sensitivity curve、通过项数、target distance 和模型排序；
- 没有 W-star 的模型明确标记为“在评价窗口内未达到可验证稳态”，不强行给稳态分数。

#### E2：GARCH-t specificity 与 sensitivity

- 复用 exp 080 参数，不重新拟合；
- long-burn、nominal、cold-low、cold-high 四组各 1000 条 CPU trajectory；
- long-burn 检验 false positive，cold groups 检验 sensitivity；
- 不允许用这四组结果反向修改已冻结阈值。

#### E3：neural-SDE transfer

- 使用 exp 108 `sv_d3_both` 的预选 seeds `{0,1,2}`；
- 每 checkpoint 32 条无冲击 rollout，完全复用 E0/E1；
- 不根据旧 scoreboard 换 seed；缺失 checkpoint 优先恢复，重训时使用原数据快照与配置 hash。

## 4. Paper S：Driven stochastic dynamics

### 4.1 允许的 headline claim

> 在 EcoMD 这一 learned Langevin simulator 中，结构化 coherent drive 与 temporary reduced friction 能从轻尾稳态触发 mechanism-dependent heavy-tail transients；瞬态深度呈饱和 dose response，并在驱动后有限恢复，而 generic heating 不产生同等响应。

这是一条 **model-internal stochastic-dynamics claim**。正文不得使用 `market law`、`universal crash mechanism`、`empirical OFI` 或 `universal critical scaling`。

### 4.2 独立成文门槛

Paper S 必须先通过 S0，并至少通过 S1--S4 中一项，才值得作为第二篇投稿：

- **S0，完整性门：** 配对统计稳定；W2 三种恢复估计器支持方向一致的“有限恢复”；结论不依赖 Hill floor、窗口挑选或错误 raw/post-impact observable。
- **S1，跨架构门：** 在冻结干预协议下，neural-SDE 至少 2/3 checkpoints 复现预注册的主要
  channel ordering，且 checkpoint-level aggregate uncertainty 支持该对照。仅观察到稳定的
  architecture-dependent difference 不算通过 S1；它必须再由 S2 的因果定位支撑，才能成为
  独立贡献。
- **S2，因果定位门：** 通过组件日志/干预定位尾部瞬态的产生环节，并给出可验证的 correction 或 diagnostic；仅有相关曲线不算通过。
- **S3，理论门：** 给出 Langevin relaxation、ergodicity 或 finite-time response 的正式命题/推导，并由模拟检验其非平凡预测。
- **S4，实证门：** 预注册的 matched real-data test 验证模型预言的 order-flow coherence、depth proxy、tail dip 和恢复 signature。

本轮截止前的首选是 S1，因为可复用 exp 108 checkpoint；S2 仅在已有组件日志足够或能做小规模预注册 ablation 时运行。S3/S4 不作为仓促补实验的理由。

### 4.3 S1 最小跨架构 stress test

- 模型：neural-SDE `sv_d3_both` seeds `{0,1,2}`；
- 市场：SPX；
- arms：control、`state_kick`、temperature spike、temporary reduced friction、price jump；具体剂量固定为 exp 126 atlas 的既有代表值，不重新搜索；
- 每 checkpoint、每 arm 32 条 `T=8000` rollout；
- primary：pre-registered post-shock Hill deficit；
- secondary：恢复、数值稳定性与 architecture × intervention interaction；
- 统计单位是 3 个 checkpoint seeds；32 rollouts 只降低 checkpoint 内 Monte Carlo error。

结果解释预先限定：

- channel contrast 复现：只能声称跨两个 learned-dynamics variants 转移，仍不是市场物理；
- 定性 channel ordering 保持、幅度稳定不同：报告 architecture-dependent susceptibility，S1
  可以通过；
- 仅 EcoMD 有效：不能以“普适 stochastic dynamics”成文，除非 S2/S3/S4 另有一项通过；
- 结果不稳定或 estimator-sensitive：S1 失败，完整报告后执行合并。

### 4.4 降级任务

trained-Lévy W1 从 P0 降为条件性 P1。它可以补充“稳态重尾源是否可被训练安装”的故事，但不能回答当前最关键的 model-error/generalizability 问题。只有在 Paper E 的 E0--E3 完成且 Paper S 已通过独立成文门后才运行或写入主文。

同样，原 W5 的大规模 self-averaging 扫描不在 workshop 关键路径；没有完成就删除机制句，不用新的探索性拟合替代。

## 5. 8 月 15 日硬决策

### 保留两篇

必须同时满足：

1. Paper E 至少达到 E-B；
2. Paper S 通过 S0，并至少通过 S1--S4 中一项；
3. 两篇不共享 headline、主结果表或主图；
4. organizer 允许 related-but-distinct submissions，且按要求披露；
5. 两篇各自能在页数内形成完整 evidence chain，而不是把同一套数据拆薄。

### 合并成一篇

出现任一情况即默认合并：

- Paper S 只有 EcoMD shock atlas，没有额外 generalizable insight；
- Paper S 的恢复或尾部结果对 estimator/observable 不稳健；
- 两篇必须复用同一核心图或核心结论才能写完整；
- 双投政策未确认；
- 8 月 15 日仍没有 Paper S 的冻结结果包。

合并方式：以 Paper E 为主稿，只保留一项预先知道的 intentional nonstationarity 作为 gate 的 positive-control stress test。不得在合并稿中把它重新包装成市场物理发现。

### 只保留 Paper S

只有当 Paper E 进入 E-C，而 Paper S 已通过 S0 加至少一个独立成文门时采用。若 Paper E
进入 E-C 且 Paper S 也未通过独立成文门，本轮不为凑数量强行投稿；保留完整 negative record，
转向后续重新设计。

## 6. 时间线

| Auckland 日期 | 必须交付 | 停止/转向条件 |
|---|---|---|
| 08-07 | 冻结本计划；建立 exp 127 目录；写 E0/S1 `DESIGN.md`、`PREREG.md`、seed manifest；补发 organizer 询问 | 不得继续沿用已过期的 7 月里程碑 |
| 08-08--08-09 | 完成 E0 实现与测试、checkpoint/R2 inventory、H20 dry run；并行完成 E2 GARCH CPU 实验 | fixed-length 或 held-out split 无法无泄漏实现则暂停 E claim |
| 08-09--08-11 | H20 运行 E1 EcoMD 与 E3 neural-SDE；冻结原始结果和 hashes | 不因初步结果改变 W grid、seed 或阈值 |
| 08-12 | E-A/E-B/E-C claim-tier 决策；生成 Paper E 三张候选图 | E-C 时停止方法调参，转完整 negative record |
| 08-12--08-14 | 完成 S0/W2；运行 S1 最小跨架构 stress test；仅有余力时恢复 trained-Lévy scoring | S1 不稳定且无其他门可过，则不再补新故事 |
| **08-15 12:00** | **硬决定：两篇、合并一篇或只保留 Paper S**；写入 `RESULTS.md` | 决定后不重新开启被杀路线 |
| 08-15--08-18 | 建立目标 paper 目录；完成摘要、图表和结果段 | 每个定量句必须能指向冻结 artifact |
| 08-19--08-20 | 第一版完整 PDF；页数内完成证据链 | 缺一项核心证据就收窄 claim，不追加 headline experiment |
| 08-21--08-22 | Reviewer-2、统计单位、引用、related-work、双稿去重检查 | 有核心重叠则合并 |
| 08-23 | 匿名化、代码链接、supplement、复现清单、最终 page fit | 任何身份泄漏或错误架构描述必须修正 |
| **08-24** | **实验和文字冻结** | 此后只修事实错误和格式 |
| **08-27** | **内部提交并下载提交回执** | 给 08-30 23:59 NZST 留出平台/网络缓冲 |

## 7. 算力与执行顺序

### P0：Paper E

- E1：7 checkpoints × 32 rollouts；
- E3：3 checkpoints × 32 rollouts；
- 合计 320 条 `T=8000` rollout，按仓库 H20 实测速率约 15 GPU-hours 的理想模拟下限；8×H20 预留 4 小时，包括加载、评分、完整性检查和失败重跑；
- E2 使用 Mac/H20-4 CPU，预计少于 2 小时；统计分析另预留 4--8 CPU 小时。

### 条件 P0：Paper S 生存门

- S1：3 checkpoints × 5 arms × 32 rollouts，共 480 条；若速度接近 EcoMD，约 22 GPU-hours 理想下限；8×H20 预留 4--5 小时；
- S0/W2：原 trajectory 可恢复时 2--4 CPU 小时；丢失时才重跑 control 与代表 kick；
- trained-Lévy 与大规模 W5 不得占用 E0--E3 或 S1 的计算窗口。

Codex 会产出可执行脚本、manifest 和 handoff commands；H20 运行仍由用户通过 SSH 执行。异构 GPU 不放进同一 `torchrun`，显式 seed manifest 保持跨卡数实验设计不变。

## 8. 文稿边界和图表

### Paper E：最多三张主图

1. fixed-length score 和 frozen stationarity gate；
2. EcoMD held-out warm-up effect；
3. neural-SDE transfer 与 GARCH specificity/sensitivity。

shock atlas、dose law、trained-Lévy Pareto 不进入独立 Paper E。若最终合并，只允许一个简化的 intentional-shock positive-control panel。

### Paper S：最多三张主图

1. 5 资产 tail-index transient 与有限恢复；
2. intervention-channel contrast 与 saturating dip-amplitude law；
3. S1 跨架构 stress test，或通过的 S2/S3/S4 证据。

没有通过第三项独立成文证据时，不用 trained-Lévy 或更多 dose 曲线填满第三张图；执行合并。

### 去重规则

- 只共享不超过一段的必要模型背景，不共享结果图；
- Paper E 不讨论市场物理，Paper S 不把 stationarity gate 当主贡献；
- 相关投稿在 cover note/论文中按 organizer 要求披露；
- 同一 manuscript 不同时投 Sim2Science、FMTS 和 AI for Science。后两者只是 Paper E 的替代路线。

## 9. Venue routing

- Paper E 达到 E-A：Sim2Science 主投；若更强调 verifier artifact，可考虑 AI for Science，但二选一。
- Paper E 仅达到 E-B：Sim2Science 仍为第一选择；FMTS 是接受 negative/preliminary simulator-evaluation work 的备选，但不得称 EcoMD 为 foundation model。
- Paper S 通过 S0+S1：STODY 主投。
- Paper S 只有理论门 S3 特别强：DynaFront 可作为 STODY 的替代，不同时提交相同稿件。
- ICAIF 只进入 8 月 9 日后的 watchlist，不影响当前实验排程。

## 10. 仓库交付物

新建 `experiments/127_workshop_claim_gates/`：

- `DESIGN.md`：E0--E3、S0/S1 的冻结设计；
- `PREREG.md`：只登记尚未观察的 held-out 假设、阈值和 decision rules；既有 exp 126 结果标为 prior evidence；
- `MANIFEST.json`：checkpoint/config/data/git/estimator hashes、R2/GPFS URI 与显式 seed；
- `RESULTS.md`：包含 null、失败、缺失、deviation 和 8 月 15 日决策；
- H20 driver 与 CPU analysis entry point；
- 两套不复用输出文件的 figure scripts。

按最终决定新建：

- `papers/paper_a_methods/workshops/sim2science/`；
- `papers/paper_a_methods/workshops/stody/`，仅在 Paper S 存活时；
- 旧 `ml4ps/` 与 `genai_finance/` 只作为素材归档，不继续覆盖修改。

## 11. 完成标准

本计划完成不是“两份 PDF 能编译”，而是：

1. 8 月 15 日的保留/合并决定由预先规定的 evidence gate 决定；
2. 每篇只有一个可证伪 headline claim；
3. 所有结果可追溯到 frozen config、seed、checkpoint 和代码 hash；
4. 统计单位正确，null 与失败完整报告；
5. 模拟器内部动力学与真实市场物理明确分开；
6. 不再错误声称 MACE/equivariance、empirical OFI、`tau(dose)` 或 universal crash law；
7. 若两篇同时提交，核心证据不重叠且 organizer policy 已确认；
8. 最终 PDF 匿名、页数合规，并在 8 月 27 日完成内部提交。
