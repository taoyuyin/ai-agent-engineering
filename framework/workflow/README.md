# Workflow

`state_machine.py` 定义 v0.1 Run 的合法生命周期：`accepted → running → completed/failed`。

## 当前行为

`RunStateMachine.transition()` 对非法转移 fail closed；Completed 和 Failed 是终态。模型无法通过返回某个字符串直接改变状态，所有转换由 Runtime 触发。

## 与 Planner 的区别

Plan 描述本次准备执行哪些业务 Step；Workflow/State Machine 决定这些 Step 在什么状态和控制规则下运行。动态规划不取消确定性生命周期。

## 当前限制与演进

v0.1 没有持久化、Waiting Approval、Cancel、Checkpoint 和 Replay。生产实现需要 Durable Event History、乐观并发、幂等、定时器、人工任务和补偿；外部 API/LLM 调用结果必须记录，重放时不能重新采样。

Chapter 20 展示事件重放，Chapter 21 展示 DAG 与人工暂停恢复。
