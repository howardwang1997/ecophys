# EcoPhys: 分子动力学视角下的金融市场群体动力学研究

> ⚠️ **SUPERSEDED**: This plan has been replaced by `plan_v3.md` (2026-04-24,
> Path C commitment — Nature Physics flagship with $8–12k high-freq data buy-in
> and 58-week timeline). Kept for historical reference.
> **Do not use this document for current planning decisions.**

**Plan version**: v2 (2026-04-23, 同日修订：$50k 数据预算 + H20 内网约束 + M3→arXiv 确认)
**Author**: Claude (以 AI 学术研究者 + critical reviewer 视角)
**Working directory**: `/Users/howardwang/Desktop/playground/ecophys`
**Compute budget**: 4×H20 GPU (96GB HBM each, ~148 TFLOPS FP16, NVLink) — 异地机
**Time budget**: 6–18 个月全职
**Venue target**: 系列论文（NeurIPS/ICML main + PRL/Nat Phys 赌注 + QF/JEDC 可选）

---

## TL;DR（4 分钟阅读版）

- **我们要建造什么**：EcoMD —— 把交易者建模为特征空间中的"粒子"，用可微 Langevin 动力学 + 学习的等变相互作用势（MACE-lite）端到端从真实市场数据中学习出来的大规模仿真器。
- **三支柱贡献**：C1 方法（首个可微 MD-style 金融仿真器）+ C2 物理（非平衡热力学/市场熵产生率/有效温度）+ C3 应用（crash 事前预测 + optimal execution）。
- **关键批判（我作为独立 reviewer 的诚实判断）**：
  - "一篇旗舰直冲 Nature Physics" 的概率 **≈ 3–8%**，失败代价过高。详细推演见 §3.1.1。
  - **推荐路径**：做研究时按 Nature Physics 标准设计实验，但以**系列论文**发表（Paper A → NeurIPS/ICML main；Paper B → PRL 为主 / 如 M4 结果 exceptional 再赌 Nature Physics；Paper C → QF/JEDC 可选）。
- **算力结论**：4×H20 足以在 5–10 天跑完主实验（~10⁵ agents × 5×10³ 步 × 10³ 梯度迭代）。不能走 TradeFM 那种 foundation model 的纯规模路线；我们的 niche 是"可微 + 物理可解释"。
- **对朴素 MD 类比的主要批判**（必须在论文正面回答）：(a) 观测不到单个交易者 → agent 定义在订单流隐空间；(b) 非平稳 → 时变势 + regime；(c) 交易者优化效用不是极小能量 → 势函数分解为保守+耗散两部分。详见 §1.3。
- **关键里程碑**：Wk 26 M3（EcoMD v1 超越 baselines，**立即 arXiv 预印本 + Paper A draft**）→ Wk 33 M4（≥3 次真实 crash 事前预测，决定是否值得赌 Nature Physics）→ Wk 46 M6（Paper A 正式投稿会议）。
- **下一步**：用户批准 plan → 建立项目骨架 + 长期记忆 → Phase 0 开始。

## v2 修订摘要（2026-04-23 同日）

1. **数据预算从 ~$300 上调到 ≤ $50k**：Tier 1 全部 go，Tier 2 全部 go，加 Tier 1.5（国际股指、跨市场普适性数据），显著强化 C2 Nature Physics 赌注的概率（从 3–8% → 5–12%）。详见 §5。
2. **H20 在公司内网且网络不稳**：数据流从"S3 为中心"改为"Mac 处理 + 大批量打包 + 单向灌给 H20"。推荐 Cloudflare R2（零 egress）替代 S3。H20 本地保留大型数据缓存，避免反复传输。详见 §7.3。
3. **M3 完成即发 arXiv**：优先权保护策略确立。Paper A 的 scope 需要在 Phase 3 就定稿——C2（非平衡热力学）成果**不在 M3 arXiv 里**，保到 Paper B 单独发；避免 C2 一次性曝光。详见 §4 Phase 6 和 §6 修订。

---

## 1. Context — 为什么做这个研究

### 1.1 问题陈述
把金融市场的每个参与者类比为 MD 中的原子，把市场的波动类比为统计物理性质（温度、相变、输运系数）。目标是构建**可微、大规模、物理启发**的市场仿真器，既能再现 stylized facts、又能揭示非平衡统计力学规律、还能预测极端事件。

### 1.2 Sanity check — 为什么值得做
调研后发现关键空白：
- **Tóth-Lux-Sornette (PRL 2018)** 已经手工推导了 HFT 的 Boltzmann 方程 —— 但**没有人用 ML 力场（MACE/NequIP 风格）去学习交易者之间的相互作用势**。物理社区和 ML force-field 社区完全分离。
- **Chopra et al. (2022)** 的可微 ABM 只做到 ~10³–10⁴ agents，局限于流行病学，**没人在金融市场做端到端可微的粒子仿真器**。
- **Maskawa (Entropy 2025, 27(4), 435)** 首次实证验证了股市波动率级联过程满足积分涨落定理（~5% 误差），**但没人把涨落定理作为学习目标或评估指标嵌入仿真器**。
- **TradeFM / TRADES (2025)** 等生成模型不可微、不可策略优化、无可解释的"相互作用力"。

这三条空白恰好对应本研究的三个贡献支柱（方法/物理/预测），且相互强化。

