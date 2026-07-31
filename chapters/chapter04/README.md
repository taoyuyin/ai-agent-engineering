# Chapter 4 Agent 与 Workflow 的区别

Part I Foundations —— 为什么需要 AI Agent

Version: 2026-07

Last Updated: 2026-07-31

## Core Question

Agent 与 Workflow 到底有什么区别？

## Chapter Conclusion

Workflow 和 Agent 都可以组织任务执行，但它们解决的问题不同。

Workflow 的核心是预定义流程。它适合步骤明确、路径可控、规则稳定的任务。

Agent 的核心是目标驱动。它适合目标明确但路径不确定、需要动态判断和工具选择的任务。

一句话概括：

Workflow 适合“流程已知”的任务，Agent 适合“目标已知但路径未知”的任务。

在真实企业系统中，两者不是互斥关系，而是经常组合使用：

```text
Workflow 控制边界
Agent 处理开放性步骤
```

## Learning Objectives

完成本章后，你应该能够理解：

- Workflow 为什么不是 Agent
- Agent 为什么不等于 Workflow
- 什么场景适合 Workflow
- 什么场景适合 Agent
- 为什么企业系统通常需要 Agent + Workflow 组合

## 4.1 为什么这个问题重要

在 Agent 工程实践中，最常见的混淆之一，就是把 Agent 和 Workflow 混为一谈。

有些系统本质上是固定流程，但因为中间调用了 LLM，就被称为 Agent。

有些系统本质上需要动态决策，却被强行设计成复杂 Workflow，结果流程越来越难维护。

这两种做法都会带来问题。

如果把 Workflow 误认为 Agent，就会高估系统自主性。

如果把 Agent 误认为 Workflow，就会试图提前写死所有可能路径。

因此，在进入 Agent Architecture 之前，必须先建立一个清晰边界：

Workflow 和 Agent 都是任务执行组织方式，但它们的控制逻辑不同。

## 4.2 Workflow 的核心是预定义流程

Workflow 的核心是：

开发者提前定义任务的执行路径。

典型 Workflow 可以表示为：

```text
Step A
  ↓
Step B
  ↓
Condition
  ├── Step C
  └── Step D
  ↓
Step E
```

Workflow 通常具备这些特点：

- 步骤提前定义
- 分支条件提前定义
- 输入输出结构明确
- 每个节点职责清晰
- 失败处理路径可设计
- 容易测试、审计和复现

例如，报销审批流程非常适合 Workflow：

```text
提交报销单
  ↓
直属主管审批
  ↓
财务审核
  ↓
付款
  ↓
归档
```

这个过程不需要 Agent 自主决定下一步。

系统应该严格按照企业制度执行。

在这种场景中，引入过多 Agent 自主性，反而会降低可靠性。

## 4.3 Agent 的核心是目标驱动

Agent 的核心不是预定义流程，而是围绕目标动态决定下一步。

典型 Agent 执行过程可以表示为：

```text
Goal
  ↓
Observe
  ↓
Decide
  ↓
Act
  ↓
Observe
  ↓
Continue / Stop
```

Agent 通常具备这些特点：

- 目标可以由自然语言表达
- 执行路径不完全预定义
- 下一步动作依赖中间结果
- 可能需要选择不同工具
- 可能需要修改计划
- 可能需要重试、反思或请求人工介入

例如：

```text
分析过去三个月客户流失的主要原因，并给出改进建议。
```

这个任务很难提前写死完整流程。

Agent 可能先查客户流失率，再按行业、地区、产品、客户规模拆解，也可能进一步分析客服工单、产品使用日志或续约记录。

下一步取决于上一轮观察结果。

这就是 Agent 与 Workflow 的关键差异。

## 4.4 为什么 Workflow 不是 Agent

Workflow 可以使用 LLM。

例如，一个固定流程中可以有一个节点：

```text
读取用户反馈
  ↓
调用 LLM 生成摘要
  ↓
进入人工审核
```

这个系统使用了 LLM，但它仍然是 Workflow。

因为它的执行路径由开发者提前定义。

LLM 只是其中一个处理节点。

类似地，一个客服工单系统可以：

```text
接收工单
  ↓
LLM 分类
  ↓
按分类进入固定队列
  ↓
人工处理
```

这仍然不是 Agent。

它是 AI-enhanced Workflow。

判断一个系统是不是 Agent，关键不是它有没有调用 LLM，而是：

执行路径是否由系统在运行时根据目标和反馈动态决定。

## 4.5 为什么 Agent 不等于 Workflow

反过来，Agent 也不等于 Workflow。

