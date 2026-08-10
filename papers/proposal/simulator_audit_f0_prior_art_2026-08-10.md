# EcoMD simulator-audit F0 先验工作与 claim 审计

**冻结日期：** 2026-08-10  
**审计对象：** `plan_v4a_simulator_audit_release.md` 中 A1--A4 作为一篇 TMLR 通用方法/benchmark
论文的可辩护新颖性  
**决定：** **F0 FAIL；停止通用 simulator-audit/TMLR 主线**  
**保留价值：** exp128--143 继续作为 EcoMD 的软件验证、失败披露和发布质量控制，不作为“首个审计
框架”的论文贡献

## 1. 判定标准

F0 不是问这些检查是否有用，而是问下面两件事能否同时成立：

1. A1--A4 中存在一个超出既有 verification、mutation testing、differentiable-simulator benchmark、
   model-discrepancy 和 observation-aware inference 的**可检测方法缺口**；
2. 该缺口本身足以构成论文贡献，而不是把已知检查打包成一个 EcoMD-specific checklist。

“没有找到一篇论文同时使用我们全部六个字段”不算通过。若各字段及其主要因果结论已有直接先例，
组合必须带来新的定理、指标、算法，或预先定义且非平凡的新经验现象，才能保留通用 claim。

## 2. 直接相关先验工作

| 领域 | 已有直接覆盖 | 对当前 claim 的影响 |
|---|---|---|
| 模型状态、调度、随机性和 observation 文档 | ODD 已要求 entities/state variables/scales、process scheduling、stochasticity、observation、initialization、input 和 submodels；TRACE 进一步覆盖模型设计、测试、分析与适用性记录 | A1 的 contract 字段不是新的科学分类；机器可检验形式最多是工程实现 |
| 端到端验证协议 | Troost et al. 给出覆盖构建、参数推断、不确定性和 simulation 的十二步 context-adequate ABM 验证协议；Jakeman et al. 又给出 SciML V&V 的 16 项建议 | “完整验证流程”或“trustworthy simulator protocol”不能作为首创 |
| 测试先于实现 | Test-Driven Simulation Modelling 明确要求在 simulation model 实现前指定 unit test | preregistered contract/test-first 不是方法新颖性 |
| 错误、artefact 与科学解释 | Galán et al. 已区分实现 error 和 accessory-assumption artefact，并讨论它们如何妨碍正确理解 simulation；Donkin et al. 的跨语言/平台 ABM 复现产生了不同幅度、趋势和最终结论 | “实现细节可翻转科学结论”已有直接 ABM 证据 |
| 缺陷注入与测试充分性 | Adra--McMinn 为 ABM 定义 communication、memory、function 和 environment mutation operators；Ding et al. 将 metamorphic testing、mutation testing 和 adequacy 用于 Monte Carlo scientific software | A2 的单因素 defect injection 与 mutation-kill 设计不是新方法 |
| 随机程序自动测试 | ProbFuzz 对 Edward、Pyro、Stan 生成概率程序/数据并用多种 oracle 找到 67 个新 bug | 以 stochastic fixtures、oracles 和跨系统执行来发现错误已有强先例 |
| 可微 simulator 梯度审计 | Zhong et al. 比较多类 contact simulator gradient 并证明梯度不总正确；Suh et al. 分析长时程/刚性/不连续下 first-order gradient 的 bias--variance；Mosaic 统一接口比较 14 个可微 PDE solver 的成本、梯度、conditioning 和结构兼容性 | optimizer/gradient validity 与跨 solver benchmark 已被直接占据 |
| RNG、并行流与 checkpoint | L'Ecuyer et al. 已系统化 independent streams/substreams；SC23 checkpoint-history 工作已在 MD 上比较 identical-input runs 的中间状态 | RNG continuity/exact resume 是重要工程规范，但不足以单独成为方法贡献 |
| observation operator 与模型误差 | Cvetković et al. 直接研究 parameter-to-observable map 不一致如何造成 misspecified likelihood 和错误估计；OASIS 把 observation model 显式嵌入 simulator 后在 observed-data distribution 上推断 | A4 的 latent-to-observed bridge 与 observation misspecification 不是空白 |
| calibration / validation 隔离 | 预测模型 validation 已明确区分 calibration data 与 independent validation data；ABM 验证协议也把 parameter inference 与 generalization 纳入全流程 | train-only fitting、held-out firewall 和 temporal independence 是必要严谨性，不是新贡献 |
| “诊断正常但结果错误” | 2026 年 PINN preprint 在三个 PDE 中注入参数 misspecification，得到低于/等于 clean baseline 的 loss 但最高 71%/128% solution error，并比较六种检测手段 | E-C 的 false-safe headline 已有非常接近的跨系统实验范式 |
| 错误校准改变决策量 | cycle-accurate simulator 校准工作展示未校准 baseline 给出 10.3x speedup，而校准后为 5.3x；Donkin et al. 已展示 ABM 趋势和结论变化 | “缺陷传播到下游 conclusion sign/decision”本身不是新 endpoint |

