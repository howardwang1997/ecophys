# 数据采购单 v2 — 按论文顺序（2026-04-24）

替代 `buy_order_zh.md`（v1）。采购优先级按 plan v3 的论文投稿顺序重排：
**Paper A → Paper B（Nature Physics）→ Paper B.5（companion PRL）→ Paper C**。
只买每篇论文真正 load-bearing 的数据，按论文出稿顺序采购。

## 预算总盘

| 类别 | 金额 |
|---|---|
| 总预算（已批） | $50,000 |
| **前期锁定投入** | **$6–10k** |
| 预留（Phase 4/5 应急） | $40–44k |

预留重设计：plan v3 承认 flagship 失败概率不低，多数预算保持流动让我们在
Gate 2（M3.5）分叉时可以灵活切换数据采购方向。

---

## Tier 0 — 已在仓库 / 免费（成本 $0）

已提交到 git `data/sample/`：

- **yfinance**：SPY + ^GSPC 日线，2015–2026。管道可扩展到任意 ticker。
- **Binance**：BTCUSDT + ETHUSDT 分钟，2024 Q1。管道可扩展到任意现货对。
- **LOBSTER 免费样本**：8 个 ZIP（AAPL、AMZN、GOOG、MSFT、SPY）× 2012-06-21。

**够用场景**：v0 到 v1 训练、smoke tests、M2（Wk 16）之前的全部开发工作。

---

## Tier A — Paper A（方法论，NeurIPS/ICML main），Wk 26 arXiv

Paper A 在 M3（Wk 26）出稿。它需要：

- v1 训练用的 SPX + BTC 收益率（✓ Tier 0 已有）
- 11 项 Cont stylized facts 对比表（✓ experiments 000–005 已出）
- 可选：微观结构附录与 LOB 对比

### 必需
**无**。Paper A 可以只靠免费数据出稿。

### 推荐（如果想要 LOB 微观结构章节）
- **LOBSTER 学术订阅**：10–20 symbols × 1 个月，L10
  - **目标价**：$500–$1,500
  - **为什么**：Paper A 的 reviewer-2 会问 "你的 agent 模拟器与真实 LOB 微观结构是否
    匹配？" 回答需要至少 20k 事件在 5+ symbols 上
  - **决策门槛**：**仅当 v1 在 SPX 上达到 ≥7/11**（M2，~Wk 16）时才买。
    如果 v1 卡住，这笔钱转入预留
 
### 跳过
- 任何报价 > $2k 的 LOB sample —— 免费 LOBSTER sample + 后面 Tier C 的订阅更便宜
  且覆盖同一 claim

**Paper A 前期锁定**：$0（保证）；$500–1500 取决于 M2 成功与否。

---

## Tier B — Paper B（Nature Physics flagship），Wk 48 投稿

Paper B 是 flagship。它的 load-bearing claim 是跨市场普适性（A1：T_eff 标度）+
Jarzynski 自洽（B2）。Gate 2（Wk 30）如果普适性失败就 kill Paper B，所以数据
必须在 Wk 28–30 到位。

### 必需
8 个市场 × 多年收益率。大部分 yfinance 免费：

| 市场 | Ticker | 成本 |
|---|---|---|
| S&P 500 | ^GSPC | $0（✓ 已有）|
| Russell 2000 | ^RUT | $0（yfinance）|
| 日经 225 | ^N225 | $0（yfinance）|
| DAX 30 | ^GDAXI | $0（yfinance）|
| FTSE 100 | ^FTSE | $0（yfinance）|
| 恒生 | ^HSI | $0（yfinance）|
| 比特币 | BTCUSDT | $0（✓ 已有）|
| 以太币 | ETHUSDT | $0（✓ 已有）|
| （外汇 可选）| EURUSD=X | $0（yfinance）|

只需将现有 yfinance ingest 脚本扩展到新的 tickers，不需要任何第三方供应商。

### 强烈推荐
- **Tardis.dev crypto L2 数据**：BTCUSDT + ETHUSDT × 3 个月，完整订单簿变更
  - **目标价**：$2,500–$3,500
  - **为什么**：A1 普适性 claim 如果只基于日线，会被 "你没在微观结构时间尺度测试"
    这一攻击拆穿。Tardis L2（跨资产 L2 的最便宜路径）关掉这个攻击面
  - **决策门槛**：Wk 27 买。Gate 2（3 市场日线 A1 pilot）若看似有希望即买

