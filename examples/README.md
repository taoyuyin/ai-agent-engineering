# Examples

这里存放基于统一 `framework/` Agent Runtime 的完整业务案例。

- 问题背景
- 架构设计与 Runtime 组件映射
- 环境依赖、配置与运行方式
- 完整 Python 工程
- Tool、权限、Guardrail 和 Evidence
- 测试、评测与部署方式

## 当前参考实现

- [SQL Agent](sql-agent/README.md)：Schema、只读 SQL、权限、证据、Trace、FastAPI 和 Docker Compose

后续 Data Agent、RAG Agent、Coding Agent 等案例应复用 Runtime 契约，不再各自实现一套不兼容的 Agent Loop。
