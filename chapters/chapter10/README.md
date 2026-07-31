# Chapter 10 Function Calling：模型提出调用，Runtime 承担执行责任

Part II LLM Foundations —— Agent 为什么能够工作

Version: 2026-07

Last Updated: 2026-07-31

## Core Question

模型为什么能“调用工具”？JSON Schema、Structured Output、Tool Registry 和安全执行边界分别承担什么责任？

## Chapter Conclusion

模型并不会直接执行 Python 函数。它根据工具描述生成结构化调用意图，应用程序验证并执行真实函数，再把结果返回给模型。

JSON Schema 只能约束参数形状，不能证明调用安全、语义正确或用户有权限。企业级 Tool Runtime 必须独立完成授权、业务校验、隔离、幂等、审计和副作用审批。

## Learning Objectives

- 理解 Function Calling 的完整协议循环
- 区分 Tool Calling 与 Structured Output
- 设计供应商无关的 Tool Definition 和适配器
- 比较 OpenAI、Anthropic、Gemini 与 Agent 框架的工具机制
- 实现带 schema、权限和幂等控制的 Python Tool Runtime

## 10.1 模型没有跨越进程边界

完整流程是：

```text
Application → Model: user message + tool definitions
Model → Application: tool name + arguments + call id
Application: validate → authorize → execute → audit
Application → Model: tool result + matching call id
Model → Application: final answer or next tool call
```

模型产生的是建议执行的结构化数据。真正拥有数据库连接、文件权限和网络凭证的是应用 Runtime。

因此安全责任不能推给模型。

## 10.2 为什么需要 JSON Schema

自然语言参数有歧义：

```text
查询华东最近的销售
```

结构化参数可以是：

```json
{
  "region": "east",
  "start_date": "2026-07-01",
  "end_date": "2026-07-31",
  "limit": 20
}
```

Schema 定义类型、必填字段、枚举、范围和额外字段策略，使供应商、模型和 Runtime 共享一个接口契约。

推荐原则：

- 名称表达一个清晰动作；
- 描述说明何时使用和何时不能使用；
- 枚举替代模糊自由文本；
- 默认 `additionalProperties: false`；
- 读写工具分离；
- 返回值也定义稳定结构；
- 工具描述里不要放秘密或租户数据。

## 10.3 Structured Output 与 Tool Calling 的区别

| 能力 | Structured Output | Tool Calling |
|---|---|---|
| 目标 | 让模型输出符合 schema | 让模型选择动作并生成参数 |
| 是否必然执行外部代码 | 否 | 由 Runtime 决定 |
| 常见用途 | 抽取、分类、报告对象 | 搜索、数据库、发送消息 |
| 主要风险 | 字段语义错误、遗漏 | 权限、副作用、注入、重放 |

两者都能保证“形状更稳定”，但不能保证内容真实。例如 `amount: -100` 可能满足 number 类型，却违反业务规则。

## 10.4 Tool Contract 设计

一个领域层工具定义至少包括：

```text
ToolDefinition
├── name / description / version
├── input_schema / output_schema
├── required_scopes
├── side_effecting
├── timeout / rate_limit
├── idempotency_policy
└── data_classification
```

供应商适配器再把统一定义转换为具体 API 格式。这样权限和审计不会散落在 OpenAI、Anthropic、Google 三套代码中。

### 工具粒度

`run_sql(sql)` 很灵活，但攻击面大。对固定业务，更推荐：

```text
get_sales_summary(region, start_date, end_date)
```

它可以限定数据域、时间范围和行数。探索型 SQL Agent 则应配备只读账户、SQL AST 校验、查询成本限制和结果脱敏。

## 10.5 模型供应商横向对比

| 维度 | OpenAI | Anthropic Claude | Google Gemini |
|---|---|---|---|
| 工具定义 | function tool + JSON Schema | tool + input_schema | function declarations |
| 调用结果关联 | call id 对应 tool output | tool_use id 对应 tool_result | function call 与 function response |
| 并行/多次调用 | 支持，Runtime 需分别执行和回传 | 支持多个 tool_use block | 支持并行和组合式调用 |
| 强 schema 约束 | strict structured/function schema 能力 | strict tool use（支持的 Schema 子集） | 提供 function calling 模式和 schema |
| 工具选择控制 | auto/required/指定工具等 | auto/any/tool/none 等 | auto/any/none/validated 等，依 API |
| 主要注意点 | Responses 消息格式与旧接口不同 | tool_result 顺序和 block 结构需遵循协议 | SDK 自动调用和手动循环行为不同 |

供应商能力会演进，领域层不应硬编码某个当前模型名。应写契约测试验证：

- 必填、枚举、嵌套对象；
- 并行调用；
- 超长工具结果；
- 工具报错后重试；
- 多轮 call id 关联。

## 10.6 Agent 工具框架横向对比

