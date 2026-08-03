# Evaluation

`evaluation/` 定义 Agent 是否“做对了”的评分契约。评测不是只检查最终回答，而要覆盖 Goal、Plan、Tool、Evidence、安全、成本和端到端业务结果。

## 评测分层

| 层次 | 典型问题 | 指标示例 |
| --- | --- | --- |
| Component | 检索、工具选择或 Schema 是否正确 | Recall@K、Tool Accuracy、Schema Pass Rate |
| Trajectory | 执行路径是否合理 | Step Success、Retry、Loop、Handoff Rate |
| Outcome | 最终任务是否完成 | Task Success、Groundedness、Business Correctness |
| Safety | 是否越权或泄露数据 | Unsafe Action、Policy Violation、PII Leakage |
| System | 是否满足服务约束 | P95 Latency、Cost/Task、Availability |

## 推荐目录

```text
evaluation/
├── suites/             # EvalCase 与数据集绑定
├── scorers/            # 确定性和模型评分器
├── rubrics/            # 人工/LLM Judge 量表
├── reports/            # 可再生报告，不保存不可追溯截图
└── README.md
```

一个 Eval Case 至少包含 `case_id`、输入、期望行为、禁止行为、数据版本、评分器版本和阈值。模型评分器必须同时保留 Judge 模型、Prompt 版本和原始理由，并用人工标注校准。

## 发布门禁

```text
Candidate Agent
  → Offline Regression
  → Safety Suite
  → Shadow / Replay
  → Canary Online Metrics
  → Promote or Rollback
```

总分不能掩盖安全失败。越权、错误写操作和跨租户泄漏应作为硬门禁；质量、延迟和成本可以使用分层阈值。

Chapter 29 的 [`evaluation_runtime`](../chapters/chapter29/evaluation_runtime/) 提供离线评分与 Release Gate MVP。完整企业评测目录应在出现跨案例共享 Suite 时再加入实现，避免提前制造空脚手架。
