# Knowledge Runtime MVP

本模块实现带治理元数据的 Knowledge Catalog，展示知识工程发生在 RAG 检索之前。

## 实现内容

- `KnowledgeAsset`：Tenant、Domain、Source、Owner、有效期、Tag 和连续版本；
- 发布时验证来源、Owner、有效期和不可变版本；
- `current()` 按查询日期选择有效版本；
- `search()` 先做 Tenant/Domain 隔离，再用词项重合排序；
- 返回完整 Asset，保留 Provenance。

## 模型关系

模型可用于 Query Understanding 和答案生成；知识有效性、版本和租户过滤由 Catalog 决定，不能交给 Prompt。

```bash
python chapters/chapter25/example.py
python -m unittest discover -s chapters/chapter25 -p "test_*.py"
```

生产系统应加入 Ingestion Workflow、ACL、删除传播、质量评分和索引版本。正文见 [Chapter 25](../README.md)。
