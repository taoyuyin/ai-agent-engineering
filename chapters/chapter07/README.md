# Chapter 7 Embedding 与向量数据库

Part II LLM Foundations —— Agent 为什么能够工作

Version: 2026-07

Last Updated: 2026-07-31

## Core Question

为什么向量可以表达语义？向量数据库又解决了普通数组、关系数据库和关键词搜索无法高效解决的什么问题？

## Chapter Conclusion

Embedding 把文本、文档、问题、指标和工具描述映射到连续向量空间，使“语义相似”成为可以计算的问题。

向量数据库则把一次向量相似度计算扩展成可用于生产系统的数据基础设施，负责：

- 向量和业务元数据的持久化
- 大规模近似最近邻检索
- 租户、权限、时间和业务条件过滤
- 索引构建、增量写入、删除和数据更新
- 副本、分片、备份、监控和容量扩展

对 Agent 工程而言，Embedding 是 RAG、Memory Retrieval、Tool Selection 和知识路由的基础；向量数据库是承载这些能力的检索系统，但它既不等于知识库，也不自动保证回答正确。

## Learning Objectives

完成本章后，你应该能够：

- 解释 Embedding、向量空间和余弦相似度
- 区分精确检索与近似最近邻检索
- 理解 FLAT、HNSW、IVF、PQ 和磁盘索引的核心取舍
- 设计包含写入链路和查询链路的向量检索架构
- 从部署、索引、过滤、一致性、扩展、运维和成本等维度选择向量数据库
- 使用 Chroma、Qdrant、Milvus、Weaviate、Pinecone 和 pgvector 的 Python API 完成最小检索闭环
- 识别企业 RAG 中容易被忽略的权限、版本和评估问题

## 7.1 原理剖析：从离散文本到连续空间

文本本身是离散符号。

```text
"销售额"
"收入"
"revenue"
```

字符串匹配只知道字符是否相同，无法直接判断这几个词在具体业务中是否表达相近含义。

Embedding 模型把输入映射成固定维度向量：

```text
embedding("销售额") → [0.21, 0.72, ..., -0.08]
embedding("收入")   → [0.20, 0.69, ..., -0.05]
```

在经过训练的向量空间中，语义或使用上下文相近的输入通常距离更近。于是，原本难以计算的语义问题，被转换成了数值计算问题。

需要特别注意：向量不是词典定义，也不是事实数据库。向量空间表达的是模型从训练数据中学习到的统计关系。同一段文本使用不同 Embedding 模型会得到不同维度、不同数值、不同检索效果。

因此，一个 collection 或 index 中的文档向量与查询向量必须来自兼容的 Embedding 模型和版本。

## 7.2 相似度：距离函数必须与模型和索引一致

常见相似度或距离函数包括：

| 度量 | 直觉 | 常见使用方式 |
|---|---|---|
| Cosine Similarity | 比较方向，弱化向量长度 | 文本语义检索最常见 |
| Dot Product / Inner Product | 同时受方向和长度影响 | 模型训练目标与点积一致时使用 |
| Euclidean / L2 Distance | 比较空间中的直线距离 | 图像、推荐或已按 L2 训练的向量 |

余弦相似度定义为：

```text
cosine(a, b) = dot(a, b) / (|a| × |b|)
```

值越接近 `1`，两个向量方向越接近。

如果向量已经做过 L2 归一化，余弦相似度和点积排序通常等价。但在工程中不能因为“通常等价”就随意切换：

- 写入和查询必须使用同一度量
- 数据库返回的可能是 similarity，也可能是 distance
- similarity 越大越相关，distance 通常越小越相关
- 阈值不能跨模型、跨度量直接复用

一个常见线上错误，是把数据库返回的 cosine distance 当作 cosine similarity，再用相反方向的阈值过滤。

## 7.3 为什么普通数组不够：精确检索与 ANN

如果有 `N` 个 `D` 维向量，最直接的检索方式是计算查询向量与所有向量的距离，再排序取 Top-K。

这种 FLAT 或 brute-force 检索的特点是：

- 优点：在指定距离函数下结果精确
- 缺点：计算量随向量数量线性增长

在几百或几千条数据的教学 Demo 中，Python 列表足够。在百万、千万甚至更大规模的数据上，每次扫描全部向量会造成明显的延迟和计算成本。

