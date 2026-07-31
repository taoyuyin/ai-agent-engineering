# Observation Runtime MVP

把供应商相关 Tool Result 归一化为有来源、大小边界、错误分类和信任标记的 Observation。

完整示例同时处理本地 Function Call 结果和 MCP 风格 `structuredContent/isError`，统一执行截断、错误分类、来源记录和 untrusted data 标记。

对应 Part II：Function Calling、MCP、Token/Context Result Budget。

```bash
python chapters/chapter18/example.py
python -m unittest discover -s chapters/chapter18 -p "test_*.py"
```
