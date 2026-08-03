# Architecture

`architecture/` 保存跨章节架构视图。正文解释设计原因，源码验证 Contract，本目录用统一图示连接组件、状态、部署和企业边界。

## 视图索引

| 目录 | 回答的问题 | 关联内容 |
| --- | --- | --- |
| [sequence/](sequence/README.md) | 一次 Agent Run 如何交互 | Chapter 12、18、23 |
| [state-machine/](state-machine/README.md) | 状态如何转换与恢复 | Chapter 20、21 |
| [deployment/](deployment/README.md) | 服务如何部署、扩缩与隔离 | Chapter 31–33 |
| [enterprise/](enterprise/README.md) | 身份、数据、Tool 和治理如何组合 | Chapter 23、28–30、42–50 |

Runtime 的代码级架构见 [`framework/ARCHITECTURE.md`](../framework/ARCHITECTURE.md)。

## 图示规范

- Mermaid 用于可版本化的 Flow、Sequence 和 State Diagram；
- 所有节点名称对应仓库中的 Contract 或明确的外部系统；
- 图中标注 Trust Boundary、Control Plane 和 Data Plane；
- 不把模型、Agent、Workflow 和 Tool 画成同一个黑盒；
- 架构改变时同步正文、代码和图，而不是只更新截图。

## 统一原则

```text
Model / Planner → Proposal
Runtime / Policy → Validation and Decision
Tool / Workflow → Authorized Execution
Observation / Evidence → Verifiable Result
```

四个视图共享同一原则：概率性组件负责理解与候选，确定性系统负责状态、权限、预算、副作用和审计。
