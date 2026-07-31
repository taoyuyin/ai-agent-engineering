# Chapter 9 Reasoning

Part II LLM Foundations —— Agent 为什么能够工作

Version: 2026-07

Last Updated: 2026-07-31

## Core Question

Reasoning、CoT、ReAct、ToT、Reflection 分别解决什么问题？Agent 工程师应该如何使用这些思想？

## Chapter Conclusion

Reasoning 技术让模型从直接回答走向显式中间步骤、工具交互、多路径探索和自我修正。

对 Agent 工程而言，Reasoning 不是“让模型想得更玄”，而是把复杂任务拆成可观察、可验证、可恢复的执行过程。

## Learning Objectives

完成本章后，你应该能够理解：

- CoT 为什么能改善多步问题
- ReAct 如何把 reasoning 和 acting 结合起来
- ToT 为什么适合多路径探索
- Reflection 如何用于失败修复
- Reasoning 在企业 Agent 中的边界

## 9.1 CoT：显式中间步骤

Chain-of-Thought 的基本思想是让模型在回答前生成中间推理步骤。

工程直觉是：

复杂任务不要直接从问题跳到答案，而要把中间过程显式化。

对 Agent 来说，中间步骤可以变成：

- 计划
- 子任务
- 工具调用理由
- 结果解释
- 验证清单

## 9.2 ReAct：Reason + Act

ReAct 把推理和行动交替组织：

```text
Thought
  ↓
Action
  ↓
Observation
  ↓
Thought
```

这和 Agent Runtime 非常接近。

ReAct 的价值在于，模型不是一次性回答，而是边思考、边调用工具、边观察结果。

## 9.3 ToT：多路径探索

Tree of Thoughts 的核心是保留多个候选路径。

对一些任务，第一条推理路径未必最好。

例如业务原因分析：

- 路径 A：先查销售额
- 路径 B：先查成本
- 路径 C：先查库存

ToT 的工程化版本可以是：生成多个候选计划，然后评分选择。

## 9.4 Reflection：自我检查与修复

Reflection 让 Agent 在失败后进行自我检查。

常见触发条件：

- 工具调用失败
- 输出格式不合法
- 结果置信度低
- 验证器不通过
- 用户指出错误

Reflection 不应该无限循环。企业系统必须设置最大重试次数、失败原因记录和人工交接。

## 9.5 架构设计：Reasoning Controller

一个工程化 Reasoning Controller：

```text
Goal
  ↓
Generate Candidate Steps
  ↓
Score / Select
  ↓
Execute Tool
  ↓
Validate Observation
  ↓
Reflect or Continue
```

它把“推理”变成可控制的运行时策略。

## 9.6 工具横向对比

| 方法 / 工具 | 核心思想 | 适用场景 |
|---|---|---|
| CoT | 显式中间推理 | 数学、解释、分析 |
| ReAct | 推理与行动交替 | 工具调用、多步任务 |
| ToT | 多候选路径探索 | 规划、复杂决策 |
| Reflection | 失败后自我修复 | 调试、重试、质量控制 |
| LangGraph | 用图控制推理流程 | 可恢复 Agent |
| 本书 framework | 用 Python 状态机实现 | 教学与企业落地 |

## 9.7 业务场景案例：客户流失分析

用户问：

```text
分析过去三个月客户流失的主要原因。
```

Agent 可以生成多个候选分析路径：

- 产品使用下降
- 客服投诉增加
- 价格变化
- 竞品影响

然后逐步查询数据，观察结果，再调整计划。

## Python MVP

本章示例实现一个迷你 ReAct Loop：根据目标选择工具，观察结果，再决定是否继续。

运行：

```bash
python chapters/chapter09/example.py
```

## Summary

Reasoning 在 Agent 工程中不是神秘能力，而是可设计的执行策略。好的 Agent 会把推理过程显式化、工具化、可观察化，并设置失败边界。

## References

[1] Yao et al.  
ReAct: Synergizing Reasoning and Acting in Language Models.  
https://arxiv.org/abs/2210.03629

[2] Yao et al.  
Tree of Thoughts.  
https://arxiv.org/abs/2305.10601

[3] Shinn et al.  
Reflexion.  
https://arxiv.org/abs/2303.11366

以上 URL 已在 2026-07-31 验证可访问。
