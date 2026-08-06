# Workshop 论文完成与双 V100 执行计划（2026-08-07）

**状态：** 用户已于 2026-08-07 确认，立即执行。

**冻结决策：** 两台节点按 V100 32GB 使用；H20 路线关闭，缺失 checkpoint 按原配置重训并
作为新 artifacts；Paris/Sydney 均可按科学需要参加，venue 不再受地点约束；Paper E /
Sim2Science 为 P0，Paper S / STODY 仍需证据门。

**外部截止：** STODY 与 Sim2Science 均为 2026-08-29 23:59 AoE，即 2026-08-30
23:59 Auckland。内部提交保持 2026-08-27，实验与正文保持 2026-08-24 冻结。

**与旧计划的关系：** 本文是当前执行主计划，取代
`workshop_claim_gates_and_merge_plan_2026-08-07.md` 的机器分配、checkpoint 假设和 exp108
跨架构表述；其 E-A/E-B/E-C、S0--S4、claim 边界和“不为凑两篇而强投”的原则继续有效。
`workshop_submission_plan_2026-08-07.md` 继续负责模板、OpenReview、匿名化和现场报告。

## 1. 要交付的结果

P0 是完成一篇可以独立投稿的 Sim2Science 5-page paper：

> 对具有 persistent internal state 的模拟器，直接对完整 rollout 评分会把初始化松弛混入
> steady-state model quality；一个只使用 calibration trajectories 冻结的 stationarity gate，
> 配合固定长度 post-gate scoring，可以检测并量化这一混淆。

STODY 4-page short paper 是条件性第二篇。新增 GPU 不改变它的科学门槛：如果只能证明 EcoMD
内部存在冲击后的重尾瞬态，而不能给出稳健估计和非平凡诊断，就把一个 intentional-shock
panel 合入 Paper E 作为 positive control，不单独投稿。

最终仓库交付：

- `experiments/127_workshop_claim_gates/`：冻结设计、预注册、显式 seed manifest、结果、deviation；
- `papers/paper_a_methods/workshops/sim2science/`：官方 2026 模板、正文、参考文献、checklist、图；
- `papers/paper_a_methods/workshops/stody/`：只有通过 rescue gate 后才建立完整稿；
- 两台远端机器的可复现实验 launcher、环境清单、硬件/软件 manifest 和结果回传记录；
- release-candidate PDF、匿名化检查、引用核验、PDF hash 和本地 submission checklist。

## 2. 已核实的机器事实

两台用户提供的 32GB GPU 节点记为 `v100-a` 与 `v100-b`；地址只写入 gitignored 的
`scripts/machines.local.json`，不进入论文、日志或公开 git。

| 项目 | v100-a | v100-b |
|---|---:|---:|
| `nvidia-smi` 名称 | Tesla PG503-216 | Tesla PG503-216 |
| 显存 | 32768 MiB | 32768 MiB |
| compute capability | 7.0 | 7.0 |
| driver / reported CUDA | 550.127.05 / 12.4 | 550.127.05 / 12.4 |
| 主机内存 | 31 GiB | 31 GiB |
| `/data` 可用 | 约 180 GiB | 约 98 GiB |
| 当前 GPU 状态 | idle | idle |

compute capability 7.0 是 Volta 路径，因此执行上必须按 **V100 32GB** 而不是 Blackwell B100
处理。两台机器均可通过 `root` key 登录，但当前没有 EcoPhys 仓库或 `ecophys` Conda 环境。

生产文件统一放 `/data/ecophys_workshop/`，不用空间更紧的根分区。每台只放当前需要的代码、
checkpoint 和 rollout；结果验证后立即回传 Mac，并清理可再生临时文件。远端不保存长期 R2
密钥；checkpoint 由 Mac 定向下载后 rsync，或由用户从 H20/GPFS 同步。

## 3. 当前最高风险：关键 checkpoint 不在现有归档

本机没有 exp108、exp113、exp114 或 exp126 的 `checkpoint.pt`。对 R2 `checkpoints/` 的只读
扫描得到 7856 个对象，但没有 exp108/113/114 路径；常见替代前缀同样为空。当前 R2
checkpoint 目录中的标准实验归档只列到 exp096。exp125/126 本地也没有正式 trajectory NPZ，
只剩 windowed reports，因此不能从现有文件完成新的 fixed-length gate 或恢复估计器审计。

正式运行前必须选择以下一条 provenance 路线：

1. **首选，恢复原 checkpoint：** 从 H20/GPFS 找回 exp108 `sv_d3_both` seeds 0/1/2、
   exp113 SPX concave/baseline、exp114 NDX/Gold/EURUSD/BTC concave 及 BTC baseline，核对 SHA256
   后定向传到两台 V100；
