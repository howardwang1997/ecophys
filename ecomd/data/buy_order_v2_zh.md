# 数据采购单 v2 — Path C（高频投入，2026-04-24 修订）

替代 v2 早稿与 v1。对齐 plan v3 + Path C：用户选择承诺高频数据采购，
让 Nature Physics flagship 有物理级 protocol 支撑。论文顺序：
**Paper A → Paper B（NP）→ Paper B.5（PRL）→ Paper C**。

## 预算总盘

| 类别 | 金额 |
|---|---|
| 总预算（已批） | $50,000 |
| **前期锁定（Path C）** | **$8–12k** |
| 预留（Phase 4/5 应急） | $38–42k |

Path C 比纯日线方案前期多投 $3-5k，但 NP 概率从 10-15% 提到 15-22%。
多花的钱买的是对 reviewer 三个主要攻击的物理级回应：Jarzynski work
protocol、TUR 平稳性、T_eff 相对 Mantegna-Stanley 1995 的新颖性。

---

## Tier 0 — 已在 git / 免费（成本 $0）

- **yfinance**：SPY + ^GSPC 日线 2015-2026（管道可扩展到任意 ticker）
- **Binance**：BTCUSDT + ETHUSDT 分钟 2024 Q1（管道可扩展到任意现货对）
- **LOBSTER 免费样本**：8 个 ZIP，2012-06-21（免费学术版）

**够用场景**：v0 到 v1 在 SPX 日线上训练、smoke tests、Mac 开发全程。

---

## Tier A — Paper A（方法论，NeurIPS/ICML），Wk 28 arXiv

- **必需**：无额外采购（v1 在 SPX 日线 + BTC 分钟上训练，已有）
- **推荐**：等 Tier B 的 LOBSTER 采购到位（Wk 16-20）后写一段微观结构附录
- **前期锁定**：$0（所有 LOB 需求由 Tier B 覆盖）

---

## Tier B — Paper B（Nature Physics flagship），Wk 54 投稿

**钱主要花在这里。** Paper B flagship 需要：
- A1 普适性在 ≥3 个时间尺度上验证（日线、分钟、L2 事件级）
- B2 Jarzynski 用物理可接受的 work protocol（FOMC / 财报日 intraday）
- B3 TUR 在 L2 事件速率下（稳态近似最干净）
- 跨资产覆盖：股票 + 加密

### B.1 — Tardis.dev crypto L2（必买，Wk 16）
- **范围**：BTCUSDT + ETHUSDT × **6 个月**（早稿是 3 个月），完整 L2 订单簿 + trades
- **目标价**：**$4,000–$5,500**
- **为什么**：提供最干净的 L2 事件级数据做 B3 TUR 和微观结构时间尺度的跨资产普适性。
  6 个月（不是 3 个月）是为了覆盖 ≥2 次 regime shift 做平稳性检查
- **决策门槛**：Wk 16 v1 在 SPX 日线收敛后买

### B.2 — FirstRate（或 AlgoSeek）美股分钟（必买，Wk 16-17）
- **范围**：20 symbols × **3 年**（优先 2019-2022，覆盖 COVID + 通胀 + SVB），1 分钟
  OHLCV + survivorship-bias-free
- **目标价**：**$1,500–$2,500**
- **为什么**：A1 普适性 claim 在股票 intraday 时间尺度需要。Paper B abstract 的
  "多时间尺度" 措辞必需。顺便支撑 Paper C 的 crash EWS 分钟分辨率
- **决策门槛**：与 B.1 并行采购

### B.3 — LOBSTER 研究订阅（必买，Wk 17-18）
- **范围**：20-50 symbols × **2-3 年**，L10，覆盖 2019-2022 或 2020-2023
- **目标价**：**$3,000–$4,500**
- **为什么**：事件级美股 LOB 做 B3 TUR 饱和、B2 Jarzynski 用开盘/收盘作 protocol、
  A1 事件时间尺度。同时服务 Paper C 最优执行（Tier C 合并到这里）
- **决策门槛**：Wk 17 在 B.1 和 B.2 谈判启动后买

### 跳过
- Bloomberg / Refinitiv 机构级 feeds —— 对我们规模过度
- NASDAQ TotalView 原始 raw —— LOBSTER 重构已覆盖
- FX 供应商（OANDA / Refinitiv FX）—— yfinance EURUSD=X 免费版够用

