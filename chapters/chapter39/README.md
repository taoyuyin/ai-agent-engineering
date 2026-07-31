# Chapter 39 PydanticAI

Part V Frameworks —— 主流 Agent 框架设计

Version: 2026-07

Last Updated: 2026-07-31

## 本章结论

PydanticAI 把 Agent 当作一个带依赖类型和输出类型的 Python 应用组件：`Agent[DepsT, OutputT]`。它的优势不是隐藏 Python，而是让依赖注入、工具参数、结构化输出、重试和测试保持类型安全。

它适合已有 Pydantic/FastAPI 工程体系、希望把 Agent 像普通服务一样开发的团队；复杂跨阶段 Workflow 仍需要 Graph、持久化执行集成或外部编排。

## 学习目标

完成本章后，你应该能够：

- 理解 `Agent` 的 `deps_type` 与 `output_type`；
- 使用 `RunContext` 向 Tool 注入数据库、身份和配置；
- 用 Pydantic Schema 验证最终结果；
- 区分输出重试、工具重试和基础设施重试；
- 将 PydanticAI Agent 集成进分层 Python 服务。

## 39.1 为什么类型是 Agent 的工程边界

模型输出本质上不可靠，而业务系统要求稳定 Contract。类型系统不能保证模型一定正确，却可以确保错误在进入下游之前被发现。

PydanticAI 的核心表达可以简化为：

```python
Agent[Dependencies, Output]
```

其中：

- Dependencies 是运行时资源，如 Repository、用户身份、HTTP Client；
- Output 是本次运行必须返回的领域对象；
- Tool 通过 `RunContext[Dependencies]` 访问依赖；
- Pydantic 完成解析和校验；
- 校验失败可触发受控重试。

这与传统分层架构高度一致：Agent 是应用服务，Tool 是 Port/Use Case，Repository 或 API Client 是 Adapter。

## 39.2 依赖注入，而不是全局变量

本章定义：

```python
@dataclass
class SalesRepository:
    tenant_id: str
    scopes: frozenset[str]
```

运行时传入具体实例：

```python
result = agent.run_sync(question, deps=repository)
```

Tool 从 Context 获取：

```python
@agent.tool
def query_sales(ctx: RunContext[SalesRepository], year: int) -> dict:
    return ctx.deps.query(year, None)
```

这种设计有四个好处：

- 每个请求拥有独立身份和租户；
- 测试时可注入 Fake Repository；
- Tool 不依赖隐式全局连接；
- 静态类型检查能发现依赖用错。

真实项目可以把多个依赖包装为 `AppDependencies`，但不要把所有系统 Client 都无差别暴露给每个 Agent。

## 39.3 输出类型是业务 Contract

示例的 `SalesReport` 要求：

- 年份；
- 摘要；
- 区域明细；
- 证据源。

模型输出缺字段或数值类型错误时，验证会失败。框架可以把错误反馈给模型进行修复，但重试不能无限：

- 输出重试用于修复格式或可解释的约束问题；
- 工具重试用于模型参数错误或可恢复 Tool 错误；
- 网络超时重试应由 HTTP/数据库 Client 按幂等规则处理；
- 业务拒绝不应伪装成重试。

“重试次数更多”不是可靠性。错误分类和上限才是可靠性。

## 39.4 Tool 的两种边界

Tool 可以只依赖模型参数，也可以通过 `RunContext` 读取依赖：

- 普通 Tool：纯函数、公开数据、无需请求上下文；
- Context Tool：需要身份、数据库、Feature Flag 或租户配置。

工具 Docstring 和参数类型会影响模型生成参数。参数应尽量使用领域语言，避免把任意 SQL、URL 或 Shell 命令作为自由字符串暴露。

对高风险 Tool，应先让 Agent 生成类型化“操作提案”，再由确定性代码校验和审批，最后执行。

## 39.5 Prompt、Validator 与业务规则

不同规则应放在不同层：

| 规则 | 推荐位置 |
| --- | --- |
| 写作风格、角色说明 | System Prompt |
| 输出字段和基本约束 | Pydantic Model |
| 跨字段业务规则 | Output Validator / 领域服务 |
| 身份和租户权限 | Dependency / Repository / API |
| 高风险操作批准 | Workflow / 审批服务 |

