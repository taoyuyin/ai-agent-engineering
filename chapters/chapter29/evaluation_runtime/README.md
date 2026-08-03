# Evaluation Runtime MVP

本模块实现确定性的 Offline Evaluation 与 Release Gate。

## 实现内容

- `EvalCase` 定义必需内容、预期 Tool、Citation、延迟和成本阈值；
- `AgentResult` 保存一次被测运行的标准结果；
- `score()` 输出逐项 Check，而不是只有总分；
- 缺失结果显式失败；
- `EvaluationSuite` 根据最小通过率决定是否发布。

## 模型关系

任意模型或 Agent 的结果都先归一化为 `AgentResult`，评分器与被测模型解耦。主观质量可增加 LLM Judge，但必须版本化 Rubric 并用人工标注校准。

```bash
python chapters/chapter29/example.py
python -m unittest discover -s chapters/chapter29 -p "test_*.py"
```

安全失败在生产中应作为硬门禁，不能被平均分抵消。正文见 [Chapter 29](../README.md)。
