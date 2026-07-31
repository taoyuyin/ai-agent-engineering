"""Bounded parallel execution, TTL caching and end-to-end deadlines."""

from concurrent.futures import ThreadPoolExecutor, TimeoutError
from dataclasses import dataclass
from threading import Lock
from time import monotonic
from typing import Callable, Dict, Iterable, Mapping, Tuple


@dataclass(frozen=True)
class Task:
    name: str
    cache_key: str
    operation: Callable[[], object]


class TTLCache:
    def __init__(self, ttl_seconds: float) -> None:
        self.ttl_seconds = ttl_seconds
        self._values: Dict[str, Tuple[float, object]] = {}
        self._lock = Lock()

    def get(self, key: str):
        with self._lock:
            item = self._values.get(key)
            if item is None or monotonic() - item[0] > self.ttl_seconds:
                self._values.pop(key, None)
                return None
            return item[1]

    def put(self, key: str, value: object) -> None:
        with self._lock:
            self._values[key] = (monotonic(), value)


class PerformanceRuntime:
    def __init__(self, max_workers: int = 4, cache_ttl_seconds: float = 30) -> None:
        self.max_workers = max_workers
        self.cache = TTLCache(cache_ttl_seconds)
        self.stats = {"cache_hits": 0, "executed": 0}
        self._stats_lock = Lock()

    def _run(self, task: Task) -> object:
        key = "%s:%s" % (task.name, task.cache_key)
        cached = self.cache.get(key)
        if cached is not None:
            with self._stats_lock:
                self.stats["cache_hits"] += 1
            return cached
        value = task.operation()
        self.cache.put(key, value)
        with self._stats_lock:
            self.stats["executed"] += 1
        return value

    def execute(self, tasks: Iterable[Task], deadline_ms: float) -> Mapping[str, object]:
        task_list = list(tasks)
        started = monotonic()
        with ThreadPoolExecutor(max_workers=self.max_workers) as pool:
            futures = {task.name: pool.submit(self._run, task) for task in task_list}
            result = {}
            for name, future in futures.items():
                remaining = deadline_ms / 1000 - (monotonic() - started)
                if remaining <= 0:
                    raise TimeoutError("latency budget exhausted")
                result[name] = future.result(timeout=remaining)
        return result
