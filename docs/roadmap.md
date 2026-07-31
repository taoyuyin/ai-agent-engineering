# Roadmap

Version: 2026-07

Last Updated: 2026-07-28

## 项目愿景

`AI Agent Engineering` 是一本持续更新的企业级 AI Agent 工程教材，也是一套配套源码工程。

它的目标不是介绍某一个框架的 API，而是建立一套完整的 Agent 工程知识体系：

- 理解 Agent 为什么出现
- 理解 LLM 为什么让 Agent 成为可能
- 理解 Agent 内部如何工作
- 掌握企业级 Agent 的工程实现方法
- 分析主流 Agent 框架的设计思想
- 落地真实企业场景
- 思考下一代软件形态

本项目坚持：

```text
Agent Runtime
  ↓
OpenAI Agents SDK / LangGraph / Google ADK / CrewAI / AutoGen / Dify
```

先理解并实现 Agent Runtime，再学习成熟框架为什么这样设计。

## 全书结构

```text
Part I    Foundations          为什么需要 AI Agent
Part II   LLM Foundations      Agent 为什么能够工作
Part III  Agent Architecture   Agent 内部如何工作
Part IV   Agent Engineering    如何构建企业级 Agent
Part V    Frameworks           主流 Agent 框架设计
Part VI   Enterprise Practice  企业实践
Part VII  Future               下一代软件
```

## 工程贯通里程碑

章节源码用于解释单一能力，根目录工程用于验证这些能力能否组合：

```text
Chapter 12–23  Agent Architecture MVP
        ↓
framework/     Agent Runtime v0.1
        ↓
Chapter 24–33  Production Engineering
        ↓
examples/      企业场景端到端实现
```

当前第一条纵向主线：

- `framework/`：Goal、Plan、Tool、Policy、Executor、Memory、Workflow、Trace、Evidence；
- `examples/sql-agent/`：Schema Discovery、只读 SQL、权限、Evidence、FastAPI、Docker；
- Chapter 23：解释统一 Runtime 架构；
- Chapter 42：从 SQL Agent MVP 演进到生产级 Text-to-SQL。

## Part I Foundations —— 为什么需要 AI Agent

目标：建立世界观，理解 Agent 出现的历史背景。

这一部分不涉及任何框架。

### Chapter 1 软件为什么需要 AI Agent？

核心问题：为什么今天会出现 Agent？

主要内容：

- 软件复杂度的持续增长
- 从“执行流程”到“完成目标”
- LLM 带来的变化
- Agent 出现的必然性

输出：Agent 是软件执行范式的变化。

### Chapter 2 软件架构为什么不断演进？

主要内容：

```text
MVC
  ↓
SOA
  ↓
Microservice
  ↓
Cloud Native
  ↓
AI Agent
```

每一次架构演进都要回答：它解决了什么问题？

最后建立完整的软件技术栈视角。

输出：Agent 是 Intelligence Layer。

### Chapter 3 什么是真正的 AI Agent？

第一次正式定义 Agent。

讨论不同厂商和社区定义：

- OpenAI
- Anthropic
- Google

Agent 的五个组成：

- Goal
- Planning
- Tool
- Memory
- Feedback

输出：Agent 的统一定义。

### Chapter 4 Agent 与 Workflow 的区别

回答：

- 为什么 Workflow 不是 Agent
- 为什么 Agent 不等于 Workflow
- 什么时候需要 Workflow
- 什么时候需要 Agent
- 什么时候组合使用

输出：Agent 与 Workflow 的边界。

## Part II LLM Foundations —— Agent 为什么能够工作

目标：理解 LLM，而不是训练 LLM。

这一部分建立 Agent 的理论基础。

### Chapter 5 Transformer

主要内容：

- 为什么需要 Attention
- 为什么 Transformer 出现
- Transformer 对 LLM 的意义

### Chapter 6 Token

主要内容：

- Tokenizer
- BPE
- 为什么 Token 不是字符
- Token 对成本、上下文和输出控制的影响

### Chapter 7 Embedding

主要内容：

- 为什么向量可以表达语义
- Embedding 空间
- 相似度
- Embedding 在 Agent 和 RAG 中的位置

### Chapter 8 Context

主要内容：

- Context Window
- KV Cache
- 为什么模型会“遗忘”
- 上下文管理对 Agent 的意义

### Chapter 9 Reasoning

主要内容：

- Chain-of-Thought
- ReAct
- Tree of Thoughts
- Reflection
- Reasoning Model

