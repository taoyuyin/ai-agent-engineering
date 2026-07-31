# State Machine Runtime MVP

用合法转移、不可变事件、乐观并发序号和 replay 重建 Agent 状态。

完整示例把 Goal、Plan、Tool Request、Tool Result 和 Completion 转换为事件，再通过 replay 重建终态。模型和 Function Call 只能提出事件，不能绕过 transition invariant 直接改状态。

对应 Part II：Structured Command、Function Calling/MCP Result 与 Context Checkpoint。

```bash
python chapters/chapter20/example.py
python -m unittest discover -s chapters/chapter20 -p "test_*.py"
```
