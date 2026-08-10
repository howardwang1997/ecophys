# 真实市场物理零成本阶段结案与下一入口（2026-08-11）

**状态：** 零成本 empirical-discovery 阶段结案；当前没有通过预注册门槛的真实市场物理定律。
EcoMD v1 正面 model-paper、NCS 不变测度方法、静态 evaluator、日频 regime-memory 和分钟级
taker-flow relaxation 均停止。下一项允许启动的工作只有 **T0：熵产生/TUR 的可识别性与观测合同审计**；
它是 CPU-only 的理论/合成 gate，不是新的真实数据搜索。

## 1. 结论先行

现有结果支持的是一套可靠的失败检测与数据基础设施，不支持 Nature Physics/NCS 级真实市场发现：

1. EcoMD 的重尾瞬态是可重复的**模拟器内部动力学**，但市场真实崩盘没有复现实验预测；它不是已发现的
   市场物理。
2. 唯一较稳定的真实数据 hint 是 squared-return memory；它在新 instruments 上只刚好达到最低覆盖门槛，
   进一步的 lagged-regime 检验又因 4.38% 效应和 `p=0.147` 失败。不能称为新定律。
3. 分钟级 taker-flow sign 与 archive 语义正确，但 relaxation shape 不跨资产/月转移。更细逐笔数据不能用来
   事后挽救同一假设。
4. 旧 Plan v3 的 A1（有效温度临界标度）、B2（Jarzynski）和 B3（TUR）都不能继续作为默认主张。
   A1/B2 目前既有明显 prior art 又缺物理上唯一的观测定义；B3 仍可能成为候选，但必须先证明从部分可观测
   市场数据能够定义可反演路径、反对称 current 和有意义的 entropy-production bound。
5. 因而当前正确动作不是继续换市场、lag 或 proxy，而是先做可识别性/no-go 审计。若 T0 失败，真实市场
   stochastic-thermodynamics 主线也停止；若通过，再冻结全新数据上的 pilot。

## 2. 证据台账

| 证据 | 冻结结果 | 能保留什么 | 禁止写成什么 |
|---|---|---|---|
| EcoMD v1 M1 | stationarity transfer PASS；所有固定窗口 fidelity `2/11` | state-complete rollout、resume、stationarity gate 的工程能力 | validated market simulator、真实市场统计复现 |
| Exp123 重尾瞬态 | state kick 在 5/5 模拟市场重启重尾；真实五次 crypto crash pooled `z=+1.03`、方向相反/为零 | 模型内部非平衡瞬态与 model--reality gap | 市场崩盘的普适重尾瞬态 |
| Evaluator v2 初始市场 | 11 metrics 中只有 raw-return autocorrelation 合格 | conformal/surrogate evaluator 基础设施 | 多事实 realism score |
| Evaluator v2 新市场 | 四项 core 仅 acf-squared 为 `6/10`；其余 `1/10,1/10,2/4` | acf-squared 是待解释 hint | 静态 universal stylized-fact bands |
| Lagged-regime memory | MSE 改善 4.3769%，`12/17` periods、`10/11` symbols；permutation `p=0.147` | 跨市场方向一致但弱的探索信号 | 可转移的 regime law |
| Binance taker flow | January sign sanity 3/3 PASS；February decay `p=.008`，March `p=.562` 且 pooled decay 为负 | 1m parser、checksum、taker sign 语义 | universal impact relaxation / CKS OFI |
| 免费 LOBSTER / exp138--140 | 2,641,557 messages 的 schema、queue reconstruction、连续时间 likelihood 可执行；正式 gates 分别 FAIL `8/9,8/9,7/9` | L2/event infrastructure 与失败诊断 | 独立多日物理确认、EcoMD latent--L2 bridge |
| NCS G0 | 33 篇一手文献审计后，候选可约化为已有方法组件 | 已知 baselines、exact-resume、观测接口 | 新的不变测度梯度方法 |

这些失败不相互“投票”生成一个正面 claim。相反，它们共同说明：真实市场 estimand 尚未稳定，模型训练与
大数据扩容现在没有科学目标函数。

## 3. 已花费数据与不可再次充当 confirmation 的集合

