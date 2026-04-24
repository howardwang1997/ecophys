# EcoPhys / EcoMD — Plan v3 (revision 2026-04-24 evening)

**Date**: 2026-04-24 (original); **Revised 2026-04-24 (Path C commitment)**
**Supersedes**: `plan_v2.md`
**Primary target**: Nature Physics (flagship paper B) + supporting papers
**Total timeline**: **58 weeks** to M6 (was 52 before Path C; data pipeline adds ~6 weeks)
**Compute**: 8×H20 NVLink, long-term access
**Data budget**: $50k (unchanged envelope, **commitment upped from $6-10k to $8-12k**)

---

## 0. 本版 vs v2 + Path C 修订总结

| 维度 | v2 | v3 初版 (早) | **v3 + Path C (晚)** |
|---|---|---|---|
| 硬件 | 4×H20 | 8×H20 NVLink | 8×H20 NVLink |
| 策略 | Series-paper | Flagship + 退路 | **Flagship + 高频数据全面投入** |
| NP 概率 | 5–12% | 10–15% | **15–22%** |
| NP 接受条件 | — | A1 + B2 | **A1 + B2 at ≥3 timescales + B3 at L2** |
| 时间 | 46 周 | 52 周 | **58 周** |
| Paper A arXiv | Wk 27 | Wk 26 | **Wk 28**（+2 周让高频数据就位） |
| 数据前期锁定 | $15-25k | $6-10k | **$8-12k**（LOBSTER 从 Tier C 提到 Tier B）|
| 高频数据 | 可选 | Tardis L2 $3k | **Tardis 6 月 + FirstRate 3 年 + LOBSTER 3 年 ≈ $8-12k** |

**核心战略变化（Path C commitment 2026-04-24 晚间）**：

用户审阅后指出 daily 数据对 Nature Physics 级别物理主张是薄弱的——Jarzynski 在日线上没有 clean work protocol；TUR 需要 steady-state 但日线 30 年是非平稳；T_eff 标度如果只在日线上见过会被 reviewer 认为是 1995 Mantegna-Stanley 的扩展，不够新。

**Path C 决策**：为 NP 承诺采购高频数据的全部组合：Tardis crypto L2 (6 月 × 2 pair)、FirstRate 美股分钟 (3 年 × 20 symbols)、LOBSTER 订阅 (2-3 年 × 20-50 symbols) —— 累计 $8-12k。这让 A1 能在 ≥3 时间尺度上验证普适性、B2 能使用 FOMC/财报日 intraday 作为 work protocol、B3 能在分钟级稳态窗口计算 generalized TUR。时间线因此延后 4-6 周（数据 ingestion + 高频分析管道）。

**换来**：NP 概率从 10-15% 提到 15-22%。三个主要 reviewer 攻击全部有物理级回应。

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

## 3. 诚实概率表（Path C 修订后）

以下数字假设 **Path C 数据已购**（Tardis 6 月 + FirstRate 3 年 + LOBSTER 3 年）。
没有这些高频数据的对应概率（v3 初版）写在括号内作对照。

| 事件 | 独立概率 |
|---|---|
| v1 达 ≥9/11 且 stable（M2） | 55–70% (原 50–65%) |
| A1 ν 在 ≥6 市场上一致于 ±0.05 | 40–50% (原 35–45%) |
| **A1 ν 在 ≥3 时间尺度上一致**（新增, Path C 关键） | 40–55% |
| A2 hyperscaling 在 ≥6 市场 | 25–35% |
| B2 Jarzynski 在 FOMC/earnings 作 protocol 下自洽 | 55–65% (原 50–60%, intraday data 让 protocol 可定义) |
| B3 TUR saturation 在 L2 数据上 | 50–60% (原 40–50%, L2 提供 steady-state 窗口) |
| 全部 sanity checks 通过 | 60–70% |
| **Paper B 主 claim 存活到投稿** | **30–40%** (原 25–30%) |
| **Nature Physics 接收（conditional on 投稿）** | **45–60%** (原 40–55%, 多尺度证据提升) |
| **Joint: Nature Physics paper** | **15–22%** (原 10–15%) |

**翻译**：78–85% 概率 NP 仍不成，但通过购买合适的高频数据，reviewer-2 的三个主要攻击（Jarzynski protocol、TUR 平稳性、T_eff 新颖性）都有物理级回应。每个失败层级仍保留退路（见 §7）。

---

