# Chapters

每个章节目录包含对应文章的示例源码。

## Part I Foundations —— 为什么需要 AI Agent

- [Chapter 1 软件为什么需要 AI Agent？](chapter01/README.md)
- [Chapter 2 软件架构为什么不断演进？](chapter02/README.md)
- [Chapter 3 什么是真正的 AI Agent？](chapter03/README.md)
- [Chapter 4 Agent 与 Workflow 的区别](chapter04/README.md)

## Part II LLM Foundations —— Agent 为什么能够工作

- [Chapter 5 Transformer](chapter05/README.md)
- [Chapter 6 Token](chapter06/README.md)
- [Chapter 7 Embedding](chapter07/README.md)
- [Chapter 8 Context](chapter08/README.md)
- [Chapter 9 Reasoning](chapter09/README.md)
- [Chapter 10 Function Calling](chapter10/README.md)
- [Chapter 11 MCP](chapter11/README.md)

## Part III Agent Architecture —— Agent 内部如何工作

本部分把 Part II 的 Token、Embedding、Context、Reasoning、Function Calling 和 MCP 投射到 Agent Runtime；每章同时给出确定性控制边界与完整 Python MVP。

- [Chapter 12 Agent 生命周期](chapter12/README.md)
- [Chapter 13 Goal](chapter13/README.md)
- [Chapter 14 Planner](chapter14/README.md)
- [Chapter 15 Tool](chapter15/README.md)
- [Chapter 16 Memory](chapter16/README.md)
- [Chapter 17 Context Engineering](chapter17/README.md)
- [Chapter 18 Observation](chapter18/README.md)
- [Chapter 19 Reflection](chapter19/README.md)
- [Chapter 20 State Machine](chapter20/README.md)
- [Chapter 21 Workflow Engine](chapter21/README.md)
- [Chapter 22 Multi-Agent](chapter22/README.md)
- [Chapter 23 Agent Architecture](chapter23/README.md)

## Part IV Agent Engineering —— 如何构建企业级 Agent

- [Chapter 24 Prompt Engineering](chapter24/README.md)
- [Chapter 25 Knowledge Engineering](chapter25/README.md)
- [Chapter 26 RAG](chapter26/README.md)
- [Chapter 27 Semantic Layer](chapter27/README.md)
- [Chapter 28 Guardrails](chapter28/README.md)
- [Chapter 29 Evaluation](chapter29/README.md)
- [Chapter 30 Observability](chapter30/README.md)
- [Chapter 31 Performance](chapter31/README.md)
- [Chapter 32 Cost Optimization](chapter32/README.md)
- [Chapter 33 Deployment](chapter33/README.md)

## Part V Frameworks —— 主流 Agent 框架设计

本部分不按 API 罗列框架功能，而是用同一个“受治理的销售分析 Agent”基准，从运行时、状态、工具、结构化输出、权限、恢复和平台化能力进行横向比较。每章包含独立依赖、环境变量模板和 Python MVP。

| Chapter | 核心抽象 | 最适合解决的问题 |
| --- | --- | --- |
| 34 OpenAI Agents SDK | Agent / Runner / Tool / Handoff | 以较少代码构建完整 Agent Loop |
| 35 LangGraph | State / Node / Edge / Checkpoint | 显式状态、复杂分支、中断与恢复 |
| 36 Google ADK | Agent / Runner / Session / Event | Google 生态中的模块化 Agent 应用 |
| 37 CrewAI | Agent / Task / Crew / Flow | 角色与任务驱动的业务协作 |
| 38 AutoGen | Message / Agent / Team / Runtime | 消息驱动的动态 Multi-Agent |
| 39 PydanticAI | Agent / Dependencies / Output Type | 类型安全的 Python Agent 服务 |
| 40 LlamaIndex | Index / Retriever / Query Engine / Agent | RAG 与数据密集型 Agent |
| 41 Dify | App / Workflow / Knowledge / Plugin | 低代码 Agent 应用平台与交付 |

- [Chapter 34 OpenAI Agents SDK](chapter34/README.md)
- [Chapter 35 LangGraph](chapter35/README.md)
- [Chapter 36 Google ADK](chapter36/README.md)
- [Chapter 37 CrewAI](chapter37/README.md)
- [Chapter 38 AutoGen](chapter38/README.md)
- [Chapter 39 PydanticAI](chapter39/README.md)
- [Chapter 40 LlamaIndex](chapter40/README.md)
- [Chapter 41 Dify](chapter41/README.md)

## Part VI Enterprise Practice —— 企业实践

本部分将前五部分的 Runtime、LLM、架构、工程治理和框架能力放入真实业务。八章不共享一个空泛 Agent 模板，而是分别实现企业交付中最关键的控制面。

| Chapter | 业务能力 | MVP 验证重点 |
| --- | --- | --- |
| 42 SQL Agent | 结构化数据问答 | Semantic Metric、参数化 SQL、租户与 Evidence |
| 43 Data Agent | 探索和诊断分析 | Data Quality Gate、统计异常与可复现解释 |
| 44 BI Agent | KPI 与报表洞察 | Semantic Layer、RLS、Dashboard Spec |
| 45 Coding Agent | 代码变更闭环 | Sandbox、Patch、Test、Rollback、Approval |
| 46 Knowledge Agent | 企业制度问答 | ACL-first Retrieval、版本和 Citation |
| 47 Customer Service | 客服与工单 | 身份、政策、Action Risk 与 Handoff |
| 48 Manufacturing | 设备诊断 | OT 边界、遥测、风险和人工工单 |
| 49 Multi-Agent Platform | 企业协作平台 | Registry、Scope、Budget、Hop 与 Trace |

- [Chapter 42 SQL Agent](chapter42/README.md)
- [Chapter 43 Data Agent](chapter43/README.md)
- [Chapter 44 BI Agent](chapter44/README.md)
- [Chapter 45 Coding Agent](chapter45/README.md)
- [Chapter 46 Enterprise Knowledge Agent](chapter46/README.md)
- [Chapter 47 Customer Service Agent](chapter47/README.md)
- [Chapter 48 Manufacturing Agent](chapter48/README.md)
- [Chapter 49 Multi-Agent 企业平台](chapter49/README.md)

## Part VII Future —— 下一代软件

- [Chapter 50 Agent Platform](chapter50/README.md)
- [Chapter 51 Agent Operating System](chapter51/README.md)
- [Chapter 52 Computer Use](chapter52/README.md)
- [Chapter 53 AI Native Software](chapter53/README.md)
- [Chapter 54 Future of Software Engineering](chapter54/README.md)

## 章节目录规范

每章至少包含：

1. `README.md`：章节正文、结构、引用和工程说明
2. `example.py`：可运行的最小 Python MVP
3. `requirements.txt`：本章独立环境依赖
4. `.env.example`：需要外部服务时提供环境变量模板

平台型章节还应提供外部应用 Contract 和配置步骤，避免只保留无法复现的控制台截图。

不依赖外部服务的离线 MVP 可以不提供 `.env.example`，但仍需用 `requirements.txt` 明确 Python 版本和依赖边界。
