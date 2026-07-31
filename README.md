# AI Agent Engineering

AI Agent Engineering 是一本持续更新的企业级 AI Agent 工程教材，也是一套配套源码工程。

这个项目从“为什么需要 Agent”开始，逐步覆盖 LLM 基础、Agent Architecture、企业级工程能力、主流框架设计、企业实践和下一代软件形态。

## 项目目标

- 理解 Agent 为什么出现
- 理解 LLM 为什么让 Agent 成为可能
- 自己实现一个教学版 Agent Runtime
- 用 Python 示例解释核心工程抽象
- 分析主流 Agent 框架的设计思想，而不是只学习 API
- 面向企业场景讨论安全、评测、部署、治理和平台化

## 目录结构

```text
ai-agent-engineering/
├── docs/                    # 教材配套文档
├── chapters/                # 每章正文与源码
├── examples/                # 完整案例
├── framework/               # 自己实现 Agent Runtime
├── integrations/            # 模型与服务集成
├── prompts/                 # 提示词模板
├── datasets/                # 示例数据集
├── benchmark/               # 基准测试
├── evaluation/              # 评测方法与脚本
├── notebooks/               # 实验与分析 Notebook
├── architecture/            # 架构图与设计说明
└── scripts/                 # 工具脚本
```

## 项目文档

- [写作规范](docs/writing-guidelines.md)
- [项目路线图](docs/roadmap.md)
- [Agent Runtime 工程说明](framework/README.md)
- [Agent Runtime 架构](framework/ARCHITECTURE.md)
- [SQL Agent 完整案例](examples/sql-agent/README.md)

## 全文章节

### Part I Foundations —— 为什么需要 AI Agent

- [Chapter 1 软件为什么需要 AI Agent？](chapters/chapter01/README.md)
- [Chapter 2 软件架构为什么不断演进？](chapters/chapter02/README.md)
- [Chapter 3 什么是真正的 AI Agent？](chapters/chapter03/README.md)
- [Chapter 4 Agent 与 Workflow 的区别](chapters/chapter04/README.md)

### Part II LLM Foundations —— Agent 为什么能够工作

- [Chapter 5 Transformer](chapters/chapter05/README.md)
- [Chapter 6 Token](chapters/chapter06/README.md)
- [Chapter 7 Embedding](chapters/chapter07/README.md)
- [Chapter 8 Context](chapters/chapter08/README.md)
- [Chapter 9 Reasoning](chapters/chapter09/README.md)
- [Chapter 10 Function Calling](chapters/chapter10/README.md)
- [Chapter 11 MCP](chapters/chapter11/README.md)

### Part III Agent Architecture —— Agent 内部如何工作

把 Part II 的 Token、Embedding、Context、Reasoning、Function Calling 和 MCP 应用到 Agent Runtime，并通过逐章 Python MVP 构建完整企业级架构。

- [Chapter 12 Agent 生命周期](chapters/chapter12/README.md)
- [Chapter 13 Goal](chapters/chapter13/README.md)
- [Chapter 14 Planner](chapters/chapter14/README.md)
- [Chapter 15 Tool](chapters/chapter15/README.md)
- [Chapter 16 Memory](chapters/chapter16/README.md)
- [Chapter 17 Context Engineering](chapters/chapter17/README.md)
- [Chapter 18 Observation](chapters/chapter18/README.md)
- [Chapter 19 Reflection](chapters/chapter19/README.md)
- [Chapter 20 State Machine](chapters/chapter20/README.md)
- [Chapter 21 Workflow Engine](chapters/chapter21/README.md)
- [Chapter 22 Multi-Agent](chapters/chapter22/README.md)
- [Chapter 23 Agent Architecture](chapters/chapter23/README.md)

### Part IV Agent Engineering —— 如何构建企业级 Agent

