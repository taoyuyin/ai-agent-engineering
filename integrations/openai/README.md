# OpenAI Integration

当前状态：**Adapter 设计契约，尚无 Python 实现**。

## 目标接口

OpenAI Adapter 以 Responses API 为主要 Agent 接口，覆盖文本/结构化输出、Function Calling、Built-in Tools、Remote MCP、Streaming 和 Usage。具体 Model ID 通过 `OPENAI_MODEL` 配置，不写死在业务代码。

## 配置

| 变量 | 必需 | 说明 |
| --- | --- | --- |
| `OPENAI_API_KEY` | 是 | 由 Secret Manager 注入 |
| `OPENAI_MODEL` | 是 | 经过评测批准的模型路由 |
| `OPENAI_BASE_URL` | 否 | 代理或兼容网关地址 |
| `OPENAI_TIMEOUT_SECONDS` | 否 | 请求级超时 |

## 映射要求

- `instructions/input` 映射统一消息和 Context Section；
- Function Tool 保留 JSON Schema、严格模式和 Call ID；
- 遍历 Response Output Items，不假设第一项一定是文本；
- Tool Observation 使用对应 Call ID 回传；
- Structured Output 与 Tool Call 分开处理；
- 记录 Provider Request ID、Token Usage、Finish/Error 和模型实际版本；
- Hosted Tool 与 Client Tool 标注执行位置，避免重复执行。

## 安全边界

Built-in Tool 是否启用由服务端 Model Policy 决定。模型提出的自定义 Tool Call 仍需经过本仓库 Policy/Executor；API Key、完整敏感 Prompt 和未脱敏 Tool Result 不进入普通日志。

## 验收用例

1. 纯文本与结构化输出；
2. 单 Tool、多 Tool 和 Tool Error Round-trip；
3. Streaming 增量与取消；
4. Timeout、Rate Limit 和 Server Error 映射；
5. Usage 与 Trace 关联；
6. 未授权 Tool 即使被模型提出也不会执行。

官方资料：[OpenAI Using tools](https://developers.openai.com/api/docs/guides/tools)、[Responses API](https://developers.openai.com/api/docs/guides/migrate-to-responses)。
