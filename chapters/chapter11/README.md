# Chapter 11 MCP：为 Agent 的上下文与工具建立协议边界

Part II LLM Foundations —— Agent 为什么能够工作

Version: 2026-07

Last Updated: 2026-07-31

## Core Question

为什么仅有 Function Calling 还不够？MCP 标准化了什么，又没有解决什么？如何用官方 Python SDK 构建 Server 与 Client？

## Chapter Conclusion

Model Context Protocol（MCP）标准化 AI 应用发现和使用工具、资源、提示模板的方式。它解决的是连接协议与互操作性，不替代业务 API、Agent Runtime、模型、身份系统或权限治理。

企业采用 MCP 的真正价值，是把集成从“每个 Agent 各写一套适配器”变为“能力提供方发布一个协议化边界，多个 Host 复用”。

## Learning Objectives

- 理解 Host、Client、Server 以及 MCP 的数据层和传输层
- 区分 Tools、Resources、Prompts
- 理解发现、版本协商、调用和通知流程
- 比较 MCP、Function Calling、REST/OpenAPI、gRPC 与 A2A
- 运行零依赖协议 MVP 和官方 Python SDK 2.x Server/Client
- 识别远程 MCP 的授权、注入和供应链风险

## 11.1 Function Calling 留下了什么问题

Function Calling 规定模型如何表达“我要调用某个函数”，但没有统一回答：

- Host 如何发现外部服务有哪些工具？
- 如何读取结构化资源和复用 Prompt？
- 客户端与服务端如何声明版本和能力？
- 本地进程与远程服务如何使用一致语义？
- 工具列表变化如何通知客户端？

没有协议时，每个 AI 应用都需要为 GitHub、数据库、文件系统和企业 API 重写连接器。

## 11.2 MCP 架构

```text
┌──────────────── MCP Host / AI Application ────────────────┐
│ Model + Agent Runtime + Approval UI + Context Management  │
│                                                          │
│ MCP Client A ── stdio ── Local MCP Server                │
│ MCP Client B ── HTTP ─── Remote MCP Server               │
│ MCP Client C ── HTTP ─── Enterprise Data MCP Server      │
└──────────────────────────────────────────────────────────┘
```

- **Host**：AI 应用，管理模型、多个 Client、权限与用户交互。
- **Client**：与一个 Server 建立逻辑连接并处理协议。
- **Server**：发布工具、资源、提示模板等能力。

MCP 有两层：

| 层 | 责任 |
|---|---|
| Data Layer | JSON-RPC 2.0 消息、发现、版本/能力、Tools/Resources/Prompts、通知 |
| Transport Layer | 进程或网络传输、消息框架、HTTP 授权 |

协议不规定 Host 必须如何把资源放入模型，也不规定 Agent 如何规划。

## 11.3 三个核心 Server Primitives

### Tools

可执行动作，使用 JSON Schema 描述参数，例如查询指标、创建工单。通常由模型建议调用，但 Host 保留批准权。

### Resources

可读取的上下文数据，例如文件、数据库 schema、指标定义。Resource URI 应稳定、可授权、可追溯。

### Prompts

Server 发布的可复用交互模板。Prompt 不是高于 Host System Policy 的远程指令；Host 必须明确其信任级别。

以数据 Agent 为例：

```text
Tool:     get_metric(name, period)
Resource: metric://definitions/revenue
Prompt:   analyze_metric(name)
```

工具返回当前数值，资源提供治理定义，Prompt 提供推荐分析模板，三者职责不同。

## 11.4 2026-07-28 协议变化

本章以 `2026-07-28` 规范和官方 Python SDK 2.x 为准。与大量旧教程相比，关键认知变化包括：

- 协议强调无状态请求；
- 请求通过 `_meta` 携带协议版本和相关能力；
- `server/discover` 用于发现支持版本、能力和身份；
- Sampling 和旧 Logging primitive 已被弃用；
- 长任务可使用 Tasks 扩展；
- 官方 Python SDK 2.x 使用 `MCPServer` 和更高层 `Client`。

因此不要把旧版 `initialize` 会话流程或 v1 `FastMCP` 示例直接当作当前标准。维护已有系统时，应固定 SDK 主版本并阅读 migration guide。

## 11.5 调用生命周期

```text
Client → server/discover
Server → versions + capabilities + identity

Client → tools/list
Server → tool definitions + inputSchema

Model suggests tool call
Host validates / authorizes
Client → tools/call(name, arguments)
Server → content / structured result / error
Host → model context
```

发现响应可按服务端 TTL 缓存；工具列表也可能动态变化。聚合多个 Server 时，Host 应使用命名空间避免同名工具冲突。

## 11.6 Transport 横向对比

| 维度 | stdio | Streamable HTTP |
|---|---|---|
| 部署位置 | 通常本机子进程 | 本地或远程服务 |
| 通信 | stdin/stdout | HTTP POST，可选 SSE streaming |
| 用户规模 | 通常单 Client | 通常多 Client |
| 授权 | 不走 MCP HTTP OAuth；凭证来自进程环境 | Bearer/API key/custom header，推荐 OAuth |
| 优点 | 简单、低开销、无监听端口 | 远程共享、可网关治理 |
| 风险 | 本地进程和依赖供应链 | 网络、租户隔离、token、SSRF |
| 适用 | IDE、桌面 Agent、开发工具 | 企业共享能力和 SaaS 集成 |

旧 SSE transport 已被 Streamable HTTP 取代，不应作为新项目默认。

## 11.7 MCP 与其他技术横向对比

