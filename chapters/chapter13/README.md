# Chapter 13 Goal：把用户意图编译成可执行契约

Part III Agent Architecture —— Agent 内部如何工作

Version: 2026-07

Last Updated: 2026-07-31

## Core Question

“帮我分析一下销售”为什么还不是可执行目标？Runtime 如何得到约束、权限和可验证的完成条件？

## Chapter Conclusion

Goal 不是一段 Prompt，而是 Runtime 的输入契约。高质量 Goal 同时描述 objective、constraints、success criteria、allowed actions、risk 和 evidence requirements。

## Learning Objectives

- 区分 Intent、Goal、Task 与 Success Criterion
- 将模糊请求转换为结构化 GoalSpec
- 识别缺失信息并选择澄清或安全默认值
- 设计可由代码或人工验证的完成条件
- 运行 Goal Compiler 与 Evaluator MVP

## 13.1 从 Intent 到 Goal

```text
User Intent
  ↓  parse + resolve identity/context
Goal Draft
  ↓  clarify + policy validation
Goal Contract
  ↓
Planner / Workflow
```

示例输入：“把最近销售不好的门店处理一下。”

它缺少：

- “最近”的时间窗口；
- “不好”的指标和阈值；
- “处理”是生成建议还是关闭门店；
- 用户可访问的区域；
- 输出格式和审批要求。

Agent 不应通过想象填满高风险空白。

## 13.2 Goal Contract

```json
{
  "objective": "识别华东区 2026-07 收入环比下降超过 10% 的门店",
  "constraints": ["只读数据", "排除新开业不足 30 天门店"],
  "success_criteria": ["指标定义已引用", "异常门店有证据"],
  "allowed_tools": ["get_sales_summary"],
  "risk_level": "medium"
}
```

Success Criterion 应满足：

- 可观察，而不是“结果要好”；
- 与证据对应；
- 有范围与阈值；
- 在预算内可验证；
- 不与约束冲突。

## 13.3 Goal Validation

验证分四层：

| 层 | 问题 |
|---|---|
| Syntax | 字段是否完整、类型是否正确 |
| Semantic | objective 与 criteria 是否一致 |
| Policy | 用户是否有权请求该目标 |
| Feasibility | 当前工具、数据和预算能否完成 |

高风险 Goal 还需检查副作用、审批链和回滚方案。

## 13.4 澄清还是默认

| 缺失项 | 建议 |
|---|---|
| 展示格式 | 可使用安全默认值 |
| 低风险排序方式 | 可默认并告知 |
| 数据范围/租户 | 必须从身份确定，不让模型猜 |
| 金额、收件人、删除范围 | 必须澄清或审批 |
| 成功标准 | 若无法推导，应澄清 |

澄清问题也有成本。Runtime 应只问会改变计划、安全或结果的问题。

## 13.5 工具与框架对比

| 方案 | Goal 表达 | 优点 | 局限 |
|---|---|---|---|
| JSON Schema / Pydantic | typed GoalSpec | 明确、可验证、跨模型 | 语义冲突仍需业务规则 |
| OpenAI Agents SDK | instructions、input、output type、guardrails | 与 Runner 集成 | 领域 Goal 仍需应用建模 |
| LangGraph | typed state + entry node | Goal 可进入持久状态 | schema 不自动产生验收标准 |
| Google ADK | agent instruction + session state | 运行时上下文丰富 | 应建立独立领域契约 |
| BPMN/Workflow Input | 表单与流程变量 | 确定性、审计好 | 动态开放目标表达较弱 |

任何框架的 Prompt 字段都不应成为企业 Goal 的唯一存储。

## 13.6 Goal 与 Planner 的边界

- Goal 描述 **what + constraints + done**；
- Planner 描述 **how + order + dependencies**；
- Tool 描述 **capabilities**；
- Evaluator 判断 **done or not**。

若 Goal 直接包含固定执行步骤，它可能已经是 Workflow；若 Planner 可以修改成功标准，边界就失控了。

## Part II 能力在本章中的应用

Goal Compiler 消费模型能力，但不把自然语言直接当作执行合同：

```text
User Request + Identity + Context
        ↓ reasoning / extraction
Structured Goal Proposal
        ↓ schema + policy validation
GoalSpec
```

Token/Context 决定澄清材料的范围，Reasoning 识别隐含约束，Structured Output 把结果限制为 `GoalSpec`。Runtime 再验证 success criteria、allowed tools 和 risk level，并同时保留原始请求与编译结果。

本章示例把结构化模型提案编译成 GoalSpec，再用独立 Evaluator 对证据验收；模型负责理解，Runtime 负责合同。

## 13.7 业务案例：客服退款

用户说“给这个客户退钱”。Goal Compiler 应补齐：

- 订单 ID 与租户；
- 可退金额和币种；
- 退款原因；
- 用户权限；
- 是否超出自动审批阈值；
- 完成条件：退款网关返回成功且账务事件落库。

“模型生成了退款成功文案”不是完成条件。

## 13.8 Python MVP

```bash
python chapters/chapter13/example.py
python -m unittest discover -s chapters/chapter13 -p "test_*.py"
```

MVP 将字典编译为不可变 `GoalSpec`，强制 objective、success criteria 和 risk 合法，再用 evidence map 评估完成状态。

## Production Checklist

- [ ] Goal 使用版本化结构，而非仅保存 Prompt
- [ ] 包含 objective、constraints、criteria、tools、risk
- [ ] 身份和租户由可信系统提供
- [ ] 高风险歧义必须澄清
- [ ] success criteria 可由证据验证
- [ ] Goal 变更产生新版本和审计事件
- [ ] Planner 无权修改业务验收标准

## Summary

Goal 是自然语言世界与确定性 Runtime 之间的编译产物。Goal 越模糊，Planner 的自由度越大，系统风险也越高。

## Notes

Goal Understanding 可以使用模型，但 Goal Validation 必须结合确定性 schema、身份、策略和业务规则。

## References

[1] OpenAI Agents SDK, Agents.
https://openai.github.io/openai-agents-python/agents/

[2] LangGraph, Graph API.
https://docs.langchain.com/oss/python/langgraph/graph-api

[3] JSON Schema.
https://json-schema.org/understanding-json-schema/

以上 URL 已在 2026-07-31 核对。
