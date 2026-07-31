# Chapter 38 AutoGen

Part V Frameworks —— 主流 Agent 框架设计

Version: 2026-07

Last Updated: 2026-07-31

## 本章结论

AutoGen 的核心设计是用消息和事件连接 Agent。高层 AgentChat 提供 AssistantAgent、Team 和常见协作模式，底层 Core 提供事件驱动、可扩展的 Agent Runtime。

它适合研究型、多角色对话和动态协作，但生产系统不应把一个通用 `AssistantAgent` 当成完整业务架构。需要长期维护时，应明确消息 Contract、终止条件、状态保存和自定义 Agent 边界。

## 学习目标

完成本章后，你应该能够：

- 区分 AutoGen Core、AgentChat 和扩展包；
- 理解 AssistantAgent、Message、Tool、Team 与终止条件；
- 使用结构化消息输出类型安全的结果；
- 解释多 Agent 对话为什么容易失控；
- 判断何时使用预置 Agent，何时实现领域 Custom Agent。

## 38.1 分层架构

AutoGen 不是单一的“群聊框架”，其主要层次是：

```text
Application
   |
AgentChat
  ├── AssistantAgent
  ├── UserProxy / Code Executor
  ├── Teams
  └── Termination Conditions
   |
Core
  ├── Agent Runtime
  ├── Messages / Events
  └── Distributed Extensions
   |
Extensions
  ├── Model Clients
  ├── Tools
  └── External integrations
```

AgentChat 适合快速搭建应用；Core 适合需要自定义消息协议、事件路由或 Runtime 的团队。不要在还没验证业务价值时就下沉到底层，也不要在需求已经超出预置 Agent 边界时继续堆 Prompt。

## 38.2 AssistantAgent 是有状态的运行组件

`AssistantAgent` 能组合模型、系统消息、工具、结构化输出和多轮工具调用。它会维护自身的消息状态，因此：

- 同一实例不应被多个并发请求无隔离地共享；
- 任务之间要明确是否继承上下文；
- 需要持久化时应使用状态保存/恢复能力；
- 测试要从干净状态开始，避免历史消息污染。

官方文档也将其定位为方便的高层 Agent。对于强领域约束、复杂生命周期或特殊消息协议，生产实现可能更适合自定义 Agent。

## 38.3 Message 是协作 Contract

多 Agent 系统中的核心不是“谁说了什么自然语言”，而是消息是否拥有稳定的类型和语义。

| 消息内容 | 推荐结构 |
| --- | --- |
| 任务委派 | task_id、goal、constraints、deadline |
| 工具结果 | status、data、source、error |
| 审核结论 | decision、violations、reviewer |
| 最终报告 | 领域 Pydantic Model |

自由文本适合面向人的解释，不适合 Agent 之间的关键控制。使用 `StructuredMessage` 和 Pydantic 模型，可以让下游代码拒绝缺字段或类型错误的输出。

## 38.4 Tool Loop 与并行调用

AssistantAgent 可以自动执行工具调用，并在工具结果后继续推理。工程上要控制：

- `max_tool_iterations`：最多执行几轮工具；
- `parallel_tool_calls`：模型客户端是否允许并行调用；
- Tool 超时和幂等；
- Tool 返回内容长度；
- 是否必须调用某个事实工具。

并行并不总是更快。多个工具如果写同一资源、依赖顺序或使用同一非线程安全客户端，应关闭并行。示例设置 `parallel_tool_calls=False`，确保销售查询行为可预测。

## 38.5 Team 与终止条件

Team 可以实现轮询、选择器或图式协作。一个 Team 至少需要明确：

- 哪个 Agent 可以发言或执行；
- 谁选择下一 Agent；
- 什么条件表示任务完成；
- 达到最大消息数后如何失败；
- 是否允许重复委派；
- 最终结果由哪个消息类型承载。

常见反模式是只写“大家讨论直到解决问题”。没有确定性终止条件的群聊可能循环、互相确认或不断生成新任务，成本和延迟不可控。

## 38.6 状态、恢复与分布式边界

AgentChat 组件支持状态保存和加载，但业务级恢复仍要设计：

- 保存哪一个 Agent/Team 的状态；
- 模型调用成功而外部写操作失败时如何补偿；
- 代码和消息 Schema 升级后旧状态如何兼容；
- 多租户状态如何隔离；
- 分布式 Runtime 中如何保证消息至少一次或至多一次处理。

消息驱动不自动等于可靠消息系统。需要跨进程运行时，应结合持久化队列、幂等消费者和可观测性。

