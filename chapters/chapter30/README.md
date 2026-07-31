# Chapter 30 Observability：看见 Agent 为什么这样行动

Part IV Agent Engineering —— 如何构建企业级 Agent

Version: 2026-07

Last Updated: 2026-07-31

## Core Question

如何用 Logging、Metrics、Tracing 和 Timeline 重建一次 Agent Run 的决策与执行过程？

## Chapter Conclusion

Agent Observability 的最小分析单元不是 HTTP 请求，而是包含模型、检索、工具、状态转移和评估的 Run。Trace 负责因果关系，Metrics 负责趋势告警，Logs/Events 负责审计细节。

## Learning Objectives

- 设计 run/trace/span/event 数据模型
- 建立模型、RAG、Tool 和 Workflow 统一关联
- 区分运维 telemetry、质量证据与审计日志
- 对比 OTel、OpenInference、Langfuse、Phoenix、LangSmith
- 运行一个嵌套、脱敏、错误可见的 Trace Recorder

## 30.1 为什么普通 APM 不够

HTTP 200 只表示接口成功，不表示答案正确。Agent 失败可能来自错误 Prompt 版本、召回旧文档、模型选错工具、重试耗尽或审批超时。因此要记录 logical run，而不只记录进程调用。

## 30.2 Trace 模型

```text
Run / Trace
├── goal.compile
├── retrieval.query
│   └── rerank
├── model.generate
├── tool.call
├── reflection
└── evaluator
```

关键属性包括 run_id、tenant_id、prompt/model/tool/knowledge version、token、cost、status、retry、citation 和 policy decision。敏感正文默认不采集或先脱敏。

## 30.3 四类信号

| 信号 | 回答 |
|---|---|
| Metrics | 失败率、P95、成本是否异常 |
| Trace | 哪一步、为何慢或失败 |
| Structured Log/Event | 具体状态和错误上下文 |
| Audit | 谁以何身份对什么资源做了什么 |

审计记录通常需要更强不可变性和保留策略，不能等同于调试日志。

## 30.4 工具横向对比

| 工具 | 定位 | 优点 | 局限 |
|---|---|---|---|
| OpenTelemetry | 通用 telemetry 标准 | 厂商中立、生态广 | Agent UI/评估需上层 |
| OpenInference | AI/LLM 语义约定与 instrumentation | 衔接 OTel、框架覆盖广 | 后端需另选 |
| Langfuse | LLM trace、prompt、eval、usage | 开源/托管、Agent 视图 | 与通用 APM 仍需整合 |
| Arize Phoenix | Trace、RAG/LLM 分析和评估 | OpenInference 生态强 | 企业运维方案需评估 |
| LangSmith | LangChain trace/eval/deployment 体验 | 生态集成顺滑 | 平台耦合权衡 |
| OpenAI Agents Tracing | SDK 原生 Agent trace | 接入成本低 | 跨栈统一需 OTel/网关 |

## 30.5 采样与隐私

全量保存 Prompt/Output 会带来 PII、密钥、知识产权和成本风险。建议：

- metadata 全量，正文按风险采样；
- ingest 前 redaction/tokenization；
- tenant 与环境分区；
- debug 临时提权并审计；
- 生产保留期、删除和导出策略明确。

## 30.6 企业案例：客服 Agent 事故

投诉显示 Agent 错误承诺退款。通过 trace 发现检索命中了已退役政策，原因是删除事件未传播到向量索引。系统可按 knowledge_version 找到全部受影响 Run，回放评估、下线索引并通知相关客户。只有一条文本日志无法完成此类影响分析。

## 30.7 Python MVP

`observability_runtime` 实现 parent-child span、duration、status、属性脱敏、JSON 导出和聚合指标：

```bash
python3 chapters/chapter30/example.py
python3 -m unittest discover -s chapters/chapter30 -p "test_*.py"
```

## 30.8 Production Readiness Checklist

- [ ] 所有组件传播 run/trace context
- [ ] Span 覆盖 model、retrieval、tool、workflow、eval
- [ ] 版本、usage、policy decision 可关联
- [ ] 错误、重试和 fallback 明确记录
- [ ] Prompt/Output 默认最小化并脱敏
- [ ] 质量、延迟、成本、安全分别告警
- [ ] Trace 可链接 evaluation 和用户反馈
- [ ] 审计存储与调试日志分离

## Summary

Observability 让非确定性系统具备可调查性。能重建 Run，团队才有能力定位回归、评估影响、控制成本并安全迭代。

## Notes

OpenTelemetry GenAI 语义约定仍在演进；生产 schema 应显式版本化，并通过 adapter 与内部稳定事件模型解耦。

## References

[1] OpenTelemetry, Generative AI semantic conventions.
https://opentelemetry.io/docs/specs/semconv/gen-ai/

[2] OpenInference Documentation.
https://arize-ai.github.io/openinference/

[3] Langfuse Documentation.
https://langfuse.com/docs

[4] OpenAI Agents SDK, Tracing.
https://openai.github.io/openai-agents-python/tracing/

以上 URL 已在 2026-07-31 核对。
