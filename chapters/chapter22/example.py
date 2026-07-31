"""Chapter 22: delegate a task to a capability-scoped specialist."""

from multi_agent_runtime import AgentCard, Coordinator, TaskEnvelope


def main() -> None:
    coordinator = Coordinator(max_delegations=3)
    coordinator.register(
        AgentCard(
            "data-agent",
            ("sales", "analysis"),
            ("sales:read",),
            "分析收入趋势、区域销售和经营异常",
        ),
        lambda task: {"answer": "华东收入下降 12%", "confidence": 0.91, "evidence": ["query-7"]},
    )
    task = TaskEnvelope("task-1", "分析华东销售异常", ("sales", "analysis"), ("sales:read",))
    print("discovered:", [card.agent_id for card in coordinator.discover(task.objective, task.delegated_scopes)])
    print(coordinator.delegate(task))


if __name__ == "__main__":
    main()
