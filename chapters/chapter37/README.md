# Chapter 37 CrewAI

Part V Frameworks —— 主流 Agent 框架设计

Version: 2026-07

Last Updated: 2026-07-31

## 本章结论

CrewAI 用“角色—目标—任务—团队”描述多 Agent 协作，并用 Flow 补充事件驱动、可持久化的确定性流程。它的优势是业务语义直观，适合快速表达专业角色协作；风险是角色化叙事可能掩盖真实的状态、权限和失败边界。

企业项目应把 Crew 当作可控的任务执行单元，把关键流程、审批和持久化放在 Flow 或外部 Workflow 中。

## 学习目标

完成本章后，你应该能够：

- 解释 Agent、Task、Crew、Process 和 Flow 的关系；
- 设计有真实职责差异的多角色协作；
- 使用 Tool 和 Pydantic Output 构建结构化任务链；
- 区分 Crew 的自主协作与 Flow 的确定性控制；
- 识别角色冗余、上下文膨胀和责任不清等反模式。

## 37.1 从业务团队映射到软件抽象

CrewAI 的核心抽象接近人类组织：

| 抽象 | 业务含义 | 工程责任 |
| --- | --- | --- |
| Agent | 具备角色、目标、背景和工具的执行者 | 模型、Prompt、权限和迭代上限 |
| Task | 有描述、期望输出和负责人的工作项 | 输入、输出、依赖与验收标准 |
| Crew | 一组 Agent 和 Task | 协作边界与资源预算 |
| Process | Task 的执行策略 | 顺序或层级调度 |
| Flow | 事件驱动的状态流程 | 持久化、分支、组合与生命周期 |

这种抽象让业务人员容易理解，但代码评审不能停留在“分析师 Agent 很专业”。必须继续追问：

- 它能访问哪些工具？
- Task 的输入输出是什么类型？
- 失败后由谁重试？
- 数据从哪个 Task 传到哪个 Task？
- 最终结果由谁负责？

## 37.2 Agent 角色必须对应能力边界

好的拆分：

- 数据 Agent：只能读取受治理数据源；
- 报告 Agent：只能消费已验证事实并生成报告；
- 发布 Agent：只有在审批通过后才能调用发布 Tool。

不好的拆分：

- “聪明 Agent”“高级 Agent”“审核 Agent”都使用相同模型、相同工具和相同上下文；
- 为了展示多 Agent 而把一个函数拆成五个角色；
- 让每个 Agent 都看到所有密钥和写工具。

判断是否应拆分的标准是：工具、权限、上下文、优化目标或评测标准是否不同。角色名称本身不产生隔离。

## 37.3 Task 是协作 Contract

Task 至少要明确：

- 输入问题和可使用的上下文；
- 必须使用的数据/工具；
- 期望输出的格式和质量；
- 负责 Agent；
- 上游 Task；
- 完成条件和失败语义。

`expected_output` 是给模型的描述，`output_pydantic` 才提供机器可验证的输出契约。对下游系统消费的结果，应优先使用 Pydantic 模型，避免依赖自由文本解析。

## 37.4 Process 与 Flow

Crew 的 Process 负责如何执行一组 Task：

- `sequential`：按顺序执行，最容易理解和审计；
- hierarchical：由管理角色分派工作，适合动态协作，但增加一次路由判断。

Flow 则更接近应用级 Workflow：可以保存状态、监听事件、执行条件分支并组合 Crew。两者的关系可以理解为：

```text
Flow：应用生命周期和确定性控制
  ├── validate_request
  ├── run_analysis_crew
  ├── human_approval
  └── publish_report

Crew：一个阶段内的自主协作
  ├── data_agent
  └── report_agent
```

高风险业务不应让 hierarchical Process 自主决定是否跳过审批。

## 37.5 Tool 设计与数据传递

CrewAI Tool 仍然是代码执行边界。本章示例通过 `@tool` 注册销售查询，并在内部检查 `sales:read`。

工具返回数据时应包含指标、粒度、时间范围和证据源。下游报告 Agent 只根据上游已验证结果生成报告，不再次“凭记忆”填充数字。

真实项目中建议：

- 每个 Agent 只持有最小工具集合；
- Tool 内使用真实请求身份，而不是从 Prompt 解析租户；
- 大结果写入对象存储，Task 只传引用和摘要；
- 对写工具增加幂等键和人工批准。

## 37.6 最小可运行 MVP：双角色销售分析 Crew