### Chapter 10 Function Calling

主要内容：

- 为什么模型可以调用 Tool
- Structured Output
- JSON Schema
- Function Calling 与 Tool Calling 的工程意义

### Chapter 11 MCP

主要内容：

- 为什么需要 MCP
- MCP 的定位
- 协议设计
- 未来生态

## Part III Agent Architecture —— Agent 内部如何工作

目标：理解 Agent 的内部结构。

这是全书核心。

Part III 不重复 Part II 的底层原理，而是回答这些能力如何进入 Agent Runtime：

| Part II 底层能力 | Part III 架构落点 |
|---|---|
| Transformer / Model | Model Gateway、Planner、Reflection、Multi-Agent |
| Token | Run Budget、Context Budget、Observation Size、Cost |
| Embedding | Tool Discovery、Memory Retrieval、Agent Discovery、Knowledge Retrieval |
| Context | Context Compiler、Step Input、Delegation Envelope、Checkpoint |
| Reasoning | Goal Compiler、Planner、Reflection、Evaluator |
| Function Calling | Tool Proposal、Structured Command、Observation、State Event |
| MCP | Tool/Data Gateway、Capability Discovery、跨进程调用与治理 |

每章示例必须展示两层边界：

1. 模型或底层能力生成候选、分数或结构化提案；
2. Runtime 使用 schema、状态、权限、预算和策略做确定性控制。

### Chapter 12 Agent 生命周期

主要内容：

- Agent 生命周期
- 状态转换
- 从请求到结果的完整执行链路

### Chapter 13 Goal

主要内容：

- 目标理解
- 目标转换
- Goal Planning

### Chapter 14 Planner

主要内容：

- 任务拆解
- Planning Algorithm
- Plan Update
- Plan Execution

### Chapter 15 Tool

主要内容：

- Tool Registry
- Tool Selection
- Tool Routing
- Tool Result

### Chapter 16 Memory

主要内容：

- Working Memory
- Long-term Memory
- Memory Update
- Memory Retrieval

### Chapter 17 Context Engineering

主要内容：

- Context Assembly
- Context Compression
- Context Window 管理
- Prompt、Memory、Tool Result 的上下文组织

### Chapter 18 Observation

主要内容：

- Tool Result
- Observation
- Observation 到下一步决策的转换

### Chapter 19 Reflection

主要内容：

- Reflection
- Retry
- Repair
- Failure Recovery

### Chapter 20 State Machine

主要内容：

- 为什么 Agent 本质是状态机
- 状态、事件、转移
- Agent Runtime 中的状态管理

### Chapter 21 Workflow Engine

主要内容：

- Workflow
- DAG
- 事件驱动
- Workflow 与 Agent Runtime 的组合方式

### Chapter 22 Multi-Agent

主要内容：

- Agent Communication
- Task Delegation
- 协作、冲突与一致性

### Chapter 23 Agent Architecture

总结企业级 Agent 架构。

输出：从组件到系统的完整 Agent Architecture。

配套工程输出：`framework/ Agent Runtime v0.1`。各章的局部 MVP 在这里被组合为统一运行时，后续企业案例复用同一套契约。

## Part IV Agent Engineering —— 如何构建企业级 Agent

目标：Production Ready。

这一部分关注工程能力。

### Chapter 24 Prompt Engineering

主要内容：

- Prompt Architecture
- Prompt Version
- Prompt Evaluation

### Chapter 25 Knowledge Engineering

主要内容：

- 知识组织
- 知识生命周期
- 知识更新与治理

### Chapter 26 RAG

主要内容：

- Index
- Chunk
- Retrieve
- Generate
- RAG 与 Agent 的关系

### Chapter 27 Semantic Layer

主要内容：

- 为什么 Agent 需要 Semantic Layer
- 企业数据语义
- 指标、维度、口径与权限

### Chapter 28 Guardrails

主要内容：

- 安全
- 输出控制
- 权限
- 风险拦截

### Chapter 29 Evaluation

主要内容：

- Agent 如何评估
- Offline Evaluation
- Online Evaluation
- Benchmark

### Chapter 30 Observability

主要内容：

- Logging
- Tracing
- Timeline
- Agent 执行过程可观测性

### Chapter 31 Performance

主要内容：

- Latency
- Cache
- Batch
- Streaming

### Chapter 32 Cost Optimization

主要内容：

- Token
- 模型路由
- Cache
- 成本与质量平衡

### Chapter 33 Deployment

主要内容：

