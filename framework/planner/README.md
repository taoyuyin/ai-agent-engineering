# Planner

`core.py` 定义 Goal Compiler、Planner 和 Answer Synthesizer 三个端口。

- Goal Compiler 将用户目标转换为完成标准与约束。
- Planner 产生结构化 `ExecutionPlan`，不直接调用工具。
- Answer Synthesizer 只消费标准化 Observation，并返回答案与 Evidence。

业务 Agent 实现这些端口；Runtime 负责验证 Plan。