### 1.3 对朴素 MD 类比的批判性检视（必须在论文中正面处理）
| MD 中的假设 | 金融市场中的现实 | 我们的应对 |
|---|---|---|
| 所有粒子位置、速度可观测 | **我们看不到单个交易者**，只看到聚合订单流 | 把 agent 定义在**订单流的隐空间**（而不是真实交易者个体），用深度集合（DeepSets）+ VAE 编码观测为 agent 状态 |
| 粒子遵循时间不变的力定律 | 市场非平稳，策略演化、制度变迁 | 加入**时变相互作用势** V(s_i, s_j, t\|regime)，并显式建模 regime-switching |
| 原子追求能量极小 | 交易者优化财富/效用 | 把势函数分解为**耗散部分（交易成本、流动性消耗）+ 保守部分（持仓偏好、风险厌恶）**，与非平衡热力学一致 |
| 相互作用满足空间局域性 | 交易者通过订单簿**全局耦合** | 使用 MACE-style **特征空间局域性**（在策略/资金/暴露度的 k 近邻内定义相互作用），而非物理空间 |

这张表会在论文 Related Work + Discussion 中作为核心批判出现，既是 limitation 也是贡献点。

---

## 2. 核心贡献（论文叙事）

### 2.1 三个独立可拆又相互强化的贡献

**C1（方法）**：**首个可微、等变、基于学习势函数的大规模金融市场粒子仿真器**（代号 **EcoMD**）。
- 从订单流/成交数据中端到端学习交易者相互作用势（V_pairwise + V_external）
- 使用 MACE-lite 等变 GNN 架构，在 agent 特征空间而非物理空间定义局域性
- 支持 10⁵ agents × 5×10³ 时间步 × 10³ 梯度迭代，在 4×H20 上 5–10 天完成

**C2（物理/理论）**：**用 EcoMD 严格检验非平衡统计力学定律**，得到市场有效温度 T(t)、熵产生率 σ(t)，作为**普适**的危机前兆。
- 学出的仿真器 → 显式提取 drift/diffusion → 代入 Jarzynski/Crooks 涨落定理
- 关键命题：熵产生率在相变（crash）前系统性增大，是**模型无关**的 early warning signal
- 跨市场（美股 + 加密）验证普适性

**C3（预测/应用）**：在真实 2010 Flash Crash / 2020 COVID / 2022 Luna-FTX 等事件上，**用 C1+C2 构建的指标做事前预测**，对比 LPPL、VIX、put-call ratio 等基线。

### 2.2 为什么这个叙事可能冲顶
- **三支柱互锁**：方法新 → 理论可验证 → 预测可实证。任何一支柱单独都不够强，但三者合起来构成"新物理发现"级别的故事。
- **跨领域**：ML(方法) × Physics(理论) × Finance(实证)。天然匹配 *Nature Physics / PNAS / NeurIPS Oral* 的跨学科偏好。
- **可证伪**：涨落定理 + 涌现温度 是明确可证伪的预测，而不是 post-hoc 拟合。

---

## 3. 批判性可行性评估（**我对顶会顶刊可行性的诚实判断**）

### 3.1 Venue 分层 —— 给用户的现实预期

| 等级 | 代表 venue | 本研究能否进入 | 需要达到的条件 | 预估概率 |
|---|---|---|---|---|
| **梦幻** | *Nature Physics / PNAS* | 只有 C2 跑出来 + 在≥3 次真实 crash 上做出**事前**预测（时间锁定、不作弊），才可能 | 必须有可被其他团队复现的**新物理量**（如 market temperature），且显著优于 LPPL 等基线 | 见 §3.1.1 |
| **顶会主会** | *NeurIPS / ICML / ICLR main* | C1 做扎实（新方法+新架构+强实证）+ C3 的一个任务 | 方法本身要有 ML 社区能接受的理论贡献（identifiability、收敛性、样本复杂度） | 30–50% |
| **顶刊高水平** | *PRE / Phys Rev X / JFE / QF* | C1+C2 其中一个做扎实 | 物理口：新现象+理论；金融口：实证说服力+经济解释 | 60–75% |
| **高产出兜底** | *Physica A / JEDC / ICAIF / NeurIPS-W* | 单独 C1 或单独 C3 | 方法 OK、实证 OK 即可 | >85% |

### 3.1.1 **关键批判评估：旗舰大论文能否到 Nature Physics 级别？**

你问了一个极其重要的问题。我作为你的"独立研究伙伴"必须诚实给你数字，而不是放卫星。

**Nature Physics 过去 5 年 (2021–2026) 与经济/金融相关的文章数量**：据我调研，**个位数**，且多为"复杂系统"或"城市/集体行为"角度。**纯金融市场建模的文章接近 0**。相比之下 *Physical Review E / Physica A* 每年各接收几十篇 econophysics。

**Nature Physics 对一篇论文的硬门槛**（从近年录用模式反推）：
1. **新物理现象**（不是新方法、不是新模型）—— 必须发现"过去不知道的东西"
2. **跨领域普适性** —— 不能只是金融现象，要和其他非平衡系统（颗粒物质、活性物质、生态、大脑临界性）建立定量的**相同标度**或**相同机理**的联系
3. **可证伪性 + 事前预测** —— 不能是事后拟合；必须在 hold-out 真实事件上给出清晰的数量预测
4. **理论深度 + 简单表述** —— 需要一句话能讲清楚的"新定律"或"新不等式"

**我对本研究达到这 4 条的概率评估**：

| 门槛 | 达到难度 | 我的概率估计 | 最大风险 |
|---|---|---|---|
| 1. 新物理现象 | 高 | 20–30% | 大概率只是"学出了一个 σ(t)"，但不是真正的新物理量（reviewer 会说"这只是高阶 GARCH"） |
| 2. 跨领域普适性 | 很高 | 10–15% | 需要证明 market temperature 和诸如 active matter 中的 effective temperature 满足**相同**标度 —— 这是个硬活，需要独立的活性物质数据对比 |
| 3. 事前预测 crash | 中高 | 25–35% | 历史上所有 crash 预测工作都在这里翻车（LPPL 的复现性争议至今）；样本数（~10 次 major crash）太小做不出 p<0.001 |
| 4. 一句话定律 | 中 | 40% | 如果我们能写出 "σ(t) ≥ α·|∇ξ|² 对所有市场成立"，那就成了；但这种简洁不等式通常需要数年 |

