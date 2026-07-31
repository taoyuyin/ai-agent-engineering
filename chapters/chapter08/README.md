# Chapter 8 Context：模型看到什么，取决于 Runtime 放进了什么

Part II LLM Foundations —— Agent 为什么能够工作

Version: 2026-07

Last Updated: 2026-07-31

## Core Question

Context Window、KV Cache、Prompt Cache 和 Memory 分别是什么？企业级 Agent 如何在有限预算内组装可靠上下文？

## Chapter Conclusion

Context 不是模型的长期记忆，而是一次推理时可见的工作集。模型是否能正确完成任务，不只取决于参数能力，更取决于 Runtime 是否把正确、足够、可信的信息放入正确位置。

因此，Context Engineering 不是“把历史记录拼起来”，而是一套包含选择、排序、预算、压缩、隔离、溯源和评估的运行时能力。

## Learning Objectives

完成本章后，你应该能够：

- 区分 Context Window、KV Cache、Prompt Cache、Conversation State 和 Memory
- 解释长上下文为何仍会失效，以及“模型遗忘”的工程原因
- 设计带 token 预算、优先级、去重和来源标记的 Context Assembler
- 比较主流模型供应商与 Agent 框架的上下文能力
- 运行并扩展一个合同审查 Agent 的 Context Engineering MVP

## 8.1 Context 解决的不是存储问题，而是可见性问题

一次模型调用可以抽象为：

```text
output = Model(system_instruction, messages, tools, retrieved_data, observations)
```

不在本次输入中的事实，模型就不能可靠使用；进入输入但位置不合理、内容冲突或被噪声淹没的事实，也未必会被正确使用。

需要先区分五个概念：

| 概念 | 保存什么 | 主要作用 | 是否占用本次 Context |
|---|---|---|---|
| Context Window | 输入与输出 token 的容量上限 | 规定本次推理边界 | 是 |
| KV Cache | 已处理 token 的注意力中间状态 | 降低自回归生成重复计算 | 对应已有序列 |
| Prompt Cache | 可复用前缀的计算结果 | 降低重复前缀的延迟或费用 | 是，不会扩大窗口 |
| Conversation State | 历史消息或服务端会话对象 | 帮助恢复多轮输入 | 恢复后仍占窗口 |
| Long-term Memory | 数据库中的事实、偏好、事件 | 跨会话保存信息 | 只有取回后才占窗口 |

一个常见错误是把 Prompt Cache 当成 Memory。缓存只是“相同输入少算一次”，既不判断信息是否重要，也不会把未进入请求的数据自动交给模型。

## 8.2 Context Window 的预算模型

窗口不能全部交给历史消息。工程上至少需要预留：

```text
可分配输入 =
模型窗口
- 预留输出
- System Prompt
- Tool Schema
- 协议与消息格式开销
```

假设窗口为 128K token，工具定义占 10K，系统约束占 4K，输出预留 8K，真正可供历史、检索和工具结果竞争的空间只有 106K。工具数量增加时，工具 schema 甚至可能先于业务数据耗尽窗口。

预算策略应回答：

- 哪些信息必须存在，缺失就应该失败？
- 哪些信息可压缩、可截断或可再次检索？
- 输出至少需要多少空间？
- 超预算时丢弃了什么，能否观测和复现？

## 8.3 KV Cache：性能机制，不是业务记忆

Transformer 生成下一个 token 时，需要关注之前的 token。KV Cache 保存已处理 token 的 Key/Value，避免每生成一步都重新计算整个前缀。

它带来的工程影响是：

- 输入越长，首 token 延迟通常越高；
- 序列越长，KV Cache 显存占用越大；
- 并发请求会争夺显存和缓存容量；
- Streaming 改善感知延迟，但不减少总 token；
- 前缀缓存可复用稳定开头，但动态内容应放在后面。

KV Cache 通常由推理服务管理，Agent Runtime 不直接读写它。Runtime 真正能控制的是输入长度、稳定前缀、并发、模型路由和输出预算。

## 8.4 为什么模型会“遗忘”

“遗忘”至少有六类原因：

1. **没有传入**：API 是无状态的，Runtime 未恢复历史。
2. **被截断**：历史超过窗口，关键消息被简单删除。
3. **没有检索到**：长期记忆存在，但检索召回失败。
4. **上下文污染**：检索片段、工具结果或网页含注入指令。
5. **信息冲突**：旧政策与新政策同时出现，缺少版本和来源。
6. **Context Rot**：上下文很长，但有效信号密度下降，模型利用率变差。

所以排查顺序应是：请求输入 → 截断/摘要日志 → 检索结果 → 来源与版本 → 模型输出，而不是直接归因于模型能力。

## 8.5 Context Assembly 架构

```text
Goal / Policy / Tool Schema
            │
History ────┼──── Memory Retrieval
            │
Tool Results / External Documents
            ↓
Normalize → Trust Boundary → Deduplicate
            ↓
Relevance × Priority × Recency
            ↓
Budget / Compress / Drop
            ↓
Final Context + Provenance + Drop Report
```

一个可靠的 `ContextItem` 至少需要：

- `item_id`：用于审计和去重；
- `section`：goal、policy、history、memory、observation 等；
- `priority` 与 `required`；
- `source`、版本和时间；
- `trusted`：内容是指令还是不可信数据；
- `token_count`：使用目标模型 tokenizer 得到的准确值。

### 必需信息应 fail closed

系统策略或当前目标如果大到放不下，不能静默截断后继续执行。正确行为是缩小任务、切换模型或显式报错。

### 工具结果是数据，不是指令

