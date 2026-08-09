# 两篇 workshop paper 修改与实验计划（2026-07-22）

**状态：** 执行计划，尚未开始新增实验。
**目标投稿：** STODY（4 页 short paper）与 Sim2Science（5 页、double blind、non-archival）。两者当前公开截止时间均为 **2026-08-29 AoE**；内部冻结时间设为 **2026-08-24**，内部提交时间设为 **2026-08-27（Auckland time）**。
**适用草稿：** `papers/paper_a_methods/workshops/ml4ps/` 与 `papers/paper_a_methods/workshops/genai_finance/`。这两个旧目录只作为素材来源，不直接改名投稿。
**证据基线：** exp 123、125、126；其中 `experiments/126_strengthen_workshops/PREREG.md` 仍是既有实验的约束性预注册记录，本计划不得倒改其假设、阈值或结果解释。

## 1. 先做出的修改决定

### Paper 1：STODY——受驱随机动力学

暂定题目：**Driven Heavy-Tail Transients in a Differentiable Langevin Market Simulator**。

只讲一个主问题：一个本来轻尾的稳态系统，在不同外部驱动下何时出现重尾瞬态，以及它如何恢复。正文保留：

1. 无冲击稳态与 `state_kick` 后的尾指数轨迹；
2. coherent kick、temperature spike、reduced-friction/depth proxy、price jump 的机制对照；
3. 5 个资产上的饱和型 **dip-amplitude law**；
4. 训练态 Lévy 噪声实验，用来判断稳态重尾源是否能被训练安装，以及代价是什么。

正文删除或降级：warm-up 方法学长篇、11 个 stylized facts 总分、跨生成器评价、真实 crash “stationarity”论断、未验证的实证 OFI 预测。恢复时间只报告为有限恢复及估计器敏感性；不再声称存在 `tau(dose)` 定律。

### Paper 2：Sim2Science——状态初始化污染模型评价

暂定题目：**A Stationarity Gate for Evaluating Stateful Scientific Generators**。

只讲一个主问题：对有内部状态的生成器，直接评分完整 rollout 会把初始化松弛误当作稳态模型性质；应先通过 stationarity gate，再计算固定长度的 stylized facts。正文保留：

1. EcoMD 上的固定样本长度 warm-up 敏感性；
2. 一个不使用经验目标调参的 stationarity gate；
3. warm-up 前后模型分数与排序是否改变；
4. neural-SDE 架构变体的迁移测试，以及 GARCH-t 的稳态初始化负对照和错误初始化正对照。

正文删除：shock atlas、dose law、OFI 机制、真实 crash 图、Lévy 稳态重尾 Pareto。这样两篇论文没有共用结果图，只有必要的模型背景重叠。

### 双投约束

- 2026-07-24 前分别询问两个 workshop organizer：同一研究计划下的 related-but-distinct submissions 是否允许，以及是否需要在投稿中披露。
- 若 organizer 不允许，或最终正文仍共享一个核心结论/一张结果图，则只投证据更完整的一篇。
- 两篇文稿分别建立 `workshops/stody/` 和 `workshops/sim2science/`；旧的 `ml4ps/`、`genai_finance/` 归档，不在原目录上继续叠加。

## 2. 已有证据、缺口与优先级

| 项目 | 当前状态 | 对投稿的意义 | 动作 |
|---|---|---|---|
| 5 资产 shock atlas | 完成，约 24 rollouts/arm | kick 与 reduced-friction 明显，temperature 近似 control，EURUSD 的 kick 较弱 | 直接用于 STODY，重新做配对统计 |
| 5 资产 dense dose | 完成 | dip amplitude 的饱和拟合强；SPX `R²=0.9743` | 保留 amplitude law，撤销 `tau(dose)` headline |
| return/ED 随 N 扫描 | 完成 | raw ED 近似平坦，return 与标准化 return 变轻 | 因 SNR/价格形成混杂，不进入核心论证 |
| 12 个 trained-Lévy 模型 | 已训练、未评分；checkpoint 不在本地 | STODY 最有价值的未闭环证据 | P0：修正 observable 后评分 |
| EcoMD warm-up arms | 有汇总 JSON，本地无原始 trajectory | Sim2Science 需要固定长度、可配对的严格重算 | P0：恢复轨迹或重跑 |
| neural-SDE exp 108 | 60 个训练日志/评分在库中，checkpoint 不在本地 | 只能称“第二架构变体”，不能称独立代码库 | P0：预选 3 seeds 做迁移测试 |
| 独立模型负对照 | 尚无专门实验 | 防止把所有模型都宣称成有 burn-in 问题 | P0：CPU 上做 GARCH-t 初始化对照 |
| 真实 L2 order flow | workshop 核心尚不需要 | 采购与清洗会威胁截止期 | 不进关键路径 |