## 38.7 最小可运行 MVP：类型化销售 Agent

本章示例先使用单个 AssistantAgent，避免在理解基本机制前引入 Team：

- `OpenAIChatCompletionClient` 提供模型适配；
- `query_sales` 是带 Scope 校验的异步 Tool；
- `SalesReport` 是最终输出 Schema；
- `output_content_type=SalesReport` 请求结构化消息；
- `max_tool_iterations=4` 限制循环；
- `finally` 中关闭模型客户端。

安装与运行：

```bash
cd chapters/chapter38
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export OPENAI_API_KEY="<your-api-key>"
export AGENT_SCOPES="sales:read"
python example.py "查询 2025 年各区域净销售额"
```

示例校验最后一条消息必须是 `StructuredMessage`，然后读取 Pydantic 内容。相比直接打印 `str(result)`，这使下游服务得到明确 Contract。

下一步可增加一个审核 Agent，但建议让它接收 `SalesReport`，而不是重新阅读全部对话并猜测事实。

## 38.8 与 CrewAI 的区别

| 维度 | AutoGen | CrewAI |
| --- | --- | --- |
| 主要抽象 | Message / Agent / Team | Role / Task / Crew |
| 协作方式 | 对话、事件、Team | 任务和角色分工 |
| 研究与动态讨论 | 强 | 中 |
| 业务可读性 | 中 | 高 |
| 底层 Runtime 扩展 | Core 提供较低层能力 | 重点在 Crew 与 Flow |
| 主要风险 | 消息循环与状态复杂 | 角色冗余与 Task 上下文膨胀 |

动态软件研究、代码执行和会话式协作适合 AutoGen；岗位职责和任务链清晰的运营流程更适合 CrewAI。两者都不能代替业务权限和可靠 Workflow。

## 38.9 企业案例：软件故障分析 Team

```text
Incident Coordinator
  ├── Log Analyst Tool/Agent
  ├── Deployment Analyst Agent
  ├── Code Search Agent
  └── Reviewer Agent
```

各 Agent 通过类型化消息传递证据。Coordinator 维护问题清单和截止时间，Reviewer 只能标记证据不足，不能直接执行回滚。回滚由外部审批 Workflow 调用受控 Tool 完成。

这个场景适合消息式协作，因为调查路径会随新证据变化；生产变更步骤则保持确定性。

## 38.10 生产化清单

- 不跨并发请求共享有状态 Agent 实例；
- 为消息定义 Pydantic Contract 和版本；
- 设置最大消息数、最大工具轮数和时间预算；
- 为 Team 定义确定性终止条件；
- Tool 使用最小权限、超时、幂等和审计；
- 保存/恢复状态时考虑 Schema 迁移；
- 对模型 Client 做生命周期管理；
- 记录每条消息、工具结果和路由决定；
- 将高风险写操作移到审批 Workflow；
- 分别评测单 Agent 能力、路由正确率和 Team 完成率。

## 38.11 优点、局限与适用场景

优点：

- 从高层 AgentChat 到低层 Core 的扩展路径完整；
- 消息和 Team 模型适合动态多 Agent 协作；
- 工具、结构化输出和模型客户端可组合；
- 研究、代码执行和复杂对话模式丰富。

局限：

- 多 Agent 消息流容易增加复杂度、延迟和成本；
- 预置 AssistantAgent 不一定满足生产领域约束；
- 并发、状态共享和终止条件需要谨慎设计；
- 可靠分布式执行仍需要消息基础设施和业务幂等。

最适合：软件工程 Agent、研究 Agent、动态问题求解、多角色模拟，以及需要自定义消息驱动 Runtime 的项目。

## Summary

AutoGen 把 Agent 协作建模为消息和事件。AgentChat 让原型开发快速，Core 为自定义 Runtime 留出空间。工程化的关键不是让 Agent 说得更多，而是让消息有类型、循环有终点、状态可隔离、工具有权限。

本章从单 AssistantAgent MVP 开始，是为了先掌握类型化 Tool Loop；只有当角色边界和协作收益明确后，再升级为 Team。

## References

[1] Microsoft. AutoGen AgentChat User Guide.
https://microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/index.html

[2] Microsoft. AgentChat Agents Tutorial.
https://microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/tutorial/agents.html

[3] Microsoft. AgentChat Teams Tutorial.
https://microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/tutorial/teams.html

[4] Microsoft. AutoGen Core Tools.
https://microsoft.github.io/autogen/stable/user-guide/core-user-guide/components/tools.html
