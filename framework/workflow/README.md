# Workflow

`state_machine.py` 定义 Agent Run 的合法状态转换。

v0.1 使用进程内状态机；生产实现需要持久化 Checkpoint、幂等键、长任务恢复和 Human-in-the-loop 节点。