优先级定义：P0 是投稿前必须闭环；P1 只有在核心实验完成后才运行；P2 不影响两篇 workshop 投稿。

## 3. P0 实验与分析

### W0：observable 与 provenance gate（两篇共用前置条件）

**问题。** exp 123 把 `log_raw_excess_demand=true`，而 exp 126 的 Lévy configs 使用默认 `false`。当前 `score_noise_ablation.py` 却把后者的 post-impact quantity 也命名为 `steady_alphaED`，不能直接比较。

**实施。**

1. 不改写原训练配置；为评分生成独立的 eval-only config，唯一改动是 `price_formation_kwargs.log_raw_excess_demand=true`，或给 `run_large` 增加等价的显式只读 override。
2. 在所有 ED 分析入口强制检查 trajectory 的 `ed_is_raw==1`；否则立即失败，不生成 Pareto 表。现有 `baseline_tdf5` 报告也是 `ed_is_raw=0`，必须和 12 个 Lévy 模型一起重新推理，不能复用旧 ED 数值。
3. 修正 no-shock 语义：无冲击报告写 `shock_step=null`，steady estimator 使用完整的 `[500,T)`，不得像当前脚本一样因默认 `shock_step=3000` 而把无冲击序列任意截成 `[500,3000)`。
4. 用相同 checkpoint 和 seed 做 A/B 回归测试，验证 raw-ED logging 开关不改变 returns、prices 或模型状态，只改变保存的辅助 observable。
5. 每个结果写入 checkpoint SHA256、训练 config SHA256、eval config SHA256、git SHA、seed 列表与 estimator version；字段明确区分 `n_rollouts` 与 `n_checkpoints`，不再把 rollout 数写成 `n_seeds`。
6. 将过期的硬编码 SPS RNG golden test 改成不依赖具体随机样本值的 A/B 等价或不变量测试。

**验收。** 任一参与比较的 trajectory 若 `ed_is_raw!=1`，或 no-shock 报告仍带数值型 `shock_step`，W1 不能汇总；相同 seed 的 logging A/B returns 必须 bitwise 一致。

**资源。** Mac，`ecophys` Conda 环境，约 2–4 CPU 小时；不需要 GPU 或新数据。

### W1：trained-Lévy 稳态尾部与动力学代价（STODY 核心）

**设计。** 沿用 exp 126 的绑定预注册，不更换 alpha、seed 或主要 observables：

- Lévy alpha：`{1.9, 1.7, 1.5, 1.3}`；
- 每个 alpha 三个训练 seed：`{0,1,2}`，共 12 个 checkpoint；
- SPX，无冲击，`T=8000`；
- 每个 checkpoint 32 个独立 rollout；8 cards × 4 realizations/card 只是最快的执行方式，不是实验设计的一部分；
- t(df=5) 的 `concave_d050` 作为 anchor；
- primary：steady raw-ED Hill 与 return Hill；secondary：ACF²(r²)、leverage effect、数值稳定性。

**统计单位。** 对“训练方法”的结论以 checkpoint seed 为单位（每个 alpha 只有 `n=3`），32 个 rollout 只用于降低每个 checkpoint 内的 Monte Carlo 误差。使用 nested bootstrap 或先在 checkpoint 内求均值、再跨 3 seeds 报告均值和区间；不得把 96 条 rollout 当成 96 个独立训练重复。单一 t(df=5) anchor 只能作为参考点，其训练 seed 不确定性必须列为限制。

**结果分级。**

