# Chapter 5 Transformer

Part II LLM Foundations —— Agent 为什么能够工作

Version: 2026-07

Last Updated: 2026-07-31

## Core Question

为什么 Transformer 会成为现代 LLM 的基础结构？它和 AI Agent 工程有什么关系？

## Chapter Conclusion

Transformer 的关键价值不只是“效果更好”，而是它让模型能够在大规模数据和大规模参数下高效学习语言中的依赖关系。

对 Agent 工程而言，Transformer 解释了三个底层事实：

- LLM 为什么能够理解上下文中的语义关系
- LLM 为什么可以根据不同位置的信息生成下一步输出
- Agent 为什么必须认真管理 Context，而不是把所有信息都塞给模型

## Learning Objectives

完成本章后，你应该能够理解：

- RNN / Seq2Seq 在长文本建模上的瓶颈
- Attention 解决了什么问题
- Self-Attention 如何计算 token 之间的关系
- Transformer 为什么更适合大规模并行训练
- Transformer 对 Agent 的上下文理解意味着什么

## 5.1 原理剖析：为什么需要 Attention

在 Transformer 之前，序列建模常见方法包括 RNN、LSTM、GRU 和 Seq2Seq。

这些模型的共同特点是：信息沿着序列一步步传递。

```text
token1 → token2 → token3 → token4 → output
```

这种结构对短文本有效，但对长文本会遇到两个问题。

第一，长距离依赖难以保留。

如果一句话前面出现了关键实体，后面才出现动作，模型需要把前面的信息一路传到后面。序列越长，信息越容易衰减。

第二，训练难以充分并行。

RNN 类结构天然依赖前一步的隐藏状态，因此不容易像矩阵乘法那样大规模并行。

Attention 的核心思想是：

当前 token 在生成表示时，不必只依赖前一个状态，而是可以直接“看”序列中其他 token，并为它们分配不同权重。

例如：

```text
“利润下降的主要原因是什么？”
```

当模型处理“原因”时，它应该重点关注“利润下降”，而不是平均看待所有词。

Attention 让这种“选择性关注”变成可计算结构。

## 5.2 Self-Attention 的工程直觉

Self-Attention 可以理解为：序列中的每个 token 都向其他 token 提问。

每个 token 会生成三个向量：

- Query：我想找什么信息
- Key：我能提供什么信息
- Value：如果别人关注我，我贡献什么内容

计算过程可以简化为：

```text
score = Query · Key
weight = softmax(score)
output = weight · Value
```

对软件工程师来说，不需要一开始就纠结所有矩阵细节。更重要的是理解：

Self-Attention 让模型可以动态计算 token 之间的关系。

这就是 LLM 能够在上下文中关联目标、约束、工具结果和历史消息的基础。

## 5.3 架构设计：Transformer 的关键组件

一个简化 Transformer Block 可以表示为：

```text
Token Embedding
  ↓
Positional Encoding
  ↓
Multi-Head Self-Attention
  ↓
Feed Forward Network
  ↓
LayerNorm / Residual
  ↓
Next Token Prediction
```

对 Agent 工程最重要的是三点。

第一，模型输入不是字符串，而是 token 序列。

第二，模型在当前 context 内计算 token 之间的关系。

第三，模型输出本质上仍然是下一个 token 的概率分布。

这意味着 Agent Runtime 不能把模型当成全知的数据库，也不能假设模型自动记住所有业务事实。

Agent 必须负责：

- 选择哪些信息进入上下文
- 控制上下文长度
- 把工具结果组织成模型容易使用的格式
- 在上下文不足时检索外部知识

## 5.4 工具横向对比

| 工具 / 框架 | 与 Transformer 的关系 | 对工程师的意义 |
|---|---|---|
| OpenAI API | 封装 Transformer / MoE / Reasoning Model 等模型能力 | 关注 context、tool calling、structured output |
| Anthropic Claude | 强调长上下文和安全对齐 | 适合长文档、复杂推理和 workflow/agent 区分 |
| Google Gemini / ADK | 把模型能力放入 Agent 开发框架 | 关注 Agent、Tool、Session、Runner |
| 本书 framework | 不实现 Transformer，只使用模型能力 | 重点实现 Agent Runtime、Context、Tool、Memory |

本书不会训练 Transformer。

但必须理解 Transformer 的输入输出特性，因为 Agent 的很多工程问题都来自这些特性。

## 5.5 业务场景案例：销售分析 Agent

假设用户问：

```text
分析最近一个季度利润下降的原因。
```

Agent 需要把这些信息放进 context：

- 用户目标
- 指标定义
- 可用工具
- 已查询的数据结果
- 安全和权限约束
- 输出格式要求

Transformer 可以在这些 token 之间建立关系，但不会自动知道哪些信息最重要。

如果 Agent 把无关日志、过长表格、重复上下文都塞进去，模型就可能关注错误信息。

所以 Transformer 的能力越强，Context Engineering 反而越重要。

## Python MVP

本章示例用纯 Python 实现一个极简 Self-Attention。

运行：

```bash
python chapters/chapter05/example.py
```

你会看到每个 token 对其他 token 的注意力权重。这个例子不是为了训练模型，而是让你直观看到：模型如何把一个 token 的表示变成“其他 token 的加权组合”。

## Summary

Transformer 让模型可以在上下文中计算 token 之间的关系，并通过并行训练扩展到大规模语言模型。

对 Agent 工程师来说，Transformer 的意义不是要自己训练模型，而是理解 LLM 的边界：模型只看当前 context，只输出 token 概率，需要 Agent Runtime 负责组织目标、工具、记忆和反馈。

## Notes

本章只解释 Transformer 与 Agent 工程相关的最小必要知识，不展开完整训练细节、多头注意力优化、位置编码变体或 MoE 架构。

## References

[1] Vaswani et al.  
Attention Is All You Need.  
https://arxiv.org/abs/1706.03762

[2] OpenAI.  
A Practical Guide to Building Agents.  
https://openai.com/business/guides-and-resources/a-practical-guide-to-building-ai-agents/

[3] Anthropic.  
Building Effective Agents.  
https://www.anthropic.com/engineering/building-effective-agents

以上 URL 已在 2026-07-31 验证可访问。