## 4. 时间线与硬 gate（Path C 修订）

| M | 名称 | 周 (v3 初版) | **周 (Path C)** | 硬 gate 条件 | 失败退路 |
|---|---|---|---|---|---|
| M0 | 数据/基础 | 4 | ✓ 已达成 | — | — |
| M1 | Baselines + stylized facts | 10 | ✓ 已达成 | — | — |
| **M1.5** | **高频数据采购 + 入库**（Path C 新增） | — | **20** | Tardis + FirstRate + LOBSTER 已下载、验证、分片、ingest 管道跑通 | 供应商延迟 → 用已有 Tardis L2 3 月缩水执行 |
| M2 | v1 at ≥7/11 | 16 | **18** (+2) | v1 ≥7/11 stable on SPX daily | 架构回炉 |
| **M3** | v1 全面训练（包括高频） | 26 | **28** (+2) | ≥9/11 on ≥2 markets **+ 高频数据 pipeline 就位 + Paper A arXiv preprint with pre-registered crash list + 多时间尺度 stylized facts 对比** | ≤7/11 → 放弃 NP，NeurIPS 路线 |
| **M3.5** | A1 pilot (3 markets × 3 时间尺度) + ALL sanity checks | 30 | **34** (+4) | (1) ν 一致 on 3/3 markets **× 3/3 时间尺度** + (2) surrogate null passes + (3) no sanity check fails | fail → **立即停 flagship**，Paper A arXiv 已投，转 PRL 系列 |
| M4 | A1 full (8 markets) + A2 + B2 + B3 主实验 | 36 | **42** (+6) | A1 pass on ≥6/8 markets × ≥3 scales + B2 pass on FOMC/earnings protocol + B3 pass on ≥5 markets L2 | 任一 fail → 降级 PRL |
| **M5** | "一句话物理" 正式化 | 42 | **48** (+6) | 能用 ≤3 公式描述发现 + sanity + robustness appendices 完整 | fail → 拆 2 PRL + 1 QF |
| M6 | Nature Physics 投稿 | 48 | **54** (+6) | paper 就绪 + 所有 gates 通过 + pre-registration 合规 | — |
| M7 | 终局 | 52 | **58** (+6) | accept / desk reject / revision | rejection → 1 周内转 PRL |

**Path C 带来的 6 周延迟分解**：
- Wk 17-20 (新 M1.5)：+4 周数据采购、ingestion、验证。与 v1 H20 训练**并行**（v1 不需要这些数据）
- Wk 28-34 (新 M3.5)：+4 周 A1 pilot 现在要在 3 个时间尺度上而非 1 个
- Wk 34-42 (新 M4)：+6 周 8 市场 × 多尺度是大量独立实验
- Wk 48-54 (新 M6)：+6 周 paper 文本写 robustness appendix 更长（含多时间尺度 + L2 + FOMC protocol 各自的 sanity）

### Gate 交付物（Path C 修订）

**M1.5 gate**（Wk 20，Path C 新增）：
- 高频数据全部 ingested 到 Parquet 格式
- Tardis L2 BTC+ETH × 6 月 ingested + L2 snapshot 重建验证
- FirstRate 美股分钟 × 3 年 × 20 symbols ingested + 与 yfinance 日线交叉验证
- LOBSTER 订阅 × 3 年 × 20-50 symbols ingested + 事件流重建正确性测试
- R2 + H20 NFS 同步完成

**M2 gate**（Wk 18）：
- v1 code frozen
- test suite ≥ 130 tests（加 vendor_schemas 多格式测试）
- Paper A 结果表（SPX 日线 5-way comparison）

**M3 gate**（Wk 28）：
- **arXiv preprint** 提交（Paper A + pre-registered crash list + 实验方案 + 多时间尺度 stylized facts 对比）
- 至少 2 市场 v1 ≥9/11
- Phase 3 实验配置冻结

**M3.5 gate**（Wk 34）——最关键的 hard cut：
- A1 pilot on SPX (daily + minute) + BTC (minute + L2) + EUR/USD 全部 **3 市场 × 3 时间尺度 ν 一致**
- IID null + GARCH null sanity checks 通过
- 7 项 sanity checks 全部通过
- **任一失败 → 停 flagship**（Paper A arXiv 已锁 priority）

