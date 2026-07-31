# Chapter 34 OpenAI Agents SDK

Part V Frameworks —— 主流 Agent 框架设计

Version: 2026-07

Last Updated: 2026-07-31

## 本章结论

OpenAI Agents SDK 的核心价值不是提供更多“魔法”，而是用少量 Python 原语封装常见 Agent Loop：模型推理、工具调用、Handoff、Guardrail、会话和 Trace。

它适合快速构建以 OpenAI 模型能力为中心的 Agent 服务。当业务需要完全显式的状态机、跨天恢复或复杂人工审批时，应在 SDK 外增加持久化 Workflow，或选择 LangGraph 一类图运行时。

## 学习目标

完成本章后，你应该能够：

- 解释 `Agent`、`Runner`、Tool、Handoff、Guardrail 和 Trace 的职责；
- 理解 SDK 如何把一次模型调用扩展成受控 Agent Loop；
- 使用类型化上下文、函数工具和结构化输出实现最小可运行 Agent；
- 判断 OpenAI Agents SDK、Responses API 和显式 Workflow 的边界；
- 为企业场景补齐权限、幂等、审计、评测和持久化能力。

## 34.1 它解决的不是模型调用，而是运行循环

直接调用模型通常只有一轮：

```text
messages -> model -> text
```

Agent 则需要反复判断：

```text
用户目标
  -> 模型决定调用工具
  -> 运行时校验并执行工具
  -> 工具结果进入上下文
  -> 模型继续推理
  -> 得到结构化结果、Handoff 或异常
```

自己实现这条循环并不难，难的是稳定处理工具参数、最大轮数、异常、会话历史、结构化输出、敏感数据和 Trace。OpenAI Agents SDK 把这些通用机制放进 `Runner`，让应用代码聚焦 Agent 定义和业务边界。

## 34.2 核心抽象

| 抽象 | 职责 | 企业工程中的对应物 |
| --- | --- | --- |
| `Agent` | 定义模型、指令、工具、输出类型和 Handoff | Agent 配置与能力边界 |
| `Runner` | 驱动模型与工具循环，直到产生最终结果 | Runtime / Executor |
| Function Tool | 把 Python 函数及其 Schema 暴露给模型 | Tool Registry + Adapter |
| Handoff | 把当前任务交给另一个专业 Agent | 路由与任务委派 |
| Guardrail | 在输入、输出或工具边界执行检查 | 安全策略与验证器 |
| Context | 向工具传递不应暴露给模型的依赖和身份 | Request Scope / DI Container |
| Session | 保存同一会话的历史 | Working Memory |
| Trace | 记录模型、工具、Handoff 等 Span | Observability |

一个容易混淆的点是：`instructions` 是给模型看的，`context` 是本地 Python 对象。用户身份、数据库连接和权限集合应放在 Context 中，由工具执行时检查，不能只写在 Prompt 里。

## 34.3 从源码抽象理解 Runner

从架构视角，可以把 `Runner.run` 理解成以下伪代码：

```python
for turn in range(max_turns):
    response = call_model(agent, history, tool_schemas)
    if response.has_handoff:
        agent = resolve_handoff(response)
    elif response.has_tool_calls:
        observations = execute_validated_tools(response.tool_calls, context)
        history.extend(observations)
    else:
        return validate_output(response, agent.output_type)
raise MaxTurnsExceeded()
```

真正的 SDK 还会处理并行工具、生命周期 Hook、Guardrail、会话和 Trace。这个简化版本揭示了两个重要事实：

1. Agent 的自主性仍被工具集合、Schema、最大轮数和代码权限所约束；
2. SDK 管理的是一次运行循环，不等于天然拥有业务级长事务和故障恢复。

## 34.4 Tool：Schema 只是入口，授权必须在执行点

`@function_tool` 会根据函数签名和 Docstring生成工具 Schema。模型看到的是工具名称、说明和参数，而不是函数内部实现。

本章示例中的权限校验发生在工具内部：

```python
@function_tool
def query_sales(
    context: RunContextWrapper[RequestContext],
    year: int,
    region: str | None = None,
) -> str:
    if "sales:read" not in context.context.scopes:
        raise PermissionError("sales:read scope is required")
    ...
```

这条边界非常关键。Prompt 中的“只能读取授权数据”是行为提示，工具内的 Scope 校验才是安全控制。真实系统还应在查询层追加 `tenant_id` 过滤，避免 Agent 通过参数绕过租户隔离。

## 34.5 Handoff 与 Agent-as-Tool

多 Agent 组合通常有两种语义：

- **Handoff**：当前 Agent 把对话控制权交给专业 Agent，后续由新 Agent 面向用户；
- **Agent-as-Tool**：编排 Agent 调用专业 Agent 获取一个结果，然后继续持有控制权。

客服分流适合 Handoff；“主报告 Agent 调用税务分析 Agent 计算一项指标”更适合 Agent-as-Tool。选型关键不是 Agent 数量，而是谁拥有最终控制权、上下文和响应责任。