- return/ED tail 随 alpha 下降而系统性变重，同时 ACF² 或 leverage 变差：报告 tail–dynamics Pareto；
- tail 不变或更轻：报告重尾 bath 未能建立重尾稳态，不能写成“证明所有重尾源都会自平均”；
- 部分 alpha 训练/推理发散：完整报告稳定性边界和所有存活点；
- 不论结果，不从 Hill estimator 的约 0.5 下限推断矩不存在。

**实施前修正。** 当前 `scripts/gd1b_score_and_emit.sh` 在 W0 完成前不可直接运行；修正后再做 Mac smoke 和 H20 dry run。

**资源。**

- checkpoint 可恢复：8×H20，预计 2.5–3.5 小时 wall time，约 20–28 active GPU-hours；
- 12 个 checkpoint 必须重训：额外约 2.1–3 小时 wall time。每个训练任务单卡、N=10k、fp32、`chunk_steps=24`；不能把 8 张卡的 HBM 当成一张卡使用；
- HBM：当前 custom-autograd 配置在 exp 126 的实测峰值为 14.19 GiB allocated、14.85 GiB reserved。P0 不要求 96 GB HBM；A100 40/80 GB 和 V100 32 GB 在显存上均有余量，V100 16 GB 过于贴边，不作为生产训练方案。为复现实验协议仍保持 `chunk_steps=24`，不得为了迁就设备改动训练截断长度；
- 数据：推理不需要市场数据。仅在重训时需要与原实验完全相同、带 hash 的 SPX daily 2015–2026 shard；禁止临时下载更新后的数据替代旧快照。

### W2：恢复时间估计器审计（STODY 必须完成，非新定律搜索）

**动机。** 新 dense dose 结果中 SPX 八个剂量的 `tau_recovery` 都等于 350，和旧文稿的约 236 不一致。这首先是分辨率/定义问题，而不是可继续挑选拟合形式的机会。

**分析。** 在现有 5 资产 control 与 `kick6` trajectories 上，预先固定三种定义：

1. alpha(t) 回到 pre-shock 均值一个 standard error 内，并连续保持 3 个窗口的 first-passage time；
2. shock 后 alpha deficit 的单指数拟合时间常数，并报告拟合残差；
3. alpha deficit 曲线的 integrated relaxation time。

对 window size `{200,500,1000}` 做敏感性表。主文只使用 estimator 间方向一致、量级不超过约 2 倍差异的“有限恢复”结论。`dip(dose)` 保持原预注册的三种曲线比较；`tau(dose)` 不再拟合或 headline，即使某个新 estimator 恰好给出好看的曲线也不升级为 confirmatory 结果。

**资源。** 若 H20/GPFS 上原 trajectory 可恢复，则 Mac/CPU 节点分析约 2–4 小时、零 GPU。若原 trajectory 丢失，仅重跑 5 资产的 control 与 `kick6`（24 rollouts/arm，T=8000）：8×H20 约 1.5–2 小时。

### W3：固定长度的 stationarity-aware scoring（Sim2Science 核心）

**模型和样本。**

- `concave_d050`：SPX、NDX、BTCUSDT、Gold、EURUSD，共 5 个 checkpoint；
- baseline family：SPX、BTCUSDT，共 2 个 checkpoint；
- 每个 checkpoint 32 个无冲击 rollout，`T=8000`，所有模型使用同一组 seed；
- 16 条 trajectory 只用于选择 stationarity threshold/W-star，另外 16 条作为冻结后的评价集。

**固定长度原则。** 任何 warm-up 比较都在相同长度 `L=4000` 上评分：比较 `[W,W+L)`，而不是简单从固定 T 中删掉前 W 后用越来越短的样本。候选 W 为 `{0,50,100,200,500,1000,1500,2000,3000}`。

**Stationarity gate。**

1. 将 calibration trajectories 切成长度 500 的不重叠 blocks；
2. 对 model-agnostic delay vector `(r_t, |r_t|, |r_{t+1}|)` 计算 energy distance；尺度只用 calibration split 的晚期数据确定，并用 trajectory-level block bootstrap 保留时间依赖；
3. 用同一模型 `[6000,8000)` 内互不重叠 blocks 之间的 distance 分布定义模型自身的 late-vs-late tolerance；
4. block 起点固定为 `{0,500,1000,...,4000}`。W-star 是不超过 3000、且从该点开始连续 3 个不重叠 blocks 都落入 tolerance 的最早位置；若不存在，则标记为“给定评价窗口内未达到可验证稳态”，不强行评分稳态性质；
5. threshold 和 W-star 在 calibration split 冻结，再在 held-out split 上计算结果。

