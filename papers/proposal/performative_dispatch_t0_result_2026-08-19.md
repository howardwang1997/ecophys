# 公开预测—市场响应 T0 新颖性与可识别性结果（2026-08-19）

## 结论

T0 **FAIL**，按冻结协议停止在 AEMO/NZEM 市场数据下载、模型实现和计算实验之前。候选问题是真问题，
但当前项目没有得到可支撑 NMI/NCS 的不可约贡献：

- **E0 identification theorem：FAIL。** 完整公开时序日志在隐藏共同信息下不识别 `do(F)`；而随机预测、
  过参数化/离散预测、跨环境 causal domain shift 和连续时间反馈识别等主要救援路径已有直接方法。
- **E1 real instrument：FAIL。** 找到的发布中断或制度变化要么同时影响投标、出清或结算，要么是单次、
  捆绑实施且无法满足冻结的五个独立事件要求。
- **E2 constraint-mediated law：FAIL。** active set、critical region、分段仿射/不连续 LMP、极端价格大偏差
  和含网络损耗的全局敏感度均已有直接理论；本项目没有导出一个额外的可证伪恒等式。
- **E3 benchmark：最多是基础设施候选。** AEMO/NZEM 的公开资料说明数据形态有潜力，但 E3 单独不能
  解锁高影响路线，也不能补上因果识别。

因此不启动 V100/RTX2060，不排 CPU 队列，不下载市场数值行，也不把“预测之后出现 rebid”包装成因果
发现。若未来没有真正随机/分阶段的信息披露、可辩护的发布中断，或新识别定理，这条路线保持关闭。

## 正式性

- frozen config：`configs/empirical_physics/performative_dispatch_t0_v1.yaml`，SHA-256
  `f96c39e7f6a3185f4d6827d68288746b8c08e07aaa8bda449fa02f1ac31dd719`；
- human freeze：`papers/proposal/performative_dispatch_t0_freeze_2026-08-19.md`，SHA-256
  `c6ee4b71f611171f09d34791fe1d7d1a0727e009f2c6da77e4b04e67a4f9b6f8`；
- freeze commit：`dfba54d5b1120d053022b5b66763a06855a69f57`，已先于本审计推送；
- structured result：`results/empirical_physics/performative_dispatch_t0_result.json`，canonical payload SHA
  `0fc3396a20e47dfb9cd73a2caf0cfa4d9e51b40ad21db48cf374a5fab2dea374`，file SHA
  `9e1843c7343d5642ec7522f746a82d8ab3b7a90bf4c78e69487fd41425623723`；
- literature/official-metadata cutoff：2026-08-19 NZST；
- 没有读取价格、投标量、dispatch quantity、constraint outcome 或 event-window statistic；
- 无 numerical implementation，CPU-only 文献/制度审计，无 GPU。

