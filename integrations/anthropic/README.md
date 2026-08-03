# Anthropic Integration

当前状态：**Adapter 设计契约，尚无 Python 实现**。

## 目标接口

Anthropic Adapter 使用 Messages API，将 Content Blocks、`tool_use`、`tool_result`、Server Tool 和 Usage 转换为统一 Runtime Contract。Model ID 由 `ANTHROPIC_MODEL` 配置。

## 配置

| 变量 | 必需 | 说明 |
| --- | --- | --- |
| `ANTHROPIC_API_KEY` | 是 | Secret 注入 |
| `ANTHROPIC_MODEL` | 是 | 评测批准的模型 |
| `ANTHROPIC_TIMEOUT_SECONDS` | 否 | 请求超时 |

## 映射要求

- 遍历全部 Content Blocks，区分 Text、Client Tool 和 Server Tool；
- `tool_use.id` 与下一轮 `tool_result` 严格配对；
- 根据 stop reason 决定继续 Tool Loop、完成或失败；
- Client Tool 由本地 Executor 执行，Server Tool 不重复执行；
- Tool Error 作为结构化结果返回，不拼进不可信自由文本；
- 记录 Input/Output Usage、Request ID 和模型版本。

## 安全与验收

Tool Schema 不等于权限；每个 Client Tool Call 仍经过 Scope、Risk、Budget 和 Approval。验收覆盖单/并行 Tool、严格 Schema、Tool Error、最大 Token、Streaming、Server Tool 与 Client Tool 混合回合。

官方资料：[Tool use with Claude](https://platform.claude.com/docs/en/agents-and-tools/tool-use/overview)、[Messages API](https://platform.claude.com/docs/en/api/messages/create)。