**主要输出。**

- primary：return Hill 在 `W=0` 与 `W=W-star` 的配对差及 95% CI；
- secondary：11 个 stylized facts 的完整 sensitivity curve；
- 实际 target-distance/通过项数量在 warm-up 前后的变化；
- 模型排序是否翻转。排序翻转不是通过条件；没有翻转也要报告效应大小；
- 每个模型、资产的 W-star，而不是先假定所有模型都应丢弃 50 或 500 steps。

**可宣称范围。** 在 W4 完成前，只能写“EcoMD case study”；不得写“generative models generally”或“standard practice universally fails”。

**资源。** 7 个 checkpoint × 32 rollouts：8×H20 约 1.5–2 小时，或 2×H20 约 6–7 小时。CPU 分析约 4–8 小时。推理不需要市场数据，只需要既有 checkpoints。

### W4：迁移与负对照（Sim2Science claim gate）

#### W4a：neural-SDE 架构变体

- 使用 `experiments/108_neural_sde_scout` 的 `sv_d3_both`，事先固定 seeds `{0,1,2}`，不能根据旧 scoreboard 选最好 seed；
- 每个 checkpoint 32 个无冲击 rollout，`T=8000`，完全复用 W3 protocol；
- 该模型和 EcoMD 共享大量 simulator code，因此只称“第二架构变体”，不称“独立生成器家族”。

checkpoint 可恢复时，8×H20 少于 1 小时；若需重训 3 个模型，单卡并行约 1–1.5 小时，且需要原 SPX daily shard。

#### W4b：GARCH-t 初始化对照

使用 exp 080 已保存的 SPX GARCH-t 参数，不重新拟合。生成四组各 1000 条、T=8000 的 CPU trajectories：

1. long-burn reference：内部先运行 5000 steps，再记录 8000 steps；
2. nominal start：初始方差等于无条件方差，不做内部 burn-in；
3. cold-low：初始方差为无条件方差的 0.1 倍；
4. cold-high：初始方差为无条件方差的 10 倍。

预期不是要求所有组都出现同方向的 Hill 偏差，而是检验 gate 的 specificity：long-burn reference 应基本不触发长 warm-up；错误初始化若产生分布漂移，gate 应检测到。该实验不使用经验 target 做任何阈值调参。

**资源。** Mac 或 H20-4 CPU 节点，8–16 CPU cores、16–32 GB RAM，预计少于 2 小时；不需要 GPU 或新数据。

#### W4 的论文决策规则

- EcoMD、neural-SDE 变体和错误初始化 GARCH 均显示可检测漂移，而 long-burn GARCH 不显示：可写“protocol transfers across two learned dynamical variants and an independent analytic control”；
- 只有 EcoMD 显示：论文降级为 EcoMD case study，保留 GARCH specificity，不做跨模型推广；
- gate 在 long-burn GARCH 上也频繁误报：先修 gate/calibration，不提交方法学主张。

## 4. P1 条件实验

### W5：return self-averaging 的因果拆解

只有在 STODY 仍需要“尾部在 price-formation stage 自平均”这句话时才运行；否则从两篇 workshop 正文中删除该机制，不为已有好看斜率补故事。

**设计。** SPX 与 BTCUSDT；`N={100,1000,10000,100000}`；每格 24 rollouts；三种价格形成条件：

1. 原始配置；
2. `sigma_price=0`，去掉固定 additive price noise；
3. fixed-SNR：对每个 N 调整 `sigma_price`，使 deterministic impact term 与 price-noise 的标准差比固定为 N=10k 基线值。

新增非侵入式日志：raw ED、post-impact ED、`beta_eff*impact(ED)`、additive price-noise draw、Hawkes/excitation contribution。相同 seed 下，打开日志前后的 return 必须 bitwise 一致。