**联合概率**（独立性假设偏乐观）：**约 3–8%** 冲上 Nature Physics（v1 估计）。

**v2 更新（$50k 预算后）**：有钱买国际股指 + Tardis L2 大幅强化门槛 #2（跨领域普适性）。
- 门槛 #2 从 10–15% → **20–30%**（5 个独立市场 + 加密 L2 跨交易所普适性检验）
- 门槛 #3 从 25–35% → **30–40%**（更多 crash 事件覆盖 + cleaner data，提高统计显著性）
- 联合概率：**约 5–12%**。
- 质变是"从值得做"上升到"小概率但可盘算"——但仍然**不值得 all-in 赌 flagship**。系列论文策略依旧最优；Nature Physics 作为 Paper B 的第一次投稿尝试。

**我的判断**：一篇"旗舰一次到位 Nature Physics"**不是好的 bet**。原因：
- 期望收益率（概率 × 收益）vs 系列论文策略差不多，但**失败时一无所获**（9-13 个月后只有一份未接收的 draft）
- Nature Physics 即便拒稿，也没有"主动降级到 PRE"的快速通道，意味着重投要再多花 4-6 个月
- 独立研究没有共同作者背书，Nature Physics 更看重机构/团队 signal

**强烈推荐的策略**：**"以 Nature Physics 的标准做研究，但以系列论文的方式发表"**（等价于我最初推荐的方案）。
1. Paper A（方法学，目标 NeurIPS/ICML main，8–10 个月）：C1 + C3 的一个应用任务。即便 C2 还不成熟也能投。
2. Paper B（物理学，目标 **PRL → 如果 reviewer 反馈 exceptional 才转投 Nature Physics**，12–16 个月）：C2 深入 + 跨市场普适性。
3. Paper C（金融学，目标 JFE/QF/JEDC，可选，14–18 个月）：C3 的更深入经济解释版。

**极小概率的 "all-in" 替代方案**：如果你坚持赌 Nature Physics，需要额外做两件事：(a) 在 Phase 4 前期就把 "跨非平衡系统普适性" 作为硬约束设计实验；(b) 设置明确的 go/no-go 检查点（Wk 33 的 M4 如果没有跨市场显著 lead time，立即切到系列论文策略）。

**最终我的建议**：采用**系列论文策略**，但 Paper B 以 PRL 标准撰写，完成后如果结果够 exceptional，先投 Nature Physics 赌一次，15 天 desk reject 后快速转 PRL。这样既有上限的追求，又不失保底。

---

### 3.2 算力可行性（4×H20）
- **单机总 HBM 384 GB**，可以训练 ~500M–1B 参数模型 bfloat16 + gradient checkpointing
- **可微仿真主要瓶颈**：T 步 BPTT 的激活内存 ≈ N × d_state × T × 2（bf16） + 等变层激活
  - 10⁵ agents × d=64 × T=5000 × 2B ≈ 64 GB（无 ckpt），用 ckpt 降到 ~20 GB → 可行
  - 10⁶ agents 会 OOM，需要分层/稀疏交互 —— 作为 stretch goal
- **训练时长估算**：
  - Phase 2 主实验：~10⁵ agents × 5×10³ steps × 10³ iters ≈ **5–10 天 on 4×H20**
  - Phase 3 扩展实验（多市场、多 regime）：每组 ~3–5 天
- **不能做**：与 TradeFM (524M params, billions of events) 比拼 pure scale。我们走"可微 + 物理可解释"路线。

### 3.3 时间可行性（vibe coding 速度）
| 阶段 | 内容 | 日历周数 |
|---|---|---|
| Phase 0 | 基础设施、数据管道、文献深读 | 3–4 周 |
| Phase 1 | 复现 stylized facts + baseline ABM (ABIDES / Lux-Marchesi) | 4–6 周 |
| Phase 2 | EcoMD v0（核心可微仿真器） | 6–8 周 |
| Phase 3 | 学习势函数 + 等变架构（C1 完整） | 6–8 周 |
| Phase 4 | 非平衡热力学实验（C2） | 5–7 周 |
| Phase 5 | Crash 预测 + 基线比较（C3） | 4–6 周 |
| Phase 6 | 第一篇论文写作 + 投稿 | 4–6 周 |
| 机动 | Bug / 重做 / 失败重启 | 4–8 周 |
| **总计** | | **36–53 周 (9–13 个月)** |

在 6–18 个月窗口内现实可达。18 个月上限允许追加 C2 的深入版本和可能的期刊修改周期。

---

## 4. 研究程序 — 按阶段拆解

### Phase 0（第 1–4 周）— 基础设施与深读
- **代码仓库**：`ecophys/`，Python + PyTorch 2.3+，可选 JAX 用于部分物理模块
  - 目录：`ecomd/` (core), `data/` (ingestion), `stylized_facts/` (eval), `experiments/`, `notebooks/`, `logs/`, `papers/`, `references/`
- **数据管道（便宜优先）**：
  - 美股日频：`yfinance` → S&P 500 历史
  - 美股分钟：Databento $125 试用额度 + Kaggle/第一批 FirstRate 样本
  - 加密高频：`data.binance.vision` 免费 tick/kline 下载（BTC, ETH, SOL 主流品种 1 年 ≈ 50–200 GB zstd）
  - LOBSTER 免费样本（NASDAQ 10 只股票微观结构）
- **文献深读**（必读 15 篇 + 精读 5 篇）：
  - Must read: Cont 2001, Bouchaud & Potters 2003, Tóth-Lux-Sornette 2018, Chopra 2022, MACE (Batatia 2022), Allegro (Musaelian 2023), ABIDES, Maskawa 2025 (Entropy 27(4), 435), Farmer-Patelli-Zovko 2005, Yakovenko-Rosser 2009, Sornette LPPL 回顾
  - 精读：MACE 复现、Chopra GradABM 源码、ABIDES 源码

