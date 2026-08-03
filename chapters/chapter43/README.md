# Chapter 43 Data Agent

Part VI Enterprise Practice —— 企业实践

Version: 2026-08

Last Updated: 2026-08-03

## 本章结论

Data Agent 不是自动生成图表的聊天机器人，而是一个能理解分析目标、检查数据质量、选择分析方法、执行可复现计算并解释不确定性的分析运行时。

任何结论都必须绑定数据版本、过滤条件、计算方法和质量状态。数据质量失败时，Agent 应阻止结论生成，而不是用更流畅的语言掩盖问题。

## 学习目标

- 区分 SQL Agent、Data Agent 与 BI Agent；
- 将业务问题转换为指标、切片、基线和分析计划；
- 在分析之前执行 Schema、完整性、唯一性和时效性检查；
- 生成可复现统计结果、异常说明和 Evidence；
- 设计离线评测与分析师反馈闭环。

## 43.1 业务背景

经营团队问“华东收入最近为什么上涨”。查询一张表只能得到数字，Data Agent 还要决定：

- 时间窗口和对比基线是什么？
- 上涨来自价格、销量、客户结构还是一次性订单？
- 数据是否完整，指标口径是否变化？
- 异常是统计异常还是业务事件？
- 证据是否足以支持因果表达？

Data Agent 应优先输出“观察到的关联”和“下一步验证”，除非有实验或可靠因果设计，否则不能把相关性写成因果。

## 43.2 与 SQL Agent、BI Agent 的边界

| 类型 | 主要任务 | 典型输出 |
| --- | --- | --- |
| SQL Agent | 安全获取结构化数据 | 查询结果 + SQL Evidence |
| Data Agent | 探索、诊断、统计和解释 | 分析报告 + 方法 + 不确定性 |
| BI Agent | 统一指标问答与报表消费 | KPI、钻取、Dashboard Spec |

三者可以组合，但责任要清楚：SQL Agent 提供可信数据，Data Agent 执行分析，BI Agent 提供标准化消费界面。

## 43.3 需求与架构

```text
Business Question
  -> Goal & Metric Resolver
  -> Dataset Discovery
  -> Data Quality Gate
  -> Analysis Planner
  -> Sandboxed Compute
  -> Statistical Validator
  -> Narrative + Evidence
  -> Review / Evaluation
```

分析计划应是结构化对象：数据集、指标、维度、时间窗口、对比基线、方法、完成条件和限制。Notebook 可以用于探索，但上线任务应转换为版本化代码或受控算子。

## 43.4 数据质量是前置 Gate

至少检查：

- Schema：字段、类型和枚举是否符合 Contract；
- Completeness：关键字段缺失率；
- Uniqueness：业务主键是否重复；
- Validity：范围和跨字段规则；
- Freshness：数据是否在 SLA 内；
- Reconciliation：总量是否与权威来源一致。

质量结果要参与状态机：`accepted -> profiling -> blocked/computing -> reviewed -> completed`。`blocked` 是正常业务结果，不是系统异常。

## 43.5 最小可运行 MVP

`example.py` 对六个月销售序列执行：Scope 校验、Schema/缺失/重复检查、基线均值、增长率、Z-Score 异常检测、解释和证据输出。

```bash
cd chapters/chapter43
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python example.py revenue
```

代码故意在最后一个月放入显著跃升。输出会标记统计异常，并建议继续检查价格、产品组合和一次性订单，而不会声称已经找到原因。

示例只使用 Python 标准库，便于看清算法和质量 Gate。生产环境可将数据 Adapter 换为 Warehouse，将质量检查换为 Great Expectations/dbt tests，将计算换为受控 Spark、DuckDB 或 Notebook Sandbox。

## 43.6 分析工具横向选择

| 工具类型 | 优点 | 局限 | 适合场景 |
| --- | --- | --- | --- |
| Python 标准库 | 透明、零依赖 | 数据规模有限 | 教学与轻量任务 |
| pandas / Polars | 表格分析效率高 | 内存与隔离需治理 | 单机交互分析 |
| DuckDB | 本地 SQL/列式分析 | 分布式能力有限 | 文件与中型数据 |
| Spark | 大规模分布式 | 启动与运维成本高 | 企业数据湖 |
| Great Expectations | 数据质量 Contract | 规则需要持续维护 | 质量 Gate |

Agent 应通过统一 Compute Tool 调用这些引擎，不能直接获得无限制 Python/Shell 权限。

## 43.7 沙箱与可复现性

代码执行沙箱至少限制：CPU、内存、磁盘、网络、时间、可导入包和数据路径。每次运行记录：

- 数据集 ID 与快照；
- 代码/算子版本；
- 参数和随机种子；
- 运行环境镜像；
- 质量结果和输出 Hash。

大结果保存到 Artifact Store，Context 中只传 Schema、摘要和引用。

## 43.8 评测与上线

离线评测覆盖：指标理解、切片选择、计算正确性、异常检测、引用完整性、拒绝错误数据、越权率和叙事过度推断。

上线采用 Copilot 模式：Agent 生成分析草稿，分析师审阅并标记“正确、部分正确、错误口径、证据不足”。这些反馈进入评测集，不直接作为未经治理的长期记忆。

## 43.9 常见踩坑

- 数据质量检查放在分析之后；
- 将统计异常直接写成业务根因；
- 同一指标在不同分析中重复实现；
- 让模型生成任意 Python 并访问生产网络；
- 只保存最终报告，不保存数据和计算 Evidence；
- 用“结果看起来合理”代替数值断言。

## 43.10 生产化清单

- 结构化 Analysis Plan；
- 质量失败可阻断；
- Compute Sandbox 与资源配额；
- 指标和数据集版本化；
- 统计方法与不确定性可见；
- Artifact、Trace 和 Evidence 可关联；
- 分析师审批与反馈闭环；
- 固定金标数据做持续回归。

## Summary

Data Agent 的企业价值是缩短“问题—数据—分析—验证—解释”链路，同时保持统计纪律和证据。MVP 展示的重点是先质量、后计算、再解释；接入 LLM 后也必须保留这条顺序。

## References

[1] Great Expectations. GX Core Introduction.
https://docs.greatexpectations.io/docs/core/introduction/

[2] NIST. AI Risk Management Framework.
https://airc.nist.gov/airmf-resources/airmf/