- SPX/NDX/GLD/EURUSD 2015--2024 和十个新增 instruments 的共同历史已用于 evaluator 设计或确认；
- 11-market 半年度 panel 已用于 lagged-regime estimand；
- Binance BTC/ETH/SOL 2024 Q1 1m bars 已用于 taker-flow threshold/confirmation/temporal test；
- 当前免费 LOBSTER samples 只有单日/单小时，已用于 exp130、exp138--140；
- Luna、FTX、COVID、China-ban、Celsius crash windows 已用于重尾瞬态检验；
- sealed 2020 仍未解析，继续保持 sealed，不能为当前失败主张开封。

上述数据可用于复现、debug 和新理论的**开发诊断**，不能被重新命名为独立确认集。任何新 confirmatory
claim 必须在 estimand、代码、阈值和 stop rule 冻结后使用新的时期、市场或供应商数据。

## 4. 哪些能力真正存活

### 4.1 可发布的基础设施

- hash-bound manifest、官方 checksum、daily/monthly exact crosscheck 和不再分发 raw data 的 provenance；
- 严格按时间 split、sealed-period enforcement、clean HEAD=upstream execution 和原子 self-hashed artifact；
- dependence-aware calendar permutation、calendar-day bootstrap、surrogate kill 与 unfavorable reporting；
- LOBSTER event/sign/schema、visible-queue reconstruction 和 continuous-time marked likelihood；
- Binance taker-buy quote semantics；该量必须继续叫 `taker_flow_imbalance`，不是 CKS OFI；
- EcoMD state-complete trajectory、跨主机 exact resume、source-preview 构建和 stationarity gate。

这些足以支持一个透明的、明确标注 **empirically unvalidated** 的 source research preview，也足以让下一项
真实物理检验从可靠的工程底座开始；它们本身不构成高影响物理论文。

### 4.2 仍可作为开发信号、但不能进摘要的现象

- squared-return memory 的跨市场弱一致性；
- February taker-flow reversal 和 March BTC-only relaxation；
- LOBSTER aligned queue features 的正向 likelihood diagnostic；
- EcoMD state-kick 的强重尾/flow 瞬态。

每一项都已经暴露于结果查看，且至少一个绑定 gate 失败。只能用于形成机制问题，不能作为下一篇论文的
confirmatory evidence。

## 5. 旧 Plan v3 三条定律的重新判定

### A1：`T_eff` crash critical scaling — 暂停，优先级 2/3

“market temperature”并不新：Kleinert--Chen 早在 2006 年已把温度与波动联系并讨论 crash warning；
2025 年已有基于 fluctuation theorem 的九指数危机预测定义，2026 年又有跨股票、指数和 crypto 的
coarse-grained effective-temperature preprint。只把 volatility、return asymmetry 或 learned latent energy
重新命名为 `T_eff` 没有新颖性，也容易成为同义反复。

重新开放 A1 必须同时满足：

1. 温度来自独立的 fluctuation--response 或 path-probability identity，而不是由将被预测的 volatility 定义；
2. 三种预先指定定义在 calibration data 上给出可检验的等价/不等价结论；
3. crash event list、lead time、false-alarm metric 和无危机 control periods 在看 test 前冻结；
4. 对 GARCH/rough-volatility/Hawkes 等强 surrogate 有增量信息；
5. 相对 2006、2025、2026 最近邻能写出不可约的新物理 claim。

### B2：Jarzynski/FOMC/earnings — 当前形式停止，优先级 3/3

Jarzynski/Crooks 关系需要明确的 forward/reverse protocol、初始 ensemble、work functional 和相应的
微观可逆/路径概率条件。市场上不同 FOMC 或 earnings event 不是同一受控 protocol 的重复实验，事件前
状态也不是已知 canonical ensemble。把 learned `U_theta` 的差与事件期价格路径拼成 `W` 会让模型同时
定义两边，无法排除 self-consistency tautology。

Maskawa 2025 已在金融 volatility cascade 中检验 integral fluctuation theorem；2025 年也已有将 price
impact round trip 写成 stochastic thermodynamics 的理论预印本。除非获得真正可重复、可反演的外生执行
protocol（或把 claim 明确限制为 simulator theorem），否则 B2 不进入真实市场主线。模拟器内 recover
Jarzynski 只能验证实现，不能证明市场服从该关系。

