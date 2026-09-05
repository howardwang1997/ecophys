# EcoMD 数据资产：采购与使用决策（2026-09-05）

## 结论

普通订单簿数据的价值在于工程验证、测量与校准；它们不能单独支持“模拟器能够
预测市场机制干预之反事实响应”的结论。数据采购应分阶段进行：先用免费源完成
事件语法与重放基础设施，之后才为一项已冻结、可证伪的假设购买最小历史面板。
在没有合格 re-entry trigger 和 machine decision 前，不下载、购买、采集或启动 GPU
实验。

本文件是数据选择的决策记录，不是对数据供应商价格、可用性或再分发权的永久
承诺。购买前须重新核对当日报价、许可、地域限制、存储和再分发条件。

## 数据能力分层

| 层级 | 资产 | 成本模式 | 可支持的工作 | 不能支持的结论 |
|---|---|---|---|---|
| P0 | IEX HIST/DEEP+ | 免费 | 展示订单事件表示、盘口重放、校准和时间留出评测 | 完整市场状态或机制干预的因果反事实 |
| P0 | Coinbase Exchange full/L3 的前瞻性自建归档 | 数据免费；有采集/存储成本 | 含订单状态变化的在线消息生命周期、断档恢复和数据管线测试 | 可公开复查的历史真值、已分配处理或潜在结果 |
| P0 | Nasdaq ITCH 样例及解析器 | 免费 | schema、parser、顺序重放的单元/集成测试 | 有统计效力的市场实证 |
| P0 | QuantReplay、intrepidkarthi/orderbook | 免费开源 | 独立撮合实现间的一致性与回归测试 | 独立外部市场响应真值 |
| P1 | Nasdaq TotalView-ITCH（经 Databento 或交易所） | 按量/许可付费 | 订单级展示流动性、撤单/成交/队列的历史重放与留出验证 | 隐藏流动性、跨场所完整状态、随机规则干预 |
| P1 | LOBSTER 学术数据 | 许可付费 | NASDAQ 消息流与 L10 重构订单簿；与 order-book ML 文献可比 | 交易所内部完整状态或个体策略真值 |
| P1 | Tardis 多交易所加密历史数据 | 订阅/按计划付费 | 跨场所 L2 复现、流动性与波动稳健性检验 | 逐订单身份、完整生命周期和真实处理分配 |
| P2 | 前瞻性受控连续双边拍卖（CDA）真值资产 | 专项建设/合作成本 | 机制干预、状态保持反事实、独立确认和模拟器有效性 | 不适用；这是能解除该缺口的资产类别 |

## P0：立即可用的免费开发资产

### IEX HIST 与 DEEP+

IEX 提供免费 T+1 HIST 下载，并保留滚动的最近 12 个月；DEEP+ 提供每一个**展示的**
静态订单。其文档也明确排除非展示订单及 reserve order 的非展示部分。因此它应被
标注为“展示订单簿测量资产”，不能被描述为完整订单簿或完整市场状态。

