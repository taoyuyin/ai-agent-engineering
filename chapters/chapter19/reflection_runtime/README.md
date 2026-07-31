# Reflection Runtime MVP

依据错误类别选择 retry、repair arguments、replan、abort 或 escalate，并限制重试预算。

完整示例输入 TIMEOUT、INVALID_SCHEMA 和 PERMISSION_DENIED 三类 Observation，分别得到有限 retry、参数修复和立即终止。模型可以辅助分类复杂质量问题，但最终 action 只能来自 Runtime allowlist。

对应 Part II：Reasoning、Reflection、Structured Repair Decision 与 Token/Retry Budget。

```bash
python chapters/chapter19/example.py
python -m unittest discover -s chapters/chapter19 -p "test_*.py"
```
