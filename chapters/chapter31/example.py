"""Chapter 31: cache repeated work and parallelize independent tasks."""

from performance_runtime import PerformanceRuntime, Task


def main() -> None:
    runtime = PerformanceRuntime(max_workers=2, cache_ttl_seconds=60)
    tasks = [
        Task("profile", "customer-7", lambda: {"tier": "gold"}),
        Task("orders", "customer-7", lambda: ["O-1", "O-2"]),
    ]
    print(runtime.execute(tasks, deadline_ms=500))
    print(runtime.execute(tasks, deadline_ms=500))
    print(runtime.stats)


if __name__ == "__main__":
    main()
