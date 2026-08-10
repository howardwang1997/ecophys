# EcoPhys / EcoMD — Plan v4a：可证伪的模拟器审计与首次正式发布

**日期：** 2026-08-10
**状态：** G0 FAIL 后的当前执行路线；先做零采购、低算力验证
**首选投稿：** TMLR；若跨系统证据不足，则缩为软件/模拟方法 venue
**资源边界：** 当前 2×V100 32 GB；未来可扩展 GPU/CPU，但不使用 H20
**数据边界：** 先用仓库现有数据、公开免费样本和 synthetic；任何付费数据由后续 gate 决定

## 1. 论文主线

这篇工作不再声称发明新的不变测度梯度估计器，也不把 EcoMD 的模拟误差写成市场物理。候选主线
改为一个可证伪的计算科学问题：

> 在有隐状态、随机事件和长时程反馈的可微模拟器中，部分状态续接、梯度开关改变随机动力学、
> 以及把 latent proxy 当成外部可观测量，会不会系统性地产生错误的校准与科学结论？建立一个带
> defect injection、exact-resume、observation-semantic 和 held-out controls 的审计协议，量化这些
> 失败何时发生、现有诊断何时抓不住，并以 EcoMD 及至少两个非金融系统验证。

EcoMD 是主要复杂案例和首次正式软件发布，不是普适性证据的唯一来源。若缺少两个独立系统，论文
不得声称通用 simulator audit。

## 2. 暂定贡献与禁止 claim

| 贡献 | 投稿前必须成立 |
|---|---|
| A1：审计 contract | 对 state closure、transition-law parity、RNG/clock continuity、observation semantics、optimizer validity 和 temporal independence 给出机器可检验 contract |
| A2：因果 defect benchmark | 每种缺陷由单因素注入/修复；量化其对梯度、参数恢复、长期统计和结论方向的影响，而不是只列单元测试 |
| A3：跨系统边界 | 至少两个非 EcoMD 的公开 stateful stochastic simulators；报告哪些缺陷普遍、哪些仅 EcoMD 出现 |
| A4：观测桥审计 | 明确 latent、aggregate observable 与 individual-order data 的层级；错误映射必须被 negative control 拒绝 |
| A5：EcoMD v1 release | 核心模型、训练、配置、checkpoint、审计器、synthetic replacement data 和复现实验首次公开 |

禁止声称：

- “首个可微市场模拟器”“首个模拟器审计框架”或“首次稳态校准”，除非新的独立文献审计支持；
- simulator-only 重尾瞬态是真实市场物理；
- `latent_flow_alignment` 是经验 OFI；
- aggregate queue emitter 具有 individual-order、price-time-priority 或交易所撮合语义；
- 一个 checkpoint、一个市场或 rollout 伪重复足以证明普适性。

## 3. 硬 gate

| Gate | 问题 | 通过标准 | 失败动作 |
|---|---|---|---|
| F0 审计新颖性 | 现有 simulator verification / differentiable-program testing 是否已完整覆盖 A1--A4？ | claim matrix 找到可检测的组合缺口；不依赖“EcoMD 首次发布” | 改投纯 EcoMD software/model paper |
| F1 observation semantics | EcoMD state 能否无矛盾地映射到声明的数据层级？ | 冻结字段级 map；price/time/size/sign/identity 均有单位、clock 和 negative controls | 放弃 message/order-level claim，只做 aggregate-bin validation |
| F2 causal defect effect | 三类核心缺陷是否会实质改变结论？ | 独立 seeds 下至少两类缺陷稳定改变预注册主指标；修复消除对应效应；无 lookahead | 仅发布 correctness note/release，不写科学影响 |
| F3 cross-system | 结论是否超出 EcoMD？ | 两个公开非金融系统上同一 contract 和至少一个 defect effect 复现 | TMLR 通用 claim 停止，缩为 domain/software venue |
| F4 external evidence | 真实数据桥是否优于 observation-only/null 且在未见数据存活？ | 冻结协议、独立时间 split、至少两个独立 panel；null/错位/permutation 不复制 | 真实结果完整报告为 null；不影响审计方法但降低影响力 |
| F5 release | 第三方能否从干净环境重现？ | 一键 CPU smoke、V100 reference、公开 checkpoint/替代数据、hash manifest 全通过 | 延迟投稿/发布 |