### B3：entropy production / TUR — 条件保留，优先级 1/3

这是三者中唯一值得先做理论 gate 的方向，但不是因为“金融文献为零”。一般 TUR、finite-time TUR、
coarse-grained entropy bounds 和 optimal-current estimation 都已有成熟理论；2025--2026 的金融 fluctuation-
theorem 工作也压缩了直接套用空间。剩余问题必须更窄：

> 对部分可观测、带隐藏订单与参与者异质性的真实 limit-order book，哪些 pathwise irreversibility 或
> entropy-production **lower bounds** 可由消息流识别；这些 bounds 是否在独立市场上约束一个预先指定的
> liquidity current，并能否证伪对应的 EcoMD observation bridge？

若只能把绝对收益、交易量或同一 imbalance 同时放到 TUR 两边，路线失败。若 coarse-graining 使总熵产生
不可识别，则只能报告有证明的 lower bound，不能称为市场总 entropy production 或热力学效率极限。

## 6. 下一项允许执行的实验：T0 observability/no-go gate

T0 在任何新市场数据之前完成，允许使用解析模型和合成消息流，不读取已暴露的真实 test 数值。

### 6.1 工作包

1. **观测合同。** 明确 microstate、event alphabet、time-reversal involution、反对称 current、forward/
   reverse path density、stationarity 条件和 hidden-state boundary。
2. **解析 controls。** 至少包括 detailed-balance chain（真熵产生为 0）、driven three-state ring（真值非零）
   和两个“观测分布相同但 hidden entropy 不同”的反例。
3. **估计器验证。** 比较 plug-in path-ratio、known-rate truth、block/coarse-grained lower bound 和一个
   与 current 无共享构造的 null；报告 bias、coverage、finite-sample failure 和 time reversal sign。
4. **可识别性证明。** 给出在何种 Markov/order/observation 假设下等式成立；假设不满足时写成 lower
   bound 或 no-go，而不是用神经网络补全不可观测自由度。
5. **prior-art claim matrix。** 至少覆盖 Seifert/Crooks、finite-time TUR、optimal-current inference、
   coarse-graining bounds、Maskawa 2025 及 2025--2026 最近的金融 FT/FDT 工作。

### 6.2 通过条件

T0 全部满足才允许设计真实 L2 pilot：

- equilibrium false-positive rate `<=5%`；driven-ring entropy/current 的预注册相对误差 `<=10%`，
  90% interval coverage 在 `85%--95%`；
- 路径反演两次回到原路径，current 与 estimated entropy 在 time reversal 下符号正确；
- coarse-graining 后的量有数学保证的方向（例如 lower bound），并在反例上**拒绝**输出总熵产生；
- TUR 版本与 stationarity/finite-time assumptions 唯一冻结，不能在结果后选择更宽的 inequality；
- 对 finance 最近邻的差异能写成一条不可约命题；若只有“首次应用已有 estimator”，不得以 NCS/NP 为目标；
- 所有 synthetic gates 必须在未看真实 L2 test 前通过。

任一 identifiability、null 或 novelty 条件失败：停止 stochastic-thermodynamics 主线，不买 L2、不训练
EcoMD。数值实现通过只说明 measurement 合法，不说明市场有新物理。

## 7. 数据进入条件

| 阶段 | 数据 | 用途 | 当前授权 |
|---|---|---|---|
| T0 | 解析 chain + 新生成 synthetic event streams | 定义、真值、反例、coverage | **已授权，免费** |
| T1 | 新的、未被 exp130/138--140 使用的多日 L2；至少两个 symbols、两个不重叠月份 | 单交易所 pilot、stationarity/hidden-state sensitivity | **锁定，T0 PASS 后再获取** |
| T2 | 至少两个独立 venues，股票/期货/crypto 中至少两类市场；多个正常与压力时期 | 预注册 temporal/market confirmation | **锁定，T1 PASS 后再采购/扩展** |
| T3 | 三类市场、三个尺度、独立 crisis/control periods，并保留最终 sealed test | universality/early-warning 或模型机制论文 | **锁定，T2 PASS 后** |

