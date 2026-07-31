# Chapter 6 Token

Part II LLM Foundations —— Agent 为什么能够工作

Version: 2026-07

Last Updated: 2026-07-31

## Core Question

为什么 Token 不是字符？为什么 Agent 工程师必须理解 Token？

## Chapter Conclusion

Token 是 LLM 处理文本的基本单位，也是上下文窗口、成本估算、输出控制和工具参数设计的基础。

对 Agent 工程而言，Token 决定了：

- 一次请求能放多少上下文
- 长文档为什么必须 chunk
- 工具结果为什么要压缩
- 成本为什么和输入输出规模相关
- JSON 输出为什么需要 schema 和长度控制

## Learning Objectives

完成本章后，你应该能够理解：

- Token 与字符、单词的区别
- BPE 的基本思想
- Token budget 如何影响 Agent Context
- 为什么工具返回结果不能无限长
- 如何在代码中做简化版 token 估算

## 6.1 原理剖析：Token 不是字符

LLM 不直接处理字符串。

在进入模型之前，文本会先经过 Tokenizer，被切分成 token id 序列。

例如：

```text
"AI Agent Engineering"
  ↓
["AI", " Agent", " Engineering"]
  ↓
[token_id_1, token_id_2, token_id_3]
```

Token 可能是一个字符、一个词、一个词的一部分，也可能包含前导空格。

这就是为什么同样长度的中文、英文、代码、JSON，token 数可能完全不同。

对 Agent 来说，这件事非常实际：

- 用户问题占 token
- 系统提示词占 token
- 工具说明占 token
- 工具结果占 token
- 历史消息占 token
- 模型输出也占 token

所以 Agent Runtime 必须管理 token budget。

## 6.2 BPE 的基本思想

BPE（Byte Pair Encoding）的直觉是：

从小单位开始，不断把高频相邻片段合并成更大的 token。

例如：

```text
l o w
l o w e r
n e w e s t
```

如果 `l + o` 经常一起出现，就合并为 `lo`。

如果 `lo + w` 经常出现，就合并为 `low`。

最终，常见词会被切成较少 token，罕见词会被拆成更小片段。

这让模型可以处理开放词表，同时控制词表规模。

## 6.3 架构设计：Token Budget

一个 Agent 请求的上下文可以理解为：

```text
System Prompt
  +
Developer Instructions
  +
User Goal
  +
Tool Definitions
  +
Memory
  +
Retrieved Knowledge
  +
Tool Results
  +
Output Budget
```

如果总 token 超过模型 context window，请求就会失败，或者必须截断。

因此，Agent Runtime 需要一个 Context Budget Manager：

```text
Input Sources
  ↓
Token Estimate
  ↓
Priority Ranking
  ↓
Compression / Truncation
  ↓
Final Context
```

## 6.4 工具横向对比

| 工具 / 框架 | Token 相关能力 | 工程关注点 |
|---|---|---|
| OpenAI API | 模型上下文、输入输出 token、结构化输出 | 控制 prompt、tool result、output budget |
| Anthropic Claude | 长上下文能力突出 | 长文档仍需组织和引用管理 |
| LlamaIndex | Chunk、Index、Retriever | 把长文档切成可检索片段 |
| LangGraph | 状态和消息管理 | 避免 graph state 无限膨胀 |
| 本书 framework | 简化 Token Budget Manager | 先做估算、裁剪和优先级 |

## 6.5 业务场景案例：企业知识库问答

用户问：

```text
根据公司差旅制度，上海到北京出差高铁二等座能不能报销？
```

Agent 可能检索到 20 段制度文本。

如果全部塞进上下文：

- 成本上升
- 延迟上升
- 模型可能关注无关片段
- 输出可能引用错误条款

更合理的做法是：

- 先估算 token
- 按相关性排序
- 保留最相关片段
- 对过长片段做摘要
- 给输出保留预算

## Python MVP

本章示例实现一个简化 BPE Tokenizer 和 token budget 裁剪器。

运行：

```bash
python chapters/chapter06/example.py
```

## Summary

Token 是 LLM 的输入输出单位。Agent 工程师不需要实现工业级 tokenizer，但必须理解 token budget 对上下文、成本、延迟和工具结果设计的影响。

## Notes

本章示例是教学版 tokenizer，不等价于任何真实模型 tokenizer。真实项目应使用模型供应商或开源库提供的 tokenizer。

## References

[1] Sennrich et al.  
Neural Machine Translation of Rare Words with Subword Units.  
https://arxiv.org/abs/1508.07909

[2] OpenAI.  
A Practical Guide to Building Agents.  
https://openai.com/business/guides-and-resources/a-practical-guide-to-building-ai-agents/

以上 URL 已在 2026-07-31 验证可访问。
