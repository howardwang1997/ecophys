# EcoPhys / EcoMD — Plan v4：面向 Nature Computational Science 的不变测度校准路线

**日期：** 2026-08-09

**状态：** NCS 路线的当前执行计划

**主目标：** *Nature Computational Science* Article

**建议周期：** 42 周（所有 gate 通过时）；当前两张 V100 足够完成前置 gate，完整项目建议按 gate 扩容

**算力边界：** 当前 2×V100 32 GB；未来可增加更多 GPU/CPU 节点；**本计划不使用、也不依赖 H20**

**数据边界：** 当前数据只是 D0 起点；后续按科学问题和 gate 扩展市场、交易所、时间跨度与数据模态

本文件取代以下文档中与 NCS 投稿直接相关的旧路线：

- `paper_a_ncs_worklist_2026-06-19.md`；
- `paper_a_ncs_viability_routes_2026-06-19.md`；
- `ecomd_model_paper_release_plan_2026-08-09.md` 中仅限“下一篇 NCS 方法论文”的部分。

`plan_v3.md` 保留为 Nature Physics 物理路线的历史计划，不再为本 NCS 项目提供算力、数据或
时间表假设。Sim2Science 论文仍是一次独立的 simulator audit，不是 EcoMD 的首次方法或软件发布。

---

## 1. 执行结论

### 1.1 论文主线

不能把“发布一个从未公开的市场模拟器”本身当作 NCS 贡献，也不能把 exp127 中已经识别出的
初始化瞬态包装成市场物理。NCS 的合理主线是：

> 为有隐状态、随机事件和长混合时间的可微模拟器建立一种可扩展的不变测度校准方法；给出梯度
> 误差或偏差—方差的受控刻画；在 EcoMD 之外的独立系统上验证；随后修复 EcoMD 的长时程语义，
> 通过经过验证的观测算子连接模型与真实 L2 数据，并完成一个冻结的、方法依赖的样本外预测。

这里的“方法依赖”是硬要求：如果标准短时程 BPTT、只拟合观测的模型或传统生成时序基线也能得到
同样的真实数据结果，真实应用不能支撑本论文的主 claim。

### 1.2 预期贡献结构

| 贡献 | 投稿前必须成立的内容 |
|---|---|
| C1：通用方法 | 明确定义不变测度目标和可扩展梯度估计器，而不是只把训练状态跨 chunk 传递 |
| C2：理论/受控误差 | 对线性可解系统给出正确性；对一般遍历系统给出一致性、偏差界、方差或可诊断的误差刻画 |
| C3：跨系统证据 | 在至少两个独立于 EcoMD 的模型族上优于等预算基线，并报告准确度、稳定性、内存和吞吐 |
| C4：EcoMD 修复 | 训练和推理使用同一科学动力学；完整状态、时钟、随机数和 checkpoint 可连续恢复；长时程 fidelity 显著改善 |
| C5：真实应用 | 用经过验证的 L2 观测桥，在冻结样本外数据上得到不能被短时程/观测-only 基线解释的结果 |
| C6：资源 | 首次正式发布 EcoMD 核心代码、训练代码、配置、可公开 checkpoint、评估器和可替代数据 |

### 1.3 明确不主张什么

- 不主张 EcoMD 是“首个可微市场模拟器”或“首个 Langevin 市场模型”；
- 不把模拟器误差称为真实市场物理；
- 不把 EcoMD 当前的 `sum(dpos) / sum(abs(dpos))` 称为真实 L2 OFI；
- 不把“初始化很重要”“persistent state 有用”或“长 rollout 更好”单独当作创新；
- 不在只有一个市场、一个 checkpoint 或 rollout-level 伪重复时声称普适性；
- 不把 stylized-fact 通过数量作为唯一主指标，也不从 early/burn-in 窗口挑最好结果；
- 在 G0–G4 任一硬 gate 失败时，不强行提交 NCS。

### 1.4 诚实概率与退出原则

从当前状态直接完成并被 NCS 接收的联合概率暂估 **7–12%**；若 G0–G4 全部通过，条件接收概率
可上调到约 **20–35%**。这是研究规划判断，不是统计量。NCS 官方定位同时要求显著的计算方法推进
和跨科学问题的价值；Article 目前限制主文约 3,500 词、摘要 150 词、最多 6 个 display items。

退出不是失败掩饰：每个 gate 都对应一个仍可发表且科学边界清楚的退路，见第 12 节。

---

## 2. 当前证据与必须先解决的缺口

### 2.1 已有正面证据

- exp127 完成十次独立训练和 320 条 hash-verified rollout；审计效应在 7/7 可评分市场、6/7
  held-out transfer 市场上稳定，说明仓库已经具备严谨冻结、分层统计和可复现执行能力；
- 2×V100 32 GB 已验证可在不降低 `N=10,000`、fp32 和 `chunk_steps=24` 的情况下完成训练与
  `T=8,000` rollout；
- 仓库已有多市场目标、长时程评分、真实分钟数据、LOBSTER 样本、R2 同步和 provenance 基础。

### 2.2 当前阻断 NCS 的事实

