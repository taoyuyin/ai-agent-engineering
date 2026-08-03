# Examples

`examples/` 保存跨章节的完整业务工程。Chapter MVP 验证单一抽象；Example 必须展示一次从用户输入、模型/Planner、Tool、Policy、Observation、Evidence 到服务部署的完整交互。

## 当前状态

| 案例 | 状态 | 当前入口 | 重点 |
| --- | --- | --- | --- |
| [SQL Agent](sql-agent/README.md) | 已实现 | `python examples/sql-agent/main.py` | Runtime、SQL、Scope、Evidence、API、Docker |
| [Data Agent](data-agent/README.md) | 设计契约 | Chapter 43 MVP | 数据质量、分析、报告 |
| [RAG Agent](rag-agent/README.md) | 设计契约 | Chapter 26/46 MVP | ACL Retrieval、Citation |
| [Coding Agent](coding-agent/README.md) | 设计契约 | Chapter 45 MVP | Sandbox、Patch、Test、Approval |
| [Browser Agent](browser-agent/README.md) | 设计契约 | Chapter 52 MVP | Computer Use Harness、安全确认 |
| [Multi-Agent](multi-agent/README.md) | 设计契约 | Chapter 49 MVP | Registry、Delegation、Budget、Trace |

“设计契约”表示 README 已定义业务目标、架构和验收标准，但该目录尚无可运行工程；不能把章节 MVP 或未来文件结构描述为已经完成。

## 完整案例统一要求

每个已实现案例必须包含：

- 可验收业务问题，而不是通用聊天；
- 环境、依赖、配置和一条可复制运行命令；
- 模型在流程中的明确位置和离线替代方式；
- Identity、Tenant、Tool Scope、Guardrail 与人工审批；
- Trace、Evidence、错误、重试和恢复；
- 单元/契约测试、Eval Dataset 和质量门禁；
- API、容器、部署与生产升级边界。

案例复用 [`framework/`](../framework/README.md) 的稳定 Contract。厂商差异由 `integrations/` 隔离，业务包不能把模型 SDK 对象传播到 Runtime 核心。