2. **fallback，完整重训：** 使用仓库中的原 config 和原数据快照重训所需 checkpoint。重训
   结果是新 artifact，不能和 exp126 的旧汇总曲线假装成同一 checkpoint 的配对证据；需要
   重跑进入论文的相应 rollout，并完整披露；
3. 若两条路线都不能在 8 月 10 日前形成冻结 checkpoint manifest，Paper E 降为更窄的
   EcoMD case study，Paper S 取消，不用不相干的旧汇总填证据缺口。

重训前先在 V100 上跑一个原配置 10-iteration probe。不得降低 `chunk_steps=24` 后仍称复现
原训练协议。现有实测训练峰值 14.85 GiB reserved，32GB 显存足够；真实时长以 probe 为准。

## 4. 科学审计后的必要修正

`experiments/108_neural_sde_scout/config_sv_d3_both_seed*.yaml` 仍实例化 `EcoMDSimulator`，使用
相同的 `pairwise_kind: stochastic_mlp`、agent state、SPS potential 和冲击实现，只增加 learned
stochastic-volatility components。它是 **EcoMD 内的架构变体**，不是独立 neural-SDE 生成器
家族。

因此：

- Paper E 的 E3 改名为 **within-family architectural robustness**；
- 可以写“在两个 learned-dynamics variants 和独立 analytic controls 上测试”，不能写
  “跨两个独立生成器家族”；
- 它不再自动满足 Paper S 的跨架构普适性门；Paper S 必须靠新的 causal diagnostic 或理论
  结果取得独立价值；
- 任何结果都仍是 simulator/model-error physics，不是实证 market physics。

## 5. Paper E 的实验包

### E0：实现、冻结和完整性测试

- 新建 exp127 的 `DESIGN.md`、`PREREG.md`、`MANIFEST.json`、`RESULTS.md`；
- 固定 `T=8000`、评分长度 `L=4000`、候选
  `W={0,50,100,200,500,1000,1500,2000,3000}`；
- delay vector 固定为 `(r_t, |r_t|, |r_{t+1}|)`，500-step non-overlapping blocks；
- threshold 只由每模型 calibration split 的 late-vs-late energy-distance distribution 确定；
- W-star 是最早连续三个 blocks 通过 tolerance 的起点；无 W-star 时报告“在评价窗口内未达到
  可验证稳态”，不强行评分；
- 增加显式 seed manifest 支持，禁止继续用 `seed_base + rank*1000 + realization_idx` 隐式
  推导正式样本；两节点各包含 calibration 和 held-out seeds，避免节点与 split 混淆；
- 单测至少覆盖：相同分布低误报、已知 change point 检出、fixed-length 等长、split 无泄漏、
  seed 不随 GPU 数变化、缺失 W-star、NPZ/manifest hash 一致。

### E1：held-out EcoMD fixed-length scoring

- 5 个 concave checkpoints：SPX、NDX、BTCUSDT、Gold、EURUSD；
- 2 个 baseline-family checkpoints：SPX、BTCUSDT；
- 每 checkpoint 32 条 no-shock `T=8000` rollout；16 calibration、16 held-out；
- primary：held-out `Hill(W-star) - Hill(W=0)` 的 checkpoint/trajectory-aware paired effect；
- secondary：11 facts sensitivity、target distance、通过项数、模型排序；排序翻转不是 pass 条件；
- 所有比较使用相同 `L=4000`，不允许删掉 warm-up 后使用更短序列。

### E2：独立 analytic specificity/sensitivity controls

使用 exp080 已有参数，不重新拟合：

- GARCH-t：long-burn、nominal、cold-low、cold-high 各 1000 条 CPU trajectories；
- 新增 AR(1)-SV 同构对照：stationary start、cold-low、cold-high；参数来自已保存的 exp080
  配置/结果，不重新选择最好参数；
- long-burn/stationary-start 用于 false-positive，cold starts 用于 sensitivity；
- primary 是在相同 calibration false-positive budget 下的 detection rate 和 detection delay；
- 不根据 Hill target 或 held-out 结果调整 threshold。

### E3：EcoMD stochastic-volatility 架构变体

- `sv_d3_both` seeds `{0,1,2}`，每 checkpoint 32 条 no-shock `T=8000` rollout；
- 完全复用 E0，不根据旧 scoreboard 换 seed；
- 只解释为 within-family replication；null 结果完整进入正文或 supplement。

### E4：简单 baseline 比较

在完全相同的 calibration/held-out split、false-positive budget 和 `L=4000` 下比较：

