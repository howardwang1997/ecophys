# T0 entropy-production/TUR G0 新颖性与可识别性结果（2026-08-11）

## 结论

G0 **FAIL**，按冻结 gate 顺序在任何数值实现前停止。四个允许出口全部失败：partial L2 无法在当前假设下
识别 total entropy；partial/lower-bound estimator 已被 path-KLD、waiting-time、hidden-state 与 semi-Markov
文献覆盖；market TUR 已有直接 theoretical-finance 结果；EcoMD bridge 又被 v1 M1 的真实 fidelity failure
阻断。没有不可约 theorem、estimator identity 或已通过的独立市场 law。

绑定动作是：关闭当前 entropy/TUR 路线，不实现 conditional G2，不买 L2，不下载 bulk data，不启动
EcoMD 或 V100。旧 Plan v3 的 A1/B2 此前已暂停，B3 现在也关闭；三条 stochastic-thermodynamics 默认
主张均不再是活跃计划。

## 正式性

- frozen protocol：`configs/empirical_physics/entropy_tur_observability_t0_v1.yaml`，SHA
  `38f3e02eee8063a74a40224dc2bcbd960a23955f657f6e9a595a8561f00bcc43`；
- human freeze SHA：`2a8c96a617d3348ab997c517dd60b57a0f1571a56f83a54f975ec4558287afa6`；
- clean/pushed audit source：`49766d1cbb95a6a0f9a1af0f6dd65fd87d668fa8`；
- artifact：`results/empirical_physics/entropy_tur_observability_t0_g0.json`；
- artifact canonical SHA：`75624f950b9c129309467f3f8738a454374f21d5e7f2fe0f38f832d0e97cacd3`；
- artifact file SHA：`3b3f39ed8575b61b6817ce38c84aa469e0b564b8613a84248c6738318d846816`；
- literature cutoff：2026-08-11 UTC；29 个 peer-reviewed papers/primary preprints/author records；
- 没有读取真实市场数值，没有实现 estimator，没有 synthetic run，CPU-only/no GPU。

负的新颖性判定不需要证明“世界上再无一篇相关论文”：每个出口只要存在一个直接覆盖或一个数学
non-identifiability counterexample 就足以失败。本审计仍覆盖了冻结的八个文献簇并沿 anchor 做 backward/
forward search。

## Claim matrix

| 文献簇 | 已有直接结果 | 对本项目的约束 |
|---|---|---|
| Path probability / FT | Crooks 1999、Seifert 2005 已把 forward/reverse path ratio、work/entropy FT 形式化 | 不能把路径 log-ratio 或 IFT 作为新方法 |
| Stationary trajectory KLD | Roldan--Parrondo 2010/2012 用 time-reversal KLD 从单条 stationary trajectory 估计 dissipation，并明确是 lower bound | `KL(P_forward||P_reverse)` 的 market application 不是新 estimator |
| Hidden entropy | Kawaguchi--Nakayama 2013 研究消去变量后的 hidden entropy 与 coarse-graining；后续工作细化 parity 条件 | 可见消息不能自动等于 total physical entropy |
| Partial Markov observation | Skinner--Dunkel 2021 用 waiting times 给 hidden-system entropy bounds；van der Meer--Ertel--Seifert PRX 2022 给出何时恢复 full EP、何时只得 lower bound | “用 event waiting time 修正隐藏订单”已被直接覆盖 |
| Coarse-grained TUR | Ertel--van der Meer--Seifert 2022 已证明 thermodynamically consistent semi-Markov 及其 coarse-grained Markov 描述的 operational TUR | partial L2 + semi-Markov TUR 是直接应用 |
| General/finite-time TUR | Barato--Seifert 2015、Gingrich et al. 2016、Horowitz--Gingrich 2017、Liu--Gong--Ueda 2020 覆盖 steady/finite/nonsteady variants | 不能结果后选择最宽 TUR；也没有新 inequality |
| Optimal/learned EP | Vu--Vo--Hasegawa 2020、Dieball--Godec 2023、Lyu et al. 2024、Ji et al. 2026 覆盖 optimal currents、saturation 和 learned irreversible coordinates | neural current/representation 也不是未占空间 |
| TUR 与理论金融 | Liu--Ueda, *Phys. Rev. Research* 2023 明确把 universal TUR 与 theoretical-finance inequality/Hansen--Jagannathan 类 bound 统一 | “TUR 首次进入金融”是错误 claim |
| 金融 time irreversibility | Lacasa--Flanagan 2016 在 35 个金融序列上用 irreversibility 区分 crisis/stable years，并讨论 entropy lower bound | crisis irreversibility 不是空白 |
| LOB temperature/entropy | Li et al., *Entropy* 2023 用 Bitcoin spot LOB 定义 market temperature/entropy 并关联 liquidity/volatility | “首次用 L2 定义市场熵/温度”是错误 claim |
| 金融 FT / temperature | Maskawa 2025 在 volatility cascade 上检验 IFT；Ramezani 2025 与 Gao et al. 2026 分别做 crisis temperature 和 coarse-grained FT-like temperature | A1/B2/B3 的术语与应用邻域均已拥挤 |
| 2026 直接邻居 | Parande 2026 做 conditional market FDT；Trivedi 2026 preprint 从 equity probability currents/EPR 导出 TUR/strategy bound | 即使忽略 peer-review 强度，也足以要求实质数学差异而非应用 |

