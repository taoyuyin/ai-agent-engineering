# Deployment Runtime MVP

本模块把 Agent 暴露为可部署服务资源，并提供标准库 HTTP Adapter、Dockerfile 和 Kubernetes 示例。

## 实现内容

- `AgentService` 验证 Tenant、Goal 和请求大小；
- `POST /runs` 创建异步语义的 Queued Run；
- `GET /runs/{id}` 查询状态；
- `/healthz` 与 `/readyz` 区分存活和接流量；
- Graceful Shutdown 停止接收新 Run；
- Kubernetes 配置包含副本、Probe 和资源限制。

## 模型关系

`MODEL_ENDPOINT` 表示独立 Model Gateway；HTTP Service 不直接硬编码厂商 SDK。当前 MVP 不实际执行模型，只验证服务与部署边界。

```bash
python chapters/chapter33/example.py
python -m unittest discover -s chapters/chapter33 -p "test_*.py"
```

生产仍需 Queue、持久状态、认证、TLS、幂等、限流、Secret、Telemetry 和 Autoscaling。正文见 [Chapter 33](../README.md)。
