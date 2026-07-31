# Chapter 23 Agent Architecture：企业级 Agent 的完整系统边界

Part III Agent Architecture —— Agent 内部如何工作

Version: 2026-07

Last Updated: 2026-07-31

## Core Question

Goal、Planner、Tool、Memory、Context、Observation、Reflection、State Machine、Workflow 和 Multi-Agent 如何组合成企业级架构？

## Chapter Conclusion

企业级 Agent 不是“模型加工具”，而是 Intelligence Plane、Deterministic Control Plane、Data Plane 和 Governance Plane 的组合。模型负责不确定判断，Runtime 与 Workflow 负责状态、安全和可靠执行。

## Learning Objectives

- 建立 Agent 的组件、运行和部署架构
- 明确模型、Runtime、Workflow、工具和数据的信任边界
- 设计同步、异步和 Human-in-the-loop 执行
- 对比主流框架在整体架构中的位置
- 运行一个包含身份、策略、租户数据、证据和审计的 MVP

## 23.1 四个平面

```text
Channels / API / UI
        ↓
Governance Plane
Identity · Policy · Guardrails · Audit · Evaluation
        ↓
Deterministic Control Plane
Lifecycle · State Machine · Workflow · Approval · Budget
        ↓
Intelligence Plane
Goal · Planner · Model Gateway · Context · Reflection · Multi-Agent
        ↓
Capability & Data Plane
Tool Gateway · MCP · Semantic Layer · Memory · Enterprise Systems
```

Governance 不是最后加的一层过滤器，而是穿过每个调用和状态转移。

## 23.2 核心组件

| 组件 | 输入 | 输出 | 关键责任 |
|---|---|---|---|
| API/Channel | user request | authenticated request | 身份、限流 |
| Goal Compiler | request/context | GoalSpec | 澄清、约束、验收 |
| Runtime | GoalSpec/state | commands/events | 生命周期与预算 |
| Planner | goal/observation | Plan | 分解与更新 |
| Context Compiler | state/data | model request | 选择、隔离、预算 |
| Model Gateway | request/policy | model output | 路由、fallback、usage |
| Tool Gateway | tool call/identity | ToolResult | schema、权限、执行 |
| Observation Adapter | result | Observation | 归一、脱敏、来源 |
| Memory | policy/data | records/retrieval | 持久、更新、遗忘 |
| Evaluator | output/evidence | verdict | 完成和质量判断 |
| Workflow | events/tasks | durable progress | 等待、重试、审批 |

## 23.3 一次 Run 的执行序列

```text
1. Authenticate request
2. Compile and validate Goal
3. Create Run + checkpoint
4. Select workflow/planning policy
5. Assemble step context
6. Call model
7. Validate proposed command
8. Execute authorized tool
9. Normalize Observation
10. Verify / repair / update plan
11. Complete, wait, fail or escalate
12. Persist trace, evidence and metrics
```

每一步都应有 run_id、tenant_id、actor_id 和 trace context。

## 23.4 信任边界

| 数据/动作 | 默认信任 |
|---|---|
| System policy / verified identity | 高，但仍版本化 |
| User request | 不可信输入 |
| Model output | 不可信 command proposal |
| Tool/MCP result | 不可信外部 data |
| Memory | 需来源、权限和新鲜度验证 |
| Human approval | 需身份、对象版本与审计 |
| Side effect | 需策略、幂等和确认 |

“来自内部系统”不等于可以当作模型指令。

## 23.5 同步与异步架构

### 同步

适合秒级问答和只读查询。API worker 可以等待模型与少量工具，但仍要设总 deadline。

### 异步

适合研究、报表、Coding 和审批任务：

```text
API → Run Store → Queue/Workflow → Agent Worker
                            ↓
                    Tool/Model Gateway
                            ↓
                     Events / WebSocket
```

客户端通过 Run API 查询或订阅事件。不要保持一个 HTTP 请求等待数十分钟。

## 23.6 存储架构

至少区分：

