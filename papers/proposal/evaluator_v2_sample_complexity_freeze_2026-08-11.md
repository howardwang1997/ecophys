# Evaluator v2.1 合成 sample-complexity 冻结（2026-08-11）

## 目的

Feasibility-v1 证明旧 11-fact suite 不能直接构造真实市场 acceptance bands。下一步先问更基础的问题：
**在一个明确含有/不含有目标结构的已知 DGP 上，当前 estimator 至少需要多少样本才能稳定识别？**

本实验只校准测量工具，不产生市场物理、universality、EcoMD 或模型优越性 claim。v1 中已经看过的四市场
2015--2024 结果不得用于修阈值，也不能成为 estimator 改版后的确认集。

## 设计

每个 metric 在 N={120,180,240,500,1000,2000,4000} 上运行 64 条独立路径，每条路径配八个由冻结
seed 生成的 primary surrogate。signal DGP 明确含目标结构；null DGP 不含该结构但尽量保留混淆因素：

- Hill/aggregation：Student-t signal 对 Gaussian null；
- gain/loss：负 jump mixture 对 symmetric Student-t；
- intermittency/acf-squared：GARCH 对独立厚尾 null；
- conditional kurtosis：t-GARCH 对 Gaussian GARCH；
- DFA：多时间尺度 log-volatility 对独立厚尾 null；
- leverage：GJR-GARCH 对 symmetric GARCH；
- volume coupling：与 |return| 耦合的 volume 对 independent volume；
- autocorrelation：Gaussian iid 等价性 sanity check；Zumbach 仍只诊断。

所有参数、burn-in、长度、重复数和 seed 已写入机器可读 YAML。DGP 不是市场生成模型候选，只是 unit test
fixture；“在刻意构造的 DGP 上有 power”也不代表真实市场存在该机制。

## 解析 sample floor

正式 admissibility 不在 estimator 数学上不可能工作的长度判失败：aggregation 至少 N=180，DFA 至少
N=240，Zumbach 至少 N=180；Hill 要求 k≥25，因此从 N=500 开始；99% Fano 至少有 20 个期望 extreme，
因此从 N=2000 开始。其余 floor 见 YAML。这些 floor 在任何合成 metric 输出前固定。

## 双门槛

每个 signal cell 必须 64/64 real 与全部 surrogate estimates 有限；real-minus-within-path-control-median 的
方向比例至少 0.80，median effect 至少 0.5 pooled-IQR。相应 null cell 必须与 surrogate 等价，绝对
median effect 不超过 0.5 pooled-IQR。IQR 非正 fail closed。

metric 的 admissible minimum 不是“第一次偶然通过”的长度，而是最小的 grid N，使 signal 与 null 在
该 N 及所有更长 grid N 都通过。后面任何一次失败都会否定更早的 minimum。Zumbach 不给 admissibility。

## 停止与后续

- 实现/source 必须先 commit/push，正式结果才可产生；
- 失败后不能改本协议里的 DGP 参数、grid 或阈值再重跑同一 formal experiment；
- 通过最多允许为**全新市场**写下一份确认协议，不能回头把当前四市场包装成 confirmatory；
- 本阶段 CPU-only、零付费、禁止 GPU。V100 继续空闲。