**许可结论。** 只有当 raw ED、post-impact term 与最终 return 的 N 依赖在三种条件下给出一致的成分证据，才能使用“CLT/self-averaging mechanism”。否则只报告经验性的 `alpha_ret(N)` 变化，不给因果标签。

**资源。** 16 个新增 cells，8×H20 预留 6 小时（约 48 GPU-hours）；CPU 分析 4–8 小时；无需新市场数据。此项不得挤占 W1–W4 或论文写作时间。

## 5. P2：高频 L2 数据扩展（明确不在 workshop 关键路径）

两篇 workshop 的可提交版本都不需要采购新数据。即使 L2 数据在截止前到位，也只在 2026-08-05 前完成标准化与 provenance 的情况下进入 appendix；否则留给后续 full paper。

若未来执行，最低字段为：交易所/标的、纳秒或毫秒 timestamp、event type、side、price、size、至少 top-10 depth 或完整 message stream、交易与盘口更新的同步规则。需要 crash windows 与预先固定的 matched calm windows，并保存 vendor、授权、下载日期、原始文件 hash、清洗代码 git SHA。真实 crash 数据只能做最终评价，不能用于选择模型、窗口或阈值。

数据路线沿用 `ecomd/data/buy_order_v2_{en,zh}.md`：Tardis L2、LOBSTER 等属于整个 Paper B/Nature Physics 计划的 $8–12k 数据投入，不应为了这次 workshop 单独仓促采购。L2 清洗主要需要 16–32 CPU cores、64–128 GB RAM 和高速 SSD；通常不需要 H20。

## 6. 总算力与存储预算

### 推荐排程

| 节点 | 工作 | 正常 wall time | 最坏情况 |
|---|---|---:|---:|
| H20-1，8×96 GB | W1 trained-Lévy scoring | 2.5–3.5 h | checkpoint 重训后共 5–6 h |
| H20-2，2×96 GB | W3 EcoMD warm-up trajectories | 6–7 h | 8 h |
| H20-3，2×96 GB | W4a neural-SDE | 2.5–3 h | 重训后 4–5 h |
| Mac/H20-4 CPU | W0、W2、W3/W4 分析与 GARCH | 1 个工作日内 | 2 个工作日 |

若只使用 8-card 节点串行运行：

- **正常路径：预订连续 12 小时。** 约 5 小时 active GPU work，至少 6 小时用于评分、结果完整性检查、失败重跑和打包；预订容量约 96 GPU-hours，预计真正计算约 35–50 GPU-hours。
- **checkpoint 丢失路径：预订连续 18 小时。** 包含 12 个 Lévy 与 3 个 neural-SDE 模型的补训、轨迹重跑和 6–8 小时 evaluation reserve；预订容量约 144 GPU-hours。
- **若执行 W5：** 另加一个 8×H20、6 小时窗口，不和 P0 同批冒险运行。

训练继续使用 N=10k、fp32、`chunk_steps=24`。现有 DDP 是按 realization/config 做数据并行，不是 agent 维度的 tensor parallel；8 张卡不会增加单个训练任务可用的 96 GB HBM。

### 少卡与替代 GPU

P0 的 W1、W3、W4a 合计为 23 个 checkpoint、736 条 `T=8000` rollout。仓库中 H20 的 N=10k 实测约为 168 秒/rollout，因此只计模拟的理想下限为 34.4 GPU-hours。少卡不会改变科学设计，只会增加 wall time；必须保持每个 checkpoint 的 32 条 rollout、相同的显式 seed manifest 和相同 estimator。

| GPU 方案 | P0 核心推理的理想下限 | checkpoint/原 trajectory 均可恢复时建议预订 | 同时需要 15 个补训和 W2 重跑时 |
|---|---:|---:|---:|
| 1×H20 | 34.4 h | 48 h | 72–84 h |
| 2×H20 | 17.2 h | 24–30 h | 40–48 h |
| 4×H20 | 8.6 h | 14–18 h | 24–30 h |
| 8×H20 | 4.3 h | 12 h | 18 h |