- **Run Store**：状态、checkpoint、计划；
- **Event/Audit Store**：不可变事件；
- **Memory Store**：跨 Run 事实；
- **Artifact Store**：大文件和工具结果；
- **Vector Index**：语义召回；
- **Evaluation Store**：样本、trace 与评分。

同一张 conversation 表无法承担所有语义。

## 23.7 框架在架构中的位置

| 工具 | 最适合的位置 | 不应单独承担 |
|---|---|---|
| OpenAI Agents SDK | Agent Runner、tools、handoff、trace | 企业 IAM 与 durable workflow |
| LangGraph | 状态图、checkpoint、HITL | 完整 API Gateway/数据治理 |
| Google ADK | Agent runtime、graph/workflow、Google 部署 | 企业跨域治理全部职责 |
| Temporal | durable control plane | 模型推理与 Context |
| Airflow | 批处理/调度 Agent Job | 交互式动态 Agent loop |
| MCP | capability/data protocol | Agent planning 与授权策略 |
| AutoGen/CrewAI | multi-agent patterns | 企业状态与安全基座 |

选型应组合能力，而不是寻找一个“全能 Agent 框架”。

## 23.8 部署拓扑

生产环境通常拆分：

- stateless API；
- horizontally scalable Agent Worker；
- 独立 Model Gateway；
- Tool/MCP Gateway；
- Workflow/Queue；
- Postgres/Redis/Object Store/Vector DB；
- OTel Collector 与评估服务；
- Secret Manager 与 Policy Engine。

不同租户、数据等级和工具风险可以运行在不同安全域。

## 23.9 企业案例：经营分析 Agent Platform

用户通过 SSO 发起报告任务。Goal Compiler 固化数据范围和验收标准，Workflow 冻结 snapshot 并并行调用领域 Agent。所有数据访问经 Semantic/Tool Gateway 执行行级权限，Observation 带来源。Evaluator 检查指标定义和引用，管理者批准后发布。平台记录模型/Prompt/Tool/数据版本，使报告可复现。

## 23.10 Python MVP

```bash
python chapters/chapter23/example.py
python -m unittest discover -s chapters/chapter23 -p "test_*.py"
```

MVP 是 composition root：`AgentRequest` 携带 tenant/actor/scope，PolicyEnforcer 在数据访问前授权，结果带 evidence，成功和拒绝均写 AuditSink。它不模拟 LLM，而是展示模型之外必须存在的架构边界。

## 23.11 Production Readiness Checklist

- [ ] 所有请求有 identity、tenant、run 和 trace ID
- [ ] Goal、Plan、State、Tool、Observation schema 版本化
- [ ] 模型输出只作为 command proposal
- [ ] Tool Gateway 独立执行授权
- [ ] Memory 与数据检索在查询阶段隔离租户
- [ ] 长任务使用 durable workflow
- [ ] Side effect 有审批、幂等、补偿和对账
- [ ] Context、trace 和日志执行脱敏
- [ ] Offline/online evaluation 与发布门禁
- [ ] 监控质量、延迟、费用、失败与安全事件
- [ ] 支持模型、Prompt、工具和数据版本回放

## Summary

Part III 最终建立的是一个可控制的智能执行系统：Goal 定义成功，Planner 组织工作，Tool 连接外部世界，Memory 与 Context 提供信息，Observation 与 Reflection 闭环反馈，State Machine 与 Workflow 保证可靠，Multi-Agent 扩展专业能力，Governance 贯穿全程。

## Notes

本章架构是厂商中立的参考模型。具体项目可以合并组件，但不能删除其责任；例如把 Tool Gateway 写在 Runtime 进程内，仍必须保留独立授权边界。

## References

[1] OpenAI Agents SDK, Running agents.
https://openai.github.io/openai-agents-python/running_agents/

[2] LangGraph, Overview.
https://docs.langchain.com/oss/python/langgraph/overview

[3] Google ADK, Documentation.
https://adk.dev/

[4] Temporal, Workflows.
https://docs.temporal.io/workflows

[5] Model Context Protocol, Architecture.
https://modelcontextprotocol.io/docs/2026-07-28/learn/architecture

以上 URL 已在 2026-07-31 核对。
