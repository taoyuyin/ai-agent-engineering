# Chapter 17 Context Engineering：为每一步构建最小充分信息集

Part III Agent Architecture —— Agent 内部如何工作

Version: 2026-07

Last Updated: 2026-07-31

## Core Question

Chapter 8 已解释 Context 原理。本章进一步回答：Agent Runtime 如何在每一个 Step 动态选择、隔离、压缩和验证上下文？

## Chapter Conclusion

Context Engineering 是 Runtime 的编译阶段：它把 Goal、Policy、Plan、Memory、Knowledge、Tool schema 和 Observation 编译成模型本次决策的最小充分工作集。

## Learning Objectives

- 设计按 section 分区的 Context Policy
- 区分 instruction、trusted fact 与 untrusted data
- 管理工具 schema、历史和证据预算
- 比较供应商缓存与框架状态能力
- 运行 section quota Context MVP

## 17.1 从 Prompt 拼接到 Context Compiler

```text
Runtime State
├── Goal / Success Criteria
├── Policy / Identity
├── Current Plan Step
├── Relevant Memory
├── Retrieved Knowledge
├── Available Tools
└── Recent Observations
          ↓
Context Compiler
  normalize → authorize → rank → budget → render
          ↓
Model Request + Context Manifest
```

Context Manifest 应记录输入来源、版本、token、选择原因和丢弃原因，使一次模型决策可以复现。

## 17.2 Context Sections

推荐分区：

| Section | 信任级别 | 是否必需 | 超预算策略 |
|---|---|---:|---|
| System Policy | instruction | 是 | 失败/切换窗口 |
| Goal | instruction/data contract | 是 | 失败 |
| Current Step | instruction | 是 | 失败 |
| Tool Schema | capability contract | 按需 | 延迟加载 |
| Evidence | trusted/untrusted data | 按需 | rerank/摘要 |
| Memory | data | 可选 | top-k/压缩 |
| History | data | 可选 | 截断/摘要 |

不要让外部网页、邮件或工具文本与 System Policy 处于同一指令区。

## 17.3 Budget 不只是总 token

只设总预算会让某一类内容挤占全部空间。分区预算可以保证：

- policy 和 goal 永远存在；
- evidence 获得足够空间；
- history 不会无限增长；
- 工具 schema 按当前 capability 加载；
- 输出空间提前预留。

预算还要考虑多模态输入、reasoning token 与工具返回上限。

## 17.4 Compression 策略

| 策略 | 优点 | 风险 |
|---|---|---|
| Truncate | 快、确定 | 丢失关键尾部/中部 |
| Extract facts | 信息密度高 | 抽取错误 |
| Summarize | 适合历史 | 数字和例外丢失 |
| Retrieve on demand | 节省窗口 | 多一次延迟 |
| Hierarchical summary | 可处理长任务 | 误差逐层累积 |

高风险证据应保留原文引用和 hash。摘要不能成为唯一审计记录。

## 17.5 工具能力横向对比

| 层 | 工具 | 主要能力 | 不解决 |
|---|---|---|---|
| Provider | OpenAI conversation state / prompt caching | 多轮状态、前缀复用 | 业务优先级 |
| Provider | Anthropic context editing / caching | 清理旧工具结果、缓存 | 长期 Memory 治理 |
| Provider | Gemini long context / context caching | 大内容与缓存 | 任务相关性 |
| Runtime | LangGraph state/checkpoint/store | 状态持久化与恢复 | 自动预算策略 |
| Knowledge | LlamaIndex retriever/reranker | 知识选择 | Goal/Policy 组装 |
| 自研 | Context Compiler | 业务分区、权限、溯源 | 模型本身能力 |

Prompt Cache 优化计算，不减少 Context 占用；Checkpoint 保存状态，不代表所有状态都应发给模型。

## 17.6 Context Quality Evaluation

至少测量：

- required fact inclusion rate；
- evidence precision/recall；
- conflicting fact rate；
- token utilization；
- prompt injection resistance；
- 压缩前后任务正确率；
- 不同位置的事实利用率；
- 工具数量增加后的选择准确率。

Context 评估集应保存“必须包含”和“必须排除”的信息。

## Part II 能力在本章中的应用

Context Compiler 是 Token、Embedding 和 Context Window 的汇合点：

```text
Memory / Knowledge / Tools / Observations
        ↓ embedding + metadata retrieval
Authorized Candidates
        ↓ rerank + section quota + token budget
Model Context + Context Manifest
```

Embedding 负责候选召回；reranker 判断当前 Step 相关性；section quota 防止 History 挤掉 Policy、Goal 和 Evidence；token estimator 为输出预留窗口。Prompt Cache 只减少重复计算，不会扩大 Context Window。

本章示例保留 section budget、trusted/untrusted 边界和 dropped reason，展示候选集合到模型请求的确定性编译。

## 17.7 业务案例：企业知识 Agent

用户询问报销制度时：

1. Goal 与员工地区来自可信身份；
2. 检索当前生效政策；
3. 旧版本只用于冲突说明，不与新版本等权；
4. 网页内容作为不可信证据；
5. 输出引用条款、版本和生效日；
6. 若地区或政策版本无法确认，停止给确定结论。

## 17.8 Python MVP

```bash
python chapters/chapter17/example.py
python -m unittest discover -s chapters/chapter17 -p "test_*.py"
```

MVP 在总预算上增加 section quota，按优先级选择内容，并在渲染时保留 trusted/untrusted 边界及丢弃原因。

## Production Checklist

- [ ] 每次模型请求生成 Context Manifest
- [ ] Policy、Goal、Step 使用独立必需区
- [ ] 外部内容永远标记为 data
- [ ] 总预算之外设置 section quota
- [ ] 工具 schema 按需发现和加载
- [ ] 摘要保留原文引用
- [ ] 记录 token、选择与丢弃原因
- [ ] 用注入、冲突和长上下文集评估

## Summary

Context Engineering 决定模型在某一步能知道什么、能忽略什么、会信任什么。它是 Agent Runtime 的核心编译器，而不是 Prompt 模板管理的别名。

## Notes

Chapter 8 关注模型上下文原理；本章关注多步 Agent 中 Context 与 Runtime State 的工程边界。

## References

[1] LangGraph, Context concepts.
https://docs.langchain.com/oss/python/concepts/context

[2] Anthropic, Context windows.
https://platform.claude.com/docs/en/build-with-claude/context-windows

[3] Google, Context caching.
https://ai.google.dev/gemini-api/docs/caching

[4] OpenAI, Conversation state.
https://developers.openai.com/api/docs/guides/conversation-state

以上 URL 已在 2026-07-31 核对。
