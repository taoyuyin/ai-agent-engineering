# Lifecycle Runtime MVP

显式建模创建、验证、规划、运行、等待和终态，并拒绝非法转移。

完整示例以销售分析 Run 为输入，依次执行 Goal 验证、规划、模型 usage 记录和完成判定。`max_steps` 控制 Agent 循环，`max_tokens` 控制模型消耗；任一预算超限都进入明确终态并留下事件。

对应 Part II：Token Budget、Context Checkpoint、Function Calling/MCP 的等待和恢复边界。

```bash
python chapters/chapter12/example.py
python -m unittest discover -s chapters/chapter12 -p "test_*.py"
```