例如“报告必须包含证据源”可以由 Schema 强制；“只能读取本租户数据”必须由 Repository 强制。不要指望一个复杂 Prompt 同时承担所有规则。

## 39.6 最小可运行 MVP

本章示例包含：

- 类型化 `SalesRepository` 依赖；
- Repository 内的 Scope 校验；
- `RunContext` Tool；
- `SalesReport` 结构化输出；
- 独立的工具和输出重试上限；
- 环境变量模型配置。

安装与运行：

```bash
cd chapters/chapter39
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export OPENAI_API_KEY="<your-api-key>"
python example.py "查询 2025 年各区域净销售额"
```

要做隔离测试，可以构造不含 `sales:read` 的 Repository，确认调用被拒绝。要做单元测试，则注入一个 Fake Repository 返回固定行，不需要访问真实数据库。

示例的静态数据属于 Repository 内部。替换成 SQLAlchemy 或 HTTP Adapter 时，Agent、Tool Contract 和输出类型不需要改变。

## 39.7 在 Web 服务中的位置

推荐架构：

```text
FastAPI Endpoint
  -> authenticate request
  -> build AppDependencies
  -> run PydanticAI Agent
  -> validate domain output
  -> serialize response
```

不要创建一个携带请求状态的全局依赖对象。Agent 定义可以复用，但每次运行注入独立 Dependencies。

如果请求运行时间较长，应把执行交给任务队列或 Durable Workflow，HTTP 层返回任务 ID。PydanticAI Agent 负责某个推理阶段，不负责整个分布式事务。

## 39.8 与相邻方案对比

| 维度 | PydanticAI | OpenAI Agents SDK | LangGraph |
| --- | --- | --- | --- |
| 核心优势 | 类型、依赖注入、Python 工程体验 | 轻量 Agent Loop、Handoff、Trace | 显式状态、分支和恢复 |
| 模型取向 | 多提供商 | OpenAI 生态最自然 | 模型无关编排 |
| 状态机 | 可结合 Graph/持久化集成 | SDK Loop | 一等公民 |
| 输出约束 | `output_type` + Pydantic | `output_type` | 由节点/State 设计 |
| 适合团队 | Python 类型化后端 | 快速 OpenAI Agent | 复杂 Workflow 团队 |

如果问题主要是“如何让 Agent 成为可测试、类型安全的 Python 组件”，PydanticAI 很合适；如果主要是“复杂状态如何流转和恢复”，LangGraph 更直接。

## 39.9 生产化清单

- Dependencies 从认证后的服务端上下文构造；
- 为 Agent、Tool 输入和输出保留稳定类型；
- 区分模型修复重试与基础设施重试；
- Repository 执行租户隔离和最小权限；
- 用 Fake Model/Fake Dependencies 做确定性测试；
- 记录模型、Prompt、Tool Schema 与输出 Schema 版本；
- 对 PII 和 Trace 做脱敏；
- 长任务接入队列或 Durable Execution；
- 高风险操作使用提案—审批—执行模式；
- 评测结构合规率、事实准确率、工具选择率和越权率。

## 39.10 优点、局限与适用场景

优点：

- 与现代 Python 类型系统和 Pydantic 生态一致；
- 依赖注入让 Tool 易测试、易隔离；
- 结构化输出和重试语义清晰；
- 多模型适配，适合已有后端工程。

局限：

- 类型只能发现结构错误，不能自动保证事实正确；
- 复杂多 Agent Workflow 需要其他编排能力；
- 平台级 UI、知识库和应用发布不是其重点；
- 团队仍需设计状态、权限、可观测和部署。

最适合：类型化 Python API、企业内部工具、结构化数据 Agent、需要多模型适配的后端服务，以及重视测试与依赖注入的团队。

## Summary

PydanticAI 将 Agent 拉回熟悉的软件工程模型：显式依赖、类型化工具和受验证输出。它不消除模型不确定性，而是把不确定性限制在可校验边界内。

本章 MVP 的关键是 `SalesRepository -> RunContext -> Tool -> SalesReport` 这条类型链。生产化时可以替换底层 Adapter，而不破坏 Agent 的业务 Contract。

## References

[1] Pydantic. PydanticAI Agents.
https://ai.pydantic.dev/agents/

[2] Pydantic. PydanticAI Documentation.
https://ai.pydantic.dev/

[3] Pydantic. Durable Execution.
https://ai.pydantic.dev/durable_execution/