| 框架 | 工具定义方式 | 优点 | 局限 | 适用 |
|---|---|---|---|---|
| LangChain / LangGraph | decorator、typed schema、ToolNode | 生态广、路由和错误处理方便 | 生产授权仍需自建 | 多供应商 Agent |
| PydanticAI | Python 类型与 Pydantic schema | 类型体验好、验证清晰 | 需理解框架运行时 | 强类型 Python 项目 |
| OpenAI Agents SDK | function tools、guardrail、trace | 与 OpenAI 工作流集成紧密 | 跨供应商需适配 | OpenAI 技术栈 |
| Google ADK | tool/function 与 Agent 抽象 | Gemini/Google 生态集成 | 跨云治理需额外层 | Google 生态 |
| 自研 Tool Runtime | 统一 contract + adapters | 权限、审计和版本可统一 | 建设成本高 | 企业平台 |

框架生成 schema 很有价值，但“能调用”与“能安全上线”之间还有一个执行控制面。

## 10.7 安全架构

```text
Model Tool Call
      ↓
Tool Name Allowlist
      ↓
Schema Validation
      ↓
Identity / Tenant / Scope Authorization
      ↓
Business Invariants
      ↓
Side-effect Approval + Idempotency
      ↓
Sandbox / Timeout / Rate Limit
      ↓
Sanitized Result + Audit Event
```

### 常见风险

| 风险 | 示例 | 控制 |
|---|---|---|
| Prompt Injection | 网页要求 Agent 删除文件 | 外部内容不可信、动作独立授权 |
| SQL Injection | 把模型文本拼接进 SQL | 参数化查询、AST、只读账户 |
| SSRF | 模型请求内网 metadata URL | 域名/IP allowlist、网络隔离 |
| Path Traversal | `../../secrets` | 工作目录沙箱、规范化路径 |
| 越权 | 普通用户查询全公司薪资 | actor/tenant/scope 检查 |
| 重复副作用 | 重试导致重复付款 | idempotency key、状态机 |
| 数据泄漏 | 把完整结果写入 trace | 脱敏、最小返回、日志分级 |

`strict: true` 不能解决其中任何授权问题。

## 10.8 业务案例：销售数据 Agent

需求：“查询华东本月销售额，并把异常门店发送给区域经理。”

应拆成两个工具：

- `get_sales_summary`：只读，`sales:read`；
- `send_anomaly_report`：有副作用，`report:send`，需要确认。

Runtime 首先验证 region、日期和 limit，再根据当前用户过滤租户数据。发送工具必须显示收件人和报告摘要，获得批准后使用幂等键执行。

如果把它们合成 `analyze_and_send(prompt)`，就很难对查询与发送分别授权和审计。

## 10.9 Python MVP：安全 Tool Runtime

目录：

```text
chapter10/
├── example.py
└── function_calling/
    ├── models.py
    ├── schema.py
    ├── registry.py
    ├── adapters.py
    └── test_function_calling.py
```

运行：

```bash
python chapters/chapter10/example.py
python -m unittest discover -s chapters/chapter10 -p "test_*.py"
```

MVP 实现：

- 统一 `ToolDefinition`；
- OpenAI、Anthropic、Google schema 适配示例；
- required、type、enum、min/max、额外字段校验；
- scope 和副作用审批；
- 基于 call id 的进程内幂等；
- 统一错误结果。

教学 validator 只实现 JSON Schema 子集。生产项目应使用成熟库，并将幂等结果放入持久化存储。

## 10.10 测试策略

至少覆盖：

- 合法调用；
- 缺失字段、额外字段、类型错误和边界值；
- 未知工具；
- 无 scope 与跨租户；
- 超时、限流和下游失败；
- 同一 call id 重放；
- 副作用审批拒绝；
- 工具结果包含恶意指令；
- 不同供应商适配器契约一致。

评估不能只看“最终答案是否好”，还要统计错误工具选择率、非法参数率、越权拦截率和副作用重复率。

## Production Checklist

- [ ] 工具 contract 有版本和 owner
- [ ] 输入和输出都验证
- [ ] actor、tenant、scope 在执行层检查
- [ ] 读写工具分开，副作用显式批准
- [ ] 超时、速率、并发和结果大小有限制
- [ ] 使用幂等键和补偿策略
- [ ] 秘密不进入模型上下文
- [ ] 错误信息脱敏但保留 reason code
- [ ] 所有调用有 audit id 和 evidence id

## Summary

Function Calling 把概率模型与确定性软件连接起来。模型负责提出结构化意图，Runtime 负责决定能否执行并承担安全责任。这条边界越清晰，Agent 越容易从 Demo 走向生产。

## References

[1] OpenAI, Function calling.
https://developers.openai.com/api/docs/guides/function-calling

[2] Anthropic, How tool use works.
https://platform.claude.com/docs/en/agents-and-tools/tool-use/how-tool-use-works

[3] Anthropic, Strict tool use.
https://platform.claude.com/docs/en/agents-and-tools/tool-use/strict-tool-use

[4] Google, Function calling.
https://ai.google.dev/gemini-api/docs/function-calling

[5] JSON Schema, Type-specific keywords.
https://json-schema.org/understanding-json-schema/reference/type

[6] LangChain, Tools.
https://docs.langchain.com/oss/python/langchain/tools

以上 URL 已在 2026-07-31 核对。
