# Multi-Agent

当前状态：**设计契约，尚无本目录可运行工程**。语义委派 MVP 见 [Chapter 22](../../chapters/chapter22/README.md)，企业控制面见 [Chapter 49](../../chapters/chapter49/README.md)。

## 业务目标

协调 Policy、Sales 和 Risk 三个领域 Agent，生成可对外共享的销售摘要。案例验证 Agent Registry、结构化委派、最小 Scope、预算、冲突解决和统一 Trace。

## 端到端流程

```text
Task Envelope
  → Coordinator Plan
  → Capability Discovery
  → Policy / Scope / Budget Check per Hop
  → Parallel or Sequential Delegation
  → Structured Result + Evidence Contract
  → Conflict Resolution
  → Final Synthesis
  → Trace / Cost / Handoff Report
```

## 模型与确定性边界

模型可帮助拆解和选择 Agent 候选；Registry 和 Policy 决定可调用版本与委派 Scope。Agent 间传递 Task Envelope 和结构化 Result，不共享无边界完整对话或上游全部权限。

## 目标工程结构

```text
multi-agent/
├── README.md
├── requirements.txt
├── multi_agent/
│   ├── contracts.py
│   ├── registry.py
│   ├── coordinator.py
│   ├── delegation.py
│   ├── conflict.py
│   └── application.py
├── agents/
├── tests/
├── evaluation/
└── Dockerfile
```

## 最小验收

- 每个 Agent 有 Owner、Version、Capability、Scope、SLO 和 Eval；
- 每次委派限制 Token、Cost、Deadline 和最大 Hop；
- 检测重复 Task 与 A→B→A 循环；
- 子 Agent 返回 Evidence，否则 Coordinator 不接受结果；
- 冲突不会通过“多数模型同意”自动掩盖；
- Trace 关联全部 Agent、模型、工具、策略和成本。

## 生产升级

接入 Durable Workflow、Queue、服务发现、熔断、幂等和 Agent Release Gate。只有单 Agent 无法维护真实领域边界时才引入 Multi-Agent。
