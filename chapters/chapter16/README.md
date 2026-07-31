# Chapter 16 Memory：让 Agent 跨步骤和会话保留有效信息

Part III Agent Architecture —— Agent 内部如何工作

Version: 2026-07

Last Updated: 2026-07-31

## Core Question

Conversation History、Checkpoint、向量检索和 Long-term Memory 有什么区别？Agent 应该记住什么，又必须忘记什么？

## Chapter Conclusion

Memory 是受策略控制的读写系统，不是无限增长的聊天记录。可靠 Memory 必须定义类型、写入条件、命名空间、检索、更新、冲突、过期和删除。

## Learning Objectives

- 区分 Working、Episodic、Semantic、Procedural Memory
- 区分 thread checkpoint 与跨 thread store
- 设计 tenant/subject namespace 和更新版本
- 比较框架 Memory 与存储实现
- 运行一个隔离、检索、更新和遗忘 MVP

## 16.1 Memory 分类

| 类型 | 保存内容 | 生命周期 | 示例 |
|---|---|---|---|
| Working | 当前 Run 中间状态 | step/run | 当前计划与观察 |
| Episodic | 发生过的事件 | 跨 run | 上次退款失败 |
| Semantic | 稳定事实与偏好 | 长期 | 用户偏好中文报告 |
| Procedural | 可复用流程知识 | 长期、版本化 | 月报生成步骤 |

Context 是“本次可见什么”，Memory 是“可供未来取回什么”。Memory 只有被检索并组装进 Context 后才影响模型。

## 16.2 Memory Pipeline

```text
Candidate Event
  ↓ Write Policy
Extract / Normalize / Classify
  ↓
Tenant + Subject Namespace
  ↓
Store + Version + TTL
  ↓
Retrieve → Rank → Validate
  ↓
Context Assembler
```

不是每条对话都值得长期保存。写入策略应考虑稳定性、未来价值、敏感性、置信度和用户同意。

## 16.3 写入、更新与冲突

“用户喜欢简洁报告”可能后来变成“审计报告需要完整细节”。Memory 应：

- 保存来源和时间；
- 使用稳定 key 更新，不无限追加同一事实；
- 保留版本或 supersedes 关系；
- 对冲突事实按来源、时效和置信度处理；
- 低置信推断不得伪装为用户声明。

## 16.4 Retrieval

Memory Retrieval 不只做向量相似度。常见评分：

```text
score =
semantic_similarity
+ recency
+ importance
+ source_trust
+ task_relevance
- conflict_penalty
```

权限过滤必须发生在检索期间，而不是拿到结果后再删除，否则可能产生侧信道和日志泄漏。

## 16.5 工具横向对比

| 工具/层 | Thread State | Cross-thread Memory | 持久化实现 | 适用 |
|---|---:|---:|---|---|
| OpenAI Agents SDK Sessions | 是 | 由应用设计 | SQLite/custom/session backend | 会话历史 |
| LangGraph Checkpointer | 是 | 否 | memory/SQLite/Postgres 等 | checkpoint、resume |
| LangGraph Store | 可 | 是 | InMemory/Postgres/Redis 等 | 用户长期记忆 |
| Google ADK Session/State/Memory | 是 | 是 | Runtime service | ADK Agent |
| Vector DB | 否 | 是 | 专用向量索引 | 语义检索 |
| Relational DB | 是 | 是 | SQL/事务 | 事实、版本、审计 |

向量数据库适合召回，不适合单独承担强一致版本、删除证明和事务。企业 Memory 常组合 SQL 元数据与向量索引。

## 16.6 安全与隐私

Memory 是高风险数据面：

- 跨租户泄漏；
- 保存敏感信息和秘密；
- 错误事实长期污染；
- 用户无法删除；
- 恶意输入被提升为程序性记忆。

最低要求是 tenant/subject namespace、数据分类、TTL、加密、访问审计和删除接口。Tool Result 中的指令不应自动写成 Procedural Memory。

## Part II 能力在本章中的应用

Embedding 只负责 Memory 候选召回，Memory Runtime 负责完整读写治理：

```text
Write: Event → Write Policy → Normalize → Embed
             → Metadata + Vector + Version

Read:  Task → Query Embedding → Tenant/Subject Filter
             → Semantic + Confidence Rank
             → Context Candidate
```

Token/Context 决定最终装入多少 Memory；Embedding 模型版本应随索引记录；升级时采用双索引或重建；删除同时传播到事实存储与向量索引。

本章示例将租户/主体过滤放在评分之前，并组合词项、语义相似度和 confidence，说明 Vector DB 是索引而不是 Memory 本身。

## 16.7 业务案例：客户服务 Agent

可保存：

- 客户明确选择的语言；
- 已验证产品版本；
- 未解决工单 ID；
- 经确认的沟通偏好。

不应保存：

- 一次性验证码；
- 支付卡信息；
- 模型猜测的情绪标签；
- 未经确认的医疗/法律敏感推断；
- 已关闭工单的完整长对话（除非合规要求）。

## 16.8 Python MVP

```bash
python chapters/chapter16/example.py
python -m unittest discover -s chapters/chapter16 -p "test_*.py"
```

MVP 实现 memory type、tenant/subject namespace、置信度、版本更新、词项检索和 forget。生产系统需加入持久化、向量召回、TTL、加密和 deletion audit。

## Production Checklist

- [ ] 定义 Memory 类型和写入策略
- [ ] tenant、subject、purpose 多层隔离
- [ ] 保存来源、时间、置信度和版本
- [ ] 检索阶段执行权限过滤
- [ ] 冲突和过期有明确规则
- [ ] 用户可查看、更正和删除
- [ ] 不保存 secrets 与无依据敏感推断
- [ ] 评估 recall、污染率和跨租户隔离

## Summary

好的 Memory 不追求“什么都记住”，而追求在正确权限下保存少量稳定、有用、可纠正的信息。

## Notes

本章使用确定性的轻量 Embedding 演示语义 Memory Retrieval，便于无外部模型运行。真实项目应替换为经过评估的 Embedding 模型并记录模型版本；向量数据库选型与 Python API 已在 Chapter 7 展开。

## References

[1] LangGraph, Persistence and Store.
https://docs.langchain.com/oss/python/langgraph/persistence

[2] OpenAI Agents SDK, Sessions.
https://openai.github.io/openai-agents-python/sessions/

[3] Google ADK, Sessions.
https://adk.dev/sessions/

以上 URL 已在 2026-07-31 核对。
