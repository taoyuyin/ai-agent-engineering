# RAG Runtime MVP

本模块实现零第三方依赖的 RAG 检索管道，用于看清 Chunk、Index、Retrieve、Context 和 Citation 的数据流。

## 实现内容

- `Document` 与带稳定 ID/Source 的 `Chunk`；
- 字符窗口切分和 Overlap 校验；
- 词项统计与 BM25 风格评分；
- `retrieve()` 返回 Top-K Chunk、组装 Context 和去重 Citation；
- 空索引和无命中有显式行为。

## 模型关系

该 MVP 不调用生成模型，只验证 Retrieval。接入 LLM 后，模型只能根据返回 Context 组织答案，Citation 仍来自 Chunk 元数据。

```bash
python chapters/chapter26/example.py
python -m unittest discover -s chapters/chapter26 -p "test_*.py"
```

生产升级包括语义 Embedding、Hybrid Retrieval、Rerank、ACL-first Filter 和 Groundedness Eval。正文见 [Chapter 26](../README.md)。
