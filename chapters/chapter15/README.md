# Chapter 15 Tool：Agent 连接外部世界的能力边界

Part III Agent Architecture —— Agent 内部如何工作

Version: 2026-07

Last Updated: 2026-07-31

## Core Question

工具已经在 Chapter 10 定义，Runtime 还需要解决什么？当工具达到几十或几百个时，如何发现、选择、路由和治理？

## Chapter Conclusion

Tool 不只是一个 Python 函数，而是带 capability、schema、权限、成本、风险和运行策略的受治理能力。模型可以建议工具，Tool Runtime 决定哪些工具可见、可选和可执行。

## Learning Objectives

- 区分 Tool Definition、Registry、Selector、Router 与 Executor
- 设计 capability 与权限双重过滤
- 比较直接函数、框架工具、MCP 与 API Gateway
- 处理工具过多、命名冲突和路由失败
- 运行一个成本感知的 Tool Router MVP

## 15.1 Tool Control Plane

```text
Tool Catalog
  ↓ discovery / version / health
Policy Filter
  ↓ actor + tenant + scope
Capability Router
  ↓ quality + latency + cost
Model-visible Tool Set
  ↓ structured call
Execution Gateway
  ↓ validate + authorize + timeout
Observation
```

先过滤再交给模型，能减少 token、误选和越权风险。绝不能把所有工具交给模型，再希望它自觉不调用无权限工具。

## 15.2 Tool Metadata

除了输入 schema，还需要：

| 字段 | 作用 |
|---|---|
| capability tags | 与任务需求匹配 |
| required scopes | 执行授权 |
| read_only / side_effecting | 审批与重试策略 |
| cost / latency class | 路由与预算 |
| owner / version | 运维与兼容 |
| data classification | 数据治理 |
| health / rate limit | 可用性路由 |

Tool description 面向模型，metadata 面向 Runtime，两者不要混为一段自然语言。

## 15.3 Tool Selection 与 Routing

Selection 是“模型在可见工具中选哪个”；Routing 是“平台将 capability 映射到哪个实现”。

例如 `sales.read_summary` 可以路由到：

- 实时 API：新鲜但成本高；
- 数仓查询：延迟高但适合分析；
- 缓存：低延迟但可能陈旧。

Runtime 可按数据新鲜度、SLA、费用和健康状态选择实现，不必把底层差异暴露给模型。

## 15.4 工具规模问题

工具过多会带来：

- schema 占用 Context；
- 相似描述导致误选；
- 同名工具冲突；
- 低权限用户看到不应知道的能力；
- 每次请求都做全量检索。

常见解法：

1. 按领域预路由；
2. capability/tool search；
3. 延迟加载 schema；
4. 使用 namespace；
5. 根据身份构造临时可见集；
6. 对路由器单独评估 recall@k。

## 15.5 工具体系横向对比

| 方案 | 发现 | 路由 | 跨进程 | 治理重点 |
|---|---|---|---|---|
| Python Registry | 代码注册 | 自定义 | 否 | 简单、低开销 |
| LangChain Tools | decorator/schema/ToolNode | 模型或图 | 可适配 | 生态与错误处理 |
| OpenAI Agents SDK Tools | function/hosted/MCP/agent-as-tool | Runner | 是 | approval、trace |
| Google ADK Tools | function/OpenAPI/MCP 等 | Agent/Workflow | 是 | callback、确认与认证 |
| MCP | tools/list + tools/call | Host 聚合 | 是 | 互操作与信任 |
| API Gateway | OpenAPI/API catalog | 规则/服务路由 | 是 | 网络、认证、限流 |

MCP 是 AI-facing 协议，API Gateway 是服务控制面；企业通常将 MCP Server 放在 Gateway 与语义层之上。

## 15.6 Tool Result 不等于 Observation

Tool Result 是供应商或函数返回的原始数据；Observation 是 Runtime 归一化后的证据：

- 结果大小受限；
- 来源和时间明确；
- 错误可分类；
- 外部文本标记为不可信；
- 敏感字段被脱敏；
- 关联 call_id 和 step_id。

Chapter 18 会实现这层转换。

## Part II 能力在本章中的应用

当工具数量增加时，Embedding、Function Calling 与 MCP 分别承担不同责任：

```text
Goal → Embedding/Keyword Tool Search → Top-K Candidates
     → Scope/Risk/Health Filter → Model-visible Schemas
     → Function Call Proposal → Runtime Authorization
     → Local Function / API / MCP → ToolResult
```

Embedding 用于语义召回，不用于授权；Token/Context 决定暴露多少 schema；Function Calling 产生结构化提案；MCP 提供跨进程 discovery/call；Tool Gateway 在执行时重新验证 scope、tenant、schema 和副作用。

本章完整示例增加语义 Tool Discovery，同时保留 capability filter、成本路由、最小权限和执行时二次授权。

## 15.7 业务案例：多数据源销售查询

一个销售 Agent 有三种读取实现。Router 先检查 `sales:read`，再根据请求：

- “刚刚发生的订单” → 实时 API；
- “过去一年趋势” → 数仓；
- “首页概览” → 5 分钟缓存。

模型只看到统一的 `get_sales_summary`，避免将基础设施细节变成模型决策负担。

## 15.8 Python MVP

```bash
python chapters/chapter15/example.py
python -m unittest discover -s chapters/chapter15 -p "test_*.py"
```

MVP 按 capability、scope、read-only 与 cost 过滤和排序，并在真正调用时再次授权，体现“可见性过滤不替代执行授权”。

## Production Checklist

- [ ] Tool 有 owner、version、capability 和风险等级
- [ ] 可见工具集按身份与任务动态构造
- [ ] Router 有质量、延迟、成本和健康信号
- [ ] 执行时重新验证 scope 和 tenant
- [ ] 读写工具分离，副作用需要确认
- [ ] namespace 防止同名和 shadowing
- [ ] 评估路由 recall、误选率和降级行为

## Summary

Tool Engineering 的核心不是注册更多函数，而是让正确用户在正确目标下，以可控成本调用正确能力。

## Notes

Chapter 10 关注单次 Function Calling contract；本章关注大规模 Tool Catalog、选择、路由和治理。

## References

[1] OpenAI Agents SDK, Tools.
https://openai.github.io/openai-agents-python/tools/

[2] LangChain, Tools.
https://docs.langchain.com/oss/python/langchain/tools

[3] Google ADK, Custom tools.
https://adk.dev/tools-custom/

[4] MCP, Architecture.
https://modelcontextprotocol.io/docs/2026-07-28/learn/architecture

以上 URL 已在 2026-07-31 核对。