## 3. A1--A4 claim matrix

符号：`X` = 直接覆盖；`P` = 组件级覆盖；`--` = 本次检索未找到精确同构结果。`--` 不是新颖性
证明。

| 先验工作 | state / schedule | RNG / resume | law / gradient | observation semantics | calibration isolation | injected defect | false-safe / wrong conclusion | cross-system |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| ODD / TRACE / Troost protocol | X | P | P | X | X | -- | P | P |
| Galán 2009 / Donkin 2017 | X | P | P | P | P | P | X | X |
| TDSM / ABM mutation / Monte Carlo MT | P | P | P | P | P | X | P | P |
| ProbFuzz / stochastic software testing | P | P | X | P | P | X | X | X |
| Zhong / Suh / Mosaic | P | -- | X | P | P | P | X | X |
| L'Ecuyer / checkpoint histories | P | X | -- | -- | -- | P | P | X |
| model discrepancy / observation operator / OASIS | P | -- | P | X | X | P | X | X |
| Silent PINN failures 2026 | P | -- | X | P | P | X | X | X |

逐项决定：

| 候选贡献 | F0 结论 | 理由 |
|---|---|---|
| A1 machine-checkable audit contract | **FAIL as research novelty** | 字段和流程均有成熟先例；schema/validator 是 EcoMD release engineering |
| A2 causal defect benchmark | **FAIL as stated** | domain mutation、scientific-software adequacy 和 injected silent-failure benchmark 均已有直接工作 |
| A3 two-external-system replication | **FAIL as novelty** | 多系统/多 solver/跨平台 replication 是现有 benchmark 的标准证据要求 |
| A4 observation bridge audit | **FAIL as research novelty** | observation operator mismatch、model discrepancy 和 observation-aware SBI 已直接研究 |
| A1--A4 的简单组合 | **FAIL** | 当前没有新定理、算法、可识别性结果或已观察到的非加性规律；组合必要但不足以支持 TMLR 方法 claim |

## 4. 唯一未被精确同构覆盖的残差

本次检索没有找到一篇工作同时对**有隐状态、随机长时反馈且可微**的 simulator 注入 state-closure、
transition-law 和 observation-semantic 三类缺陷，并估计它们经过 calibration 后的交互效应。然而：

- “文献中未出现完全相同的三因素表格”不是贡献；
- 当前仓库尚无预注册的非加性交互、检测充分性或信息论界；
- 若只证明每个已知 defect 会造成已知类型的 bias，审稿人可合理判定为应用性 QA；
- 2026 PINN silent-failure 工作已经非常接近“低 loss、注入 misspecification、多系统、检测方法比较”
  的候选 headline。

因此这项残差记为**未来可重新审计的问题**，不把 F0 改为 AMBER。只有出现下列之一才允许重开：

1. 解析结果：给出单缺陷不可见但组合缺陷可识别/不可识别的条件；
2. 新算法或指标：相对 mutation score、metamorphic relations、SBC、finite difference 和 held-out
   validation 有清晰增益；
3. 预注册的两系统结果：存在非人为调参得到的 composite mutant，它通过上述标准诊断却稳定翻转
   预先定义的科学结论，并且修复对应语义后消失。

在这些条件出现前，不为探索这个残差启动 E-B production、外部 simulator adapter 或 V100 sweep。

## 5. 执行决定

立即生效：

1. 停止 Plan v4a 的通用 TMLR A1--A4 论文路线；
2. 不启动五臂 E-B production，不占用 V100，不购买数据，不扩容；
3. exp128--143 全部保留为 EcoMD 的 verification evidence 和失败披露；
4. exp142/143 的 contract、aggregate-bin P3 与 identifiability warning 进入 EcoMD v1；
5. 下一阶段只做 EcoMD-specific 的状态闭合、训练/推理 law parity、观察层级、文档、许可、CPU
   smoke 和可复现 release；
6. 在 stationary fidelity 与真实 held-out aggregate evidence 修复前，不把 EcoMD 发布描述为经验证的
   market digital twin，也不把 simulator-only transient 描述为市场物理。

这不是停止 EcoMD，而是停止把已有 QA 组合包装成通用方法论文。真正有影响力的后续科学工作仍需
回到真实可观测量、真实 held-out 市场规律和可证伪物理机制。

## 6. 核心一手来源

