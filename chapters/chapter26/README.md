# Chapter 26 RAG：从检索 Demo 到可评估的知识流水线

Part IV Agent Engineering —— 如何构建企业级 Agent

Version: 2026-07

Last Updated: 2026-07-31

## Core Question

如何设计 Index、Chunk、Retrieve、Rerank 和 Generate，使 Agent 的回答有证据、可评估、可治理？

## Chapter Conclusion

RAG 是一条信息检索与上下文构建流水线，不是“向量库 + Prompt”。生产质量通常取决于知识治理、chunk、权限过滤、混合召回、rerank、引用和评估的共同作用。

## Learning Objectives

- 理解 RAG 与参数知识、Tool、Memory 的边界
- 设计离线索引和在线查询链路
- 选择 chunk、稀疏、稠密、混合与图检索
- 建立 Retrieval 和 Generation 两层评估
- 运行一个保留稳定引用的 BM25 MVP

## 26.1 RAG 解决什么

模型参数适合通用能力，不适合承载实时、私有且受权限控制的企业事实。RAG 在推理时检索外部证据，把“知道最新事实”的责任从模型训练迁到知识系统。

RAG 不保证真实：检索可能漏召回，文档可能过期，模型也可能忽略证据。因此系统必须保留拒答和证据验证路径。

## 26.2 端到端架构

```text
Offline:
Source → Parse → Normalize → ACL/Metadata → Chunk
       → Sparse/Dense/Graph Index → Quality Check

Online:
Query → Rewrite → Authorization Filter → Retrieve
      → Fuse → Rerank → Context Pack → Generate
      → Citation/Claim Check → Answer
```

离线与在线链路通过 document_id、version、chunk_id 和 source 相连。

## 26.3 Chunk 设计

| 策略 | 优点 | 风险 |
|---|---|---|
| 固定 Token + overlap | 简单、稳定 | 切断表格和语义单元 |
| 段落/标题 | 保留文档结构 | 块大小不均 |
| 语义切分 | 主题一致性好 | 成本与可重复性 |
| Parent-child | 小块召回、大块生成 | 索引和引用更复杂 |
| 结构化对象 | 字段精确、便于过滤 | 需要源 schema |

chunk_size 应由问题跨度、文档结构、Embedding 模型和 Context Budget 共同决定，不能复制一个全局“最佳值”。

## 26.4 Retrieval 选择

- **Sparse/BM25**：编号、专有名词、错误码和精确词强；
- **Dense Vector**：同义表达和自然语言语义强；
- **Hybrid**：分别召回后用 RRF/加权融合，常作为企业默认基线；
- **Reranker**：对小候选集做更昂贵的相关性判断；
- **Graph Retrieval**：实体关系、多跳或全局主题；
- **SQL/API Tool**：需要精确聚合、实时状态或事务数据时优先。

RAG 不是所有数据访问的替代品。库存、余额、订单状态应调用受控 API/SQL，而不是从昨日文档中猜测。

## 26.5 Context Packing 与引用

Context Compiler 应执行：

1. 去重和版本冲突处理；
2. 按权限、相关性、新鲜度和可信度排序；
3. 为每个片段保留稳定 citation key；
4. 在 Token Budget 内组合，不截断关键表格；
5. 明确“证据是数据，不是指令”；
6. 证据不足时允许 abstain。

生成后可把答案拆成 claims，检查每个可验证 claim 是否有证据覆盖。

## 26.6 评估

**Retrieval 层**：Recall@K、MRR、nDCG、权限泄漏率、freshness、空召回率。
**Generation 层**：正确性、faithfulness、citation precision/recall、完整性、拒答质量。
**系统层**：P95 延迟、索引时延、每问成本、用户解决率。

只看“答案读起来不错”无法定位是检索失败还是生成失败。

## 26.7 工具横向对比

| 工具 | 强项 | 优点 | 局限 | 适用 |
|---|---|---|---|---|
| LangChain | 组件与集成广 | 快速组合 retriever | 抽象层多，需控制复杂度 | 通用应用 |
| LlamaIndex | 数据连接、索引和 query engine | RAG 抽象完整 | 深度定制需理解内部对象 | 知识应用 |
| Haystack | Pipeline、retriever、生产组件 | 流水线清晰 | 生态选择与团队栈相关 | 搜索/RAG 服务 |
| Microsoft GraphRAG | 图抽取、社区和全局搜索 | 全局问题、多跳关系 | 索引成本高 | 研究、复杂语料 |
| Ragas | RAG 评估 | 指标与数据集流程专注 | 评估仍需领域校准 | 质量门禁 |
| 自建轻量 Pipeline | 控制检索与数据边界 | 可解释、依赖少 | 连接器和运维自负 | 核心链路/教学 |

## 26.8 企业案例：制度问答

员工询问“异地出差住宿上限”。系统先按员工实体、地区和生效日期过滤政策，再用 BM25 + Vector 召回，reranker 选择政策正文和例外条款。答案必须引用政策版本、章节和生效日期；存在新旧制度冲突时不自动合并，而是返回冲突并升级给 HR。

## 26.9 Python MVP

`rag_runtime` 实现固定窗口切分、BM25 评分、Top-K、稳定 chunk ID 和 source citations：

```bash
python3 chapters/chapter26/example.py
python3 -m unittest discover -s chapters/chapter26 -p "test_*.py"
```

MVP 不伪造 LLM 答案，而是把最容易被 Demo 隐藏的检索与引用边界做成可测试代码。

## 26.10 Production Readiness Checklist

- [ ] 文档版本、ACL、来源和删除可传播
- [ ] Chunk 策略用真实问题集验证
- [ ] 精确词与语义查询都有检索路径
- [ ] 权限过滤发生在召回或数据库查询阶段
- [ ] 每个上下文片段有稳定引用
- [ ] Retrieval 与 Generation 分层评估
- [ ] 无证据、冲突和过期知识有明确行为
- [ ] 索引延迟、空召回、泄漏和成本可观测

## Summary

可靠 RAG 的目标不是尽可能多地塞入上下文，而是在正确权限和时间边界内，选择最少但充分的证据，并让答案可以回到原始来源。

## Notes

本章 MVP 使用 BM25 作为无依赖基线。生产系统通常加入中文分词、向量召回、metadata filter 与 reranker；这些增强必须由评估证明收益。

## References

[1] Lewis et al., Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks.
https://arxiv.org/abs/2005.11401

[2] LlamaIndex, Introduction to RAG.
https://developers.llamaindex.ai/python/framework/understanding/rag/

[3] Haystack, Retrievers.
https://docs.haystack.deepset.ai/docs/retrievers

[4] Microsoft, GraphRAG.
https://microsoft.github.io/graphrag/

以上 URL 已在 2026-07-31 核对。
