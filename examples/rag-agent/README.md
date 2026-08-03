# RAG Agent

当前状态：**设计契约，尚无本目录可运行工程**。检索管道见 [Chapter 26](../../chapters/chapter26/README.md)，企业 ACL 问答见 [Chapter 46](../../chapters/chapter46/README.md)。

## 业务目标

面向企业制度和技术文档回答问题，答案必须使用调用者有权查看、当前有效的知识，并返回可定位 Citation；证据不足或冲突时拒答、澄清或转人工。

## 端到端流程

```text
Question + Identity
  → Query Rewrite / Domain Routing
  → ACL-first Candidate Filter
  → Hybrid Retrieval / Rerank
  → Context Budget + Injection Isolation
  → Grounded Generation
  → Citation / Entailment Check
  → Answer or Abstain
  → Feedback + Trace
```

## 模型与确定性边界

模型可改写问题、排序候选和组织答案；服务端必须先按 Tenant/ACL/有效期过滤，再进行向量或关键词检索。Citation 由 Chunk 元数据产生，模型不能编造 URL 或文档版本。

## 目标工程结构

```text
rag-agent/
├── README.md
├── requirements.txt
├── rag_agent/
│   ├── ingestion.py
│   ├── retrieval.py
│   ├── reranker.py
│   ├── context.py
│   ├── answer.py
│   └── api.py
├── data/
├── tests/
├── evaluation/
└── Dockerfile
```

## 最小验收

- 同一问题对不同身份只检索各自有权内容；
- 文档版本和有效期进入检索与 Citation；
- Prompt Injection 文本保持为不可信 Context；
- 每个事实可映射到稳定 Chunk/Source；
- 无证据、冲突证据和过期证据有明确策略；
- 评测覆盖 Retrieval、Groundedness、Citation 和 Leakage。

## 生产升级

引入异步 Ingestion、解析/OCR、混合检索、Reranker、索引版本、删除传播、缓存与在线反馈。Embedding 模型升级必须构建新索引并支持灰度切换。