- [Chapter 24 Prompt Engineering](chapters/chapter24/README.md)
- [Chapter 25 Knowledge Engineering](chapters/chapter25/README.md)
- [Chapter 26 RAG](chapters/chapter26/README.md)
- [Chapter 27 Semantic Layer](chapters/chapter27/README.md)
- [Chapter 28 Guardrails](chapters/chapter28/README.md)
- [Chapter 29 Evaluation](chapters/chapter29/README.md)
- [Chapter 30 Observability](chapters/chapter30/README.md)
- [Chapter 31 Performance](chapters/chapter31/README.md)
- [Chapter 32 Cost Optimization](chapters/chapter32/README.md)
- [Chapter 33 Deployment](chapters/chapter33/README.md)

### Part V Frameworks —— 主流 Agent 框架设计

使用同一个受治理销售分析业务，对八种框架/平台的运行时、状态、工具、输出、权限与恢复能力进行横向比较。每章包含独立 `requirements.txt`、环境变量模板和具备完整运行入口的 Python MVP。

- [Chapter 34 OpenAI Agents SDK](chapters/chapter34/README.md)
- [Chapter 35 LangGraph](chapters/chapter35/README.md)
- [Chapter 36 Google ADK](chapters/chapter36/README.md)
- [Chapter 37 CrewAI](chapters/chapter37/README.md)
- [Chapter 38 AutoGen](chapters/chapter38/README.md)
- [Chapter 39 PydanticAI](chapters/chapter39/README.md)
- [Chapter 40 LlamaIndex](chapters/chapter40/README.md)
- [Chapter 41 Dify](chapters/chapter41/README.md)

### Part VI Enterprise Practice —— 企业实践

- [Chapter 42 SQL Agent](chapters/chapter42/README.md)
- [Chapter 43 Data Agent](chapters/chapter43/README.md)
- [Chapter 44 BI Agent](chapters/chapter44/README.md)
- [Chapter 45 Coding Agent](chapters/chapter45/README.md)
- [Chapter 46 Enterprise Knowledge Agent](chapters/chapter46/README.md)
- [Chapter 47 Customer Service Agent](chapters/chapter47/README.md)
- [Chapter 48 Manufacturing Agent](chapters/chapter48/README.md)
- [Chapter 49 Multi-Agent 企业平台](chapters/chapter49/README.md)

### Part VII Future —— 下一代软件

- [Chapter 50 Agent Platform](chapters/chapter50/README.md)
- [Chapter 51 Agent Operating System](chapters/chapter51/README.md)
- [Chapter 52 Computer Use](chapters/chapter52/README.md)
- [Chapter 53 AI Native Software](chapters/chapter53/README.md)
- [Chapter 54 Future of Software Engineering](chapters/chapter54/README.md)

## 开发环境

当前仓库以 Python 为主要示例语言。

```bash
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install -U pip
python -m pip install -r requirements.txt
python -m pip install -e .
```

运行 Agent Runtime 的第一个端到端案例：

```bash
python examples/sql-agent/main.py "查询 2025 年各区域净销售额" --show-trace
```

启动 API：

```bash
uvicorn sql_agent.api:app --app-dir examples/sql-agent --port 8080
```

使用 Docker：

```bash
docker compose -f examples/sql-agent/docker-compose.yml up --build
```

运行任意章节的独立 MVP：

```bash
cd chapters/chapter34
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python example.py
```

## 核心路线

本项目坚持：

```text
Agent Runtime
  ↓
OpenAI Agents SDK / LangGraph / Google ADK / CrewAI
  ↓
AutoGen / PydanticAI / LlamaIndex / Dify
```

先理解并实现 Agent Runtime，再学习成熟框架为什么这样设计。

当前 `framework/ v0.1.0` 已提供 Goal、Plan、Tool、Policy、Executor、Memory、State Machine、Trace 和 Evidence 的统一契约。`examples/sql-agent/` 展示这些能力如何组合成一条可运行、可服务化、可容器化的企业案例。

## License

待定。
