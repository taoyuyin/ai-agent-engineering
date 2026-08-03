# Chapter 54 Future of Software Engineering

Part VII Future —— 下一代软件

Version: 2026-08

Last Updated: 2026-08-03

## Core Question

当 Agent 能够理解代码库、调用开发工具并提出完整变更时，软件工程会发生什么变化？

## Chapter Conclusion

Agent 会把软件工程的主要工作单元从“编写代码”推向“定义并验证结果”，但不会取消软件工程。需求质量、架构边界、上下文、评测、安全和运营能力将决定 Agent 是放大生产力，还是放大组织原有的问题。

未来最稀缺的能力不是生成更多代码，而是构建一个能让人和 Agent 共同产生可信变更的工程系统。

## Learning Objectives

完成本章后，你应该能够：

- 用证据而不是演示判断 Coding Agent 的真实价值；
- 理解 SDLC 每个阶段的变化与新工程制品；
- 设计 Agent-generated Change 的 Evidence Gate；
- 规划开发者、架构师、平台团队和治理角色的转变；
- 区分近期高置信趋势、中期判断和长期不确定预测。

## 54.1 先区分能力、基准与生产力

“模型能解多少代码题”“Agent 能合并多少 PR”“团队交付是否更快”是三个不同问题。

- **Capability**：模型在受控任务上能否生成正确候选；
- **Benchmark**：Agent 在固定环境、数据和时间限制下的完成率；
- **Productivity**：真实团队从需求到价值交付的时间、质量和运营结果；
- **Organizational Outcome**：软件是否提升收入、成本、风险或客户体验。

基准能力快速上升，不会自动变成团队生产力。真实工作包含陌生需求、隐性约束、跨团队沟通、遗留架构、发布风险和长期维护。

DORA 2025 将 AI 描述为组织能力的放大器：基础工程系统强，AI 更可能加速；测试薄弱、平台碎片化和反馈缓慢，AI 也会更快地产生返工。METR 针对熟悉自身开源仓库的资深开发者进行的一项 2025 随机对照研究，观察到使用当时 AI 工具后完成时间增加 19%。这不是“AI 永远降低效率”的结论，而是提醒我们：人群、任务、工具版本和测量方法会显著改变结果。

## 54.2 工作单元从代码转向可验证结果

传统工作单元常被描述为 Story、Ticket、Commit 或 Pull Request。Agent 参与后，更完整的单位是：

```text
Executable Intent
  + Context Package
  + Candidate Change
  + Verification Evidence
  + Provenance
  + Approval Decision
  = Trusted Change
```

Agent 可以大幅降低 Candidate Change 的生产成本。因此瓶颈会向上游和下游移动：目标是否明确、上下文是否充分、验证能否自动化、责任是否清晰。

## 54.3 SDLC 如何变化

### Requirements：从描述变成可执行契约

需求除了自然语言，还需要示例、验收测试、约束、非目标和风险等级。Agent 最怕的不是需求短，而是把隐含假设当成自由度。

### Design：架构决策机器可读

ADR、模块边界、依赖规则、数据分类和性能预算需要进入仓库。没有这些上下文，Agent 只能模仿局部代码，无法维护系统意图。

### Implementation：候选生成被大量委派

Agent 可以搜索、修改、运行工具和迭代修复。工程师从逐行输入转向定义范围、提供反馈、审查架构影响和处理异常。

### Verification：成为交付核心

测试、类型、Lint、安全扫描、契约、迁移检查、性能基线和 Eval 必须自动化。生成速度越快，验证门禁越重要。

### Review：从风格检查转向风险判断

低价值格式问题交给机器；人类关注需求覆盖、架构退化、数据边界、不可逆操作和长期维护成本。

### Operations：从发布后监控到持续评测

除了错误率和延迟，还要监控 Agent Task Success、工具失败、成本、人工接管、策略拒绝和模型升级回归。

## 54.4 Agent-ready Repository

一个适合人机协作的仓库需要把隐性知识外显：

| 工程制品 | 作用 |
| --- | --- |
| `README` / Architecture | 建立系统地图和模块边界 |
| `AGENTS.md` / Instructions | 声明局部工作规则与命令 |
| ADR | 保存架构选择及原因 |
| API / Schema Contract | 限制跨模块变更 |
| Test / Eval Dataset | 把正确行为变成可执行证据 |
| Policy as Code | 权限、安全和发布规则 |
| Fixture / Seed Data | 提供可复现实验环境 |
| Trace / Change Provenance | 记录谁、用什么模型、为什么修改 |
| Runbook | 定义失败、回滚和人工接管 |

“上下文工程”不只是给模型塞更多文件，而是让仓库本身具备可发现结构、稳定契约和可执行反馈。

## 54.5 新的软件供应链风险

Agent 能读取 Issue、网页、依赖文档和代码评论，这些都可能携带不可信指令。Agent 还能调用 Shell、包管理器、云控制台和发布系统，攻击面比代码补全更大。

必须增加：

- 沙箱与最小文件、网络、Secret 权限；
- 依赖来源和锁文件验证；
- 不可信内容与授权指令分离；
- 变更 Provenance：Agent、模型、Prompt/Policy、工具和 Trace；
- 敏感目录与高风险命令的人工审批；
- 生成代码的 SAST、SCA、Secret 和 License 检查；
- 发布凭证与开发 Agent 隔离；
- 一键停止、回滚和证据保留。

不能因为代码通过测试，就认为生成过程可信；也不能因为生成过程可审计，就跳过代码验证。

## 54.6 Python MVP：Agent Change Evidence Gate

