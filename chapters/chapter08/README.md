# Chapter 8 Context

Part II LLM Foundations —— Agent 为什么能够工作

Version: 2026-07

Last Updated: 2026-07-31

## Core Question

Context Window、KV Cache 和“模型遗忘”到底是什么？为什么 Agent 工程离不开 Context 管理？

## Chapter Conclusion

Context 是模型当前可见的工作空间。模型不会自动记住所有历史事实，它只能基于当前请求中的上下文生成输出。

Agent 工程的关键任务之一，就是把目标、记忆、工具结果、检索知识和约束组装成高质量上下文。

## Learning Objectives

完成本章后，你应该能够理解：

- Context Window 的工程含义
- KV Cache 为什么影响推理效率
- 模型为什么会“遗忘”
- Context Assembly 的基本设计
- 如何用优先级管理上下文

## 8.1 原理剖析：Context Window

Context Window 是模型一次请求能处理的最大 token 范围。

它不是数据库，也不是长期记忆。

如果某条信息没有进入当前 context，模型就无法可靠使用它。

这解释了为什么 Agent 需要 Memory 和 Retrieval。

Memory 负责存储，Retrieval 负责取回，Context Engineering 负责把取回的信息放进当前请求。

## 8.2 KV Cache 的工程直觉

Transformer 推理时，会为已经处理过的 token 保存 Key / Value。

生成下一个 token 时，可以复用这些缓存，而不是每次从头计算整个序列。

这就是 KV Cache 的直觉。

它对 Agent 的影响包括：

- 长上下文会增加首 token 延迟
- 长输出会持续占用推理资源
- 多轮对话如果不断追加历史，成本和延迟都会上升
- Streaming 可以改善用户感知延迟，但不减少总计算

## 8.3 为什么模型会“遗忘”

用户常说“模型忘了前面说过的话”，工程上通常有几种原因：

- 历史消息没有被传入当前请求
- 历史太长，被系统截断
- 相关信息被低质量上下文淹没
- 模型注意到错误片段
- 记忆没有被正确检索

因此，“遗忘”不一定是模型能力问题，也可能是 Agent Runtime 的上下文管理问题。

## 8.4 架构设计：Context Assembler

一个 Context Assembler 可以这样设计：

```text
Goal
  +
System Instruction
  +
Tool Definitions
  +
Short-term Memory
  +
Retrieved Knowledge
  +
Tool Observations
  ↓
Priority Ranking
  ↓
Token Budget
  ↓
Final Prompt
```

关键不是“放最多”，而是“放最有用”。

## 8.5 工具横向对比

| 工具 / 框架 | Context 管理方式 | 工程关注点 |
|---|---|---|
| OpenAI Responses / Agents | 支持工具、状态、trace 等 Agent 工作流能力 | 管理输入、工具结果和输出格式 |
| Anthropic | 强调清晰上下文和 workflow/agent 边界 | 长上下文仍需选择和组织 |
| LangGraph | 用 state 管理多步上下文 | 防止 state 无限膨胀 |
| LlamaIndex | 用 retriever 控制知识进入上下文 | chunk、top-k、rerank |
| 本书 framework | ContextAssembler + TokenBudget | 教学实现，理解边界 |

## 8.6 业务场景案例：合同审查 Agent

合同审查 Agent 需要上下文：

- 审查目标
- 合同片段
- 公司法务规则
- 历史相似案例
- 已发现风险点
- 输出格式

如果把整份合同和所有制度一次性塞入 context，成本高且不稳定。

更合理的方式是按条款检索、分段审查、汇总风险。

## Python MVP

本章示例实现一个按优先级和 token budget 组装 context 的最小版本。

运行：

```bash
python chapters/chapter08/example.py
```

## Summary

Context 是模型当前可见的信息边界。Agent 可靠性很大程度取决于 Context Engineering，而不是单纯依赖模型“记忆力”。

## References

[1] OpenAI.  
A Practical Guide to Building Agents.  
https://openai.com/business/guides-and-resources/a-practical-guide-to-building-ai-agents/

[2] Anthropic.  
Building Effective Agents.  
https://www.anthropic.com/engineering/building-effective-agents

以上 URL 已在 2026-07-31 验证可访问。
