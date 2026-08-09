# EcoMD Workshop 投稿执行计划（2026-08-07）

> **2026-08-09 最终执行决策（覆盖本文所有双稿、STODY 和合并分支）：** 本轮只完成并投稿
> **Paper E / Sim2Science**。Paper S / STODY **正式取消**，不建立 STODY 稿件、不再补 S0--S4
> 实验，也不把 shock atlas 塞入 Paper E。原因是 Paper S 未通过独立成文门，而两个稿件又共同
> 依赖从未公开、原稿中未充分定义的 EcoMD。Sim2Science 保持 E-B 的 simulator-specific audit
> 定位，在正文和技术附录中自包含地定义被冻结的 EcoMD audit object；匿名 artifact 只发布审计
> 代码、冻结轨迹与结果，不发布 EcoMD 核心训练源码或 checkpoint。完整 EcoMD 方法与软件待修复
> stationary-fidelity 缺陷后另写 model paper。下文双稿内容仅作为决策历史，不再是待办事项。

**状态：** 单稿执行中；Sim2Science 是唯一 workshop 投稿，STODY 已取消。

**范围：** 本文负责 venue 选择、双稿约束、格式、匿名化、OpenReview、内部审稿、现场报告和提交后义务。实验和 claim 生存门以 `workshop_claim_gates_and_merge_plan_2026-08-07.md` 为准，不在此重复设计。

**外部硬截止：** 2026-08-29 23:59 AoE，即 2026-08-30 23:59 Auckland time。

**内部提交：** 2026-08-27；不得把 AoE 硬截止当作正常工作时间。

## 1. 投稿目标

### Paper E：stationarity-aware evaluation

- **主投：** Sim2Science — ML with Imperfect Scientific Models；
- **形式：** 5-page Workshop Paper，不走 2-page Tiny Paper；
- **暂定题目：** *A Stationarity Gate for Evaluating Persistent-State Scientific Generators*；
- **唯一主张：** 未经稳态验证的 full-rollout scoring 会把初始化松弛混入 steady-state model quality；frozen stationarity gate 加 fixed-length scoring 可检测并避免该混淆；
- **替代路线：** FMTS；只有 verifier artifact 达到 E-A 时才考虑 AI for Science。替代路线是二选一，不并行提交同一稿件。

### Paper S：driven stochastic dynamics

- **条件主投：** STODY — AI for Stochastic Dynamics；
- **形式：** 默认 4-page Short Paper；只有 8 月 15 日前出现正式理论结果或足够完整的第三条证据链，才升级为 8-page Regular Paper；
- **暂定题目：** *Driven Heavy-Tail Transients in a Learned Langevin Market Simulator*；
- **唯一主张：** 在 EcoMD 内部，coherent drive 与 temporary reduced friction 触发 mechanism-dependent heavy-tail transients，幅度随 dose 饱和并有限恢复，generic heating 不产生同等响应；
- **存活条件：** 必须通过 `workshop_claim_gates_and_merge_plan_2026-08-07.md` 的 S0 加至少一个 S1--S4 门；否则不单独投稿。

## 2. 已核实的 venue 规则

