"""CLI entry point for the SQL Agent."""

from __future__ import annotations

from argparse import ArgumentParser
from json import dumps

from sql_agent import build_application


def main() -> None:
    parser = ArgumentParser(description="Run the AI Agent Engineering SQL Agent.")
    parser.add_argument(
        "objective",
        nargs="?",
        default="查询 2025 年各区域净销售额",
    )
    parser.add_argument("--show-trace", action="store_true")
    arguments = parser.parse_args()

    application = build_application()
    response = application.ask(arguments.objective)
    print(response.answer)
    print("\nEvidence:")
    print(dumps([item.model_dump() for item in response.evidence], ensure_ascii=False, indent=2))

    if arguments.show_trace:
        print("\nTrace:")
        print(
            dumps(
                [
                    event.model_dump(mode="json")
                    for event in application.runtime.trace.list_run(response.run_id)
                ],
                ensure_ascii=False,
                indent=2,
            )
        )


if __name__ == "__main__":
    main()
