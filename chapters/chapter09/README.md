# Chapter 9 Reasoning：把“会思考”变成可控制的执行过程

Part II LLM Foundations —— Agent 为什么能够工作

Version: 2026-07

Last Updated: 2026-07-31

## Core Question

CoT、ReAct、ToT、Reflection 和 Reasoning Model 分别解决什么问题？工程系统应如何控制推理成本、证据与失败边界？

## Chapter Conclusion

Reasoning 不是让模型输出越长越好的“思维过程”，而是让系统在不确定任务中形成中间状态、获取证据、验证结果并决定下一步。

生产 Agent 不应依赖或记录模型私有思维链。应观测的是计划、动作、工具参数、观察结果、验证结论、重试原因和最终证据。

## Learning Objectives

- 理解 Direct、CoT、Self-consistency、ReAct、ToT、Reflection 的差异
- 依据任务不确定性、可验证性、延迟和费用选择策略
- 区分模型推理能力与 Agent Runtime 控制能力
- 构建有步数预算、证据验证和 trace 的 Reasoning Controller
- 避免把“推理更长”误认为“答案更可靠”

## 9.1 从一次生成到闭环求解

传统调用是：

```text
Question → Model → Answer
```

Agent 面对的数据分析、故障排查和代码修复通常需要：

```text
Goal
  ↓
Plan → Action → Observation
  ↑                  ↓
  └──── Repair ← Verify
                    ↓
                  Answer
```

这里的关键变化不是展示更多自然语言，而是把求解过程分成可执行、可验证、可中止的状态。

## 9.2 主要推理范式

### Direct

模型直接回答。延迟和成本最低，适合简单分类、抽取、改写和已有上下文中的明确问题。任务复杂时容易跳步或编造。

### Chain-of-Thought（CoT）

CoT 通过中间推理提高复杂任务表现。工程上可以要求结构化解题步骤或决策摘要，但不要把供应商内部的私有思维链当作可依赖 API，也不要将其作为审计证据。

### Self-consistency

对同一问题生成多个候选路径，再投票或评分。它能降低单一路径偶然错误，但费用近似随候选数增加，且同源候选可能共同犯错。

### ReAct

ReAct 交替执行 Reason/Act/Observation，适合需要搜索、数据库、代码执行等外部工具的任务。生产系统应把 Reason 收敛为“下一步操作摘要”，把真实证据留在 Observation 中。

### Tree of Thoughts（ToT）

ToT 同时保留多个候选状态，进行扩展、评分和剪枝。适合搜索空间大、可以评估局部状态的问题；不适合所有日常请求，否则延迟和 token 快速膨胀。

### Reflection / Reflexion

系统根据失败结果生成可执行修复意见，再重试。Reflection 只有在存在验证信号时才有意义；让同一个模型无证据地“再想一遍”，可能只是更自信地重复错误。

## 9.3 技术横向对比

| 策略 | 工具交互 | 候选路径 | 需要验证器 | 成本 | 适用任务 |
|---|---|---:|---:|---:|---|
| Direct | 否 | 1 | 可选 | 低 | 抽取、分类、简单问答 |
| CoT | 否 | 1 | 建议 | 中 | 数学、规则推导 |
| Self-consistency | 否 | N | 投票/评分 | 高 | 有稳定答案空间的推理 |
| ReAct | 是 | 动态 | 是 | 中高 | 搜索、数据、运维 Agent |
| ToT | 可选 | 树状 | 强依赖 | 很高 | 规划、组合搜索 |
| Reflection | 可选 | 重试 | 强依赖 | 中高 | 可测试、可反馈任务 |

选型可用四个问题：

1. 一次生成是否足够？
2. 是否必须访问外部世界？
3. 中间结果能否被代码、规则或人验证？
4. 错误的业务代价是否值得更多计算？

## 9.4 Reasoning Model 不等于 Agent

Reasoning Model 提供更强的任务分解和推断能力，但仍不能替代：

- 工具权限和执行隔离；
- 状态持久化与恢复；
- 步数、时间和费用预算；
- 业务验证器；
- 人工审批；
- 失败分类与审计。

模型决定“建议下一步做什么”，Runtime 决定“是否允许做、如何做、做到何时停止”。

## 9.5 供应商与框架能力对比

| 层 | 产品 / 工具 | 主要控制面 | 优点 | 工程注意点 |
|---|---|---|---|---|
| 模型/API | OpenAI Reasoning | reasoning effort、工具、多轮状态、摘要能力 | 统一推理与工具工作流 | 不依赖隐藏 CoT，管理费用和上下文 |
| 模型/API | Anthropic | effort / thinking 与 tool use | 可控制整体工作强度 | 具体参数随模型版本变化 |
| 模型/API | Gemini Thinking | thinking budget/level、summary、function calling | 多模态与工具组合 | 不同模型支持能力需运行时探测 |
| Runtime | LangGraph | graph、state、checkpoint、interrupt | 状态清晰、可恢复 | 推理策略和验证器仍需设计 |
| 优化层 | DSPy | 以指标优化模块和 prompt | 适合有训练/评估集的系统 | 依赖高质量指标和样本 |
| 自研 Runtime | Controller + Verifier | 策略、预算、证据、权限 | 行为可控 | 维护成本更高 |

