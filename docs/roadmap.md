# Roadmap

Version: 2026-08

Last Updated: 2026-08-03

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

目标：学习设计思想，不把教程写成 API 手册。

每一章统一回答：

- 为什么这样设计？
- 核心抽象如何映射到 Agent Runtime？
- 运行循环、状态、工具和恢复如何实现？
- 优点、局限和适用场景是什么？
- 与相邻框架如何选择？
- 如何通过独立 Python MVP 验证？
- 上线前还需要补齐哪些企业能力？

统一比较基准：

> 用户查询 2025 年各区域净销售额。系统必须在工具执行点校验 `sales:read`，禁止模型编造事实，并在结果中保留数据证据源。

各章使用框架的原生抽象实现同一业务，以便比较控制流、状态模型、类型约束、依赖注入、多 Agent、RAG 和平台化差异。每章提供 `README.md`、`example.py`、`requirements.txt` 和 `.env.example`；平台型产品额外提供应用 Contract 与配置步骤。

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

统一交付标准：

- 每章从一个可验收的业务目标开始，而不是从框架 API 开始；
- 明确 Identity、Data、Tool、Workflow、Human Approval 和 Evidence 边界；
- 提供默认离线可运行的 Python MVP，先验证控制面，再替换为 LLM 节点；
- 说明生产数据源、权限、部署、可观测和评测升级路径；
- 对安全拒绝、空数据、冲突证据、工具失败和恢复路径进行设计；
- 用业务指标、质量指标和系统指标共同验收。

八章能力递进：

```text
SQL / Data / BI
  -> Coding / Knowledge / Customer Service
  -> Manufacturing High-risk Boundary
  -> Multi-Agent Enterprise Platform
```

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

目标：从当前可验证的 Agent 工程能力出发，讨论下一代运行平台、交互方式、软件架构和研发范式。

这一部分的写作规则：

1. 区分当前能力、架构抽象和趋势预测；
2. 趋势判断注明时间尺度、置信度和关键假设；
3. 优先引用协议、官方文档、研究报告和论文等一手资料；
4. 不为尚未出现的产品编造 API，MVP 验证可落地的控制面；
5. 延续全书边界：模型提出候选，确定性 Runtime、Policy 和 Evidence 决定执行。

| Chapter | 核心问题 | Python MVP |
| --- | --- | --- |
| 50 Agent Platform | 多团队如何复用、发布和治理 Agent | Manifest、Release Gate、Registry、Router |
| 51 Agent Operating System | Agent 工作负载如何调度、隔离与恢复 | Filter/Score Scheduler、资源预留、Capability |
| 52 Computer Use | Agent 如何安全操作 GUI | Observation、Action Policy、Human Confirmation |
| 53 AI Native Software | 软件如何从功能驱动转向目标驱动 | Goal-to-Capability Planner、动态 UI Projection |
| 54 Future of Software Engineering | 人与 Agent 如何共同交付可信变更 | Change Provenance、Evidence Gate、Trust Score |

### Chapter 50 Agent Platform

主要内容：

- Agent Application、Runtime 与 Platform 的边界
- Control Plane、Runtime Plane 和 Data Plane
- Model Gateway、Registry、Tool/MCP、Knowledge、Eval、Policy、Observability、FinOps
- Agent Manifest、发布门禁、版本、灰度与回滚
- SDK、低代码、云托管、自研和混合平台横向比较
- 从单应用到生态化的平台成熟度模型

输出：Agent Platform 是多团队规模化后的共享交付与治理系统，而不是所有企业的第一步。

### Chapter 51 Agent Operating System

主要内容：

- Agent OS
- Agent Runtime、Platform 与 OS 的职责边界
- Workload Spec、生命周期、Checkpoint 和 Durable Execution
- Filter/Score 调度与 Token、成本、工具、人工注意力资源模型
- Capability-based Security 与最小权限委派
- 与 Kubernetes Scheduler、Workflow Engine 和传统 OS 的类比及边界
- Context 虚拟化、跨模型迁移和资源计量等开放问题

输出：Agent OS 是有状态 Agent Workload 的架构抽象，当前仍处于概念与实现快速演进期。

### Chapter 52 Computer Use

主要内容：

- GUI Agent
- Browser Agent
- API、DOM、Accessibility、Vision 和 Hybrid 路线对比
- Observation–Action–Execute–Verify 循环
- 坐标脆弱性、部分可观测状态、幂等和独立验证
- Sandbox、Allowlist、Prompt Injection、Secret 与即时人工确认
- Task Success、Recovery、Unsafe Action、Latency 和 Cost 评测

输出：Computer Use 是无 API 场景的受治理 Tool，生产原则是 API first、GUI fallback。

### Chapter 53 AI Native Software

主要内容：

- 什么是 AI Native
- AI Native 与传统软件的区别
- Goal、Constraint、Plan、Evidence、Confidence 与 Approval 一等状态
- Deterministic Core、Intelligence Layer 与 Interaction Projection
- Capability Contract、动态规划和生成式 UI
- Context、Memory、模型可替换与降级
- 传统应用从 AI Feature 到 AI Native Product 的演进路径

输出：AI Native 的本质是目标驱动和能力动态组合，业务不变量仍由确定性核心维护。

### Chapter 54 Future of Software Engineering

主要内容：

- Agent 对软件工程的影响
- Capability、Benchmark、Productivity 与 Business Outcome 的证据边界
- 软件工作单元从代码转向 Executable Intent + Evidence + Provenance
- Requirements、Design、Implementation、Verification、Review 和 Operations 的变化
- Agent-ready Repository 与新软件供应链风险
- 开发者、架构、测试、平台、安全和产品角色变化
- 近期、中期和长期预测及置信度

输出：Agent 改变代码生产方式，但可信结果仍依赖更强的软件工程系统。

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

## 后续执行优先级

1. 将 54 章的独立 MVP 纳入统一静态检查和示例索引；
2. 把 Part VI 的业务案例与 `framework/` Runtime 形成更多纵向工程主线；
3. 为关键章节补充架构图、评测数据集和可复现实验；
4. 按季度复核 Part V 工具版本和 Part VII 趋势判断；
5. 建立章节完成度、引用验证和代码运行状态清单。
