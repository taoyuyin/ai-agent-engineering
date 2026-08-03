# Executor

`core.py` 负责在授权之后执行一个 Tool Step，并把成功或失败统一转换为 `ToolObservation`。

## 执行顺序

1. 根据 `ToolDefinition.input_model` 验证参数；
2. 调用只接收已验证对象的 Handler；
3. 记录 Attempt 和 Duration；
4. 将返回值封装为 Completed Observation；
5. 受控异常在预算内重试，耗尽后返回 Failed Observation。

Step 可以覆盖默认 Retry，但上限来自 Pydantic Contract。Schema、Value、Lookup 和受控 Runtime Error 会被归一化；进程级故障和取消需要生产执行器单独处理。

## 重要边界

Policy 拒绝发生在 Executor 之前。当前 v0.1 会重试部分 `ValueError/RuntimeError`，因此只适用于教学型只读或幂等 Handler；生产系统应按错误分类决定 Retry，并要求写操作提供 Idempotency Key。

生产扩展还应包括 Timeout、Circuit Breaker、Cancellation、Sandbox、Rate Limit、Artifact Store 和结构化错误码。对应 Chapter 15、18、19。
