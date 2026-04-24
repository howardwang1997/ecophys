# EcoPhys / EcoMD — Plan v3

**Date**: 2026-04-24
**Supersedes**: `plan_v2.md`
**Primary target**: Nature Physics (flagship paper B) + supporting papers
**Total timeline**: 52 weeks (vs v2 的 46)
**Compute**: 8×H20 NVLink, long-term access
**Data budget**: $50k (unchanged from v2)

---

## 0. 本版 vs v2 的变化

| 维度 | v2 | **v3** |
|---|---|---|
| 硬件 | 4×H20 (pull-and-train) | **8×H20 NVLink**, single node, long-term |
| 策略 | Series-paper (Paper A 先，B/C 后) | **Flagship (Paper B → Nature Physics) + 系列 papers 作退路** |
| NP 概率估算 | 5–12% | **10–15%**（A1+B2 + rigor 条款生效后） |
| 时间 | 46 周到 M6 | **52 周到 M6**（加 2 个新 gate） |
| Paper A arXiv 时机 | Wk 27 (M3.5) | **Wk 26 (与 M3 同步)，pre-register crash list** |
| 新硬约束 | — | **三条科研严谨性条款**（见 §6） |

**核心战略变化**：从 "多少都发，能多好多好" 变成 "flagship 失败有退路，但 flagship 按 NP 级别严谨度执行"。

---

## 1. 研究程序（不变）

EcoMD — 可微分、等变、大规模 MD 风格的金融市场仿真器。

- **C1 方法贡献**：首个可微分 MD 市场模拟器，学习等变相互作用势
- **C2 物理贡献**：非平衡热力学量（有效温度、熵产生率）作为 universal crash precursor
- **C3 应用贡献**：crash 早期预警、最优执行

---

## 2. 一句话定律（pre-register 列表）

Paper B 核心 claim 候选，**四个同时测量，三层 load-bearing 结构**：

### 2.1 Primary（Paper B 主干）

**A1**: 有效温度临界标度
> T_eff(t) ∝ (t_c − t)^(−ν)，8 市场上 ν 统一于 ν̄ ± 0.05

**B2**: Jarzynski 自洽
> ⟨e^(−βW)⟩ = e^(−βΔF)，W 由路径积分计算，ΔF 由学习的 U_θ 独立读出，两者在 15% 内一致

**A1 + B2 组合** 的意义：首次同时 (a) 从 learned dynamics 提取 T_eff 并证明其临界性 + (b) 用 Jarzynski 验证 learned potential 真的是物理 potential。**这组合 kill 掉 "就是个 curve fit" 的主流反驳**。

### 2.2 Secondary（Paper B 支持性 claim，仅在 A1 过关后报告）

**A2**: Hyperscaling
> ν(2−η) = γ，三个独立测量的指数自洽

**A2 作用**：从 "scaling 像 critical" 升级到 "**是** critical phenomenon in physics sense"。若 A1 通过但 A2 不通过 → paper 仍可发但降级为 PRL。

### 2.3 独立 track（Paper B.5 / companion PRL）

**B3**: TUR 饱和
> Var(J)·⟨Σ⟩ ≈ 2k_B T_eff on ≥5 markets，市场运行在热力学效率极限

**B3 独立路径**：generalized TUR 在金融零文献，单独 PRL 量级已经足够。不塞入 Paper B 避免 Bonferroni 问题。

---

## 3. 诚实概率表

| 事件 | 独立概率 |
|---|---|
| v1 达 ≥9/11 且 stable（M3） | 50–65% |
| A1 在 ≥6 市场上满足 ν 一致 | 35–45% |
| A2 hyperscaling 在 ≥6 市场 | 25–35% |
| B2 Jarzynski 自洽在 ≥5 市场 | 50–60% |
| B3 TUR 饱和在 ≥5 市场 | 40–50% |
| 全部 sanity checks 通过 | 60–70% |
| **Paper B 主 claim 存活到投稿** | **25–30%** |
| **Nature Physics 接收（conditional on 投稿）** | **40–55%** |
| **Joint: Nature Physics paper** | **10–15%** |

**翻译**：85–90% 概率 NP 不成，但**每个失败层级都有清晰退路**（见 §7）。

---

## 4. 时间线与硬 gate

