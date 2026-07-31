# Chapter 22 Multi-Agent：何时需要多个 Agent 协作

Part III Agent Architecture —— Agent 内部如何工作

Version: 2026-07

Last Updated: 2026-07-31

## Core Question

多个 Agent 是否天然优于单 Agent？如何设计通信、委派、权限、共享状态、冲突解决和终止条件？

## Chapter Conclusion

Multi-Agent 的价值来自能力边界、上下文隔离、并行和组织责任，而不是角色数量。没有明确委派契约和预算，多个 Agent 只会放大延迟、成本和错误传播。

## Learning Objectives

- 判断何时应使用单 Agent、agent-as-tool、handoff 或 team
- 设计 Agent Card 与 Task Envelope
- 实施最小权限 delegation 和 evidence contract
- 比较 OpenAI、LangGraph、Google ADK、AutoGen、CrewAI
- 运行 capability-scoped Coordinator MVP

## 22.1 先问：为什么不能用一个 Agent

需要 Multi-Agent 的合理信号：

- 不同领域需要隔离 Prompt、工具和数据权限；
- 子任务可安全并行；
- 一个 Agent 的工具集合过大；
- 责任需要独立审计；
- 子任务有明确输入输出；
- 不同模型/成本策略适合不同角色。

“模仿公司里的五个职位”不是充分理由。

## 22.2 四种协作模式

| 模式 | 控制权 | 适用 |
|---|---|---|
| Router → Specialist | Router | 领域分流 |
| Agent as Tool | 调用方保留 | 有界子任务 |
| Handoff | 接收方接管 | 对话责任转移 |
| Supervisor/Team | 协调者 | 多步骤协作与汇总 |

优先从 agent-as-tool 开始，因为调用者保留 Goal 和终止权。Handoff 需要明确传递哪些历史、权限和未完成责任。

## 22.3 Agent Card

Agent 能力不应只由名字描述：

```json
{
  "agent_id": "sales-analyst",
  "capabilities": ["sales", "analysis"],
  "accepted_input": "SalesAnalysisTask/v1",
  "output": "EvidenceReport/v1",
  "required_scopes": ["sales:read"],
  "max_cost": 1.0
}
```

Card 是发现契约，不是权限授予。

## 22.4 Task Delegation

Task Envelope 应包含：

- task_id / parent_run_id；
- objective 与 success criteria；
- 输入引用，不复制全部父 Context；
- delegated scopes；
- budget 与 deadline；
- output schema；
- evidence requirement；
- cancellation token。

子 Agent 只能获得完成子任务所需的最小 scope，不能继承协调者全部凭证。

## 22.5 通信与共享状态

共享全部对话会造成 Context 污染和权限泄漏。更推荐：

- 结构化消息；
- 引用对象存储中的 artifact；
- append-only event；
- 父子 task lineage；
- 每个子 Agent 独立 scratchpad；
- 只将验证后的输出合并到父状态。

子 Agent 的自然语言结论不能自动成为事实。

## 22.6 冲突解决

多个 Agent 给出不同答案时：

1. 比较证据来源和新鲜度；
2. 检查指标定义和范围；
3. 使用确定性 verifier；
4. 必要时追加独立查询；
5. 无法解决时保留分歧并交给人。

多数投票可能让多个同源 Agent 一起犯错。置信度也必须校准。

## 22.7 框架横向对比

| 框架 | 主要模式 | 状态/通信 | 优点 | 注意点 |
|---|---|---|---|---|
| OpenAI Agents SDK | handoff、agent-as-tool | Runner/session/trace | 模式直接、trace 完整 | 定义交接历史和权限 |
| LangGraph | subgraph、supervisor、tool call | typed state/checkpoint | 控制与恢复强 | subgraph 持久策略需选择 |
| Google ADK | agent team、workflow/graph | session state/events | workflow 与 agent 组合 | ADK 2.0 能力演进快 |
| AutoGen AgentChat | agents、teams、group chat | message/team runtime | 协作模式丰富 | 控制对话终止和成本 |
| CrewAI | agents、tasks、crews/flows | role/task/process | 业务抽象直观 | 避免角色 Prompt 代替契约 |

框架 API 不会自动解决跨 Agent 权限与证据一致性。

## 22.8 A2A 与 MCP

- MCP：AI Host 连接工具、资源和 Prompt Server；
- A2A：独立 Agent/服务之间交换任务和结果；
- 内部函数调用：同一 Runtime 内的最低开销委派。

进程内子 Agent 不必为了“标准化”强行使用网络协议。跨团队、跨平台和远程 Agent 才更需要 A2A 类协议。

## 22.9 业务案例：经营分析团队

Coordinator 将同一数据 snapshot 下的子任务交给 Sales、Inventory、Service Agent。每个 Agent 只访问本领域数据，返回 `EvidenceReport`。合并器检查时间窗口和指标定义一致，再生成综合结论。发布仍由确定性 Workflow 和管理者审批。

## 22.10 Python MVP

```bash
python chapters/chapter22/example.py
python -m unittest discover -s chapters/chapter22 -p "test_*.py"
```

MVP 使用 AgentCard、capability/scope 匹配、委派预算和 evidence contract；没有合适权限的 Agent 时 fail closed。

## Production Checklist

- [ ] 每增加一个 Agent 都有明确理由
- [ ] Agent Card 与 Task Envelope 版本化
- [ ] delegation 采用最小 scope
- [ ] 子 Agent 有 budget、deadline 和 cancellation
- [ ] 父子 Run/Task lineage 可追踪
- [ ] 只合并验证后的输出
- [ ] 冲突按证据解决，不盲目投票
- [ ] 防止 delegation loop 和无限对话

## Summary

Multi-Agent 是组织复杂度工具，不是智能倍增器。先把单 Agent contract 做清楚，再通过有界委派组合专业能力。

## Notes

Google ADK 文档已迁移至 `adk.dev`，且 ADK 2.0 引入更灵活的 graph/dynamic workflow；教程引用当前官方地址。

## References

[1] OpenAI Agents SDK, Handoffs.
https://openai.github.io/openai-agents-python/handoffs/

[2] LangGraph, Subgraphs.
https://docs.langchain.com/oss/python/langgraph/use-subgraphs

[3] Google ADK, Multi-agent systems.
https://adk.dev/workflows/

[4] AutoGen AgentChat.
https://microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/tutorial/index.html

以上 URL 已在 2026-07-31 核对。
