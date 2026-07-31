# Runtime

`agent.py` 是 Agent Runtime 的组合根，负责：

- Goal 与 Plan 生命周期；
- Plan 预算和依赖校验；
- Policy、Registry 与 Executor 编排；
- Observation、Memory、Trace 和 Evidence；
- Run 完成或失败状态。

Runtime 不包含具体行业逻辑，业务能力通过 Planner、Tool 和 Answer Synthesizer 接入。
