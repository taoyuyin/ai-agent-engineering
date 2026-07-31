# Chapter 24 Prompt Engineering：把 Prompt 当作软件资产

Part IV Agent Engineering —— 如何构建企业级 Agent

Version: 2026-07

Last Updated: 2026-07-31

## Core Question

Prompt 如何从一次性字符串，演进为可版本化、可评估、可发布、可回滚的工程资产？

## Chapter Conclusion

企业 Prompt Engineering 的核心不是“写出一句神奇提示词”，而是建立 Prompt Architecture、Registry、Evaluation 和 Release Gate。Prompt 是 Agent 行为配置的一部分，但权限、状态机和安全策略不能只靠 Prompt 保证。

## Learning Objectives

- 拆分 Prompt 的策略、任务、上下文、示例与输出契约
- 建立不可变版本、环境晋级、灰度和回滚机制
- 区分 Prompt 单测、离线评估与在线实验
- 对比厂商 Prompt 管理与独立评估工具
- 运行一个严格变量检查、带校验和的 Prompt Registry

## 24.1 为什么字符串拼接会失控

开发阶段把 Prompt 写在业务代码里很快，生产阶段却会出现：

- 无法回答某次结果使用了哪个 Prompt；
- 修改一句话导致工具选择和 JSON 格式同时回归；
- system policy、用户输入和检索内容混在同一信任域；
- 多团队复制同一 Prompt，修复无法同步；
- 线上问题只能改代码、重新发布，不能快速回滚。

Prompt 的输出是概率性的，但 Prompt 的输入结构、版本与发布过程应是确定性的。

## 24.2 Prompt Architecture

```text
Policy Layer         不可被业务覆盖的安全与行为边界
Task Layer           角色、目标、完成条件
Context Layer        当前状态、检索证据、工具结果
Demonstration Layer  少量高质量示例
Tool Contract        工具名称、参数 schema、调用约束
Output Contract      JSON Schema、引用与错误格式
```

这些层可以最终序列化为一条模型请求，但在代码和配置中应保持独立。检索文档和用户文本属于不可信数据，不能与 system instruction 等价。

## 24.3 设计原则

1. **明确任务和成功标准**：说明“完成”的可检查条件。
2. **边界清晰**：用字段、标签或消息角色隔离 instruction 与 data。
3. **最少必要上下文**：更多 Token 不等于更多有效信息。
4. **结构化输出**：能用 schema 验证的，不靠自然语言约定。
5. **模型适配**：不同模型族、版本和 reasoning 模式分别评估。
6. **失败可见**：信息不足时返回缺口，不鼓励模型猜测。

## 24.4 Prompt 版本模型

推荐记录：

```text
prompt_id + semantic_version + checksum
model_family + model_snapshot
input_schema + output_schema
owner + change_reason + evaluation_report
created_at + promoted_at + rollback_target
```

已发布版本不可原地覆盖。新版本先通过 lint、样本回放和安全测试，再进入 staging、canary、production。版本号本身不足以证明内容未变，运行记录还应保存 checksum。

## 24.5 评估与发布

```text
Edit → Static Validation → Offline Dataset → Safety Red Team
     → Shadow/Canary → Online Metrics → Promote or Roll Back
```

评估至少覆盖：

- 格式有效率、任务成功率和工具选择准确率；
- 引用完整性、幻觉率和拒答质量；
- P50/P95 延迟、输入/输出 Token、单次成本；
- Prompt injection、越权工具和敏感信息测试。

LLM-as-a-judge 适合评价风格和开放任务，但应校准 judge、固定 rubric，并与确定性检查和人工抽检组合。

## 24.6 工具横向对比

| 方案 | 主要能力 | 优点 | 局限 | 适用场景 |
|---|---|---|---|---|
| OpenAI Prompts/Evals | Prompt、模型调用与评估闭环 | 与 OpenAI 平台集成紧 | 多模型治理需额外抽象 | OpenAI 为主的应用 |
| Anthropic Console | Claude Prompt 开发与测试 | 模型指南和工作流直接 | 平台范围集中于 Claude | Claude 专项优化 |
| Google AI Studio | Gemini Prompt 原型与调试 | 多模态实验方便 | 企业版本治理需外接 | Gemini 原型验证 |
| LangSmith | Prompt Hub、Dataset、Trace、Eval | LangChain 生态完整 | 平台耦合与托管权衡 | LangChain/LangGraph |
| Promptfoo | 配置化多模型回归与红队 | 本地/CI 友好，开源 | 生产 trace 不是核心 | 多模型发布门禁 |
| 自建 Registry | 版本、权限、审批完全自定义 | 可接企业 Git/CMDB | 研发与维护成本高 | 强治理、私有化 |

不要只比较 UI。真正的选型维度是：版本不可变性、数据集、评估器、CI、审批、审计、模型覆盖和数据边界。

## 24.7 企业案例：客服 Prompt 发布

客服团队将“退款解释”Prompt 从代码中迁出。每个版本绑定政策知识快照和 300 条离线样本。CI 检查 JSON Schema、引用、越权动作和成本；新版本先承接 5% 只读流量。当任务成功率上升且投诉、人工转接、延迟无显著退化后晋级。任一安全门禁失败，Registry 将 active pointer 回滚到上一版本。

## 24.8 Python MVP

本章 `prompt_runtime` 实现：

- 不可变 Prompt 版本；
- 模板变量与声明严格一致；
- active version 切换；
- 内容 checksum 和输出 schema；
- canary 版本在激活前不影响生产。

```bash
python3 chapters/chapter24/example.py
python3 -m unittest discover -s chapters/chapter24 -p "test_*.py"
```

MVP 不调用模型，因为本章首先验证的是模型之外的配置控制面。

## 24.9 Production Readiness Checklist

- [ ] Prompt 分层并隔离不可信数据
- [ ] input/output schema 可机器验证
- [ ] 发布版本不可原地修改
- [ ] Run 记录 prompt/model/tool/knowledge 版本
- [ ] 离线数据集覆盖正常、边界和攻击样本
- [ ] 发布有 canary、门禁和一键回滚
- [ ] 日志不保存密钥和未脱敏个人数据
- [ ] 权限和业务规则在确定性代码中执行

## Summary

Prompt Engineering 的工程终点是 PromptOps：可重复、可比较、可审计地改变 Agent 行为。好 Prompt 很重要，但可靠性来自 Prompt、schema、evaluation、guardrail 和 runtime 的组合。

## Notes

各平台对 Prompt 对象、缓存和评估 API 的实现变化较快；本章强调稳定的工程职责，不把某个厂商 UI 当作通用架构。

## References

[1] OpenAI, Prompt engineering.
https://developers.openai.com/api/docs/guides/prompt-engineering

[2] OpenAI, Working with evals.
https://developers.openai.com/api/docs/guides/evals

[3] Anthropic, Prompt engineering overview.
https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/overview

[4] Google, Prompt design strategies.
https://ai.google.dev/gemini-api/docs/prompting-strategies

[5] Promptfoo Documentation.
https://www.promptfoo.dev/docs/

以上 URL 已在 2026-07-31 核对。
