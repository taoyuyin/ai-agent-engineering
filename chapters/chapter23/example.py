"""Chapter 23: run a small enterprise Agent through policy and audit boundaries."""

from enterprise_runtime import AgentRequest, EnterpriseAgentRuntime


def main() -> None:
    runtime = EnterpriseAgentRuntime()
    response = runtime.run(
        AgentRequest("run-99", "tenant-a", "user-7", "生成华东销售摘要", ("sales:read",))
    )
    print(response)
    print("context:\n", response["context"])
    print("embedding:", response["embedding_model"])
    print(runtime.audit.events)


if __name__ == "__main__":
    main()