L2 不是自动答案：数据必须支持逐事件顺序、买卖方向、可见队列状态、trading halts/session boundary、
corporate action/contract roll 和明确许可。若只有 bars 或 aggregate taker volume，只能检验对应 proxy，不能
声称 entropy production、CKS OFI 或 hidden liquidity。

## 8. 算力进入条件（未来不使用 H20）

| 阶段 | 资源上限/估计 | GPU 决策 |
|---|---|---|
| T0 | Mac/普通 CPU，`<=100 core-h`、`<=20 GB` 临时数据；目标 2--5 天内结案 | 禁止 GPU |
| T1 | CPU `100--500 core-h`；按数据源约 `0.1--1 TB` raw+derived storage | 默认无 GPU；只有已冻结 neural density baseline 才做单卡短 probe |
| T2 | 可扩展 CPU `2k--10k core-h`、约 `2--10 TB`；以独立 shards 并行 | 必要时 `100--500 V100-eq h`，可扩展到更多非 H20 GPU |
| T3/EcoMD mechanism | 先在现有 2xV100 做 `200--600 V100-eq h` pilot；通过后再按实测吞吐扩容 | 仅真实物理 gate PASS 后启动；未来 GPU 不限于两张，但不包含 H20 |

CPU 实验可以在 V100 主机上跑，但不得占 GPU 或以 GPU 可用性推动不成熟的假设。当前两台 V100 保持
空闲，没有排队任务；bulk `aggTrades`、付费 L2 和 EcoMD production 均未授权。

## 9. 投稿与影响力边界

- 现阶段可以完成：Sim2Science audit 投稿、S0 source preview、完整 failure/provenance archive。
- 现阶段不能完成：一篇有正面真实物理主张的 NCS/Nature Physics 稿件，或 validated EcoMD model paper。
- T0/T1 若只验证已有 entropy estimator 在市场数据上的可用性，目标应是方法/跨学科 specialist venue，
  不是 NCS/NP。
- 只有在 T2/T3 出现独立市场、独立时期、surrogate-resistant 的新 law，并由 EcoMD 做可证伪机制区分时，
  才重新评估 NCS/NP。
- “模拟器误差”只有在揭示一类模型共有、可预测且会改变科学结论的机制时才可能成为论文；当前单一
  checkpoint 的 fidelity failure 是研发负结果，不应取代真实物理主线。

## 10. 参考锚点（本次仅为窄范围占位检查）

- Crooks, *Phys. Rev. E* 60, 2721 (1999),
  <https://doi.org/10.1103/PhysRevE.60.2721>；
- Seifert, *Phys. Rev. Lett.* 95, 040602 (2005),
  <https://doi.org/10.1103/PhysRevLett.95.040602>；
- Toth et al., *Phys. Rev. X* 1, 021006 (2011),
  <https://doi.org/10.1103/PhysRevX.1.021006>；
- Bladon, Moro and Galla, *Phys. Rev. E* 85, 036103 (2012),
  <https://doi.org/10.1103/PhysRevE.85.036103>；
- Yura et al., “Financial Brownian particle ... fluctuation-dissipation relations” (2014),
  <https://arxiv.org/abs/1401.8065>；
- Kleinert and Chen, “Boltzmann Distribution and Temperature of Stock Markets” (2006),
  <https://arxiv.org/abs/physics/0609209>；
- Maskawa, *Entropy* 27, 435 (2025), <https://doi.org/10.3390/e27040435>；
- Ramezani et al., “Novel Market Temperature Definition Through Fluctuation Theorem” (2025),
  <https://arxiv.org/abs/2509.23692>；
- Jha, “A Stochastic Thermodynamics Approach to Price Impact and Round-Trip Arbitrage” (2025),
  <https://arxiv.org/abs/2512.03123>；
- Gao et al., “Coarse Graining Reveals a Fluctuation-theorem-like Asymmetry in Financial Markets” (2026),
  <https://arxiv.org/abs/2604.14962>；
- Seifert, “Universal bounds on entropy production from fluctuating coarse-grained trajectories” (2026),
  <https://doi.org/10.1038/s42254-026-00954-5>。

这不是完整系统综述。它足以否定“金融中尚无人做 fluctuation theorem/effective temperature/FDT”的
前提；T0 的 claim matrix 必须继续沿这些论文的引用网络做完整 forward audit。
