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


if __name__ == "__main__":
    unittest.main()
