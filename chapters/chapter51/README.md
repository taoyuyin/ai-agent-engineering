# Chapter 51 Agent Operating System

Part VII Future —— 下一代软件

Version: 2026-08

Last Updated: 2026-08-03

## Core Question

当 Agent 成为长期运行、消耗多种资源并调用外部能力的工作负载时，我们是否需要一个 Agent Operating System？

## Chapter Conclusion

`Agent OS` 目前更适合作为架构隐喻，而不是已经稳定的行业标准。它描述的是位于 Agent Application 与基础设施之间的一组系统能力：生命周期、调度、资源核算、上下文隔离、能力授权、持久化和恢复。

真正值得建设的不是“像桌面操作系统一样的界面”，而是一套可以运行、暂停、迁移、恢复和治理 Agent Workload 的内核契约。

## Learning Objectives

完成本章后，你应该能够：

- 区分 Agent Runtime、Agent Platform 与 Agent OS；
- 建立传统 OS 与 Agent Workload 的类比及边界；
- 设计 Workload Spec、Scheduler、Capability Token 和 Checkpoint；
- 理解 Filter/Score 调度和 Token/Cost 资源核算；
- 识别 Agent OS 尚未解决的开放问题。

## 51.1 为什么需要 OS 视角

一个请求内完成的 Agent Loop，Runtime 足以承载。以下场景开始要求更高层抽象：

- 任务持续数小时或数天，需要暂停和恢复；
- 同一租户并发运行多个 Agent，需要配额和优先级；
- Browser、Code Sandbox、GPU Model 和企业工具分布在不同节点；
- 数据不能离开指定地域；
- Agent 之间需要委派，但不能传递全部权限；
- 模型供应商故障或预算耗尽时，需要迁移执行；
- 人工审批等待期间不能占用昂贵计算资源。

这时，Agent 不再只是一个函数调用，而是一种有状态工作负载。

## 51.2 与传统操作系统的类比

| Traditional OS | Agent OS 抽象 | 不能直接等同的原因 |
| --- | --- | --- |
| Process | Agent Run / Workload | Run 可能跨机器、跨模型并等待数天 |
| Instruction | Model / Tool Step | 步骤非确定、延迟和价格差异大 |
| Address Space | Context + Working Memory | 语义状态会压缩、检索和重建 |
| System Call | Governed Tool Call | 调用可能产生真实世界副作用 |
| Scheduler | Workload Scheduler | 同时受 Token、成本、地域和能力约束 |
| File System | Memory / Artifact Store | 需要来源、ACL、版本和遗忘策略 |
| User / Permission | Identity + Capability | 权限应按任务限时、最小化委派 |
| Process Snapshot | Checkpoint + Event History | 模型输出不能依赖重放时重新采样 |

最大的差异是非确定性。传统指令在给定状态下具有清晰语义，LLM 输出会受模型版本、采样、上下文和服务状态影响。因此 Agent OS 不能只保存“程序计数器”，必须保存输入、决策、工具结果和证据。

## 51.3 Agent Workload Spec

调度器不应该理解自然语言任务细节，而应消费一个结构化 Workload：

```yaml
run_id: run-51-001
tenant: manufacturing
priority: 8
required_capabilities: [retrieval, code]
required_region: cn
model_tier: reasoning
token_budget: 12000
cost_budget: 0.25
deadline_seconds: 300
checkpoint_policy: every_step
```

`required_capabilities` 描述运行环境必须提供什么，不代表 Agent 自动获得权限。调度成功后，安全系统还需要签发短期 Capability Token，约束租户、Run、Scope、有效期和最大调用次数。

## 51.4 调度：先过滤，再评分

Kubernetes Scheduler 对 Pod 先过滤不满足约束的节点，再对可行节点评分。Agent Workload 可以复用这一思想，但资源维度不同。

### Filter：硬约束

- 数据地域是否匹配；
- 节点是否提供 Browser、Code、Retrieval 等能力；
- 是否支持指定模型等级；
- 剩余 Token、并发和内存是否足够；
- 预计成本是否在预算内；
- 节点的安全等级是否满足数据分类。

### Score：软偏好

- 端到端延迟更低；
- 数据和工具更近；
- 推理价格更低；
- 缓存命中概率更高；
- 当前负载更均衡；
- 高优先级任务获得更多分数。

调度结果必须包含选择原因与资源预留。只做负载均衡，却不预留 Token 和成本，会在运行中产生超卖。

## 51.5 Agent 的资源模型

传统服务主要看 CPU、内存、网络；Agent 还需要核算：

