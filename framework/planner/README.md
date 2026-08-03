# Planner

`planner/` 定义业务智能与 Runtime 控制面的三个 Port：`GoalCompiler`、`Planner` 和 `AnswerSynthesizer`。

## 职责

- Goal Compiler：把 `AgentRequest` 转换成 Objective、Success Criteria 和 Constraints；
- Planner：产生结构化 `ExecutionPlan`，声明 Tool、Arguments、Dependency 和 Scope；
- Answer Synthesizer：只消费标准化 Observation，返回 Answer 与 Evidence。

模型 Adapter、规则、Workflow 或领域算法都可以实现这些 Port。Runtime 不关心候选如何产生，只验证其结果。

## 确定性边界

Planner 不直接执行 Tool、不读取长期密钥、不推断调用者真实权限，也不能修改 `AgentRequest` 中的 Tenant 和 Scope。空 Plan、重复 Step、前向依赖和超出 Step Budget 会被 Runtime 拒绝。

## 扩展要求

新增业务 Planner 应测试：目标歧义、无解目标、权限不足候选、依赖顺序、预算和稳定输出 Schema。接入 LLM 时记录 Model/Prompt 版本，并保留可离线运行的 Fake 或规则实现。

调用链见 [`runtime/agent.py`](../runtime/agent.py)，教学原理见 Chapter 13、14 和 19。
