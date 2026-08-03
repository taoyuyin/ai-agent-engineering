# Tools

`registry.py` 提供类型化 `ToolDefinition` 和 `ToolRegistry`。Tool 是模型可以提出调用的能力，不是模型拥有的权限。

## Tool Contract

每个 Tool 声明 `name`、`description`、Pydantic `input_model`、Handler、`required_scopes` 和 `risk`。`describe()` 只暴露模型选择所需的 JSON Schema 与治理元数据，Handler 保留在服务端。

## 注册与调用

1. 业务包定义输入模型和 Handler；
2. 启动时注册唯一名称；
3. Planner 只能引用 Registry 中存在的名称；
4. Policy 合并 Step 与 Tool Scope；
5. Executor 校验参数后调用 Handler；
6. 返回值被归一化为 `ToolObservation`。

## 安全边界

Tool Arguments 不能覆盖服务端 Tenant、Actor 或凭证；这些信息应通过受信上下文注入。写操作需要业务幂等键和补偿策略，不能依赖 Executor 自动重试保证安全。

生产 Adapter 可把 Registry 映射到 MCP 或远程 Tool Gateway，但仍要保留 Schema、Scope、Risk、Timeout、Rate Limit 和审计。对应 Chapter 10、11 和 15。
