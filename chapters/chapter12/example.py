"""Chapter 12: drive an Agent run through its legal lifecycle."""

from lifecycle_runtime import AgentRun, LifecycleEngine, RunStatus


def main() -> None:
    run = AgentRun("run-001", "生成本周销售异常报告", max_steps=4)
    engine = LifecycleEngine()
    for target, reason in [
        (RunStatus.VALIDATING, "goal_received"),
        (RunStatus.PLANNING, "goal_valid"),
        (RunStatus.RUNNING, "plan_ready"),
        (RunStatus.COMPLETED, "success_criteria_met"),
    ]:
        engine.transition(run, target, reason)
    print(run.status.value)
    for event in run.events:
        print(event)


if __name__ == "__main__":
    main()
