# Chapter 12 Agent 生命周期：一次运行如何开始、暂停、恢复和结束

Part III Agent Architecture —— Agent 内部如何工作

Version: 2026-07

Last Updated: 2026-07-31

## Core Question

一个目标进入 Agent 后经历哪些状态？Runtime 如何保证它不会无限执行、丢失状态或在失败后重复产生副作用？

## Chapter Conclusion

Agent 不是一次模型调用，而是一个有身份、有预算、有中间状态和终止条件的 Run。生命周期是所有 Planner、Tool、Memory、Reflection 和 Workflow 能力共同遵守的控制边界。

## Learning Objectives

- 区分 Agent、Run、Turn、Step 和 Tool Call
- 设计可暂停、恢复、取消的生命周期
- 建立终止条件、预算和失败语义
- 比较 Agent Runner、状态图与工作流引擎的生命周期
- 运行一个拒绝非法状态转移的 Python MVP

## 12.1 五个容易混淆的执行单位

| 概念 | 含义 | 示例 |
|---|---|---|
| Agent | 可复用的能力与策略定义 | Sales Analyst |
| Run | 为一个目标创建的执行实例 | 分析 7 月华东异常 |
| Turn | 一次模型决策回合 | 模型决定查询销售 |
| Step | Runtime 中可持久化的工作单元 | query_sales |
| Tool Call | 对外部能力的一次调用 | call-17 |

Agent 是定义，Run 才是运行状态的归属。生产系统必须为 Run 分配唯一 ID，并让所有模型调用、工具结果、审批与审计记录继承它。

## 12.2 推荐生命周期

```text
Created
  ↓
Validating ─────────────→ Failed
  ↓
Planning ───────────────→ Failed
  ↓
Running ←───────────────┐
  ├── Waiting Approval ─┤
  ├── Waiting Event ────┤
  ├── Completed         │
  ├── Failed            │
  └── Cancelled         │
```

- **Created**：只完成 Run 身份与输入落库。
- **Validating**：检查目标、身份、配额、风险与数据边界。
- **Planning**：生成或选择执行计划。
- **Running**：模型决策、工具调用和验证循环。
- **Waiting**：释放计算资源，等待人或外部事件。
- **Terminal**：Completed、Failed、Cancelled，默认不可再转移。

暂停不是“让线程睡眠”。可靠系统应持久化 checkpoint，释放 worker，并在事件到达后恢复。

## 12.3 终止条件

至少需要五类硬边界：

1. Success criteria 已满足；
2. 最大 turn/step 数；
3. token、费用和时间预算；
4. 连续失败或重复动作阈值；
5. 人工取消或策略拒绝。

“模型说任务完成了”只能作为候选信号。最终完成应由 Goal Evaluator 或业务验证器确认。

## 12.4 Failure、Cancel 与 Timeout

| 终态 | 含义 | 是否可从 checkpoint 重试 |
|---|---|---|
| Completed | 验收标准满足 | 通常不需要 |
| Failed | 系统无法在当前策略下完成 | 视错误类型 |
| Cancelled | 用户或策略主动终止 | 需显式重新启动 |
| Timed out | 时间预算耗尽 | 可归类为 Failed |

取消应传播到正在执行的工具，但工具未必支持真正中断。对付款、发信等副作用，还需要幂等键和执行后对账。

## 12.5 工具横向对比

| 层 | 工具 | 生命周期模型 | 持久化/恢复 | 适用 |
|---|---|---|---|---|
| Agent Runner | OpenAI Agents SDK | Runner 循环、tool、handoff、final output、max turns | Sessions/服务端状态；可集成 durable runner | OpenAI Agent 应用 |
| 状态图 | LangGraph | node、edge、interrupt、checkpoint | 原生 checkpoint 与 resume | 状态复杂 Agent |
| Agent Runtime | Google ADK | event loop、session、state、resume/cancel | Runtime 服务管理 | Google 生态 |
| Durable Workflow | Temporal | Workflow、Activity、Event History | 确定性 replay | 长任务与关键副作用 |
| Python Workflow | Prefect | flow run state、retry、timeout | 服务端跟踪状态 | 数据/业务流程 |

Agent Runner 管理模型循环，Workflow Engine 管理长期可靠执行。企业系统常将前者作为后者的一个 Activity，而不是二选一。

## Part II 能力在本章中的应用

生命周期是底层能力的总预算边界，而不是简单的状态枚举：

| 底层能力 | 生命周期中的应用 |
|---|---|
| Token | 输入、输出、累计 usage 与超限终止 |
| Context | 每个 Step 只读取当前 checkpoint 和必要上下文 |
| Reasoning | 规划和反思有次数、时间与费用上限 |
| Function Calling | 模型提出 tool call，Run 进入执行或等待状态 |
| MCP | 远程调用可能超时、断连，需要恢复和幂等 |

完整链路是 `request → validate → plan → context → model → tool/MCP → observation → evaluate → terminal`。示例中的 Run、step budget 和事件记录形成确定性外壳；生产实现还应把 token、deadline 和 cost usage 写入同一 Run Budget。

## 12.6 业务案例：采购审批 Agent

采购 Agent 生成供应商建议后必须暂停，等待预算负责人批准。正确设计：

- `run_id` 与采购单 ID 关联；
- 候选与证据在等待前落库；
- 等待状态不占用 worker；
- 审批事件包含 actor、decision、timestamp；
- 恢复时重新检查权限和采购单版本；
- 创建订单使用幂等键。

如果只在内存里 `input()` 等待，进程重启后就无法安全恢复。

## 12.7 Python MVP

```text
chapter12/
├── example.py
└── lifecycle_runtime/
    ├── runtime.py
    └── test_runtime.py
```

运行：

```bash
python chapters/chapter12/example.py
python -m unittest discover -s chapters/chapter12 -p "test_*.py"
```

MVP 建模合法转移、终态保护、step budget 与事件记录。生产实现需把事件与 checkpoint 写入持久化存储。

## Production Checklist

- [ ] Run、Turn、Step、Tool Call 均有稳定 ID
- [ ] 状态转移由 Runtime 验证
- [ ] 终止条件不依赖模型自述
- [ ] 等待释放 worker 并持久化 checkpoint
- [ ] 取消传播到下游，副作用具备幂等
- [ ] 恢复时重新校验身份、版本和策略
- [ ] terminal run 默认不可修改

## Summary

生命周期把概率性的模型循环装进确定性的运行边界。没有生命周期，Planner、Memory 和 Tool 只是函数集合；有了生命周期，它们才组成可恢复、可审计的 Agent Runtime。

## Notes

本章对比的是不同抽象层。OpenAI Agents SDK 与 LangGraph偏 Agent orchestration；Temporal、Prefect 偏 durable workflow，不能仅按 API 数量横向评价。

## References

[1] OpenAI Agents SDK, Running agents.
https://openai.github.io/openai-agents-python/running_agents/

[2] LangGraph, Persistence.
https://docs.langchain.com/oss/python/langgraph/persistence

[3] Temporal, Workflows.
https://docs.temporal.io/workflows

[4] Prefect, Flows.
https://docs.prefect.io/v3/concepts/flows

以上 URL 已在 2026-07-31 核对。
