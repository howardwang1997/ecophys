# Binance taker-flow response feasibility — 2026-08-11

Zero-cost high-frequency gate after the daily regime-memory FAIL. Three Binance spot pairs (BTC/ETH/SOL), Q1
2024 1m bars; January fit, February confirmation, March temporal test. The observable is explicitly
`taker_flow_imbalance=(2*taker_buy_quote-quote_volume)/quote_volume`, never CKS OFI. Frozen protocol/result:
`papers/proposal/taker_flow_response_feasibility_{freeze,result}_2026-08-11.md`.

Acquisition from clean `a8450e759` passed 36/36 official checksums, exact grids and all 27 selected daily/monthly
all-column comparisons. Manifest SHA `ea05914c…`; 19 MB raw root remains unredistributed. A pre-output definitional
correction changed first eligible day index 60 to 61 because index-0 return is unavailable; no other setting
changed.

Formal result from clean/pushed `cf72e3435`: hard FAIL. January sign sanity passes strongly for all three assets
(mean contemporaneous response 0.996--1.299 pre-vol units) and all six evaluation symbol-months exceed event-count
floor. February pooled decay is real within that month (early 0.0426, late -0.1024, decay +0.1450, circular p=.008,
bootstrap 90% CI [.0450,.2427]) but BTC early is negative and the 0.05 early floor fails. March does not transfer:
pooled early .0335, late .0512, decay -.0177, p=.562, CI [-.2021,.1667]; only BTC relaxes while ETH/SOL early and
decay are negative.

Artifact canonical SHA `c30f716fe985052643ddcc0c7d02cd105c23634367a7f0e17dca0dc3a6bc89e1`, file SHA
`78d90818bd949faeb6ce2daa131279accff4d12f74758fb8f926bcd081ff3eed`; 1.78 s CPU/no GPU. Binding decision:
stop taker-flow relaxation and do not download bulk aggTrades. Do not rescue by selecting February/BTC, changing
lags/windows or rebranding negative altcoin response. Parser/sign semantics survive only as infrastructure.
EcoMD and V100s remain idle; theory/prior-art selection must precede any new empirical hypothesis.