### 跳过
- 更高端的股票 LOB 用于普适性实验（比如 $10k+ 的分钟数据供应商）。
  日线 + crypto L2 已足以支撑普适性 claim；不要过度采购

**Paper B 前期锁定**：$0（保证）；**$3k 取决于** Gate 2 pilot 看到希望

---

## Tier B.5 — Companion PRL（TUR 饱和）

复用 Paper B 的数据。**无额外投入**。

---

## Tier C — Paper C（应用，QF/JEDC），Wk 45+

Paper C 两个产出：crash EWS（复用 Paper B 数据）+ 最优执行（需要 LOB 消息）

### 必需（仅针对最优执行产出）
- **LOBSTER 研究订阅** 或 **AlgoSeek LOB feed**
  - 20–50 symbols × 2–3 年，L10，覆盖 2019–2022 或 2020–2023
  - **目标价**：$3,000–$5,000
  - **为什么**：没有真实 LOB 消息无法 benchmark 执行策略。免费 LOBSTER sample 只
    覆盖 1 天 × 8 symbols —— 不足以稳健训练 RL 或做 Almgren-Chriss 回测
  - **决策门槛**：仅当 Paper A 被接收或明显在正轨上（Wk 34）时才买

### 跳过
- 机构级 feeds（NASDAQ TotalView direct）—— 对我们的规模过度
- 替代数据 / 新闻 / 情绪数据 —— 超 Paper C 范围

**Paper C 前期锁定**：$3–5k 取决于 Paper A 投稿轨迹

---

## 采购时间轴（对齐 plan v3 gates）

| 周 | 触发条件 | 采购 | $ |
|---|---|---|---|
| **现在（Wk ~17）** | v1 在 H20 开训 | 无 | 0 |
| Wk 22–24 | v1 收敛 ≥7/11 | 无（现有数据跑） | 0 |
| Wk 26 | **M3 arXiv 投稿** | yfinance 扩展 8 市场（免费）| 0 |
| Wk 27–28 | **Gate 2 A1 pilot 之前** | （可选）Tardis crypto L2 | $3k |
| Wk 30 | **Gate 2 结果** | （视情况）小 LOBSTER 用于 Paper A 修订 | $500–1500 |
| Wk 34–36 | Paper C 启动、A1 full 推进 | （视情况）LOBSTER 订阅 | $3–5k |
| Wk 48+ | Paper B/B.5 投稿 | 无（数据已锁）| 0 |

**最大前期投入**：$6.5–9.5k，占 $50k 预算的 13–19%

---

## 流程图 — 决策节点

```
现在 ───── v1 跑免费数据 ──────────────┐
                                        │
                              v1 ≥ 7/11 ?
                                ├── 否 ──→ 继续免费数据，迭代架构
                                └── 是 ──→ Wk 26：arXiv Paper A preprint
                                            │
                                            ↓
                              Wk 27：买 Tardis crypto L2？($3k)
                                ├── （Gate 2 pilot 看好）是 ─→ 买
                                └── （Gate 2 pilot 弱）    否 ─→ 留作预留
                                            │
                                            ↓
                              Wk 30 Gate 2：A1 pilot 普适性？
                                ├── 通过 ──→ Paper B flagship 继续；
                                │            Wk 34：买 LOBSTER ($3–5k) 用于 Paper C
                                └── 失败 ──→ 退到 2-PRL 拆分；
                                             暂时不买 LOBSTER
                                             （Paper C 延后）
```

---

## 操作细节

- 给供应商的询价模板在 `ecomd/data/data_wishlist.md`
- 所有采购先进 R2（`r2://ecophys/vendor/<vendor>/<date>/`），再通过
  `scripts/h20_pull_from_r2.sh` 同步到 H20 NFS
- 每份 vendor package 要附带 provenance 文件（其目录下 `PROVENANCE.md`），
  符合 `CLAUDE.md` 的数据纪律规则

---

## 为什么与 buy_order_v1 不同

- v1 在 plan v2（系列论文，无 Nature Physics 承诺）下写的，把美股分钟 + LOB 
  采购都前置了
- v2 在 plan v3（Nature Physics flagship + 退路）下写的，把较大的 LOB 开支
  延后到 Paper C / Tier C，并且把 Tardis crypto L2 作为 Paper B 普适性 claim
  下最划算的单次采购
- 净效果：前期承诺更少、Phase 4/5 预留更多、采购由真实研究里程碑触发
