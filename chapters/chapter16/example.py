"""Chapter 16: write and retrieve tenant-isolated long-term memories."""

from memory_runtime import MemoryRecord, MemoryStore


def main() -> None:
    store = MemoryStore()
    store.put(MemoryRecord("m1", "tenant-a", "user-7", "semantic", "用户偏好中文技术报告", 0.9))
    store.put(MemoryRecord("m2", "tenant-a", "user-7", "episodic", "上次分析华东销售异常", 0.6))
    for memory in store.search("tenant-a", "user-7", "请使用中文生成工程文档", limit=2):
        print(memory.memory_id, memory.content, memory.embedding_model)


if __name__ == "__main__":
    main()
