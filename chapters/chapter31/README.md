# Chapter 31 Performance：优化 Agent 的关键路径

Part IV Agent Engineering —— 如何构建企业级 Agent

Version: 2026-07

Last Updated: 2026-07-31

## Core Question

如何围绕 Latency、Cache、Batch、Parallelism 和 Streaming 优化 Agent，而不破坏正确性？

## Chapter Conclusion

性能优化先减少工作，再并行独立工作，最后加速模型。Agent 的 P95 是模型、检索、工具、队列与重试的总和，必须用 trace 和 latency budget 优化关键路径。

## Learning Objectives

- 分解 TTFT、生成、工具和端到端延迟
- 设计 deadline、timeout、parallelism 与 backpressure
- 区分结果缓存、Prompt Cache、KV Cache 和语义缓存
- 理解 batch、continuous batching 与 streaming 的权衡
- 运行带 TTL Cache、并行和 deadline 的 MVP

## 31.1 延迟预算

```text
P95 total = queue + retrieval + model TTFT + generation
          + tool calls + retries + serialization
```

为端到端 SLO 分配子预算，并向下游传播 deadline。每层各自使用 30 秒 timeout，会让总延迟不可控。

## 31.2 优化顺序

1. 删除不必要模型调用和反思循环；
2. 缩短输出，精简上下文；
3. 缓存确定且可安全复用的结果；
4. 并行无依赖检索/工具；
5. 使用 streaming 改善感知延迟；
6. 批处理离线任务，推理服务做 continuous batching；
7. 最后再考虑更昂贵的硬件与模型服务优化。

## 31.3 Cache 类型

| Cache | Key | 风险 |
|---|---|---|
| Tool/Result | tenant + args + data version | 新鲜度、权限 |
| Exact Response | normalized request + versions | 个性化与泄漏 |
| Semantic | embedding similarity + policy | 错误复用、难失效 |
| Provider Prompt Cache | 相同前缀 | 厂商规则、隐私 |
| KV Cache | token prefix/session | GPU 内存与调度 |

Cache key 必须包含 tenant、policy、Prompt、模型和知识版本中会影响结果的部分。

## 31.4 Batch、Parallel、Streaming

- Batch 适合非实时评估、索引、夜间报表；
- continuous batching 提高推理吞吐，但可能增加排队；
- parallel 只用于无依赖步骤，并设置并发上限；
- streaming 降低感知等待，但不降低完整生成时间；
- side effect 不应为追求速度盲目并行。

## 31.5 工具横向对比

| 工具 | 强项 | 适用 |
|---|---|---|
| vLLM | 高吞吐 LLM serving、continuous batching | 自托管模型 |
| NVIDIA Triton | 多模型、dynamic batching、GPU serving | 异构推理平台 |
| Hugging Face TGI | 文本生成服务与标准部署 | HF 模型服务 |
| Provider Batch API | 托管离线批处理 | Eval、离线生成 |
| Redis | 分布式 cache、rate limit、协调 | Agent 服务层 |
| 自建 Bounded Executor | 工具并发和 deadline | Runtime 关键路径 |

## 31.6 企业案例：研究 Agent

研究 Agent 并行执行三个只读数据源，统一 deadline 为 12 秒；模型生成与工具调用分别分配预算。相同政策查询按 tenant + policy version 缓存，金融行情不缓存或使用秒级 TTL。正文 streaming 前先完成引用和安全校验，避免边生成边泄漏。

## 31.7 Python MVP

`performance_runtime` 实现 TTL Cache、bounded thread pool、独立任务并行和端到端 deadline：

```bash
python3 chapters/chapter31/example.py
python3 -m unittest discover -s chapters/chapter31 -p "test_*.py"
```

## 31.8 Production Readiness Checklist

- [ ] 建立 P50/P95/P99 与 TTFT 指标
- [ ] deadline 从入口传播到所有下游
- [ ] 每个 cache 定义权限、版本与失效
- [ ] 独立任务并行且有限流/backpressure
- [ ] 重试有预算、jitter 和幂等
- [ ] Streaming 前置必要安全检查
- [ ] 批任务与交互流量隔离
- [ ] 优化用 trace 和负载测试验证

## Summary

高性能 Agent 不是单次 benchmark 更快，而是在并发、失败和长尾条件下仍满足 SLO。最有效的优化通常是减少串行步骤与无价值 Token。

## Notes

推理引擎特性随版本快速变化，选型应使用自己的模型、序列长度和并发分布压测。

## References

[1] OpenAI, Latency optimization.
https://developers.openai.com/api/docs/guides/latency-optimization

[2] OpenAI, Batch API.
https://developers.openai.com/api/docs/guides/batch

[3] vLLM Documentation.
https://docs.vllm.ai/en/latest/

[4] NVIDIA Triton, Batchers.
https://docs.nvidia.com/deeplearning/triton-inference-server/user-guide/docs/user_guide/batcher.html

以上 URL 已在 2026-07-31 核对。
