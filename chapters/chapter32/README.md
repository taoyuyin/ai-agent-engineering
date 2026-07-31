# Chapter 32 Cost Optimization：在质量约束下控制 Agent 单位经济性

Part IV Agent Engineering —— 如何构建企业级 Agent

Version: 2026-07

Last Updated: 2026-07-31

## Core Question

如何通过 Token、模型路由、缓存、预算和架构优化成本，同时守住质量与安全？

## Chapter Conclusion

成本优化的目标不是每次调用最便宜，而是最小化“每个成功任务成本”。模型单价只是成本的一部分，重试、无效检索、长上下文、工具和人工复核都应进入账本。

## Learning Objectives

- 建立 per-run 与 per-outcome 成本模型
- 设计 capability/quality-aware model routing
- 理解缓存、batch、压缩和 retry 的经济性
- 对比 Provider Router、LiteLLM 和自建 Gateway
- 运行一个预算约束下的最便宜可用模型路由器

## 32.1 完整成本模型

```text
Run Cost =
  input/output/reasoning token
  + embedding/rerank
  + search/vector/database/tool
  + compute/storage/egress
  + retry/fallback
  + human review
```

更小模型若导致三次重试和更多人工接管，任务成本可能反而更高。

## 32.2 优化杠杆

1. 删除无价值步骤和重复 Context；
2. 对静态前缀使用 Prompt Cache；
3. 对离线工作使用 Batch；
4. 将分类、抽取交给更小模型；
5. 复杂推理按 capability 升级；
6. 对工具结果、检索和摘要做安全缓存；
7. 设置 run、tenant、team、month 多级预算；
8. 超预算时 degrade、queue、review 或 reject。

## 32.3 Model Routing

路由输入不应只有价格，还包括：

- capability：视觉、工具、长上下文、推理；
- quality tier 与业务风险；
- latency/region/data residency；
- 当前 rate limit、错误率和可用性；
- 预计输入/输出 Token 与剩余预算。

路由决定和实际 usage 都写入 ledger，估算偏差持续校准。

## 32.4 工具横向对比

| 方案 | 优点 | 局限 | 适用 |
|---|---|---|---|
| Provider 原生能力 | Prompt Cache、Batch、usage 精确 | 单厂商 | 单云/单模型族 |
| LiteLLM Router/Proxy | 多供应商统一、路由与预算 | 需维护网关和配置 | 多模型平台 |
| 云 AI Gateway | IAM、配额、审计集成 | 云平台耦合 | 企业云治理 |
| 自建 Model Gateway | 策略与结算完全自定义 | 高可用、价格更新成本 | 大规模/强治理 |
| FinOps/BI | 跨团队归因和预算 | 不执行实时路由 | 管理与复盘 |

## 32.5 企业案例：文档处理平台

平台先用小模型分类文档并抽取标准字段，只有低置信或复杂合同升级到强模型。相同模板前缀利用缓存，夜间批量任务进入 Batch 队列。每个租户有日预算和单文档上限，ledger 记录模型、Token、缓存命中、重试和最终成功状态，团队按“每份通过审核文档成本”优化。

## 32.6 Python MVP

`cost_runtime` 实现 capability、quality tier、Token 单价、cached token、remaining budget 与 cheapest-capable 路由：

```bash
python3 chapters/chapter32/example.py
python3 -m unittest discover -s chapters/chapter32 -p "test_*.py"
```

示例价格是教学数据，不代表任何厂商当前价格。

## 32.7 Production Readiness Checklist

- [ ] 记录估算与实际 usage/cost
- [ ] 成本归因到 run、tenant、feature 和 outcome
- [ ] 路由包含能力、质量、区域和可用性
- [ ] Prompt/Tool/RAG Cache 有隔离与失效策略
- [ ] Retry、fallback 和人工成本进入账本
- [ ] 多层 budget 有明确超限行为
- [ ] 价格与模型目录自动版本化更新
- [ ] 以 cost per successful outcome 优化

## Summary

成本是架构反馈信号。可观测的 usage、明确的质量门槛和能力感知路由，才能让 Agent 从“能跑”走向可持续规模化。

## Notes

厂商价格、缓存折扣和 Batch 条件会变化，本章不固化实时价格；生产 Model Catalog 应带 effective date。

## References

[1] OpenAI, Cost optimization.
https://developers.openai.com/api/docs/guides/cost-optimization

[2] OpenAI, Prompt caching.
https://developers.openai.com/api/docs/guides/prompt-caching

[3] LiteLLM, Router.
https://docs.litellm.ai/docs/routing

以上 URL 已在 2026-07-31 核对。