Agent 可以包含 Workflow，但 Agent 的核心不是固定流程。

Agent 更像一个运行时：

```text
目标输入
  ↓
计划生成
  ↓
工具调用
  ↓
观察结果
  ↓
计划调整
  ↓
继续执行
```

它的流程在运行时展开。

当然，Agent 不能无限自由。

企业级 Agent 必须有边界：

- 哪些工具可以调用
- 哪些数据可以访问
- 哪些动作必须人工确认
- 哪些结果必须经过校验
- 什么时候停止

这些边界往往需要 Workflow、Policy、Guardrails 和权限系统来控制。

所以 Agent 不是 Workflow 的替代品。

Agent 需要 Workflow 提供确定性边界。

## 4.6 什么时候使用 Workflow

当任务满足以下特征时，优先使用 Workflow：

- 流程稳定
- 步骤明确
- 分支条件清楚
- 合规和审计要求高
- 不希望系统自主改变路径
- 输出格式和责任边界固定

典型场景包括：

- 审批流程
- 财务结算
- 数据同步
- 定时任务
- 报表生成
- 标准化工单流转
- CI/CD 发布流程

在这些场景中，确定性比灵活性更重要。

使用 Workflow 可以提高可预测性、可测试性和可审计性。

## 4.7 什么时候使用 Agent

当任务满足以下特征时，适合使用 Agent：

- 目标明确，但路径不确定
- 输入是自然语言或半结构化信息
- 需要动态选择工具
- 需要根据中间结果调整计划
- 需要处理开放性问题
- 需要结合多个数据源或系统

典型场景包括：

- 数据分析
- SQL 生成与解释
- 合同风险提取
- 企业知识问答
- 代码修改与调试
- 客服问题诊断
- 复杂业务原因分析

在这些场景中，灵活性比固定流程更重要。

Agent 的价值在于，它可以根据目标和观察结果动态组织执行过程。

## 4.8 企业系统通常需要组合使用

真实企业系统很少只需要 Workflow 或只需要 Agent。

更常见的模式是组合：

```text
Workflow
  ↓
Agent Step
  ↓
Workflow
  ↓
Human Review
  ↓
Workflow
```

例如，一个合同审查系统可以这样设计：

```text
上传合同
  ↓
Workflow 校验文件格式
  ↓
Agent 阅读合同并提取风险点
  ↓
Workflow 判断风险等级
  ↓
高风险进入法务审核
  ↓
低风险自动归档
```

在这个系统中：

- Workflow 控制流程边界
- Agent 处理开放性理解任务
- Human Review 处理高风险决策

这比单纯使用 Agent 更安全，也比单纯使用 Workflow 更灵活。

## 4.9 一个判断准则

可以用一个简单问题判断：

这个任务的执行路径，是否可以在开发时基本确定？

如果答案是“可以”，优先使用 Workflow。

如果答案是“不可以，需要根据中间结果动态决定”，考虑使用 Agent。

进一步判断：

```text
流程已知，规则稳定
  → Workflow

目标已知，路径未知
  → Agent

部分流程固定，部分步骤开放
  → Workflow + Agent
```

这个准则并不复杂，但非常重要。

很多 Agent 项目的失败，不是模型能力不够，而是一开始就把问题放错了架构位置。

## Summary

Workflow 和 Agent 都是任务执行组织方式，但它们的控制逻辑不同。

Workflow 的核心是预定义流程，适合流程稳定、规则明确、合规要求高的任务。

Agent 的核心是目标驱动，适合目标明确但路径不确定、需要动态判断和工具选择的任务。

Workflow 不是 Agent，因为调用 LLM 的固定流程仍然是 Workflow。

Agent 也不等于 Workflow，因为 Agent 的执行路径在运行时根据目标和反馈展开。

在企业系统中，最常见也最可靠的模式是：

Workflow 控制边界，Agent 处理开放性步骤。

## Notes

Anthropic 在 “Building Effective Agents” 中明确区分了 Workflow 和 Agent：Workflow 是通过预定义代码路径编排模型和工具，Agent 则由模型动态指导流程和工具使用。

本书后续会沿用这个边界：Workflow 用于确定性控制，Agent 用于开放性执行。

## References

[1] Anthropic.  
Building Effective Agents.  
https://www.anthropic.com/engineering/building-effective-agents

[2] OpenAI.  
A Practical Guide to Building Agents.  
https://openai.com/business/guides-and-resources/a-practical-guide-to-building-ai-agents/

[3] Google.  
Agent Development Kit Documentation.  
https://adk.dev/

以上 URL 已在 2026-07-31 验证可访问。
