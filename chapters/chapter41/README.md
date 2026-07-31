# Chapter 41 Dify

Part V Frameworks —— 主流 Agent 框架设计

Version: 2026-07

Last Updated: 2026-07-31

## 本章结论

Dify 更准确的定位是 Agent Application Platform，而不是 Python Agent Framework。它把模型、Prompt、知识库、Tool、Workflow、监控和应用发布集中到可视化平台，并通过 API 把已发布应用交付给业务系统。

它适合跨职能团队快速构建和运营 Agent 应用；代价是平台版本、Workflow DSL、插件安全、部署和变更治理会成为新的工程责任。

## 学习目标

完成本章后，你应该能够：

- 区分 Agent Framework 与 Agent Platform；
- 理解 Dify Chatflow、Workflow、Agent Node、Knowledge 和 Tool；
- 设计可被外部服务调用的稳定 Workflow Contract；
- 使用 Python API Client 调用已发布 Workflow；
- 评估自托管、平台治理和供应商/DSL 依赖。

## 41.1 为什么 Dify 不是普通框架

代码框架主要提供库和运行时，应用团队仍需搭建 UI、配置管理、知识库、日志和发布流程。Dify 把这些能力放到一个平台：

| 平台能力 | 解决的问题 |
| --- | --- |
| Model Provider | 统一配置不同模型 |
| Prompt/LLM Node | 可视化维护推理步骤 |
| Workflow/Chatflow | 组合节点、变量、分支和迭代 |
| Knowledge | 文档摄取、检索和引用 |
| Tool/Plugin | 连接外部 API 与能力 |
| Application API | 将发布应用暴露给业务系统 |
| Logs/Monitoring | 查看执行记录和问题 |
| Version/Export | 管理应用配置与迁移 |

因此 Dify 的交付物不仅是 Python 文件，还包括平台中的 Workflow、知识配置、凭证和发布版本。

## 41.2 Workflow、Chatflow 与 Agent Node

- **Workflow**：面向自动化任务和 API 执行，输入和输出明确；
- **Chatflow**：面向多轮对话应用，包含会话语义；
- **Agent Node**：在 Workflow 中让模型自主选择工具；
- **LLM Node**：执行一次相对确定的模型调用；
- **Knowledge Retrieval Node**：从知识库召回上下文；
- **Code/HTTP Node**：执行确定性处理或调用外部服务。

原则是：能用确定性节点表达的业务规则，就不要交给 Agent Node。权限、金额阈值、状态判断和发布审批应由代码、条件分支或外部服务控制。

## 41.3 稳定 Contract 比画布更重要

业务系统不应该依赖画布中的内部节点名，而应依赖已发布应用的输入输出 Contract。

本章定义：

```json
{
  "inputs": {
    "question": "string",
    "tenant_id": "string",
    "scopes": "string"
  },
  "outputs": {
    "answer": "string",
    "evidence_source": "string"
  }
}
```

Contract 需要版本化。Workflow 内部可以从一个 LLM Node 演进到多个检索和 Agent Node，只要外部输入输出保持兼容，调用方就不需要修改。

## 41.4 本章 Workflow 设计

在 Dify 控制台创建 Workflow：

```text
Start
  inputs: question, tenant_id, scopes
    |
Scope Condition
  ├── scopes contains "sales:read"
  |      |
  |   HTTP/Tool: governed sales API
  |      |
  |   LLM: summarize only returned facts
  |      |
  |   End
  |     answer, evidence_source
  |
  └── unauthorized
         |
       End
        answer="permission denied"
        evidence_source=""
```

生产环境不应让 Dify 直接信任调用方提交的 `scopes`。更安全的方案是：

1. 业务后端验证用户 Token；
2. 后端用服务端保存的 Dify API Key 调用 Workflow；
3. 受治理数据 API 根据服务身份和租户再次授权；
4. Dify 只编排，不成为最终权限裁决者。

本章的 `scopes` 输入用于展示 Contract，不代表完整 IAM 实现。

## 41.5 Python API MVP

目录：

```text
chapter41/
├── README.md
├── example.py
├── workflow-contract.json
├── workflow-setup.md
├── requirements.txt
└── .env.example
```

`example.py` 实现最小服务客户端：

- 调用 `POST /v1/workflows/run`；
- 使用 Bearer API Key；
- 发送 Workflow Inputs；
- 使用 `blocking` 响应模式；
- 检查 HTTP 与 Workflow 两层状态；
- 读取 `data.outputs`。

运行前，按 [workflow-setup.md](workflow-setup.md) 在 Dify 创建并发布满足 `workflow-contract.json` 的 Workflow，然后获取应用 API Key：

```bash
cd chapters/chapter41
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export DIFY_BASE_URL="https://api.dify.ai"
export DIFY_API_KEY="<your-workflow-api-key>"
python example.py "查询 2025 年各区域净销售额"
```