- exp127 的冻结 post-gate stylized-fact fidelity 只有约 1–2/11；有利的重尾主要是初始化瞬态；
- `rollout_chunk` 虽在内部更新 `h_agent` 与 `h_global`，但接口只返回 `h_regime`，训练 chunk
  边界会丢失部分状态；局部 `step_idx` 也会重新从零开始；
- `create_graph=True` 时 jump 使用确定性 drift proxy，推理则抽样 compound-Poisson jump，
  因而 autodiff 开关改变了科学动力学；
- simulator 的其他 mutable buffers、shock schedule、cache、RNG 与 checkpoint 没有统一的
  state-complete 语义；
- 模型内部 `ofi` 是 latent-agent alignment，真实 exp124 OFI 来自盘口深度变化和成交；两者
  之间没有经过验证的 observation operator；
- 初始化/隐状态校准、persistent chains 和稳态灵敏度已有大量先行工作，不能先命名方法再补
  novelty audit。

因此，工作的先后顺序必须是：**新颖性审计 → 语义修复 → 因果 gate → 通用方法 → 跨系统验证
→ 观测桥 → 冻结真实数据实验 → 论文与 release**。

---

## 3. 总体依赖关系与硬 gate

| Gate | 最晚周次 | 进入条件 | 通过标准 | 失败动作 |
|---|---:|---|---|---|
| G0 新颖性 | W2 | 完成系统 prior-art/claim matrix | 找到相对已有稳态灵敏度、persistent-chain、DA 和截断 BPTT 的实质方法差异，并能设计可证伪 benchmark | 停止 NCS 方法 claim；转 simulator audit/benchmark |
| G1 状态与动力学 | W10 | WP1 测试全绿、WP2 screening 完成 | 完整状态连续性和动力学 parity 成立；联合修复在 SPX/BTC 的冻结长时程主指标有一致改善，并通过独立训练 seed 确认 | 不发布正面 EcoMD claim；方法只在别的系统继续或转 TMLR |
| G2 通用方法 | W18 | 新 estimator 实现和受控 benchmark 完成 | 至少两个非 EcoMD 模型族上，相同预算下的梯度/校准误差优于强基线；没有只在一个 mixing regime 生效 | 停止 NCS；保留为专用方法或负结果 |
| G3 观测桥 | W24 | L2 emission/observation layer 与 synthetic recovery 完成 | 能从模型输出同定义的 quote/trade/L2 observable；参数与观测在 synthetic holdout 可恢复；模型 `ofi` 已重命名 | 禁止 model-to-real 验证措辞；真实 L2 另写实证论文 |
| G4 真实样本外 | W32 | 协议预注册、数据封存、基线冻结 | 在至少两个独立资产/交易所或资产类别上，预注册主指标相对短时程和 observation-only 基线显著改善，且 null/surrogate 不复制结论 | 不投 NCS；方法论文转 TMLR/ML venue，真实结果单独报告 |
| G5 投稿与 release | W42 | 全部结果冻结、artifact dry-run | 六图主故事闭合；代码/checkpoint/数据替代物可从干净环境复现；所有 claim 可追到实验 | 延迟投稿，不以 deadline 换完整性 |

G1 的三训练 seed 仅用于 screening。正式论文统计不得停在三个 seed；确认阶段至少二十个独立训练
seed，rollout seeds 作为嵌套重复而不是独立样本。

---

## 4. 工作包总表

所有 GPU 数字均为 **V100-equivalent GPU-hour（V100-eq h）** 的规划区间。未来新增硬件先跑统一
benchmark 得到换算系数，不能按厂商峰值算力直接折算。后续工作包只有在前一 hard gate 通过后
才消耗完整预算，因此这些数字不是现在一次性承诺。

| WP | 工作 | 主要数据 | GPU | CPU / 内存 | 主要交付物 |
|---|---|---|---:|---|---|
| WP0 | 新颖性、定义、预注册框架 | 论文、现有日志与代码 | 0–10 h | 200–400 core-h | prior-art matrix、claim ledger、G0 报告 |
| WP1 | state-complete EcoMD 与动力学 parity | synthetic fixtures、现有 checkpoints | 20–50 h | 200–500 core-h | state API、回归测试、可恢复 checkpoint |
| WP2 | 四臂因果实验与确认 | 当前 SPX/BTC 目标 | 450–850 h | 500–1,200 core-h | 语义缺陷归因、G1 决策报告 |
| WP3 | 不变测度目标与长时程梯度方法 | 可解/受控 synthetic systems | 300–800 h | 500–1,500 core-h | 通用 estimator、理论或误差刻画 |
| WP4 | 跨模型族 benchmark | synthetic + 独立公开 benchmark | 600–1,600 h | 1,000–3,000 core-h | baseline-fair benchmark suite、G2 报告 |
| WP5 | L2 observation bridge | 免费样本、synthetic L2、训练期 L2 | 500–1,500 h | 2,000–8,000 core-h；128–256 GB RAM | event/queue emission、synthetic recovery、G3 报告 |
| WP6 | 多市场冻结样本外应用 | crypto L2、equity L2、minute panel、事件元数据 | 1,000–2,500 h | 3,000–10,000 core-h | 预注册真实实验、G4 报告 |
| WP7 | 鲁棒性、规模化、消融、不确定性 | WP4–WP6 全部冻结数据 | 800–2,500 h | 1,000–4,000 core-h | confirmatory tables、scaling、failure map |
| WP8 | 论文、软件、checkpoint 与复现 | 可公开/可替代数据 | 100–300 h | 500–1,500 core-h | NCS 稿件、supplement、EcoMD v1 release |
| **总计（全部 gate 通过）** |  |  | **约 3,800–10,100 h** | **约 8,900–30,100 core-h** | 完整投稿包 |