- 不丢弃 warm-up；
- 固定 `W=500` 与 `W=1000`；
- ADF/KPSS，分别作用于 returns 与 absolute returns；
- frozen energy-distance gate。

如果 proposed gate 在 analytic cold-start detection、held-out score bias 或 false-positive tradeoff
上没有优于固定 discard/标准测试的可重复收益，删除“新 gate 更好”的 claim；最多保留 EcoMD
measurement pitfall case study。

### Paper E claim gate

- **E-A：** held-out EcoMD effect、long-burn specificity、cold-start sensitivity、within-family E3
  及至少一个独立 analytic control 均成立，而且 E4 显示 gate 有非平凡收益；
- **E-B：** EcoMD effect 与 analytic specificity 成立，但 E3 或 baseline advantage 不充分；题目、
  摘要明确限定为 case study/protocol audit；
- **E-C：** long-burn 误报失控、held-out effect 消失、需要 target leakage，或 fixed-length 无法
  实现；停止当前方法学投稿，不继续调参直到正结果出现。

## 6. Paper S 的 rescue gate

默认不把 exp126 的旧 shock atlas 自动升级成第二篇。只有 E0--E4 已完成，且以下全部在
8 月 14 日前冻结，才保留 STODY：

1. **S0 estimator integrity：** 三种 recovery estimator 在 window `{200,500,1000}` 下方向一致，
   结论不依赖 Hill floor、raw/post-impact 混淆或窗口挑选；
2. **S-R1 norm-matched causal control：** 新增 `balanced_state_kick`。与 coherent `state_kick`
   使用相同选中比例、坐标、每代理绝对位移和总 L2 norm，但用冻结的一半正/一半负符号使
   mean displacement 为零；
3. **S-R2 reproducibility：** 在 SPX EcoMD checkpoint 和 `sv_d3_both` seeds `{0,1,2}` 上使用
   同一显式 seed manifest，比较 control/coherent/balanced/temperature/reduced-friction；
4. **diagnostic value：** coherent 与 balanced 的差异必须稳定跨 checkpoint，并形成预注册的
   coherence-sensitivity diagnostic。若二者相同，删除 coherence mechanism；若只在单一
   checkpoint 成立，Paper S 取消；
5. claim 只能是“learned Langevin simulator 内的 intervention-specific transient 与诊断”，
   不能写 universal stochastic dynamics、market law 或 crash mechanism。

balanced kick 只是比现有 temperature control 更公平的能量/范数对照；它不等于真实市场
验证。若 rescue gate 失败，只在 Paper E 放一张 intentional-nonstationarity positive-control
小图，不把更多 dose curves 或 trained-Lévy 结果拿来填满第二篇。

## 7. 两台 V100 的部署与作业分配

### 7.1 部署原则

- 在 `/data/ecophys_workshop/` 建代码快照、Conda env、checkpoint staging 和 results；
- 使用 Python 3.11 Conda 环境，安装后验证 PyTorch build 包含 `sm_70`；
- 远端运行代码必须对应一个冻结 git SHA；在当前 dirty worktree 直接 rsync 后运行不算正式结果；
- 两节点分别启动单 GPU worker，不做跨节点 `torchrun`；
- manifest 记录 GPU UUID、driver、PyTorch/CUDA、git SHA、config SHA256、checkpoint SHA256、
  seed、wall time、peak allocated/reserved memory；
- 每个 completed shard 先做 schema/hash/count 校验，再回传 Mac；失败 shard 只按 manifest 重跑。

### 7.2 必过 probe

每台先跑同一 checkpoint、同一 seed 的一条完整 `T=8000` lightweight rollout：

- 无 NaN/Inf、输出长度和 schema 正确；
- peak memory 低于安全阈值；
- 两台结果无需 bitwise 相同，但同 GPU 型号/软件栈的统计量必须在预定容差内；
- 以实测 rollout time 替换当前 3--5x H20 的保守估计。

如果需要重训，再在每台做保持 N=10k、fp32、`chunk_steps=24` 的 exact 10-iteration probe。

### 7.3 正式分片

Paper E E1+E3 共 320 条 rollout。每个 checkpoint 的 32 个 seeds 分为两个 16-seed shard，
每台各运行 8 calibration + 8 held-out seeds；这样 checkpoint 对比仍使用完全相同的 seeds，
硬件与数据 split 也不混淆。按当前保守估计总计 45--75 V100 GPU-hours，即两卡约
22.5--37.5 小时纯计算，排期预留 28--48 小时含重试和回传。

E2/E4 在 Mac CPU 并行运行，不占 GPU。Paper S rescue 只有 Paper E 结果冻结后才入队，绝不
让条件稿阻塞必保稿。

## 8. 日程（Auckland time）