**Milestone M0**: 仓库骨架 + 数据管道跑通 + 文献精读笔记 5 篇。

### Phase 1（第 5–10 周）— Stylized facts 复现 + baseline ABM
- 实现 **Cont 2001 canonical 11 stylized facts evaluation suite**（可作为独立 PyPI 包副产品）：
  - Fat tails（Hill/Pickands 尾指数）、volatility clustering（ACF² + GARCH fit）、leverage、long memory（Hurst via DFA）、aggregational Gaussianity、gain/loss asymmetry、volume-volatility、bid-ask bounce 等
  - 度量套件：Wasserstein / MMD / energy distance / ACF-MSE / moment matching
- 实现 2 个 baseline：
  - **ABIDES-lite**：一个简化的 order-book 事件驱动仿真器（可不完全可微）
  - **Lux-Marchesi (1999)**：经典两类 agent 模型（fundamentalist + chartist），PyTorch 实现
- 在 SPX + BTC 1 年数据上跑 baselines，记录所有 stylized facts 指标

**Milestone M1**: 所有 baseline 可跑 + 11 项 stylized facts 全部实现 + 真实数据的 reference 值表（论文的 Table 1）。

### Phase 2（第 11–18 周）— EcoMD v0：可微仿真器骨架（**C2 早期核心约束**）
- **Agent 状态**：d=32–64 维隐向量（资金、持仓、风险偏好、信息状态）
- **动力学**：显式 Langevin 形式（**为 C2 埋下结构**）
  - s_i^{t+1} = s_i^t − γ ∇_i U_θ(s, context) Δt + √(2 k_B T_θ(t) γ Δt) · ε
  - U_θ 分解为 V_pairwise + V_external + V_dissipation（保留可识别的保守/耗散项）
  - T_θ(t) 是显式可学的有效温度字段；γ 是可学的 friction
- **C2 早期设计约束**（Phase 4 不用重写）：
  - 所有动力学更新保留"力 × 速度"的可计算表示，以便任意时刻可抽取功、热、熵产生率
  - 初次训练就保存 (force_t, velocity_t, state_t) 三元组，供 Phase 4 跑涨落定理分析
  - 非保守力与保守力分开记账（这是 Jarzynski/Crooks 类实验的必要条件）
- **可微性技巧**：
  - 离散动作（buy/sell/hold）用 Gumbel-softmax 松弛
  - 长 BPTT 用 activation checkpointing（参考 Gruslys 2016，降 60% 内存）
  - 关键数值稳定性：gradient clipping, layer norm, 预 warm-up 训练
- **训练目标 v0**：让仿真轨迹的 stylized facts 匹配真实数据（Wasserstein / MMD loss）+ 涨落定理一致性辅助损失（权重小，起正则作用）
- **规模测试**：10³ → 10⁴ → 10⁵ agents 逐级 scale，记录 speed / memory / gradient norm

**Milestone M2**: EcoMD v0 可训练，10⁴ agents 能复现 ≥6 个 stylized facts（初步），且力/速度/状态 log 结构可被 Phase 4 直接消费。

### Phase 3（第 19–26 周）— 学习相互作用势 + 等变架构（C1 完整）
- 把 μ_θ, σ_θ 替换为 **MACE-lite 等变 GNN**：
  - 在 agent 特征空间做 k-NN 图（k=16–32）
  - 节点特征：agent 状态 s_i
  - 边特征：|s_i − s_j|、持仓差、策略相似度
  - 消息传递使用 SO(3)-无关的**高阶不变多项式特征**（降级版 MACE：不做真正 SO(3) 等变，但保持置换不变）
- **势函数分解**（符合批判表 1.3）：
  - V_pairwise(s_i, s_j, t): 学习的
  - V_external(s_i, P_t, σ_t): 学习的（agent 对市场整体状态的响应）
  - V_dissipation: 显式建模（流动性消耗、手续费）
- **可识别性策略**（正面回应 identifiability 担忧）：
  - 结构化先验：agent 分 K 类（例如 fundamentalist / chartist / noise / market-maker），每类的 V 共享参数
  - 正则化：|∇V|² 平滑性惩罚、对称性惩罚
  - 多任务训练：同时拟合返回率 + 波动率 + ACF + 尾部
- **方法论理论结果（争取）**：在简化设定下证明势函数可识别性 / 收敛率（半理论论文价值）

**Milestone M3**: 学习势函数的 EcoMD v1 在 crypto + 美股数据上 stylized facts 匹配显著优于 ABIDES-lite / Lux-Marchesi / TRADES / GARCH。

### Phase 4（第 27–33 周）— 非平衡热力学实验（C2）
- **从训练好的 EcoMD 提取 drift/diffusion 场**，计算：
  - 熵产生率 σ(t) = ⟨force · velocity⟩_non-equil
  - 有效温度 T_eff(t)（Einstein 关系校准版）
  - Jarzynski 等式检验：⟨e^{-βW}⟩ = e^{-βΔF}
  - Crooks 涨落定理检验：P(+W) / P(−W) = e^{βW}
- **关键实验**：
  - 在 crash 前 200–400 天观察 σ(t), T_eff(t) 的系统性变化（可复现 Cavalli et al. 2024 早期预警信号结果，但首次用**学习出的物理量**而非手工指标）
  - 跨市场普适性测试：美股 6 次 crash + 加密 3 次 crash（Luna, FTX, SVB spillover）
- **对照组**：用不学习的 ABIDES / Lux-Marchesi 做同样计算，证明 EcoMD 抽出的 T_eff 更有预测力

