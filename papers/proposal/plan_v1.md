# EcoPhys: 分子动力学视角下的金融市场群体动力学研究

> ⚠️ **SUPERSEDED**: This plan has been replaced by `plan_v2.md` (same day revision)
> and ultimately by `plan_v3.md` (2026-04-24, Path C commitment). Kept for historical
> reference. **Do not use this document for current planning decisions.**

**Plan version**: v1 (2026-04-23)
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
- **关键里程碑**：Wk 26 M3（EcoMD v1 超越 baselines）→ Wk 33 M4（≥3 次真实 crash 事前预测，决定是否值得赌 Nature Physics）→ Wk 46 M6（Paper A 投稿）。
- **下一步**：用户批准 plan → 建立项目骨架 + 长期记忆 → Phase 0 开始。

---

## 1. Context — 为什么做这个研究

### 1.1 问题陈述
把金融市场的每个参与者类比为 MD 中的原子，把市场的波动类比为统计物理性质（温度、相变、输运系数）。目标是构建**可微、大规模、物理启发**的市场仿真器，既能再现 stylized facts、又能揭示非平衡统计力学规律、还能预测极端事件。

### 1.2 Sanity check — 为什么值得做
调研后发现关键空白：
- **Tóth-Lux-Sornette (PRL 2018)** 已经手工推导了 HFT 的 Boltzmann 方程 —— 但**没有人用 ML 力场（MACE/NequIP 风格）去学习交易者之间的相互作用势**。物理社区和 ML force-field 社区完全分离。
- **Chopra et al. (2022)** 的可微 ABM 只做到 ~10³–10⁴ agents，局限于流行病学，**没人在金融市场做端到端可微的粒子仿真器**。
- **Doshi et al. (Entropy 2025)** 首次实证验证了波动率过程满足涨落定理（~5% 误差），**但没人把涨落定理作为学习目标或评估指标嵌入仿真器**。
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

**联合概率**（独立性假设偏乐观）：**约 3–8%** 冲上 Nature Physics。

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
  - Must read: Cont 2001, Bouchaud & Potters 2003, Tóth-Lux-Sornette 2018, Chopra 2022, MACE (Batatia 2022), Allegro (Musaelian 2023), ABIDES, Doshi 2025 (Entropy), Farmer-Patelli-Zovko 2005, Yakovenko-Rosser 2009, Sornette LPPL 回顾
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
- **论文 1**（方法主导，目标 NeurIPS/ICML main 或 ICLR）：
  - "Differentiable Molecular Dynamics Simulators for Financial Markets with Learned Interaction Potentials"
  - 主内容：C1 + 部分 C3（execution task）
  - 如果 C2 结果够漂亮，增加一个"Physics Insight"章节
- **论文 2**（物理主导，目标 PRE 或 Nature Physics 投石问路）：
  - "Non-equilibrium Thermodynamics of Financial Markets via Learned Dynamics"
  - 主内容：C2 深入 + 跨市场普适性
  - 如果实验结果 exceptional → 直接冲 Nature Physics；否则 PRE

**Milestone M6**: 1 篇主论文投稿 + 1 篇物理扩展 draft。

### 机动缓冲（第 47–53 周）
- rebuttal、修改重投、追加实验、可能的第三篇 applied paper（QF/JEDC）。

---

## 5. 数据策略

| 市场/频率 | 来源（免费优先） | 体量估算 | 用途 |
|---|---|---|---|
| 美股日频 | yfinance | <100 MB | Stylized facts 主基准；跨品种统计 |
| 美股分钟 | Databento $125 credit → FirstRate 样本 | ~1 GB/年 S&P 500 | 中频实验；Flash Crash 2010 测试 |
| 美股 LOB | LOBSTER 免费样本（10 股票 × 若干天） | ~10 GB | 微观结构消融；订单流建模 |
| 加密分钟 | CryptoDataDownload + Binance data.binance.vision | <5 GB | Stylized facts；富样本训练 |
| 加密 tick | Binance `data.binance.vision` aggTrades | 50–200 GB/年 for BTC/ETH/SOL | 主训练数据（sample abundance）|
| Crash 事件窗 | 专门抓取 2008/2010/2020/Luna/FTX/SVB 前后 N 天 | 按需 | C2/C3 核心测试集 |

**数据工程原则**：
- 全部 Parquet + zstd 压缩，放在本地 SSD + 备份到云（避免 H20 机器故障丢失）
- 严格 train/val/test 时间划分（绝不 leak 未来数据）
- 预留 2019-01 至 2019-12 作为"未见过的普通时期"测试集
- Crash 测试集事件在首次看到前不参与任何调参

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

### 7.3 工作流细节（用户选定：Mac 开发 + S3 + GitHub + H20 pull-and-train）
- **数据流**：
  - Mac 本地写 ingestion 脚本 → 跑通小样本 → 把处理完的 Parquet 分片 upload 到 S3（`s3://ecophys-data/{source}/{symbol}/{date}.parquet`）
  - H20 机器 `aws s3 sync` 拉数据（只拉本次实验需要的分片，节省磁盘）
  - S3 是 single source of truth；Mac 和 H20 都只作 cache
  - S3 开启版本控制 + lifecycle policy（>90 天移到 Glacier）
- **代码流**：
  - Mac git commit + push → GitHub → H20 git pull
  - `main` 分支保持可跑状态；实验用 feature 分支
  - 长实验用 `tmux` + `wandb resume` 防断
- **实验触发**：
  - 小实验（≤10⁴ agents，<1h）可在 Mac 跑
  - 中大实验（10⁴–10⁵ agents，>1h）一律 H20
  - H20 机器设置统一的 `run_experiment.sh` 脚本：自动拉 git、同步 S3、启动 W&B、写日志

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

## 9.1 仍需回答的小问题（可后续解决，不阻塞 plan）

1. **ML 框架**：PyTorch 2.3+ 为主；某些物理模块（ODE integrator、batched fluctuation theorem analysis）是否允许用 JAX/diffrax？（推荐：允许）
2. **数据预算**：是否愿意花 ~$100–500 预算解锁 Databento 更大额度 / Tardis 学术版 / Polygon 付费版？（推荐：预留 $300 作为关键卡点时的解决方案）
3. **AWS S3**：是否已有 AWS 账号 + 配置好的 bucket？预估存储成本：~$5–20/月（<1 TB 数据）。
4. **arXiv 预印本策略**：Paper A M3 milestone（Wk 26）达成后是否立刻发 arXiv 抢占优先权？（推荐：是）

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
9. 文献精读 5 篇（Cont 2001、Tóth-Lux-Sornette 2018、MACE、Chopra 2022、Doshi 2025）并写笔记入 `references/notes/`
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
15. Doshi et al. (Entropy 2025) — fluctuation theorem on volatility
16. Cavalli et al. (EPJ Data Science 2024) — early warning for crashes
17. Wiese et al. (QuantGAN)
18. TRADES (arXiv 2502.07071)
19. Gruslys et al. (2016) — Memory-efficient BPTT
20. Farmer & Joshi (2002) — agent price dynamics

(详细 bib 在 `references/` 建立后维护)