- Grimm et al., [A standard protocol for describing individual-based and agent-based
  models](https://www.usgs.gov/publications/a-standard-protocol-describing-individual-based-and-agent-based-models),
  *Ecological Modelling* 198 (2006).
- Grimm et al., [The ODD protocol: a review and first
  update](https://www.sciencedirect.com/science/article/abs/pii/S030438001000414X),
  *Ecological Modelling* 221 (2010).
- Grimm et al., [Towards better modelling and decision support: documenting model development, testing, and
  analysis using TRACE](https://research.wur.nl/en/publications/towards-better-modelling-and-decision-support-documenting-model-d/),
  *Ecological Modelling* 280 (2014).
- Troost et al., [How to keep it adequate: a protocol for ensuring validity in agent-based
  simulation](https://cgspace.cgiar.org/items/3ac81c3b-df45-4e94-aeba-45e00fb13b4b),
  *Environmental Modelling & Software* 159 (2023).
- Onggo and Karatas, [Test-driven simulation
  modelling](https://eprints.lancs.ac.uk/id/eprint/78979), *European Journal of Operational Research* 254
  (2016).
- Galán et al., [Errors and Artefacts in Agent-Based
  Modelling](https://www.jasss.org/12/1/1.html), *JASSS* 12 (2009).
- Donkin et al., [Replicating complex agent based models, a formidable
  task](https://www.sciencedirect.com/science/article/pii/S1364815216310088), *Environmental Modelling &
  Software* 92 (2017).
- Adra and McMinn, [Mutation Operators for Agent-Based
  Models](https://philmcminn.com/publications/adra2010.pdf), ICSTW (2010).
- Ding et al., [Application of metamorphic testing monitored by test adequacy in a Monte Carlo simulation
  program](https://bmlaser.physics.ecu.edu/literature/2017-9_metamorphic%20testing%20monitored%20by%20test%20adequacy%20in%20a%20MC%20program.pdf),
  *Software Quality Journal* 25 (2017).
- Dutta et al., [Testing Probabilistic Programming
  Systems](https://misailo.web.engr.illinois.edu/papers/probfuzz-fse18.pdf), ESEC/FSE (2018).
- Zhong et al., [Differentiable Physics Simulations with Contacts: Do They Have Correct
  Gradients?](https://arxiv.org/abs/2207.05060), AI4Science at ICML (2022).
- Suh et al., [Do Differentiable Simulators Give Better Policy
  Gradients?](https://proceedings.mlr.press/v162/suh22b.html), ICML (2022).
- Rehmann et al., [Mosaic: A Benchmark Suite for Differentiable Physics
  Solvers](https://arxiv.org/abs/2606.27895), preprint (2026).
- Jakeman et al., [Verification and Validation for Trustworthy Scientific Machine
  Learning](https://arxiv.org/abs/2502.15496), preprint (2025).
- L'Ecuyer et al., [An Object-Oriented Random-Number Package with Many Long Streams and
  Substreams](https://ideas.repec.org/a/inm/oropre/v50y2002i6p1073-1075.html), *Operations Research* 50
  (2002).
- Assogba et al., [Asynchronous Multi-Level Checkpointing: An Enabler of Reproducibility using Checkpoint
  History Analytics](https://sc23.supercomputing.org/proceedings/workshops/workshop_pages/ws_scsc104.html),
  SuperCheck-SC23 (2023).
- Cvetković et al., [Choosing Observation Operators to Mitigate Model Error in Bayesian Inverse
  Problems](https://epubs.siam.org/doi/10.1137/23M1602140), *SIAM/ASA Journal on Uncertainty
  Quantification* (2024).
- Farahi et al., [OASIS: Observation-Aware Simulation-Based Inference via Distributional
  Matching](https://arxiv.org/abs/2606.22572), preprint (2026).
- McShannon and Dietrich, [Silent Failures in Physics-Informed Neural Networks: Parameter Poisoning and the
  Limits of Loss-Based Validation](https://arxiv.org/abs/2606.25151), preprint (2026).
- Asri et al., [Simulator Calibration for Accelerator-Rich Architecture
  Studies](https://slam.ece.utexas.edu/pubs/samos16.Marss-x86-i7.pdf), SAMOS (2016).
- Morrison et al., [Data partition methodology for validation of predictive
  models](https://www.sciencedirect.com/science/article/pii/S0898122113005476), *Computers & Mathematics
  with Applications* 66 (2013).

## 7. 审计边界

检索截至 2026-08-10，覆盖 ABM V&V、scientific-software testing、differentiable simulation、SBI、
inverse problems、RNG/checkpoint 和近期 2026 preprints。它不是形式化的 exhaustive systematic
review；因此本文避免“绝不存在相关工作”的反向 claim。F0 FAIL 只需要更弱且已经满足的结论：现有
证据足以推翻当前 A1--A4 的新颖性主张，而当前没有足以抵消这些先例的新方法或新结果。
