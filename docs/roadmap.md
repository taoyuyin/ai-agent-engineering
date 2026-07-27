# Roadmap

Version: 2026-07

Last Updated: 2026-07-27

## 项目愿景

`AI Agent Engineering` 希望形成一个长期演进的开源知识体系：

- 一本企业级 AI Agent 工程教材
- 一个可运行、可演进的 Agent Runtime 源码仓库
- 一组真实业务场景下的 Agent 案例
- 一套面向生产环境的评测、部署、安全与治理方法

## 第一阶段：教材与源码一体化

目标：完成基础目录、写作规范、章节结构和最小 Agent 示例。

重点内容：

- Chapter 01：软件为什么需要 AI Agent
- Chapter 02：AI Agent 的工程定义
- Chapter 03：最小 Agent Runtime
- Chapter 04：Tools 与外部系统
- Chapter 05：Memory 与 Context
- Chapter 06：Planner 与任务分解

## 第二阶段：自研 Agent Runtime

目标：实现一个教学版但结构完整的 Agent Runtime。

核心模块：

- `framework/runtime`
- `framework/planner`
- `framework/memory`
- `framework/tools`
- `framework/workflow`
- `framework/executor`

设计原则：

- 简单优先
- 可阅读优先
- 每个抽象都能对应文章解释
- 后续案例必须复用同一 Runtime

## 第三阶段：完整 Agent 案例

目标：把 Runtime 应用到多个完整案例。

计划案例：

- SQL Agent
- Data Agent
- Coding Agent
- RAG Agent
- Browser Agent
- Multi-Agent

每个案例应包含：

- 问题背景
- 架构设计
- 运行方式
- 核心代码
- 评测方法
- 局限性说明

## 第四阶段：企业级 Agent Engineering

目标：形成差异化方向：Enterprise AI Agent Engineering。

重点模块：

- Semantic Layer
- Metadata
- Governance
- Lineage
- Metrics
- Data Quality
- Warehouse / Lakehouse
- 权限与审计
- 企业级部署

关键问题：

- 为什么企业 Agent 离不开 Semantic Layer？
- 为什么 Data Agent 不应该直接生成 SQL？
- 如何让 Agent 理解企业指标和业务语义？
- 如何把数据质量、元数据、权限体系接入 Agent？
- 如何评估 Agent 在企业环境中的可靠性？

## 第五阶段：文档站点与生态

目标：将 GitHub、Book、Blog 和文档站点统一起来。

可能形态：

- `ai-agent-engineering`：教材配套源码与核心 Runtime
- `agent.itaoyuyin.com`：文档站点
- `itaoyuyin.com`：技术博客与系列文章
- 公众号：内容传播与更新通知

第一阶段只维护一个仓库。等 Runtime、案例和文档成熟后，再考虑拆分独立仓库。

## 版本与标签建议

建议后续按章节维护 tag：

```text
v0.1 / chapter01
v0.2 / chapter02
v0.3 / chapter03
...
```

读者可以通过 tag 回到某一章对应的代码状态。