本章示例使用相同的 Part V 基准业务，将职责拆为：

1. `Governed Data Analyst` 调用受权限保护的销售工具；
2. `Sales Reporting Engineer` 消费上游事实，输出 `SalesReport`；
3. `Crew` 以顺序 Process 执行两个 Task。

安装与运行：

```bash
cd chapters/chapter37
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export OPENAI_API_KEY="<your-api-key>"
export AGENT_SCOPES="sales:read"
python example.py "查询 2025 年各区域净销售额"
```

代码中的关键控制：

- 数据 Agent 拥有查询 Tool，报告 Agent 没有；
- 两个 Agent 都关闭任意委派；
- `max_iter` 限制每个 Agent 的循环；
- 第二个 Task 通过 `context=[retrieve]` 显式依赖上游；
- `output_pydantic=SalesReport` 提供结构化最终结果。

这不是为了证明两 Agent 一定优于一 Agent，而是展示 Crew 的职责分离。如果业务只有一次查询和格式化，单 Agent 成本更低；当两类角色拥有不同数据权限或评测标准时，拆分才有价值。

## 37.7 与其他多 Agent 方案比较

| 维度 | CrewAI | AutoGen AgentChat | OpenAI Agents SDK |
| --- | --- | --- | --- |
| 主要心智模型 | 角色、Task、Crew | 消息、Agent、Team | Agent、Tool、Handoff |
| 业务可读性 | 高 | 中 | 中 |
| 动态对话研究 | 中 | 高 | 中 |
| 确定性应用流 | Flow | GraphFlow/外部 Workflow | 应用层/外部 Workflow |
| 类型化 Task 输出 | Pydantic Output | StructuredMessage | `output_type` |
| 典型优势 | 角色协作和业务自动化 | 多 Agent 对话与研究 | 轻量工具 Agent |

选择 CrewAI 时应确认团队需要的是“任务和角色编排”，而不是仅仅需要并行调用两个函数。

## 37.8 企业业务案例

以月度经营报告为例：

```text
Flow 接收请求
  -> 校验组织和月份
  -> 数据 Crew
       ├── 销售分析 Agent
       ├── 库存分析 Agent
       └── 风险分析 Agent
  -> 报告 Agent 汇总
  -> 人工审批
  -> 发布服务
```

数据 Agent 之间可以并行，但它们不应直接发布报告。Flow 持有业务状态和审批结果，Crew 只负责一个有边界的分析阶段。

## 37.9 生产化清单

- 为每个 Agent 定义最小工具和权限；
- 为每个 Task 定义结构化输入、输出和验收标准；
- 用 Flow 或外部引擎持久化长流程状态；
- 限制 Agent 迭代、委派层数、Token 和执行时间；
- 对上游事实与下游文案分别评测；
- 记录 Task 依赖、工具调用、Agent 输出和最终决策；
- 对错误设置明确的重试者，避免 Agent 之间互相转交；
- 将人工审批建模为确定性步骤；
- 验证并行任务的数据合并规则；
- 评估托管平台能力与开源 Runtime 的运维边界。

## 37.10 优点、局限与适用场景

优点：

- 角色、目标和 Task 对业务人员直观；
- 多角色顺序或层级协作表达简洁；
- Tool、结构化输出和 Flow 能覆盖完整应用链路；
- 适合快速验证多职能自动化流程。

局限：

- 角色叙事容易造成不必要的多 Agent；
- 自主委派会增加成本和不可预测性；
- 复杂状态、权限和副作用仍需显式工程设计；
- 当 Task 数量很大时，上下文和 Trace 容易膨胀。

最适合：市场研究、内容生产、运营自动化、跨专业报告和具有明确岗位分工的企业流程。

## Summary

CrewAI 的核心价值是把多 Agent 协作提升为业务可读的 `Agent + Task + Crew`，并用 Flow 管理应用流程。优秀的 Crew 设计不是角色越多越好，而是每个角色都有清晰能力边界，每个 Task 都有可验证 Contract。

本章 MVP 通过“数据获取—报告生成”两阶段展示最小工具权限与结构化交付。生产系统应进一步把状态、审批和发布放到 Flow 或外部 Workflow。

## References

[1] CrewAI. Documentation.
https://docs.crewai.com/

[2] CrewAI. Agents.
https://docs.crewai.com/core-concepts/Agents

[3] CrewAI. Using Annotations.
https://docs.crewai.com/learn/using-annotations
