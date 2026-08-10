# Binance taker-flow response/relaxation 可行性结果（2026-08-11）

## 结论

预注册 feasibility gate **FAIL**，因此停止 taker-flow relaxation 路线，不下载 bulk `aggTrades`，不启动
EcoMD。失败不是 archive、样本量或 sign convention 问题：全部 checksum/grid/crosscheck 已通过，六个
evaluation symbol-month 均远超 20-event floor，January 三资产 contemporaneous signed response 都强正。

真正失败的是跨月份、跨资产的 response shape。February pooled curve 有显著 early-to-late reversal，
但 BTC early response 已为负且 pooled early 低于 practical floor；March 只在 BTC 上出现正向 relaxation，
ETH/SOL 的 early 与 decay 都为负，pooled circular-sign `p=0.562`、bootstrap interval 跨零。不能把一个
month/asset-specific pattern 写成 universal physical relaxation law。

## 正式性与 provenance

- artifact：`results/empirical_physics/taker_flow_response_feasibility_v1.json`；
- clean HEAD/upstream：`cf72e3435b771cdca279d86422664da5fab9a836`；
- canonical payload SHA：`c30f716fe985052643ddcc0c7d02cd105c23634367a7f0e17dca0dc3a6bc89e1`；
- file SHA：`78d90818bd949faeb6ce2daa131279accff4d12f74758fb8f926bcd081ff3eed`；
- analysis protocol SHA：`6b14e9daa61c2fdf3c5b84b8356ea08312780ca0adca4b0cd6a32e1427695941`；
- manifest canonical/file SHA：`ea05914ce27307b597e2824d4f3d2ecfcc221b9489cf72c906a4689a9344be1f` /
  `d0fff2a28a0a6c1a0c1b77fcc8fd9065ae612acd940c7091106a886200fbeaaa`；
- artifact 内部计时 1.78 s；CPU-only，`gpu_used=false`；
- pre-output correction 只把 first eligible minute 从 60 改为 61，以满足同一协议的 60 个有效 past
  returns；correction 在任何 imbalance/event/response 输出前完成并写入 artifact。

数据完整性保持 binding：9/9 monthly、27/27 daily archives 和 36/36 official checksums 通过，所有
预选 monthly/daily slices 全列逐行一致。Raw bytes 未提交或再分发。

## Threshold 与 measurement sanity

January 99% absolute-imbalance thresholds 是 BTC 0.8810、ETH 0.8715、SOL 0.8287。January 只验证
measurement/sign，不进入 primary evidence：

| Symbol | Selected events | Asset-days | Mean contemporaneous signed response | Sanity |
|---|---:|---:|---:|---|
| BTCUSDT | 176 | 29 | 1.299 pre-vol units | PASS |
| ETHUSDT | 186 | 29 | 1.235 | PASS |
| SOLUSDT | 178 | 30 | 0.996 | PASS |

这证明 `(2*taker_buy_quote-quote_volume)/quote_volume` 的方向与分钟内价格移动一致。它只验证
`taker_flow_imbalance`，不把该量升级为 CKS OFI、L2 liquidity 或外生冲击。

## Evaluation curves

Curve 顺序为 h=1,2,5,10,30,60 minutes；所有 response 都按 past-60min volatility 与 `sqrt(h)` 标准化。

| Month / symbol | Events | Curve | Early | Late | Decay |
|---|---:|---|---:|---:|---:|
| Feb pooled | 715 | [0.039, 0.065, 0.023, -0.067, -0.084, -0.102] | 0.0426 | -0.1024 | +0.1450 |
| Feb BTC | 188 | [-0.031, 0.019, 0.000, -0.052, -0.055, -0.164] | -0.0041 | -0.1643 | +0.1602 |
| Feb ETH | 206 | [0.098, 0.084, 0.040, -0.038, -0.034, -0.030] | +0.0740 | -0.0304 | +0.1044 |
| Feb SOL | 321 | [0.047, 0.089, 0.028, -0.110, -0.161, -0.117] | +0.0546 | -0.1170 | +0.1716 |
| Mar pooled | 254 | [0.006, 0.019, 0.075, 0.147, 0.006, 0.051] | 0.0335 | +0.0512 | -0.0177 |
| Mar BTC | 76 | [0.380, 0.116, 0.294, 0.395, 0.184, 0.020] | +0.2634 | +0.0195 | +0.2439 |
| Mar ETH | 87 | [-0.082, -0.012, 0.031, 0.064, 0.030, 0.110] | -0.0210 | +0.1098 | -0.1308 |
| Mar SOL | 91 | [-0.208, -0.025, -0.058, 0.032, -0.169, 0.014] | -0.0971 | +0.0138 | -0.1109 |

February decay survives both dependence-aware checks: circular-sign `p=0.008` and calendar-day bootstrap 90% CI
[0.0450, 0.2427]。但它仍不通过 all-symbol early positivity，也没有达到 pooled early >=0.05。March
circular-sign `p=0.562`，bootstrap 90% CI [-0.2021, 0.1667]，并且 pooled decay 为负。

## Gate audit

| Clause | Decision |
|---|---|
| January contemporaneous sign sanity, 3/3 | PASS |
| Minimum events, 6/6 symbol-months | PASS |
| Early response > 0, 6/6 | **FAIL** |
| Decay > 0, 6/6 | **FAIL** |
| Pooled early >= 0.05 in both months | **FAIL** |
| Decay/early >= 0.20 in both months | **FAIL** |
| Circular-sign p <= 0.05 in both months | **FAIL** |
| Calendar-day bootstrap lower > 0 in both months | **FAIL** |

## Reviewer-2 决策

1. 保留的工程结论是 Binance taker sign/quote-volume parser 可用；不保留 universal relaxation claim。
2. 不把 February 单独提交，也不删 BTC、只报 March BTC 或把负 ETH/SOL 解释成另一个事后 regime。
3. 不用更细 `aggTrades` “救”同一假设。Frozen decision 明确要求 H0 PASS 才允许 bulk event-time 数据；
   H0 已 FAIL。
4. 该结果不值得单独写高影响论文。它再次说明从已有数据中连续试 stylized patterns 会迅速变成
   hypothesis fishing；下一步应先做 theory/prior-art 选择，再获得真正独立数据，而不是继续换 lag/window。
5. 两张 V100 继续空闲，EcoMD training 保持停止。
