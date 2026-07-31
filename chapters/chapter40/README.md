# Chapter 40 LlamaIndex

Part V Frameworks —— 主流 Agent 框架设计

Version: 2026-07

Last Updated: 2026-07-31

## 本章结论

LlamaIndex 的差异化优势是数据和知识抽象：Document、Node、Index、Retriever、Query Engine、Tool 与 Agent 可以组成一条完整的知识访问链。Agent 不是孤立聊天机器人，而是受控调用数据能力的决策层。

它最适合 RAG、企业知识和数据密集型 Agent；如果应用没有知识检索需求，只需要几个业务 Tool，使用更轻量的 Agent SDK 会更简单。

## 学习目标

完成本章后，你应该能够：

- 理解 LlamaIndex 从数据摄取到 Agent Tool 的分层；
- 区分 `FunctionAgent`、`AgentWorkflow` 和 Query Engine；
- 将普通 Python 函数或 RAG Query Engine 暴露为 Tool；
- 设计带权限、引用和证据的知识 Agent；
- 评估模块化生态带来的能力与依赖成本。

## 40.1 数据是第一等公民

典型知识 Agent 链路：

```text
Data Sources
   -> Reader / Ingestion
   -> Document / Node
   -> Embedding / Index
   -> Retriever
   -> Query Engine
   -> Tool
   -> FunctionAgent / AgentWorkflow
```

这条链路覆盖 Chapter 7 Embedding、Chapter 16 Memory、Chapter 17 Context Engineering 和 Chapter 26 RAG 在 Agent 中的实际落点。

模型负责理解目标和选择工具；Retriever 负责候选召回；Query Engine 负责基于证据生成或聚合；权限层负责过滤可见数据。四者不能混成一个巨大 Prompt。

## 40.2 核心抽象

| 抽象 | 作用 | 常见工程问题 |
| --- | --- | --- |
| Document / Node | 表示原始内容和切分单元 | 元数据、版本、ACL |
| Index | 组织可检索表示 | 更新、一致性、成本 |
| Retriever | 根据查询召回候选 | Top-K、过滤、混合检索 |
| Query Engine | 对检索结果执行回答/聚合 | 引用、Prompt、响应模式 |
| Tool | 向 Agent 暴露函数或 Query Engine | 描述、Schema、权限 |
| FunctionAgent | 基于 Function Calling 选择 Tool | 循环上限、模型能力 |
| AgentWorkflow | 组织多个 Agent 或工作阶段 | 状态、路由、交接 |

真正影响知识 Agent 质量的通常不是 Agent Prompt，而是数据新鲜度、Chunk、Embedding、Metadata、Retriever 和引用链。

## 40.3 FunctionAgent 的运行机制

`FunctionAgent` 接收模型、工具和 System Prompt。运行时大致执行：

```text
user_msg
  -> model reads tool schemas
  -> chooses tool and arguments
  -> tool returns evidence
  -> evidence enters context
  -> model produces answer
```

普通 Python 函数可以直接作为 Tool；已有的 Query Engine 也可以包装成 Tool。因此团队可以先独立验证检索质量，再交给 Agent 做路由，避免同时调试 RAG 和 Agent Loop。

## 40.4 AgentWorkflow 与事件驱动

当一个 Agent 不足以完成任务时，`AgentWorkflow` 可以组合多个 Agent。适合拆分的情况包括：

- 不同数据域具有不同 ACL；
- 不同 Agent 使用不同 Query Engine；
- 一个 Agent 负责研究，另一个负责引用审查；
- 不同阶段需要不同模型或成本策略。

仍然要避免“每个知识库一个聊天角色”的机械拆分。若只是需要跨多个索引检索，可以先用 Router Retriever 或统一 Tool 层解决。

## 40.5 权限必须进入检索链

知识库权限不能依赖模型自觉忽略无权内容。正确链路是：

```text
authenticated identity
  -> tenant / group ACL filter
  -> Retriever
  -> authorized Nodes only
  -> Query Engine
  -> Agent answer with citations
```

如果先全库召回再让模型过滤，敏感内容已经进入上下文，构成数据泄露。Metadata Filter、分租户索引、行级权限或受治理 Search API 必须在检索阶段生效。

## 40.6 最小可运行 MVP：数据工具型 FunctionAgent

为了单独理解 Agent 机制，本章先用普通 Python 函数作为数据 Tool：

- `query_sales` 校验 `sales:read`；
- Tool 返回指标、行数据和证据源；
- `FunctionAgent` 必须通过 Tool 获取事实；
- OpenAI LLM Adapter 由独立包提供；
- 异步 `agent.run` 执行任务。

安装与运行：

