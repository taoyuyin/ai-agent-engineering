# Framework Tests

本目录保存跨组件 Runtime Contract Test，而不是单个业务 Agent 的测试。

`test_runtime.py` 使用 Echo Tool 验证：授权的 Plan 可以完成、Evidence 正确返回、Trace 最终产生 `run.completed`。组件级边界由后续测试逐步扩展。

## 必须覆盖的失败路径

- 无效 AgentRequest、空 Plan、重复 Step 和未知依赖；
- 未注册 Tool、参数 Schema 失败和 Retry 耗尽；
- Scope、Write 和 Privileged 权限拒绝；
- Tenant Memory 隔离；
- Failed Run 的 Trace 完整性；
- Evidence 只来自成功 Observation。

业务 Tool、数据和 API 测试放在 `examples/<agent>/tests/`。Provider Adapter 使用 Fake Client 做 Contract Test，真实 API 只做受控 Smoke Test。

开发命令见 [`../DEVELOPMENT.md`](../DEVELOPMENT.md)。