**Milestone M4**: 至少 1 个"新物理量"（大概率是熵产生率或 T_eff 的某种形式）在 ≥3 次真实 crash 上显著早于 LPPL/VIX 发出信号。这是 Nature Physics 彩票的关键。

### Phase 5（第 34–39 周）— 应用与基线对比（C3）
- **任务 1：Crash early warning**（接 Phase 4）
  - ROC/AUC 指标，lead time 分布
  - 基线：LPPL (Sornette)、VIX、put-call、DFA-based critical slowing
- **任务 2：Optimal execution under regime shift**（finance 卖点）
  - 用 EcoMD 做环境，训练 execution agent（RL）
  - 对比 Almgren-Chriss、基线 RL（ABIDES 环境）
  - 证明物理感知的 EcoMD 环境训出的策略在真实数据上更 robust
- （可选）任务 3：Stress testing for risk management

**Milestone M5**: 至少 1 个真实可用的 finance 任务，比 baseline 提升 ≥10% 于核心指标。

### Phase 6（第 40–46 周）— 论文写作 + 投稿

**策略修订（v2）**：M3（Wk 26）达成即发 arXiv + Paper A draft，不等 M6。Phase 4–5 的结果作为 Paper B 单独投稿，避免 C2 提前暴露。

- **Paper A**（方法主导，**M3 即出 arXiv**，目标 NeurIPS/ICML main 或 ICLR 下一次 deadline）：
  - 标题候选：*"Differentiable Molecular Dynamics Simulators for Financial Markets with Learned Equivariant Interaction Potentials"*
  - 主内容：C1 完整 + C3 的一个执行/早期预警 baseline task
  - **关键原则**：**不在 Paper A 里泄露 C2 的非平衡热力学框架**。Paper A 定位为方法学，让 C2 的 novelty 留给 Paper B。
  - Paper A 里可以提到"learned Langevin dynamics with separable conservative/dissipative forces"作为架构细节，但不展开 fluctuation theorem / entropy production 的实验结果
  - arXiv version + main-conference version 可以略有差异（arXiv 先放，投稿版根据 deadline 和 feedback 调整）
- **Paper B**（物理主导，Wk 40+ 起草，M4/M5 结果出来后完整）：
  - 标题候选：*"Non-equilibrium Thermodynamics of Financial Markets: Universal Entropy Production from Learned Microscopic Dynamics"*
  - 主内容：C2 深入 + 跨市场普适性（美股+加密+国际股指 ≥ 5 个市场）
  - 投稿策略：先投 Nature Physics（15 天 desk reject worst-case），desk reject 后转 PRL；PRL 被拒转 PRE。Submission Wk 50+。

**Milestone M6**: Paper A arXiv 上线（Wk 26–28）+ Paper A 主会议投稿（Wk 40–46）+ Paper B 完整 draft。

### 机动缓冲（第 47–53 周）
- rebuttal、修改重投、追加实验、可能的第三篇 applied paper（QF/JEDC）。

---

## 5. 数据策略（v2，$50k 预算）

### 5.1 采购优先级（总目标 $15k–30k，留 $20k–35k 余量给 Phase 4/5 追加与应急）

**Tier 0 — 免费（Phase 0 立刻做）**
| 数据 | 来源 | 用途 |
|---|---|---|
| SPX 日频 30+ 年 | yfinance | Stylized facts reference |
| BTC/ETH/SOL 分钟+tick 5+ 年 | Binance data.binance.vision | 加密主训练集 |
| NASDAQ LOB 样本 | LOBSTER free | 微观结构 smoke test |
| VIX 日频 | CBOE public | Crash baseline |

**Tier 1 — 确认买（预算 ~$8k–15k）**
| 数据 | 规格 | 目标价 | 为何关键 |
|---|---|---|---|
| **美股分钟 OHLCV 15 年** | S&P 500 + Russell 1000，2008–现在，survivorship-bias-free，含分红拆股调整 | **$3k–8k**（FirstRate bulk / 卖家现货） | Paper A 核心训练数据；yfinance 分钟只有 6 个月 |
| **LOBSTER/NASDAQ ITCH 全量** | 学术订阅 1 年 或 3 个月 × 50 股票 × 全深度 | **$3k–5k** | Paper B 微观结构 → 粗粒化；也用于 ABIDES-lite 标定 |
| **CBOE DataShop EOD 期权** | SPX/SPY/QQQ 2005–现在，全行权价全到期，put-call OI/volume | **$1k–2k** | Paper B/C crash 预测必比 baseline（implied vol skew, put-call ratio） |

**Tier 1.5 — 强烈建议买（预算 ~$5k–10k，**强化 Nature Physics 赌注**）**
| 数据 | 规格 | 目标价 | 为何关键 |
|---|---|---|---|
| **国际股指成分股日频+分钟** | FTSE 100, DAX, Nikkei 225, HSI, SSE 50 各 ≥ 10 年 | **$2k–5k** | 跨市场普适性验证（§3.1.1 Nature Physics 硬门槛#2）。美股+加密+3 国股指 = 5 个独立市场 |
| **Tardis.dev 商业 3 个月** | Binance+Coinbase+Bybit+OKX L2 book + 清算 + 资金费率，覆盖 Luna/FTX | **$3k–5k** | 加密 L2 跨交易所。Paper B 物理量跨市场一致性的核心证据 |
| **Refinitiv/iBloomberg tick 样本** | 可选，某个单一 crash 窗口 tick 级美股 | **$0–2k** | 仅当 Tier 1 的分钟数据在 Flash Crash 2010 颗粒度不够时追加 |

**Tier 2 — 有便宜的才买（预算 ~$2k–5k）**
| 数据 | 目标价 |
|---|---|
| CRSP daily 1990–现在（survivorship-bias-free factor-adjusted，若非 WRDS 学术） | $2k–5k |
| 商品+汇率日频（作为"非权益非加密"对照组） | <$1k |
| 替代新闻/情绪数据 | skip（out of scope） |