| M | 名称 | 周 | 硬 gate 条件 | 失败退路 |
|---|---|---|---|---|
| M0 | 数据/基础 | 4 | — | ✓ 已达成 |
| M1 | Baselines + stylized facts | 10 | — | ✓ 已达成 |
| M2 | v1 at ≥7/11 | 16 | v1 ≥7/11 stable | 架构回炉 |
| **M3** | v1 全面训练 | **26** | ≥9/11 on ≥2 markets **+ Paper A arXiv preprint with pre-registered crash list** | ≤7/11 → 放弃 NP，NeurIPS 路线 |
| **M3.5** | A1 pilot (3 markets) + ALL sanity checks | **30** | (1) ν 一致 on 3/3 pilot markets + (2) surrogate null passes + (3) no sanity check fails | fail → **立即停 flagship，Paper A arXiv 起步独立系列** |
| M4 | A1 full (8 markets) + A2 + B2 + B3 主实验 | 36 | A1 pass on ≥6/8 + B2 pass on ≥5/8 | 任一 fail → 降级 PRL |
| **M5** | "一句话物理" 正式化 | **42** | 能用 ≤3 公式描述发现 + sanity appendix 完整 | fail → 拆 2 PRL + 1 QF |
| M6 | Nature Physics 投稿 | 48 | paper 就绪 + 所有 gates 通过 + pre-registration 合规 | — |
| M7 | 终局 | 52 | accept / desk reject / revision | rejection → 1 周内转 PRL |

### Gate 交付物

**M2 gate**（Wk 16）：
- v1 code frozen
- test suite ≥ 120 tests
- Paper A 结果表（5-way comparison）

**M3 gate**（Wk 26）：
- **arXiv preprint** 提交（Paper A + pre-registered crash list + 实验方案）
- 至少 2 市场 v1 ≥9/11
- Phase 3 实验配置冻结

**M3.5 gate**（Wk 30）——最关键的 hard cut：
- A1 pilot on SPX + BTC + EUR/USD 全部 3 市场 ν 一致
- IID null + GARCH null sanity checks 通过
- 7 项 sanity checks 全部通过
- **任一失败 → 停 flagship**

**M5 gate**（Wk 42）：
- Paper B abstract 能写出 ≤ 3 个 equation
- Robustness appendix 完整（所有 sanity checks 结果）
- Pre-registration 合规 (arXiv 已公开)

---

## 5. 8×H20 NVLink 分阶段分配

### 5.1 阶段 1（现在 → M2, Wk 12 内）

```
Mac/CPU          v0.6 → v1 迭代（Student-t noise, state-β 等）
H20 × 0–1 卡     单次 smoke test 大规模验证（可选）
H20 × 2–7 卡     空置
```

**原则**：v1 未达 5/11 → 8/11 前不要碰 H20。H20 只加速 bug-finding，不加速 truth-finding。

### 5.2 阶段 2（M2 → M3, Wk 16→26）

```
卡 0–7 NVLink    Tensor-parallel EcoMD v1 单模型训练
                 N=3–5×10⁵ agents, d=64, MACE-lite k=32
                 ~5–8 天 × 3 种 ablation
```

**NVLink 的核心红利**：单大模型 tensor-parallel 跑 N=5×10⁵（无 NVLink 只能 N ≤ 10⁵）。

### 5.3 阶段 3（M3 → M3.5, Wk 26→30）

```
卡 0–2      共享 θ multi-market pilot training (SPX, BTC, EUR/USD)
卡 3, 4, 5  独立 single-market 控制对照（SPX-only, BTC-only, EUR/USD-only）
卡 6, 7     A2 FT pilot (10³ trajectories × 3 markets)
并行        IID surrogate + GARCH surrogate pipeline
```

Gate 2 检验：pilot 通过才进阶段 4；否则停止 flagship。

### 5.4 阶段 4（M3.5 → M4, Wk 30→36）

```
卡 0–5      共享 θ 8-market joint training (SPX, Russell, Nikkei, DAX, 
            FTSE, BTC, ETH, EUR/USD)
卡 6–7      B2 主实验 (10⁴ trajectories × 8 markets) + B3 TUR 实验
```

### 5.5 阶段 5（M4 → M6, Wk 36→48）

```
卡 0–1      分析 jobs (scaling law fits, T_eff extraction)
卡 2–3      Robustness + sanity check 重跑（reviewer-2 预演）
卡 4–7      Backup 实验 / alternative definitions
```

### 5.6 阶段 6（M6 → M7, Wk 48→52）

```
卡 0–3      Reviewer 响应实验（新 ablation、additional markets、etc）
卡 4–7      Paper C（应用层，crash EWS + 最优执行）启动
```

