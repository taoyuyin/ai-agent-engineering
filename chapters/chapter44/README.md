# Chapter 44 BI Agent

Part VI Enterprise Practice —— 企业实践

Version: 2026-08

Last Updated: 2026-08-03

## 本章结论

BI Agent 应建立在 Semantic Layer 上：模型负责理解问题和组织解释，指标定义、Join、权限和聚合由受治理语义服务执行。没有统一指标层的 BI Agent，只会更快地产生彼此矛盾的数字。

## 学习目标

- 理解 Metric、Dimension、Entity、Time Grain 和 Drilldown；
- 区分 BI Agent 与自由探索型 Data Agent；
- 用 Semantic Layer 保证跨报表指标一致；
- 设计行级权限、Dashboard Spec 和可追溯洞察；
- 评估指标准确率、钻取成功率和业务采用率。

## 44.1 业务背景

管理者希望用自然语言查询 KPI、解释报表和下钻区域。BI Agent 的困难不是画图，而是让“收入”“活跃客户”“转化率”等词在所有部门拥有同一可治理定义。

一个指标 Contract 至少包含：名称、描述、表达式、实体、时间粒度、允许维度、单位、Owner、版本、认证状态和数据延迟。

## 44.2 参考架构

```text
Chat / BI Extension
  -> Intent + Ambiguity Resolver
  -> Semantic Catalog Retrieval
  -> Governed Metric Query API
  -> RLS / Column Policy
  -> Result + Definition + Lineage
  -> Insight Generator
  -> Dashboard / Drilldown Spec
```

Agent 不应绕过 Metric API 直接查询底表。用户问“收入”但目录中存在 `gross_revenue` 和 `net_revenue` 时，应澄清而不是猜测。

## 44.3 Semantic Layer 的核心对象

| 对象 | 例子 | 作用 |
| --- | --- | --- |
| Metric | `net_revenue` | 统一计算口径 |
| Dimension | `region`、`month` | 切片与分组 |
| Entity | `customer`、`order` | 定义 Join 语义 |
| Time Grain | day/month/quarter | 统一时间聚合 |
| Access Policy | allowed_regions | 约束数据可见性 |
| Lineage | mart → model → metric | 追溯来源和影响 |

指标定义应该在数据建模层集中维护。dbt Semantic Layer 的官方文档也强调集中定义指标并让下游工具一致消费。

## 44.4 最小可运行 MVP

本章 `example.py` 实现一个内存 Semantic Layer：

- 注册 `net_revenue` 和 `order_count`；
- 只允许 `region`、`month` 两个维度；
- 请求上下文只授权 east/north 区域；
- 聚合可见事实表；
- 返回指标定义、结果、洞察、Dashboard Spec 和 Evidence。

```bash
cd chapters/chapter44
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python example.py net_revenue region
```

数据中包含 south 区域，但输出不会出现它，说明权限必须在聚合前应用。

## 44.5 BI Agent、NL2SQL 与 Dashboard Copilot

| 方案 | 控制力 | 灵活性 | 风险 |
| --- | --- | --- | --- |
| NL2SQL | 中 | 高 | 口径和 Join 容易漂移 |
| Semantic BI Agent | 高 | 中高 | 依赖指标建模质量 |
| Dashboard Copilot | 高 | 中 | 局限于既有报表上下文 |
| Data Agent | 中 | 最高 | 需要更强沙箱和分析审核 |

企业默认路径应是 Semantic BI Agent；开放式探索再委派给 Data Agent。

## 44.6 洞察生成的约束

洞察不能只是“华东最高”。应包含：比较对象、时间范围、绝对变化、相对变化、贡献度、证据和置信限制。对根因只能生成候选假设，并提供下一步 Drilldown。

Dashboard Spec 应是结构化对象，而不是让模型直接生成任意前端代码。渲染服务负责主题、可访问性、数据格式和安全链接。

## 44.7 权限与缓存

缓存键必须包含：指标版本、筛选条件、时间范围、用户/权限边界和数据快照。不能把高权限用户的结果复用给低权限用户。

行级策略尽量下推到仓库或语义服务。输出还应执行小样本抑制、敏感维度限制和导出权限。

## 44.8 评测与上线

核心指标：

- Metric Resolution Accuracy；
- Filter/Time Grain Accuracy；
- 数值与官方 Dashboard 一致率；
- Drilldown Success Rate；
- Unauthorized Slice Rate；
- Insight Support Rate；
- 查询延迟、缓存命中和采用率。

上线前使用财务或经营团队签字的 KPI 金标集，覆盖同义词、跨期比较、权限差异、口径变更和空数据。

## 44.9 常见踩坑

- 指标定义藏在 Prompt；
- 允许 Agent 任意 Join；
- 只比较最终数字，不验证筛选和时间粒度；
- Dashboard 缓存忽略权限；
- 将排序第一名包装成“深度洞察”；
- 指标变更后不重跑历史评测。

## 44.10 生产化清单

- 指标 Contract、Owner 和版本；
- Metric API 而非底表直连；
- 权限在查询/聚合前执行；
- Dashboard Spec 结构化；
- 缓存包含权限和数据版本；
- 洞察绑定数值 Evidence；
- KPI 金标回归；
- 口径变更具备影响分析和回滚。

## Summary

BI Agent 的 Intelligence 建立在可信 Semantic Layer 之上。MVP 展示了指标注册、维度白名单、行级可见性、聚合、洞察和 Dashboard Contract 的最小闭环。

## References

[1] dbt Labs. dbt Semantic Layer.
https://docs.getdbt.com/docs/use-dbt-semantic-layer/dbt-sl

[2] PostgreSQL. Row Security Policies.
https://www.postgresql.org/docs/current/ddl-rowsecurity.html
