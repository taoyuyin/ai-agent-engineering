# Chapter 7 Vector Database Python MVPs

本目录使用六种向量数据库实现同一个检索任务，帮助读者比较原生 Python API，而不是通过 LangChain 或 LlamaIndex 隐藏数据库差异。

## 统一场景

所有示例使用同一组指标文档，并执行：

```text
upsert documents
  ↓
query embedding
  ↓
tenant_id = acme
  +
doc_type = metric
  ↓
Top-2 vector search
  ↓
delete cross-tenant demo record
```

预期结果只包含当前租户的 `gmv` 和 `revenue`，不能返回 `other-tenant-gmv`。

`common.py` 提供固定 64 维的教学版 hashing embedding。它不调用网络，不代表真实语义质量，目的是让不同数据库收到完全相同的向量。

## 环境

- Python 3.10+：运行当前版本的六种数据库 SDK
- Python 3.8+：只运行 `example.py` 和 `common.py`
- Docker 与 Docker Compose：只在运行 Weaviate 和 pgvector 示例时需要
- Pinecone API Key：只在运行 Pinecone 示例时需要

建议在独立虚拟环境中按数据库安装依赖，不要一次安装全部 SDK：

```bash
python3 -m venv .venv
source .venv/bin/activate
```

先验证公共 embedding：

```bash
python chapters/chapter07/vector_databases/common.py
```

## 示例对照

| 数据库 | 数据库位置 | Python SDK | 主要 API | 外部服务 |
|---|---|---|---|---|
| Chroma | 本地持久化目录 | `chromadb` | `upsert` / `query` / `delete` | 不需要 |
| Qdrant | Python Local Mode | `qdrant-client` | `upsert` / `query_points` / `delete` | 不需要 |
| Milvus | Milvus Lite 本地文件 | `pymilvus` | `upsert` / `search` / `delete` | 不需要 |
| Weaviate | Docker 单节点 | `weaviate-client` | `insert/replace` / `near_vector` / `delete_by_id` | 本地 Docker |
| Pinecone | Serverless | `pinecone` | `upsert` / `query` / `delete` | Pinecone Cloud |
| pgvector | Docker PostgreSQL | `psycopg` + `pgvector` | SQL `INSERT` / `ORDER BY <=>` / `DELETE` | 本地 Docker |

## 1. Chroma

```bash
pip install -r chapters/chapter07/vector_databases/requirements/chroma.txt
python chapters/chapter07/vector_databases/chroma_mvp.py
```

默认数据目录：

```text
chapters/chapter07/vector_databases/.data/chroma
```

可以用 `CHROMA_PATH` 修改。

观察重点：

- `PersistentClient` 把数据保存在本地
- `collection.upsert` 同时写入 ID、document、metadata 和 embedding
- `where` 使用 Chroma metadata filter 语法
- Chroma 返回 cosine distance，示例转换为 `1 - distance`

## 2. Qdrant

```bash
pip install -r chapters/chapter07/vector_databases/requirements/qdrant.txt
python chapters/chapter07/vector_databases/qdrant_mvp.py
```

默认数据目录：

```text
chapters/chapter07/vector_databases/.data/qdrant
```

可以用 `QDRANT_PATH` 修改。

观察重点：

- `QdrantClient(path=...)` 使用 Local Mode
- collection 显式声明 vector size 和 distance
- 在导入数据前为 `tenant_id`、`doc_type` 创建 payload index
- filter 由 `must + FieldCondition` 组成
- `query_points` 返回相似度 score

生产环境切换为 Qdrant Server 或 Cloud 时，业务侧主要检索 API 可以保留，只需替换 client 连接参数。

## 3. Milvus Lite

```bash
pip install -r chapters/chapter07/vector_databases/requirements/milvus.txt
python chapters/chapter07/vector_databases/milvus_mvp.py
```

默认数据库文件：

```text
chapters/chapter07/vector_databases/.data/milvus.db
```

可以用 `MILVUS_URI` 修改。连接远程 Milvus 时还可以设置 `MILVUS_TOKEN`。

观察重点：

