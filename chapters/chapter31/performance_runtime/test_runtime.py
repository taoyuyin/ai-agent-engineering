import unittest

from performance_runtime import PerformanceRuntime, Task, TTLCache


class PerformanceRuntimeTest(unittest.TestCase):
    def test_second_execution_uses_cache(self):
        calls = []
        runtime = PerformanceRuntime(max_workers=1, cache_ttl_seconds=30)
        task = Task("tool", "same", lambda: calls.append(1) or "value")
        self.assertEqual({"tool": "value"}, runtime.execute([task], 1000))
        self.assertEqual({"tool": "value"}, runtime.execute([task], 1000))
        self.assertEqual(1, len(calls))
        self.assertEqual(1, runtime.stats["cache_hits"])

    def test_independent_tasks_return_by_name(self):
        runtime = PerformanceRuntime(max_workers=2)
        result = runtime.execute(
            [Task("a", "1", lambda: 1), Task("b", "1", lambda: 2)], 1000
        )
        self.assertEqual({"a": 1, "b": 2}, result)

    def test_cache_miss_is_distinct_from_false_value(self):
        cache = TTLCache(30)
        cache.put("k", False)
        self.assertIs(False, cache.get("k"))


if __name__ == "__main__":
    unittest.main()
