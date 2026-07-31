"""Chapter 30: record a nested Agent trace without leaking secrets."""

from observability_runtime import TraceRecorder


def main() -> None:
    recorder = TraceRecorder("run-42")
    with recorder.span("agent.run", {"tenant_id": "retail"}):
        with recorder.span("tool.call", {"tool": "crm.read", "api_key": "secret"}):
            pass
    print(recorder.to_json())
    print(recorder.metrics())


if __name__ == "__main__":
    main()