上限覆盖 confirmatory rerun 和正常失败重跑，不覆盖无止境调参。每个 WP 在执行前先用 1–3 个
canonical jobs 更新实测预算。

---

## 5. 各工作包的工作、数据和算力需求

### WP0 — 新颖性审计、目标定义和注册框架（W0–W2）

**工作。**

1. 系统审计以下文献簇：稳态 Markov/SDE sensitivity、Poisson-equation/implicit differentiation、
   pathwise/tangent 与 likelihood-ratio estimator、regenerative/debiased estimator、persistent
   contrastive divergence/state bank、data assimilation learned ABM、truncated BPTT 和 differentiable
   simulators；
2. 做 claim matrix：每项已有工作解决什么、假设什么、复杂度如何、是否支持离散 jump、隐状态和
   大规模粒子系统；
3. 在完成审计前只使用“candidate estimator”，不命名新算法；
4. 冻结主目标：对目标数据的统计量向量或分布定义
   \(J(\theta)=D(\mu_\theta,\mu_{\mathrm{data}})\)，其中 \(\mu_\theta\) 是模型不变测度或指定
   非平稳协议下的路径测度；
5. 写 G0 preregistration：benchmark、baselines、评价指标、失败阈值、compute matching 和允许的
   方法修改次数。

**数据。** 只需论文、当前代码、exp127 冻结结果和小型 synthetic trajectories；不采购市场数据。

**算力。** 以 CPU 为主；最多 0–10 V100-eq h 做 estimator 可行性 microbenchmark。

**交付与 gate。** `papers/proposal/ncs_g0_novelty_audit.md`、引用库、claim ledger 和一页 estimator
spec。若无法指出至少一个“算法上实质不同且 benchmark 可检测”的贡献，G0 失败。

### WP1 — state-complete EcoMD 语义（W2–W6）

**工作。**

1. 定义单一 `SimulatorState`，至少包含 agent state、previous state、price state、regime state、
   agent memory、global state、volatility latent、absolute clock、shock protocol state、可变 EMA/
   integrator buffers、neighbor/cache version 和所有 RNG states；
2. `step`、`rollout_chunk`、monolithic rollout 和 checkpoint loader 只消费并返回完整状态；
3. 把 `create_graph` 从科学动力学中解耦：训练和推理必须抽样同一个 jump law。若某个 jump 无法
   pathwise differentiable，则明确采用 score-function、relaxation 或停止该参数的 pathwise claim；
4. 统一 fresh initialization、persistent training、warm-up、detach boundary 与 exact resume；
5. 删除未知 dataset key 静默回退，任何市场名、schema 或 split 错误必须 hard fail；
6. 加入以下回归测试：
   - monolithic 与任意 chunk partition 的轨迹/RNG 一致；
   - `create_graph=True/False` 的分布一致；
   - checkpoint-resume 与 uninterrupted run 一致；
   - state serialization round-trip；
   - CPU/V100 与不同 CUDA 版本的容差协议；
   - long rollout 无 NaN、无 cache 泄漏、absolute clock 不重置。

**数据。** 固定 synthetic fixture、当前 SPX/BTC targets、少量历史 checkpoint；不需要新数据。

**算力。** 20–50 V100-eq h；大部分单元测试在 Mac/CPU，V100 只跑长轨迹 parity 与显存测试。

**交付与 gate。** 完整状态 API、migration loader、测试和行为变更表。这里验证“正确”，不把正确性
修复本身写成 NCS novelty。

### WP2 — 四臂因果 gate：缺陷是否造成长时程失败（W5–W10）

**实验设计。**

| Arm | 状态/绝对时钟连续 | 训练/推理 jump parity | 目的 |
|---|---|---|---|
| A Legacy | 否 | 否 | 冻结历史基线 |
| B State | 是 | 否 | 隔离状态与 clock mismatch |
| C Jump | 否 | 是 | 隔离 jump-law mismatch |
| D Combined | 是 | 是 | 完整修复 |

Screening 使用 4 arms × 3 training seeds × 2 markets（SPX、BTC），每个 checkpoint 16 个固定
rollout seeds、固定 `T=8,000` post-gate 窗口。根据 exp127 实测并留 margin，约 **96 V100-eq h**；
当前 2×V100 在 70% 有效利用率下约 3 天。只有 screening 方向一致才追加正式确认：保留必要 arms，
扩到至少 20 training seeds、每 checkpoint 32 rollouts。若只保留 A/D，预计再用约 350–450
V100-eq h；若 B/C 也必须进入归因确认，上限约 750 h。WP2 总预算因此为约 450–850 h。

**主指标。** 在确认数据前冻结一个连续 invariant/path-distribution distance；11-fact count、Hill、
ACF、Zumbach、early/post-gate/late-reference 作为解释性分量。不能用某个分量改善替代主指标失败。

