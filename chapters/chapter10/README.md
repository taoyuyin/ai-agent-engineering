# Chapter 10 Function Calling

Part II LLM Foundations —— Agent 为什么能够工作

Version: 2026-07

Last Updated: 2026-07-31

## Core Question

为什么模型可以调用工具？Function Calling 与普通文本输出有什么本质区别？

## Chapter Conclusion

Function Calling 把模型输出从自然语言扩展为结构化动作描述。

对 Agent 工程而言，它是 LLM 与外部系统之间的桥梁：模型负责选择工具和生成参数，Runtime 负责校验、执行、记录和反馈。

## Learning Objectives

完成本章后，你应该能够理解：

- Function Calling 的基本流程
- JSON Schema 为什么重要
- Tool Registry 如何设计
- Runtime 为什么必须校验参数
- Function Calling 与 Agent Tool 的关系

## 10.1 原理剖析：从文本到动作

普通 LLM 输出是文本：

```text
你可以查询销售数据库。
```

Function Calling 输出是结构化动作：

```json
{
  "tool": "query_sales",
  "arguments": {
    "region": "east",
    "quarter": "2026Q2"
  }
}
```

模型并不会真的执行函数。

真正执行函数的是 Agent Runtime。

因此，Function Calling 的职责边界是：

```text
Model selects tool and arguments
  ↓
Runtime validates arguments
  ↓
Runtime executes tool
  ↓
Runtime sends observation back to model
```

## 10.2 JSON Schema 的意义

Tool 参数必须有结构。

如果没有 schema，模型可能输出：

- 错误字段
- 缺少必填参数
- 类型错误
- 越权参数
- 无法执行的工具名

JSON Schema 的作用是把工具能力表达为机器可校验的接口。

对软件工程师来说，这和 API Contract 很像。

## 10.3 架构设计：Tool Registry

一个最小 Tool Registry 包含：

- tool name
- description
- input schema
- permission scope
- handler

```text
Tool Registry
  ↓
Model Tool Selection
  ↓
Argument Validation
  ↓
Execution
  ↓
Observation
```

## 10.4 工具横向对比

| 工具 / 框架 | 工具调用方式 | 工程特点 |
|---|---|---|
| OpenAI | Function / Tool Calling、Structured Outputs | Schema 和工具执行边界清晰 |
| Anthropic | Tool use | 强调 workflow 和 agent 组合 |
| Google ADK | Tool 抽象 | 与 Agent / Runner / Session 集成 |
| LangGraph | Tool node / graph state | 工具调用可编排和恢复 |
| 本书 framework | 自实现 Tool Registry | 理解参数校验和执行闭环 |

## 10.5 业务场景案例：SQL Agent

用户问：

```text
查询华东区本季度销售额。
```

模型应输出工具调用：

```json
{
  "tool": "query_metric",
  "arguments": {
    "metric": "sales",
    "region": "east",
    "period": "current_quarter"
  }
}
```

Runtime 必须检查：

- 用户是否有权限查该指标
- region 是否合法
- period 是否合法
- metric 是否来自 Semantic Layer
- 工具返回是否可解释

## Python MVP

本章示例实现一个可运行的 Tool Registry、参数校验和工具执行闭环。

运行：

```bash
python chapters/chapter10/example.py
```

## Summary

Function Calling 让模型可以输出结构化动作，但它不是完整 Agent。真正的 Agent Runtime 必须负责工具注册、参数校验、权限、安全、执行和观察结果反馈。

## References

[1] OpenAI.  
Function Calling Guide.  
https://platform.openai.com/docs/guides/function-calling

[2] Schick et al.  
Toolformer.  
https://arxiv.org/abs/2302.04761

[3] Google.  
Agent Development Kit Documentation.  
https://adk.dev/

以上 URL 已在 2026-07-31 验证可访问。
