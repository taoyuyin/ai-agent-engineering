# Chapter 27 Semantic Layer：让 Agent 理解企业指标而不是猜 SQL

Part IV Agent Engineering —— 如何构建企业级 Agent

Version: 2026-07

Last Updated: 2026-07-31

## Core Question

为什么企业 Data Agent 需要指标、维度、实体、口径和权限组成的 Semantic Layer？

## Chapter Conclusion

LLM 能生成语法正确的 SQL，却不知道企业认可的“收入”“活跃客户”和“库存”口径。Semantic Layer 把业务语义编译成受控查询，是 Data Agent 与数据仓库之间的确定性契约。

## Learning Objectives

- 区分数据库 schema、知识图谱和分析语义层
- 建模 metric、dimension、entity、join、time 与 policy
- 理解自然语言到 Semantic Query 再到 SQL 的编译链
- 对比 dbt、Cube、LookML 和自建方案
- 运行一个 allowlist + 参数化 SQL 的 Metric Compiler

## 27.1 为什么 Text-to-SQL 不够

同一个“销售额”可能是含税订单额、支付额、确认收入或扣除退款后的净收入。让模型直接查看数百张表会导致：

- join 路径错误或 fan-out 重复计算；
- 指标口径随 Prompt 漂移；
- 使用未来数据、错误时区或不完整周期；
- 绕过行列级权限；
- SQL 能执行，但业务结论不可接受。

SQL 是执行语言，不是业务语义。

## 27.2 Semantic Layer 模型

```text
Entity: Customer, Order, Product
Dimension: region, channel, category
Metric: net_revenue = SUM(order_amount - refund_amount)
Time: order_date, fiscal_calendar, timezone
Join: cardinality, keys, allowed path
Policy: tenant, row filter, column mask
Metadata: owner, version, description, unit, certification
```

指标必须声明 grain、聚合、时间窗口、单位和重大排除项。否则“同名指标”仍会产生不同答案。

## 27.3 查询编译链

```text
Question
  ↓ intent/entity resolution
Semantic Query (metric, dimensions, filters, time)
  ↓ catalog validation + authorization
Logical Plan
  ↓ dialect compiler
Parameterized SQL
  ↓ warehouse
Result + metric version + lineage
```

模型可以提出 Semantic Query，但不能绕过 catalog 直接执行任意 SQL。编译器负责 allowlist、join、policy 和参数绑定。

## 27.4 Semantic Layer 与 RAG

RAG 适合解释“指标是什么意思”，Semantic Layer 负责“指标如何计算”。典型 Data Agent 会：

1. 用 catalog/RAG 发现候选指标；
2. 生成结构化 MetricRequest；
3. Semantic Layer 验证维度、过滤和权限；
4. 执行查询；
5. Agent 基于结果和定义生成分析。

把指标定义作为纯文本放进 Prompt，无法替代确定性计算与权限执行。

## 27.5 工具横向对比

| 工具 | 模型方式 | 优点 | 局限 | 适用 |
|---|---|---|---|---|
| dbt Semantic Layer/MetricFlow | dbt metrics + query engine | 与 dbt lineage、模型开发衔接 | 团队需采用 dbt 体系 | 现代数据栈 |
| Cube | Cube/View、Semantic SQL/API | API、缓存、权限和嵌入能力强 | 引入独立服务与模型体系 | BI、嵌入分析、Agent |
| LookML | Model/Explore/View | 成熟 BI 语义和权限 | Looker 平台耦合 | Looker 企业 |
| 云仓库 Semantic View | 仓库原生对象 | 数据就地、治理统一 | 跨仓库可移植性有限 | 单一云数仓 |
| 自建 Metric API | 领域 DSL/服务 | 契合 IAM、行业口径 | 编译器和治理成本高 | 核心指标平台 |

比较维度应包括：metric expressiveness、join safety、time semantics、row security、API、cache、lineage、Git/CI 和多仓库支持。

## 27.6 企业案例：经营分析 Agent

CEO 询问“华东本季度收入为什么下降”。Agent 从语义层选择 `net_revenue`，按 region、product 和 week 分解。Semantic Layer 自动加入财务日历、华东权限范围和退款扣减规则。结果附 metric version、数据快照与查询计划。随后 Agent 才对趋势做解释；它不能临时改成订单总额来让结果“更合理”。

## 27.7 Python MVP

`semantic_runtime` 实现：

- 指标、维度、时间、owner、unit 和 version；
- 标识符安全检查；
- 请求维度和 filter allowlist；
- 参数化 SQL 与 metric metadata。

```bash
python3 chapters/chapter27/example.py
python3 -m unittest discover -s chapters/chapter27 -p "test_*.py"
```

## 27.8 Production Readiness Checklist

- [ ] 每个指标定义 grain、公式、窗口、单位和 owner
- [ ] join cardinality 与允许路径可验证
- [ ] 时间语义包含时区、财务日历和完整周期
- [ ] row/column/tenant policy 在查询层执行
- [ ] Agent 只提交 Semantic Query，不执行任意 SQL
- [ ] 查询结果携带 metric/catalog/data snapshot 版本
- [ ] 指标变更走 Git、Review、CI 和影响分析
- [ ] 与 BI 报表对账并建立黄金问题集

## Summary

Semantic Layer 将自然语言的模糊意图压缩成企业认可的计算契约。它不是为了限制 Agent，而是让 Agent 的灵活推理建立在稳定数据语义之上。

## Notes

Semantic Layer 与本体/知识图谱有交集，但本章聚焦分析指标编译。企业也可以把指标目录暴露为 MCP Tool，但授权仍应由服务端执行。

## References

[1] dbt, Semantic Layer.
https://docs.getdbt.com/docs/use-dbt-semantic-layer/dbt-sl

[2] Cube, Documentation.
https://docs.cube.dev/docs/introduction

[3] Google Cloud, Introduction to LookML.
https://docs.cloud.google.com/looker/docs/what-is-lookml

以上 URL 已在 2026-07-31 核对。