**数据。** 当前 SPX daily 和 BTC minute 即可；时间 split 不变，crash 事件继续封存。

**统计。** training seed 是实验单位；rollout seed 嵌套于 checkpoint；报告 market × training seed
hierarchy、paired effect 和区间。screening threshold 只决定是否继续，不能作为论文显著性结果。

**G1。** D 必须通过语义测试，并在两个市场的冻结主指标上对 A 有方向一致、实质而非数值噪声的
改善；确认阶段 pooled interval 排除零且没有一个市场出现预注册的严重退化。若 fidelity 仍停在当前
约 1–2/11 且连续指标无改善，EcoMD 正面发布路线停止。

### WP3 — 不变测度匹配与长时程梯度方法（W8–W18）

**工作。**

1. 建立跨 trajectory 的 persistent ensemble/state bank，使初态来自近似 \(\mu_\theta\) 而不是每个
   batch 从人工初态重新开始；
2. 研究 mixing-aware horizon allocation：依据有效样本量、autocorrelation time 或 coupling
   diagnostic 决定 burn-in、unroll 和 refresh，而不是固定 24-step loss；
3. 设计 candidate gradient estimator，组合 truncated pathwise gradient、Poisson/control-variate
   correction、jump 的适当估计和必要时的 debiasing；
4. 对状态库滞后、有限 horizon、finite ensemble 和非平稳参数更新产生的偏差分别做理论或受控
   数值刻画；
5. 提供 fail-visible diagnostics：mixing 未达标、gradient ESS 太低、方差爆炸或 observation
   non-identifiability 时必须报警，而不是返回貌似稳定的 loss；
6. 实现与具体 simulator 解耦的接口，并把 EcoMD 作为 adapter 而不是核心算法特例。

**基线。** fresh-init short BPTT、persistent-state truncated BPTT、long/full BPTT（小系统）、random
warm-start、finite difference/SPSA、likelihood ratio、可行的 Poisson/implicit baseline，以及等 wall-time
和等 simulator-step 两种预算。

**数据。** OU/linear Langevin、非线性双稳态/慢混合系统、带 jump 的受控过程；全部可生成并提供
真值或高精度 reference。

**算力。** 300–800 V100-eq h；理论/数值验证另需 500–1,500 CPU core-h。先在小系统 CPU/单卡，
再将 estimator 规模扩大。

**交付。** 通用 package、算法描述、复杂度表、证明或明确标记的 conjecture、误差实验。算法名字和
“first”类措辞只能在 G0 审计后确定。

### WP4 — 跨模型族验证（W12–W22）

**工作与 benchmark。**

1. **可解系统：** multivariate OU/linear Langevin，比较 invariant moments 和 \(\partial_\theta\)
   真值；
2. **慢混合/稀有跃迁系统：** 双稳态 Langevin、反应网络或同等受控系统，检验 bias–variance 与
   mode coverage；
3. **独立公开模型族 A：** 从 differentiable epidemiology/agent-based、neural SDE 或其他许可证
   合适的 stateful simulator 中选择一个；
4. **独立公开模型族 B：** 选择与 A 动力学和观测结构不同的第二个系统；
5. **EcoMD：** 只作为第三个复杂 application，不承担所有通用性证据。

独立系统的最终选择由 G0 的 prior-art、许可证、可复现性和能否提供长时程 ground truth 决定，
不能为了得到好结果事后换 benchmark。

**指标。** exact/finite-difference gradient relative error、gradient cosine、calibration regret、
invariant-distribution distance、mode coverage、wall time、simulator steps、peak memory 和失败率。

**数据。** 前两类为合成；独立模型使用其公开数据或完全 synthetic protocol。每个外部数据集仍需
provenance、license 和固定版本。

**算力。** 600–1,600 V100-eq h；1,000–3,000 CPU core-h。至少三种 mixing regime、五个 screening
seeds；进入 headline 的 confirmatory cells 至少二十个独立 seeds。

**G2。** 相同计算预算下，candidate method 必须在至少两个非 EcoMD 模型族上显著降低梯度或最终
校准误差，并给出失败区间；若只在 EcoMD 上有效，不投 NCS。

### WP5 — 从 EcoMD 隐状态到真实 L2 的观测桥（W16–W24）

**工作。**

1. 将现有模型变量正式重命名为 `latent_flow_alignment`，保留 backward-compatible migration，
   禁止继续称其为 empirical OFI；
2. 设计显式 marked-event observation layer，输出至少包括 limit add、cancel、market order、side、
   price level、size 和 event time；若不能可信表示 queue，则限制到可验证的 L1/L2 量而不伪装 L3；
3. 从 event stream 重建 best bid/ask、depth、spread、midprice、CKS OFI、trade imbalance、impact
   和 relaxation statistics；模型与真实数据调用同一 evaluator；
4. 在 synthetic L2 上做 simulation-based calibration、parameter recovery、posterior predictive
   checks 和 identifiability stress tests；
5. 观测层只在训练 split 拟合；禁止使用冻结测试事件选择 emission family；
6. 与 observation-only point process、Hawkes/queue-reactive 和简单 empirical resampling 比较，
   防止灵活观测层掩盖错误 latent dynamics。

