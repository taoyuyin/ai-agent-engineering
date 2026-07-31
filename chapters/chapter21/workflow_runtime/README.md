# Workflow Runtime MVP

实现依赖 DAG、状态传递、有限重试和人工审批暂停/恢复。

完整示例执行 query → draft → publish，前两步完成后在审批点暂停，批准后从持久状态继续。模型、Tool 或 MCP 调用都可以被包装为带输入快照、幂等键和 retry policy 的 Task。

对应 Part II：Context Snapshot、Reasoning Task、Function Calling/MCP 与 Human Gate。

```bash
python chapters/chapter21/example.py
python -m unittest discover -s chapters/chapter21 -p "test_*.py"
```