---

## 6. 三条科研严谨性硬条款（2026-04-24 锁定）

**用户已明确接受，这三条是 plan v3 的必要条件，违反任一条自动降级 flagship。**

### 6.1 Surrogate data 可以 kill 主 claim

所有主 claim 的实验流程同时跑在：
1. 真实市场数据
2. **IID Student-t surrogate**（匹配真实 returns 的 kurtosis / std）
3. **GARCH(1,1)-t surrogate**（匹配真实 vol clustering）

**判据**：
- Primary claim 在真实数据满足 + 在 surrogate 中**不**满足 → claim 有效
- Primary claim 在 surrogate 中**也**满足 → claim 废（是 pipeline artifact，不是物理）

### 6.2 Sanity check 任一失败即降级

**七项必做 sanity check**，在 Gate 2 (Wk 30) 之前全部跑完：

| # | Check | 目的 | 通过判据 |
|---|---|---|---|
| S1 | IID null | 排除 pipeline artifact | surrogate 不给同样结果 |
| S2 | GARCH-t null | 排除 vol-clustering 幻觉 | 同上 |
| S3 | Markov-toy model | B2 pipeline 正确 | recover 已知 ΔF 在 5% 内 |
| S4 | Single-market check | 排除单市场 fit 假 universality | single-market run 不给 universality |
| S5 | Dropout test | 排除单一事件 dominate | 去任一 crash 事件，ν 变化 < 0.1 |
| S6 | Across-regime split | time-universality | 训练期 / 测试期 ν 一致 |
| S7 | Definition robustness | 非 cherry-picking | 3 种 T_eff 定义都给一致 ν |

**任意 1 项失败 → Paper B 降级，Nature Physics 不投**。

### 6.3 Pre-registration on arXiv

**Wk 26（M3）时**：arXiv preprint 公开以下内容，之后**不得修改**：

1. **Crash event list**：所有 Paper B 会用的 crash 事件，含起止时间
2. **T_eff definition**：选定的唯一定义公式
3. **ν estimation protocol**：window size, bootstrap 方法, CI 定义
4. **Sanity check 结果预期**：每项通过的量化 threshold
5. **Falsification criteria**：什么结果算 "claim 失败"

**意义**：
- 消除 researcher degrees of freedom
- 获得 priority stake（即使 flagship 延迟）
- 事后无法 cherry-pick

---

## 7. 失败退路（每个 gate 都有清晰逃生口）

### 7.1 Gate 1 (M2, Wk 16) 失败
= v1 在 CPU/smoke 规模都无法过 7/11。
→ 回到架构设计。Phase 3 MACE-lite 提前启动，但 Paper 目标降为 NeurIPS/ICML。

### 7.2 Gate 2 (M3.5, Wk 30) 失败（最可能发生，概率 ~50%）
= pilot 3 市场 ν 不一致，或 sanity check 挂掉。
→ **立即**行动：
  1. Paper A arXiv preprint 已投（M3），priority 已锁
  2. Paper A 投 NeurIPS/ICML 最近 deadline
  3. Paper B 拆成 2 个 PRL（single-market critical + TUR）
  4. 已跑的 pilot 作为 Paper A 补充实验

### 7.3 Gate 3 (M4, Wk 36) 失败
= full 8-market 实验失败（≤4 市场一致）。
→ Paper B 降级为 PRL "market-specific critical phenomena"。B3 TUR 作为 companion paper。

### 7.4 Gate 4 (M5, Wk 42) 失败
= 写不出 ≤3 equation 描述新物理。
→ 拆 2 PRL（phenomenology 一个 + TUR 一个）+ QF 应用 paper。

### 7.5 M6 被 desk reject
→ 1 周内 reformat 投 PRL。失去 ~2 月，论文不浪费。

---

## 8. Paper 系列结构（v3 版本）

### Paper A：C1 方法论
- 目标：NeurIPS / ICML main
- Wk 26 arXiv preprint
- 包含：差异化架构（可微分 Langevin + learned potential）、v1 stylized facts reproduction、对照组
- **不包含**：C2（fluctuation theorem、T_eff、universality）——全留 Paper B

### Paper B：C2 物理 → **Nature Physics flagship**
- 目标：Nature Physics
- Wk 48 投稿
- 包含：A1 + B2 + A2（作为 supporting）+ 完整 sanity appendix
- 核心：**"physics of markets" 一线定律**

