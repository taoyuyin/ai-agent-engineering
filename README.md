# AI Agent Engineering

AI Agent Engineering 是一个面向工程实践的 AI Agent 系列教程与源码仓库。

这个项目会从最小可运行的 Agent 开始，逐步覆盖工具调用、规划、记忆、工作流、RAG、浏览器自动化、多 Agent 协作、评测与部署等主题。

## 项目目标

- 用源码解释 AI Agent 的核心机制，而不是只停留在概念层
- 构建一个可教学、可扩展的 Agent Runtime
- 提供完整案例，展示 Agent 在真实任务中的工程落地方式
- 沉淀提示词、数据集、评测方法和架构图，方便复用与二次开发

## 目录结构

```text
ai-agent-engineering/
├── docs/                    # 教材配套文档
├── chapters/                # 每章源码
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

## 推荐阅读路径

1. `chapters/chapter01`：从一个最小 Agent 开始
2. `framework/`：理解 Agent Runtime 的核心组件
3. `examples/`：阅读完整应用案例
4. `evaluation/`：学习如何评测 Agent 的效果
5. `architecture/`：补齐工程架构、部署和企业级设计

## 项目文档

- [写作规范](docs/writing-guidelines.md)
- [项目路线图](docs/roadmap.md)

## 开发环境

当前仓库以 Python 为主要示例语言。

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -U pip
```

运行第一章示例：

```bash
python chapters/chapter01/minimal_agent.py
```

## 内容规划

- Chapter 01：什么是 Agent：最小循环
- Chapter 02：工具调用：让 Agent 连接外部世界
- Chapter 03：Planner：任务拆解与执行计划
- Chapter 04：Memory：短期记忆与长期记忆
- Chapter 05：Workflow：可控流程与 Agent 自主性的边界
- Chapter 06：RAG Agent：检索增强生成
- Chapter 07：Browser Agent：浏览器自动化
- Chapter 08：Coding Agent：代码生成、修改与验证
- Chapter 09：Multi-Agent：协作、分工与冲突处理
- Chapter 10：Evaluation：如何评测 Agent
- Chapter 11：Deployment：从 Demo 到生产系统
- Chapter 12：Enterprise Agent：权限、审计、安全与治理

## License

待定。