向量数据库通常使用 ANN（Approximate Nearest Neighbor，近似最近邻）索引，以少量召回损失换取更低延迟和更高吞吐。

### 常见索引家族

| 索引 | 核心思想 | 优点 | 缺点 | 适用场景 |
|---|---|---|---|---|
| FLAT | 扫描全部向量 | 精确、无需训练索引 | 数据量大时慢 | 小数据、离线评估、召回基线 |
| HNSW | 构建多层近邻图并逐层导航 | 高召回、低延迟、增量查询体验好 | 内存和构建成本较高 | 在线 RAG、Memory、低延迟检索 |
| IVF | 先把向量分桶，只搜索部分桶 | 可控制速度与召回，适合批量数据 | 需要训练和调参，增量数据分布变化需关注 | 大规模、数据相对稳定 |
| PQ / SQ | 对向量或索引进行量化压缩 | 显著降低内存和存储 | 可能降低召回，需要重排或精确向量兜底 | 内存受限、超大规模 |
| DiskANN 类 | 让主要索引驻留 SSD，配合缓存搜索 | 降低纯内存成本 | 对磁盘、缓存和参数更敏感 | 大规模、成本敏感型部署 |

没有“永远最快”的索引。索引选择取决于：

- 数据规模和维度
- 写入频率
- 查询并发与 P99 延迟目标
- 过滤条件的选择性
- 可接受的召回损失
- 内存、SSD 和网络预算

## 7.4 从 Vector Index 到 Vector Database

向量索引只解决“如何找到近邻”。生产系统还需要数据库能力。

一个最小记录通常包含：

```json
{
  "id": "metric-gmv-v3",
  "vector": [0.12, -0.08, 0.31],
  "text": "GMV 是指定统计周期内的成交总额……",
  "metadata": {
    "tenant_id": "acme",
    "doc_type": "metric_definition",
    "version": 3,
    "status": "published",
    "acl": ["finance", "management"],
    "updated_at": "2026-07-31T08:00:00Z"
  }
}
```

向量数据库至少应回答以下工程问题：

1. 如何保证 ID 幂等写入，而不是重复生成 chunk？
2. 文档更新后，旧向量如何失效或删除？
3. 查询时能否先限制租户和权限，再执行向量检索？
4. 新写入数据多久可以被检索到？
5. 索引重建期间是否继续服务？
6. 单节点故障后数据如何恢复？
7. 如何监控查询延迟、过滤命中率、召回率和索引大小？

这就是向量库与一个内存数组的边界。

## 7.5 架构设计：写入链路与查询链路必须分开

### 写入链路

```text
Data Source
  ↓
Parse / Clean
  ↓
Chunk
  ↓
Attach Metadata / ACL / Version
  ↓
Embedding Model
  ↓
Validate Dimension / Normalize
  ↓
Upsert Vector Database
  ↓
Index / Replicate / Observe
```

### 查询链路

```text
User Query
  ↓
Query Rewrite
  ↓
Embedding Model
  ↓
Tenant + ACL + Business Filters
  ↓
Vector / Hybrid Search
  ↓
Top-K Candidates
  ↓
Rerank
  ↓
Context Assembly
  ↓
Agent / LLM
```

这里有三个关键边界：

- Embedding 负责表示，不负责事实正确性
- Vector Database 负责召回候选，不负责最终回答
- Reranker 与 LLM 负责进一步判断，但仍需引用、权限和评估约束

## 7.6 Metadata Filter 不是附加功能

企业检索很少是“在全部文档里找最相似内容”。真实查询通常带有：

- `tenant_id = 当前租户`
- `department in 用户可访问部门`
- `status = published`
- `effective_at <= 当前时间`
- `region = CN`
- `document_type = policy`

如果先做全库向量搜索，再在应用层过滤，会出现两个问题：

1. 召回的 Top-K 可能全部无权限，过滤后没有结果。
2. 无权限数据已经进入检索链路，增加泄露风险。

正确方向是让租户、权限和业务过滤尽可能进入数据库查询，并为高频过滤字段建立合适的标量或 payload 索引。

注意：不同数据库对过滤与 ANN 的结合方式不同。过滤可能发生在向量搜索之前、搜索过程中或候选集之后，这会直接影响性能和召回率。因此，选型测试必须使用真实过滤分布，不能只测无过滤查询。

## 7.7 常用向量数据库横向对比

