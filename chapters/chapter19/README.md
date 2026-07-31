# Chapter 19 Reflection：失败之后，系统应该重试、修复还是停止

Part III Agent Architecture —— Agent 内部如何工作

Version: 2026-07

Last Updated: 2026-07-31

## Core Question

Reflection 为什么不是“让模型再想一次”？如何基于验证信号选择 Retry、Repair、Replan、Escalate 或 Abort？

## Chapter Conclusion

Reflection 的工程本质是 Failure Diagnosis + Repair Policy。只有存在可观察错误和验证器时，反思才可能提高质量；无条件自我反思容易增加成本并重复错误。

## Learning Objectives

- 区分 Retry、Repair、Replan、Compensation 和 Escalation
- 建立错误 taxonomy 与修复策略
- 设计重试预算、退避和防循环机制
- 比较模型反思与确定性验证
- 运行错误驱动 Repair Controller MVP

## 19.1 Reflection Loop

```text
Observation
  ↓
Verifier
  ↓ failure(code, evidence)
Failure Classifier
  ↓
Repair Policy
  ├── retry same action
  ├── repair arguments
  ├── choose another tool
  ├── replan downstream
  ├── compensate side effect
  └── escalate / abort
```

“答案看起来不够好”不是可操作错误；`MISSING_DENOMINATOR`、`SCHEMA_INVALID` 才是。

## 19.2 Retry ≠ Repair

| 动作 | 是否改变输入/计划 | 适用 |
|---|---:|---|
| Retry | 否或只改时机 | timeout、rate limit |
| Repair Arguments | 是 | schema、范围错误 |
| Reroute | 改工具实现 | provider unavailable |
| Replan | 改下游步骤 | 假设错误、证据不足 |
| Compensation | 产生逆向业务动作 | 已发生副作用 |
| Escalate | 交给人/上层 | 权限、高风险、不确定 |

权限拒绝绝不能靠 Retry 解决。

## 19.3 Retry Policy

可靠重试需要：

- 仅针对明确 transient error；
- exponential backoff + jitter；
- max attempts 与 max elapsed time；
- 幂等键；
- circuit breaker；
- 尊重 `Retry-After`；
- 记录每次 reason code。

LLM 调用也可能失败，但重新生成会产生不同输出；它是新的尝试，不是字节级重放。

## 19.4 Verification 信号

| 场景 | 强验证器 |
|---|---|
| Coding | compile、unit test、static analysis |
| SQL | parser、只读策略、schema、row count |
| RAG | citation entailment、source presence |
| Data | metric definition、sample size、freshness |
| Workflow | state invariant、idempotency record |

模型 Judge 可做弱信号，但要校准偏差，并避免让同一模型只评价自己的表达风格。

## 19.5 Reflection 方法对比

| 方法 | 反馈来源 | 优点 | 风险 |
|---|---|---|---|
| Prompt self-reflection | 模型自身 | 简单 | 同源偏差 |
| Reflexion memory | 环境反馈 + 文字记忆 | 可跨尝试学习 | 错误记忆污染 |
| Deterministic verifier | 代码/规则 | 稳定、可审计 | 覆盖有限 |
| Model critic | 另一模型/角色 | 可评语义 | 成本与一致性 |
| Human review | 专家 | 适合高风险 | 延迟与规模 |

生产系统优先使用强验证器，再用模型补充开放语义判断。

## 19.6 防止反思循环

Runtime 应检测：

- 相同工具 + 相同参数重复；
- 相同错误连续出现；
- 计划版本没有实质变化；
- token/费用快速增长；
- critic 与 actor 相互否定；
- 没有新增 evidence。

达到阈值应降级、澄清或升级人工，而不是继续生成。

## 19.7 业务案例：Coding Agent

补丁编译失败：

1. 编译器返回结构化文件、行号、错误码；
2. Repair 只修改相关文件；
3. 重新编译；
4. 编译通过后运行目标测试；
5. 测试失败按 failure 分类；
6. 达到修复预算后交给开发者。

“让模型再审查一遍所有代码”范围过大且不可验证。

## 19.8 Python MVP

```bash
python chapters/chapter19/example.py
python -m unittest discover -s chapters/chapter19 -p "test_*.py"
```

MVP 把权限、schema、质量、transient 和未知错误映射到不同动作，并为 transient retry 设置独立 step budget。

## Production Checklist

- [ ] Verifier 输出稳定 failure code
- [ ] Retry 只处理 transient error
- [ ] 权限错误 fail closed
- [ ] 参数修复不绕过 schema
- [ ] Replan 只修改未完成部分
- [ ] 副作用有幂等与补偿
- [ ] 检测重复动作和无新增证据
- [ ] 达到预算后升级或停止

## Summary

Reflection 不是更长的思考，而是反馈驱动的控制策略。诊断越结构化，修复越局部，Agent 越可靠。

## Notes

本章不要求模型暴露私有思维链；工程 trace 记录 failure、decision、evidence 和 repair action。

## References

[1] Shinn et al., Reflexion.
https://arxiv.org/abs/2303.11366

[2] LangGraph, Workflows and agents.
https://docs.langchain.com/oss/python/langgraph/workflows-agents

[3] Temporal, Failure detection.
https://docs.temporal.io/encyclopedia/detecting-workflow-failures

以上 URL 已在 2026-07-31 核对。