**数据。** 先用生成的 event streams 和免费 LOBSTER/Tardis 样本做 schema、reconstruction 与
recovery；G2 通过后才解锁付费 L2 的训练 split。真实测试 split 在预注册后保持封存。

**算力。** 500–1,500 V100-eq h 训练 emission/联合模型；2,000–8,000 CPU core-h 做逐事件重建；
推荐 32–64 CPU cores、128–256 GB RAM 的独立数据节点。GPU 不用于可并行的 CSV/Parquet 重建。

**G3。** 同定义 observable、synthetic recovery、holdout calibration 与 observation-only 对照必须
全部通过。若观测桥不可识别，不能把真实 L2 结果写成 EcoMD prediction。

### WP6 — 冻结的真实数据应用（W20–W32）

**主任务候选。** 在预注册前从以下候选中只选一个 primary：预测 held-out 市场日/事件窗口中的
order-flow persistence、liquidity/impact relaxation 或完整短期路径分布。任务必须同时满足：

- 长时程/不变测度校准相对 short-horizon calibration 有理论上的作用路径；
- 可在一般市场日上连续评分，而不是只靠少数著名 crash；
- 训练、validation、test 按时间严格分开，并包含 market/exchange holdout；
- stress/crash 窗口只在最后一次 confirmatory analysis 打开；
- 结果能与真实 forecasting/generative baselines 比，而不是只比较 EcoMD 自己的 ablation。

**核心对照。** 本方法、fresh-init BPTT、persistent-only、最佳生成时序基线、Hawkes/queue-reactive、
observation-only、matched-compute simulator baseline、IID/Student-t、GARCH/SV 和 block-shuffled null。

**数据。** 使用第 6 节 D1–D4 的分层数据。minimum viable confirmatory set 至少包含一个 crypto
L2 域和一个 US-equity L2 域；每个域需要多个资产和足够的市场日，不能把两个 crypto token 当成
两个独立科学领域。

**算力。** 1,000–2,500 V100-eq h；L2 reconstruction/feature store 另需 3,000–10,000 CPU core-h。

**G4。** 在 test 解封前冻结主指标、最小效应、cluster/block bootstrap、缺失数据处理和多重比较
方案。主结论至少在两个独立资产/交易所或资产类别重复，并且 ablation 证明增益来自 WP3 方法而非
更大模型或 observation layer。阈值通过 pilot/power analysis 冻结，不在本计划里事后拍定。

### WP7 — 规模、泛化、消融和不确定性（W28–W38）

**工作。**

- 跨时间、市场、交易所、频率和模型规模的冻结泛化；
- 状态库规模、refresh 频率、unroll horizon、mixing diagnostic、jump estimator、观测层容量消融；
- 参数数量、训练步数、simulator calls 和 wall-time matched 比较；
- training seed、rollout seed、checkpoint、market/exchange、market-day 的分层不确定性；
- 长 rollout 数值稳定性、初始化敏感性、OOD regime 和 missing/corrupt event stress；
- 审计 surrogate 是否也产生 headline effect；若产生，主 claim 被 kill；
- 在不同 GPU 型号上做 numerical/reproducibility check，但不要求 bitwise 跨架构一致。

**数据。** 只使用已经冻结的 WP4–WP6 数据与预先定义的扩展集；不能看到 test 后再购买“更容易
成功”的市场。

**算力。** 800–2,500 V100-eq h；1,000–4,000 CPU core-h。所有确认实验输出完整 run manifest。

### WP8 — NCS 论文与 EcoMD 首次正式 release（W34–W42）

**工作。**

1. 按 NCS Article 限制写约 3,500 词主文、150 词摘要和最多 6 个 display items；
2. 主文只保留一个方法 spine，EcoMD、外部 systems 和真实 L2 都服务于同一个 claim；
3. release EcoMD v1：核心 simulator、训练、inference、evaluation、observation bridge、Hydra configs、
   environment lock、checkpoint、seed manifests、data provenance 和端到端命令；
4. 商业数据不能重分发时，提供 schema-compatible smoke data、生成脚本、checksum manifest 和
   用户自购数据的完整复现入口；
5. 在至少两台干净节点上做 source-to-figure rebuild；当前两台 V100 分别执行一次，未来新增型号
   至少抽一台执行 portability run；
6. 同版本打 git tag、归档 artifact、生成软件/data availability statement。

**六图结构。**

1. 短时程校准问题、state-complete simulator 与方法总图；
2. 可解/慢混合系统上的梯度正确性和误差刻画；
3. 两个独立模型族的等预算 benchmark；
4. EcoMD 四臂因果实验与 post-stationarity 改善；
5. L2 observation bridge 和 synthetic recovery；
6. 冻结真实样本外预测、关键 ablation 与 compute scaling。

**数据与算力。** 只做冻结结果的必要重建；100–300 V100-eq h 和 500–1,500 CPU core-h。

**发布边界。** 若 NCS gate 全通过，这篇论文是 EcoMD 的首次正式方法/软件发布；若 NCS 退出，
同一经过审计的 release 随 fallback archival paper 发布。Sim2Science 的 audit-only artifact 不因本计划
而改变。

---

## 6. 可扩展数据计划

### 6.1 原则

