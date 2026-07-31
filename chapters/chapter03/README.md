# Chapter 3 什么是真正的 AI Agent？

Part I Foundations —— 为什么需要 AI Agent

Version: 2026-07

Last Updated: 2026-07-31

## Core Question

什么是真正的 AI Agent？

## Chapter Conclusion

AI Agent 不是“接入了 LLM 的应用”，也不是“能调用工具的聊天机器人”。

本书采用一个工程化定义：

AI Agent 是一个围绕目标运行的软件执行系统。它能够理解目标、规划步骤、调用工具、管理上下文和记忆，并根据反馈持续调整执行过程，直到任务完成、失败或交还给人类。

统一表达为：

```text
Agent = Goal + Planning + Tool + Memory + Feedback
```

## Learning Objectives

完成本章后，你应该能够理解：

- 为什么 Agent 需要一个清晰定义
- OpenAI、Anthropic、Google 对 Agent 的定义侧重点
- 为什么 LLM 应用不一定是 Agent
- Agent 的五个核心组成
- 本书后续采用的统一工程定义

## 3.1 为什么必须先定义 Agent

“Agent” 是一个很容易被泛化使用的词。

有些产品把接入 LLM 的聊天机器人称为 Agent。

有些框架把能够调用工具的程序称为 Agent。

有些平台把预设工作流、知识库问答、自动化脚本都称为 Agent。

这些说法并非完全错误，但如果没有清晰定义，工程讨论就会变得混乱。

例如，当我们说“构建一个企业级 Agent”时，到底是在说：

- 一个带 Prompt 的聊天应用？
- 一个能调用 API 的模型应用？
- 一个固定 Workflow？
- 一个能自主规划和执行的 Runtime？
- 一个包含权限、审计、评测、观测的平台？

如果定义不清，后续讨论 Planning、Memory、Tool、Evaluation、Guardrails 都会混在一起。

因此，本章先给出本书采用的工程定义。

## 3.2 LLM 应用不等于 Agent

最简单的 LLM 应用是：

```text
User Input
  ↓
LLM
  ↓
Response
```

这种应用可以很有价值。

它可以回答问题、总结内容、翻译文本、生成文案。

但它还不是本书意义上的 Agent。

原因很简单：

它没有持续执行一个目标。

它只是对输入做一次响应。

如果一个系统只是把用户问题发送给模型，然后把模型输出返回给用户，那么它是 LLM Application，不是 Agent Runtime。

Agent 至少需要多出一层执行组织能力：

```text
Goal
  ↓
Plan
  ↓
Action
  ↓
Observation
  ↓
Next Action
```

这意味着 Agent 不是一次性响应，而是一个围绕目标展开的执行循环。

## 3.3 Tool Calling 也不自动等于 Agent

现代模型应用经常支持工具调用。

例如，模型可以生成一个函数调用：

```json
{
  "name": "query_sales",
  "arguments": {
    "start_date": "2026-04-01",
    "end_date": "2026-06-30"
  }
}
```

这是一项非常重要的能力。

但工具调用本身仍然不等于 Agent。

因为一个系统可能只是：

```text
User Input
  ↓
LLM selects tool
  ↓
Tool executes
  ↓
LLM returns answer
```

如果这个过程没有目标状态、没有计划更新、没有反馈循环、没有失败恢复，它仍然只是一个带工具的模型应用。

Agent 的关键不是“能不能调用工具”，而是“能不能围绕目标组织工具调用”。

Tool 是 Agent 的组成部分，但 Tool 不是 Agent 本身。

## 3.4 不同来源如何理解 Agent

不同厂商和社区对 Agent 的表述有差异，但有一些共同点。

OpenAI 在 Agent 构建指南中强调，Agent 可以独立代表用户完成任务，并通常具备模型、工具、指令和执行控制等要素。

Anthropic 在 “Building Effective Agents” 中区分了 Workflow 和 Agent：Workflow 通常是预定义路径，而 Agent 则更强调模型动态决定流程和工具使用方式。

Google ADK 则从开发框架角度强调 Agent、Tool、Session、Runner 等工程组件，关注如何把 Agent 应用组织成可运行系统。

这些定义的表述不同，但共同指向一个事实：

Agent 不是孤立模型，而是一个围绕任务执行的系统。

## 3.5 Agent 的五个组成

本书采用一个简化但足够工程化的结构：

```text
Agent = Goal + Planning + Tool + Memory + Feedback
```

### Goal

Goal 是 Agent 要完成的目标。

它可能来自用户自然语言，也可能来自系统事件、业务流程或另一个 Agent。