下面选取六种具有代表性的方案。它们分别代表嵌入式开发体验、专用向量引擎、分布式大规模系统、检索平台、全托管服务和关系数据库扩展。

> 表格描述的是 2026-07 官方产品能力与典型工程定位，不是厂商性能排名。真实性能必须用自己的向量、过滤条件和并发模型进行基准测试。

| 产品 | 部署形态 | 索引与检索 | Metadata / Hybrid | 一致性与事务 | 扩展与运维 | 主要优点 | 主要缺点 |
|---|---|---|---|---|---|---|---|
| Chroma | 本地嵌入、Client/Server、Cloud | Single Node 使用 HNSW，Distributed/Cloud 使用 SPANN；支持 dense、sparse、hybrid | Metadata、全文与正则过滤 | API 简洁，事务能力取决于具体部署形态 | 适合从本地原型平滑进入服务化 | 上手成本低，文档/embedding/metadata 抽象直接，适合 Agent 原型 | 大规模生产选型仍需验证部署、隔离、备份和性能边界 |
| Qdrant | Local Mode、单机、分布式、Cloud | Dense 使用 HNSW；支持 sparse、quantization、ACORN | Payload 类型和过滤能力强，支持混合检索 | 支持分布式副本与写入顺序配置 | 自托管可控，Cloud 降低运维 | Filterable HNSW、API 清晰、Rust 引擎、过滤场景友好 | Dense 索引路线以 HNSW 为主；自建集群仍需容量、分片和恢复治理 |
| Milvus | Lite、Standalone、Distributed、Zilliz Cloud | FLAT、HNSW、IVF、SCANN、DiskANN 及量化变体 | 标量过滤、dense/sparse、多向量和 hybrid search | Strong、Bounded、Session、Eventually 多级一致性 | 计算存储分离，组件可独立扩展 | 索引选择丰富，面向超大规模和高吞吐，Lite 到集群 API 基本一致 | 分布式部署组件多，资源规划、索引参数和运维复杂度较高 |
| Weaviate | Embedded、Docker/Kubernetes、Cloud | Vector search、named/multi vectors、hybrid BM25F | Schema、filter、hybrid、模块化 vectorizer/reranker/generative | 提供复制、多租户和集群能力 | 数据库与模型集成较完整 | 一体化检索体验强，多模态和模块生态丰富 | 配置面较大；Python v4 API 和数据库版本兼容性需要管理 |
| Pinecone | 全托管 Serverless | Dense、Sparse、Full-text/Hybrid；底层算法由服务管理 | Namespace、metadata filter、集成 embedding | 最终一致，新写入可见存在短暂延迟 | 自动扩展，无需管理集群和索引参数 | 运维负担低，适合快速构建托管型生产检索 | 商业服务成本与供应商绑定；底层索引控制和本地离线能力较少 |
| pgvector | PostgreSQL 扩展，本地/自建/托管 PostgreSQL | Exact、HNSW、IVFFlat；支持 dense、half、binary、sparse | 原生 SQL、WHERE、JOIN、全文检索组合 | 继承 PostgreSQL ACID、WAL、备份、复制 | 复用现有 PostgreSQL 运维体系 | 结构化数据与向量同库，事务和权限模型成熟，系统组件少 | 超大规模专用向量负载需要精细调优；ANN、过滤、VACUUM 和容量竞争需压测 |

### Chroma

适合：

- 教学、Notebook、单机 Agent 和中小型知识库
- 希望直接用 collection 管理文档、metadata 和 embedding
- 团队需要最快建立可运行检索闭环

优势是开发体验和本地启动成本低。需要警惕的是，不应把本地原型的体验直接等同于企业生产能力；上线前仍要验证鉴权、租户隔离、备份恢复、并发写入和容量上限。

### Qdrant

适合：

- Metadata filter 很重要的 RAG、推荐和多租户检索
- 需要自托管，同时希望 API 和运维模型相对直接
- 以 HNSW 在线检索为主，关注低延迟和 payload 条件

Qdrant 的 filterable HNSW 会把 payload 索引与图检索结合。高频过滤字段应在导入向量前建立 payload index，否则可能需要重建 HNSW 才能获得完整优化收益。

### Milvus

适合：

- 千万、亿级及更高规模的向量检索
- 需要多种索引、量化和一致性级别
- 有 Kubernetes、对象存储和分布式系统运维能力