补训的 H20 实测增量约为 14.3 GPU-hours：12 个 Lévy checkpoint 各约 62.4 分钟，3 个 neural-SDE checkpoint 各约 36.5 分钟。W2 若丢失原 trajectory，5 资产 control/kick6 重跑另加约 11.2 GPU-hours。上表已为加载、CPU scoring、写盘、完整性检查和失败重跑留出余量；CPU 分析可以和单卡 GPU 队列重叠。

- **单卡 H20：** 是最直接、最稳妥的低卡数方案，P0 全部可做；训练按 config 串行，推理按 rollout/seed block 串行。
- **A100 40/80 GB：** P0 推理和补训在显存上均可行。首次使用前跑一个完整 `T=8000` rollout 和一个 10-iteration 训练 probe，以实测速率替换 H20 的 168 秒/rollout 与训练时长；不能用理论 FLOPS 直接换算。
- **V100 32 GB：** 显存上可行，但需先验证当前 PyTorch/CUDA build 包含 `sm_70`，并预计 wall time 明显长于 H20；优先作为推理或溢出队列。**V100 16 GB** 只比 14.85 GiB 的训练 reserved 峰值多很少，不承担生产补训，推理也先做峰值显存 probe。
- **异构混用：** H20/A100/V100 分别启动单卡 worker，不在一个 `torchrun` job 内混卡。尽量让一个成对比较完整地落在同一 GPU 型号上，并把 GPU 型号、CUDA、PyTorch 写入 manifest。
- **seed 约束：** 当前 `run_large` 使用 `seed_base + rank*1000 + realization_idx`。从 8 卡改为 1 卡时不能简单设置 `n_realizations_per_rank=32` 后宣称 seed 不变；应增加显式 seed manifest，或把原 8 个 rank 的 seed block 逐个排队后再合并。
- **跨 GPU 复现：** 不要求不同 GPU 架构上的长随机轨迹 bitwise 相同；要求固定 checkpoint/seed 后的统计输出在预先设定容差内一致。W0 的 raw-ED logging bitwise A/B 必须在同一 GPU、同一软件环境内完成。

### 存储

- H20/GPFS scratch 至少预留 200 GB，用于 checkpoint 恢复、轨迹与中间日志；
- 新增 scalar trajectories 预计远小于 10 GB，但 checkpoint 体积与 R2 恢复缓存可能更大；
- Git 只提交 config、manifest、分析脚本、汇总 JSON 与最终图，不提交大 checkpoint/trajectory；大文件保存在 R2/GPFS，并在 manifest 中记录 URI 与 SHA256。

## 7. 数据清单

### P0 必需

1. exp 113/114 的 5 资产 `concave_d050` checkpoints；
2. SPX、BTCUSDT baseline-family checkpoints；
3. exp 126 的 12 个 trained-Lévy checkpoints；
4. exp 108 `sv_d3_both` seeds 0、1、2 checkpoints；
5. exp 123/126 已有的汇总 JSON，以及能恢复时的原始 trajectories；
6. 与 checkpoint 对应的 config、git SHA、训练日志与 seed 列表。

这些都是已有模型产物或已有模拟结果，不是新的市场数据采购。

### 仅在补训时必需

- 原实验使用的 yfinance daily snapshot，至少包含 SPX 2015–2026；如补训其他资产，再加入 NDX、BTCUSDT、Gold、EURUSD 的对应 snapshot；
- 必须使用原始快照的明确截止日期和 hash。不能因为目录名写着 `2015-2026_daily` 就默认今天重新下载的数据与原训练集相同；
- 数据从 R2/GPFS 一次性同步到 H20 本地/共享盘，训练热路径不访问公网。

### 不需要

- workshop 核心不需要 Tardis、LOBSTER 或 FirstRate 新采购；
- 不需要用 5 个 crypto crash episodes 调参；它们最多作为弱外部边界说明，并且不能再被描述为证明真实尾部“stationary/universal”。

## 8. 写作与图表修改

### 两篇都必须修正