| 项目 | STODY | Sim2Science |
|---|---|---|
| 官方页面 | [STODY CFP](https://eethanshi.github.io/stochastic-dynamics-2026/) | [Sim2Science CFP](https://www.sim2science.com/cfp.html) |
| OpenReview | [STODY venue](https://openreview.net/group?id=NeurIPS.cc%2F2026%2FWorkshop%2FSTODY) | [Sim2Sci venue](https://openreview.net/group?id=NeurIPS.cc%2F2026%2FWorkshop%2FSim2Sci) |
| 截止 | 2026-08-29 23:59 AoE | 2026-08-29 23:59 AoE |
| 页数 | Short ≤4；Regular ≤8；参考文献和 appendix 不计 | Workshop Paper 5；Tiny Paper 2；参考文献不计，appendix 不限 |
| 模板 | 官方 NeurIPS 2026 默认格式 | 官方 NeurIPS 2026，`dblblindworkshop`，`\workshoptitle{Sim2Science}` |
| 评审 | OpenReview，至少 3 reviews | Double blind；reciprocal reviewing |
| 特殊义务 | 当前 OpenReview 表单没有 short/regular track selector，需询问 organizer 如何标注 | 投稿时指定一名作者为 reciprocal reviewer，并完成 2 篇评审；未按时完成可能 desk reject |
| Checklist | 官网未明确；投稿前向 organizer 确认 | 标准 NeurIPS reproducibility checklist 必须完整填写，放在 references 后、appendix 前 |
| Notification | 2026-09-29 | 2026-09-29 |
| Camera ready | 2026-10-09 | TBD |
| Workshop | Sydney，2026-12-11 或 12，线下一日 | Paris，2026-12-12 或 13，线下一日 |
| Archival | NeurIPS workshop 统一 non-archival | Non-archival |

OpenReview 当前两个 submission forms 均要求：所有作者已有 OpenReview profile、title、keywords、abstract、PDF、author-email sharing 确认、accepted-paper public-release 确认和 CC BY 4.0 license。Sim2Science 另外要求 track 和 nominated reciprocal reviewer。PDF 上限为 50 MB。

Sim2Science 明确 discourages 把同一论文平行提交到多个 NeurIPS workshops。两篇若同时提交，必须是 claim、实验、主图和结论均不同的 related-but-distinct papers，并取得 organizer 的书面确认。

## 3. 双稿投稿的线下报告门

这是本计划新增的最高优先级约束。

STODY 在 Sydney，Sim2Science 在 Paris，日期重叠。NeurIPS 2026 workshops 是线下一日活动；官方只允许每个 workshop 最多一小时的 remote presentation capacity，且定位为 unforeseen emergencies，由 organizer 自行决定。计划中的跨洲冲突不能默认被当作 emergency。

作为 solo author，在以下任一条件满足前，不得假设可以同时提交两篇：

1. 有另一位对论文作出实质贡献、符合 authorship 标准且能现场报告的共同作者；或
2. 两边 organizer 在投稿前书面确认相关双稿合规，并明确接受一篇远程报告；或
3. 最终 venue routing 把两篇放到同一城市、确认 workshop 日不冲突，并允许作者完整履行两边报告义务。

不得为解决报告问题临时添加没有实质贡献的作者。也不得采用“先投两篇，若都录用再撤一篇”的默认策略，因为这会浪费评审资源且可能损害信誉。

若 2026-08-15 前没有可履行的双报告方案，执行单稿路线：

- Paper E 达到 E-A/E-B、Paper S 未过门：只投 Sim2Science；
- Paper E 为 E-C、Paper S 过门：只投 STODY；
- 两篇都过门但只能报告一篇：科学上默认优先 Paper E/Sim2Science；若 Paris 出行不可行，则在 STODY 与 Paper E 改投 Sydney 的 FMTS 之间按最终证据强度二选一；
- 两篇都未过门：本轮不强投。

## 4. 48 小时内必须完成的外部准备

以下操作会产生外部通信或账户状态，须由用户执行或另行明确授权：

### 4.1 Organizer 邮件

给 STODY 询问：

1. OpenReview 当前没有 Short/Regular selector，4-page short paper 应如何标记；
2. 是否要求 NeurIPS checklist；
3. related-but-distinct EcoMD submissions 分投两个 workshops 是否允许、如何披露；
4. accepted paper 是否必须由作者现场报告，是否存在预先批准的 remote 机制。

给 Sim2Science 询问：

1. related-but-distinct submission 的披露方式；
2. accepted paper 的现场报告要求；
3. reciprocal reviewer 的 assignment/review deadline；
4. solo author 若存在不可避免的跨 venue 冲突，是否允许 remote presentation。不能把询问理解成已获得许可。

邮件和回复保存到明确不进 git 的 private admin 目录；匿名稿件内不出现作者身份或邮件内容。

### 4.2 OpenReview profile

- 检查姓名、历史 affiliation、当前 institution、verified email 和 conflict domains；
- 确认投稿作者列表。Sim2Science 开始评审后不能新增作者；
- solo submission 时，用户本人即 nominated reciprocal reviewer；
- 核对用户是否满足 CFP 所说的 relevant high-profile-venue publication 要求；若不确定，投稿前
  询问 organizer，不能提名非作者或为此添加名义作者；
- 确认能够在 organizer 规定期限内完成 2 篇评审；若不能，不投 Sim2Science；
- reciprocal reviews 属于 confidential material，NeurIPS workshop reviewers 禁止使用 LLM。不得把分配论文、评审草稿或任何保密内容上传给 Codex 或其他模型。

### 4.3 现场可行性

- 记录 Sydney 与 Paris 的可出行/不可出行结论、护照签证、预算和时间约束；
- 8 月 15 日前不能确认 Paris 现场可行时，Sim2Science 必须有 organizer 明确 remote approval 或改走可履行的替代 venue；
- 不在论文被录用后才第一次评估 travel feasibility。

## 5. 仓库与模板迁移

旧 `workshops/ml4ps/` 与 `workshops/genai_finance/` 使用 `neurips_2024.sty` fallback，不能直接投稿。它们只作为文字与 bibliography 素材来源。

新建：

```text
papers/paper_a_methods/workshops/
├── sim2science/
│   ├── main.tex
│   ├── references.bib
│   ├── checklist.tex
│   ├── figures/
│   ├── BUILD.md
│   ├── SUBMISSION_CHECKLIST.md
│   └── submission_metadata.example.yaml
└── stody/                         # 仅在 Paper S 通过生存门后建立完整稿
    ├── main.tex
    ├── references.bib
    ├── figures/
    ├── BUILD.md
    ├── SUBMISSION_CHECKLIST.md
    └── submission_metadata.example.yaml
```

要求：

- 从官方 NeurIPS 2026 archive 新建模板，不在旧 2024 source 上逐项修补；
- private author IDs、邮箱、submission number、reviewer assignment 和 receipt 不提交到可能公开的 git；
- `submission_metadata.example.yaml` 只保留字段，不放私人账户信息；
- 每张图只由冻结结果 artifact 生成，记录 script、input hash 和 output hash；
- 两篇不共享主图；Paper E 不使用 shock atlas，Paper S 不把 stationarity gate 当主贡献。

## 6. 投稿时间线

| Auckland 日期 | 投稿交付物 | Gate |
|---|---|---|
| 08-07 | 冻结本计划；整理 CFP/OpenReview 规则 | 不再使用 2024 template |
| 08-08 | 用户发送两封 organizer 邮件；检查 OpenReview profile；完成 travel feasibility 初判 | 外部问题未答不视为许可 |
| 08-08--08-09 | 建立 Sim2Science 2026 template skeleton、checklist 和 build/QA 脚本 | 无 fatal error、undefined reference/citation 或未解释的 overfull box |
| 08-09--08-12 | 按 claim-gate 计划运行 E0--E3；并行写 Problem/Method/Limitations | 不等待最终数字才开始写作 |
| 08-12 | Paper E claim tier；冻结 title v0、abstract v0、TL;DR、keywords | E-C 不创建虚假方法学叙事 |
| 08-12--08-14 | 若 Paper S 仍存活，建立 STODY skeleton 并完成 S0/S1；准备 4-page short 结构 | 未过门不写第二篇完整稿 |
| **08-15 12:00** | **决定提交 0/1/2 篇；锁定 venue、track、作者、reviewer 和现场报告方案** | 无双报告方案则单稿 |
| 08-15--08-18 | 完成结果段、三张主图、related work、limitations；生成第一版完整 PDF | 每个定量句可追溯 |
| 08-19 | 内部 Review A：claim/evidence 和统计单位 | 失败则收窄 claim，不追加故事 |
| 08-20 | 内部 Review B：venue fit、novelty、related work、引用逐条核验 | 未核验引用不得提交 |
| 08-21 | 内部 Review C：匿名化、模板、页数、checklist、PDF metadata | 任一 desk-reject 风险清零 |
| 08-22 | 完成 supplement、artifact availability、limitations 和 AI-use policy audit | 主文必须自洽，不能依赖 appendix 才成立 |
| 08-23 | Reviewer-2 blind read；只允许删减、澄清和修错 | 不新增 headline experiment |
| **08-24** | **内容与实验冻结；生成 release-candidate PDF** | 此后只修事实/格式错误 |
| 08-25 | 用户在 OpenReview 创建/更新 submission，填 metadata，上传 RC1 | 下载平台 PDF 再检查 |
| 08-26 | 最终作者确认：claim、license、公开发布、related-submission disclosure、现场义务 | 用户逐项签字确认 |
| **08-27** | **上传 final PDF；保存 forum ID、submission number、UTC/NZST 时间和 PDF SHA256** | 完成内部提交 |
| 08-28--08-29 | 仅处理平台错误或致命事实错误 | 不做内容扩写 |
| 08-30 23:59 | Auckland hard deadline | 不计划使用此缓冲 |

## 7. 两篇稿件的页数预算

### Sim2Science：5 pages

| 内容 | 预算 |
|---|---:|
| Problem、failure mode、contributions | 0.6 page |
| Related work 与 scope boundary | 0.4 page |
| Stationarity gate 与 fixed-length protocol | 1.1 pages |
| EcoMD held-out result | 1.0 page |
| neural-SDE transfer 与 GARCH controls | 1.1 pages |
| Limitations、discussion、conclusion | 0.8 page |

正文必须明确：排名翻转不是通过条件；E-B 时只称 EcoMD case study；real-market physics 不属于本文 claim。

### STODY：4-page short

| 内容 | 预算 |
|---|---:|
| 问题、模型和严格 claim boundary | 0.7 page |
| 干预协议与统计单位 | 0.6 page |
| 5 资产 transient + finite recovery | 0.9 page |
| channel contrast + saturating amplitude | 0.9 page |
| S1/S2/S3/S4 中通过的独立证据 | 0.6 page |
| limitations 与 conclusion | 0.3 page |

若没有最后一项独立证据，不用更多 dose plots 或 trained-Lévy 填充篇幅；取消独立 STODY。

## 8. 内部审稿清单

### 8.1 Claim 与证据

- 摘要只出现冻结 evidence 支持的 claim tier；
- `state_kick` coherence 明确标为 imposed；
- model-internal physics 与 empirical market physics 分开；
- 不出现 MACE/equivariant、empirical OFI、`tau(dose)`、universal crash precursor；
- primary、secondary、exploratory 和 prior evidence 标签一致；
- checkpoint seed 与 rollout 数不混用；null、发散和缺失完整报告。

### 8.2 引用与 prior art

- 每个引用打开原文核对题名、作者、年份、venue、claim 支持范围；
- 使用已验证的 Tóth et al. PRX 2011、Chopra et al. AAMAS 2023、MACE、Cont 2001、Maskawa 2025 等相关引用；
- 不恢复不存在的 “Tóth-Lux-Sornette PRL 2018”；
- differentiable/Langevin market simulator 的先例必须包含 Bouchaud--Cont 与 Dyer/GradABM 路线，不能声称 first。

### 8.3 匿名化

- PDF 无姓名、affiliation、acknowledgment、grant、个人 URL、W&B entity、R2 URI、用户名或机器路径；
- self-citation 使用第三人称，不写 “our previous work”；
- code/data 链接必须匿名且不会通过 commit history、owner、domain 或 metadata 反向识别；
- `pdfinfo` 的 Author/Creator/Producer 不暴露身份；
- 文件名、figure metadata 和 supplement 压缩包不含作者姓名；
- 从 OpenReview 下载平台保存的 PDF，再运行一次相同扫描。

### 8.4 格式与可读性

- 使用 2026 官方 style，字号、边距和行距未修改；
- 主文页数合规，references/checklist/appendix 顺序正确；
- 图中文字在 100% 缩放可读，色彩在灰度和色盲模式下可区分；
- 所有表格、坐标轴、单位、样本量、置信区间和 estimator 定义完整；
- PDF 无缺失字体、越界框、坏链接或空白页，文件小于 50 MB；
- main text 在不读 appendix 的情况下仍能验证核心 claim。

### 8.5 AI 使用与作者责任

- 用户逐句确认稿件、公式、图、引用和 submission metadata，并对内容承担全部责任；
- AI 不列为作者；重要、非标准的 agent/LLM 使用按 NeurIPS 2026 policy 披露；
- 不在稿件中留下 prompt injection、系统指令、模型自述或未经核验的生成引用；
- reciprocal reviewing 期间完全禁止把 confidential submissions 或 review 内容交给 LLM。

## 9. OpenReview 提交操作

每篇先准备本地 `SUBMISSION_CHECKLIST.md`，全部通过后才在 OpenReview 操作。

提交字段：

1. track；STODY 若表单仍无 selector，按 organizer 书面指示处理；
2. title；
3. 完整且最终的 author list/OpenReview IDs；
4. 4--8 个精准 keywords；
5. 一句 TL;DR，不写超出正文的 claim；
6. abstract，与 PDF 完全一致；
7. final anonymized PDF；
8. Sim2Science reciprocal reviewer；
9. email-sharing、public-release 和 CC BY 4.0 confirmations；
10. confidential related-submission disclosure，按 organizer 指定渠道提交。

上传后：

- 重新下载 PDF，核对 SHA256、页数、字体、匿名化和图像；
- 保存 forum ID、paper number、提交时间和表单截图/receipt；
- 不把含作者身份的 receipt 提交到公开仓库；
- 8 月 27 日后若替换 PDF，必须重新生成 hash 并记录原因；
- 截止前最后一次打开 venue 页面，确认 submission 状态不是 draft/withdrawn。

实际提交、license 同意和公开发布确认属于外部状态变更，由用户完成；Codex 未经明确授权不点击最终提交或发送 organizer 邮件。

## 10. 投稿后义务

### Sim2Science reciprocal review

- assignment 到达即记录 deadline；
- 为两篇评审预留独立时间，按时提交是本稿不被 desk reject 的必要条件；
- 不使用任何 LLM/agent，不泄露论文内容；
- 完成后保存非保密的“已提交”时间记录，不保存或提交对方论文内容到本仓库。

### Decision 与 camera ready

- 两站 notification 均为 2026-09-29；
- STODY camera-ready 为 2026-10-09；Sim2Science 日期待公布，每周检查一次官网/OpenReview；
- 录用后才加入作者、affiliation、acknowledgment 和非匿名 artifact link；
- camera ready 仍逐项核查 claim，不能借去匿名化加入未经评审的新 headline result；
- 保存最终公开版本、license、program link、poster/slides 和 artifact DOI。

### 现场报告

- 录用后立即完成 NeurIPS registration、travel 和 presentation confirmation；
- poster 与 talk 只覆盖论文允许 claim，不把 workshop 交流升级成市场 universality；
- 若出现真正 unforeseen emergency，立即联系 organizer；不能事后自行改为 remote。

## 11. 决策矩阵

| Paper E | Paper S | 双报告可行 | 行动 |
|---|---|---|---|
| E-A/E-B | 未过门 | 不相关 | 只投 Sim2Science |
| E-C | 过门 | 不相关 | 只投 STODY |
| E-A/E-B | 过门 | 是，且 organizer 允许 related submissions | 两篇各投对应 venue，严格去重 |
| E-A/E-B | 过门 | 否 | 默认 Sim2Science；若 Paris 不可行，在 STODY 与 Paper E 的 Sydney 替代 venue 中二选一 |
| E-C | 未过门 | 不相关 | 不投稿，保留 negative record |
| 任意 | 任意 | organizer 明确不允许 | 只投证据和现场可行性综合最强的一篇 |
| 任意 | 任意 | organizer 到 08-15 未回复 | 不把沉默视为许可；按单稿路线执行 |

## 12. 完成定义

投稿阶段完成必须同时满足：

1. 0/1/2 篇决定由预先冻结的 claim gate 与现场可行性共同决定；
2. venue、track、作者、reciprocal reviewer、license 和 presentation plan 已锁定；
3. 使用官方 2026 template，页数、checklist 和匿名化符合各自 CFP；
4. 每个 claim、数字、图和引用均经人工核验并可追溯；
5. 两篇同时提交时不存在核心证据切片、重复图或不可披露的关系；
6. OpenReview final PDF 经下载复核，receipt 与 SHA256 已保存；
7. 2026-08-27 完成内部提交，并履行后续 reciprocal review、camera-ready 和现场报告义务。
