# Ollama Integration

当前状态：**Adapter 设计契约，尚无 Python 实现**。

## 目标接口

Ollama Adapter 连接本地或私有 Ollama 服务，优先使用原生 `/api/chat`，并可根据现有网关选择 OpenAI Compatibility。Adapter 必须探测所选模型是否真正支持 Tool Calling 和 Structured Format。

## 配置

| 变量 | 默认/必需 | 说明 |
| --- | --- | --- |
| `OLLAMA_BASE_URL` | `http://localhost:11434` | 服务地址 |
| `OLLAMA_MODEL` | 必需 | 本地已拉取模型 |
| `OLLAMA_TIMEOUT_SECONDS` | `120` | 冷加载可能较慢 |

## 映射要求

- Chat Messages、Tool Calls、JSON/JSON Schema Format 与 Usage 归一化；
- 处理 Streaming Chunk、模型加载时间和 Keep Alive；
- 将“服务不可达”“模型不存在”“输出 Schema 不合法”分开报告；
- 记录模型名称、量化/部署元数据和本地 Endpoint；
- 不因运行在本地就跳过 Scope、DLP 和审计。

## 验收

纯文本、JSON Schema、Tool Round-trip、Streaming、冷/热延迟、并发和模型不支持能力的显式失败都要进入测试。生产环境还需验证 GPU/CPU 资源、队列和数据驻留。

官方资料：[Ollama Chat API](https://docs.ollama.com/api/chat)、[Tool Calling](https://docs.ollama.com/capabilities/tool-calling)。
