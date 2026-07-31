# Chapter 35 LangGraph

Part V Frameworks —— 主流 Agent 框架设计

Version: 2026-07

Last Updated: 2026-07-31

## 本章结论

LangGraph 不是“替你写 Agent”的高级封装，而是一个面向长运行、有状态任务的低层编排运行时。它把 Agent 明确表示为 `State + Node + Edge`，并通过 Checkpoint、Interrupt 和线程状态支持恢复、人工审批与审计。

它适合业务路径复杂、状态必须可见、失败后需要恢复的企业 Agent；代价是团队必须认真设计状态 Schema、节点副作用和版本迁移。

## 学习目标

完成本章后，你应该能够：

- 用状态机而不是对话脚本理解 LangGraph；
- 设计 `StateGraph`、Node、普通 Edge 和 Conditional Edge；
- 解释 Checkpointer、`thread_id` 与持久化恢复的关系；
- 把 LLM 节点、工具节点和确定性业务节点组合在一张图中；
- 判断何时使用 LangGraph，何时简单 Agent Loop 已经足够。

## 35.1 为什么需要显式图

简单 Agent 可以让模型自行决定下一步，但企业流程经常包含不能交给模型自由判断的规则：

- 未授权必须立即终止；
- 写操作之前必须人工审批；
- 工具超时要进入补偿节点；
- 同一任务重启后必须从最近状态继续；
- 不同分支需要不同 SLA、权限和审计策略。

LangGraph 将这些约束提升为图结构。模型可以在某个节点内部推理，但节点之间如何移动仍由 Edge 和路由函数控制。因此它不是“Workflow 与 Agent 二选一”，而是把确定性 Workflow 与非确定性 Agent 放进同一个运行时。

## 35.2 核心模型

| 抽象 | 含义 | 设计问题 |
| --- | --- | --- |
| State | 节点共享、逐步更新的数据 | 哪些字段必须持久化，如何合并 |
| Node | 接收 State 并返回状态更新的函数 | 是否有副作用，能否安全重试 |
| Edge | 固定的状态转移 | 哪些顺序必须确定 |
| Conditional Edge | 根据当前状态选择下一节点 | 路由逻辑是否可测试 |
| Checkpointer | 保存每一步的状态快照 | 存储、隔离、保留和恢复策略 |
| Thread | 同一执行历史的标识 | 如何映射租户、会话和业务任务 |
| Interrupt | 暂停图并等待外部输入 | 审批身份、超时和恢复 |

典型运行图：

```text
START
  -> understand
  -> authorize
       ├─ allowed  -> query_sales -> synthesize -> END
       └─ rejected -> reject --------------------> END
```

这里的权限分支是普通 Python 函数，因此可以单元测试；未来把 `understand` 或 `synthesize` 换成 LLM 节点，不会改变授权边界。

## 35.3 State 不是消息列表

很多入门示例只维护 `messages`，但企业状态还包括：

- `tenant_id`、`actor_id` 和授权 Scope；
- 当前阶段、重试次数和截止时间；
- 结构化计划和工具结果；
- 审批决定与审批人；
- 业务主键、幂等键和证据源；
- 用户可见答案与内部错误。

状态设计应遵循三个原则：

1. **最小但足够恢复**：不保存能重新计算的巨量临时数据；
2. **Schema 明确**：使用 `TypedDict`、Dataclass 或 Pydantic 类型；
3. **外部数据存引用**：大文件、向量和敏感记录留在专用存储中，State 只保存 ID 和摘要。

当多个节点并行更新同一字段时，还需要定义 Reducer。状态合并语义如果不明确，并行图会产生难以复现的结果。

## 35.4 Node：把副作用隔离出来

节点可以是普通函数、异步函数或调用 Agent 的函数。推荐将节点分为三类：

- **纯计算节点**：解析、路由、格式化，可安全重放；
- **推理节点**：调用模型，需记录模型、Prompt 和输出；
- **副作用节点**：查询数据库、发消息、写订单，需超时、幂等和补偿。

Checkpoint 允许重新运行，并不自动让副作用幂等。例如支付节点成功后进程崩溃，如果恢复时再次执行就可能重复扣款。正确做法是让节点使用业务幂等键，并从外部系统查询操作状态。

## 35.5 Checkpoint、Thread 与恢复

编译 Graph 时配置 Checkpointer：

```python
graph = builder.compile(checkpointer=checkpointer)
```

调用时提供稳定的 `thread_id`：

```python
config = {"configurable": {"thread_id": business_task_id}}
result = graph.invoke(input_state, config=config)
```

