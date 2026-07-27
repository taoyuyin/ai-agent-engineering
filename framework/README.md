# Framework

这里会逐步实现一个教学版 Agent Runtime。

核心模块：

- `planner/`：任务拆解与计划生成
- `memory/`：短期记忆、长期记忆和检索
- `tools/`：工具定义、注册与调用
- `workflow/`：可控流程编排
- `executor/`：动作执行与错误恢复
- `runtime/`：Agent 运行时主循环
