import unittest

from memory_runtime import MemoryRecord, MemoryStore


class MemoryTest(unittest.TestCase):
    def test_isolates_tenants(self) -> None:
        store = MemoryStore()
        store.put(MemoryRecord("1", "a", "u", "semantic", "secret alpha", 1.0))
        self.assertEqual([], store.search("b", "u", "secret"))

    def test_update_increments_version(self) -> None:
        store = MemoryStore()
        record = MemoryRecord("1", "a", "u", "semantic", "old", 1.0)
        store.put(record)
        store.put(MemoryRecord("1", "a", "u", "semantic", "new", 1.0))
        self.assertEqual(2, store.search("a", "u", "new")[0].version)

    def test_semantic_index_is_deleted_with_memory(self) -> None:
        store = MemoryStore()
        store.put(MemoryRecord("1", "a", "u", "semantic", "用户偏好中文报告", 1.0))
        self.assertEqual("1", store.search("a", "u", "中文文档")[0].memory_id)
        store.forget("a", "u", "1")
        self.assertEqual([], store.search("a", "u", "中文文档"))


if __name__ == "__main__":
    unittest.main()
