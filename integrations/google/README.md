# Google Integration

当前状态：**Adapter 设计契约，尚无 Python 实现**。

## 目标接口

Google Adapter 面向 Gemini API 的 Function Calling 和工具能力。Google 文档同时存在不同调用表面，Adapter 实现时必须明确选择的 API/SDK 路径，并用 Contract Test 固定行为，不能混用不同响应结构。

## 配置

| 变量 | 必需 | 说明 |
| --- | --- | --- |
| `GEMINI_API_KEY` | 是 | Secret 注入 |
| `GOOGLE_MODEL` | 是 | 评测批准的模型 |
| `GOOGLE_TIMEOUT_SECONDS` | 否 | 请求超时 |

## 映射要求

- Function Declaration 从统一 JSON Schema 生成；
- 遍历全部 Step/Part，不依赖 Function Call 的固定位置；
- 保留 Function Call ID 及需要回传的上下文元数据；
- 区分 Google 执行的 Built-in Tool 和应用执行的 Custom Function；
- SDK 自动 Function Calling 仅用于受控低风险 Tool，企业 Runtime 默认保留手动执行边界；
- 归一化 Safety/Finish、Usage、Streaming 和 Provider Error。

## 安全与验收

覆盖单 Tool、并行/顺序 Tool、Structured Output、Safety Stop、Streaming、Context Continuation 和错误映射。高风险 Tool 不使用 SDK 自动执行，必须返回 Runtime 审批。

官方资料：[Gemini Function Calling](https://ai.google.dev/gemini-api/docs/function-calling)、[Using Tools](https://ai.google.dev/gemini-api/docs/tools)。
