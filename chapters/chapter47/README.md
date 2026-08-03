# Chapter 47 Customer Service Agent

Part VI Enterprise Practice —— 企业实践

Version: 2026-08

Last Updated: 2026-08-03

## 本章结论

Customer Service Agent 是“知识回答 + 客户数据工具 + 业务流程 + 人工升级”的组合。它不应以对话结束作为成功，而应以问题是否安全解决、动作是否正确、客户是否得到连续服务作为验收标准。

## 学习目标

- 设计意图、身份、知识、订单和工单协作链；
- 区分回答型 Tool 与有副作用的 Action Tool；
- 建立自动处理阈值与 Human Handoff；
- 维护会话摘要、证据和工单连续性；
- 评估解决率、转人工准确率、政策合规和客户体验。

## 47.1 业务背景

客户问“订单 A-1001 可以退款吗”。Agent 必须认证客户、校验订单归属、检索当前退款制度、计算时限与金额边界，并决定自动创建审核还是升级人工。

仅回答一段退款政策并没有完成任务；未验证归属就暴露订单信息则构成安全问题。

## 47.2 参考架构

```text
Channel Gateway
  -> Authentication / Session
  -> Intent & Risk Classifier
  -> Knowledge Retrieval
  -> Customer/Order Tools
  -> Policy Decision
  -> Action Workflow
  -> Response + Citation
  -> Human Handoff / QA
```

Channel Gateway 统一 Web、App、邮件和电话转写；CRM/OMS/工单系统通过受治理 Tool 暴露，不直接把后台凭证交给模型。

## 47.3 Tool 分级

| 类型 | 示例 | 控制 |
| --- | --- | --- |
| Public Read | 查询公开政策 | 引用与版本 |
| Private Read | 查询本人订单 | 认证、对象归属、脱敏 |
| Reversible Write | 创建/补充工单 | 幂等、审计、限频 |
| Financial Action | 退款、补偿 | 金额阈值、审批、反欺诈 |
| Irreversible Action | 关闭账号、法律承诺 | 默认人工处理 |

Agent 可以提出 Action Proposal，Workflow 决定是否执行。

## 47.4 最小可运行 MVP

本章示例完成：

- 根据问题检索版本化退款政策；
- 校验客户认证与订单归属；
- 计算签收天数和金额；
- 低风险订单创建自动退款审核；
- 超过边界时创建高优先级人工工单；
- 返回决定、动作、政策引用和质检字段。

```bash
cd chapters/chapter47
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python example.py "订单 A-1001 可以退款吗？"
```

示例把“自动退款”拆成“创建待库存确认的审核”，避免模型直接完成资金动作。

## 47.5 会话与工单连续性

转人工时传递结构化 Handoff Package：客户身份、已验证订单、用户目标、已执行工具、引用政策、失败原因、建议下一步和 Trace ID。人工坐席不应要求客户重新陈述全部信息。

长期记忆只保存经批准的客户偏好和摘要；支付、身份和敏感字段保留在源系统，通过 ID 引用。

## 47.6 Human Handoff 触发条件

- 身份或订单归属无法验证；
- 高金额、欺诈风险或法律风险；
- 政策冲突或无证据；
- 客户明确要求人工；
- 连续两次工具/理解失败；
- 情绪升级、自伤或安全事件；
- 需要系统没有授权的动作。

升级不是失败，而是风险控制成功。

## 47.7 Guardrail 与 Prompt Injection

客户输入、邮件附件和知识文档都可能包含恶意指令。模型输出不能直接成为 API 参数；Action Tool 使用固定 Schema、服务器端身份和业务校验。

隐私输出按最小披露原则，日志中对电话、地址、订单和聊天内容进行脱敏与保留周期管理。

## 47.8 评测与上线

核心指标：

- Intent Accuracy；
- Grounded Answer Rate；
- Safe Resolution Rate；
- Handoff Precision/Recall；
- Unauthorized Data Exposure，目标 0；
- First Contact Resolution、AHT、CSAT；
- 错误动作率、重复工单率和人工返工率。

先做 Agent Assist：向坐席建议答案；再开放低风险自助；资金和不可逆动作最后开放，并保留审批。

## 47.9 常见踩坑

- 把 FAQ Bot 当完整客服 Agent；
- 未认证就查询订单；
- 用 Prompt 决定退款权限；
- 转人工只传一段聊天记录；
- 追求转人工率越低越好；
- 客户输入直接进入 Tool 参数；
- 只评估语言满意度，不评估动作正确性。

## 47.10 生产化清单

- 统一身份与对象归属验证；
- Tool 权限和动作风险分级；
- 政策版本与引用；
- 幂等工单和资金流程；
- 结构化 Handoff；
- 隐私、脱敏和留存；
- 离线场景回归与在线质检；
- Kill Switch、回滚和人工兜底。

## Summary

客服 Agent 的完成条件是安全解决业务问题，而非输出一段自然语言。MVP 展示了身份、订单、政策、确定性决策、低风险动作和人工升级的完整闭环。

## References

[1] NIST. AI Risk Management Framework.
https://airc.nist.gov/airmf-resources/airmf/

[2] OWASP. GenAI Security Project.
https://genai.owasp.org/