所有 gate 失败都保留，不放宽阈值追求正结果。

### 3.1 F1 静态审计决定（2026-08-10）

`papers/proposal/ecomd_observation_map_spec_v0.md` 已冻结字段级边界。当前
`EcoMDL2Adapter` 对真实 `aggregate_event` / `individual_order` 映射为 **FAIL**：它强制每个
EcoMD step 一个事件、使用无市场单位的 size、以逐事件新编号冒充 `order_id`，且 emitted book price
与 EcoMD `log_price` 是两个独立过程。它只能作为 `synthetic_fixture`。

免费可恢复路线是 `aggregate_bin` + P3（只比较按物理时间分箱后的收益、成交量与 aggregate marks，
不声称逐订单生成）。Exp142 从干净 implementation `44daf531` 正式 **PASS 9/9**，把该边界变成
code-enforced specification；exp143 又从干净 implementation `2b54170e` 正式 **PASS 10/10**，完成
60 秒 bin、share volume、六 marks、checkpoint、train-only fitting 和 identifiability warning 的
synthetic implementation。因此 **F1 对 aggregate-bin P3 的结构/实现部分 PASS**；逐消息/逐订单仍
FAIL，真实外部预测完全留给 F4，未因 synthetic recovery 获得任何正证据。

## 4. 工作、数据和算力

| WP | 工作 | 当前免费数据 | 后续可扩展数据 | 当前算力 | Gate 后扩展 |
|---|---|---|---|---:|---:|
| A0 | prior-art、claim ledger、protocol threat model | 论文、exp128--140 日志 | 无 | 100--250 CPU core-h | 无 |
| A1 | observation-map spec、schema validator、structural-identifiability tests | synthetic L2、免费 LOBSTER samples | 独立免费日期/市场；之后才考虑付费 L2 | 100--300 CPU core-h，0--10 V100 h | 500--2,000 CPU core-h |
| A2 | analytic defect fixtures：AR/OU、jump/CTMC、bistable | 生成数据 | 无 | 200--600 CPU core-h | 无 |
| A3 | EcoMD 三类 defect-injection factorial | 现有 checkpoint、SPX/BTC targets、冻结 exp127 artifacts | 更多公开/自有低频市场仅作 robustness | 80--200 V100-eq h screening | F2 后 300--800 V100-eq h confirmatory |
| A4 | 两个外部 simulator adapter + benchmark | 公开模型及 synthetic observations | 第三个科学域用于 robustness | 300--1,000 CPU core-h，20--100 V100 h | F3 后 200--600 V100-eq h |
| A5 | unseen real aggregate validation | 未使用的免费样本；当前 real test 不再算 confirmatory | crypto/equity L2、多日期、多交易所；是否购买由 F1--F3 决定 | 500--2,000 CPU core-h | 200--800 V100-eq h（如需联合训练） |
| A6 | paper、artifact、EcoMD v1 release | 全部冻结结果 | license-safe replacement data | 200--500 CPU core-h，10--50 V100 h | 无 |

当前阶段上限是约 **10 V100 h + 1,150 CPU core-h**，两台现有 V100 机器足够，且 CPU 任务可在
其主机上运行。F0--F2 通过前不扩容；F1--F3 通过前不买数据。后续 GPU 数按 V100-equivalent
记录，不按卡名折算，也不以减少 seeds/horizon/baselines 来适配资源。

## 5. 数据需求

### D0：立即可用

- exp127 的独立训练/rollout manifests 与 frozen post-stationarity 结果；
- 当前 SPX/BTC calibration targets 和分钟数据；
- 免费 LOBSTER sample messages/books 及其 provenance；
- synthetic aggregate/dynamic L2、two-state、jump-OU、bistable fixtures；
- 当前 EcoMD checkpoints 和 exact-resume artifacts。

这些数据足以做 F0、F1 的结构审计和 F2 screening，不足以做新的真实 confirmatory claim。

### D1：免费扩展

- 尚未用于 exp138--140 设计或查看结果的公开日期/市场；
- 两个带明确许可证、版本和可生成 ground truth 的非金融 stateful simulators；
- 每个外部系统的解析或高预算 reference、固定 config 和 provenance hash。