数据规模由假设和独立性决定，不由当前库存决定。另一方面，“可以买更多”不能变成看完结果再挑
市场。每次扩展必须在打开对应 test split 前登记：研究目的、universe、日期、vendor、字段、license、
缺失规则、预期 storage、hash 和停止规则。

商业价格和产品覆盖会变化。下列金额只是规划区间，采购前必须以供应商正式 quote、license 和样本
完整性为准；不把 2026 年 4 月的旧报价当作当前价格。

### 6.2 数据层级

| 层级 | 最小范围 | 可扩展范围 | 用途 | 解锁条件 |
|---|---|---|---|---|
| D0 当前/免费 | SPX、NDX、gold、EURUSD daily；BTC minute；LOBSTER samples；exp127 rollouts | 增加免费指数、FX、crypto bars | 开发、WP1/2、schema test | 立即使用 |
| D1 Crypto L2 core | BTC、ETH；至少 2 个交易所；建议 12 个月；book updates + trades + liquidation/metadata | 5–10 assets、3–5 exchanges、2–3 年、spot + perp | 观测桥、跨交易所 holdout、stress prediction | G2 通过、协议草案冻结 |
| D2 US equity L2 core | 5–10 个流动性/市值分层股票；至少 1 年，目标 1–3 年；L10 或可验证深度 | 20–50 stocks、3–5 年、ETF/小盘/不活跃标的 | 独立资产类别、CKS OFI、impact、calm/stress | G2 通过、样本重建通过 |
| D3 Equity/minute panel | 20–50 stocks/ETF、3–5 年、含 delisted/survivorship 信息 | 全市场或 100+ symbols、更多频率、futures/FX | 跨频率验证、事件上下文、real-only baselines | G1 后可购；G4 前冻结 |
| D4 Event/market metadata | FOMC、earnings、exchange outages、halts、liquidations、calendar/session/timezone | 宏观公告、期货 roll、corporate actions、news timestamps | exogenous protocol、排除时钟和制度混杂 | 与 D1–D3 同期 |
| D5 外部科学 benchmark | 两个公开 stateful simulator 及其固定数据/版本 | 增加反应网络、流体/材料或 epidemiology domain | 证明方法不只适用于金融 | G0 选型后 |
| D6 可选扩展 | futures/FX L2、commodities、更多国家股票 | 多市场长期面板 | reviewer request、真正 universality 检验 | G4 已通过且预注册新问题 |

Tardis 官方目前提供逐笔 order-book snapshots/updates、trades、liquidations 等多交易所 crypto 数据；
FirstRate 官方目前提供分钟/更粗 bars、tick data 和包含 delisted tickers 的股票覆盖；LOBSTER 用于
US equity message/order-book 数据。产品能力只用于选型，最终 schema 和完整性必须通过样本验证。

### 6.3 预算、存储和采购 gate

| 阶段 | 规划采购额 | 规划存储 | 决策 |
|---|---:|---:|---|
| 样本与询价 | $0–1k | <0.5 TB | 只验证 schema、coverage、license、重建速度；不打开未来 test |
| Core confirmatory | 约 $10–25k | 原始压缩数据约 2–10 TB 的容量池 | G2 和样本重建通过后采购 D1–D4 minimum set |
| Expanded confirmatory | 累计约 $25–50k | 可扩到 10–30 TB | 仅 G3/G4 pilot 支持、且扩展 universe 已预注册时采购 |
| Reviewer/后续扩展 | 另行报价与批准 | 按样本实测 | 不预先承诺；不能用于挽救失败的冻结主检验 |

上述 storage 是容量规划，不是对供应商文件大小的断言。采购前用一个交易日或一个月样本估算：
`raw compressed + normalized parquet + derived features + temporary reconstruction`，容量按实测峰值至少
留 2 倍余量。R2 作为 canonical bulk store；计算节点只保留 active shards 和可恢复 cache。

### 6.4 数据治理

- 每份数据有 `PROVENANCE.md`：source、download time、license、原始 hash、preprocess git SHA；
- raw 数据 immutable；normalized/derived 数据按 content hash version；
- 时间戳统一保留原时区和 UTC，显式处理 DST、session、exchange clock drift 和 duplicate events；
- order-book reconstruction 每天从 snapshot 起步并做 sequence-gap、crossed-book、negative-depth test；
- train/validation/test 严格按时间，市场外和交易所外 split 另行保存；
- crash/stress 事件不参与超参数选择；test key 未知、文件缺失或 schema 漂移时 hard fail；
- 商业数据不进 git，不在 release 中违规重分发；公开 compatible synthetic/sample data。

---

## 7. 可扩展算力计划（无 H20）

### 7.1 当前资源与未来架构

- **当前：** 两个独立节点，各 1×V100 32 GB。它们足够完成 WP0–WP2、单卡方法开发和小规模
  benchmark；
- **未来：** 可增加更多 32 GB 或更大显存的 CUDA GPU，以及独立 CPU/RAM 数据节点；不假定
  某个具体型号、互联或云厂商；
- **明确排除：** 未来计划不包含 H20，任何脚本、预算、论文结果和时间表都不能以 H20 可用为前提；
- **并行方式：** 主增益来自 config/seed/market/job-array 并行。不同 GPU 型号分池运行，单个
  `torchrun` job 不混型号；同一 paired comparison 尽量使用同一型号；
