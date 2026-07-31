# Chapter 33 Deployment：把 Agent 作为可靠服务发布

Part IV Agent Engineering —— 如何构建企业级 Agent

Version: 2026-07

Last Updated: 2026-07-31

## Core Question

如何服务化、扩缩容、灰度和运维一个包含长任务、模型与工具依赖的企业级 Agent？

## Chapter Conclusion

Agent Deployment 不是把脚本装进 Docker。生产架构要分离 stateless API、durable run、worker、model/tool gateway 和 state store，并建立 readiness、幂等、灰度、回滚、容量和安全边界。

## Learning Objectives

- 设计同步 API 与异步 Run API
- 区分 API、Worker、Workflow、Gateway 和 Store
- 选择容器、Kubernetes、Ray Serve、BentoML 等部署层
- 建立多模型、高可用和安全发布策略
- 运行一个带 health/readiness/run resource 的 HTTP MVP

## 33.1 部署拓扑

```text
Client → API Gateway → Agent API → Run Store
                              ↓
                       Queue / Workflow
                              ↓
                         Agent Worker
                       ↙             ↘
              Model Gateway       Tool Gateway
                       ↓             ↓
                 Model Serving   Enterprise Systems
```

API 接受请求并创建 run；长任务由 worker/workflow 执行。客户端轮询、Webhook 或订阅事件，不占用一个长 HTTP 连接。

## 33.2 服务契约

建议资源模型：

```text
POST /runs              创建，返回 202 + run_id
GET  /runs/{id}         状态与结果
POST /runs/{id}/cancel  请求取消
GET  /healthz           进程存活
GET  /readyz            可安全接流量
```

创建副作用任务要支持 idempotency key。状态至少区分 queued、running、waiting_approval、succeeded、failed、cancelled。

## 33.3 扩缩容

- API 按请求率/并发扩展；
- Worker 按 queue depth、oldest age、active run 扩展；
- Model serving 按 GPU 利用率、KV cache、token throughput 扩展；
- 工具依赖有独立 rate limit 和 bulkhead；
- scale-to-zero 适合离线低频服务，不适合严格 TTFT；
- 多租户要有公平调度和配额，避免 noisy neighbor。

CPU HPA 指标通常不足以代表 Agent backlog。

## 33.4 发布策略

发布单元不只有镜像，还包括：

```text
runtime + prompt + model catalog + tool schema
+ policy + knowledge/index + semantic catalog + evaluator
```

先跑离线 eval，再 shadow/canary。数据库和 state schema 使用向前/向后兼容迁移。回滚时必须考虑旧 Worker 是否能读取新 checkpoint。

## 33.5 多模型部署

托管 API 便于弹性和模型更新，自托管便于数据边界与推理控制。常见组合是 Model Gateway 对上提供统一 contract，对下连接多个 provider 和 vLLM/TGI。Gateway 执行路由、配额、熔断和 usage，但不应吞掉 provider 原始错误。

## 33.6 工具横向对比

| 工具 | 强项 | 局限 | 适用 |
|---|---|---|---|
| Kubernetes | 通用编排、Probe、HPA、隔离 | 平台复杂度 | 标准企业底座 |
| KEDA | Queue/Event 驱动扩缩容 | 依赖 scaler/指标质量 | Agent Worker |
| Ray Serve | Python 模型/推理 DAG 与伸缩 | 引入 Ray 运行时 | AI serving |
| BentoML | 模型服务打包、部署抽象 | 与既有平台整合需设计 | 模型/API 服务 |
| vLLM | 高吞吐 LLM serving | 主要是推理层 | 自托管 LLM |
| Serverless | 运维少、弹性快 | 冷启动、时限、状态 | 短、无状态任务 |

Kubernetes 解决进程编排，不自动解决 durable workflow、Agent state 或 evaluation。

## 33.7 企业案例：多租户 Data Agent

API 通过 SSO 取得 tenant 和 scope，创建 immutable run request。Workflow 冻结 semantic catalog 和数据快照，Worker 生成查询并等待审批。Model Gateway 按区域路由；Tool Gateway 使用行级权限访问数仓。KEDA 按 queue age 扩 Worker，Pod 终止前停止接新 run 并保存 checkpoint。新 Prompt/Runtime 只接 5% 租户并通过在线门禁后晋级。

## 33.8 Python + Container MVP

`deployment_runtime` 包含：

- `AgentService` 请求验证、readiness、run store 与 graceful shutdown；
- 标准库 `ThreadingHTTPServer` 适配器；
- 非 root Dockerfile；
- Kubernetes Deployment、Service、Probe 与资源限制。

```bash
python3 chapters/chapter33/example.py
python3 -m unittest discover -s chapters/chapter33 -p "test_*.py"

docker build -f chapters/chapter33/deployment_runtime/Dockerfile \
  -t agent-service:chapter33 chapters/chapter33
```

内存 Run Store 只用于 MVP，生产应使用持久数据库与 durable workflow。

## 33.9 Production Readiness Checklist

- [ ] 长任务使用 Run API + durable execution
- [ ] create/cancel/tool side effect 支持幂等
- [ ] readiness 与 liveness 语义正确
- [ ] shutdown 停止接流量并保存 checkpoint
- [ ] API/Worker/Model 按正确指标独立扩缩容
- [ ] Secret、network、service identity 和 egress 最小权限
- [ ] 版本组合可追踪、评估、灰度和回滚
- [ ] 多 AZ/区域故障与 provider outage 已演练
- [ ] SLO、容量、成本、安全和数据恢复有 runbook

## Summary

企业 Agent 的部署对象是一个有状态、外部依赖多、行为非确定的分布式系统。把控制面、执行面和推理面分离，才能独立扩展、隔离故障并安全发布。

## Notes

示例 Kubernetes manifest 用于解释部署边界，不包含生产 Ingress、TLS、PDB、NetworkPolicy、Secret Manager、HPA/KEDA 和持久存储。

## References

[1] Kubernetes, Concepts.
https://kubernetes.io/docs/concepts/

[2] KEDA Documentation.
https://keda.sh/docs/

[3] Ray Serve Documentation.
https://docs.ray.io/en/latest/serve/

[4] BentoML Documentation.
https://docs.bentoml.com/en/latest/

[5] OpenAI, Production best practices.
https://developers.openai.com/api/docs/guides/production-best-practices

以上 URL 已在 2026-07-31 核对。