| 技术 | 主要连接对象 | 能力发现 | 面向模型语义 | 是否替代业务 API |
|---|---|---:|---:|---:|
| Python Function | 同进程代码 | 代码导入 | 否 | 否 |
| REST/OpenAPI | 服务与服务 | OpenAPI | 弱 | 本身就是 API |
| gRPC | 高性能服务 | IDL/reflection | 否 | 本身就是 RPC |
| Function Calling | 模型与 Host Runtime | 请求内工具 schema | 是 | 否 |
| MCP | AI Host 与能力 Server | 是 | 是 | 否 |
| A2A 类协议 | Agent 与 Agent | 任务/能力 | 面向协作 | 否 |

MCP Server 往往只是现有 REST/gRPC/数据库之上的 Agent-facing adapter。不要为了采用 MCP 重写成熟业务系统。

## 11.8 SDK 与生态选型

| 方案 | 特点 | 优点 | 局限 |
|---|---|---|---|
| 官方 Python SDK 2.x | `MCPServer`、`Client`、stdio/HTTP/in-memory | 与最新规范同步、适合 Python | 主版本迁移需管理 |
| 官方 TypeScript SDK | Node/TS 生态 | 前端与 SaaS 集成自然 | Python 数据工具需跨服务 |
| 社区 FastMCP 项目 | 更高层开发体验和部署能力 | 便捷、功能丰富 | 与官方 SDK 内同名历史 API 容易混淆 |
| 手写 JSON-RPC | 完全控制 | 适合协议研究 | 容易漏掉版本、错误和安全细节 |
| 平台内置 Connector | 托管配置和用户体验 | 运维少 | 可移植性和定制性受平台限制 |

新项目优先使用官方稳定 SDK。引入社区实现时，应验证它支持的规范版本、传输、授权和更新策略。

## 11.9 企业安全边界

MCP 扩大了 Agent 可发现的能力，因此 Host 与 Server 都要防御。

### Host 侧

- 只连接管理员或用户批准的 Server；
- 展示工具来源、参数和副作用；
- 对远程文本使用不可信数据边界；
- 工具命名空间避免 shadowing；
- 限制结果大小和 Context 占用；
- 不把一个 Server 的 token 转发给另一个 Server。

### Server 侧

- 每次请求检查 actor、tenant、scope；
- HTTP token 验证 issuer、audience、expiry；
- 最小权限访问下游；
- 防止 SQL 注入、SSRF 和路径穿越；
- 返回最小必要数据；
- 记录 audit id，但不记录 token。

MCP HTTP 授权以 OAuth 2.1 资源服务器模式为基础。stdio 不应照搬该流程，而应由 Host 管理子进程凭证和环境隔离。

## 11.10 业务案例：Enterprise Metrics MCP

多个 Agent 都需要企业指标：

- BI Agent 查询收入；
- SQL Agent 获取指标定义；
- Customer Service Agent 查看 SLA；
- Management Agent 生成周报。

若每个项目直连数仓，定义、权限和审计会分裂。Metrics MCP Server 可以：

- 用 Resource 暴露带版本的指标定义；
- 用 Tool 暴露受控查询；
- 用 Prompt 发布推荐分析模板；
- 在 Server 侧统一租户、行级权限和结果大小。

它不是 Semantic Layer 本身，而是 Semantic Layer 的 Agent-facing 协议入口。

## 11.11 Python MVP

目录：

```text
chapter11/
├── example.py
└── mcp_runtime/
    ├── protocol.py
    ├── server.py
    ├── client.py
    ├── requirements.txt
    └── test_protocol.py
```

### 零依赖协议演示

```bash
python chapters/chapter11/example.py
python -m unittest discover -s chapters/chapter11 -p "test_*.py"
```

它演示 discover-before-use、工具发现、调用参数验证和 Resource 读取，适合理解数据层，不声称是完整协议实现。

### 官方 SDK 2.x Server/Client

```bash
cd chapters/chapter11/mcp_runtime
python -m pip install -r requirements.txt
python client.py
uv run mcp dev server.py
```

`client.py` 使用官方 in-memory transport，测试时无需端口；SDK 的 `Client` 也可以连接 HTTP URL 或 stdio 子进程。

依赖固定为 `mcp>=2,<3`，防止未来主版本升级破坏教程。

## 11.12 Production Checklist

- [ ] 固定协议与 SDK 主版本
- [ ] Server tool/resource/prompt 有 owner、version 和数据等级
- [ ] Host 维护 Server allowlist 与工具命名空间
- [ ] 每次调用执行 actor/tenant/scope 检查
- [ ] 远程 HTTP 使用 TLS 和正确 token audience
- [ ] token 不写 URL、日志或模型 Context
- [ ] 工具参数、结果大小、超时和速率有限制
- [ ] 有副作用工具展示确认界面和幂等键
- [ ] 外部 Resource 与 Tool Result 视为不可信数据
- [ ] 使用 MCP Inspector、契约测试和攻击用例验证

## Summary

Function Calling 让一个模型会表达动作，MCP 让多个 AI Host 以统一协议发现和使用外部能力。协议带来互操作性，但权限、业务语义和 Agent 决策仍属于企业架构本身。

## References

[1] Model Context Protocol, Architecture overview (2026-07-28).
https://modelcontextprotocol.io/docs/2026-07-28/learn/architecture

[2] Model Context Protocol, Specification.
https://modelcontextprotocol.io/specification/2026-07-28

[3] Model Context Protocol, Authorization.
https://modelcontextprotocol.io/specification/2026-07-28/basic/authorization

[4] Model Context Protocol, Official Python SDK.
https://github.com/modelcontextprotocol/python-sdk

[5] MCP Python SDK documentation.
https://py.sdk.modelcontextprotocol.io/

以上 URL 已在 2026-07-31 核对。