- **大模型：** 若未来确实需要多 GPU 单模型，先证明单模型扩大对 claim 必要，再实现 DDP/FSDP；
  不因机器存在而追求更大 `N`。

### 7.2 统一计量

每种新 GPU 运行三类 canonical benchmark：

1. `N=10k, fp32, chunk=24` 的 200-iteration training；
2. 单条 `T=8,000` rollout；
3. WP3 estimator 的固定 toy benchmark。

记录 GPU 型号、显存、driver、CUDA、PyTorch、git SHA、peak memory、samples/s、energy（可得时）和
数值偏差。换算系数以完成同一 canonical job 的 wall time 为准，不用峰值 TFLOPS。

exp127 给出的当前锚点是：十次训练合计 19.90 V100 GPU-h，320 条 rollout 合计 34.51 GPU-h。
WP2 screening 采用更保守的约 96 V100-eq h 预算，包括调度和失败重跑 margin。

### 7.3 扩容触发与推荐规模

| 时点 | 最低可运行资源 | 推荐资源 | 原因 |
|---|---|---|---|
| G0–G1 | 当前 2×V100 | 2×V100 | 先判断科学方向，不为错误方法扩容 |
| G1 后 WP3/4 | 2×V100 可串行 | 8 个 GPU workers | seed/model-family jobs 高度可并行，可将方法循环压到数周 |
| G2/G3 后 WP5/6 | 4 个 GPU + 1 个大内存 CPU 节点 | 8–16 GPU + 32–64 CPU cores、128–256 GB RAM | 观测模型训练与逐事件 L2 reconstruction 分离 |
| G4 后 confirmatory | 8 个 GPU | 16–32 GPU workers | 只在主结果存在后投入多 seed、多市场和 reviewer-grade robustness |

若没有扩容，项目仍可运行，但 full-program GPU 排队时间会成为主要瓶颈；不应通过减少 seeds、缩短
冻结 horizon 或删掉基线来适配两张卡。

### 7.4 理想 GPU wall-time 场景

按全部 gate 通过后的 3,800–10,100 V100-eq h、平均 70% 有效利用率估算：

| 同时可用 GPU workers | 理想计算 wall-time | 解释 |
|---:|---:|---|
| 2 | 约 113–301 天 | 能做，但会把方法迭代和 confirmatory 阶段拖成长串行队列 |
| 8 | 约 28–75 天 | 完整 NCS 项目的最低推荐平均规模 |
| 16 | 约 14–38 天 | 适合 WP6/7 的多市场多 seed 阶段 |
| 32 | 约 7–19 天 | 只在 G4 后短期 burst；不是长期硬需求 |

这是纯 GPU 活跃时间，不是 42 周科研日历；方法依赖、数据采购、CPU reconstruction、分析和写作不
会随 GPU 线性缩短。

### 7.5 调度与可恢复性

- 每个 job 有 immutable Hydra config、seed、data hash、git SHA 和 output manifest；
- 单 GPU worker 从队列取一个完整 cell，checkpoint 每 30 分钟并支持 exact resume；
- paired arms 使用相同 seed manifest 和相同硬件池；
- scheduler 只根据状态文件重试，不覆盖已有成功结果；
- W&B 可选且不得成为运行时依赖；本地 JSONL/manifest 是 canonical record；
- Mac 负责开发、分析和写作；R2 负责数据/结果 transit；GPU 节点不在 hot loop 访问云端；
- CPU reconstruction 与 GPU training 分队列，避免 GPU 等待解压、排序或 Parquet 写入。

---

## 8. 统计、预注册与防自欺协议

### 8.1 实验单位

- simulator 主比较：training seed 为最小独立单位；rollout seeds 嵌套；
- benchmark：system × parameter regime × training seed 分层；
- 真实 L2：market-day/event window 为时间单位，asset/exchange 为 cluster；用 block/bootstrap 或
  hierarchical model 处理序列相关，不能把每个 tick 当独立样本；
- screening 可用 3–5 training seeds；所有 confirmatory headline 至少 20 training seeds，最终数目
  由 pilot 方差和 power analysis 冻结。

### 8.2 冻结顺序

1. 用 synthetic 和 training split 调试 pipeline；
2. 用 validation split 选择模型族、指标和阈值；
3. 生成带 hash 的 preregistration 和 test manifest；
4. 只运行一次 primary test；
5. 任何 test 后修改都标为 exploratory，并使用新的未来数据而不是重复打开同一 test。

### 8.3 必做 null 与 falsification

- IID Student-t、GARCH/SV、block shuffle、time reversal 和 matched-volatility surrogate；
- simulator state permutation、observation-layer-only、parameter-count-matched、compute-matched；
- synthetic known-answer cascade：OU → jump process → slow-mixing nonlinear system → synthetic L2；
- 如果 surrogate 同样产生 headline advantage，或真实结果在 observation-only baseline 下不变，主 claim
  被 falsify；
- 报告全部预注册 markets/cells，包括失败和数据质量排除原因。

---

## 9. 42 周执行时间线

