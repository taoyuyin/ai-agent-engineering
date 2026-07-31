"""Chapter 14: execute a dependency-aware plan and repair one failed step."""

from planner_runtime import Plan, PlanStep


def main() -> None:
    plan = Plan(
        [
            PlanStep("load", "加载销售数据"),
            PlanStep("analyze", "分析异常", depends_on=("load",)),
            PlanStep("report", "生成报告", depends_on=("analyze",)),
        ]
    )
    while not plan.complete:
        step = plan.ready_steps()[0]
        plan.mark_completed(step.step_id, {"ok": True})
        print("completed:", step.step_id)


if __name__ == "__main__":
    main()
