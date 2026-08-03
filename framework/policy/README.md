# Policy

`engine.py` 是模型提案与 Tool 执行之间的确定性授权边界。

## 当前规则

`PolicyEngine.authorize()` 合并 `PlanStep.required_scopes` 和 `ToolDefinition.required_scopes`，检查调用者 Scope；Write Tool 额外要求 `agent:write`，Privileged Tool 要求 `agent:privileged`。

Policy 拒绝在 Tool Handler 运行前发生，权限失败不会进入 Executor Retry。

## 信任模型

`AgentRequest.scopes` 必须来自 API Gateway/IAM 验证后的服务端上下文，不能直接接受用户或模型自报权限。Prompt 只可帮助解释 Policy，不能决定授权。

## 生产扩展

生产 Policy Decision 应加入 Tenant、Resource、Action、Data Classification、Region、Purpose、Risk、Approval、Time 和 Quota，并返回结构化 `allow/review/block + reason + obligations`。高风险审批应绑定 Proposal Hash 和有效期。

测试至少覆盖缺少 Scope、写权限、特权权限和 Tool Handler 未被调用。对应 Chapter 28 和企业案例权限边界。
