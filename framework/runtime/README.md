# Runtime

`agent.py` 是 v0.1 的 Composition Root，连接 Goal、Plan、Policy、Registry、Executor、Memory、Trace 和 Answer。

## 完整流程

```text
AgentRequest
  → Run accepted/running
  → GoalCompiler
  → Planner + Plan Validation
  → per Step: dependency → registry → policy → executor
  → Observation → Memory + Trace
  → AnswerSynthesizer + Evidence
  → completed or failed
```

Plan Validator 检查非空、最大步数、Step 唯一和依赖必须指向已出现步骤。任一失败都会进入 Failed 并保留 Trace，然后异常返回调用方。

## 业务扩展点

业务包提供 `GoalCompiler`、`Planner`、`AnswerSynthesizer` 和 Tool Registry；Runtime 提供稳定契约与执行规则。厂商 SDK、SQL 语义和 UI 不应进入本模块。

## v0.1 限制

同步、单进程、内存状态；无持久 Checkpoint、Human Approval、并发 DAG 和 Provider Adapter。生产演进路线见 [`../ARCHITECTURE.md`](../ARCHITECTURE.md)，端到端用法见 SQL Agent。

对应 Chapter 12–23 的架构汇总。
