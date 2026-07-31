"""Chapter 9 entry point: an observable, bounded ReAct controller."""

from reasoning_runtime import ReasoningController, ToolRegistry


def main() -> None:
    tools = ToolRegistry()
    tools.register("get_churn_rate", lambda segment: {"segment": segment, "rate": 0.18})
    tools.register("get_ticket_rate", lambda segment: {"segment": segment, "rate": 0.31})

    controller = ReasoningController(tools, max_steps=4, max_repairs=1)
    result = controller.run("定位 enterprise 客户流失原因", segment="enterprise")

    for event in result.trace:
        print("{:<12} {}".format(event.kind, event.detail))
    print("Final:", result.answer)


if __name__ == "__main__":
    main()
