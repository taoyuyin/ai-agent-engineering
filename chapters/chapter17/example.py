"""Chapter 17: assemble context with section quotas and provenance."""

from context_runtime import ContextAssembler, ContextItem, ContextPolicy


def main() -> None:
    policy = ContextPolicy(total_budget=80, section_budgets={"policy": 30, "evidence": 35, "history": 15})
    items = [
        ContextItem("p1", "policy", "只能读取授权区域的数据", 100, True),
        ContextItem("e1", "evidence", "华东收入较上月下降 12%", 90, True),
        ContextItem("h1", "history", "此前用户询问过华南数据" * 20, 10, False),
    ]
    result = ContextAssembler(policy).assemble_for("分析华东收入异常", items)
    print(result.render())
    print(result.dropped)


if __name__ == "__main__":
    main()
