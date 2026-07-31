"""Chapter 33: exercise the service boundary without starting a network server."""

from deployment_runtime import AgentService


def main() -> None:
    service = AgentService(model_endpoint="http://model-gateway:8000", max_request_chars=2000)
    service.mark_ready()
    print(service.health())
    run = service.create_run({"tenant_id": "retail", "goal": "生成销售摘要"})
    print(run)
    print(service.get_run(run["run_id"]))


if __name__ == "__main__":
    main()
