# Integrations

`integrations/` 是模型供应商与本教程 Runtime 之间的 Adapter 层。当前目录完成了接口设计与供应商映射，**尚未提供可导入的 Python Adapter**；核心 Runtime 仍使用确定性 Planner 和章节级框架示例。

## 统一目标

业务代码不应直接消费厂商 SDK Response。Adapter 把不同消息、工具和 Usage 格式归一化为稳定契约：

```text
ModelRequest
  model_route / instructions / input / tools / output_schema
  timeout / max_output_tokens / trace_context

ModelResponse
  text / structured_output / tool_calls / usage
  finish_reason / provider_request_id / raw_metadata
```

Tool Call 只是一项提案。Adapter 解析并验证基础结构，`framework/` 的 Registry、Policy 和 Executor 决定是否执行。

## 供应商矩阵

| Adapter | 原生接口重点 | 必须归一化的差异 | 文档 |
| --- | --- | --- | --- |
| [OpenAI](openai/README.md) | Responses、Tools、Structured Output | Output Items、Tool Call、Usage | 官方 OpenAI Docs |
| [Anthropic](anthropic/README.md) | Messages、Content Blocks、Tool Use | `tool_use/tool_result`、stop reason | Claude Platform Docs |
| [Google](google/README.md) | Gemini Tools / Function Calling | Function step/part、SDK 自动循环 | Google AI Docs |
| [Ollama](ollama/README.md) | Local Chat、Format、Tool Calls | 本地模型能力与加载状态 | Ollama Docs |
| [vLLM](vllm/README.md) | OpenAI-compatible Serving | 模型模板、Parser、服务参数 | vLLM Docs |

## Adapter 责任

- 从环境或 Secret Provider 创建客户端，不记录 Key；
- 将统一 Tool Schema 转成厂商格式；
- 保留 Call ID，正确回传 Observation；
- 归一化 Input/Output/Cached Token 与延迟；
- 处理 Streaming、Timeout、Rate Limit、Retry-After 和取消；
- 保存 Provider Request ID 和可脱敏元数据；
- 把拒绝、长度终止和协议错误映射为稳定错误类型。

## Adapter 不负责

- 业务身份和权限；
- 是否允许执行某个 Tool；
- 自动重试写操作；
- 把 Provider Conversation 当作唯一 Memory；
- 选择业务指标或验证最终 Evidence。

## 实现完成标准

每个 Provider 加入代码时必须同时提交：独立 requirements、`.env.example`、Fake Client 单测、Tool Round-trip、Structured Output、Streaming/Cancel、Usage、错误映射和最小真实 API Smoke 指南。模型名称由配置提供，不在 Runtime 中硬编码“最新模型”。

## 选择建议

先用统一 Eval Dataset 比较任务成功率、安全、延迟和成本，再决定路由。OpenAI-compatible 只表示部分 HTTP 形状兼容，不代表 Tool、Reasoning、Streaming、Usage 或错误语义完全一致。
