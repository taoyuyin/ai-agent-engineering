# Chapter 53 AI Native Software

Part VII Future —— 下一代软件

Version: 2026-08

Last Updated: 2026-08-03

## Core Question

什么样的软件才是 AI Native，而不仅是给传统应用增加一个聊天框？

## Chapter Conclusion

AI Native Software 把 `Goal、Context、Plan、Evidence、Confidence、Approval` 作为一等运行时状态。系统根据用户目标动态组合能力，但把权限、事务、预算和关键业务不变量留在确定性服务中。

AI Native 不意味着所有界面都变成对话，也不意味着让模型取代业务系统。它改变的是软件的控制入口：从用户指定每一步，演进为用户声明目标、约束和验收标准。

## Learning Objectives

完成本章后，你应该能够：

- 区分 Traditional、AI-enabled 与 AI Native Software；
- 设计 Goal-driven Architecture 和 Capability Contract；
- 划分 Probabilistic Intelligence 与 Deterministic Core；
- 理解生成式交互、动态计划和 Evidence-first UX；
- 规划传统企业应用向 AI Native 演进的路径。

## 53.1 三种软件形态

| 形态 | 用户表达 | 系统执行 | AI 的位置 |
| --- | --- | --- | --- |
| Traditional | 点击功能、填写字段 | 预定义流程 | 无或外围辅助 |
| AI-enabled | 提问、生成、推荐 | 原流程 + 单点模型能力 | Feature / Copilot |
| AI Native | 目标、约束、反馈 | 动态计划 + 受控能力组合 | Intelligence Layer |

一个 CRM 增加“帮我写邮件”仍然是 AI-enabled。如果用户可以声明“找出本周高流失风险客户，准备个性化挽回方案，不得自动发送”，系统能规划、取证、生成草案、等待审批并持续学习，才接近 AI Native。

判断标准不是用了多少模型，而是模型能力是否进入核心状态、架构和交互闭环。

## 53.2 从功能驱动到目标驱动

传统软件让用户选择函数：

```text
Menu → Form → Validation → Service → Database
```

AI Native Software 接收一个不完整目标，并逐步收敛：

```text
Goal + Constraints
        ↓
Goal Compiler → Capability Planner → Policy Gate
        ↓                ↓               ↓
 Context            Dynamic Plan      Approval
        └────────────── Runtime ──────────┘
                          ↓
                  Evidence + Result
                          ↓
                  Feedback / Learning
```

Goal 必须转换成机器可验证契约：

- `objective`：希望改变什么；
- `constraints`：不能违反什么；
- `success_criteria`：如何知道完成；
- `scope`：可以访问哪些数据和工具；
- `budget`：Token、成本、时间和人工注意力；
- `approval_policy`：哪些副作用由谁确认。

自然语言只负责表达意图，不能代替这些结构化边界。

## 53.3 AI Native 架构的三层

### Deterministic Core

保存真实业务状态并维护不变量：订单、库存、账务、身份、事务、权限和审计。它通过稳定 API 和事件暴露能力，绝不能依赖 Prompt 保证余额不为负或租户不越权。

### Intelligence Layer

负责意图理解、规划、检索、选择工具、解释结果和修复。这里允许概率性，但每个输出都应是可校验 Proposal，而不是直接写入核心状态。

### Interaction / Projection Layer

根据任务状态生成合适的交互：澄清问题、计划预览、证据表格、差异视图、审批卡片或传统表单。对话只是其中一种 Projection。

```text
Probabilistic: understand → propose → rank → explain
Deterministic: authorize → validate → transact → audit
```

这条边界是 AI Native Software 最重要的工程原则。

## 53.4 Capability 是新的组合单元

传统应用通过页面和 Service 固定串联功能。AI Native 系统让 Planner 在约束内组合 Capability：

```json
{
  "name": "compare_price_and_risk",
  "requires": ["supplier_list"],
  "produces": "comparison",
  "input_schema": "SupplierList",
  "output_schema": "SupplierComparison",
  "scopes": ["supplier:read"],
  "cost_hint": 0.25,
  "side_effect": false
}
```

一个可组合 Capability 需要：

- 明确输入输出 Schema；
- 可发现的语义描述；
- Scope 与数据分类；
- 成本、延迟和可靠性提示；
- 幂等性、副作用与补偿策略；
- 版本与兼容性；
- 可观测 Trace 和 Evidence。

MCP 可以承担跨进程能力发现和调用协议，但业务不变量仍由 Capability 背后的服务控制。

## 53.5 动态 UI，而不是没有 UI

对话适合表达模糊目标，不适合所有验证任务。让用户在长段文字中检查 50 个价格，比表格差异视图更差；审批付款时，结构化金额、对象和影响范围比一句“是否继续”更安全。

AI Native UI 应根据当前状态投射交互：

| 状态 | 推荐交互 |
| --- | --- |
| Goal 不完整 | 澄清问题 / Constraint Builder |
| Plan 已生成 | Step Timeline / 可编辑计划 |
| Evidence 到达 | Table / Chart / Citation View |
| 存在不确定性 | Alternatives / Confidence / Assumptions |
| 即将产生副作用 | Approval Card / Diff / Impact Preview |
| 运行失败 | Recovery Options / Human Handoff |

