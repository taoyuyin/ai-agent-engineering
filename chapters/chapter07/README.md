# Chapter 7 Embedding

Part II LLM Foundations —— Agent 为什么能够工作

Version: 2026-07

Last Updated: 2026-07-31

## Core Question

为什么向量可以表达语义？Embedding 在 Agent 中到底用在哪里？

## Chapter Conclusion

Embedding 把文本、文档、问题、指标和工具描述映射到向量空间，使“语义相似”可以被计算。

对 Agent 工程而言，Embedding 是 RAG、Memory Retrieval、Tool Selection 和知识路由的重要基础。

## Learning Objectives

完成本章后，你应该能够理解：

- Embedding 的基本直觉
- 余弦相似度如何衡量语义接近
- Embedding 如何支持检索
- Agent Memory 为什么需要 Retrieval
- Embedding 的局限性和治理要求

## 7.1 原理剖析：从离散文本到连续空间

文本本身是离散符号。

```text
"销售额"
"收入"
"revenue"
```

对业务人员来说，它们可能表达相近含义。但字符串匹配很难直接知道这一点。

Embedding 的作用，是把这些文本映射成向量：

```text
"销售额" → [0.21, 0.72, ...]
"收入"   → [0.20, 0.69, ...]
```

如果两个文本语义相近，它们在向量空间中的方向通常也更接近。

这让语义检索成为可能。

## 7.2 相似度：为什么常用 cosine

在向量空间中，我们通常不只关心向量长度，而更关心方向。

Cosine Similarity 衡量两个向量夹角：

```text
cosine(a, b) = dot(a, b) / (|a| * |b|)
```

值越接近 1，方向越相似。

在 Agent 中，这常用于：

- 找最相关文档
- 找最相关记忆
- 找最合适工具
- 找相似历史任务

## 7.3 架构设计：Embedding Retrieval

一个最小检索架构：

```text
Documents
  ↓
Chunk
  ↓
Embed
  ↓
Vector Store
  ↓
User Query
  ↓
Query Embedding
  ↓
Top-K Retrieval
  ↓
Agent Context
```

注意，Embedding 不直接回答问题。

它只负责找相关内容。最终答案仍需要 LLM 结合上下文生成。

## 7.4 工具横向对比

| 工具 / 框架 | Embedding 相关能力 | 适用场景 |
|---|---|---|
| OpenAI Embeddings | 通用文本向量 | 文档检索、分类、聚类 |
| LlamaIndex | Index / Retriever 抽象成熟 | RAG 和知识库 |
| LangChain / LangGraph | Retriever 可接入 Agent 流程 | 多步 Agent 检索 |
| 向量数据库 | 存储和召回 embedding | 大规模知识库 |
| 本书 framework | 先实现内存向量检索 | 理解原理和接口边界 |

## 7.5 业务场景案例：企业指标问答

用户问：

```text
GMV 和销售额有什么区别？
```

系统需要从指标字典中找：

- GMV 定义
- 销售额定义
- 口径差异
- 适用报表
- 负责人

关键词匹配可能漏掉“成交总额”“支付金额”等同义表达。

Embedding 检索可以提高召回能力，但仍需要 Semantic Layer 确认指标口径。

## Python MVP

本章示例实现一个极简 embedding 检索器。

为了不依赖外部模型，示例使用词袋向量模拟 embedding。真实系统应替换为模型 embedding。

运行：

```bash
python chapters/chapter07/example.py
```

## Summary

Embedding 让语义相似性可计算，是 RAG、Memory、Tool Selection 和企业知识检索的基础。

但 Embedding 不是业务语义真相。企业场景中仍然需要指标定义、权限、数据质量和人工治理。

## Notes

本章示例只展示向量检索接口和 cosine similarity。真实项目应使用可靠 embedding 模型和向量数据库。

## References

[1] OpenAI.  
Embeddings Guide.  
https://platform.openai.com/docs/guides/embeddings

[2] LlamaIndex.  
Documentation.  
https://docs.llamaindex.ai/

以上 URL 已在 2026-07-31 验证可访问。
