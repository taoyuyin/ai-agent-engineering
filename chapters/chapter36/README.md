# Chapter 36 Google ADK

Part V Frameworks —— 主流 Agent 框架设计

Version: 2026-07

Last Updated: 2026-07-31

## 本章结论

Google Agent Development Kit（ADK）围绕 Agent、Runner、Session、Event、Tool 和 Service 建立模块化运行时。它既能用 LLM Agent 处理开放式推理，也能用 Sequential、Parallel、Loop 等 Workflow Agent 表达确定性编排。

ADK 特别适合 Google Cloud、Gemini 和企业服务体系，但其设计并不只允许一种模型。真正的工程价值在于 Agent 定义与运行服务解耦，而不是某个模型 API。

## 学习目标

完成本章后，你应该能够：

- 解释 ADK 的 Agent、Runner、Session、Event 与 Service；
- 区分 LLM Agent、Workflow Agent 和 Custom Agent；
- 使用普通 Python 函数注册 Function Tool；
- 理解本地 `InMemoryRunner` 与生产 Runtime 的差异；
- 评估 ADK 在 Google Cloud 体系中的优势与迁移成本。

## 36.1 Agent 定义与运行环境解耦

一个 ADK 应用通常导出 `root_agent`。Agent 描述“它是谁、使用什么模型、有哪些工具”，Runner 负责“如何执行、会话放在哪里、事件如何流动”。

```text
Application
  └── root_agent
      ├── model / instruction
      ├── tools
      └── sub_agents

Runner
  ├── Session Service
  ├── Artifact Service
  ├── Memory Service
  └── Event stream
```

这种分离有利于把同一个 Agent 从开发环境迁移到服务运行环境。业务代码不应直接把会话、内存和部署细节写死在 Agent 定义中。

## 36.2 三类 Agent

| 类型 | 控制方式 | 适用场景 |
| --- | --- | --- |
| LLM Agent | 模型根据指令和工具决定下一步 | 问答、分析、开放式任务 |
| Workflow Agent | Sequential、Parallel、Loop 等确定性结构 | 固定阶段、并行收集、循环迭代 |
| Custom Agent | 开发者实现自定义执行逻辑 | 特殊协议、领域运行时、复杂控制 |

这三类可以组合。企业报告系统可以先用 `ParallelAgent` 并行获取销售、库存和风险数据，再由 LLM Agent 汇总；审批和发布仍由确定性 Workflow Agent 控制。

## 36.3 Runner、Session 与 Event

Runner 是 ADK 执行入口。一次运行不只是返回字符串，而是产生事件流。事件可能包含模型内容、工具调用、工具结果、状态变化和最终响应。

Session 保存一段交互的工作状态，Memory 则面向跨 Session 的长期信息。两者不要混为一谈：

- Session：当前任务的消息与临时状态；
- Memory：经过筛选、可在未来检索的长期信息；
- Artifact：文件、报告或其他大对象；
- Event：本次执行中发生的事实。

生产环境需要为这些 Service 选择持久化实现、隔离租户并定义保留周期。`InMemoryRunner` 适合开发验证，进程退出后数据消失。

## 36.4 Tool 与权限边界

ADK 可以把 Python 函数直接作为工具。函数签名和 Docstring 决定模型看到的工具接口：

```python
def query_sales(year: int, region: str | None = None) -> dict:
    """Return governed sales data for a year and optional region."""
    ...
```

工具应返回结构化、可解释结果，包括：

- `status`：成功、拒绝或失败；
- 业务数据；
- 指标定义；
- 证据源；
- 可恢复错误信息。

示例通过 `AGENT_SCOPES` 演示权限校验。生产系统不应信任普通环境变量，而应从认证中间件、Service Account 或请求上下文获得身份，并在数据库/API 层再次校验。

## 36.5 Multi-Agent 不是默认答案

ADK 支持父子 Agent 和 Agent Transfer，但每增加一个 Agent 都会引入：

- 上下文传递和信息丢失；
- 路由误判；
- 更多模型调用和延迟；
- 更复杂的 Trace 与评测；
- 责任边界不清。

只有当角色拥有不同工具、权限、上下文或优化目标时，才值得拆成多个 Agent。如果只是 Prompt 不同但访问同一数据、执行同一职责，先保留单 Agent。

## 36.6 最小可运行 MVP

目录结构：