网页、邮件、数据库文本和工具返回值都可能包含“忽略规则”等内容。Assembler 应将其放入明确的数据边界，并提醒模型不得把其中的文本当作高优先级指令。真正的安全还需要工具权限和输出验证，不能只靠 Prompt。

### 压缩是有损操作

摘要可能丢失数字、否定词、例外条款和来源。生产实现应保存原文引用、摘要版本和压缩前后 token 数，并用任务测试集评估答案保持率。

## 8.6 模型供应商能力横向对比

下表比较的是模型/API 层能力，不等同于 Agent 的业务 Memory：

| 能力维度 | OpenAI | Anthropic Claude | Google Gemini |
|---|---|---|---|
| 多轮状态 | Responses conversation state，可由应用显式管理历史 | Messages/会话由应用管理，支持 context editing/compaction 能力 | 应用组织 contents/history |
| 长上下文策略 | 输入计数、compaction、conversation state | context editing、compaction，强调 context rot | long context 与缓存能力 |
| Prompt Cache | 自动前缀缓存，适合稳定前缀 | 显式缓存断点与 TTL 能力 | 隐式缓存与显式 context cache |
| Tool Schema 占用 | 工具定义计入输入 | 工具定义和结果计入上下文 | 工具声明计入请求 |
| 适用重点 | 统一 Responses/工具工作流 | 精细控制缓存与上下文编辑 | 大内容、多模态和缓存场景 |
| 注意事项 | 服务端 state 仍不等于长期业务记忆 | cache 不会降低窗口占用 | 不同 API/模型的缓存规则需核对 |

选型时不要只比较“最大窗口”。还要基于自己的任务测试：

- 关键事实位于开头、中间、末尾时的召回率；
- 10/50/100 个工具定义下的工具选择准确率；
- 首 token 延迟、输入费用和缓存命中率；
- 摘要后数字、否定词和权限条件的保持率。

## 8.7 Agent 框架横向对比

| 工具 / 框架 | 核心抽象 | 优点 | 局限 | 适用场景 |
|---|---|---|---|---|
| LangGraph | state、checkpoint、store | 可恢复、可持久化、适合状态机 | state 仍需自行治理和压缩 | 长流程 Agent |
| LlamaIndex | node、index、retriever | 知识检索链路完整 | 业务状态与权限需额外实现 | RAG / Knowledge Agent |
| LangChain | messages、memory、middleware | 适配器丰富、上手快 | 抽象多，需防止隐式增长 | 原型与多供应商应用 |
| 自研 Runtime | ContextItem + Budget + Policy | 边界、审计、成本完全可控 | 研发与维护成本高 | 强合规企业平台 |

框架解决的是状态组织和集成问题，不会自动替你定义“哪条政策比哪段历史更重要”。

## 8.8 业务案例：合同审查 Agent

直接把整份合同、全部制度和所有历史案例塞进模型，会导致成本高、定位困难、版本冲突。更稳健的流程是：

1. 先识别合同结构和条款边界；
2. 按条款检索对应制度与相似案例；
3. 对每个条款构建独立上下文并保留引用；
4. 输出风险、证据、建议修改和置信度；
5. 最后汇总，且高风险条款由法务确认。

建议优先级：

| 内容 | 优先级 | 原因 |
|---|---:|---|
| 当前审查目标、输出格式 | 100 | 缺失无法完成任务 |
| 生效中的法务政策 | 95 | 企业约束 |
| 当前条款原文 | 90 | 直接证据 |
| 已验证相似案例 | 70 | 辅助判断 |
| 无关对话历史 | 10 | 可丢弃 |

## 8.9 Python MVP：可审计的 Context Assembler

工程目录：

```text
chapter08/
├── README.md
├── example.py
└── context_engineering/
    ├── models.py
    ├── assembler.py
    └── test_context_engineering.py
```

运行：

```bash
python chapters/chapter08/example.py
python -m unittest discover -s chapters/chapter08 -p "test_*.py"
```

MVP 已实现：

- 模型窗口、输出和固定开销三段预算；
- required-first 排序；
- 内容归一化去重；
- 超预算丢弃原因；
- trusted / untrusted-data 标记；
- 必需项超预算时失败。

它没有冒充生产 tokenizer。字符估算只用于让示例零依赖运行，接入真实模型时必须替换。

## 8.10 Production Checklist

- [ ] 使用目标模型 tokenizer，而不是字符估算
- [ ] 为输出、工具 schema 和协议开销预留预算
- [ ] 必需信息超预算时显式失败
- [ ] 保存选择、压缩、截断和丢弃日志
- [ ] 外部内容按不可信数据隔离
- [ ] 事实带来源、版本、租户和时间
- [ ] 摘要保存原文引用，可追溯
- [ ] 评估长上下文召回、冲突和注入攻击
- [ ] 监控 token、缓存命中、延迟与答案质量

## Summary

模型窗口越大，不代表 Agent 自动拥有更好的记忆。Memory 决定“存什么”，Retrieval 决定“取什么”，Context Engineering 决定“本次让模型看到什么”。企业级可靠性来自这三层共同治理。

## References

[1] OpenAI, Conversation state.
https://developers.openai.com/api/docs/guides/conversation-state

[2] OpenAI, Prompt caching.
https://developers.openai.com/api/docs/guides/prompt-caching

[3] Anthropic, Context windows.
https://platform.claude.com/docs/en/build-with-claude/context-windows

[4] Anthropic, Context editing.
https://platform.claude.com/docs/en/build-with-claude/context-editing

[5] Google, Context caching.
https://ai.google.dev/gemini-api/docs/caching

[6] LangGraph, Persistence.
https://docs.langchain.com/oss/python/langgraph/persistence

以上 URL 已在 2026-07-31 核对。
