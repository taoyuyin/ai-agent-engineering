# Chapter 21 Workflow Engine：为 Agent 提供确定性骨架

Part III Agent Architecture —— Agent 内部如何工作

Version: 2026-07

Last Updated: 2026-07-31

## Core Question

Agent 已经有 Planner 和状态机，为什么还需要 Workflow Engine？DAG、事件驱动、durable execution 和 Human-in-the-loop 分别解决什么？

## Chapter Conclusion

Workflow Engine 管理确定性依赖、重试、等待、调度和恢复；Agent 处理需要模型判断的不确定步骤。企业级架构通常将 Agent Step 嵌入 Workflow，而不是让整个业务流程都由模型自由决定。

## Learning Objectives

- 区分 Workflow Definition、Run、Task 和 Activity
- 理解 DAG、事件驱动与 durable replay
- 设计 Agent Step 和人工审批
- 横向比较 LangGraph、Temporal、Airflow、Prefect 与 Google ADK
- 运行带依赖、重试和审批门的 Workflow MVP

## 21.1 Workflow 与 Agent 的组合

```text
Deterministic Workflow
  validate request
        ↓
  Agent Step: analyze evidence
        ↓
  deterministic verifier
        ↓
  human approval
        ↓
  side-effect activity
        ↓
  audit and notify
```

模型只进入真正需要语义判断的节点。权限检查、付款、通知和审计继续使用确定性代码。

## 21.2 DAG

DAG 用有向无环图表示依赖：

- 节点是 Task；
- 边是依赖；
- 无环保证拓扑执行；
- 无依赖节点可并行；
- 上游失败影响下游策略。

DAG 适合拓扑相对稳定的流程。需要动态循环、等待与回边时，可使用状态图或支持循环的 workflow-as-code。

## 21.3 事件驱动

长流程经常等待：

- 人工审批；
- 文件上传；
- 外部系统 webhook；
- 定时器；
- 设备/订单状态；
- 子流程完成。

Engine 应持久化等待条件，事件到达后唤醒 Run。Polling 可以作为适配方式，但不应让 worker 长时间阻塞。

## 21.4 Durable Execution

Durable workflow 的关键不是“任务放队列”，而是进程崩溃后能根据历史恢复到一致状态。

Temporal 使用 Event History replay，要求 Workflow 决策确定性，并将网络、数据库、LLM 等副作用放入 Activity。Agent Step 作为 Activity 时，需要：

- 固定输入和输出 schema；
- timeout 与 retry policy；
- idempotency；
- token/费用预算；
- trace 与 workflow ID 关联。

## 21.5 Human-in-the-loop

人工审批对象应包含：

- Run 与 Step；
- 建议动作和关键参数；
- 证据与来源；
- 风险和预期副作用；
- approve/reject/edit 选项；
- 过期时间与审批权限。

恢复后必须重新检查业务对象是否变化，避免批准旧快照。

## 21.6 工作流工具横向对比

| 工具 | 核心模型 | 动态循环 | Durable | 调度 | Agent 适配 |
|---|---|---:|---:|---:|---|
| LangGraph | state graph | 强 | checkpoint | 弱 | 原生 Agent |
| Temporal | workflow + activity | 强 | 强 | 支持 | 适合承载 Agent Activity |
| Airflow | DAG + operator/task | 有限 | task retry/state | 强 | 适合批量 Agent Job |
| Prefect | Python flow + task | 强 | state/retry | 强 | Python 集成自然 |
| Google ADK Graph Workflow | graph routes | 强 | Runtime 能力 | 面向 Agent | 原生 ADK |
| OpenAI Agents SDK | Runner loop | 强 | 通过 integrations | 非主定位 | Agent Step |

选型先看任务生命周期和恢复要求，再看模型 SDK。

## 21.7 业务案例：月度经营报告

```text
freeze_data_snapshot
       ↓
validate_metrics
       ↓
parallel: sales_agent / service_agent / inventory_agent
       ↓
merge_and_verify
       ↓
finance_approval
       ↓
publish_report
```

数据冻结、审批和发布是 Workflow；各领域分析可以是 Agent Step。重跑分析不应重复发布。

## 21.8 Python MVP

```bash
python chapters/chapter21/example.py
python -m unittest discover -s chapters/chapter21 -p "test_*.py"
```

MVP 实现依赖执行、共享状态、有限重试和 approval gate。审批前 `publish` 保持 pending，批准后继续运行。

## Production Checklist

- [ ] 确定性步骤与 Agent Step 分离
- [ ] Workflow/Task 输入输出 schema 版本化
- [ ] 等待状态不占 worker
- [ ] Retry 与业务补偿分开
- [ ] Side effect 使用幂等与 outbox
- [ ] 审批绑定证据、参数和版本
- [ ] Agent trace 关联 workflow/run/task ID
- [ ] 支持取消、超时、恢复和重放测试

## Summary

Workflow Engine 提供业务确定性，Agent 提供局部适应性。把边界画对，比选择某个热门框架更重要。

## Notes

Airflow 适合计划型数据任务；Temporal 更强调长期 durable execution；LangGraph 专注 Agent 状态图。它们可能同时出现在一个企业平台。

## References

[1] Temporal, Workflows.
https://docs.temporal.io/workflows

[2] Apache Airflow, DAGs.
https://airflow.apache.org/docs/apache-airflow/stable/core-concepts/dags.html

[3] Prefect, Flows.
https://docs.prefect.io/v3/concepts/flows

[4] LangGraph, Persistence.
https://docs.langchain.com/oss/python/langgraph/persistence

[5] Google ADK, Workflow agents.
https://adk.dev/agents/workflow-agents/

以上 URL 已在 2026-07-31 核对。