- 官方资料：[IEX market-data connectivity](https://www.iex.io/products/equities/market-data-connectivity)
- 推荐用途：确定统一 event grammar；验证 book reconstruction、守恒约束和
  time-split 的 forecast metrics。
- 禁止推论：由其遗漏部分反推隐藏流动性、交易者策略或干预响应。

### Coinbase Exchange full/L3

Coinbase 的公开 `full` 频道逐条发出 `received`、`open`、`done`、`match`、`change`
和 `activate` 等状态事件，并携带订单与成交字段。它适合作为**从现在起**可自行
治理的采集源；采集器必须记录序列、断线与恢复过程，且其历史归档资格与许可须在
实际启动前冻结。

- 官方资料：[WebSocket feed overview](https://docs.cdp.coinbase.com/exchange/websocket-feed/overview)，[channels](https://docs.cdp.coinbase.com/exchange/websocket-feed/channels)
- 推荐用途：测试订单生命周期表、重复消息处理与缺口检测。
- 禁止推论：公开实时 feed 不自动构成完整、不可变、可审计的历史真值库。

### 开源撮合实现

[QuantReplay](https://github.com/Quod-Financial/quantreplay)（Apache-2.0）和
[intrepidkarthi/orderbook](https://github.com/intrepidkarthi/orderbook)（MIT）可作为不同
代码路径的撮合一致性参照。它们的角色是测试基础设施，而非来自独立市场的观测或
因果验证数据。

## P1：仅在冻结问题后购买的历史验证资产

### 首选：小面板 Nasdaq TotalView-ITCH

TotalView-ITCH 是 Nasdaq 的订单级全深度展示市场数据。Databento 将其作为历史
数据 schema 提供，并按其当前 data catalog/estimator 计费。小面板应先覆盖：

1. 5--10 只按流动性分层的股票；
2. 20--60 个正常交易日作为开发/验证区间；
3. 一段按时间隔离、绝不用于调参的确认区间；
4. 预先写明的盘口重放、订单寿命、取消/成交 hazard 和留出误差指标。

这样购买的目的，是最快否证一个指定的表示或模拟器假设，而不是扩大可讲述的
实证样本。任何购买前均须以供应商估算器重新取得价格，并审查是否允许本地归档、
团队访问、论文复现和派生数据发布。

- 官方资料：[Databento pricing](https://databento.com/pricing)，[Nasdaq TotalView-ITCH overview](https://databento.com/blog/nasdaq-totalview-live)，[Nasdaq historical TotalView-ITCH description](https://www.nasdaqtrader.com/TraderNews.aspx?id=dtn2009-001)

### 备选：LOBSTER

若问题需要同现有 order-book ML 基准进行严格可比的 NASDAQ L10 重构订单簿，选择
LOBSTER；否则它与 TotalView-ITCH 的能力高度重叠，不应双重采购。其学术价、可用
年份和许可按当前官方价目表确认。

- 官方资料：[LOBSTER academic price list](https://lobsterdata.com/info/docs/legal/LOBSTER_priceList.pdf)

### 加密多场所稳健性：Tardis

只有当已冻结的假设明确要求“同一可观测量跨加密交易所是否稳健”时，才购买
Tardis。它能提供逐笔交易和按交易所不同而异的 L2 snapshots/updates，适合市场
测量，但不将 L2 更新转化为订单身份、交易者状态或因果处理。

- 官方资料：[Tardis data FAQ](https://docs.tardis.dev/faq/data)，[Tardis HTTP API](https://docs.tardis.dev/api/http-api-reference)

## P2：真正需要建设的真值资产

若目标是新的 ICLR simulator-method 论文，而非仅仅是订单簿预测论文，必须取得或
建设具有下列字段的受控 CDA 数据：

- 完整请求、替换、撤单、拒绝与成交生命周期，以及稳定的 order/execution/actor ID；
- 决策、服务器接收、撮合的时间戳；操作前后 book state hash；
- 初始现金/库存、信息日程、撮合规则、调度器与 RNG 状态，能够独立确定性重放；
- 合法的随机规则处理、冻结的分析计划，以及未拆封的独立确认站点；
- 明确的存储、再分发、匿名化与研究伦理权利。

这不是“再买一份更贵的 L3 数据”可替代的要求。完整字段和双站点要求以
[`ecomd_truth_asset_capability_build_plan_2026-08-26.md`](../papers/proposal/ecomd_truth_asset_capability_build_plan_2026-08-26.md)
和当前 discovery protocol 为准。

## 采购决策规则

1. 现在不采购大范围、多年份、全市场数据订阅。
2. 任何 P1 采购必须先对应一个已写清的 estimand、竞争解释、最小 falsification
   slice、时间留出与停止规则。
3. 若仅需开发，优先 P0；若需历史的订单级测量验证，优先小面板 TotalView-ITCH；若
   需要文献 benchmark 可比性，选择 LOBSTER；若需要加密跨场所复制，才选择 Tardis。
4. P0/P1 的正结果只能作为能力与测量证据，不能解除项目当前的反事实真值阻塞。
5. P2 的任何采集、合作、参与者接触、数据访问或计算启动，均须先满足 protocol 中
   的 re-entry trigger 与 machine decision。

## 当前推荐配置

**IEX + Coinbase（免费开发） → 最小 TotalView-ITCH 面板（付费、仅在假设冻结后）
→ 受控 CDA 真值资产（仅在有合格触发器后）**。

该顺序把不可逆支出放在可证伪问题之后，并把“普通 L3 数据足够做工程”与“完整
干预真值才可能支撑因果模拟器结论”明确分开。

## 预算与进入时点（2026-09-05 估算）

以下是规划额度而非采购授权；币种为 USD，人民币按 2026-09-04 附近的
USD/CNY 约 6.71 作粗略换算。供应商价格、税费和许可会变动，付款前必须重新取得
供应商报价或使用其价格估算器。

| 资产 | 何时才需要 | 最小可行购买/留存范围 | 数据费估算 | 存储或附加成本 | 决策 |
|---|---|---|---:|---:|---|
| IEX HIST/DEEP+ | 获得 machine decision，且事件 schema/重放单测已冻结后 | 单一普通周或月作为开发 fixture | $0 | R2 100 GB 约 $1.35/月；1 TB 约 $14.85/月 | 仅 P0，先不启动 |
| Coinbase full/L3 归档 | 有被批准的 prospective recorder，且问题确实需要订单生命周期时 | 先限 BTC-USD、ETH-USD；至少保留一个独立的时间留出区间 | $0 | 以实际压缩体积计；0.5--2 TB 约 $7.35--29.85/月 | 仅 P0，先不启动 |
| Databento TotalView-ITCH MBO | 一个明确的 L3 表示/重放假设已冻结，且 P0 测试通过后 | 5--10 只股票 × 20--60 个正常交易日，另隔离确认期 | **$0--125** 为首轮硬上限，优先使用新团队 $125 historical credit；超过前必须调用 `metadata.get_cost` | 小面板通常不构成实质成本；按实际压缩后对象量计 | P1 的首选付费验证；不预购多年数据 |
| LOBSTER | 只有在“必须与 L10 order-book ML 基准直接对比”被写入假设时 | 学术机构一年订阅 | **£5,397 首年**（£4,897 年费 + £500 setup，未含 VAT），约 **$7.3k / ¥4.9 万**；续费约 £4,897 | 订阅含 1 TB 供应商端 raw storage；本地/R2 另计 | 同 ITCH 高度重叠；二者二选一，默认不买 |
| Tardis | 只有在冻结问题要求多加密交易所、L2 跨场所重复时 | 按计划选择 Spot、Perpetuals、Derivatives 或 All Exchanges；学术档需季度/年度付款 | Academic：Perpetuals $350/月、Spot $450/月、Derivatives $450/月、All $650/月；季度最低约 $1,050/$1,350/$1,350/$1,950 | 下载/归档量可能较大；1 TB R2 Standard 约 $14.85/月 | 不是生命周期真值；默认不买 |
| 两站点受控 CDA 真值资产 | 仅在 qualified re-entry trigger、冻结 estimand、预注册及独立确认设计完成后 | discovery + confirmation，各站点 32 sessions 的历史规划口径 | **上限 $20k/站点，合计 $40k**，含参与者补偿；不含已投入工程、运营和可能的伦理费用 | 另行核算；当前不授权 | 唯一可能解除反事实真值缺口的类别 |

### 价格解释与不确定性

- Databento 的历史数据按用量计费；其 API 的 `metadata.get_cost` 能在请求前返回特定
  symbol/date/schema 的美元价格。新团队当前有 $125 historical credit，且 credit 六个月
 失效。因此“$0--125”是刻意设定的第一轮止损线，而不是对全样本成本的猜测。
  [定价与 credit](https://databento.com/pricing)，[预先估价 API](https://databento.com/docs/api-reference-historical/basics/authentication?historical=http&live=http)
- LOBSTER 官方学术一年 flat-rate 是 £4,897，加首年 £500 setup，最低合同期一年，价格不
  含 VAT；数据供给及 NASDAQ academic waiver 条件需在采购时确认。
  [官方价目表](https://lobsterdata.com/info/docs/legal/LOBSTER_priceList.pdf)
- Tardis 的公开 Academic 价随 data plan 不同；Academic/Solo 只有 CSV 下载，年度付款
  提供四年历史，季度付款提供十二个月历史，月度付款提供四个月历史。上表采用当前公开
  学术价及其“季度或年度付款”限制，不把旧项目预算当作现价。
  [公开定价](https://tardis.dev/)，[订阅与历史范围](https://docs.tardis.dev/faq/billing-and-subscriptions)
- R2 Standard 当前为 $0.015/GB-month、每月前 10 GB 免费且无 egress 费；表内仅用这个
  费率换算容量，未声称上述数据源必然产生给定体积。
  [Cloudflare R2 定价](https://developers.cloudflare.com/r2/pricing/)
- $20k/站点是仓库中冻结的**上限**，不是供应商报价、已获资金或已证明可执行的预算；它
  明确不授权招募、联络、支出、结果访问或计算。
  [成本上限附录](../papers/proposal/ecomd_truth_asset_cost_ceiling_addendum_2026-08-27.md)

### 时间顺序：以门槛而非日历驱动

1. **现在：$0。** 当前没有 qualified re-entry trigger 或 machine decision，故不采集、
   购买或跑实验；三台 GPU 不应因数据订阅而启动。
2. **P0 被授权后的第 1 周：$0--15/月量级。** 固定 IEX/ITCH fixture，完成 schema、重放和
   gap-detection 验收。只有需要前瞻性生命周期时才启动 Coinbase recorder。
3. **P0 通过且出现明确、可被历史 L3 推翻的假设后：一次性 $0--125。** 用 Databento
   credit 下载最小时间冻结面板；若估价高于 $125 或假设在该面板不可判别，即停止而非扩容。
4. **只有该假设在最小面板仍存活并明确要求额外外推时：$1.05k--$7.3k+。** Tardis 或
   LOBSTER 二选一，取决于“多交易所加密复制”还是“NASDAQ L10 benchmark”；不是两者都买。
5. **只有产生真正的机制/反事实 topic machine card 后：最多 $40k 加另行审批的运营成本。**
   此时才规划两个独立 CDA 站点；数据订阅的正结果不能跳过此门槛。