```text
chapter36/
├── __init__.py
├── agent.py
├── example.py
├── requirements.txt
└── .env.example
```

`agent.py` 导出 ADK 约定的 `root_agent`，包含：

- Gemini 模型配置；
- 企业销售分析 Instruction；
- `query_sales` Function Tool；
- Scope 校验和证据源。

`example.py` 使用 `InMemoryRunner` 执行：

```bash
cd chapters/chapter36
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export GOOGLE_API_KEY="<your-api-key>"
export AGENT_SCOPES="sales:read"
python example.py "查询 2025 年各区域净销售额"
```

也可以从仓库的 `chapters` 目录使用 ADK 开发命令加载 `chapter36` Agent。官方 Web UI 面向本地开发与调试，不应直接作为生产服务暴露。

示例采用静态数据，目的是验证 Tool Contract、Runner 和事件执行。替换为数据库后，保留工具签名、权限校验和证据字段即可。

## 36.7 与相邻框架对比

| 维度 | Google ADK | OpenAI Agents SDK | LangGraph |
| --- | --- | --- | --- |
| 核心抽象 | Agent / Runner / Session / Event | Agent / Runner / Tool | State / Node / Edge |
| 确定性 Workflow | 内置 Workflow Agent | 通常在应用层组合 | Graph 是核心 |
| 多 Agent | 子 Agent、Transfer | Handoff、Agent-as-Tool | 子图、节点和路由 |
| 状态服务 | Session/Memory Service | Session/Context | Checkpointer/Store |
| 生态优势 | Gemini、Google Cloud | OpenAI 模型与工具 | 显式状态和恢复 |
| 学习成本 | 中等 | 较低 | 较高 |

如果团队已经运行在 Google Cloud，并希望统一模型、Agent、评测和部署体验，ADK 是自然选择。若只需一个轻量 OpenAI 工具 Agent，Agents SDK 更直接；若主要问题是复杂状态转移和恢复，LangGraph 更清晰。

## 36.8 生产架构

推荐把 ADK Agent 放在以下边界内：

```text
API Gateway / Identity
        |
Agent Service
  ├── ADK Runner
  ├── Session Service
  ├── Memory Service
  └── Artifact Service
        |
Governed Tools
  ├── Data API
  ├── Search
  └── Business Services
```

Agent Service 不直接持有无限权限。每个 Tool 使用短期凭证访问领域服务；领域服务负责最终授权、审计和租户过滤。

## 36.9 生产化清单

- 使用持久化 Session/Memory/Artifact Service；
- 从真实身份系统构造 Tool 权限；
- 区分开发 Runner、测试 Runner 和生产部署；
- 为 Tool 定义超时、重试、幂等与错误码；
- 保存 Event 流并关联业务 Trace ID；
- 对 Agent Transfer 设置目标白名单和最大次数；
- 管理 Instruction、模型与 Tool Schema 版本；
- 为权限拒绝、空数据、模型失败和恢复建立评测；
- 对 Artifact 和 Session 数据加密并设置生命周期；
- 在成本预算内限制循环次数和并行度。

## 36.10 优点、局限与适用场景

优点：

- Agent 与 Runner/Service 分离，模块边界清晰；
- 同时支持 LLM 推理与确定性 Workflow Agent；
- Session、Memory、Artifact、Event 模型较完整；
- 与 Google 模型及云平台衔接自然。

局限：

- 服务抽象较多，初学成本高于极简 SDK；
- 生产能力与 Google 生态结合较深时会产生平台依赖；
- Function Tool 的业务权限仍需自行实现；
- 多 Agent 设计不当会显著增加成本和调试难度。

最适合：Google Cloud 企业应用、Gemini 驱动的多模态 Agent、需要统一会话/事件服务的系统，以及同时包含 LLM Agent 和确定性工作流的项目。

## Summary

Google ADK 的关键不在于“调用 Gemini”，而在于把 Agent 定义、运行循环和状态服务分开。LLM Agent 负责开放式判断，Workflow Agent 负责确定性编排，Service 负责会话、记忆和产物。

本章 MVP 展示了可被 ADK 工具链识别的 `root_agent` 工程结构，以及如何通过 Runner 执行一个带权限和证据源的工具型 Agent。

## References

[1] Google. Agent Development Kit Documentation.
https://adk.dev/

[2] Google. Get Started with ADK for Python.
https://adk.dev/get-started/python/

[3] Google. ADK Apps.
https://adk.dev/apps/
