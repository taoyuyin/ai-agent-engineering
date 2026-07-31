# Multi-Agent Runtime MVP

使用语义 Agent Discovery、capability card、最小 scope delegation、委派预算和 evidence contract 管理协作。

完整示例从任务目标召回 Data Agent，再以最小 `sales:read` scope 委派；子 Agent 必须返回 evidence，Coordinator 才能接受或解决冲突。

对应 Part II：Embedding Agent Discovery、Context Envelope、Structured Agent Call 与 Token/Fan-out Budget。

```bash
python chapters/chapter22/example.py
python -m unittest discover -s chapters/chapter22 -p "test_*.py"
```