Goal 的关键在于，它不是简单指令，而是任务的完成意图。

例如：

```text
帮我分析本季度利润下降的主要原因
```

这个 Goal 隐含了数据范围、分析对象、输出形式和业务判断。

Agent 首先要理解这个目标。

### Planning

Planning 是把目标转换成可执行步骤的过程。

它回答：

- 需要做哪些事情？
- 先做什么，后做什么？
- 哪些步骤依赖外部工具？
- 如果结果不符合预期，下一步怎么办？

Planning 可以很简单，也可以很复杂。

早期章节中，我们会先实现最小 Planner，再逐步引入动态计划、计划修复和多 Agent 协作。

### Tool

Tool 是 Agent 与外部世界交互的方式。

工具可以是：

- 数据库查询
- API 调用
- 文件读写
- 浏览器操作
- 代码执行
- 搜索服务
- 企业系统接口

没有 Tool，Agent 很容易停留在“说”的层面。

有了 Tool，Agent 才能真正“做事”。

### Memory

Memory 是 Agent 对任务状态和历史信息的管理能力。

它可以分为：

- Working Memory：当前任务中的短期上下文
- Long-term Memory：跨任务保留的长期信息
- Retrieval Memory：通过检索获得的相关知识

Memory 的核心问题不是“存更多内容”，而是“在正确时间拿出正确内容”。

### Feedback

Feedback 是 Agent 根据执行结果调整行为的机制。

工具执行后会产生结果，模型输出后会产生反馈，用户也可能在中途修正目标。

Agent 需要根据这些反馈判断：

- 当前步骤是否成功？
- 是否需要重试？
- 是否需要修改计划？
- 是否应该停止？
- 是否需要交给人类？

没有 Feedback，Agent 就无法形成闭环。

## 3.6 本书采用的统一定义

综合以上讨论，本书采用下面的工程定义：

AI Agent 是一个围绕目标运行的软件执行系统。它能够理解目标、规划步骤、调用工具、管理上下文和记忆，并根据反馈持续调整执行过程，直到任务完成、失败或交还给人类。

这个定义有几个关键点。

第一，Agent 是软件系统，不是模型。

第二，Agent 围绕目标运行，不只是响应输入。

第三，Agent 需要工具和外部系统，否则无法完成真实任务。

第四，Agent 需要状态、记忆和反馈，否则无法持续执行。

第五，Agent 必须有边界。真正的工程系统需要知道什么时候停止、什么时候失败、什么时候请求人工介入。

## 3.7 一个最小 Agent 结构

最小 Agent 可以抽象为：

```text
Goal
  ↓
Observe
  ↓
Plan / Decide
  ↓
Act
  ↓
Observe
  ↓
Stop or Continue
```

这也是后续 `framework/runtime` 会逐步实现的核心循环。

我们不会一开始就使用复杂框架，而是先从这个循环开始。

只有先理解这个循环，才能真正理解 OpenAI Agents SDK、LangGraph、Google ADK、CrewAI、AutoGen 等框架为什么会设计出各自的抽象。

## Summary

Agent 不是一个模糊的营销词。

在本书中，Agent 是一个围绕目标运行的软件执行系统。

LLM 是 Agent 的推理能力来源，但 LLM 不等于 Agent。

Tool Calling 是 Agent 的重要能力，但 Tool Calling 也不自动等于 Agent。

一个真正的 Agent 至少需要 Goal、Planning、Tool、Memory、Feedback 五个组成。

本章给出的统一定义，将作为后续全书讨论 Agent Runtime、Workflow、Evaluation、Guardrails、Multi-Agent 和 Enterprise Agent 的基础。

## Notes

本章定义是工程化定义，不试图覆盖人工智能研究中所有 Agent 概念。

OpenAI、Anthropic、Google 的定义侧重点不同。OpenAI 更强调实际构建 Agent 应用，Anthropic 更强调 Workflow 与 Agent 的边界，Google ADK 更强调工程框架组件。本书会在这些定义之间建立统一抽象。

## References

[1] OpenAI.  
A Practical Guide to Building Agents.  
https://openai.com/business/guides-and-resources/a-practical-guide-to-building-ai-agents/

[2] Anthropic.  
Building Effective Agents.  
https://www.anthropic.com/engineering/building-effective-agents

[3] Google.  
Agent Development Kit Documentation.  
https://adk.dev/

[4] Stuart Russell, Peter Norvig.  
Artificial Intelligence: A Modern Approach.  
https://aima.cs.berkeley.edu/

以上 URL 已在 2026-07-31 验证可访问。
