# Observability Runtime MVP

本模块实现带父子关系、状态、耗时和脱敏的最小 Trace Recorder。

## 实现内容

- Context Manager 创建嵌套 Span；
- Trace ID、Span ID 和 Parent Span ID 关联完整链路；
- 异常自动标记 Error，Finally 保证 Span 落盘；
- 常见 Secret Key 在属性中被替换；
- 输出 JSON Trace 和基础 Metrics。

## 模型关系

模型调用只是一个 Span，应该记录 Model Route、Token、Cost 和 Request ID，但不默认记录私有推理或完整敏感 Prompt。

```bash
python chapters/chapter30/example.py
python -m unittest discover -s chapters/chapter30 -p "test_*.py"
```

生产实现映射到 OpenTelemetry，并增加 Sampling、Exporter、PII Policy 和 Business Outcome。正文见 [Chapter 30](../README.md)。
