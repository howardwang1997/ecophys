# Binance taker-flow response/relaxation 可行性冻结（2026-08-11）

## 研究边界

日频 lagged-regime 实验未能把弱 signal 与慢变共同宏观结构区分开。下一步先验证一个机制更近、但仍然
低成本的测量：极端 taker-flow imbalance 后，价格是否在短期沿 flow 方向响应，并在 60 分钟内部分
relax。这里的 flow 是 Binance 成交 bars 中的 aggressive buy/sell quote-volume imbalance，明确命名为
`taker_flow_imbalance`；它不是 Cont--Kukanov--Stoikov L2 OFI，也不能被写成 order-book liquidity。

本实验只决定是否值得下载更大的 fresh-quarter `aggTrades` 做真正 event-time confirmation。PASS 不是
物理定律、论文 claim 或 EcoMD 训练许可；FAIL 则停止这条 flow-relaxation 路线，不继续下载 bulk
`aggTrades`。

## 免费数据与 archive integrity

冻结 BTCUSDT、ETHUSDT、SOLUSDT spot 1m klines，2024 Q1。January 只拟合 threshold，February 是
confirmation，March 是 temporal test。官方 archive 每个 ZIP 必须匹配同目录 `.CHECKSUM`，并满足完整
UTC minute grid：January/March 各 44,640 行，leap-year February 41,760 行。

Binance 官方 [public-data README](https://github.com/binance/binance-public-data/blob/master/README.md) 说明了
kline schema、checksum 和 2025 起 spot timestamp 由毫秒切到微秒。本实验只用 2024，强制毫秒。鉴于
官方 issue tracker 已有 [monthly/daily kline 不一致报告](https://github.com/binance/binance-public-data/issues/475)，
预先固定每月 1 日、15 日和末日，共九个 dates；三个 symbols 的 daily archive 必须与 monthly slice
逐行、全列完全相等。任何 mismatch 都停止，不静默改用 daily data。

Raw ZIP 不提交、不再分发；git 只保存无价格/flow values 的 provenance manifest 和 derived result。

## Observable 与事件

每分钟定义

```text
I_t = (2 * taker_buy_quote_t - quote_volume_t) / quote_volume_t .
```

January 按 symbol 冻结 `|I|` 的 99% quantile。February/March 只选择严格超过该 threshold 的 minutes。
每个 UTC day 从 minute index 61 到 1379 顺序扫描；选中后 61 分钟内不再选，保证 60-minute response
windows 不重叠。选择不看当前或未来 return，只使用当前 `|I|` 和过去选中时间。每个 symbol-month 至少
20 个 events，否则 fail closed。

实现前、任何 imbalance/response 输出前发现原冻结写的是 index 60，但同一协议又声明每个 UTC day 的
index-0 close-to-close return 不可用；index 60 因而只有 59 个有效 past returns。唯一的 pre-output
correction 是把 first eligible index 从 60 改为 61。数据、threshold、horizons、separation 和 gates 不变。

Pre-volatility 是前 60 分钟 close-to-close returns 的 RMS。对 `h=1,2,5,10,30,60`，

```text
R_h = sign(I_t) * [log C_(t+h) - log C_t] / [sigma_pre * sqrt(h)] .
```

`early = mean(R_1,R_2,R_5)`，`late=R_60`，`decay=early-late`。先在每个 symbol-day 内平均 events，再
对有 event 的 asset-days 等权，避免 BTC 的 event 数支配结果。

## Dependence-aware null 与 gate

Null 在每个 UTC day 把完整 imbalance-sign sequence circular shift 61--1379 分钟；同一天三个资产使用
相同 shift，保留 event times、绝对 imbalance、volatility 和跨资产 calendar dependence，只打破正确
flow sign 与 future return 的对齐。每个 evaluation month 做 999 次，一侧 p-value 上限 0.05。

另以共同 UTC day 为 cluster 做 5,000 次 bootstrap；同一次重采样保留三个资产。January 只要求三个
symbols 的 contemporaneous signed response 都为正，以验证 sign convention。

Primary PASS 要求全部同时成立：

1. February/March 的六个 symbol-month 都有至少 20 events；
2. 六个 symbol-month 的 early 和 decay 都严格为正；
3. 两个月各自 pooled early 至少 0.05，`decay/early` 至少 0.20；
4. 两个月各自 circular-sign p <= 0.05；
5. 两个月各自 calendar-day bootstrap 90% decay CI 下界 > 0。

如果 response 为永久、不衰减或形状错误，不能事后改写成另一条 headline；只能作为完整诊断报告。
全流程 CPU-only、免费数据、禁止 GPU，两张 V100 保持空闲。

## 已知局限

- 1m bar 只给成交聚合，无法观察 limit-book queue、spread 或 CKS OFI；
- 三个资产来自同一交易所，独立性主要来自 calendar days，不是三套市场机制；
- Flow 与 return 都是观察量，PASS 仍不是外生冲击或因果 identification；
- 已有 market-impact/propagator 文献很强。即使通过，下一步也必须做 prior-art audit 和 fresh
  `aggTrades` event-time confirmation，不能把 basic response 当 novelty。