Milvus Lite 适合开发机 MVP，Standalone 适合单机服务，Distributed 面向大规模生产。它们提供相近的客户端 API，但生产拓扑、故障模型和成本完全不同。

### Weaviate

适合：

- 需要 vector search、BM25F、hybrid search、reranker 和模型模块的一体化检索平台
- 需要 named vectors、多模态或多租户能力
- 希望数据库可以管理 vectorizer 集成，也允许自带向量

其能力覆盖面较广，意味着版本兼容和配置治理也更重要。Python v4 Client 通过 gRPC 执行主要操作，本地部署时必须同时暴露 HTTP 和 gRPC 端口。

### Pinecone

适合：

- 团队不希望管理向量数据库集群
- 业务流量变化大，希望使用 Serverless 和自动扩展
- 可以接受托管服务、网络依赖和商业成本

Pinecone 的 Serverless 架构把存储与查询计算分离，并隐藏索引算法和集群参数。换来的代价是更少的底层控制、更明显的供应商绑定，以及需要把最终一致性纳入写后读流程。

### pgvector

适合：

- 已经使用 PostgreSQL，向量规模和 QPS 仍在数据库可承载范围
- 需要把向量检索与订单、用户、权限或知识元数据做 SQL JOIN
- 强调事务一致性、备份恢复和现有 DBA 体系

pgvector 经常是企业项目的合理起点，因为它减少一个新基础设施组件。但“减少组件”不等于“无需设计”：HNSW/IVFFlat、过滤列索引、连接池、表膨胀、VACUUM、读写副本和查询计划都需要压测。

## 7.8 如何做技术选型

不要先问“哪个向量数据库最好”，先把约束写成决策表。

| 决策维度 | 必须收集的问题 |
|---|---|
| 数据 | 向量数量、维度、精度、每天增量、删除和更新比例 |
| 查询 | 平均/P95/P99 QPS、Top-K、过滤条件、hybrid、rerank |
| 质量 | Recall@K、nDCG、无答案率、权限过滤后召回 |
| 隔离 | 租户数量、每租户规模、namespace/partition/row filter |
| 一致性 | 是否要求写后立即可读，是否允许短暂旧数据 |
| 可用性 | RPO、RTO、副本、跨可用区、备份和恢复演练 |
| 团队 | PostgreSQL、Kubernetes、云服务和搜索系统运维能力 |
| 成本 | 存储、内存、查询、写入、网络、备份和人力成本 |
| 合规 | 数据地域、加密、审计、删除证明、供应商准入 |

一个实用的初始判断是：

```text
本地学习 / 快速原型
  → Chroma / Qdrant Local / Milvus Lite

已有 PostgreSQL，规模中等且结构化关联很多
  → pgvector

过滤复杂、需要专用向量引擎并可自托管
  → Qdrant

超大规模、多索引策略、团队具备分布式运维能力
  → Milvus

希望获得检索与模型模块的一体化平台
  → Weaviate

希望完全托管、减少基础设施运维
  → Pinecone 或各产品 Cloud
```

这只是候选集缩小方法，不是最终结论。

## 7.9 基准测试：不要只测平均延迟

向量数据库 Benchmark 至少要固定：

- 相同 Embedding 模型、维度和归一化方式
- 相同数据集与 ground truth
- 相同 Top-K
- 相同过滤条件分布
- 相同写入和删除压力
- 相同硬件或等价云成本
- 相同副本和持久化要求

核心指标包括：

```text
Recall@K
P50 / P95 / P99 latency
Queries Per Second
Index build time
Write-to-search visibility delay
Memory / Disk usage
Cost per million queries
Recovery time
```

如果只比较 QPS 而不比较 Recall@K，数据库可以通过减少搜索范围获得看似更快的结果；如果只测无过滤检索，则无法代表企业权限和租户场景。

## 7.10 业务场景：企业指标问答

用户问：

```text
GMV 和销售额有什么区别？
```

系统需要从指标知识库中召回：

- GMV 定义
- 销售额定义
- 退款、取消和税费口径
- 生效版本和适用报表
- 指标负责人

关键词匹配可能漏掉“成交总额”“支付金额”等同义表达。Embedding 能提高语义召回，但数据库查询还应同时限制：

```text
tenant_id = 当前企业
status = published
effective_at <= 当前时间
user_department in acl
```

检索到文档后，Semantic Layer 仍需确认指标口径。Agent 最终答案应返回引用和版本，而不是只给出模型生成的结论。