## 34.6 Guardrail 的边界

Guardrail 可用于：

- 输入分类：拒绝越权或不支持的任务；
- 输出验证：检查必需字段、敏感信息和业务规则；
- 工具检查：限制高风险参数和操作。

但 Guardrail 不应取代底层系统权限。数据库行级权限、API IAM、支付审批和密钥隔离必须由确定性系统执行。推荐采用四层防线：

```text
输入策略 -> Agent 能力白名单 -> Tool 执行点授权 -> 输出检查与审计
```

## 34.7 最小可运行 MVP：受治理的销售分析 Agent

本章代码实现同一套 Part V 基准业务：

> 用户查询 2025 年各区域净销售额；Agent 必须调用受权限保护的工具，并返回带证据源的结构化结果。

目录：

```text
chapter34/
├── README.md
├── example.py
├── requirements.txt
└── .env.example
```

安装与运行：

```bash
cd chapters/chapter34
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
export OPENAI_API_KEY="<your-api-key>"
python example.py "查询 2025 年各区域净销售额"
```

关键工程点：

- `RequestContext` 保存租户、操作者和 Scope；
- `query_sales` 在执行点校验 `sales:read`；
- `SalesReport` 约束最终输出，不让下游解析自由文本；
- `evidence_sources` 强制保留数据血缘；
- `max_turns=6` 防止失控循环；
- 模型名通过环境变量注入。

本地数据集是为了让示例聚焦框架机制。接入生产数据库时，应替换 Tool 内部实现，而不是把 SQL 权限交给模型。

## 34.8 与 Responses API、LangGraph 的选择

| 方案 | 适用场景 | 你需要自己负责 |
| --- | --- | --- |
| Responses API | 单轮或自行控制的少量工具调用 | Agent Loop、状态、路由和 Trace 组织 |
| OpenAI Agents SDK | 快速构建工具型、Handoff 型 Agent | 业务持久化、领域权限和上线治理 |
| LangGraph | 显式分支、恢复、审批和复杂状态机 | 更多图设计、状态 Schema 和运行维护 |

经验法则：

- 一个 Agent、几个工具、运行时较短：先使用 Agents SDK；
- 流程要求可视化节点、确定性分支和断点恢复：考虑 LangGraph；
- 只有一次结构化模型调用：Responses API 已足够。

不要为了“框架统一”把所有业务都变成 Agent。确定性强、失败成本高的业务步骤仍应由普通服务或 Workflow 驱动。

## 34.9 生产化清单

MVP 上线前至少补齐：

- 将 API Key 放入 Secret Manager；
- 为每个 Tool 定义超时、重试、幂等键和错误分类；
- Context 从真实认证信息构造，禁止客户端伪造 Scope；
- 敏感数据进入 Trace 前脱敏，明确 Trace 保留周期；
- 持久化会话时区分原始消息、业务状态和可丢弃缓存；
- 对高风险工具增加人工审批；
- 用固定数据集评测工具选择率、事实准确率和越权率；
- 对模型、Prompt、工具 Schema 和评测集做版本管理。

## 34.10 优点、局限与适用场景

优点：

- 原语少，学习和落地成本低；
- Python 函数工具和结构化输出结合自然；
- Handoff、Session、Guardrail 和 Trace 是一套一致的运行模型；
- 适合 OpenAI 模型能力的快速集成。

局限：

- 复杂长流程仍需外部 Workflow 或持久化层；
- 对完全显式状态转换的表达不如图框架；
- 企业权限、数据治理和业务补偿不会由 SDK 自动解决；
- 深度依赖供应商特性时，迁移需要适配。

最适合：客服路由、企业助理、工具型知识 Agent、短周期分析 Agent，以及希望以较少代码获得完整运行循环的团队。

## Summary

OpenAI Agents SDK 把 Agent Loop 收敛为 `Agent + Runner + Tool`，再以 Handoff、Guardrail、Session 和 Trace 补齐协作与治理。它降低了运行时样板代码，但不会替代业务权限、持久化 Workflow 和生产治理。

本章 MVP 展示的核心不是“模型会查数据”，而是模型只能通过授权工具获取事实，并以可验证结构输出。这个边界也是后续七个框架的统一比较基准。

## References

[1] OpenAI. OpenAI Agents SDK Documentation.
https://openai.github.io/openai-agents-python/

[2] OpenAI. Agents.
https://openai.github.io/openai-agents-python/agents/

[3] OpenAI. Tools.
https://openai.github.io/openai-agents-python/tools/

[4] OpenAI. Running Agents.
https://openai.github.io/openai-agents-python/running_agents/

[5] OpenAI. Guardrails.
https://openai.github.io/openai-agents-python/guardrails/

[6] OpenAI. Tracing.
https://openai.github.io/openai-agents-python/tracing/