**总估算**：~$13k–30k 采购 + 留 $20k–35k 余量。**不建议一次 burst spend 到 $50k**——边际收益递减明显，而且后期 Phase 4/5 如果碰到数据缺口会后悔没有留余量。

### 5.2 关键警告 / 需用户验证的事项

- **CRSP / OptionMetrics IvyDB 常规只通过 WRDS 卖，独立研究者（无大学 affiliation）可能拿不到**。如果你有某高校合作者挂名访问，能省好几 k。否则跳过 CRSP，用 CBOE DataShop + FirstRate + yfinance 组合。
- **数据卖家的合规授权**：只认"vendor 直销 + 正规发票"或"学术授权转让"；**不接受盗版 / 灰色数据**（reviewer 或 desk editor 查出来是灾难）。在 data_wishlist.md 里我会显式要求 license terms。
- **数据到手后的 reproducibility**：论文里会引用 vendor + 购买日期 + 数据哈希（不泄露原始数据）。脚本开源，数据按 license 要求处理。

### 5.3 数据工程原则（v2 修订）
- 全部 Parquet + zstd 压缩；**provenance 元数据**（来源、下载日期、license、preprocess 哈希）作为 sidecar JSON 存在 `ecomd/data/provenance/<vendor>.md`
- 严格 train/val/test **时间划分**（绝不 leak 未来数据）
- **预留 hold-out 窗口**：2019 全年（普通市场）+ 所有 crash 窗口（2008-09..2009-03, 2010-05-06, 2020-02..04, 2022-05, 2022-11, 2023-03）在首次看到前不参与任何调参
- **数据版本化**：每次预处理输出到 `processed/v{N}/`，不覆盖前版本

---

## 6. 评估协议（避免自欺）

### 6.1 Stylized facts 自动化套件（Phase 1 交付）
- 11 项 Cont 2001 指标全部实现，输出 JSON + 可视化报告
- 所有模型（baselines + EcoMD）每次 eval 都跑全套，存盘可比

### 6.2 分布距离
- 1D 返回率分布：Wasserstein-1、KS
- 高阶：MMD（RBF kernel）、energy distance
- 轨迹级：signature distance（借鉴 Buehler-Horvath-Lyons）

### 6.3 Crash 预测评估
- **严格事前**：模型在 crash 之前冻结参数
- 指标：AUC-ROC（阈值扫）、Lead time 分布（多远之前发出警报）
- 基线必须包含：LPPL、VIX、put-call、Cavalli 早期预警信号
- 统计显著性：bootstrap p-value

### 6.4 消融实验（audit trail）
- 等变 vs 非等变
- 学习势 vs 手工势（Lux-Marchesi）
- 有无 Gumbel-softmax
- k-NN 图 vs 全连接

### 6.5 复现性
- 所有实验 config + seed 入 git
- 论文发布时开源代码 + 至少 1 个完整实验的 checkpoint
- 数据预处理脚本开源（数据本身受版权限制不开源）

---

## 7. 长期记忆与项目基础设施（需在退出 plan mode 后建立）

### 7.1 需要创建的文件
- `CLAUDE.md`（项目级指令，补充全局 CLAUDE.md）：
  - 研究者人设：以 AI 顶会顶刊投稿人 + Reviewer-2 视角思考；独立研究，Claude 承担 critical reviewer 角色
  - 工作日志要求：每次工作后更新 `logs/YYYY-MM-DD.md`
  - 批判性思考强制：用户观点可能错，遇到理论/实验设计问题主动 pushback；任何结论需要有证据或明确标注假设
  - 代码规范：PyTorch 2.3+、类型标注、单测、可重现；实验用 Hydra config + W&B
  - 实验规范：每个实验有 config、seed、artifacts；H20 运行必须可从 checkpoint 恢复
  - 工作流：Mac 本地开发 + git push → H20 拉取；数据 AWS S3 单向同步
- `.claude/` 目录（项目 hooks/skills/settings）
- 全局记忆（`/Users/howardwang/.claude/projects/-Users-howardwang-Desktop-playground-ecophys/memory/`）：
  - `user_role.md`（user）: 全职 6–18 个月独立研究者；野心冲顶会顶刊；偏好便宜数据；4×H20 异地；Mac dev + S3 + GitHub + H20 pull-and-train
  - `project_overview.md`（project）: EcoPhys 研究目标、三支柱贡献、venue 策略（系列论文 + PRL/Nat Phys 赌一次）
  - `feedback_critical_thinking.md`（feedback）: 用户明确要求批判性思考和独立 reviewer-2 角色；不盲从、主动 pushback
  - `feedback_long_memory.md`（feedback）: 用户要求每次工作写日志、维护长期记忆
  - `feedback_workflow.md`（feedback）: Mac 开发 + AWS S3 数据 + GitHub 代码 + H20 pull-and-train
  - `reference_data_sources.md`（reference）: 主要数据源清单（价格、体量、注意事项）
  - `reference_venues.md`（reference）: 目标 venue + 投稿截止 + 评分标准
  - 更新 `MEMORY.md` index

### 7.2 项目仓库结构（提议）
```
ecophys/
├── CLAUDE.md                 # 项目指令
├── .claude/                  # 项目 .claude 目录（hooks、skills、settings 等）
├── README.md
├── pyproject.toml            # conda env 名: ecophys, python 3.11
├── ecomd/                    # 核心包
│   ├── data/                 # 数据管道（S3 同步、yfinance、Binance、LOBSTER 等）
│   ├── models/               # EcoMD 架构
│   ├── training/             # 训练循环、loss
│   ├── physics/              # 涨落定理、熵产生率、T_eff
│   ├── eval/                 # stylized facts suite（可独立发布）
│   └── baselines/            # ABIDES-lite / Lux-Marchesi / GARCH / LPPL
├── experiments/              # 每个实验一个子目录（Hydra config + run 脚本 + results/）
├── notebooks/                # 探索性分析
├── logs/                     # 按日期的工作日志 YYYY-MM-DD.md
├── papers/                   # LaTeX 草稿（paper_a_methods/, paper_b_physics/, paper_c_finance/）
└── references/               # 下载的 PDF + bib
```