## 7.11 Python MVP：六种数据库实现同一检索协议

本章保留了一个不依赖第三方库的内存检索示例：

```bash
python chapters/chapter07/example.py
```

向量数据库示例位于：

```text
chapters/chapter07/vector_databases/
├── README.md
├── common.py
├── chroma_mvp.py
├── qdrant_mvp.py
├── milvus_mvp.py
├── weaviate_mvp.py
├── pinecone_mvp.py
├── pgvector_mvp.py
├── docker-compose.yml
└── requirements/
```

所有示例实现相同闭环：

```text
prepare documents
  → embed
  → upsert
  → tenant + doc_type filter
  → vector search
  → print result
  → delete demo record
```

为了让数据库 API 差异成为关注重点，示例使用 `common.py` 中确定性的教学版 embedding，不下载外部模型，也不需要模型 API Key。生产系统必须替换成经过评估的 Embedding 模型。

各示例安装和运行方式见 [vector_databases/README.md](./vector_databases/README.md)。

## 7.12 生产检查清单

在向量数据库上线前，至少确认：

- 文档和查询使用同一 Embedding 模型、版本和维度
- 每条记录具有稳定 ID、租户、版本、状态和权限元数据
- upsert、更新、删除和失败重试是幂等的
- 权限过滤在数据库查询阶段执行
- 高频过滤字段已有合适索引
- 写后读可见性符合业务要求
- 使用真实过滤分布评估 Recall@K 和 P99
- 有离线基准、线上反馈和回归数据集
- 有备份、恢复和重建索引演练
- 监控空召回、低分召回、延迟、索引大小和成本
- 原始文档仍保存在可审计的 Source of Truth 中

## Summary

Embedding 把语义关系映射到向量空间；向量索引让相似度检索在大规模数据上可用；向量数据库则补齐数据管理、过滤、扩展和可靠性能力。

对 Agent 工程师来说，真正重要的不是记住某个数据库的 API，而是理解以下边界：

- 相似不等于事实正确
- Top-K 不等于高召回
- Metadata filter 关系到性能，也关系到安全
- ANN 的速度必须与 Recall 一起衡量
- 数据库选型必须结合规模、过滤、一致性、团队能力和总成本

## Notes

本章对比基于各产品在 2026-07-31 的官方文档。向量数据库演进很快，API、部署形态和商业能力可能变化，升级依赖前应重新检查官方文档和 release notes。

对比表用于建立技术选型维度，不构成性能排名。厂商公开 Benchmark 只能作为线索，最终结论必须来自相同数据、硬件、召回目标和过滤负载下的可复现实验。

本章 MVP 使用确定性哈希向量演示数据库 API，不具备真实语义模型的检索质量。

## References

[1] OpenAI.

Embeddings Guide.

https://platform.openai.com/docs/guides/embeddings

[2] Chroma.

Introduction; Adding Data; Query and Get.

https://docs.trychroma.com/docs/overview/introduction

https://docs.trychroma.com/docs/collections/add-data

https://docs.trychroma.com/docs/querying-collections/query-and-get

[3] Qdrant.

Quickstart; Indexing; Distributed Deployment.

https://qdrant.tech/documentation/quick-start/

https://qdrant.tech/documentation/manage-data/indexing/

https://qdrant.tech/documentation/scaling/distributed_deployment/

[4] Milvus.

Milvus Lite; Overview; Consistency; Architecture.

https://milvus.io/docs/milvus_lite.md

https://milvus.io/docs/overview.md

https://milvus.io/docs/consistency.md

https://milvus.io/docs/architecture_overview.md

[5] Weaviate.

Python Client; Vector Search; Docker Installation.

https://docs.weaviate.io/weaviate/client-libraries/python

https://docs.weaviate.io/weaviate/concepts/search/vector-search

https://docs.weaviate.io/deploy/installation-guides/docker-installation

[6] Pinecone.

Quickstart; Data Modeling; Architecture.

https://docs.pinecone.io/guides/get-started/quickstart

https://docs.pinecone.io/guides/index-data/data-modeling

https://www.pinecone.io/how-pinecone-works/

[7] pgvector.

pgvector; pgvector-python.

https://github.com/pgvector/pgvector

https://github.com/pgvector/pgvector-python

以上 URL 已在 2026-07-31 验证可访问。