- 服务化
- 扩缩容
- 多模型部署
- 生产环境发布

## Part V Frameworks —— 主流 Agent 框架设计

目标：学习设计思想，不学习 API。

每一章统一回答：

- 为什么这样设计？
- 优点是什么？
- 缺点是什么？
- 适用场景是什么？
- 源码如何实现？

### Chapter 34 OpenAI Agents SDK

定位：OpenAI 官方 Agent 工程框架。

### Chapter 35 LangGraph

定位：基于图和状态机的 Agent / Workflow 编排框架。

### Chapter 36 Google ADK

定位：Google Agent Development Kit。

### Chapter 37 CrewAI

定位：面向角色分工的 Multi-Agent 框架。

### Chapter 38 AutoGen

定位：面向多 Agent 对话与协作的框架。

### Chapter 39 PydanticAI

定位：面向 Python 类型系统和结构化输出的 Agent 框架。

### Chapter 40 LlamaIndex

定位：面向数据、索引、RAG 与 Agent 的框架。

### Chapter 41 Dify

定位：Agent Platform，不是单纯的 Agent Framework。

## Part VI Enterprise Practice —— 企业实践

目标：真正落地。

每章统一模板：

- 背景
- 需求
- 架构
- 代码
- 上线
- 踩坑
- 总结

### Chapter 42 SQL Agent

面向结构化数据查询的 Agent。

配套工程输出：`examples/sql-agent/`。第一阶段使用离线可运行的确定性 Planner 验证 Runtime、安全与证据链，后续再接入 Model Gateway、Semantic Layer、SQL AST 与生产数据库权限。

### Chapter 43 Data Agent

面向数据分析、指标解释和数据任务执行的 Agent。

### Chapter 44 BI Agent

面向 BI、报表、指标问答和洞察生成的 Agent。

### Chapter 45 Coding Agent

面向代码阅读、修改、测试和提交的 Agent。

### Chapter 46 Enterprise Knowledge Agent

面向企业知识库、制度、文档和流程问答的 Agent。

### Chapter 47 Customer Service Agent

面向客服、工单、知识检索和流程执行的 Agent。

### Chapter 48 Manufacturing Agent

结合制造业场景，讨论生产、质量、设备、供应链与数据平台中的 Agent。

### Chapter 49 Multi-Agent 企业平台

讨论企业级 Multi-Agent 平台的架构、治理和运行机制。

## Part VII Future —— 下一代软件

目标：讨论 Agent 对软件工程和软件形态的长期影响。

### Chapter 50 Agent Platform

企业为什么最终都会建设 Agent Platform。

### Chapter 51 Agent Operating System

主要内容：

- Agent OS
- Agent Runtime
- Agent 调度与资源管理

### Chapter 52 Computer Use

主要内容：

- GUI Agent
- Browser Agent
- Computer Use 的工程边界

### Chapter 53 AI Native Software

主要内容：

- 什么是 AI Native
- AI Native 与传统软件的区别
- AI Native 应用架构

### Chapter 54 Future of Software Engineering

主要内容：

- Agent 对软件工程的影响
- 开发者角色变化
- 软件系统从流程驱动到目标驱动

## GitHub 工程组织

源码仓库继续围绕教材演进：

```text
ai-agent-engineering/
├── docs/                    # 教材配套文档
├── chapters/                # 每章源码
├── examples/                # 完整案例
├── framework/               # 自己实现 Agent Runtime
├── integrations/            # 模型与框架集成
├── prompts/                 # 提示词模板
├── datasets/                # 示例数据集
├── benchmark/               # 基准测试
├── evaluation/              # 评测方法与脚本
├── notebooks/               # 实验与分析 Notebook
├── architecture/            # 架构图与设计说明
└── scripts/                 # 工具脚本
```

后续章节源码应尽量复用 `framework/` 中的统一 Runtime，而不是每章复制一套临时代码。

## 版本与标签建议

建议后续按章节维护 tag：

```text
v0.1 / chapter01
v0.2 / chapter02
v0.3 / chapter03
...
v1.0 / part-i-complete
```

读者可以通过 tag 回到某一章对应的代码状态。

## 近期执行优先级

1. 完成 Part I 的 4 篇 Foundations 文章。
2. 为 `chapters/chapter01` 补齐与文章对应的源码和说明。
3. 建立章节模板，统一 `Learning Objectives / Summary / Notes / References`。
4. 为每章建立引用验证清单。
5. 逐步实现 `framework/runtime` 的最小可运行版本。