1. 产生论文结果的模型是 `pairwise_kind: stochastic_mlp` 的 permutation-symmetrized stochastic pair-sampling potential，不是 MACE-lite，也不是 E(3)-equivariant message passing；MACE-lite 是失败架构记录。
2. differentiability 支持 gradient calibration、sensitivity 和潜在 control optimization；scheduled shock interface 本身不是 differentiability 的结果。
3. ED 与 rho 是模拟的 latent-flow proxies，未做 L2 验证前不能称 empirical OFI。
4. `liquidity_drop` 的代码含义是暂时降低 Langevin friction；“market depth/liquidity”是解释性映射，必须明说。
5. `state_kick` 的瞬时 coherence 部分由干预构造；可归功于动力学的是恢复、剂量响应和跨 channel 对照。
6. `price_jump` 会进入 price/return/volatility/global-state feedback；只能说在当前训练模型中 downstream response 弱，不能说 price/news shock 一般无效。
7. alpha 约 0.5 是 estimator floor/censoring，不能用于推断均值或方差不存在。

### STODY 图表（最多 3 张主图）

1. **Fig. 1：** 5 资产 control 与 kick 后 alpha(t)，突出有限恢复与 EURUSD 边界；
2. **Fig. 2：** driver contrast 加 saturating dip-amplitude law；temperature/reduced-friction/kick/price-jump 用操作性名称；
3. **Fig. 3：** trained-Lévy tail–dynamics Pareto；若 W1 为 null，则画完整 null curve 和稳定性边界，不换成别的正结果。

warm-up 只在 Methods 中作为固定 discard/protocol 说明，不使用 Sim2Science 的核心图。

### Sim2Science 图表（2–3 张主图）

1. **Fig. 1：** fixed-length score 随 W 变化，以及 calibration/held-out stationarity gate；
2. **Fig. 2：** 7 个 EcoMD checkpoint 的 warm-up effect 与评分/排序变化；
3. **Fig. 3：** neural-SDE 迁移和 GARCH long-burn/cold-start 对照。

不使用任何 shock-atlas、dose-response 或 real-crash 图，确保与 STODY 实质区分。

## 9. 时间线与停止规则

| 日期 | 交付物 | 停止/转向条件 |
|---|---|---|
| 07-22–07-24 | 本计划冻结；organizer 询问；新 exp 目录、DESIGN、PREREG、manifest 草案 | venue 或双投规则不允许则立即改单投 |
| 07-24–07-25 | W0 代码、单测、Mac smoke、H20 dry run | raw/post ED 不可无侵入区分则 W1 暂停 |
| 07-26–07-28 | W1–W4 GPU/CPU 批次 | 不因中途结果改 seed、alpha、W grid 或主指标 |
| 07-29–08-01 | 汇总、CI、审计、claim-tier 决策 | gate 误报 long-burn GARCH 则 Sim2Science 只保留 case study 或暂停 |
| 08-02–08-10 | 两篇正文重写和独立图表 | 每个 claim 必须能指向一个冻结结果文件 |
| 08-11–08-16 | Reviewer-2 pass：方法、统计单位、措辞、引用、双稿去重 | 若核心图或核心结论仍重复，合并/改单投 |
| 08-17–08-23 | LaTeX、页数、匿名化、补充材料、复现清单 | 不再新增 headline experiment |
| 08-24 | 实验与文字冻结 | 之后只修错误和格式 |
| 08-27 | 内部提交 | 给 08-29 AoE 留缓冲 |

W5 最晚必须在 2026-08-05 前决定是否运行；超过该日期直接删除相应机制句，不再追加实验。L2 数据不设 workshop 前完成目标。

## 10. 实施时应新增的仓库交付物

建议新建 `experiments/127_workshop_revision/`，至少包含：

- `DESIGN.md`：W0–W5 的实现细节；
- `PREREG.md`：只登记尚未观察的新假设和 decision rules，既有 exp 126 结果明确标为 prior evidence；
- `MANIFEST.json`：checkpoint/config/data/代码 hash 与 R2/GPFS URI；
- `RESULTS.md`：所有结果，包括 null、发散、缺失与 deviations；
- 一个 H20 driver：preflight → checkpoint restore → W1/W3/W4a → scoring → integrity checks → package；
- 单独的 CPU analysis entry point；
- 两组互不复用最终图片的 figure scripts。

完成标准不是“两个 PDF 编译成功”，而是：每篇只有一个清晰主张；所有定量句都能追到冻结结果；统计单位正确；两篇核心证据不重叠；在没有 paid L2 的情况下仍能诚实、完整地投稿。
