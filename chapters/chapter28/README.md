# Chapter 28 Guardrails：为不可信智能建立确定性边界

Part IV Agent Engineering —— 如何构建企业级 Agent

Version: 2026-07

Last Updated: 2026-07-31

## Core Question

如何在 Input、Context、Tool、Memory 和 Output 全链路控制安全、权限与业务风险？

## Chapter Conclusion

Guardrails 不是输出敏感词过滤器，而是一组分层控制：deterministic policy 优先，分类模型和 LLM judge 补充，Human approval 承担高风险判断。模型输出始终只是未经信任的提案。

## Learning Objectives

- 建立 Agent threat model 和信任边界
- 区分 input、retrieval、tool、output 与 runtime guardrail
- 选择 allow、block、transform、review 和 observe 动作
- 对比 OpenAI、NeMo、Guardrails AI 与策略引擎
- 运行一个 fail-closed、带审计的分层 Guardrail Pipeline

## 28.1 Agent 扩大了攻击面

传统聊天模型主要产生文本；Agent 还能检索私有数据、调用工具和产生副作用。主要风险包括：

- 直接或间接 Prompt Injection；
- 敏感信息泄漏与跨租户访问；
- 模型生成越权工具参数；
- 不安全输出被下游代码执行；
- memory poisoning 和知识源污染；
- 高风险动作缺少确认、幂等与审计。

“在 system prompt 写禁止”不能形成安全边界。

## 28.2 分层防御

```text
Identity / Tenant / Scope
        ↓
Input Guardrail
        ↓
Retrieval + Context Guardrail
        ↓
Model proposes action
        ↓
Tool Policy + Approval + Sandbox
        ↓
Output Schema + DLP + Citation Check
        ↓
Audit / Detection / Incident Response
```

每一层面对不同信任对象，不能由单个 moderation API 代替。

## 28.3 控制类型

| 控制 | 适合 | 特征 |
|---|---|---|
| schema/allowlist/regex | 字段、工具、标识符、格式 | 快、确定、可解释 |
| IAM/Policy Engine | 主体、资源、动作、上下文授权 | 服务端强制 |
| 分类模型 | toxicity、PII、注入概率 | 有误判，需阈值 |
| LLM judge | 复杂语义和业务 rubric | 成本高、非确定 |
| Sandbox | 代码、浏览器、文件系统 | 限制爆炸半径 |
| Human approval | 金钱、删除、发布等高风险动作 | 延迟高但责任清晰 |

检测不等于阻断。每条规则应定义 action、reason、owner、severity、fallback 和 audit event。

## 28.4 Tool Guardrail

正确顺序是：

1. 模型生成 typed proposal；
2. Runtime 验证 schema；
3. 重新从身份系统取得 actor scope；
4. Policy Engine 对 resource + action 授权；
5. 高风险动作绑定对象版本并审批；
6. 使用 idempotency key 执行；
7. 结果归一、脱敏后回到模型。

模型不能自己声明“用户有管理员权限”。

## 28.5 Prompt Injection 防御

注入防御依赖组合：

- 把网页、邮件和检索内容标记为 untrusted data；
- 不将外部文本拼入 system policy；
- 限制工具集合和参数，而非让模型自由执行；
- 对敏感工具使用数据流和来源检查；
- 默认最小权限，未知情况 fail closed；
- 用真实攻击样本持续 red team。

单纯匹配“ignore previous instructions”只能作为一层低成本信号。

## 28.6 工具横向对比

| 工具 | 侧重点 | 优点 | 局限 | 适用 |
|---|---|---|---|---|
| OpenAI Agents SDK Guardrails | input/output/tool checks | 与 Agent run 集成直接 | 企业 IAM/策略仍需外接 | OpenAI Agents |
| NVIDIA NeMo Guardrails | 对话、内容、检索与执行 rail | DSL 与运行时能力丰富 | 学习和运行复杂度 | 对话安全编排 |
| Guardrails AI | validator、structured output | Python 集成和校验生态 | 不是完整 IAM/沙箱 | 输出/数据校验 |
| OPA/Cedar | 通用授权策略 | 确定、可审计、与模型无关 | 不理解开放语义 | 工具/数据授权 |
| Llama Guard/分类器 | 内容风险分类 | 可本地部署 | 阈值、语言和领域需评估 | 内容安全信号 |
| 自建 Pipeline | 领域规则组合 | 最贴合业务风险 | 维护和红队成本 | 强领域系统 |

## 28.7 企业案例：采购 Agent

采购 Agent 可以查询供应商和创建采购草稿，但不能直接付款。邮件内容先作为不可信上下文处理；Tool Gateway 验证供应商 ID、金额、成本中心和用户权限。超过阈值的采购进入双人审批，审批绑定草稿 hash，修改金额后旧审批失效。所有 block、review 和 execute 事件进入不可变审计。

## 28.8 Python MVP

`guardrail_runtime` 展示四个阶段：

- input 注入检测；
- context provenance 与不可信指令剥离；
- tool scope 和高风险参数 review；
- output schema 与敏感字段脱敏；
- 全部 decision 写入 audit。

```bash
python3 chapters/chapter28/example.py
python3 -m unittest discover -s chapters/chapter28 -p "test_*.py"
```

## 28.9 Production Readiness Checklist

- [ ] 完成 data flow 与 tool threat model
- [ ] 模型输出视为不可信 proposal
- [ ] IAM/tenant/scope 在服务端重新验证
- [ ] 高风险动作有审批、幂等和补偿
- [ ] 外部内容与 system instruction 隔离
- [ ] 未知策略、依赖故障默认 fail closed
- [ ] 日志和 trace 做最小化与脱敏
- [ ] block/review/false-positive/security incident 可观测
- [ ] 定期使用真实攻击集回归

## Summary

Guardrails 的目标不是消灭模型不确定性，而是让不确定输出无法越过确定的身份、数据和动作边界。安全来自纵深防御与可恢复运行，不来自一条万能 Prompt。

## Notes

OWASP Top 10 和 NIST AI RMF 提供风险框架，不直接替代应用级控制。具体规则必须结合行业法规、业务损失和组织权限模型。

## References

[1] OpenAI Agents SDK, Guardrails.
https://openai.github.io/openai-agents-python/guardrails/

[2] NIST, AI Risk Management Framework.
https://www.nist.gov/itl/ai-risk-management-framework

[3] OWASP, Top 10 for LLM Applications.
https://genai.owasp.org/llm-top-10/

[4] NVIDIA, NeMo Guardrails.
https://docs.nvidia.com/nemo/guardrails/latest/

[5] Guardrails AI Documentation.
https://guardrailsai.com/guardrails/docs

以上 URL 已在 2026-07-31 核对。