主要锚点：

- [Roldan--Parrondo 2010](https://doi.org/10.1103/PhysRevLett.105.150607) 与
  [2012](https://doi.org/10.1103/PhysRevE.85.031129)；
- [Kawaguchi--Nakayama 2013](https://doi.org/10.1103/PhysRevE.88.022147)；
- [Skinner--Dunkel 2021](https://doi.org/10.1103/PhysRevLett.127.198101)；
- [van der Meer--Ertel--Seifert 2022](https://doi.org/10.1103/PhysRevX.12.031025)；
- [Ertel--van der Meer--Seifert 2022](https://doi.org/10.1103/PhysRevE.105.044113)；
- [Liu--Ueda 2023](https://doi.org/10.1103/PhysRevResearch.5.013039)；
- [Li et al. 2023](https://doi.org/10.3390/e26010024)；
- [Lacasa--Flanagan 2016](https://doi.org/10.1016/j.physleta.2016.03.011)；
- [Maskawa 2025](https://doi.org/10.3390/e27040435)；
- [Ji et al. 2026](https://doi.org/10.1103/1ncx-6cxk)；
- [Gao et al. 2026](https://arxiv.org/abs/2604.14962)。

## 四个冻结出口

### E0：从 partial L2 识别 total entropy — FAIL

LOB feed 不观察参与者 intent、隐藏/撤回前 orders、其他 venues、internalization 和外生信息状态。没有
这些自由度的动力学假设，同一可见 path law 可由不同总耗散系统产生。冻结的 coupled-ring 构造给出完全
相同的 visible trajectories，但 total entropy rate 分别为

```text
log(2) = 0.693147
log(2) + 3 log(4) = 4.852030.
```

这不是有限样本问题；无限可见数据也无法区分。要恢复 total EP 必须加入不可由 feed 验证的结构假设，
而 PRX 2022 已系统给出恢复 full EP 与只得 lower bound 的条件。本项目没有新 identifiability theorem。

### E1：新的 partial/lower-bound estimator — FAIL

当前设想只是 path KLD、transition/waiting-time ratio、semi-Markov correction 或 optimal current 的选择/组合。
上述每一组件都有直接论文；没有更紧 bound、弱假设定理、finite-sample guarantee 或新的 time-reversal
identity。把它写成 LOB pipeline 只能是 application/engineering。

### E2：新的 market TUR — FAIL

项目没有新 inequality。Liu--Ueda 已明确把 universal TUR 与理论金融 bound 统一；2026 preprint 又直接从
market EPR/current 推 strategy-capacity bound。更关键的是，我们的真实市场候选（重尾瞬态、regime
memory、taker-flow relaxation）全部没有通过冻结门槛，因此也没有“新 market law”可以承载 TUR。

### E3：EcoMD observation bridge — FAIL

EcoMD v1 M1 在全部固定 stationary windows 只有 `2/11`，不能当 validated generator。Exp137 是 synthetic
observation gate，exp138 没有 EcoMD latent，免费 LOBSTER 又不是独立多日 panel。把已知 entropy estimator
接到一个未验证 simulator 上不产生跨模型或真实市场贡献。

## 为什么 apparent saturation 不能救 B3

冻结反例中，可见 ring current 的 mean/variance rate 分别为 1 和 3。若只用 apparent entropy，经典 TUR ratio

```text
R_app = 3 log(2) / 2 = 1.039721
```

看似贴近 1；加入一个与可见路径独立、但真实存在的 driven hidden ring 后，**可见数据完全不变**，total
ratio 却为

```text
R_total = 3 [log(2) + 3 log(4)] / 2 = 7.278045.
```

所以“由 L2 lower bound 近饱和”不能推出“市场运行在 thermodynamic efficiency limit”。这是一个逻辑
non-identifiability，而不是通过更多 symbols、days 或 GPU 能解决的误差。

## Reviewer-2 决策

1. T0 按 `stop_at_first_failure` 结束；G1 没有正式进入，conditional G2 不实现。
2. 不把 analytic ring control 单独包装成结果；它是已知 coarse-graining 逻辑的项目内反例。
3. 不买 L2 或用免费新数据寻找一个 application-only positive。
4. 旧 Plan v3 的 B3 正式退休；A1/B2/B3 均不能支撑 NCS/Nature Physics。
5. 下一条高影响主线必须从新的真实机制问题和不可约 prior-art gap 出发，先写 claim，再解锁数据；不能
   再从 EcoMD latent 或物理术语反推市场定律。
