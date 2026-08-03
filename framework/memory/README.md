# Memory

`store.py` 定义 `MemoryRecord` 和进程内 `InMemoryStore`，用于保存一次 Run 的 Observation。

## 当前 Contract

Record 包含 Tenant、Run、Kind、Content、Metadata、Record ID 和 UTC 创建时间。`list_run()` 同时按 Tenant 与 Run 过滤，展示 Memory 隔离必须由存储层执行，而不是靠 Prompt 提醒。

## 当前限制

- 进程退出后丢失；
- 不支持 TTL、删除、版本和并发；
- 不做 Embedding 和跨 Run Retrieval；
- Content 未自动脱敏或加密。

因此 v0.1 只适合教学和测试，不能保存生产用户长期记忆。

## 生产扩展

Adapter 应明确 Working、Episodic、Semantic 和 Preference Memory，支持 Tenant/Subject Namespace、来源、Confidence、有效期、删除传播、Embedding Model 与 Index Version。敏感记忆写入需要用户授权和数据治理。

对应 Chapter 16、17；更完整的教学检索实现见 Chapter 16 `memory_runtime`。
