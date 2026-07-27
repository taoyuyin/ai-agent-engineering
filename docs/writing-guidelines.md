# 《AI Agent Engineering》写作规范

Version: 2026-07

Last Updated: 2026-07-27

## 1. 定位

本系列不是普通博客，也不是零散 Demo，而是一套持续演进的企业级 AI Agent 工程教材。

目标是同时服务三种载体：

- GitHub：源码与工程实现
- Book：系统化教材
- Blog / 公众号：文章传播与阶段性输出

三者共享同一个知识体系。

## 2. 写作原则

每篇文章应遵循以下原则：

- 先解释为什么，再解释是什么，最后解释怎么做
- 观点要有依据，避免无出处的趋势判断
- 概念必须落到工程问题
- 代码来自统一仓库，而不是每篇文章复制零散示例
- 文章、源码、架构图、引用资料保持同步

## 3. 推荐文章结构

每个 Chapter 建议包含：

- Title
- Part / Section
- Core Question
- Chapter Conclusion
- Learning Objectives
- 正文
- Summary
- Notes
- Version
- Last Updated
- References

## 4. 引用规范

引用必须优先使用第一手资料。

优先级如下：

1. Official：官方文档、官方博客、官方 GitHub、RFC、协议规范
2. Paper：arXiv、ACL、NeurIPS、ICML 等论文来源
3. Further Reading：高质量博客、社区讨论、源码分析，仅作为补充

不引用二手营销文章作为核心依据。

## 5. URL 验证

每篇文章发布前必须验证 References 中的 URL 可正常访问。

引用建议格式：

```text
References

[1] OpenAI.
A Practical Guide to Building Agents.
https://openai.com/business/guides-and-resources/a-practical-guide-to-building-ai-agents/

[2] Anthropic.
Building Effective AI Agents.
https://www.anthropic.com/engineering/building-effective-agents

[3] Google.
Agent Development Kit Documentation.
https://google.github.io/adk-docs/
```

## 6. Notes

文章中涉及定义差异、版本差异、厂商实现差异时，应使用 `Notes` 明确说明。

示例：

```text
Notes

本章中的 Agent 定义采用 OpenAI 2025 年《A Practical Guide to Building Agents》的工程定义。
不同厂商存在细微差异，后续章节会统一讨论。
```

## 7. Version 与 Last Updated

AI Agent 技术变化很快，每篇文章必须标记版本和更新时间。

示例：

```text
Version

2026-07

Last Updated

2026-07-27
```

## 8. 架构图风格

架构图保持简洁、一致、工程化。

推荐使用统一方向：

```text
User
  ↓
Agent
  ↓
Planner
  ↓
Tools / Memory / Model
  ↓
Result
```

避免每篇文章使用完全不同的图形风格。

## 9. 代码规范

所有代码都应来自统一工程：

```text
ai-agent-engineering/
├── chapters/
├── examples/
├── framework/
├── integrations/
├── prompts/
├── evaluation/
└── architecture/
```

每章代码应尽量对应一个清晰的 commit 或 tag，方便读者按章节 checkout 学习。

## 10. 核心路线

本系列坚持：

```text
Agent Runtime
  ↓
OpenAI SDK / Google ADK / LangGraph / CrewAI
```

先自己实现 Agent Runtime，再解释成熟框架为什么这样设计。

这样读者能理解框架背后的工程抽象，而不是只学习某个框架的 API。