### 7.3 工作流细节（v2 修订：**H20 在公司内网，网络环境不佳**）

网络约束重塑了数据流：不能依赖 S3→H20 反复拉取，必须"一次大批量预灌"+"本地大缓存"。

- **云存储选型**：**Cloudflare R2**（S3 API 兼容，**零 egress 费**）替代 AWS S3。原因：
  - 我们会反复从云往 H20 拉数据。S3 egress $0.09/GB，500 GB 拉一次 $45；多次拉 + 多版本更贵。
  - R2 egress 免费，存储 $0.015/GB-mo（比 S3 $0.023 还便宜）。
  - 代码无需改（`boto3` 设 `endpoint_url` 指向 R2 即可）。
  - 缺点：R2 不支持 lifecycle 到 Glacier Deep Archive；但我们数据量 < 2 TB，Standard 留着也就 $30/月，不值得优化。
  - **备用方案**：如果公司 VPN / 防火墙会阻断 `.r2.cloudflarestorage.com`，退回到 AWS S3 + 优化的 batch-download 策略。

- **数据流（新版）**：
  1. Mac 本地拉 raw 数据 + 做预处理 → 写 Parquet+zstd 分片
  2. Mac `rclone sync`（或 aws cli）推到 R2（Mac 家庭带宽，一般 OK）
  3. **一次性 bulk download 到 H20 本地 NVMe**（假设 ≥ 2 TB 盘空间），运行在公司夜间 off-hour，用 `rclone --transfers=16` 多路并行
  4. 之后所有训练都用 H20 **本地路径**，不再访问云端
  5. 只有新增数据或重大预处理更新才触发增量 sync

- **H20 本地数据缓存**：
  - 规划 `/data/ecophys/{raw,processed,splits,reference_values}/` 目录结构
  - 预留 2 TB 磁盘空间（~300 GB 压缩数据 + 2× 版本存档 + 预处理中间件）
  - 设 `ECOPHYS_DATA_DIR=/data/ecophys` 作为所有训练脚本读取的 env var

- **代码流**：
  - Mac git commit + push → GitHub → H20 `git pull`
  - 代码 repo 体积小，即便网络慢 push/pull 不是瓶颈
  - `main` 保持可跑；实验用 feature 分支
  - 长实验：`tmux` + `wandb resume` 防断

- **W&B 的网络考量**：
  - 如果 H20 能访问 `api.wandb.ai`（多数公司允许 HTTPS outbound），直接用 cloud 版
  - 如果被墙，用 `wandb offline` 模式，训练完后 `wandb sync <run-dir>` 到能上网的机器（可能是 Mac 跳板）
  - 或者自部署 `wandb local`（企业版单机）

- **实验触发**：
  - 小实验（≤10⁴ agents，<1h）在 Mac 跑（MPS 或 CPU）
  - 中大实验一律 H20；通过 SSH 到 H20，进 tmux，启动 `run_experiment.sh`
  - **不要设置**依赖 H20 出网的定时任务（网络不稳，会莫名失败）

### 7.4 需要用户确认的网络细节（阻塞 R2 vs S3 决策）
1. H20 机器能否访问公网 HTTPS？（能拉 GitHub? 能拉 pip/conda? 能访问 `*.r2.cloudflarestorage.com`?）
2. H20 机器磁盘容量大致多少？（决定是否需要更精打细算的数据子集）
3. 公司是否有内网 NFS / object storage 可以放我们的数据？（如果有，比云存储更快更省）
4. Mac 到 H20 的 SSH 通道带宽实测（晚上跑一次 `iperf3` 或简单 `scp` 大文件测一下）

---

## 8. 风险登记与缓解

| 风险 | 概率 | 影响 | 缓解 |
|---|---|---|---|
| 可识别性失败（学不出稳定势函数） | 中 | 高 | 结构化先验（agent 类型）+ 多任务 + 正则化；退路：切成非等变版本 |
| 长 BPTT 梯度爆炸/消失 | 中 | 中 | Truncated BPTT、gradient clipping、stop-gradient 混合；退路：DDPG/score matching 替代 |
| H20 机器宕机或远程连接不稳 | 中 | 中 | 所有数据备份；训练 checkpoint 每 1h 存云；有 fallback 云算力预案 |
| 非平稳性毁掉 T_eff 预测 | 中 | 高 | 时变势 + regime detection；退路：降维到 C1+C3 两支柱 |
| 顶会投稿被拒 | 高 | 中 | 提前准备 ICAIF / Physica A 作为兜底；每次被拒快速吸收意见 |
| 已有 similar work（2026 新出） | 中 | 中 | 每月 ArXiv 扫一次；提前抢占预印本（arXiv + 公开代码） |
| **用户兴趣/时间变化** | 中 | 高 | 模块化设计：每阶段有独立可发表产物（stylized facts 库、ABIDES-lite、EcoMD v0、T_eff 分析） |
| 评审要求补做实验 | 高 | 中 | 主实验用 <4GPU 可跑的小规模版本，可快速补充 |

---

## 9. 已拍板的关键决策（供未来查阅）

1. **发表策略**：**系列论文（2–3 篇）**，但 Paper B 以 PRL/Nature Physics 标准撰写；Nature Physics 作为 Paper B 完成后的"低成本一次性赌注"而非主路径。理由见 §3.1.1。
2. **C2 优先级**：**早期核心**。Phase 2 架构已加入非保守/耗散力分离 + 力-速度-状态三元组记录。
3. **工作流**：Mac dev + AWS S3（数据）+ GitHub（代码）+ H20 pull-and-train。细节见 §7.3。
4. **协作模式**：独立研究，Claude 作为 critical reviewer 伙伴；需要背书/讨论时由用户找人。

