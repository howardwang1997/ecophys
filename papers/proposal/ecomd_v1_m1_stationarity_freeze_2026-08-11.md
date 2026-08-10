# EcoMD v1 M1 stationary-fidelity 冻结（2026-08-11，结果前）

**状态：** 在任何新 checkpoint 或本 checkpoint 的 rollout 产生前冻结。绑定版本是首次包含本文与
`configs/ecomd_v1/m1_stationarity_screen.yaml` 的 Git commit。本文只规定筛选实验，不预设正结果。

## 1. 问题与边界

M1 只问：采用已经冻结并通过机械门的 EcoMD v1，在 2015--2018 SPX daily 上进行一次完整、状态连续
的训练后，生成过程能否在可验证的 stationary window 内稳定达到至少中等的 11-fact fidelity。

这不是市场“真实物理”的证明，也不建立 universality、crash precursor、order-book、因果机制或优于
强基线的结论。M1 PASS 仅允许启动多 seed、基线、消融和跨市场阶段；这些后续证据未完成前不得写
paper claim。M1 FAIL 则阻止正面 model paper，但不阻止透明的软件/负结果发布。

## 2. 数据冻结

- 免费来源：Yahoo Finance，经固定版本的 `yfinance` 请求 `^GSPC`；请求区间为 2015-01-01
  inclusive 至 2025-01-01 exclusive，`interval=1d`、`auto_adjust=false`、`actions=true`。
- 价格列固定为 `adjusted_close`；预处理固定为按 timestamp 排序后
  `numpy.diff(numpy.log(adjusted_close_float64))`。
- train/calibration：2015--2018；2019 是 report-only validation；2020 是 sealed crash test；
  2021--2024 是 temporal test。只有 2015--2018 进入 loss target。
- 正式 acquisition 必须从空目录开始，并记录 UTC 开始/结束时间、库版本、Git SHA、每个物理
  Parquet 的 SHA-256/bytes/schema/rows/timestamp coverage/null/duplicate，以及每个 split 的衍生
  float64 returns hash。manifest 不写价格或收益值，vendor bytes 不提交、不随 public artifact 分发。
- 训练入口必须校验 manifest 的文件 SHA 与 split-return hash；execution record 绑定该 manifest
  文件自身 SHA。若重新下载导致 byte/return hash 改变，视为新数据版本，不可冒充相同 run。

**结果前数据绑定补充（2026-08-11）：** 正式 acquisition 已完成但尚未产生 checkpoint。冻结 manifest
为 `data/manifests/ecomd_v1_m1_spx_4a2332d62.json`，文件 SHA-256 为
`0836ddd279a16db5010907120e65da87db58a2f2634c25f0e732334a98ffff7c`。新下载的十个年度文件与
历史缓存逐字节一致；该事实不改变任何训练、rollout 或决策规则。

## 3. 唯一训练

- 模型配置只能是 `m0_reference.yaml`，raw SHA-256 为
  `8e161bee28a4712e9a152539894ad6a9193d2311498fa066d24e16427e9ffa33`；参数量必须是 36,541。
- seed 0、N=256、FP32、600 iterations、chunk 64、warmup 16、固定 loss/learning-rate schedule；不
  early-stop，不因 2019 或任何生成结果调参。
- 第一台 V100 在 iteration 300 保存完整 checkpoint 后中断；从同一 checkpoint 精确 resume 到 600。
  最终 checkpoint 必须记录 iter=600、完整 runtime/RNG/optimizer state、环境、GPU UUID、config/data
  manifest hash 和 artifact SHA。M0 已完成 uninterrupted-vs-resume 的 bit-exact 机械验证；M1 的
  300+300 是实际参考训练，不再另跑一条可供选择的竞争 checkpoint。

## 4. Calibration/held-out 隔离

最终 checkpoint 固定后生成 32 条无 shock、无 inference override 的轨迹，每条请求 8,001 steps，
并断言恰有 8,000 usable returns。新种子为：

- calibration：811000--811015；
- held-out：811100--811115。

两台 V100 各承担每个 split 的交错八条。先只生成 calibration。energy gate 的 scale、tolerance 和
W-star 写成带输入 hash 的文件并 commit/push 后，才允许启动 held-out。不存在“先跑但不看”的
held-out 例外。

## 5. Stationarity 与固定长度评分

复用 exp127 已验证的 multivariate energy gate，唯一改变是预先指定的新 bootstrap seed 811900：

1. delay vector 为 `(r_t, |r_t|, |r_{t+1}|)`；
2. calibration late blocks `[6000,6500,7000,7500]`，各长 500，用 pooled median/MAD 标准化；
3. gate starts 为 0--4000、步长 500；tolerance 是 late-pair trajectory bootstrap median 的单侧
   95% quantile，2000 replicates；
4. W-star 是不晚于 3000 的最早连续三个 passing block；
5. 冻结的 W-star 原样应用于 held-out，并同时报告 ADF/KPSS 四检验 comparator。

每个 score window 长度都为 4000；完整报告
`W={0,50,100,200,500,1000,1500,2000,3000,4000}`，并额外纳入 W-star（若不在 grid）。每条轨迹
独立计算 11 facts；每个 fact 先取 16 条 held-out 的 median，再对固定 canonical bands 计算 pass
count 与 mean normalized distance。W=0、W-star 和 W=4000 是预先指定的 early/post/late 三点，不能
只展示最好窗口。

## 6. 决策规则

机械 FAIL：checkpoint 不是 exact iter 600、任何输出非有限、轨迹/seed/hash 不匹配。

stationarity FAIL：calibration 无 W-star，或 frozen W-star 在 held-out 不能通过同一三块 persistence
rule。

科学分层同时看 post W-star 与 late W=4000：

- 任一点 `<=2/11`：停止正面 model-paper 路线；
- 任一点 `3--4/11`：仅允许诊断/透明负结果，不启动大规模 multiseed claim production；
- 只有两点均 `>=5/11`，且 late mean normalized distance 不超过 post 的 1.10 倍，才允许下一阶段
  的多 seed、GARCH/AR1-SV/神经生成基线、消融和跨市场验证。

最后一种只是继续许可，不是论文成功。完整工作仍须证明多 seed 稳健、优于强基线、机制消融和
跨时间/跨市场外推；本筛选不满足这些负担。

## 7. 当前资源与停止纪律

- CPU/Mac：数据 audit、manifest、contract tests、gate fitting 与评分；
- V100-A 32 GB：一次 300+300 reference training；
- V100-A/B：先各八条 calibration，gate commit 后才各八条 held-out；
- 不使用 H20，不购买数据，不扩大模型/seed sweep。

任何代码、数据或协议 hash 不一致先停机定位。不得用 validation/crash/held-out 结果补阈值、换 seed、
换 W、缩短 L、增加外生 heavy-tail noise，或把失败 checkpoint 静默替换成另一次训练。