| 资源 | 配额单位 | 超限策略 |
| --- | --- | --- |
| Context | input token / step | 压缩、检索或拒绝 |
| Generation | output token / run | 截断、模型降级 |
| Model Cost | currency / tenant / period | 路由、排队或停止 |
| Tool Calls | calls / tool / run | 限流、熔断 |
| Wall Time | seconds / run | checkpoint 后挂起 |
| Sandbox | CPU / memory / storage | 回收容器 |
| Human Attention | approvals / queue | 升级、超时、取消 |

“人工注意力”也是稀缺资源。如果 Agent 每一步都请求审批，系统虽然安全，却不可运营。

## 51.6 持久化与确定性边界

长任务需要 Durable Execution。可靠做法是保存状态转换和外部结果：

```text
QUEUED → SCHEDULED → RUNNING → WAITING_APPROVAL
       → RUNNING → COMPLETED / FAILED / CANCELLED
```

Workflow 重放时不能再次请求模型、数据库或外部 API，否则结果可能改变。应把这些非确定调用放入 Activity/Task，记录结果，再由确定性 Workflow 消费。Temporal 的 Workflow/Activity 边界提供了一个成熟参照。

Checkpoint 至少需要保存：

- Workload Spec 和 Agent 版本；
- 当前状态与已完成 Plan Step；
- 组装后的上下文摘要及来源；
- 模型输出和工具 Observation；
- 已消耗 Token、成本和调用次数；
- Capability Token 的引用而非长期密钥；
- 待处理的人类决策。

## 51.7 权限：从角色到能力票据

RBAC 适合表达“财务分析员可以读财务数据”，但 Agent 委派需要更细的运行时权限：

```text
Capability = who + run_id + resource + action + constraint + expiry
```

例如主 Agent 可以把“读取订单 123 的物流状态”委派给子 Agent，但不应把用户全部订单权限一并传递。票据还应限制只读、租户、地域、次数和有效期。

Host 应管理权限和生命周期；Tool/MCP Server 只暴露能力并验证收到的身份与 Scope。把所有安全责任交给 Prompt 是错误边界。

## 51.8 Python MVP：Workload Scheduler

本章示例实现一个离线调度器：

- `Workload` 声明能力、地域、模型、Token 和成本；
- `RuntimeNode` 声明容量和运行能力；
- Scheduler 过滤不可行节点，对候选节点评分；
- 调度成功后预留 Token 并生成演示用 Capability Token；
- 输出 `queued → scheduled → running` 状态和资源变化。

```bash
cd chapters/chapter51
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python example.py
```

示例中的 Token 只是可读演示。生产系统应使用签名、短期、可撤销的凭证，并由独立 Policy Decision Point 生成。

**与模型的关系**：Scheduler 在模型调用前选择满足地域、能力和预算的 Runtime Node；模型只在调度成功后执行 Workload。调度规则不应由被调度的模型自行修改。

## 51.9 Agent Runtime、Platform 与 OS 的边界

| 层次 | 核心问题 | 典型能力 |
| --- | --- | --- |
| Runtime | 一个 Run 如何正确执行 | Loop、State、Tool、Memory、Retry |
| Platform | 多团队如何交付和治理 | Registry、Eval、Policy、Release、FinOps |
| Agent OS | 多工作负载如何共享环境与资源 | Scheduling、Isolation、Capability、Checkpoint |

三者可能由同一个产品实现，但架构职责不应混在一起。平台负责声明与治理，OS 抽象负责安置和隔离，Runtime 负责单次执行语义。

## 51.10 开放问题与研究方向

以下判断仍处于演进期：

- 是否会形成跨供应商的 Agent Workload Spec；
- Context 能否像虚拟内存一样分层、换入换出并保持语义一致；
- 不同模型之间迁移 Checkpoint 时如何处理推理差异；
- Token、工具和人工成本能否形成统一资源计量；
- Capability 委派如何跨组织建立信任；
- 多 Agent 的死锁、饥饿和优先级反转如何检测。

这些问题决定 `Agent OS` 会成为独立层，还是被云平台、工作流引擎和 Agent Platform 分别吸收。

## Summary

Agent OS 是理解下一代 Runtime 的有用框架，但不是应当照搬传统 OS 的产品口号。它要求把 Agent 视为有状态、有预算、有权限、可暂停恢复的工作负载，并用确定性系统控制其非确定执行。

下一章将讨论一种特殊而重要的能力：Agent 不再只调用 API，而是像人一样观察和操作 GUI。

## References

- [Kubernetes Scheduler](https://kubernetes.io/docs/concepts/scheduling-eviction/kube-scheduler/)
- [Kubernetes Resource Quotas](https://kubernetes.io/docs/concepts/policy/resource-quotas/)
- [Temporal Workflows](https://docs.temporal.io/workflows)
- [Model Context Protocol Architecture](https://modelcontextprotocol.io/specification/2025-06-18/architecture)