冻结文档把 Clements et al. 锚点误链为 `10.1016/j.eneco.2016.12.011`。正确 DOI 是
[`10.1016/j.eneco.2016.07.011`](https://doi.org/10.1016/j.eneco.2016.07.011)。为保留预注册 SHA，冻结文件
不回写；本结果及后续引用使用正确 DOI。

## 证据拓扑

```mermaid
flowchart TD
    Q[公开 forecast 是否改变市场结果?] --> I[需要识别 do(F)]
    Q --> M[需要区别于已有市场机制]
    Q --> D[需要真实外生变化]

    I --> CE[隐藏共同信息反例]
    I --> PP[已有 performative causal identification]
    CE --> E0[E0 FAIL]
    PP --> E0

    M --> PD[新西兰 iterative pre-dispatch]
    M --> RB[澳洲 strategic rebidding]
    M --> LMP[active-set / LMP critical regions]
    PD --> E2[E2 FAIL]
    RB --> E2
    LMP --> E2

    D --> O1[发布中断同时影响 bids/systems]
    D --> O2[单次或捆绑政策变化]
    O1 --> E1[E1 FAIL]
    O2 --> E1

    E0 --> STOP[T0 overall FAIL]
    E1 --> STOP
    E2 --> STOP
    STOP --> LOCK[不下载市场行，不实现，不用 GPU]
```

## 最近方法 claim matrix

| 最近工作 | 已有结果 | 对当前候选的约束 |
|---|---|---|
| [Perdomo et al., ICML 2020](https://proceedings.mlr.press/v119/perdomo20a.html) | 把预测引起的分布变化形式化为 performative prediction，并定义稳定性/风险 | “预测会改变被预测对象”不是贡献 |
| [Mendler-Dünner, Ding & Wang, NeurIPS 2022](https://arxiv.org/abs/2208.07331) | 直接研究预测的因果效应何时能从观测数据识别；给出随机预测、过参数化和离散输出三类充分场景 | 记录 forecast 并把它作为特征不是新识别法；连续、非随机公开价格预测也不自动满足条件 |
| [Cheng, Hardt & Mendler-Dünner, ICML 2024](https://proceedings.mlr.press/v235/cheng24d.html) | 在动态反馈系统中无需随机处理识别 performative effect；使用连续观测、外生状态扰动和响应控制动作 | “用滚动序列解决静态混淆”已有直接 theorem/estimator；本项目没有更弱假设结果 |
| [Boeken, Zoeter & Mooij, CLeaR 2024](https://proceedings.mlr.press/v236/boeken24a.html) | 以 causal domain shift 识别/修正决策支持系统部署前后效应 | baseline-policy 风险和跨环境修正不是空白 |
| [Boeken, Zoeter & Mooij, NeurIPS 2025](https://arxiv.org/abs/2510.21335) | 证明 conditional performative forecast 下经典 proper score 的一般不可能性，并给 separating forecast 与 divergence 解法 | “forecast error 不等于决策价值”及替代评分已被正面覆盖 |
| [Góis et al., AISTATS 2025](https://proceedings.mlr.press/v258/gois25a.html) | 将相互依赖的多主体响应、信任、accuracy 与 welfare 放进 performative prediction/mechanism design | 多主体共同响应与 welfare 权衡也不是仅靠市场应用即可主张的新框架 |
| [Bergheimer, Cantillon & Reguant, IJIO 2023](https://doi.org/10.1016/j.ijindorg.2023.102987) | 在 NZ pre-dispatch 中发现 indicative price/quantity 越来越有信息，bid revision 与信息更新一致 | 滚动预出清、无承诺价格发现和 rebid response 已是直接领域工作 |
| [Clements, Hurn & Li, Energy Economics 2016](https://doi.org/10.1016/j.eneco.2016.07.011) | 用 AEMO 五分钟公开数据研究战略 bidding/rebidding、物理约束和极端价格 | AEMO rebid/price/constraint 联动不是未研究现象 |
| [Brown et al., Energy Economics 2025](https://doi.org/10.1016/j.eneco.2025.108505) | 评估 Alberta 市场中哪些实时信息预测企业 bidding decision | “公开市场信息可预测投标”只是现有经验问题的延伸 |
| [Bernasconi et al., 2023](https://www.ifo.de/DocDL/cesifo1_wp10384.pdf) | 利用哥伦比亚信息披露改革的预告，研究 bidding 立即变化和关系型合谋 | 信息制度变化影响 bid 的事件研究与结构解释已有强邻居 |
| [Ji, Thomas & Tong, IEEE TPS 2016](https://doi.org/10.1109/TPWRS.2016.2592380) | 多参数规划划分 critical regions，联合预测实时 LMP 与 congestion，包含时变约束和 contingencies | active-set regime 与不确定输入的概率映射已有直接方法 |
| [Nesti et al., 2020](https://arxiv.org/abs/2002.11680) | 把 LMP 写成随机输入的确定性分段仿射、可不连续函数，并对 price spike 做大偏差分析 | “约束切换放大预测误差/价格极值”不能作为新定律 |
| [Huang et al., IEEE TPS 2026](https://doi.org/10.1109/TPWRS.2026.3670782) | 对含非线性网络损耗的 LMP 给出全局解析 critical regions 与敏感度 | 把 loss 或非线性加入 active-set 分析也已有直接 2026 邻居 |

这张表不表示所有论文等价，而表示冻结的三个出口各自都缺少不可约差异。把这些工作拼成一个
“performative forecast + learned rebid + differentiable clearing”系统是合理工程，但不是新 theorem、law 或
识别设计。

## E0：识别定理 — FAIL

冻结的两个 SCM 产生完全相同的 `(F,B,C,Y)` 观测联合分布：

```text
Model A: U~Bernoulli(1/2), F=U, B=F, C=B, Y=B
Model B: U~Bernoulli(1/2), F=U, B=U, C=B, Y=B
```

但在 `do(F=1)` 下，A 的 `B,C,Y` 随之改变，B 的则不改变。即使样本无限、时间戳完全正确，也不能从
公开路径区分“参与者响应 forecast”与“forecast 和参与者同时响应同一私有/未记录信息”。

本轮没有得到能越过该反例的新结果：

1. 把滚动 forecast 当作连续处理并加入 history，不会消除新信息 `U_t`；
2. 用同一 delivery interval 的多个 vintage 做差，仍把 vintage 间到达的物理/私有信息同时送进 forecast
   和 bid；
3. 用 active constraint 作为 mediator 不能满足 front-door 条件，因为 `F -> B` 本身受 `U` 混淆，且
   constraint set 又由 bids 与物理状态共同决定；
4. Cheng et al. 已给出动态无随机处理识别所需的结构，直接套用只会成为领域应用；当前公开日志也没有
   证明其独立外生扰动与响应控制条件；
5. 一般 sensitivity bound 可以诚实表达未识别，但没有电力市场特有的 sharp bound 或新 decision theorem。

因此 E0 不是“以后样本更多即可通过”，而是当前 estimand 和公开观测契约下的结构性 FAIL。

## E1：真实 instrument / intervention — FAIL

只查看官方事件和规则元数据，未读取事件窗口结果：

| 候选变化 | 元数据事实 | relevance / exclusion 审计 | 决定 |
|---|---|---|---|
| NZ WITS，2024-07-12 | 系统运营商月报称连接问题同时影响接收新 bids/offers 和若干 schedules 发布 | 处理同时改变 action channel；排除限制直接失败 | ineligible |
| NZ WITS，2026-04-02 | 主通信链路丢失，market schedules 约 2.5 小时未发布，随后切换数据中心 | 可能接近 publication-only，但只有一个已核实事件，内部 bid/备用渠道状态仍未排除 | unresolved, insufficient |
| AEMO，2025-06-30 | 生产升级同时覆盖 Dispatch、P5MIN、Predispatch、PD7、Bidding 等组件，并包含短时 Bidding outage | 同时改变 solver/application/bid availability；不是 forecast-only instrument | ineligible |
| NZ Winter 2023 options | Option B 发布四个 demand/wind sensitivity schedules；A、D、E 在相近时期同时改变 headroom、wind review 与 discretionary demand | 单次、季节性、政策捆绑，且面向 tight-supply periods；不能把结果只归因于 forecast 内容 | ineligible |
| NZ real-time pricing，2022-11-01 | 同时改变 dispatch pricing/settlement 和发布的数据序列 | 直接改变 payoff 与市场机制 | ineligible |
| NEM five-minute settlement | 同时改变结算激励、rebid 策略和数据语义 | 直接影响 bids/outcomes，不满足 exclusion | ineligible |
| NZ EMI 缺失 forecast archive files | 官方明确部分日包可能少于 48 个文件，但不追溯原因 | 归档缺失不等于参与者实时未暴露，且原因非随机 | ineligible |

官方来源包括 [NZ WITS 架构与备份要求](https://www.ea.govt.nz/industry/mosp/wits-manager/)、
[2024 年 7 月系统运营月报](https://www.ea.govt.nz/documents/5550/July_-_System_operator_monthly_report.pdf)、
[2026 年 4 月系统运营月报](https://www.ea.govt.nz/documents/10064/Monthly_System_Operator_performance_report_for_April_2026.pdf)、
[Winter 2023 Options B/D 决定](https://www.ea.govt.nz/projects/our-projects/decision-to-implement-options-b-and-d/)
和 [AEMO market notices](https://aemo.com.au/market-notices)。

冻结要求是至少五个合格独立事件，或一个有充分两侧支持的有效 discontinuity。当前是 **0 个合格、1 个
未解决的单次事件**。不能先看 outcome 再决定把哪个 outage 叫作 instrument。

## E2：constraint-mediated law — FAIL

候选的自然数学对象是闭环灵敏度。若 response map 为 `B=R(F,Y)`，clearing map 为 `Y=C(B,X)`，局部
导数会出现类似

```text
dY/dF = (I - C_B R_Y)^(-1) C_B R_F
```

的 feedback multiplier；在 active set 改变处需要分区或广义导数。这是标准隐函数/闭环灵敏度结构，
不是本项目发现的新恒等式。Ji et al. 已用 critical regions 处理 LMP/congestion，Nesti et al. 已覆盖分段
仿射、不连续和极端事件，Huang et al. 又扩展到 lossy LMP 的全局解析区域。本轮没有发现或证明：

- 一个跨 active-set boundary 仍成立的新 conservation/response identity；
- 一个不能由 KKT、multiparametric programming 或 standard congestion decomposition 推出的 scaling law；
- 一个冻结阈值下可在第二市场外推的非平凡符号或比率预测。

因此“约束使反馈非线性”正确但 trivial；“binding constraints 放大价格”正确但已知。E2 FAIL。

## E3：数据/benchmark 边界

AEMO 官方 pre-dispatch 页面显示 P5MIN 每五分钟更新一小时展望，30 分钟 pre-dispatch 覆盖价格、需求、
发电、interconnector 与 constraints；dispatch/MMS 又提供每五分钟结果。NZ 官方则发布四类 forecast
price、最终 bids/offers 与 SPD case files。数据丰富度支持未来的 specialist benchmark，但有两个边界：

1. NZ 免费公开层主要保证 final bids/offers；完整 submission/revision 历史由系统运营商保留，可请求且
   可能收费，不能在 D0 前假定为完整免费 action path；
2. 数据中有 forecast、action 和 outcome 不等于有 `do(F)`，也不等于知道参与者实际查看/使用了哪个
   forecast。

所以 E3 不改写 E0--E2。按冻结协议，连 metadata/header-only D0 也不解锁。

## Reviewer-2 决定与后续解锁条件

1. 关闭 `performative_dispatch_t0_v1`；不启动 D0/D1、AEMO/NZEM acquisition、synthetic rescue 或模型开发。
2. 不把该候选降级为“forecast revision 与 rebid 相关”的论文；这既不能回答因果问题，也不足以达到
   当前目标期刊。
3. 不再从同一公开日志中搜索 post-hoc proxy instrument。重开必须带来冻结前可验证的新信息：
   - 随机、错峰或明确 publication-only 的制度实验；或
   - 至少五个排除限制可审计的独立发布事件；或
   - 一个已写出且区别于 Mendler-Dünner/Cheng/Boeken 的新识别定理；或
   - 一个区别于 Ji/Nesti/Huang 的新 constraint-mediated law。
4. 2×V100 与 RTX2060 此刻保持空闲是正确资源决策；该 gate 的失败不是算力瓶颈。
5. 下一轮选题应先寻找“现实中已有外生干预或可验证自然实验”的系统，而不是再选一个只能靠公开
   observational log 猜机制的市场。
