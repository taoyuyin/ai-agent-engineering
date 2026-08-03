# Chapter 46 Enterprise Knowledge Agent

Part VI Enterprise Practice —— 企业实践

Version: 2026-08

Last Updated: 2026-08-03

## 本章结论

Enterprise Knowledge Agent 的核心不是“上传文档后聊天”，而是建立知识摄取、版本、ACL、检索、引用、反馈和淘汰的完整生命周期。权限过滤必须发生在检索前，答案必须能回到有效版本的原始证据。

## 学习目标

- 设计 Document、Chunk、Metadata、ACL 和 Version Contract；
- 理解关键词、向量、混合检索和 Rerank 的取舍；
- 在检索前执行租户与用户组权限；
- 输出可验证引用并处理冲突、过期和无答案；
- 建立知识质量与回答质量双层评测。

## 46.1 业务背景

员工问“住宿费超过 800 元如何报销”。企业知识系统必须识别当前生效制度，排除旧版本，并确保提问者有权访问。只要其中一步失败，语言再流畅也可能造成合规事故。

知识 Agent 的事实源是受治理 Document，不是模型参数记忆。

## 46.2 知识生命周期

```text
Source Registration
  -> Parse / Normalize
  -> Classify / ACL
  -> Chunk / Metadata
  -> Index
  -> Retrieve / Rerank
  -> Answer / Citation
  -> Feedback / Evaluation
  -> Update / Supersede / Delete
```

每个文档至少保存：`doc_id`、Owner、版本、生效/失效时间、状态、ACL、来源 URI、内容 Hash、解析器版本和索引时间。

## 46.3 检索架构

| 方案 | 优点 | 局限 |
| --- | --- | --- |
| Keyword/BM25 | 精确词、编号和专有名词稳定 | 语义改写召回弱 |
| Vector | 语义相似能力强 | 数字、否定和专名可能失真 |
| Hybrid | 兼顾精确与语义 | 需要权重与归一化 |
| Reranker | 提升 Top-N 排序 | 增加延迟和成本 |

企业默认可以从 Hybrid + Metadata Filter 开始，再用真实问题评测，不应仅凭向量库品牌决定质量。

## 46.4 ACL 必须早于检索

正确顺序：

```text
Identity -> Tenant/Group ACL Filter -> Candidate Retrieval -> Rerank -> Context
```

错误做法是先全库召回，再让模型“不要引用无权内容”。此时敏感内容已经进入 Context。Vector Store、Search API 或知识服务必须支持可强制执行的 Metadata Filter；高敏领域可以使用物理分库。

## 46.5 最小可运行 MVP

`example.py` 实现一个零依赖知识 Agent：

- 文档包含版本、生效日期、状态和 ACL；
- 先过滤用户组和 `active` 状态；
- 对中英文文本生成关键词/CJK bigram；
- 计算轻量相关度并排序；
- 返回答案、版本化 Citation 和检索策略；
- 无证据时明确回答 `not_found`。

```bash
cd chapters/chapter46
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python example.py "住宿费超过 800 元如何报销？"
```

数据集中同时存在旧版制度和仅财务可见文档。普通员工只能召回当前有效、授权范围内的差旅制度。

## 46.6 Chunk 与 Context

Chunk 不应只按固定字符数切分。制度适合按条款、标题层级和表格语义切分；代码适合按 Symbol；工单适合按问题—处理—结果。

Chunk Metadata 应继承文档 ACL 和版本。Context Assembly 保留标题、章节、版本、日期和来源，不能只传裸文本。超长文档先检索局部证据，必要时使用层级摘要。

## 46.7 引用与冲突处理

引用质量要检查两件事：引用文档是否相关，以及引用片段是否真正支持结论。Agent 遇到以下情况应停止或升级：

- 两份同级有效制度相互冲突；
- 只有过期文档；
- 证据低于置信阈值；
- 问题要求个人法律/财务决定；
- 引用缺少 Owner 或版本。

模型不能静默合并冲突制度。

## 46.8 更新、删除与缓存

发布新版本后，旧 Chunk 必须下线或标记 superseded；删除源文档要传播到索引、缓存和备份策略。缓存键包含 ACL、文档版本和问题，权限变化时主动失效。

知识新鲜度 SLA 与业务风险匹配：产品手册可以每日同步，紧急安全公告需要分钟级传播。

## 46.9 评测与上线

分层评测：

- Retrieval：Recall@K、MRR、ACL 泄露率、新鲜度；
- Answer：事实正确、引用支持、完整性、拒答准确率；
- Operation：P95 延迟、索引延迟、失败率和成本；
- Business：自助解决率、人工转接率、制度误用事件。

测试集包含同义问题、旧制度、冲突制度、无权限问题、无答案和 Prompt Injection 文档。

## 46.10 常见踩坑

- ACL 只保存在前端；
- 新版本上线但旧 Chunk 仍被召回；
- 只评测答案，不评测 Retrieval；
- Citation 只指向文档首页；
- 用户反馈直接修改知识，无 Owner 审批；
- 把文档内容当作可信指令执行。

## 46.11 生产化清单

- Source、Owner、版本和生命周期；
- ACL-before-retrieval；
- 领域化 Chunk 与 Metadata；
- Hybrid/Rerank 基于评测选型；
- 引用支持性验证；
- 冲突、过期和无答案策略；
- 删除传播与缓存失效；
- 检索、回答和业务指标监控。

## Summary

企业知识 Agent 是 Knowledge Engineering、RAG、权限和生命周期的组合。MVP 用旧版本和受限文档证明：先决定什么证据可见，再讨论模型如何回答。

## References

[1] NIST. AI Risk Management Framework.
https://airc.nist.gov/airmf-resources/airmf/

[2] OWASP. GenAI Security Project.
https://genai.owasp.org/