自托管实例将 `DIFY_BASE_URL` 改为自己的域名。API Key 只能保存在服务端，不能放入浏览器或移动端。

这个 MVP 是“可运行的集成工程”，其前置依赖是已发布的 Dify Workflow，就像数据库示例需要先有数据库服务一样。`workflow-contract.json` 是仓库与平台配置之间的稳定契约。

## 41.6 阻塞与流式模式

Workflow API 可根据应用能力选择阻塞或流式响应：

- 阻塞适合短任务和服务到服务调用，错误处理简单；
- 流式适合长生成和交互体验，需要处理事件、断线和重连；
- 超长任务更适合异步任务架构，不能无限占用 HTTP 连接。

本章使用阻塞模式以突出 Contract。生产客户端应增加连接池、超时、有限重试、请求 ID 和日志脱敏。

## 41.7 版本与 Git 管理

Dify Workflow 在平台中编辑，但企业仍需要 Git 审查：

- 导出应用 DSL；
- 将 DSL、外部 Tool OpenAPI Schema 和测试用例提交 Git；
- PR 中审查模型、Prompt、节点、变量和权限变化；
- 在测试环境导入并运行回归集；
- 批准后发布新版本；
- 保留回滚目标。

导出的 DSL 可能随 Dify 版本变化，因此本章没有手写一个容易过期的伪 DSL。应从目标 Dify 实例导出真实文件，再纳入仓库。`workflow-contract.json` 则保持与平台版本相对独立。

## 41.8 Dify 与代码框架横向比较

| 维度 | Dify | LangGraph | OpenAI Agents SDK |
| --- | --- | --- | --- |
| 定位 | Agent 应用平台 | 状态图运行时 | Agent SDK |
| 开发方式 | 可视化 + 配置 + API | Python 图代码 | Python Agent 代码 |
| 内置知识库/UI/发布 | 强 | 需集成 | 需集成 |
| 控制流 | Workflow/Chatflow 节点 | State/Node/Edge | Runner Agent Loop |
| 源码审查 | 依赖导出 DSL | 原生 Git | 原生 Git |
| 运维对象 | 完整平台 | 应用服务与状态存储 | 应用服务 |
| 适合团队 | 产品、运营、工程协同 | 平台/后端工程 | AI/Python 工程 |

若目标是快速交付带 UI、知识库和运营能力的应用，Dify 效率高；若目标是深度定制 Runtime、严格代码审查或嵌入已有微服务，代码框架通常更灵活。

## 41.9 自托管架构与安全

典型自托管组件包括 Web/API、Worker、数据库、缓存、向量存储、对象存储和 Sandbox。生产部署需要关注：

- 各组件的版本兼容和升级迁移；
- Worker 扩缩容与队列积压；
- 向量库、数据库和对象存储备份；
- Sandbox 与外部网络访问策略；
- 插件来源、签名和权限；
- 模型密钥、Tool 凭证和租户隔离；
- 日志中的 Prompt、文档和 PII；
- 高可用、灾备和容量规划。

“自托管”不自动等于“数据安全”，它只是把安全和运维责任转移给团队。

## 41.10 生产化清单

- API Key 只保存在后端 Secret Manager；
- 为 Workflow 输入输出建立版本化 Contract；
- 从目标实例导出真实 DSL 并提交 Git；
- 测试授权、空数据、模型失败和 Tool 超时分支；
- 外部 Tool API 执行最终权限和租户隔离；
- 为发布设置开发、测试、生产环境；
- 监控运行量、失败率、延迟、Token 和队列；
- 审查 Plugin、Code Node 和外部网络权限；
- 建立知识库更新、删除与 ACL 流程；
- 设计平台升级、备份和回滚演练。

## 41.11 优点、局限与适用场景

优点：

- 从模型、Workflow、知识库到发布的一站式能力；
- 可视化降低跨职能协作门槛；
- API 便于与现有业务系统集成；
- 适合快速迭代和运营 Agent 应用。

局限：

- 平台本身需要部署、升级和安全治理；
- 可视化 DSL 的代码审查体验不如原生 Python；
- 深度定制会受到节点和插件机制约束；
- 应用配置、凭证和平台版本会形成迁移成本。

最适合：企业知识助手、客服、内部流程自动化、原型到应用发布，以及产品、运营和工程共同维护的 Agent 项目。

## Summary

Dify 把 Agent 从一个 Python 运行循环提升为可运营的应用平台。它的价值是集成与交付速度，而不是免除工程治理。

本章用 `workflow-contract.json + Python API Client` 表达平台型项目的最小交付：平台内部 Workflow 可以演进，外部服务通过稳定 Contract 调用。生产系统还必须把真实授权、版本、凭证和平台运维纳入架构。

## References

[1] Dify. Documentation.
https://docs.dify.ai/

[2] Dify. Run Workflow API.
https://docs.dify.ai/api-reference/workflow-execution/run-workflow

[3] Dify. GitHub Repository.
https://github.com/langgenius/dify
