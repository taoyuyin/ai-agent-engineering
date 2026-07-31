"""Chapter 21: run a deterministic DAG with a human approval gate."""

from workflow_runtime import Task, Workflow


def main() -> None:
    workflow = Workflow(
        [
            Task("query", lambda state: {"revenue": 218000}),
            Task("draft", lambda state: {"report": "ready"}, depends_on=("query",)),
            Task("publish", lambda state: {"published": True}, depends_on=("draft",), approval=True),
        ]
    )
    workflow.run_until_blocked()
    print(workflow.statuses())
    workflow.approve("publish")
    workflow.run_until_blocked()
    print(workflow.statuses())


if __name__ == "__main__":
    main()
