# Chapter 20 State Machine：Agent 为什么本质上是状态转换系统

Part III Agent Architecture —— Agent 内部如何工作

Version: 2026-07

Last Updated: 2026-07-31

## Core Question

模型输出具有概率性，为什么 Agent Runtime 仍应使用确定性状态机？状态、事件、转移和 checkpoint 如何组合？

## Chapter Conclusion

Agent 的决策内容可以是概率性的，但执行控制必须是显式状态转换。状态机规定当前允许发生什么，事件记录实际发生了什么，持久化让系统可以恢复和审计。

## Learning Objectives

- 区分 State、Event、Command、Transition 与 Side Effect
- 理解 reducer、checkpoint 和 event replay
- 设计状态不变量与乐观并发
- 比较状态图、事件溯源和 durable workflow
- 运行事件重放 State Machine MVP

## 20.1 状态机模型

```text
Current State + Event
        ↓ reducer / transition table
New State + Commands
        ↓ executor
External Side Effects
        ↓
New Events
```

- **State**：当前已知事实快照；
- **Event**：不可变的已发生事实；
- **Command**：希望执行的动作；
- **Transition**：哪些事件在当前状态合法；
- **Side Effect**：数据库、网络、文件等外部变化。

不要把模型自然语言输出直接当 State；先解析为 Command，再经 Policy 和 Transition 验证。

## 20.2 推荐状态

```text
Created → Planning → Ready → Running
                         ↑       ↓
                     Observation
                         ↓
                  Waiting / Repairing
                         ↓
             Completed / Failed / Cancelled
```

状态数量不宜过少，否则 `running` 包含一切；也不宜复制每个 Prompt 细节。状态应服务于恢复、查询和策略。

## 20.3 State Invariants

示例不变量：

- Completed 必须存在通过验证的 evidence；
- tool_requested 必须对应 allowed tool；
- Waiting Approval 必须有 pending approval ID；
- 同一 idempotency key 只能成功一次；
- tenant_id 在整个 Run 中不可被模型修改；
- terminal state 不接受新执行事件。

不变量由代码维护，不由 Prompt 约定。

## 20.4 Persistence 策略

| 策略 | 保存方式 | 优点 | 局限 |
|---|---|---|---|
| Snapshot | 定期完整状态 | 恢复快 | 历史和审计较弱 |
| Event Sourcing | 不可变事件流 | 完整审计、可重放 | reducer/version 复杂 |
| Checkpoint + Log | 快照加增量事件 | 平衡恢复与审计 | 两套一致性 |
| Workflow History | 引擎记录命令/事件 | durable replay | 要遵守确定性限制 |

事件流增长后可做 snapshot，但原始审计保留策略要符合合规要求。

## 20.5 并发与幂等

两个 worker 同时恢复一个 Run 会重复执行。常见控制：

- optimistic version / expected sequence；
- lease/lock；
- inbox 去重；
- idempotency key；
- transactional outbox；
- single-writer per run。

仅靠“先查状态再执行”存在竞态。

## 20.6 工具横向对比

| 工具 | 状态模型 | 恢复机制 | 特点 |
|---|---|---|---|
| LangGraph | typed state + graph | checkpoint/replay | Agent 状态图 |
| Temporal | deterministic workflow state | Event History replay | 长期可靠执行 |
| Prefect | flow/task states | server tracking/retry | Python workflow |
| XState | finite/statecharts | snapshot/persistence adapter | 前端与通用状态机 |
| 自研 Event Store | event + reducer | replay/snapshot | 完全控制、维护成本高 |

LangGraph 更接近 Agent state graph；Temporal 更接近 durable execution substrate。二者可以集成。

## Part II 能力在本章中的应用

模型、Function Calling 和 MCP 都只能产生事件候选，不能直接修改状态：

```text
Model Command / ToolResult / MCP Error
        ↓ validate and classify
Domain Event
        ↓ legal transition + invariant
New State + Checkpoint
```

Context 从 checkpoint 投影，而不是把聊天记录当状态；token usage、tool call ID 和 model version 作为 event metadata 保存；Reasoning 可以建议下一事件，但 State Machine 决定是否合法。

本章示例用不可变事件、合法转移、expected sequence 和 replay，展示如何把非确定模型装入确定状态边界。

## 20.7 业务案例：退款 Agent

```text
Requested
  ↓ policy_passed
Approved
  ↓ gateway_submitted
Processing
  ↓ gateway_confirmed
Completed
```

如果进程在 gateway 已扣款但事件未落库时崩溃，恢复后可能重复退款。必须让 gateway 使用 idempotency key，并通过对账事件修复不确定状态。

## 20.8 Python MVP

```bash
python chapters/chapter20/example.py
python -m unittest discover -s chapters/chapter20 -p "test_*.py"
```

MVP 用 transition table 校验事件、EventStore 追加不可变序号、expected sequence 防并发，并通过 reducer replay 重建状态。

## Production Checklist

- [ ] 状态和事件 schema 版本化
- [ ] 所有转移有显式合法表
- [ ] terminal state 不可继续执行
- [ ] 不变量由代码检查
- [ ] 单 Run 有并发控制
- [ ] 外部副作用使用幂等键
- [ ] reducer 支持历史事件版本迁移
- [ ] checkpoint、审计和数据保留策略明确

## Summary

状态机不是限制 Agent 智能，而是限制不可控执行。模型可以提出下一动作，Runtime 只接受当前状态下合法且授权的事件。

## Notes

Event Sourcing 不是所有 Agent 的必选项。简单系统可使用事务状态表加审计日志，但仍要保留合法转移和并发控制。

## References

[1] LangGraph, Persistence.
https://docs.langchain.com/oss/python/langgraph/persistence

[2] Temporal, Workflow replay.
https://docs.temporal.io/workflows

[3] Prefect, States.
https://docs.prefect.io/v3/concepts/states

以上 URL 已在 2026-07-31 核对。