若找不到真正未见的免费市场 panel，F4 保持 blocked，不把已打开的 test split 重新命名。

### D2：付费扩展（仅 gate 后）

- 多交易所 crypto L2 与 US-equity L2，覆盖多个独立日期和 market regimes；
- 交易所/供应商字段定义、tick/lot/corporate-action 元数据和可发表许可；
- 购买前先审样本、写 provenance、冻结 train/validation/test 与最小统计功效。

购买规模不由旧的 `$8--12k` 估算约束；按当期 quote 和 F4 所需独立单位决定。付费数据不会修复
F0/F1 的方法或语义失败。

## 6. 核心实验矩阵

### E-A：observation semantic falsification

对同一 latent path 比较三种声明：aggregate-bin、aggregate-message、individual-order。注入错误的
sign、time offset、price scale、event identity 和 observation-only truth。通过条件是 validator 在
进入真实 fit 前拒绝所有超出支持层级的声明，并且正确 aggregate mapping 可 exact reconstruct。

### E-B：state/law defect factorial

五臂沿用 exp128 的概念但缩成 audit 规模：legacy、state-only、law-only、state+law、full semantic
repair。每个 arm 使用相同初态/随机数/预算；主指标是解析梯度误差、长期统计偏差、checkpoint
continuation difference 和结论 sign flip。screening 不超过 5 seeds；任何 paper headline 至少 20
独立训练 seeds。

### E-C：diagnostic false-safe map

在 fast/slow/metastable regimes 中比较 loss plateau、ESS/IACT、split-chain 与真值误差。exp132 的
FAIL 是起点，不修改其阈值。新实验必须用独立 tuning/validation seeds，主结果是 false-safe/false-
alarm surface，而非宣称自动证明 mixing。

### E-D：external simulator replication

两个非金融系统必须使用同一 contract 和 defect vocabulary；可按系统替换 observable，但不得为
每个系统重新定义“通过”。至少一个系统含离散 jump，一个含高维连续状态或长记忆。

### E-E：real-data scoped test

只在 F1--F3 后预注册。主比较是 latent+observation 对 observation-only、continuous-time Hawkes/
queue-reactive、permutation、time-shift 和 surrogate。单位是独立日期/市场，不把 event 或 rollout
当独立科学重复。任何 null 都完整保留。

## 7. 立即执行队列（不买数据、不扩容）

1. **已完成：**冻结 `ecomd_observation_map_spec_v0.md`，并完成现有 adapter 的静态字段审计；
2. **已完成：**exp142 machine-readable contract 正式 9/9 PASS；当前 adapter 仅以
   `synthetic_fixture` 被接受，任何静默 support escalation 均失败；
3. **已完成：**预注册 exp142 的纯 synthetic validator gate；实现与正式运行必须使用后续独立提交；
4. **已完成：**exp143 `aggregate_bin` + P3 measurement object 正式 10/10 PASS；104,160 条生成行
   重构 4,096 bins，integer aggregates exact，train-only corruption firewall exact；
5. 完成 A0 的 simulator-audit prior-art matrix，决定 F0；
6. 只有 F0/F1 仍可行时，才预注册低成本 E-B screening；否则直接整理 EcoMD v1 software release。

## 8. 已有证据如何进入论文

- exp128/133：state completeness、law parity 与 exact resume 的正/负 fixtures；
- exp129/131/132：persistent bias、event-gradient baseline 与 diagnostic false-safe 边界；
- exp130/134--137：schema reconstruction、correct-specification 与 misspecification controls；
- exp138--140：外部 continuous-time baseline、优化收敛失败和阈值不后改的完整负结果；
- exp123/127：simulator-only transient 与真实市场不一致，作为“错误科学解释”的核心案例。

这些结果目前是 development/preflight evidence。论文级因果结论需要新的 fallback preregistration 和
独立 seeds；已查看的真实 test split 永远不能恢复为未见确认集。

## 9. 完成定义

工作完成不是“EcoMD 能跑”或“找到一个正向 likelihood gain”。投稿包必须包含：冻结 claim ledger、
跨系统 preregistered artifacts、全部失败结果、字段级 observation contract、20-seed headline、独立
真实 panel 或明确 null、干净环境 reproduction，以及没有把 simulator artifact 写成市场物理的稿件。
