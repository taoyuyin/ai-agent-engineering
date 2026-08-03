# Observability

`trace.py` 提供 `InMemoryTraceSink`，按 Run 保存严格递增的结构化 `TraceEvent`。

## 当前事件

Runtime 会记录 Run Accepted/Failed/Completed、Goal Compiled、Plan Created，以及 Tool Started/Completed。每个事件包含 Sequence、Run ID、Timestamp、Type 和 Attributes。

## 使用边界

Trace 用于回答“发生了什么”，Evidence 用于回答“结论依据什么”，Memory 用于后续上下文。三者不能互相替代。Attributes 不应保存 API Key、Authorization、完整 PII 或不受控的大型 Tool Result。

## 生产扩展

OpenTelemetry Adapter 应传播 Trace Context，并输出关联的 Trace、Metric 和结构化 Log。建议增加 Model/Prompt/Tool/Policy/Data Version、Token、Cost、Cache、Retry、Approval 和 Business Outcome，同时实现采样、脱敏、访问与保留策略。

测试应验证顺序、Run 隔离和敏感字段处理。Chapter 30 的 `observability_runtime` 展示嵌套 Span、状态和属性脱敏。