生成式 UI 必须使用受控组件和 Schema，不能让模型生成任意可执行前端代码后直接部署。

## 53.6 上下文与记忆成为产品状态

传统应用的状态主要是数据库字段；AI Native 系统还需要管理：

- 当前 Goal 和约束；
- 已确认与未确认的假设；
- Plan、Observation 和失败历史；
- 来源、证据和引用；
- 用户偏好及其来源；
- Confidence 和需要人工决策的节点；
- Context 的版本、过期和删除。

记忆不能等同于保存全部聊天。企业系统应区分会话状态、业务事实、用户偏好和审计记录，并为每类数据设置权限和生命周期。

## 53.7 模型可替换与降级设计

AI Native 系统不应把业务语义藏在单个模型的 Prompt 中。建议采用：

- Schema 作为模型与 Runtime 的边界；
- Eval Dataset 作为行为契约；
- Model Gateway 隔离供应商差异；
- Capability API 隔离业务系统；
- Prompt、Policy 和 Knowledge 独立版本；
- 降级到搜索、固定 Workflow 或人工处理。

当模型不可用时，核心业务仍应保持一致性。不能完成动态规划，可以退回受限工作流；不能生成解释，可以返回原始证据；不能安全执行，就转人工。

## 53.8 业务场景：采购协同系统

用户输入：

> 为华东工厂选择三家合格备件供应商并生成询价草案，预算不超过 20 万元，不要自动发送。

系统执行：

1. Goal Compiler 提取区域、供应商资质、预算和禁止自动发送；
2. Planner 发现 `retrieve_approved_suppliers`、`compare_price_and_risk`、`draft_request_for_quote`；
3. Policy 拒绝未授权供应商和自动发送能力；
4. Runtime 生成比较结果、来源和询价草案；
5. UI 显示供应商表格、风险原因和缺失数据；
6. 用户调整数量后批准；
7. 确定性采购服务创建询价记录并审计。

模型决定“建议比较什么”，采购服务决定“什么记录可以创建”。

## 53.9 Python MVP：Goal-to-Capability Planner

本章示例使用标准库实现一个最小 AI Native 控制链：

- `Goal` 保存自然语言目标、预算和约束；
- `Capability` 声明依赖、产物、成本和副作用；
- Planner 根据目标产物动态补齐中间步骤；
- 计划超预算时确定性失败；
- Side Effect 被标记为需要审批；
- 同一 Plan 被投射为前端可消费的 UI Block。

```bash
cd chapters/chapter53
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python example.py
```

示例目标只要求生成 `rfq_draft`，所以不会把发送动作加入计划。这展示了 Goal-driven 不等于最大化自动化，而是严格完成用户授权的结果。

**与模型的关系**：生产系统可让模型把自然语言编译为 Goal，并生成或排序 Plan Proposal；离线 MVP 使用确定性依赖规划器验证 Capability、预算和副作用边界。模型负责语义，Runtime 负责约束。

## 53.10 演进路线

### Stage 1：AI-assisted Feature

选择一个高频、低风险、可评测任务，用 Copilot 提升效率。先建立 Trace 和人工反馈。

### Stage 2：Governed Agent Workflow

把 Goal、Plan、Tool、Policy 和 Evidence 显式化。关键动作仍由 Workflow 和人工审批控制。

### Stage 3：Capability Platform

将多个业务服务包装为可发现、可授权的 Capability，建立统一身份、Registry、Eval 和 Runtime。

### Stage 4：AI Native Product

产品交互围绕 Goal 和 Evidence 组织，系统可以在策略内动态组合能力，并对失败、降级和长期记忆负责。

每一阶段都应由任务成功率、风险、成本和用户采用证明价值，而不是由模型能力推动架构升级。

## 53.11 常见反模式

- 把所有页面替换为一个聊天框；
- 让 Agent 直接写核心数据库；
- 用自然语言 Prompt 代替权限和事务约束；
- 为“智能”隐藏计划、证据和不确定性；
- 自动记住所有对话，不区分事实、偏好和隐私；
- 把模型升级当成功能发布，跳过回归评测；
- 只设计 Happy Path，没有降级和人工接管。

## Summary

AI Native Software 的核心不是 AI 数量，而是软件是否能够围绕 Goal 动态组织能力，并通过确定性核心、策略和证据保持可信。未来的界面会更动态，但业务不变量必须更明确。

最后一章将回到软件工程本身：当 Agent 可以理解代码库、提出变更并执行工具时，工程师的工作单元、交付流程和能力结构会如何变化？

## References

- [Model Context Protocol Architecture](https://modelcontextprotocol.io/specification/2025-06-18/architecture)
- [NIST AI Risk Management Framework](https://www.nist.gov/itl/ai-risk-management-framework)
- [OpenTelemetry Signals](https://opentelemetry.io/docs/concepts/signals/)
