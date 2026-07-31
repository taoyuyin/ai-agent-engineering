# Chapter 11 MCP

Part II LLM Foundations —— Agent 为什么能够工作

Version: 2026-07

Last Updated: 2026-07-31

## Core Question

为什么需要 MCP？它和普通 API、Function Calling、Agent Tool 有什么关系？

## Chapter Conclusion

MCP（Model Context Protocol）的目标，是为模型应用连接外部工具、资源和上下文提供统一协议。

对 Agent 工程而言，MCP 解决的是生态连接问题：不要让每个 Agent 框架都用不同方式接入工具和数据源。

## Learning Objectives

完成本章后，你应该能够理解：

- 为什么单纯 Function Calling 不足以形成工具生态
- MCP 的 Client / Server / Tool / Resource 关系
- MCP 与 Agent Runtime 的集成位置
- MCP 和企业系统权限治理的关系
- 如何用 Python 模拟一个最小 MCP 风格调用

## 11.1 原理剖析：为什么需要 MCP

Function Calling 解决了模型如何表达工具调用。

但它没有完全解决：

- 工具如何被发现
- 工具 schema 如何暴露
- 工具结果如何标准化
- 资源如何提供给模型
- 不同应用如何复用同一个工具服务
- 权限和连接如何管理

如果每个 Agent 项目都自己写一套工具协议，生态会非常碎。

MCP 的价值在于提供统一连接层。

## 11.2 MCP 的核心角色

一个简化 MCP 结构：

```text
Host Application
  ↓
MCP Client
  ↓
MCP Server
  ├── Tools
  ├── Resources
  └── Prompts
```

- Host：运行 Agent 的应用
- Client：连接 MCP Server 的客户端
- Server：暴露工具、资源和提示词
- Tool：可执行能力
- Resource：可读取上下文或数据

## 11.3 架构设计：MCP 在 Agent 中的位置

在企业 Agent 架构中，MCP 可以位于 Tool Layer：

```text
Agent Runtime
  ↓
Tool Router
  ↓
MCP Client
  ↓
MCP Servers
  ↓
Enterprise Systems
```

Agent 不需要直接知道每个企业系统 API 的细节。

它只需要通过 Tool Router 找到合适 MCP Server，并按 schema 调用工具。

## 11.4 工具横向对比

| 方式 | 优点 | 局限 |
|---|---|---|
| 直接 API 调用 | 简单直接 | 每个系统单独适配 |
| Function Calling | 模型能结构化选择工具 | 工具发现和生态复用不足 |
| MCP | 标准化工具和资源连接 | 需要 Server 生态和权限治理 |
| Dify / 平台连接器 | 产品化程度高 | 可定制性依赖平台 |
| 本书 framework | 教学实现 Tool Router | 先理解协议边界 |

## 11.5 业务场景案例：企业数据 Agent

一个 Data Agent 可能需要连接：

- 指标系统
- 数据仓库
- 元数据平台
- 数据质量平台
- BI 系统
- 权限系统

如果每个连接都写在 Agent 里，Agent 会变得非常臃肿。

更合理的设计是：

- Agent 负责目标、计划和上下文
- MCP Server 负责暴露企业能力
- 权限系统负责控制访问边界

## Python MVP

本章示例模拟一个 MCP 风格 Server：它暴露 tool schema，Client 根据 schema 调用工具。

运行：

```bash
python chapters/chapter11/example.py
```

## Summary

MCP 不替代 Agent，也不替代 Function Calling。它更像 Agent 工具生态的连接协议，让工具和资源可以被标准化暴露、发现和调用。

## References

[1] Model Context Protocol.  
Introduction.  
https://modelcontextprotocol.io/docs/getting-started/intro

[2] OpenAI.  
A Practical Guide to Building Agents.  
https://openai.com/business/guides-and-resources/a-practical-guide-to-building-ai-agents/

以上 URL 已在 2026-07-31 验证可访问。
