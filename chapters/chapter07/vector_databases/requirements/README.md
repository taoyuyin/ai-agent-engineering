# Vector Database Dependencies

本目录按数据库拆分独立依赖，避免一次安装全部 Client 和本地 Embedded Engine。

| 文件 | 示例 |
| --- | --- |
| `chroma.txt` | `chroma_mvp.py` |
| `qdrant.txt` | `qdrant_mvp.py` |
| `weaviate.txt` | `weaviate_mvp.py` |
| `milvus.txt` | `milvus_mvp.py` |
| `pgvector.txt` | `pgvector_mvp.py` |
| `pinecone.txt` | `pinecone_mvp.py` |

使用方式：

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r chapters/chapter07/vector_databases/requirements/qdrant.txt
python chapters/chapter07/vector_databases/qdrant_mvp.py
```

不同示例还可能需要 Docker Service、Endpoint 或 API Key，具体配置以父目录 [README](../README.md) 为准。依赖文件使用兼容范围，升级 Client 时必须同时验证建表、写入、过滤、检索和删除。
