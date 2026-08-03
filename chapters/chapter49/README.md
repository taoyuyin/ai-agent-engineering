# Chapter 49 Multi-Agent 企业平台

Part VI Enterprise Practice —— 企业实践

Version: 2026-08

Last Updated: 2026-08-03

## 本章结论

企业 Multi-Agent 平台的核心不是让更多 Agent 互相聊天，而是统一管理 Agent Registry、身份、能力、协议、预算、委派、状态、评测和可观测性。平台控制面决定“谁可以做什么”，运行时数据面执行具体任务。

## 学习目标

- 区分 Control Plane 与 Runtime/Data Plane；
- 设计 Agent Descriptor、Task Envelope 和 Message Contract；
- 执行能力路由、Scope、预算和最大委派深度；
- 处理版本、租户、Trace、故障和人工审批；
- 判断什么时候应该使用 Multi-Agent。

## 49.1 为什么需要平台

当企业拥有几十个 Agent，每个团队独立管理模型、Tool、权限、Trace 和评测，会出现重复建设、权限扩散、成本失控和协议不兼容。

平台不是一个“超级 Agent”，而是一组标准和共享服务。领域团队仍拥有业务 Agent 和数据权限。

## 49.2 参考架构

```text
Control Plane
  ├── Agent / Tool Registry
  ├── Policy & Identity
  ├── Prompt / Model / Version Catalog
  ├── Evaluation & Release Gate
  └── Cost / Quota / Governance

Runtime Plane
  ├── API / Task Queue
  ├── Orchestrator / Router
  ├── Agent Workers
  ├── State / Memory / Artifact
  └── Trace / Metrics / Logs

Enterprise Systems
  └── Governed Tool Gateways
```

控制面变更低频、强审查；运行面处理高频任务并执行已发布策略。

## 49.3 Agent Contract

Agent Descriptor 至少包含：

- 稳定名称和语义版本；
- 能力列表及输入输出 Schema；
- 所需 Scope 和数据分类；
- 模型、区域和部署 Endpoint；
- 单次成本、超时和并发；
- Owner、SLO、评测版本和发布状态。

Task Envelope 包含 task/tenant/actor、目标、Scope、预算、截止时间、最大 Hop、Trace Context 和幂等键。Agent 之间传递结构化消息，而不是无边界对话历史。

## 49.4 路由与委派

路由顺序建议：能力匹配 → 权限 → 数据区域 → 健康/SLO → 版本策略 → 成本。模型可以帮助选择候选能力，但 Policy Engine 做最终决定。

委派必须限制最大深度、总调用数、Token、时间和成本。检测 `A -> B -> A` 循环，并把相同 Task ID 的重复消息做幂等处理。

## 49.5 最小可运行 MVP

`example.py` 实现平台控制面的最小闭环：

- Registry 注册政策、销售和风险 Agent 版本；
- 按 Capability 解析 Agent；
- 在每次委派前检查 Scope；
- 检查 Budget 和最大 Hop；
- 执行三个独立领域 Handler；
- 汇总结构化结果；
- 输出 Agent 版本、成本和 Evidence Trace。

```bash
cd chapters/chapter49
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python example.py "汇总 2025 年销售并检查对外共享策略"
```

删除任一 Scope 或降低预算即可观察平台在调用前拒绝任务，而不是等 Agent 自觉停止。

## 49.6 通信模式

| 模式 | 优点 | 适用场景 |
| --- | --- | --- |
| Orchestrator-Worker | 控制集中、易治理 | 企业默认 |
| Pipeline | 顺序清晰、易审计 | 固定加工链 |
| Parallel Fan-out | 降低独立任务延迟 | 多源研究 |
| Event-driven | 解耦、可扩展 | 长任务与异步系统 |
| Peer-to-peer Chat | 灵活 | 研究原型，生产慎用 |

平台应优先采用 Orchestrator + 结构化消息。自由群聊难以分配责任、终止和成本。

## 49.7 状态与可靠性

跨服务任务使用持久化 Workflow/Queue。每个 Step 保存输入 Hash、Agent 版本、结果引用和副作用状态。至少一次消息需要幂等消费者；外部写操作使用业务幂等键和补偿。

Memory 不等于平台状态。任务状态用于恢复，Memory 用于未来检索，Artifact 保存大结果，Trace 记录发生过程。

## 49.8 可观测与治理

OpenTelemetry 将 Traces、Metrics、Logs 等定义为不同但可关联的信号。平台应传播统一 Trace Context，并记录：

- Router 决策和候选 Agent；
- Agent/Prompt/Model/Tool 版本；
- 每个 Hop 的延迟、Token、成本和错误；
- Policy、审批和 Evidence；
- 最终业务结果。

原始 Prompt 和 Tool Result 可能含 PII，采样、脱敏、访问和保留必须治理。

## 49.9 发布与评测

Agent 版本经过：离线评测 → 安全测试 → Shadow → Canary → 全量。Registry 支持固定版本、流量比例和快速回滚。

平台指标分三层：单 Agent 任务质量；协作路由/委派质量；业务端到端成功率。还要监控循环率、平均 Hop、预算超限、跨租户拒绝和工具错误。

## 49.10 什么时候不需要 Multi-Agent

- 单 Agent 加几个 Tool 已能完成；
- 角色没有不同权限、数据或目标；
- 顺序 Workflow 足以表达；
- 无法定义 Agent 之间的结构化 Contract；
- 团队尚未具备单 Agent 评测和可观测能力。

多 Agent 是组织和系统复杂度的放大器，应由真实边界驱动。

## 49.11 常见踩坑

- 用 Agent 名称代替能力和 Schema；
- 所有 Agent 共享超级权限；
- 无最大 Hop 和预算；
- 自由文本消息承担关键控制；
- Registry 只有 Endpoint，没有 Owner/SLO/评测；
- Trace 保存全部敏感内容；
- 平台团队接管所有领域逻辑。

## 49.12 生产化清单

- Control Plane / Runtime Plane 分离；
- 版本化 Agent、Tool 和 Message Contract；
- 身份、Scope 和租户逐 Hop 传播；
- 预算、超时、Hop 与循环控制；
- Durable State、幂等与补偿；
- Trace/Metrics/Logs 关联与脱敏；
- Release Gate、Canary 和回滚；
- 平台与领域团队责任清晰。

## Summary

Multi-Agent 企业平台首先是治理平台，其次才是协作运行时。MVP 展示了 Registry、Capability Routing、Scope、Budget、Hop 和 Trace 的控制面骨架，为 Part VII Agent Platform 和 Agent OS 建立工程基础。

## References

[1] OpenTelemetry. Signals.
https://opentelemetry.io/docs/concepts/signals/

[2] NIST. AI Risk Management Framework.
https://airc.nist.gov/airmf-resources/airmf/

[3] OWASP. GenAI Security Project.
https://genai.owasp.org/
