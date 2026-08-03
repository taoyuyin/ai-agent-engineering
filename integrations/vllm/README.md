# vLLM Integration

当前状态：**Adapter 设计契约，尚无 Python 实现**。

## 目标接口

vLLM Adapter 面向自托管 OpenAI-compatible Server。协议兼容并不保证具体模型具备相同 Tool Calling、Chat Template、Reasoning 或 Structured Output 行为，因此部署配置和模型能力必须一起版本化。

## 配置

| 变量 | 默认/必需 | 说明 |
| --- | --- | --- |
| `VLLM_BASE_URL` | 必需 | 通常以 `/v1` 结尾 |
| `VLLM_API_KEY` | 部署决定 | 网关或服务鉴权 |
| `VLLM_MODEL` | 必需 | Served Model Name |
| `VLLM_TIMEOUT_SECONDS` | 否 | 请求超时 |

## 映射要求

- 复用统一 OpenAI-compatible Transport，但保留 Provider=`vllm`；
- 启动配置记录 Model、Tokenizer、Chat Template、Tool Parser 和 Generation Config；
- 明确哪些 Endpoint 和参数经过本部署验证；
- 解析 Tool Call 前验证模型/Parser 能力，不把自由文本伪装为调用；
- 采集 Queue、TTFT、Tokens/s、KV Cache 和 GPU 指标；
- 错误区分协议、模型模板、显存、排队和超时。

## 验收

除统一 Adapter Contract Test 外，必须对每个部署模型运行 Tool/Schema Eval。升级 vLLM、模型、Tokenizer 或 Chat Template 任一项都触发回归。负载测试同时报告吞吐和 P95/P99 延迟。

官方资料：[vLLM OpenAI-Compatible Server](https://docs.vllm.ai/en/latest/serving/online_serving/openai_compatible_server/)。
