# ICLR 2027 投稿就绪审查（2026-09-01）

## 结论

不应把 PDEBench 结果硬塞进旧稿的“constraints deserve no credit”结论。已完成的父实验正式结果表明：

- 预注册主单元支持“参数化贡献更大”，但效应比为 2.015，只刚过 2 倍阈值；
- 硬约束在主单元仍带来可重复的小幅改善，并非零贡献；
- 12 个分辨率×时域单元中仅 4 个通过完整归因规则，硬约束效应还会变号。

因此主稿已改为中性的归因问题：比较方法时，必须把输出参数化和约束执行拆开；结论是条件性的，而不是“约束有用/无用”的普遍宣言。
新的四单元因子实验尚未完成，任何正式指标都未提前读取；摘要中的数字在结果揭示前仍是父实验占位，不能视为最终投稿结论。

## 已完成的稿件修订

- 改用官方 ICLR 2027 模板，并保持匿名提交设置。
- 改题为 *Who Gets Credit for Conservation? Disentangling Output Parameterization from Exact Enforcement in Neural PDE Surrogates*。
- 重写摘要、贡献、方法、结果、讨论和限制；删除旧稿的 30/30、42/42、强 soft penalty 等尚未被正式确认支持的绝对表述。
- 加入预注册主结果表、12 单元效果图、完整附录表、五个 arm 的主单元报告性汇总、投影解耦证明、数据与结果哈希。
- 明确投影恒等式是固定预测/一步门控；多步自回归投影会改变后续输入，不能把恒等式外推到整段 rollout。
- 补充 ProbConserv、hard-constrained downscaling、NCL、INO、clawNO、transform-space projection 和 adaptive correction 等直接相关工作。
- 加入 ICLR 2027 强制要求的 AI use statement，以及推荐的 reproducibility statement。
- 增加三单元不可识别定理、channel-separable training null、一步梯度耦合界和
  tangent-kernel channel-transfer 恒等式；后者把跨通道经验 NTK 块明确为约束改变守恒预测的一阶通路。
- 正面加入最接近的公开并行工作 PMFM；承认其已报告 Pure Net、Projection Only、
  Projection+GGM 等消融，不再把 projection-versus-residual-guidance 当作本文新意。

## P0：投稿前必须解决

### 1. 完成并一次性分析 Advection 四单元正式实验

V100a 正在运行 fresh seeds 3000--3029 的 `absolute/residual × free/hard` 完整因子设计，
目标恰为 150 条记录。只监控记录数、进程、GPU、哈希和错误；达到完整覆盖并退出前禁止读取
partial metrics。完成后先校验远端/本地 SHA-256，再只运行一次冻结 analyzer。主文首先报告
interaction/path-dependence 的四分类，再报告简单效应与 Shapley intervention credits；不得用父实验
的有利路径代替完整因子结果。

### 2. 完成前瞻冻结的梯度/NTK 机制检验

Advection 正式 worker 完整退出后，运行 seeds 3000--3029 的 60 条机制记录。它重建每个 seed 的
epoch-zero 第一 minibatch，记录守恒/违背梯度几何以及精确匹配的一步 Adam 干预。主检验是局部
coordinate interaction 与最终 rollout interaction 的逐 seed Spearman 相关及 50,000 次配对 bootstrap。
只有区间完全为正才支持该局部机制；过零或反向必须作为反证，不能改写成稳健性。

### 3. 完成第二个公开 PDEBench Burgers 因子复现

已前瞻固定 periodic 1D Burgers `nu=0.01`、seeds 4000--4029 和同一 2×2 设计。当前只在传输官方
固定版本文件；必须通过 bytes、MD5、SHA-256、HDF5 schema、全量 finiteness、质量漂移和保守降采样
恒等式后，才允许建立模型快照。随后 V100a/V100b 各运行预先分配的 15 个 seeds，分别得到 75 条，
合并为 150 条后一次性分析。不得因 Advection 结果改变黏性、网格、seed 或停止规则。

### 4. 新颖性定位为可识别的干预归因与机制，而非约束模块

已有工作已经提出投影、硬约束、clawNO、adaptive correction；PMFM 还公开报告了投影与 residual
guidance 的模块消融。可辩护增量是：缺失绝对-hard 单元时的不可识别性、完整 coordinate-by-training
因子干预、跨通道 NTK 传递恒等式、配对机制检验以及不挑路径的 Shapley credit。不要写 “first hard
constraint”“first residual compensation” 或 “no prior work separates the two”。

合成确认已经闭合：八个系统共 1,830 条有效记录，两项预先冻结的 Burgers 数值失败保留并排除。
该结果否定普遍 residual 优势，因此只作为边界证据进入附录，不能与公开 PDE 合并推断。

## P1：显著提高中稿概率

- 在正文中报告连续效应和置信区间，二元分类只作为预注册决策；父实验的 2.015 比值仅是占位证据。
- 将 synthetic formal confirmation 只作为附录边界证据；pilot 仍只用于选型，绝不进入正式推断。
- 为匿名 supplementary 建立一键复现入口，逐 block 校验记录、checkpoint、配置/数据/分析 SHA-256，并重建图表。
- 明确 CC BY 4.0 数据归属、block-average restriction、时间/轨迹 split、seed 为推断单位。
- 已在附录补充主单元的 total RMSE 和 mass drift；仍需补充跨 horizon 的 rollout stability 描述，且不得事后扩张主检验。
- 复核全文所有参考文献的作者、venue、年份和版本，尤其是仍为预印本的 adaptive correction。
- 现代 exact-correction baseline 只能在核心科学门已经通过后作为方法背景补充；如果交互、机制和
  Burgers 都没有形成可解释发现，继续堆 baseline 不能挽救论文，必须提出并前瞻检验新的科学假设或延期。

## 会务硬约束

- 摘要截止：2026-09-18 23:59 AOE。
- 全文与补充材料截止：2026-09-25 23:59 AOE。
- 初投稿正文最多 9 页，参考文献和附录不计入；双盲。
- 论文内必须有 AI use statement；reproducibility statement 强烈推荐。
- 摘要截止后不能新增或删除作者；应提前核对所有作者的 OpenReview profile 与 reciprocal-reviewer 登记要求，避免非学术性 desk reject。

官方来源：

- <https://iclr.cc/Conferences/2027/AuthorGuidelines>
- <https://iclr.cc/Conferences/2027/AIPolicyForAuthors>
- <https://www.iclr.cc/Conferences/2027/CallForPapers>

## 建议的提交门

只有在以下条件同时满足时再提交：

1. 正式实验覆盖、失败处置和一次性 analyzer 全部闭合；
2. 主要表格中的每个数字都能追溯到冻结 JSON；
3. 正文不再依赖 pilot-only 的成功计数；
4. 至少有跨架构或第二公开任务的正式证据；
5. 匿名 PDF、代码包、数据许可证、AI 声明和 9 页限制全部通过自动检查。

如果这些门在截止前未满足，延期到下一 venue 比提交一个公开留档但证据不完整的 ICLR 稿更有利。
