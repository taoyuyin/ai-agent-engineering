"""Chapter 13: turn an ambiguous request into an executable Goal contract."""

from goal_runtime import GoalCompiler, GoalEvaluator


def main() -> None:
    goal = GoalCompiler().compile(
        {
            "objective": "生成华东区本月销售异常报告",
            "constraints": ["只读数据", "不包含个人联系方式"],
            "success_criteria": ["包含收入指标", "列出异常门店"],
            "allowed_tools": ["query_sales"],
            "risk_level": "medium",
        }
    )
    evidence = {"包含收入指标": True, "列出异常门店": True}
    print(goal)
    print(GoalEvaluator().evaluate(goal, evidence))


if __name__ == "__main__":
    main()
