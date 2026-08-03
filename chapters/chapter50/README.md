# Chapter 50 Agent Platform

Part VII Future —— 下一代软件

Version: 2026-08

Last Updated: 2026-08-03

## Core Question

企业为什么会从开发单个 Agent，走向建设统一 Agent Platform？

## Chapter Conclusion

Agent Platform 不是一个更大的 Agent，也不是把模型 API 包一层界面。它把模型、工具、知识、Runtime、评测、权限和发布治理变成共享基础设施，使多个团队能够安全、可复用地交付 Agent。

企业并不需要从第一天建设平台；当重复集成、权限漂移、成本失控和发布质量成为组织级问题时，平台化才产生净收益。

## Learning Objectives

完成本章后，你应该能够：

- 区分 Agent Application、Agent Runtime 和 Agent Platform；
- 设计控制面、运行面和数据面的职责边界；
- 定义 Agent Manifest、Registry、Release Gate 和任务路由契约；
- 横向比较自研、框架、低代码平台和云托管方案；
- 判断企业当前是否应该平台化，以及从哪里开始。

## 50.1 从单个 Agent 到平台

第一个 Agent 往往可以由一个小团队完成：选择模型、编写 Prompt、注册工具、实现循环并部署 API。第二十个 Agent 会暴露另一类问题：

- 每个团队重复实现模型调用、重试、缓存和 Trace；
- 同一个数据源被赋予不同权限，审计口径不一致；
- Prompt、工具和模型升级没有统一评测门禁；
- Agent 无法发现或复用其他团队已经发布的能力；
- 成本被分散到多个账号，无法按租户、业务和任务核算；
- 线上事故无法还原当时的模型、上下文、工具结果和策略版本。

平台化解决的是这种组织级复杂度，而不是单次推理能力。

```text
Agent Application = 业务目标 + 交互 + 场景知识
Agent Runtime     = 状态循环 + 工具执行 + 上下文 + 恢复
Agent Platform    = 多应用共享 Runtime + 控制面 + 治理 + 运营
```

## 50.2 平台的三平面架构

```text
                    ┌──────────── Control Plane ────────────┐
Developer / Admin → │ Registry / Policy / Eval / Release    │
                    └────────────────┬───────────────────────┘
                                     │ approved manifest
User / Event ────────────────────────▼────────────────────────
                    ┌──────────── Runtime Plane ─────────────┐
                    │ Router / Agent Runtime / Workflow      │
                    │ Model Gateway / Tool Gateway / Sandbox │
                    └────────────────┬───────────────────────┘
                                     │ governed access
                    ┌────────────────▼───────────────────────┐
                    │ Data Plane                             │
                    │ Memory / Knowledge / Trace / Evidence  │
                    └────────────────────────────────────────┘
```

### Control Plane

控制面管理“什么可以运行”：Agent 注册、版本、所有者、能力声明、权限范围、模型策略、评测结果、审批与下线。它不应直接承载每一步推理流量。

### Runtime Plane

运行面管理“任务如何运行”：模型路由、上下文编译、工具调用、状态持久化、重试、超时、预算和人工中断。Chapter 12–23 实现的 Runtime 是这一层的核心。

### Data Plane

数据面保存“运行依赖什么、产生什么”：知识索引、Working Memory、长期记忆、Trace、Evidence 和评测样本。数据必须绑定租户、版本、ACL 和保留策略。

## 50.3 平台能力地图

| 能力 | 解决的问题 | 最小契约 | 关键指标 |
| --- | --- | --- | --- |
| Model Gateway | 多模型接入与路由 | Model Policy | 延迟、成本、错误率 |
| Agent Registry | 能力发现与版本治理 | Agent Manifest | 复用率、废弃版本数 |
| Tool / MCP Gateway | 工具发现和统一调用 | Tool Schema + Scope | 成功率、越权拦截率 |
| Knowledge Service | ACL-aware Retrieval | Query + Citation | 命中率、引用正确率 |
| Runtime / Workflow | 状态、恢复和长任务 | Run + Event | 完成率、恢复时间 |
| Policy Engine | 身份、权限和风险 | Decision + Reason | 拒绝率、误拦截率 |
| Evaluation | 发布前后质量控制 | Dataset + Score | 回归率、覆盖率 |
| Observability | 还原一次完整运行 | Trace + Evidence | 可诊断率、采样成本 |
| FinOps | 预算和归因 | Usage Envelope | 单任务成本、预算命中率 |

MCP 可以标准化 Host、Client、Server 之间的能力发现与调用，但协议连接成功不等于企业治理完成。身份映射、数据分类、审批、审计和预算仍由平台负责。

## 50.4 Agent Manifest 与发布门禁

容器平台依靠镜像和 Deployment 描述工作负载；Agent Platform 同样需要机器可读的发布单元。一个最小 Manifest 至少包含：

