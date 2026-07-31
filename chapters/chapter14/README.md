# Chapter 14 Planner：从目标到可修复的执行计划

Part III Agent Architecture —— Agent 内部如何工作

Version: 2026-07

Last Updated: 2026-07-31

## Core Question

Planner 应输出自然语言步骤还是可执行依赖图？什么时候预先计划，什么时候边执行边规划？

## Chapter Conclusion

Planner 的职责是把 Goal 转换为满足约束的可执行结构，并根据 Observation 更新未完成部分。计划不是模型思维链，而是 Runtime 可验证、可持久化的公共状态。

## Learning Objectives

- 理解 decomposition、dependency、ready queue 和 replan
- 比较静态、动态、分层与搜索式规划
- 设计结构化 Plan/PlanStep
- 防止循环依赖、无界计划和计划漂移
- 运行依赖图 Planner MVP

## 14.1 Plan 的最小结构

```text
Plan
├── plan_id / goal_version
├── steps[]
│   ├── step_id
│   ├── objective
│   ├── depends_on[]
│   ├── required_capability
│   ├── success_condition
│   └── status
└── budget / version
```

自然语言列表不能可靠表达依赖、并行、状态和重试。生产 Planner 应输出严格 schema，Runtime 再验证图结构和工具可用性。

## 14.2 Planning 策略横向对比

| 策略 | 何时生成计划 | 优点 | 缺点 | 适用 |
|---|---|---|---|---|
| Static Workflow | 开发期 | 可预测、易审计 | 无法应对未知情况 | 固定审批 |
| Plan-and-Execute | 运行开始 | 全局结构清晰 | 早期假设可能失效 | 报告、研究 |
| ReAct | 每步决策 | 适应反馈 | 容易局部贪心、步骤多 | 搜索与工具任务 |
| Hierarchical | 先里程碑再细化 | 适合大目标 | 状态与预算复杂 | Coding/Data Agent |
| Search / ToT | 多候选评分 | 可探索替代路径 | 成本高 | 高价值规划问题 |

默认应选择最简单的策略。确定流程用 Workflow；只在环境不确定时增加动态规划。

## 14.3 任务拆解原则

一个 Step 应：

- 只产生一种可验证结果；
- 输入依赖明确；
- 能映射到一个 capability 或子流程；
- 失败可分类；
- 粒度足够支持 checkpoint，但不过度碎片化。

“分析数据”太大；“查询华东月收入并验证数据新鲜度”更可执行。

## 14.4 Plan Validation

执行前检查：

1. step ID 唯一；
2. 依赖存在且无环；
3. 至少有 ready step；
4. required capability 可满足；
5. 权限和预算覆盖；
6. 每个 terminal path 都能得到 Goal evidence。

模型可以生成计划，不能绕过验证器。

## 14.5 Plan Update 与 Repair

Observation 到达后，Planner 只能修改未完成部分：

```text
failed step
  ├── transient → same step retry
  ├── invalid arguments → repair step input
  ├── missing capability → replace step/tool
  ├── wrong assumption → replan downstream
  └── policy denied → abort/escalate
```

已产生副作用的 Step 不应被简单删除。它需要补偿步骤或人工处置。

## 14.6 框架横向对比

| 工具 | 规划表示 | 动态性 | 持久化 | 适用 |
|---|---|---:|---:|---|
| LangGraph | graph/state/Command | 高 | checkpoint | 动态 Agent 图 |
| Google ADK Graph Workflow | graph route / dynamic workflow | 高 | session/runtime | Google Agent |
| OpenAI Agents SDK | Runner loop、handoff、agent-as-tool | 中高 | session/集成 | 模型驱动 orchestration |
| Temporal | code workflow + activities | 中 | Event History | 长期可靠流程 |
| Airflow | DAG + task dependency | 低至中 | metadata DB | 批处理与数据管道 |

Airflow 的 DAG 拓扑适合相对稳定的依赖；Agent 的动态步骤更适合状态图或在 Workflow Activity 内部运行。

## 14.7 业务案例：数据质量分析

Goal：定位订单收入下降原因。

```text
validate_metric_definition
        ↓
check_data_freshness
        ↓
query_revenue ───→ query_order_count
        └────────→ query_average_order_value
                         ↓
                   verify_explanation
```

如果新鲜度失败，后续查询不应执行；如果某一拆分维度样本过小，应调整下游计划而不是重跑全部步骤。

## 14.8 Python MVP

```bash
python chapters/chapter14/example.py
python -m unittest discover -s chapters/chapter14 -p "test_*.py"
```

MVP 实现依赖验证、循环检测、ready queue、完成与失败修复。它使用确定性输入，便于先理解 Planner contract，再接入模型。

## Production Checklist

- [ ] Plan 使用严格 schema 和版本
- [ ] 记录对应 goal_version
- [ ] 执行前检查依赖图、能力、权限和预算
- [ ] Step 有 success condition
- [ ] 只修改未完成的下游计划
- [ ] 副作用步骤使用补偿，不做盲目回滚
- [ ] 限制最大 step、深度、分支和 replan 次数

## Summary

Planner 不是让模型“想得更久”，而是把行动结构公开给 Runtime。可执行、可验证、可修复的计划，才是 Agent Architecture 中有价值的计划。

## Notes

Plan 内容可以由 LLM 生成，但 dependency validation、权限与预算检查应由确定性代码执行。

## References

[1] LangGraph, Workflows and agents.
https://docs.langchain.com/oss/python/langgraph/workflows-agents

[2] Google ADK, Template agent workflows.
https://adk.dev/agents/workflow-agents/

[3] Apache Airflow, DAGs.
https://airflow.apache.org/docs/apache-airflow/stable/core-concepts/dags.html

[4] Temporal, Workflows.
https://docs.temporal.io/workflows

以上 URL 已在 2026-07-31 核对。
