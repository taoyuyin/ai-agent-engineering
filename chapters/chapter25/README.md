# Chapter 25 Knowledge Engineering：让企业知识可治理、可检索、可追溯

Part IV Agent Engineering —— 如何构建企业级 Agent

Version: 2026-07

Last Updated: 2026-07-31

## Core Question

如何把分散文档、结构化数据、规则和专家经验，转化为 Agent 能安全使用的知识系统？

## Chapter Conclusion

Knowledge Engineering 不等于“把文档塞进向量数据库”。它管理知识的语义、来源、权限、时效、质量和生命周期；RAG 只是知识消费方式之一。

## Learning Objectives

- 区分 data、information、knowledge 与 context
- 设计知识资产模型、目录、来源和有效期
- 对比文档、搜索、图谱与混合知识架构
- 建立采集、审核、发布、更新和退役流程
- 运行一个带版本、来源和租户隔离的知识目录

## 25.1 知识系统的真实问题

企业知识通常存在于制度 PDF、Wiki、工单、数据库、API 和员工经验中。难点不是存储，而是：

- 同一政策存在多个版本，哪个时间点有效；
- 文档内容正确，但当前用户没有权限；
- 相同术语在财务、销售和制造领域含义不同；
- 来源已失效，索引却仍返回旧 chunk；
- 生成结果无法追溯到 owner 和原始证据。

如果这些问题未解决，更强的检索只会更快地返回错误知识。

## 25.2 知识资产模型

一个可治理知识资产至少包含：

```text
identity: asset_id, version, type
meaning: title, content, entities, relations, glossary
governance: tenant, domain, owner, classification, ACL
provenance: source URI, producer, transform pipeline
time: valid_from, valid_to, indexed_at, reviewed_at
quality: status, confidence, freshness SLA
```

文档 ID、chunk ID 和向量 ID 应能反向关联原始资产。Embedding 是派生索引，不是事实来源。

## 25.3 三层架构

```text
Source Layer
Documents · Databases · APIs · Events · Expert Input
        ↓
Knowledge Control Plane
Catalog · Ontology · Version · ACL · Quality · Lineage
        ↓
Serving Layer
Keyword Search · Vector Search · Graph Query · SQL · RAG
```

Control Plane 决定“什么知识在何时对谁有效”，Serving Layer 决定“如何低延迟找到它”。

## 25.4 知识组织方式

| 方式 | 擅长 | 局限 |
|---|---|---|
| 文档/对象存储 | 保存原文与附件 | 语义查询弱 |
| 关键词倒排索引 | 精确术语、编号、过滤 | 同义表达召回有限 |
| 向量索引 | 语义相似召回 | 精确值、关系和治理需补充 |
| 关系数据库 | 强 schema、事务、权限 | 非结构化语义弱 |
| 知识图谱 | 实体关系、多跳和解释 | 建模、维护成本高 |
| 混合架构 | 兼顾精确、语义与关系 | 编排与一致性更复杂 |

知识图谱不是所有项目的默认答案。规则密集、多跳关系和跨域实体对齐时价值更大；FAQ 或产品手册通常先从文档 + 混合检索开始。

## 25.5 生命周期

```text
Discover → Ingest → Normalize → Classify → Review → Publish
        → Index → Monitor → Refresh/Supersede → Retire
```

关键控制：

- 内容更新与索引更新使用 outbox/event 保持一致；
- 新版本发布前保留旧版本的历史有效期；
- 删除传播到全文、向量、图和缓存；
- 定期检测孤儿 chunk、失效链接、过期 owner；
- 高频低置信查询进入知识补全 backlog。

## 25.6 工具横向对比

| 方案 | 核心模型 | 优点 | 局限 | 适用场景 |
|---|---|---|---|---|
| Elasticsearch/OpenSearch | 文档 + 倒排 + 向量 | 过滤、全文和混合检索成熟 | 图推理不是核心 | 企业搜索、RAG |
| Neo4j | Property Graph | 关系查询和路径解释强 | 图建模与运维成本 | 关系密集知识 |
| Microsoft GraphRAG | 图抽取与社区摘要 | 全局主题与复杂关系检索 | 索引成本和流程复杂 | 大语料研究分析 |
| RDF/OWL + Triplestore | 标准三元组和本体 | 语义互操作、推理标准化 | 学习与建模门槛 | 强标准、跨组织交换 |
| Data Catalog | 元数据、血缘、owner | 数据治理和发现 | 不直接负责生成检索 | 数据/指标知识 |
| 自建 Catalog | 领域模型完全可控 | 易集成 IAM 和审批 | 持续维护成本 | 特定行业知识平台 |

不要按“是否支持向量”选 Knowledge Platform，应按 provenance、ACL、temporal、ontology、lineage 和检索组合选型。

## 25.7 企业案例：制造业故障知识

故障 Agent 同时使用设备手册、维修工单、BOM 和实时告警。设备型号和零部件关系进入图谱，手册进入全文/向量索引，实时参数保留在时序库。每条知识携带工厂、设备代次、有效期和安全等级。检索先执行工厂与角色过滤，再进行语义召回，最终答案引用手册页码或工单编号。未经工程师审核的经验只能作为低置信建议，不能触发停机操作。

## 25.8 Python MVP

`knowledge_runtime` 展示：

- KnowledgeAsset 的 owner、source、tenant、domain 和有效期；
- 不可变且连续的版本；
- as-of 时间检索；
- tenant/domain 在召回阶段隔离；
- 结果保留 provenance。

```bash
python3 chapters/chapter25/example.py
python3 -m unittest discover -s chapters/chapter25 -p "test_*.py"
```

## 25.9 Production Readiness Checklist

- [ ] 每个资产有稳定 ID、owner、source 和分类
- [ ] 版本与有效时间分离建模
- [ ] ACL 在检索前执行，不靠生成后过滤
- [ ] 原文、chunk、embedding 和图节点可追溯
- [ ] 更新、删除和权限变更传播到所有索引
- [ ] 有新鲜度、覆盖率、重复率和失败率指标
- [ ] 人工审核与争议知识有工作流
- [ ] 低置信知识不能直接驱动高风险动作

## Summary

Knowledge Engineering 为 Agent 建立可信事实边界。知识只有在能说明来源、含义、适用范围、有效时间和访问主体时，才是企业可用资产。

## Notes

RDF、Property Graph、文档索引和向量库是不同抽象，可以组合使用；本章不主张用单一存储统一全部知识。

## References

[1] W3C, RDF 1.1 Concepts and Abstract Syntax.
https://www.w3.org/TR/rdf11-concepts/

[2] Microsoft, GraphRAG Documentation.
https://microsoft.github.io/graphrag/

[3] Neo4j, GraphRAG for Python.
https://neo4j.com/docs/neo4j-graphrag-python/current/

[4] OpenSearch, Hybrid search.
https://docs.opensearch.org/latest/vector-search/ai-search/hybrid-search/

以上 URL 已在 2026-07-31 核对。
