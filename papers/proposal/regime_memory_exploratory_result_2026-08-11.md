# 真实市场 lagged-regime volatility-memory 探索结果（2026-08-11）

## 结论

预注册 primary nomination gate **FAIL**。上一半年度的 realized-volatility state 对下一半年度
squared-return memory 有方向一致但很弱的 out-of-time 预测改善：pooled MSE 降低 4.38%，低于冻结的
5% practical floor；更关键的是 calendar-preserving permutation `p=0.147`，不能拒绝“相同时间依赖和
横截面相关结构下的偶然对齐”。因此停止日频免费数据上的 lagged-regime memory claim，不启动 EcoMD。

不能把门槛从 5% 改成 4%，也不能因为普通 cluster bootstrap 区间为正就忽略 permutation failure。
结果可诚实描述为一个跨市场较一致的弱 hint，但不是可提名的物理规律。

## 正式性与数据边界

- artifact：`results/empirical_physics/regime_memory_exploratory_v1.json`；
- clean HEAD/upstream：`6f92a399d94c45871df770eb865553e3658ea9ad`；
- canonical payload SHA：`c7c70686654b4d0a168cb1e419b6d6396e4821a3e2a0bc1a4a58cb754572659b`；
- file SHA：`c4c3aab72892818cb4f8057a41b393198ed7679ef9daf87b6c8316ab01e1c2f3`；
- protocol SHA：`8732b4e75cf786b25a6944afb4d9795cf534843beeeba00ad6f16ab4825e7362`；
- artifact 内部计时 2.07 s；CPU-only，`gpu_used=false`；
- 两个 manifest、全部 raw shards 和 source evaluator result 均重新验 hash；
- 2020 没有被解析或加载，2021H1 因 predecessor 落在 2020 而预先排除。

Timestamp-only coverage 规则得到 11-market balanced panel。每个 market 有 38 个非 2020 半年度 blocks；
fit/evaluation target periods 合计 36 个，所以共有 396 regime rows。Primary 有 209 个 fit cells 和 187 个
evaluation cells，但有效推断单位仍是 17 个共同 calendar half-years，而不是 187 个独立样本。

## Primary：acf-squared memory

| 冻结条款 | 结果 | 决策 |
|---|---:|---|
| fit common slope > 0 | +0.003196 / predictor IQR | PASS |
| pooled relative MSE reduction >= 5% | 4.3769% | **FAIL** |
| pooled MAE improvement > 0 | 0.000649，约 2.22% | PASS |
| 2015H1--2019H2 MSE improvement > 0 | 4.4823% | PASS |
| 2021H2--2024H2 MSE improvement > 0 | 4.1627% | PASS |
| calendar wins >= 10/17 | 12/17 | PASS |
| symbol wins >= 7/11 | 10/11 | PASS |
| calendar-preserving permutation p <= 0.05 | 0.147（146/999 null >= real） | **FAIL** |
| calendar-cluster bootstrap 90% lower > 0 | [1.6824%, 7.2206%] | PASS |

RUT 是唯一 MSE 轻微恶化的 symbol（-0.18%）；其余十个改善从 0.40% 到 11.63%。Calendar losses 也不是
单一 crisis 驱动：两个 evaluation eras 都约改善 4%。然而 null distribution 的 median 虽为 -1.09%，
仍有 146/999 个 calendar permutations 达到真实 4.38%，最大甚至 16.50%。Observed calendar alignment
没有足够独特性。

## 为什么 bootstrap PASS 不能救 permutation FAIL

Cluster bootstrap 在**固定已观察 predictor--target 时间对齐**后重采样 17 个 half-years，回答“这组对齐
下，平均改善对 calendar sampling 是否稳定”。Permutation 则在保留每个时期的跨市场共同结构时打乱
时间标签，回答“正确的 lagged alignment 是否优于其他可能 alignment”。时间序列有缓慢 regime、自相关
和共同宏观冲击时，前者可以给出正区间而后者不显著；本实验预先要求两者都通过，所以不能选择性报告
bootstrap。

## Secondary 与 specificity

- ETF volume coupling 的 fit slope 是 -0.00753，与预期正方向相反；pooled MSE 只改善 1.44%，
  evaluation-1 为 +3.22% 而 evaluation-2 为 -1.19%，permutation `p=0.103`，bootstrap 90% CI
  [-1.98%, 4.64%]。没有可转移的 lagged-volatility relation。
- Raw-return autocorrelation diagnostic 的 MSE 恶化 3.03%，两个 eras 都恶化，permutation `p=0.675`，
  bootstrap CI 全负。这说明 primary 弱改善不是所有 estimator 都共有的 pipeline artifact，但 diagnostic
  specificity 不能补救 primary effect-size/null failure。

## Reviewer-2 决策

1. 不把 4.38% 包装成“接近通过”。Practical floor 与 permutation 是冻结前设定，任一失败都足以停止。
2. 不在同一数据上尝试 contemporaneous regime、不同 lag、不同 block size、删 RUT 或非线性模型；这些
   都会把 exploratory hint 变成多重搜索。
3. 这个负结果不值得单独作为高影响论文。它支持一个方法论判断：日频半年块太粗，弱的 state marker
   无法从慢变共同宏观结构中被可靠识别。
4. 两张 V100 继续空闲。下一条真实物理可行性路线必须使用更接近机制的免费高频 observables 和明确
   event-time protocol；在其真实数据 gate 通过前，不恢复 simulator training。