```yaml
name: finance-analysis-agent
version: 1.2.0
owner: data-platform
capabilities: [analyze_revenue, explain_variance]
required_scopes: [warehouse:read]
model_policy: reasoning
evaluation_score: 0.93
estimated_cost: 0.18
```

发布流程不是“上传 Prompt”，而是：

```text
Manifest → Static Validation → Offline Evaluation → Security Review
         → Approval → Registry → Canary → Online Evaluation → Promote/Rollback
```

每一次路由都应保留 `agent_version`、`model_route`、`policy_version` 和 `trace_id`，否则失败时无法知道系统实际执行了什么。

## 50.5 平台方案横向比较

| 路线 | 优点 | 局限 | 适用阶段 |
| --- | --- | --- | --- |
| SDK / Agent Framework | 灵活、贴近代码、启动快 | 组织治理需要自行补齐 | 单团队和原型期 |
| 低代码 Agent Platform | 可视化交付、业务参与度高 | 复杂 Runtime 和深度定制受平台边界影响 | 标准化工作流较多的团队 |
| 云托管 Agent Service | 模型与云资源集成完整、运维负担低 | 供应商绑定、跨云与数据边界需评估 | 已有明确云战略的企业 |
| 企业自研 Platform | 契合内部身份、数据和交付流程 | 成本高，容易重复造框架 | 多业务线且治理要求高 |
| 混合平台 | 共享控制面，场景 Runtime 可替换 | Contract 设计和运营复杂 | 中大型企业的常见终态 |

选择标准不应是功能清单最多，而应是：身份系统能否打通、运行证据能否导出、策略能否外置、模型和 Runtime 能否替换、数据能否满足地域与合规要求。

## 50.6 企业业务场景：财务分析 Agent 上线

财务团队希望发布一个收入差异分析 Agent。平台需要完成：

1. Registry 验证所有者、版本和能力；
2. Evaluation 验证指标计算、引用和拒答；
3. Policy Engine 检查只有 `warehouse:read`，不允许写库；
4. Router 根据任务能力、租户 Scope、成本预算选择已批准版本；
5. Runtime 执行并生成 Trace、SQL Evidence 和最终回答；
6. Online Evaluation 监控质量下降，必要时回滚。

业务 Agent 负责财务语义，平台负责可重复的交付与控制。

## 50.7 Python MVP：发布与路由控制面

本章示例实现：

- `AgentManifest`：Agent 的能力、权限、模型和质量声明；
- `evaluate_release()`：确定性的发布门禁；
- `AgentRegistry`：只接受已批准版本；
- `TaskEnvelope`：携带租户、Scope 和预算；
- `route()`：在能力、权限和成本约束下选择版本。

```bash
cd chapters/chapter50
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python example.py
```

示例故意让一个实验 Agent 无法发布，并将任务路由到通过评测且权限匹配的版本。模型可以提出候选，最终发布与路由必须由确定性控制面裁决。

**与模型的关系**：生产系统中的模型负责 Agent 执行和能力推理；本 MVP 位于模型之外，只验证版本能否发布、任务能否路由。替换模型不会改变 Manifest、Scope 和 Release Gate 契约。

## 50.8 平台成熟度路线

| 等级 | 组织表现 | 下一步 |
| --- | --- | --- |
| L0 单应用 | 每个 Agent 独立集成 | 统一 Trace 和模型网关 |
| L1 共享 Runtime | 调用、工具、状态可复用 | 建 Registry 和 Manifest |
| L2 受治理交付 | 有评测、权限、发布门禁 | 增加租户、预算和运营 |
| L3 平台化 | 多团队自助发布和复用 | 开放能力市场与组合 |
| L4 生态化 | 跨平台发现、委派和结算 | 强化互操作和供应链治理 |

不要跳级。只有两个简单 Agent 的团队，优先做好共享库、评测和 Trace；过早建设门户、市场和复杂编排，会把平台变成新的交付瓶颈。

## 50.9 常见反模式

- 把统一聊天界面称为 Agent Platform；
- 平台记录 Prompt，却不记录工具、策略和数据版本；
- 只提供“允许/拒绝”，不返回可审计原因；
- 所有 Agent 共用超级权限和长期凭证；
- 为复用而制造一个无所不能的通用 Agent；
- 只统计 Token，不关联业务结果和任务成功率；
- 平台团队定义业务语义，业务团队失去所有权。

## Summary

Agent Platform 的本质是共享的控制与交付系统。它把 Agent 从“个人 Demo”变成可注册、可评测、可授权、可观测、可回滚的企业能力。平台化不是必然的第一步，却是多团队规模化后的高概率结果。

下一章会继续向下追问：当 Agent 成为长期运行、需要调度和资源隔离的工作负载时，是否需要类似 Operating System 的抽象？

## References

- [Model Context Protocol Architecture](https://modelcontextprotocol.io/specification/2025-06-18/architecture)
- [NIST AI Risk Management Framework](https://www.nist.gov/itl/ai-risk-management-framework)
- [OpenTelemetry Signals](https://opentelemetry.io/docs/concepts/signals/)