## 9.1 仍需回答的问题（v2）

**已拍板（v2 新增）**：
- 数据预算：**≤ $50k**（用户 2026-04-23 同日确认），实际计划花 ~$15k–30k Tier 1+1.5，留余量
- M3 → arXiv 立刻上线（用户 2026-04-23 同日确认）
- 框架：默认 **PyTorch + torchsde**，JAX/diffrax 仅在 Phase 4 必要时才用

**仍待回答（阻塞工作流最终敲定）**：
1. **H20 公网访问情况**：能否 HTTPS 出网？能否访问 GitHub / Cloudflare R2 / `api.wandb.ai` / pip 镜像 / 数据 vendor 的下载接口？
2. **H20 磁盘容量**：本地 NVMe 可用多少 TB？（决定是否需要数据子集策略）
3. **公司内部存储**：是否有 NFS / 内部 object storage 可借用？
4. **Mac↔H20 带宽**：大致多少 MB/s？实测一次，决定数据预灌时间窗
5. **WRDS 访问**：是否有某高校合作者能代为访问 CRSP/OptionMetrics？（省 $5k+）
6. **数据 vendor 人脉**：具体有哪些人？他们的供货范围（转卖学术订阅? 多家 vendor 代理? 自有数据？）

---

## 10. 验证与关键里程碑

| 里程碑 | 完成标准（数字化） | 目标日历周 |
|---|---|---|
| M0 基础设施 | 数据管道跑通（≥3 个源），文献精读 5 篇笔记入 `references/` | Wk 4 |
| M1 Stylized facts + baselines | 11 项指标全部实现并在 SPX+BTC 上跑出 reference 值 | Wk 10 |
| M2 EcoMD v0 | 10⁴ agents 可训，≥6 个 stylized facts 初步匹配 | Wk 18 |
| M3 EcoMD v1（学习势） | 10⁵ agents，stylized facts 全部达到 SOTA / 接近 SOTA | Wk 26 |
| M4 非平衡热力学 | ≥1 个 learned 物理量，在 ≥3 次真实 crash 上做出 lead time ≥30 天事前预测 | Wk 33 |
| M5 Finance 应用 | Execution / early warning 任务上 ≥1 个 SOTA 超越 | Wk 39 |
| M3.5 arXiv 上线 | Paper A v1 arXiv preprint + 代码 stub 开源 | Wk 27–28 |
| M6 投稿 | 1 篇主论文投到 NeurIPS/ICML/ICLR；1 篇物理扩展 draft | Wk 46 |

---

## 11. 下一步（立即动作，待你同意 plan 后执行）

**第一批（今天内完成）**：
1. 退出 plan mode
2. 在全局 memory 写入本项目的 user/project/feedback/reference 记忆文件（§7.1 清单）
3. 在仓库建立 `CLAUDE.md`（项目指令）+ `.claude/` 目录骨架
4. 初始化 Python 项目：`conda create -n ecophys python=3.11`，pyproject.toml + 基础依赖
5. 建立 `logs/` 并写今天的第一个工作日志（本次文献调研总结 + 关键决策记录）
6. 把 plan 文件复制到项目的 `papers/proposal/plan_v1.md` 作为研究计划的第一个 draft

**第二批（本周内）**：
7. 设置 AWS S3 bucket（等你回答 §9.1.3）
8. 数据管道 v0：yfinance 拉 S&P 500 日频 + Binance data.binance.vision 拉 BTC/ETH 分钟 → Parquet → S3
9. 文献精读 5 篇（Cont 2001、Tóth-Lux-Sornette 2018、MACE、Chopra 2022、Maskawa 2025）并写笔记入 `references/notes/`
10. 实现 stylized facts suite 的骨架（先 4 项：fat tails、volatility clustering、leverage、long memory）

**检查点（Wk 4 M0）**：数据管道能跑、5 篇精读笔记完成、stylized facts suite 在真实数据上跑出 reference 值。

---

## 附录 A：必读文献清单（精选，在 Phase 0 完成）

1. Cont (2001) "Empirical properties of asset returns" — *Quantitative Finance* 1
2. Bouchaud & Potters (2003) *Theory of Financial Risk and Derivative Pricing*
3. Tóth, Lux & Sornette (2018) PRL 120 — Boltzmann equation from HFT
4. Lux & Marchesi (1999) *Nature* / follow-ups — chartists/fundamentalists
5. Farmer, Patelli, Zovko (2005) PNAS — zero intelligence
6. Bornholdt (2001) IJMPC — Ising market
7. Sornette LPPL review (2003)
8. Yakovenko & Rosser (2009) RMP — stat mech of money
9. Chopra et al. (2022) arXiv:2207.09714 — Differentiable ABM
10. Batatia et al. (MACE, NeurIPS 2022) — equivariant GNN
11. Musaelian et al. (Allegro, SC23)
12. Byrd et al. ABIDES
13. Zhang et al. (DeepLOB, 2018)
14. Buehler-Horvath-Lyons (Signatures, 2020)
15. Maskawa, J. (Entropy 2025, 27(4), 435, doi: 10.3390/e27040435) — "Empirical Study on Fluctuation Theorem for Volatility Cascade Processes in Stock Markets"
16. Cavalli et al. (EPJ Data Science 2024) — early warning for crashes
17. Wiese et al. (QuantGAN)
18. TRADES (arXiv 2502.07071)
19. Gruslys et al. (2016) — Memory-efficient BPTT
20. Farmer & Joshi (2002) — agent price dynamics

(详细 bib 在 `references/` 建立后维护)