**Paper B 前期锁定**：**$8.5–12.5k**（early draft 是 $3k）

---

## Tier B.5 — Companion PRL (TUR)，Wk 54

复用 Tier B 数据。**无额外投入**

---

## Tier C — Paper C（应用），Wk 52+

使用 Tier B 已购数据：
- LOBSTER (B.3) → 最优执行
- FirstRate 分钟 (B.2) → crash EWS 分钟分辨率
- Tardis L2 (B.1) → 加密执行 benchmark

**Paper C 前期锁定**：**$0**（全部 Tier B 覆盖）

### Tier C 可选扩展（仅 Paper A/B 进展良好时）
- Bloomberg 企业事件日历（~$500–1000）—— 精确 FOMC / 财报时间戳
- Interactive Brokers / 机构执行磁带（~$1-2k）—— 对标真实经纪商
- **决策门槛**：Wk 40+ 评估，仅 flagship 有望成功时买

---

## 采购时间轴（Path C，对齐 plan v3 修订）

| 周 | 触发条件 | 采购 | $ |
|---|---|---|---|
| **现在（Wk 17）** | v1 开训 | 无（Tier 0 覆盖 v1）| 0 |
| **Wk 17-18** | v1 SPX 日线 works | **Tardis L2 6mo + FirstRate 分钟 3y + LOBSTER 订阅** | **$8.5–12.5k** |
| Wk 18-20 | 数据 ingestion | 无（处理中） | 0 |
| **Wk 20 (M1.5)** | 高频数据就位 | 无（里程碑，不是采购）| 0 |
| Wk 22-28 | v1 + 高频实验 | 无 | 0 |
| Wk 28 (M3) | Paper A arXiv | 无 | 0 |
| Wk 34 (M3.5) | A1 pilot gate | 无（已买）| 0 |
| Wk 40+ | Paper C 应用 | 可选企业事件供应商 | $500–2k |
| Wk 54 (M6) | NP 投稿 | 无 | 0 |

**总前期锁定**：**$8.5–12.5k**（Wk 17-18）
**若加 Tier C 可选扩展**：**$9–14.5k**
**剩余预留**：**$35.5–41.5k**（预算的 71–83%）

---

## Path C 决策流

```
Wk 17 现在：v1 在 SPX 日线收敛
  ↓ 买高频数据包 (Tier B.1 + B.2 + B.3)
Wk 18-20：入库 + 验证 (M1.5 gate)
  ↓ [M1.5 失败 = 供应商延迟] 退回到 Tardis 3mo only，M3 推后到 Wk 30
Wk 28 (M3)：Paper A arXiv + 多尺度 stylized facts 对比表
  ↓
Wk 34 (M3.5)：A1 pilot on 3 markets × 3 timescales
  ├── 通过 ──→ 继续 flagship 到 M6
  └── 失败 ──→ Paper A priority 已锁，退到 2-PRL + 1 QF
              （$8-12k 高频采购不浪费 —— Paper C / PRL / Paper A 参考表都用得上）
```

**关键性质**：即使 flagship 在 M3.5 失败，$8-12k 高频采购**不浪费**——它们喂给 Paper C（Tier C 合并）、PRL 退路论文、Paper A 的 stylized facts 参考表

---

## 为什么与 v2 早稿不同

- v2 早稿（Path C 之前）：$3k Tardis L2 3 个月是唯一高频投入。NP 概率 10-15%
- **v2 Path C**（本版）：$8-12k Tardis 6mo + FirstRate 3y + LOBSTER 3y。NP 概率 15-22%
- 多花的 $5-9k 买了：Jarzynski protocol 可定义 + TUR 平稳性 + 多时间尺度
  普适性——NP 的三大 load-bearing reviewer 防御

## 为什么与 v1（plan v2 时代）不同

- v1 列的数据类似但没有 paper-gate 纪律，前期全部承诺
- v2 Path C 把每笔采购绑到具体的 Paper B claim，并说清 Paper C 已由 Tier B 覆盖

---

## 操作细节

- 每份 vendor package 带 `PROVENANCE.md`（CLAUDE.md 数据纪律要求）
- 原始数据先上 R2（`r2://ecophys/vendor/<vendor>/<date>/`），再通过
  `scripts/h20_pull_from_r2.sh` 同步到 H20 NFS
- 供应商询价模板：`ecomd/data/data_wishlist.md`
