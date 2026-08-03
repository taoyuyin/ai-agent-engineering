# Chapter 42 SQL Agent

Part VI Enterprise Practice —— 企业实践

Version: 2026-08

Last Updated: 2026-08-03

## 本章结论

SQL Agent 的核心不是“自然语言生成 SQL”，而是把指标理解、Schema、数据权限、受限查询、结果解释和证据链组织成一条可审计的数据产品链路。

生产系统中，LLM 只能生成候选查询意图或 SQL IR；只读账户、Semantic Layer、SQL AST、租户过滤、资源配额和数据库权限必须由确定性系统执行。

## 学习目标

- 区分 Text-to-SQL Demo 与企业 SQL Agent；
- 设计自然语言到指标、维度、筛选条件的中间表示；
- 理解 Scope、行列权限、只读账户和查询 Guardrail 的分层；
- 返回 SQL、参数、指标版本和数据源组成的 Evidence；
- 建立执行准确率、安全性、延迟与成本评测。

## 42.1 业务背景

销售分析师提出“查询 2025 年各区域净销售额”。真实系统必须先回答：

- “净销售额”是含税还是不含税，是否扣除退款？
- 区域使用客户区域、门店区域还是销售组织？
- 用户能访问哪些租户、区域和字段？
- 查询是否会扫描整张明细表？
- 数字如何追溯到指标版本、SQL 和数据快照？

因此 SQL Agent 是 Semantic Layer 上的受治理查询入口，不是数据库超级用户。

## 42.2 需求与验收标准

功能要求：理解年份与区域；解析注册指标；生成参数化只读查询；返回聚合结果与证据。

非功能要求：

- 默认拒绝无 Scope 请求；
- 查询必须带 `tenant_id`；
- 只允许白名单表、指标和维度；
- 设置超时、扫描量、并发和结果行数上限；
- SQL、参数、调用者、指标版本和结果摘要进入审计；
- 同一问题在固定数据快照上结果可复现。

## 42.3 参考架构

```text
API / Identity
  -> Goal Parser
  -> Schema + Semantic Retrieval
  -> SQL IR Planner
  -> Policy & SQL AST Validator
  -> Read-only Query Service
  -> Result Validator
  -> Evidence-grounded Answer
  -> Trace / Evaluation
```

推荐先生成结构化 IR：

```json
{
  "metric": "net_revenue",
  "dimensions": ["region"],
  "filters": {"year": 2025},
  "limit": 20
}
```

再由可信编译器生成 SQL。这样可以在 SQL 出现前校验指标、维度、Join 和权限。

## 42.4 五层安全边界

| 层 | 主要控制 |
| --- | --- |
| 身份层 | OIDC/JWT 派生 tenant、actor、scopes |
| 语义层 | 指标、维度、Join 和敏感级别白名单 |
| 查询层 | AST、单语句、只读、LIMIT、复杂度预算 |
| 数据库层 | 独立只读角色、RLS、列权限、Statement Timeout |
| 输出层 | PII 脱敏、聚合阈值、Evidence 与审计 |

字符串黑名单只是教学第一层，不能替代 Parser 和数据库权限。PostgreSQL Row-Level Security 可以基于角色限制可见行；表 Owner 和具备 `BYPASSRLS` 的角色可能绕过策略，因此 Agent 查询角色必须单独设计。

## 42.5 最小可运行 MVP

本章 `example.py` 使用 SQLite 实现完整链路：

1. 从问题提取年份和区域；
2. 从 Semantic Registry 解析 `net_revenue`；
3. 校验 `sales:read`；
4. 自动加入 `tenant_id = ?`；
5. 生成参数化聚合 SQL；
6. 验证只读、表白名单和租户谓词；
7. 返回指标定义、结果和 Evidence。

```bash
cd chapters/chapter42
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python example.py "查询 2025 年各区域净销售额"
```

示例数据包含另一个租户的高额订单，用于说明租户谓词必须在查询中执行，而不是生成答案后过滤。

完整 Runtime、FastAPI、Docker 和测试工程见 [`examples/sql-agent/`](../../examples/sql-agent/README.md)。章节 MVP 用于看清控制链，完整案例用于学习服务化交付。

## 42.6 接入 LLM 的正确位置

LLM 适合：同义词理解、候选指标选择、歧义澄清、SQL IR 草拟、结果解释。

LLM 不负责：认证、最终授权、SQL 执行许可、资源限额、证据真实性。

当问题存在歧义时，Agent 应询问“区域指客户区域还是销售组织”，而不是静默选择。低置信度指标映射应停止执行。

## 42.7 工具选型

| 方案 | 优点 | 局限 | 适合阶段 |
| --- | --- | --- | --- |
| 手写规则 + SQLite | 离线、透明、易教学 | 领域有限 | MVP 与控制验证 |
| SQL Parser/AST | 结构化校验强 | 方言适配成本 | 生产 Guardrail |
| dbt/MetricFlow 类语义层 | 指标集中治理 | 需要数据建模体系 | 企业指标问答 |
| 数据仓库原生权限 | 靠近数据、难绕过 | 多引擎策略不同 | 生产强制控制 |

## 42.8 上线与评测

上线顺序：Shadow Query → 只读内部用户 → 小范围分析师 → 扩展领域。不要从“能生成 SQL”直接跳到全公司开放。

核心指标：

- Intent/Metric/Filter Accuracy；
- Execution Accuracy；
- Answer Groundedness；
- Unauthorized Access Rate，目标必须为 0；
- P95 延迟、扫描字节、单查询成本；
- 澄清率、空结果率和人工修正率。

评测集必须包含越权、Prompt Injection、超大查询、错误指标、空数据和同名字段。

## 42.9 常见踩坑

- 把完整数据库 DDL 全塞入 Context，既贵又降低选表质量；
- 让模型直接拼值而不是使用绑定参数；
- 只在应用层过滤租户；
- 指标没有 Owner 和版本；
- 查询成功就算任务成功，忽略结果单位和证据；
- 只测试正常问题，不测试恶意或昂贵查询。

## 42.10 生产化清单

- 认证信息只能由服务端构造；
- 使用 SQL IR 和 AST Validator；
- 数据库使用独立只读角色与 RLS；
- Semantic Layer 版本化；
- 设置超时、扫描量、并发与结果限制；
- Trace 记录 SQL 模板与脱敏参数；
- 敏感列禁止进入模型上下文；
- 建立离线回归、在线抽检和回滚机制。

## Summary

企业 SQL Agent 是受治理的数据查询 Runtime。MVP 展示了从指标解析、Scope、租户谓词、参数化 SQL 到 Evidence 的完整最小闭环；生产升级重点是语义层、AST、数据库原生权限和持续评测，而不是换一个更大的模型。

## References

[1] PostgreSQL. Row Security Policies.
https://www.postgresql.org/docs/current/ddl-rowsecurity.html

[2] OWASP. GenAI Security Project.
https://genai.owasp.org/