| 日期 | 必须交付 | Stop/转向 |
|---|---|---|
| 08-07 | 用户确认本计划；回答 checkpoint、投稿数量/现场问题 | 未确认前只做只读审计 |
| 08-08 | exp127 DESIGN/PREREG/manifest；E0/E2/E4 实现与单测；建立两台环境 | checkpoint provenance 不明则不正式跑 |
| 08-09 | checkpoint 恢复；双机 full-rollout probe；冻结执行 SHA 和 seed shards | probe 不兼容/超显存则先修，不降协议 |
| 08-09--08-11 | 双机 E1/E3；Mac 并行 E2/E4；持续校验和回传 | 不查看 held-out 后改 gate/W/seed |
| 08-12 | 冻结 Paper E 结果，判定 E-A/E-B/E-C；生成三张候选图；完成 abstract v0 | E-C 停止方法调参 |
| 08-12--08-14 | 仅当 Paper E 完成后运行 S0 和 S-R1/S-R2；并行写 Paper E | 无 raw/ckpt 或 diagnostic 不稳则取消 S |
| **08-15 12:00** | **锁定 0/1/2 篇、venue、track、作者、reviewer 和现场方案** | 默认一篇 Paper E，不为数量延期 |
| 08-15--08-18 | Paper E 完整 5-page v1；若 S 存活，完成 4-page v1 | 每个数字指向 frozen artifact |
| 08-19--08-21 | 三轮内部审稿：claim/statistics；venue/prior art；匿名/格式 | 核心缺口只收窄 claim，不开新故事 |
| 08-22--08-23 | supplement、artifact、limitations、引用逐条核验、blind Reviewer-2 | 未核验引用不得提交 |
| **08-24** | **实验和正文冻结，生成 RC1 PDF** | 之后只修事实/格式错误 |
| 08-25--08-27 | 平台 PDF QA、作者确认、OpenReview 内部提交、receipt/hash | 08-30 仅作平台故障缓冲 |

## 9. 写作计划

### Paper E：Sim2Science 5 pages

暂定题目：*When Is a Persistent-State Simulator Ready to Score? Stationarity-Gated Evaluation of
Learned Market Dynamics*。

正文预算：

1. Problem、failure mode、三条贡献：0.6 page；
2. related work 与 scope boundary：0.4 page；
3. frozen gate 与 fixed-length protocol：1.1 pages；
4. held-out EcoMD evidence：1.0 page；
5. architecture variant、analytic controls、baseline comparison：1.1 pages；
6. limitations、discussion、conclusion：0.8 page。

最多三张主图：gate schematic/baselines；held-out EcoMD score effect；variant 与 analytic controls。
shock atlas 不进入独立 Paper E；若合并，只留一个 positive-control panel。

### Paper S：STODY 4 pages，仅在 rescue gate 后

暂定题目：*Coherence-Sensitive Heavy-Tail Transients as a Diagnostic of a Learned Langevin
Simulator*。

最多三张主图：已有 5-asset transient/recovery；driver/dose contrast；新的 coherent-vs-balanced
diagnostic 与 within-family checkpoint replication。没有第三张可独立解释的图就不成稿。

两稿都必须删除或禁止：MACE/equivariance、empirical OFI、`tau(dose)`、universal crash law、
first differentiable market simulator，以及把 model-internal response 写成 real-market physics。

## 10. 完成和验收标准

实验完成要求：

- frozen config/seed/checkpoint/code hashes 完整；
- calibration 与 held-out 无泄漏；
- checkpoint seed 和 rollout seed 的统计层次不混淆；
- null、失败、缺失和 deviation 全部进入 `RESULTS.md`；
- CPU 分析可在 Mac 的 `ecophys` Conda 环境从回传 artifact 一键重建；
- 正式结果不依赖未记录的远端手改配置。

论文完成要求：

- 每篇一个可证伪 headline claim，摘要不超出结果 tier；
- 每个定量句、图、表都能追到 frozen artifact；
- 官方 NeurIPS 2026 模板、页数、checklist、匿名化和 PDF metadata 全部通过；
- 引用逐条打开原文核验，不出现不存在或支持范围错误的文献；
- 如果两篇同时提交，政策、现场报告、主图和核心证据均无冲突；
- 用户最终核对作者、license、公开发布、reciprocal-review 和提交字段后再上传。

## 11. 当前需要用户回答的三件事

这些问题已于 2026-08-07 得到用户答复：节点确认为 V100；H20 无法连接，因此执行完整重训
fallback；Paris/Sydney 均可按最终 venue 参加。双稿仍取决于 organizer policy 与 Paper S 的
科学证据门，地点本身不再限制 paper count。