- 本地文件 URI 自动使用 Milvus Lite
- collection 显式设置 dimension、COSINE 和 Strong consistency
- dynamic fields 保存教学示例的业务 metadata
- `filter` 使用 Milvus 表达式
- 同一个 `MilvusClient` API 可以连接 Lite、Standalone、Distributed 或 Cloud

## 4. Weaviate

先启动数据库：

```bash
docker compose \
  -f chapters/chapter07/vector_databases/docker-compose.yml \
  up -d weaviate
```

安装并运行：

```bash
pip install -r chapters/chapter07/vector_databases/requirements/weaviate.txt
python chapters/chapter07/vector_databases/weaviate_mvp.py
```

停止服务：

```bash
docker compose \
  -f chapters/chapter07/vector_databases/docker-compose.yml \
  down
```

观察重点：

- collection 使用 `self_provided`，由应用传入向量
- schema 显式声明 metadata properties
- Python v4 Client 同时依赖 HTTP `8080` 和 gRPC `50051`
- 示例通过 `exists + insert/replace` 实现幂等写入
- `near_vector` 同时接收向量和 property filter

`docker-compose.yml` 为教学环境开启匿名访问，不能直接用于生产。

## 5. Pinecone

设置环境变量：

```bash
export PINECONE_API_KEY="your-api-key"
```

安装并运行：

```bash
pip install -r chapters/chapter07/vector_databases/requirements/pinecone.txt
python chapters/chapter07/vector_databases/pinecone_mvp.py
```

可选配置：

```bash
export PINECONE_INDEX="chapter07-metrics"
export PINECONE_CLOUD="aws"
export PINECONE_REGION="us-east-1"
```

观察重点：

- 示例创建 BYO-vector Serverless index
- namespace 与 metadata filter 是两个不同的隔离维度
- `upsert` 写入 values 和扁平 metadata
- Pinecone 是最终一致，示例在查询前有界轮询 index stats
- 示例只删除演示记录，不会自动删除整个 index

运行 Pinecone 示例会使用真实云资源，执行前应检查账户区域和计费规则。

## 6. pgvector

先启动 PostgreSQL：

```bash
docker compose \
  -f chapters/chapter07/vector_databases/docker-compose.yml \
  up -d postgres
```

安装并运行：

```bash
pip install -r chapters/chapter07/vector_databases/requirements/pgvector.txt
python chapters/chapter07/vector_databases/pgvector_mvp.py
```

默认连接字符串：

```text
postgresql://chapter07:chapter07@localhost:5432/chapter07
```

可以用 `PGVECTOR_DSN` 修改。

观察重点：

- `CREATE EXTENSION vector` 启用 pgvector
- `ON CONFLICT DO UPDATE` 实现 ACID upsert
- `(tenant_id, doc_type)` B-tree index 支持结构化过滤
- HNSW 使用 `vector_cosine_ops`
- `<=>` 返回 cosine distance，SQL 使用 `1 - distance` 计算 similarity
- 向量过滤和业务字段查询在同一条 SQL 中完成

示例中的用户名和密码只用于本地教学环境，不能用于生产。

## 验证层级

本目录提供三层验证：

1. `common.py` 可在无第三方依赖时运行，验证向量维度、归一化和确定性。
2. 所有 Python 文件都应通过 `py_compile`，验证 Python 3.8 语法。
3. 安装对应 SDK、启动所需服务后运行单个 MVP，验证数据库集成。

发布或升级依赖时，应分别执行六个集成示例。云服务示例还应在隔离的测试 index 和受控预算下运行。

## 从教学 MVP 到生产系统

本目录刻意没有加入真实 Embedding API、异步批处理和框架封装。生产实现还需要：

- 用真实模型替换 `common.embed`
- 批量写入、限流、重试和 dead-letter queue
- 文档版本、chunk lineage 和删除同步
- 租户、ACL、状态与时间过滤
- secret manager 和最小权限凭证
- 离线 Recall@K 与线上检索质量评估
- tracing、metrics、备份和恢复

先让数据库原生 API 的边界清晰，再引入 LangChain、LlamaIndex 或统一 Repository 接口。