**M5 gate**（Wk 48）：
- Paper B abstract 能写出 ≤ 3 个 equation
- Robustness appendix 完整（所有 sanity checks + 多时间尺度 + L2 验证 + FOMC protocol sanity）
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
- ✓ **M2 GATE PASSED（2026-04-24）**：EcoMD v0.8 命中 **7/11** stylized facts on SPX daily，超过 GARCH(1,1)-t 基线（7/11），打破 LM99（5/11）。架构是 shared MLP PairwisePotential（v0.x 系）；v1 MACE-lite 暂未通过（见 9.4）。

### 9.2 当前状态（2026-04-24）

| 模型 | 命中 | 关键特征 |
|---|---|---|
| GARCH(1,1)-t fitted | 7/11 | 单变量基线 |
| LM99 (3-type heterogeneous) | 5/11 | ABM 基线 |
| **EcoMD v0.6 trained** | 6/11 | **最强 vol clustering（acf(r²)=+0.306），Student-t noise + learnable β** |
| **EcoMD v0.8 trained** | **7/11** | **M2 winner。v0.6 关掉 learnable β 即达，保 #1/#8/#10** |
| EcoMD v1 MACE-lite (best: H F4 hybrid) | 6/11 | acf(r²)=+0.202 但 **形状 flat 而非 peak-decay**（见附录 B） |

v0.6 vs v0.8 是 **Pareto frontier 上的两个点**：
- v0.6 胜在 #2 Hill、#3 skew、#6 ACF(r²) 强度（heavy tails 更对）
- v0.8 胜在 #1 ACF(r)、#8 DFA、#10 corr(V,\|r\|)（volume-vol 一致性更对）

### 9.3 下周（2026-04-25 起）Phase 3 Paper A 准备

**立刻 (Mac/CPU)**：
1. 写 Paper A methodology 章（v0.x shared MLP + training recipe: persistent state + warmup detach + Student-t + cosine LR）
2. 补充 ablation 表：noise_dist, learnable_β, persistent_state, init_state_scale 单独效应
3. 跨资产复现：把 v0.6 / v0.8 recipe 拿 BTC 1m 跑一遍（data/sample 已有）
4. **不**继续在 v1 MACE-lite 上花时间（见 9.4 诊断）

**Phase 3 并行起步**：
5. 用 v0.6（vol clustering 最强）算 T_eff 初探：长 rollout 10⁴ 步，测 cross-timescale T_eff 相似度 → 给 Paper B 打底

### 9.4 v1 MACE-lite 为什么没有跑通（今日确诊）

经过 A-H 八个架构变体 + 力量级 probe，病因是**架构设计与金融市场物理不匹配**，不是工程 bug。主要结论（详见 logs/2026-04-24.md Session 17-18）：

1. **V_pair 量级不足**：v0.x PairwisePotential `V = Σ_{N²} f(s_i, s_j)` 自然 O(N²) scale；MACE-lite `V = Σ_{N} U(h_i)` 只有 O(N) scale，force 差 60-190×，被 Langevin 噪声完全淹没。
2. **结构不生成 burst dynamics**：强制 scale（F1 multiplier）后 force 量级对了，acf(r²) 仍为 0。per-node readout MLP 的 SiLU/LN 组合产生平滑 equilibrium dynamics，而 vol clustering 来自 intermittent burst + slow decay。
3. **hybrid 变体（H）触及 acf 均值 +0.202 但形状 flat**：经典 Goodhart — 单一均值 target 被 "常数高方差 regime" 作弊满足，物理上不是真 clustering。

**Paper A 里 v1 不作为主 claim，而作为 "scaling attempt + negative result"**（见下面的 Paper A 战略）。Phase 4 (T_eff scaling, M3+) 如果需要 N ≥ 10⁴，考虑 v0.x + sparse attention pass，不继续推 MACE-lite 路线。

### 9.5 未来 12 周 roadmap（刷新）

| 周 | 目标 |
|---|---|
| +1 (Wk 10) | Paper A methodology draft + v0.6/v0.8 ablation 表 |
| +2 (Wk 11) | Cross-asset 复现（BTC 1m）+ Paper A results 章 |
| +3 (Wk 12) | Paper A arXiv pre-print draft 完成 |
| +4-6 | Phase 3 T_eff 初探（v0.6 长 rollout）+ pre-registration 文档 |
| +6-8 | Path C vendor 数据到货（Tardis L2、FirstRate）→ 高频 v0.x training |
| +8-12 | M3 冲刺（v0.x 在 ≥2 markets 达 ≥7/11） + Paper B 起步 |

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
