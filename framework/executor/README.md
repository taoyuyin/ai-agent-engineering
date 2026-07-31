# Executor

`core.py` 在工具执行前验证 Pydantic 输入，并将成功或失败统一转换为 `ToolObservation`。

重试次数受到 Request 和 Step 预算约束。权限拒绝由 Policy 处理，不进入 Executor 重试。