本章示例把 Agent 生成的软件变更建模为两个独立对象：

- `ChangeProposal`：目标、Agent/模型来源、文件、风险和假设；
- `Evidence`：测试、类型检查、安全发现、需求覆盖、人工审批和 Trace；
- `verify()`：用确定性规则计算 Trust Score 并决定是否通过；
- 高风险变更缺少人工批准时不能进入发布链。

```bash
cd chapters/chapter54
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python example.py
```

代码生成可以是概率性的，Release Gate 必须是可解释、可复现的。生产系统还应根据服务等级加入契约测试、性能、数据库迁移、灰度和回滚验证。

**与模型的关系**：Coding Agent 和模型位于 `ChangeProposal` 上游，负责产生候选变更；本 MVP 从候选之后开始，只消费 Provenance 和验证证据。模型能力升级可以提升候选质量，但不能取消发布门禁。

## 54.7 团队角色如何变化

| 角色 | 减少的工作 | 增长的工作 |
| --- | --- | --- |
| Software Engineer | 重复样板、机械搜索 | Spec、架构、验证、复杂调试 |
| Tech Lead / Architect | 手工同步细节 | 维护边界、ADR、技术经济性 |
| QA / SDET | 重复点击与固定回归 | Eval 设计、风险覆盖、测试系统 |
| Platform Engineer | 单一 CI/CD 管道 | Agent Sandbox、Context、Policy、Evidence |
| Security Engineer | 发布末期扫描 | Tool 权限、供应链和运行时治理 |
| Product Manager | 只写自然语言 Ticket | Goal、约束、验收样例与结果指标 |

角色不会简单消失，而会在不同组织以不同速度重组。系统边界清晰、反馈自动化程度高的团队，更容易把 Agent 变成可靠协作者。

## 54.8 工程教育的变化

学习编程仍然重要。不了解数据结构、并发、事务、网络和安全，就无法判断 Agent 的输出是否正确。教学重点会从“记住 API”转向：

1. 建立计算机科学和软件设计基础；
2. 能够阅读、运行、调试和验证陌生代码；
3. 把需求转换成 Schema、测试和不变量；
4. 理解 LLM、Context、Tool、Memory 与 Evaluation；
5. 设计权限、证据、可观测性和人机协作；
6. 对模型结论保持实验意识和研究判断。

能写代码仍是基础；能设计让代码可信地产生、演进和运行的系统，将变得更重要。

## 54.9 分时间尺度的判断

未来判断必须注明时间与置信度，避免把方向写成确定事实。

### 近期：1–2 年，高置信

- Coding Agent 从补全扩展到仓库级任务与工具循环；
- Agent Trace、Sandbox、Eval 和 Policy 进入开发平台；
- PR 会附带更多机器生成的测试、解释和 Provenance；
- 工程团队会同时测量速度、质量和返工，而非只统计生成量。

### 中期：3–5 年，中等置信

- 部分标准变更从 Ticket 直接进入受控 Agent Workflow；
- Spec、测试和架构规则会成为人机共同消费的接口；
- 多 Agent 会承担开发、验证和运维角色，但由统一控制面治理；
- 软件平台会按“可验证结果”而不只是构建次数计量价值。

### 长期：5 年以上，低置信

- 自主维护大规模生产系统是否可行；
- 软件团队规模与角色会以何种比例重构；
- 是否形成跨厂商的 Agent 软件供应链标准；
- 自然语言是否会成为多数软件的主要编程入口。

长期预测受模型能力、算力成本、监管、责任制度和组织适应共同影响，不应作为当前架构投资的唯一依据。

## 54.10 企业采用路线

1. 选择可回滚、反馈快的任务建立基线；
2. 记录 Lead Time、缺陷、返工、审查时间和开发者体验；
3. 在只读和受限仓库中试点 Agent；
4. 把测试、Policy、Sandbox 和 Provenance 纳入平台；
5. 按风险逐步扩大文件、工具和发布权限；
6. 用随机或准实验方法比较真实结果；
7. 定期复核：节省的是输入时间，还是端到端交付时间？

不要把采用率当生产力，也不要用单个成功 Demo 替代组织级证据。

## 54.11 全书回顾

本教程从“软件为什么需要 Agent”开始，最后回到软件工程：

```text
LLM 提供概率性理解与生成
Agent Runtime 把能力组织成有状态循环
Engineering 用评测、权限和可观测性建立可信边界
Framework 提供不同设计取舍
Enterprise Practice 验证业务闭环
Platform / OS / AI Native 把 Agent 变成下一代软件基础设施
```

贯穿 54 章的核心原则没有改变：

> 模型负责提出候选，确定性系统负责验证和执行；Agent 负责追求目标，工程体系负责让这个过程可控、可观测、可恢复。

## Summary

Agent 不会取消软件工程，而会把软件工程推向更高层次的明确性。代码生产成本下降后，好的 Goal、Architecture、Context、Verification 和 Governance 会成为主要约束。工程师的价值从“亲自输入每一行”转向“设计并证明系统能正确演进”。

## References

- [DORA 2025 Report](https://dora.dev/research/2025/dora-report/)
- [METR: Early-2025 AI on Experienced Open-Source Developer Productivity](https://metr.org/blog/2025-07-10-early-2025-ai-experienced-os-dev-study/)
- [NIST AI Risk Management Framework](https://www.nist.gov/itl/ai-risk-management-framework)
- [OmniCode: A Benchmark for Evaluating Software Engineering Agents](https://arxiv.org/abs/2602.02262)