Checkpointer 保存某个 Thread 在各个 Super-step 的状态。开发阶段可使用内存实现，生产环境应替换为持久化存储，并设计：

- 租户级数据隔离；
- Checkpoint 加密和保留周期；
- State Schema 升级与兼容；
- 历史分支清理；
- 恢复后的副作用语义。

`thread_id` 应映射业务任务，而不是每次请求随机生成，否则无法恢复同一执行。

## 35.6 Human-in-the-loop

人工审批不是在 Prompt 中询问“是否继续”，而是在危险节点前暂停运行，向外部审批系统发出可审计任务，收到审批结果后从同一 Thread 恢复。

```text
prepare_action -> interrupt
                  |
          approval service
             /          \
        approve          reject
           |               |
       execute_action     cancel
```

生产系统还需验证恢复者身份、防止重复审批、设置超时策略，并记录“谁在何时批准了什么参数”。

## 35.7 最小可运行 MVP：可检查点的销售分析状态机

本章 `example.py` 实现：

- `understand`：从问题提取年份；
- `authorize`：确定性校验 `sales:read`；
- Conditional Edge：在查询和拒绝分支间路由；
- `query_sales`：读取演示数据；
- `synthesize`：生成用户答案；
- `InMemorySaver`：保存运行状态。

安装与运行：

```bash
cd chapters/chapter35
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python example.py "查询 2025 年各区域净销售额"
```

这个 MVP 不需要模型 API，因此可以先看清图运行机制。若要增加 LLM，只需把 `understand` 或 `synthesize` 替换成模型调用，而不是让模型接管权限路由。

要验证拒绝路径，可将输入 State 的 `scopes` 改为空列表。要演示跨进程恢复，则把 `InMemorySaver` 替换为官方支持的持久化 Checkpointer，并使用固定 `thread_id`。

## 35.8 与 OpenAI Agents SDK 的区别

| 维度 | LangGraph | OpenAI Agents SDK |
| --- | --- | --- |
| 中心抽象 | State / Node / Edge | Agent / Runner / Tool |
| 控制流 | 开发者显式定义 | Runner 管理 Agent Loop |
| 状态可见性 | 高，State 是一等公民 | 以运行结果、会话和上下文组织 |
| 长流程恢复 | Checkpointer 是核心能力 | 通常结合外部持久化流程 |
| 人工审批 | Interrupt 与恢复自然表达 | 可通过工具/应用层实现 |
| 开发成本 | 较高 | 较低 |

两者可以组合：用 LangGraph 管理跨阶段业务状态，在某个节点内调用一个 Agents SDK Agent 完成开放式推理。

## 35.9 生产化清单

- 为 State 建立版本号和迁移策略；
- 每个副作用节点都实现业务幂等；
- 持久化 Checkpointer，不使用进程内存作为生产状态；
- `thread_id` 包含可追踪业务语义，但不泄露敏感信息；
- 节点设置超时、重试上限和错误分类；
- 将授权和审批做成确定性节点；
- 记录每次状态转移、模型版本、工具参数和审批结果；
- 评测正常路径、拒绝路径、超时、恢复和重复执行；
- 为死循环设置递归/步数上限；
- 图升级时验证在途 Thread 能否恢复。

## 35.10 优点、局限与适用场景

优点：

- 控制流和状态显式，易审计、调试和恢复；
- 可以自然混合确定性代码、模型和人工节点；
- 适合长运行、有分支、有中断的业务；
- 不强制特定 Prompt 或 Agent 架构。

局限：

- 状态和图设计需要较强工程能力；
- 节点增多后图可能演化为难维护的“面条图”；
- Checkpoint 不自动解决副作用幂等；
- 可观测平台、生产存储和权限仍需单独配置。

最适合：审批流、研究任务、长周期数据处理、复杂客服流程、需要故障恢复的 Coding Agent，以及跨多个确定性系统的企业 Agent。

## Summary

LangGraph 的关键思想是：Agent 本质上是一个随状态演进的计算过程。显式 Graph 让非确定性推理受到确定性控制，让暂停、恢复和审计成为运行时能力。

本章 MVP 故意不使用 LLM，因为理解 `State + Node + Edge + Checkpoint` 比先学会某个模型调用更重要。下一步可在保持授权节点不变的前提下，把理解和生成节点替换为真实模型。

## References

[1] LangChain. LangGraph Overview.
https://docs.langchain.com/oss/python/langgraph/overview

[2] LangChain. Graph API.
https://docs.langchain.com/oss/python/langgraph/graph-api

[3] LangChain. Persistence.
https://docs.langchain.com/oss/python/langgraph/persistence
