# EcoPhys 项目状态与路线图（2026-09-05）

> 面向 PI 的全局简报：已完成什么、正在进行什么、下一步做什么。
> 权威来源不变：`research/discovery/protocol.yaml`、
> `.claude/memory/research_route_knowledge_graph.yaml`、`research/discovery/current_machine_decision.yaml`。

---

## 一、现在做了什么（按工作线）

### 1. Paper D — 约束归因论文（ICLR 2027）：科学工作完结，只差投稿动作

**结论**（条件性主张，非普适定律）：
- 输出参数化（residual vs absolute 坐标）因果地决定学到的模拟器的 OOD 误差（8/8 系统显著，
  6/8 偏 residual）；**精确硬约束本身不获信用**；机制 = 映射收缩 vs 近恒等。
- 已注册的 U-Net 架构迁移门**失败**（`complete_gate_not_passed`）：FNO 结论不迁移到 U-Net，
  论文如实报告为架构边界。

**状态**：
- 确认实验（30 种子）、全部扩展（Advection 因果盒、梯度耦合机制、浅水独立复现、规范干预）
  完结；amended analyzer 恰好运行一次（2026-09-01）。
- 稿件 + 可复现 artifact 完成并通过 138 项洁净抽取测试；本地提交 `3aae4926a` 及后续。
- **双盲冲突已修复**（2026-09-05）：GitHub 仓库 `howardwang1997/ecophys` 已转 **PRIVATE**
  （0 fork；verification_liquidity 读外部仓库 API，不受影响）。

### 2. 选题探索（discovery loop）：饱和关闭，元结论明确

- 16 个选题周期 + 84 个原始问题 + 99 次重入触发审计：**0 张机器卡、0 个合格触发器**；
  222 条路线 failed_closed。
- 共同死因：不存在"合法随机分配的市场干预 + 完整可重放状态 + 独立同估计复现"的真值资产。
  想法不是瓶颈，真值才是。
- 决策：不再做重贴标签的选题周期；转入真值资产建设（见第 3 线）。

### 3. 真值资产阶梯（A-3 计划）：**三级连续完成（2026-09-05 一天内）**

| 阶段 | 内容 | 状态 |
|---|---|---|
| A-3 契约 | 七部件论文级设计（估计量/分配/schema/权利/确认分区/复现/止损） | ✅ 冻结于 2026-08-26 |
| A-2 平台资格 | Part 4 tape 契约全字段覆盖；lab-asset-v3 schema 冻结 + 双臂 fixture 束 + 独立验证器；27 项测试；2 次工程迭代零失败 | ✅ 出口判据满足 |
| A-3 处理选择 | 结果盲审计 5 个候选家族 | ✅ 完成（见下） |

**已选主处理**：等价队列优先规则 — **严格 FIFO vs 均匀随机单位抽样**（防拆分单位核）。
理由：唯一以冻结工件通过全部三道否决门的候选——① 2026-08-27 搜索清单证明无人类同估计
先例（Lim 2026 为仿真/理论邻居；Khapko-Zoican 2021 是速度减速带非分配规则）；② 语法臂
不变已在 A-2 束中证明；③ C2 引理族 fork 已冻结（交换性不变零假设 vs 阈值族深度符号）。
**备选**：最小停留时间（零 schema 改动，待 fork 推导冻结）。
**否决**：深度可见性（Hendershott et al. 2022 JFM 人类隐藏订单实验 + Boulatov 2013 RFS
理论 = 直接先占）。清单新增 9 项带标识工作。

### 4. 记录与基础设施

- 全部记录已提交推送至 `paper-d-iclr-2027-completion`（最新 `e3d09b1e4`）；两个大传输归档
  留在 R2+双机未入 git（.gitignore 防护已加）。
- 双治理验证器通过：684 证据记录、99 触发审计（0 合格）、251 路线节点（active=1 =
  `verification_liquidity` 密封协议）、270 边、964 locator。
- `goal_state.yaml` / `current_machine_decision.yaml` 保持实时反映机器决策链。

---

## 二、机器决策链（当前无任何 standing 授权）

| 决策 | 状态 |
|---|---|
| Paper D 约束归因链（confirmation → extensions → U-Net result） | 终结：`complete_gate_not_passed` |
| `truth_asset_a2_platform_qualification_20260905` | 终结：出口判据满足（2 次迭代零失败） |
| `truth_asset_a3_treatment_selection_audit_20260905` | 终结：主处理已选（结果盲） |

---

## 三、之后要做什么（按优先级）

### P0 — 有截止日期

1. **ICLR 2027 投稿执行（PI 账户级，摘要截止 2026-09-18）**
   - OpenReview 账户/资料、互惠审稿人资格确认（reciprocal-reviewer eligibility）。
   - 摘要提交 → 全文 + 匿名 artifact 上传（仓库已 private，上传清单已备）。
   - 不改任何冻结科学结果。

### P1 — 真值资产阶梯继续（每级需新的 PI 授权）

2. **A-1 准备**（论文级部分可先行，外部接触必须待明确授权）：
   - 双独立治理站点选择（发现站 + 确认站，Part 6/7 契约）。
   - 伦理申报材料 + 预注册草案（主处理已冻结：FIFO vs random-unit）。
   - Part 8 成本上限：PI 冻结预算后才能进入 A-1 报价/联系。
3. **A-0（远期）**：人类被试市场、结果访问、模拟器拟合、确认开封 — 全部待 A-1 完成后
   另行授权。

### P2 — 待办/观察

4. **verification_liquidity 密封协议**：holdout **2026-10-17 UTC 前**禁止打开；届时重新
   派生状态。
5. **备份处理 fork 推导**（最小停留时间）：论文级，一个会话，完成其备选资格。
6. **运维**：V100 磁盘 98%/96% 满需清理；本地 `main` 与活跃分支分叉（79 个 2026-04 旧提交）
   需裁决（合并或归档）；选题侧仅保持触发器监控（新定理/新授权真值资产出现才重审）。

### 触发重开的条件（选题侧）

任何 closed 路线的重入仍需 re-entry ledger 中的合格触发条目；真值资产（A-1→A0）建成后，
"模拟器能否预测人类市场的分配干预响应"类选题才可能通过 activation gate 立项。

---

## 四、当前禁止事项（无新授权不得做）

人类被试/招募/外联/伦理申报（A-1 未开）；市场数据结果访问/购买；GPU 用于发现路线；
EcoMD 集成；候选收获/选题卡创建；重开 `failed_closed` 家族；2026-10-17 前打开
verification_liquidity holdout。