### Paper B.5 / Companion PRL：TUR
- 目标：PRL
- 与 Paper B 同期或 M6+1 月投稿
- 包含：B3 TUR 饱和单独展开

### Paper C：C3 应用
- 目标：JFin / QF / JEDC
- Wk 45+ 投稿
- 包含：crash EWS + 最优执行 baseline

### 退路 papers（如 flagship fail）
- "Learned critical phenomena in single-market finance" → PRL
- "Differentiable agent-based simulators: architecture and benchmarks" → NeurIPS

---

## 9. 当前状态与本周行动

### 9.1 已达成
- ✓ M0（数据 + 基础设施）
- ✓ M1（stylized facts + baselines）
- ✓ Phase 2 起步（EcoMD v0/v0.5，5/11 命中波动率结构 facts）

### 9.2 本周（2026-04-24 起）

**立刻 (Mac/CPU)**：
1. v0.6 实现 Student-t noise 替换 Langevin Gaussian 噪声（目标：补 #2 Hill, #5 Fano）
2. v0.6 实现 state-dependent β（目标：补 #1 ACF）
3. experiments/005_ecomd_v0p6/ 新建 + 运行
4. 目标：v0.6 ≥ 7/11，达 M2

**不要做**：
- ❌ 不要动 H20 — v0.6 没跑通前，H20 只帮倒忙
- ❌ 不要提前开 A1/B2 实验 — 架构 unstable 时做 universality 测试只是浪费
- ❌ 不要新开 Paper B draft — claim 未定型，写稿等于 fantasy

### 9.3 未来 12 周 roadmap

| 周 | 目标 |
|---|---|
| 本周 | v0.6 Student-t + state-β |
| +1–2 | v0.6 评估 + 可能的 v0.7 | 
| +2–3 | v1 架构设计（MACE-lite k-NN + agent type prior） |
| +4–6 | v1 CPU/smoke 验证 |
| +6–8 | v1 上 H20 主训练（NVLink tensor-parallel） |
| +8–12 | M2 冲刺 + M3 准备（pre-registration 文档 draft） |

---

## 10. 本版的关键 research discipline 变化

v2 → v3 多出来的纪律：

1. **每个 claim 都有写死的 falsification criteria**（不是 "努力证明对的"）
2. **每个实验都有 null hypothesis surrogate**（Bonferroni 意识）
3. **每个选择有 pre-registration**（消除 researcher degrees of freedom）
4. **每个 gate 都有退路 paper**（沉没成本陷阱免疫）

这些都来自 2010 年后 replication crisis 推动的科研规范。Nature Physics 现代接收 universality paper 的必要条件。

---

## 附录 A：v0.6 → v1 待完成改进

（接续 logs/2026-04-24.md Session 11）

```
v0.6 (planned):
  - Student-t(ν=5) noise in OverdampedLangevin
  - State-dependent β in ExcessDemandPrice (learnable, takes vol/last_return)
  - Wasserstein return-distribution loss as auxiliary

v0.7 (if v0.6 still < 7/11):
  - Longer chunks via activation checkpointing (chunk_steps=128)
  - Fluctuation-theorem consistency loss (light weight)
  - Multi-frequency sampling (日频 + 分钟频 联合 loss)

v1 (target M2-M3):
  - MACE-lite k-NN (k=16, L=2-3) 替换 pairwise MLP
  - Agent-type structured prior (K=4 类)
  - 共享 θ multi-market training infrastructure
  - 规模 N=10⁵–5×10⁵ (NVLink)
```

## 附录 B：pre-registration 模板（Wk 26 用）

```
=== EcoMD Pre-Registration Document ===
Date: 2026-10-XX  
Authors: [user]
arXiv ID: (pending)

1. Primary claim (A1 + B2):
   [exact formulation]

2. Pre-registered crash events:
   SPX: [list]
   BTC: [list]
   ...
   Total: N events

3. Measurement protocols:
   T_eff definition:   [equation]
   ν estimation:       [method]
   Jarzynski W:        [definition]

4. Falsification criteria:
   A1 fails iff:        [quantitative criteria]
   B2 fails iff:        [quantitative criteria]

5. Sanity checks committed:
   S1–S7 (see plan v3 §6.2)

6. Compute: 8×H20 NVLink
7. Data: [list markets + periods]
```

---

*End of plan v3. Next anchor doc rewrite: 当 Gate 2 通过或失败时，写 plan v3.1 反映实际结果。*
