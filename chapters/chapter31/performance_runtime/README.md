# Performance Runtime MVP

本模块展示 Agent 性能优化的三个基础控制：有界并行、TTL Cache 和端到端 Deadline。

## 实现内容

- `Task` 声明名称、Cache Key 和 Operation；
- `ThreadPoolExecutor` 并行运行独立任务；
- `TTLCache` 使用 Lock 保证进程内并发安全；
- False 等合法值不会被误判为 Cache Miss；
- Deadline 按整个批次剩余时间执行，而不是每个 Tool 单独重置。

## 模型关系

模型调用、检索和只读 Tool 都可包装为 Task；是否并行和缓存由 Runtime 根据依赖、幂等、数据时效与权限决定。

```bash
python chapters/chapter31/example.py
python -m unittest discover -s chapters/chapter31 -p "test_*.py"
```

生产升级包括异步 I/O、Single-flight、分布式 Cache、取消、背压和 SLO 分解。正文见 [Chapter 31](../README.md)。
