"""Chapter 12: drive an Agent run through its legal lifecycle."""

from lifecycle_runtime import AgentRun, LifecycleEngine, RunStatus


def main() -> None:
    run = AgentRun("run-001", "生成本周销售异常报告", max_steps=4, max_tokens=1200)
    engine = LifecycleEngine()
    for target, reason in [
        (RunStatus.VALIDATING, "goal_received"),
        (RunStatus.PLANNING, "goal_valid"),
        (RunStatus.RUNNING, "plan_ready"),
    ]:
        engine.transition(run, target, reason)
    engine.record_model_usage(run, input_tokens=420, output_tokens=180)
    engine.transition(run, RunStatus.COMPLETED, "success_criteria_met")
    print(run.status.value)
    print("tokens:", run.tokens_used, "/", run.max_tokens)
    for event in run.events:
        print(event)


if __name__ == "__main__":
    main()
