# T0 entropy-production/TUR observability gate 冻结（2026-08-11）

## 研究问题

零成本真实数据阶段没有产生通过门槛的市场定律。旧 Plan v3 中，A1 `T_eff` 与 B2 Jarzynski 已因直接
prior art 和观测定义问题暂停；B3 entropy production/TUR 是唯一条件保留方向。本 gate 不问“能否在市场
数据上算出一个正数”，而问：

> 部分可观测的市场消息流能否支持一个相对已有 stochastic-thermodynamics 与金融文献不可约、物理上
> 可识别且非同义反复的 entropy/TUR claim？

T0 是 theory/prior-art/synthetic observability gate，不是市场实证。它禁止读取新的真实市场值、购买数据、
训练 EcoMD 或使用 GPU。

## 为什么先做 G0，而不是先写 estimator

Scoping search 已找到四类直接邻居：hidden entropy 的 fluctuation theorem、从 waiting time 估计 hidden
entropy bound、coarse-grained semi-Markov TUR，以及明确把 universal TUR 联系到 theoretical finance 的
工作；金融 time irreversibility、order-book temperature/entropy 和 volatility-cascade fluctuation theorem
也已经发表。故 numerical pipeline 通过不等于方法或物理新颖性。

冻结 gate 顺序为 G0 prior art/claim → G1 observability/no-go → G2 analytic/synthetic recovery → G3 fresh
L2 design，任一失败立即停止。尤其是 G0 失败时，禁止为了生成结果而实现 G2。

## G0：不可约 claim gate

完整 matrix 必须沿 required anchors 做 backward/forward audit，并覆盖：

1. path probability、entropy production 与 fluctuation theorem；
2. hidden/coarse-grained entropy 与 waiting-time bounds；
3. steady-state、finite-time、semi-Markov 和 optimal-current TUR；
4. 金融 time irreversibility、危机识别、market temperature、TUR 和 LOB thermodynamics。

只允许四个 candidate exits：

| Exit | 必须达到的差异 |
|---|---|
| 从 partial L2 识别 total entropy | 在明确市场观测假设下给出 theorem-level identifiability |
| partial entropy lower bound | 比已有 hidden/semi-Markov 方法更紧或假设严格更弱 |
| market TUR | 新 inequality，或独立数据支持的新 law；直接套公式不算 |
| EcoMD observation bridge | 跨模型/真实市场结论，不能只审计当前未验证 simulator |

至少一个 exit 同时有不可约数学陈述和可证伪 benchmark 才 PASS。“首次金融应用”“首次用 L2”或已有
estimator 的工程实现都算 FAIL。G0 FAIL 立即关闭 stochastic-thermodynamics 路线，不进入数值实验。

## G1：部分观测的解析反例

冻结一个 exact coupled counterexample。可见过程 `B` 是均匀三状态连续时间 ring：顺时针 rate 2，
逆时针 rate 1；观测 current 为顺时针次数减逆时针次数。两个完整系统共享**逐路径完全相同**的 `B`：

- completion A 的隐藏 ring `A` 为 1/1，满足 detailed balance；
- completion B 的隐藏 ring `A` 为 4/1，持续耗散；
- 隐藏 ring 与可见 ring 独立，因此两 completion 的可见 path law 完全相同。

对 rate 为 `k+`,`k-` 的均匀 ring，steady-state entropy-production rate 是

```text
sigma = (k+ - k-) * log(k+ / k-).
```

因此可见 apparent entropy rate 在两系统都是 `log 2`，但 total truth 分别是
`log 2` 与 `log 2 + 3 log 4`。任何只读取可见路径的 estimator 都不可能区分二者。

更强的警告来自经典 steady-state TUR ratio

```text
R = Var(J_T) * E[Sigma_T] / (2 * E[J_T]^2).
```

可见 current 的 mean rate 为 1、variance rate 为 3。用 apparent entropy 得
`R_app = 3 log(2)/2 = 1.0397`，看起来几乎“饱和”；completion B 的 total truth 却是
`R_total = 3[log(2)+3log(4)]/2 = 7.2780`，远离效率极限。故 lower-bound saturation 不能推出 total
entropy saturation。实现必须输出 `partial/lower_bound` 或拒绝 total claim；把它标成市场总熵或效率极限
即 G1 FAIL。

## 条件 G2：只有 G0 PASS 才运行

若 G0 找到不可约出口，才实现 exact Gillespie homogeneous ring controls。冻结 100 batches、每 batch
64 条独立 stationary trajectories，fit/evaluation horizon 各 250，root seed `814200`，float64。Fit 只估
path-flux log ratio，evaluation 使用未来不重叠 segment；禁止 pseudocount，任一方向零计数返回 unresolved。

G2 全部门槛：

- 97.5% null test 下 equilibrium false-positive `<=5%`；
- driven 4/1 ring 的 grand relative error `<=10%`，90% batch-CI coverage 在 `[85%,95%]`；
- path reversal 是 involution，current 与 path entropy 都严格反号；
- unresolved fraction 为 0；
- apparent/total TUR ratio 相对解析真值误差各 `<=10%`；
- coupled hidden pair 的 observed paths exact equal，同时 total truths 严格不同；
- 输出语义明确是 lower bound/refusal。

G2 通过只验证 measurement；不构成真实市场定律。只有 G0--G2 全部通过，才允许冻结新的多日 L2 pilot。

## 数据、算力与停止边界

- G0/G1：论文、解析推导、普通 CPU；
- 条件 G2：最多 100 CPU core-hours、20 GB temporary storage；
- 禁止真实 test values、paid data、bulk `aggTrades`、GPU 和 H20；
- 两张 V100 继续空闲；
- G0 失败后不得降低目标 venue、删最近邻或把 application-only 改名为 theorem。

本 freeze 绑定源决策 commit `bf9e5c56b04d16ea3b787a44a910b1f4a4c08d8e` 与文件 SHA
`ce1baf012e26c3c48abcc58377db46ed1a4e14f6b2ced27c266dcc49c58661f2`。完整 machine-readable contract
是 `configs/empirical_physics/entropy_tur_observability_t0_v1.yaml`。