| 周 | 主工作 | 并行工作 | 里程碑 |
|---|---|---|---|
| W0–W2 | WP0 novelty audit、claim ledger、toy spec | 数据供应商样本/许可证询问 | G0 |
| W2–W6 | WP1 complete-state API、jump parity、resume tests | canonical V100 benchmark | state freeze |
| W5–W10 | WP2 四臂 screening + confirmatory extension | 论文方法 skeleton | G1 |
| W8–W18 | WP3 estimator、理论/误差刻画 | WP4 benchmark adapters | G2 method freeze |
| W12–W22 | WP4 两个独立模型族的正式 benchmark | D1–D4 样本重建、quote | G2 |
| W16–W24 | WP5 event/queue observation bridge、synthetic recovery | 真实协议草案 | G3 |
| W20–W32 | 数据采购、ingest、WP6 训练/validation/一次性 test | 论文结果段滚动写作 | G4 |
| W28–W38 | WP7 confirmatory、scaling、robustness | artifact dry-run、figure freeze | result freeze |
| W34–W42 | WP8 主文、Methods、supplement、双节点重建 | 编辑预审材料与 release | G5 / submit |

42 周目标假定：G1 后平均约 8 个 GPU workers，G3/G4 阶段可短期增加到 16 个；若长期只有 2×V100，
应把投稿窗口延长，而不是降低统计标准。

---

## 10. 论文与 artifact 的完成定义

只有以下全部成立才称为“完成 NCS paper”：

- G0–G5 有带日期、hash 和签字式结论的 gate report；
- 主算法的 novelty 已逐项对照 prior art，没有未核实的“first”；
- 至少两个非 EcoMD 系统的 controlled benchmark 和一个 EcoMD complex benchmark；
- EcoMD 的 train/inference law、完整状态、时钟和 checkpoint 语义一致；
- post-stationarity 主指标相对 legacy 与强 baselines 有稳定改善；
- L2 observation operator 通过 synthetic recovery，模型变量与 empirical OFI 不再混名；
- 真实 primary test 在预注册后只打开一次，并在至少两个独立资产/交易所或资产类别上存活；
- 方法 ablation 证明真实增益依赖 WP3，而不是更多参数、更多算力或 observation-only 模型；
- 主文 6 图能完整讲完，不靠 supplement 隐藏主失败；
- EcoMD v1 release 在干净环境可复现，商业数据有合法替代路径；
- 论文中的每个经验 claim 都能定位到 config、seed manifest、结果文件和 figure-building command。

---

## 11. 接下来 14 天的具体动作

1. 完成 G0 prior-art matrix，决定是否存在真正的新 estimator；在此之前不写算法名称和摘要；
2. 建立 `experiments/128_long_horizon_state_parity/` 的冻结 `DESIGN.md`，写明四臂、seeds、主指标和
   stop rule；
3. 先写 `SimulatorState` schema 与六类 parity/resume tests，再改训练逻辑；
4. 用当前两张 V100 重跑 canonical training/rollout benchmark，记录新的 V100-eq anchor；
5. 从免费 LOBSTER/Tardis 样本跑一个交易日的重建，测 CPU、RAM、压缩比和完整性；
6. 向 D1–D3 供应商索取当前 academic/research quote、coverage matrix、license 和 sample，不采购
   confirmatory 数据；
7. 第 14 天召开 G0/G1-preflight review：若 novelty 不成立，停止 WP3；若 state API 设计无法保证
   chunk/monolithic parity，先修设计而不启动训练。

---

## 12. 风险与投稿退路

| 失败点 | 科学含义 | 退路 |
|---|---|---|
| G0：方法不新 | 这是工程修复或已有稳态灵敏度方法的应用 | 写严谨 simulator-audit/benchmark，目标 TMLR 或软件/方法 venue |
| G1：修复不改善长时程 | 已知 mismatch 不是 fidelity ceiling 的主因 | EcoMD 仅作失败案例；不发布正面 model claim |
| G2：只对 EcoMD 有效 | 缺乏 NCS 所需的通用计算推进 | simulator-specific TMLR/ML paper |
| G3：观测桥不可识别 | model latent 与市场数据不能因果对接 | 去掉 model-to-real claim；真实 L2 独立投 microstructure/finance venue |
| G4：真实结果为 null | 方法可能正确，但没有足够广泛的科学应用 | 方法论文转 TMLR/下一届 ML main；完整报告 null |
| 数据许可/完整性失败 | 某供应商无法支撑复现或统计独立性 | 换预先列出的供应商/市场；重新预注册，不沿用已看的 test |
| 算力未扩容 | 不影响科学定义，只影响 wall time | 延长日历、保持 seeds/horizon/baselines，不降规格 |
| NCS desk reject | scope 或影响力不足，不等于方法错误 | 一周内按预先准备版本转 TMLR；下一届合适 ML main 只在双重投稿规则允许时考虑 |

---

## 13. 外部依据（2026-08-09 核验）

- [Nature Computational Science — Aims & Scope](https://www.nature.com/natcomputsci/aims)
- [Nature Computational Science — Content Types](https://www.nature.com/natcomputsci/content)
- [Tardis.dev — crypto tick/L2 datasets](https://tardis.dev/)
- [LOBSTER — limit-order-book data](https://lobsterdata.com/)
- [FirstRate Data — intraday market data](https://firstratedata.com/)

供应商链接证明当前产品类型，不构成价格、许可或完整性保证。采购以当期书面 quote、样本审计和
最终 license 为准。