不要用某个模型的当前参数名设计领域层。应定义供应商无关的 `ReasoningPolicy`，例如：

```python
ReasoningPolicy(
    strategy="react",
    effort="medium",
    max_steps=6,
    max_candidates=2,
    require_verification=True,
)
```

适配器再把它映射到不同供应商 API。

## 9.6 Reasoning Controller 架构

Controller 至少包含：

- **Strategy Selector**：Direct、ReAct、候选搜索或人工升级；
- **Planner**：输出结构化任务和依赖；
- **Tool Router**：只允许白名单动作；
- **Evidence Store**：保存观察结果及来源；
- **Verifier**：检查完整性、计算、schema、业务规则；
- **Budget Manager**：限制步骤、token、费用和墙钟时间；
- **Trace**：记录可公开的操作状态，而非私有 CoT。

建议 trace：

```json
{
  "kind": "verification",
  "status": "failed",
  "reason_code": "MISSING_DENOMINATOR",
  "evidence_ids": ["query-17"],
  "next_action": "query_active_customers"
}
```

这比保存一大段“我认为……”更适合审计、统计和回放。

## 9.7 Verification 是推理可靠性的支点

不同任务需要不同验证器：

| 任务 | 验证方式 |
|---|---|
| SQL Agent | 只读解析、成本预估、结果 schema、抽样复核 |
| Coding Agent | 编译、单测、静态分析、安全扫描 |
| Data Agent | 指标定义、分母、时间窗口、数据新鲜度 |
| RAG Agent | 引用存在、证据支持、冲突检测 |
| Workflow Agent | 状态不变量、幂等键、补偿结果 |

一个模型给另一个模型打分可以作为弱信号，但不应取代确定性验证。

## 9.8 业务案例：客户流失分析 Agent

用户问：“为什么 enterprise 客户最近流失增加？”

合理流程：

1. 固化指标定义和观察窗口；
2. 查询流失率，并与历史基线比较；
3. 按地区、产品、合同类型拆分；
4. 查询工单、使用率、续约报价等候选因素；
5. 检查样本量和数据新鲜度；
6. 区分相关性、假设和已验证因果；
7. 输出证据、局限和下一步实验。

危险流程则是先生成一个听起来合理的故事，再选择支持故事的数据。

## 9.9 Python MVP：有边界的 ReAct Runtime

目录：

```text
chapter09/
├── example.py
└── reasoning_runtime/
    ├── tools.py
    ├── runtime.py
    └── test_runtime.py
```

运行：

```bash
python chapters/chapter09/example.py
python -m unittest discover -s chapters/chapter09 -p "test_*.py"
```

示例故意使用确定性 Planner，展示最重要的 Runtime 边界：

- 工具注册表；
- 最大步骤数；
- plan/action/observation/verification trace；
- 缺失证据时失败；
- 最终结论区分观察与待验证假设。

接入模型时，只替换 Planner/Decision Adapter，不删除边界控制。

## 9.10 Production Checklist

- [ ] 简单任务默认 Direct，不滥用复杂推理
- [ ] 为步骤、候选、token、费用和时间设硬上限
- [ ] 工具动作经过独立授权
- [ ] 关键结论关联 evidence id
- [ ] 数学、schema、代码优先用确定性验证
- [ ] 重试按错误类型执行，避免无限 Reflection
- [ ] 记录操作摘要，不记录或索取私有思维链
- [ ] 高风险副作用要求人工确认
- [ ] 评估正确率、完成率、步骤数、成本和超时率

## Summary

Reasoning 的工程价值是管理不确定性，而不是生成更长文本。Agent 能否可靠工作，取决于推理策略、外部证据、验证器和 Runtime 边界能否形成闭环。

## References

[1] Wei et al., Chain-of-Thought Prompting Elicits Reasoning in Large Language Models.
https://arxiv.org/abs/2201.11903

[2] Wang et al., Self-Consistency Improves Chain of Thought Reasoning.
https://arxiv.org/abs/2203.11171

[3] Yao et al., ReAct.
https://arxiv.org/abs/2210.03629

[4] Yao et al., Tree of Thoughts.
https://arxiv.org/abs/2305.10601

[5] Shinn et al., Reflexion.
https://arxiv.org/abs/2303.11366

[6] OpenAI, Reasoning guide.
https://developers.openai.com/api/docs/guides/reasoning

[7] Google, Gemini thinking.
https://ai.google.dev/gemini-api/docs/thinking

以上 URL 已在 2026-07-31 核对。
