# EcoMD 独立模型论文与软件发布计划（2026-08-09）

**状态：** 延后执行；不属于 2026 workshop 投稿。本计划承接 Sim2Science audit 之后的 EcoMD
首次正式方法发布。

## 1. 为什么不能现在直接发布

EcoMD 尚无论文或公开软件，而 exp 127 已显示：初始化窗口中的有利重尾分数在冻结的 post-gate
等长窗口中不能维持，late-time stylized-fact fidelity 很弱。此时把 Sim2Science 改写成 EcoMD
model paper，会把一个已识别的模型缺陷包装成方法贡献。正确顺序是先公开审计结论，再修复模型，
最后用独立论文发布方法、代码和 checkpoints。

## 2. 独立模型论文的最小 claim

> EcoMD 是一个可微、随机相互作用的 Langevin 多智能体市场模拟器；在严格时间外测试、固定长度
> post-stationarity 评价和强基线下，它能以可复现的方式生成若干预先指定的市场统计，并支持对
> 模型内部机制的梯度校准与受控干预。

“首个”、普适重尾、真实市场物理、crash precursor、MACE/equivariant 等表述都不是默认 claim。
只有相应理论、prior-art 审计和真实数据实验通过后才能加入。

## 3. 发布前硬门

### M0：方法冻结

- 建立单一、可版本化的 `EcoMD v1` 规格，删除历史配置中未启用却容易造成误解的模块名；
- 逐项对齐论文公式、配置 schema、实现和 checkpoint loader；
- 明确训练时 jump proxy 与 inference compound-Poisson jump 的差异，优先消除而不是隐藏；
- 修复训练 chunk 每 24 steps 把 global state $u$ 归零、而 inference 让它连续 8,000 steps 的
  horizon/state mismatch，并用回归测试锁定；
- 给参数量、计算复杂度、随机边采样无偏性和可微路径提供测试或推导。

### M1：stationary-fidelity 修复

- 所有模型选择只看 calibration/validation 时间段，测试期与 crash 事件完全封存；
- 每个 checkpoint 先通过独立于目标 stylized fact 的 stationarity protocol，再做固定长度评分；
- 至少覆盖股票、外汇/商品和加密资产，并使用多个训练 seed；
- 同时报告 early、post-gate 和 late-reference 结果，禁止只保留最好窗口；
- 若 post-gate fidelity 仍只有当前约 1--2/11，则停止 model-paper claim，继续作为负结果研发记录。

### M2：基线与消融

- 与 GARCH/SV、至少一个现代生成时序基线、一个 differentiable ABM 基线比较；
- 逐项消融 random-pair potential、global state、agent types、Hawkes feedback、impact map 和 jump；
- 区分“容量带来的拟合”与“物理结构带来的可识别增益”；
- 所有排名使用相同样本长度、时间切分、调参预算和不确定性估计。

### M3：泛化和稳定性

- 时间外、市场外和采样频率外至少各有一个冻结测试；
- 报告训练 seed、rollout seed、checkpoint 和市场四层不确定性；
- 做长 rollout 数值稳定性、初始化敏感性和尾指数稳定性测试；
- 不把 latent excess demand 或 `rho` 称为 empirical OFI，除非有匹配真实微观数据的验证。

### M4：可微与规模贡献

- 给出梯度正确性有限差分测试、随机估计方差与训练稳定性；
- 报告 $N$、随机伙伴数 $k$、显存、吞吐和 wall-clock scaling；
- 用至少一个真正需要可微模拟器的任务证明效用，例如可识别校准或受约束 optimal execution，
  而不只报告 stylized facts。

### M5：首次正式 release

- 论文、完整 simulator/training/evaluation 源码、配置、环境锁、数据 provenance 和 checkpoint
  同版本打 tag；
- 提供从数据到训练、trajectory generation、scoring 和 figure 的端到端命令；
- 每个数据集写 license/redistribution 边界；公开不了的原始数据必须提供可替代 smoke dataset；
- release candidate 在干净环境和两台 V100 上各做一次重建，记录 hash 和可复现性差异。

## 4. 与 Sim2Science 的边界

Sim2Science 只发布 audit code、冻结 synthetic trajectories、结果和 EcoMD audit-object 的完整
科学规格；不发布核心模型源码与 checkpoint binaries。未来 model paper 必须引用并正面讨论该
audit，证明修复后结果不再依赖初始化瞬态。两篇不能共享同一个正面 fidelity claim：前者是发现
并量化失败，后者只有在失败被预注册实验真正修复后才成立。

## 5. 下一次启动条件

完成 Sim2Science submission 后再启动 M0/M1。第一阶段只做 stationary-fidelity repair 和
surrogate sanity cascade；在 M1 通过前不写 model-paper 摘要、不公开 checkpoints，也不为追求
venue 叙事新增真实市场物理 claim。