```bash
cd chapters/chapter40
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export OPENAI_API_KEY="<your-api-key>"
export AGENT_SCOPES="sales:read"
python example.py "查询 2025 年各区域净销售额"
```

下一步升级为 RAG Agent 时，可以保持 FunctionAgent 不变，把 `query_sales` 替换为经过独立评测的 Query Engine Tool：

```python
knowledge_tool = QueryEngineTool.from_defaults(
    query_engine=query_engine,
    name="search_product_manual",
    description="Search approved product manuals and return citations.",
)
```

生产代码还应返回结构化 Source Node、文档版本和可点击引用，而不是只返回拼接文本。

## 40.7 与向量数据库的关系

LlamaIndex 不是向量数据库。它提供数据连接、索引和检索抽象，底层向量可以存入 Qdrant、Milvus、Weaviate、Pinecone、pgvector 等系统。

选择数据库时回到 Chapter 7 的维度：

- 数据规模与写入频率；
- Metadata Filter 与多租户隔离；
- 混合检索；
- 一致性和备份；
- 托管或自建成本；
- 团队已有数据库能力。

框架 Adapter 降低了接入成本，却不能消除数据库特性差异。上线前必须基于真实数据评测召回率、P95 延迟和更新可见时间。

## 40.8 与相邻框架对比

| 维度 | LlamaIndex | PydanticAI | LangGraph |
| --- | --- | --- | --- |
| 核心优势 | 数据、索引、检索、Query Engine | 类型化 Agent 应用 | 显式状态与 Workflow |
| RAG 能力 | 一等公民 | 通过自定义 Tool 集成 | 作为节点集成 |
| Agent 抽象 | FunctionAgent / Workflow | Agent + Deps + Output | Node/Subgraph |
| 适合问题 | 知识与数据密集型 Agent | 类型化业务服务 | 复杂长流程 |
| 主要代价 | 模块与依赖较多 | 需自行组合知识层 | 图和状态设计复杂 |

三者可以组合：LlamaIndex 构建 Query Engine，PydanticAI 提供类型化业务 Agent，LangGraph 管理长流程。但只有在复杂度确实需要时才组合，避免框架叠加。

## 40.9 企业案例：制造业知识 Agent

```text
用户故障描述
  -> 身份与设备权限
  -> 设备型号路由
  -> 混合检索
       ├── 维修手册
       ├── 历史工单
       └── 备件知识
  -> FunctionAgent 选择诊断 Tool
  -> 输出步骤、风险和引用
  -> 高风险动作转人工
```

索引中的 Node 要带设备型号、工厂、版本、生效时间和 ACL。回答必须展示证据，过期手册不得参与召回。Agent 只能建议，不直接绕过维修审批。

## 40.10 生产化清单

- 为 Document/Node 保存来源、版本、时间和 ACL；
- 在 Retriever 阶段执行租户与权限过滤；
- 独立评测 Chunk、Embedding、Retriever 和 Reranker；
- 返回引用并检查引用是否真正支持结论；
- 建立增量索引、删除传播和数据新鲜度监控；
- 限制 Agent 工具循环和上下文大小；
- 对 Query Engine 与 Agent 分层记录 Trace；
- 锁定包版本并验证升级兼容；
- 对空召回、冲突证据和过期内容定义策略；
- 高风险建议进入人工审核。

## 40.11 优点、局限与适用场景

优点：

- 数据连接、摄取、索引、检索到 Agent 的抽象完整；
- Query Engine 可以作为独立可评测能力；
- 支持多种模型和向量存储；
- 适合构建带引用的知识密集型 Agent。

局限：

- 模块化生态带来较多包和版本管理工作；
- 抽象层多时，问题定位需要理解完整数据链；
- 使用框架不代表 RAG 质量自动达标；
- 简单工具 Agent 使用它可能过重。

最适合：企业知识库、文档问答、研究 Agent、数据检索 Agent、制造业维护知识和需要多数据连接器的系统。

## Summary

LlamaIndex 的核心不是“又一个 Agent Loop”，而是把企业数据加工成 Agent 可调用、可引用、可评测的工具。FunctionAgent 负责选择数据能力，Retriever 和 Query Engine 负责证据，权限过滤负责安全。

本章 MVP 先验证 Function Tool Agent；真正的企业升级路径是把工具替换为经过独立质量评测的受治理 Query Engine。

## References

[1] LlamaIndex. Python Documentation.
https://docs.llamaindex.ai/en/stable/

[2] LlamaIndex. Agents.
https://docs.llamaindex.ai/en/stable/module_guides/deploying/agents/

[3] LlamaIndex. Agent Introduction.
https://developers.llamaindex.ai/python/framework/understanding/agent/
