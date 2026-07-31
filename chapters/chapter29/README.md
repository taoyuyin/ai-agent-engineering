# Chapter 29 Evaluation：用证据决定 Agent 能否上线

Part IV Agent Engineering —— 如何构建企业级 Agent

Version: 2026-07

Last Updated: 2026-07-31

## Core Question

非确定性的 Agent 应如何离线评估、在线监控、回归对比和发布门禁？

## Chapter Conclusion

Agent Evaluation 不是一个总分，而是覆盖结果、轨迹、安全、延迟和成本的分层证据系统。没有黄金数据集、trace 和发布门禁，就无法可靠改 Prompt、模型、工具或知识。

## Learning Objectives

- 建立 case、dataset、evaluator、experiment、report 抽象
- 区分 deterministic、human 与 LLM-as-a-judge
- 评估最终答案、工具轨迹和系统约束
- 对比主流 Evaluation 平台
- 运行一个多指标离线 Release Gate

## 29.1 为什么传统测试不够

Agent 的同一输入可能产生不同文本和路径，精确字符串断言过于脆弱；但完全依赖人工“看起来不错”又无法回归。解决方法是把可确定部分严格断言，把开放质量转为 rubric、pairwise 或人工评价。

## 29.2 分层指标

| 层 | 指标示例 |
|---|---|
| Goal/Outcome | task success、业务解决率、人工接管率 |
| Answer | 正确性、完整性、引用、格式 |
| Trajectory | 工具选择、参数、步骤数、禁止动作 |
| Retrieval | Recall@K、faithfulness、权限泄漏 |
| Safety | injection、PII、越权、拒答质量 |
| System | latency、availability、token、cost |

最终答案正确但调用了未授权工具，仍应判失败。

## 29.3 Evaluation Loop

```text
Production Failure / Expert Case
        ↓
Versioned Dataset + Expected Behavior
        ↓
Candidate Run + Full Trace
        ↓
Deterministic Checks + Judge + Human Sample
        ↓
Compare Baseline → Gate → Canary → Online Monitor
```

数据集至少分 normal、edge、adversarial、regression，避免只优化平均场景。保留 train/dev/test，防止 Prompt 对公开评测样本过拟合。

## 29.4 Evaluator 选择

- deterministic：schema、tool、citation、latency、cost，优先使用；
- reference-based：与专家答案/事实对比；
- LLM judge：复杂语义，需 rubric、校准和 judge 版本；
- pairwise：比较 candidate 与 baseline，常比绝对分稳定；
- human：高风险与抽样校准，是成本较高的基准。

## 29.5 工具横向对比

| 工具 | 强项 | 局限 | 适用 |
|---|---|---|---|
| OpenAI Evals | OpenAI 平台 eval、grader、优化闭环 | 多供应商治理需抽象 | OpenAI 应用 |
| LangSmith | Dataset、Experiment、Trace、Online Eval | 与 LangChain 生态更顺滑 | LangGraph/LangChain |
| Ragas | RAG/Agent 指标与测试集 | 指标需领域校准 | RAG 评估 |
| DeepEval | Python 测试式评估 | 平台运维视版本而定 | CI/unit eval |
| MLflow GenAI | Experiment、trace、评估与模型生命周期 | 体系较完整也较重 | 已有 MLflow 企业 |
| 自建 Harness | 业务指标和审批完全可控 | 评估器、UI、存储自建 | 强领域/合规 |

## 29.6 企业案例：SQL Agent

数据团队维护 500 个黄金问题，验证 metric、维度、过滤、表访问、结果和解释。任何 P0 越权即阻断发布；正确率、P95、成本分别有阈值。候选版本与当前生产版本 pairwise 回放，灰度后观察用户修正率和错误查询率，失败 trace 自动沉淀为新回归样本。

## 29.7 Python MVP

`evaluation_runtime` 同时检查内容、工具轨迹、引用、延迟和成本，并按 pass rate 生成发布结论：

```bash
python3 chapters/chapter29/example.py
python3 -m unittest discover -s chapters/chapter29 -p "test_*.py"
```

## 29.8 Production Readiness Checklist

- [ ] Dataset、Prompt、模型、工具和知识版本可重放
- [ ] 指标映射真实业务风险
- [ ] 确定性检查优先于 LLM judge
- [ ] Judge 有 rubric、校准集和版本
- [ ] 安全 P0 采用独立硬门禁
- [ ] Candidate 与 baseline 同批对比
- [ ] Canary 与在线指标能触发回滚
- [ ] 线上失败持续进入回归集

## Summary

Evaluation 把“我觉得更好”变成可复现的工程判断。发布门禁保护底线，在线实验验证真实收益，失败数据推动下一轮改进。

## Notes

不同平台的内置指标名称相似但实现不一定相同。跨工具对比时应固定输入、rubric、judge 和聚合方法。

## References

[1] OpenAI, Working with evals.
https://developers.openai.com/api/docs/guides/evals

[2] LangSmith, Evaluation.
https://docs.langchain.com/langsmith/evaluation

[3] Ragas Documentation.
https://docs.ragas.io/en/stable/

以上 URL 已在 2026-07-31 核对。
