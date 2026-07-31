"""Chapter 20: rebuild Agent state by replaying immutable events."""

from state_machine_runtime import AgentStateMachine, EventStore


def main() -> None:
    store = EventStore()
    machine = AgentStateMachine(store)
    for event in ("goal_validated", "plan_created", "tool_requested", "tool_succeeded", "completed"):
        machine.apply("run-42", event)
    print(machine.rebuild("run-42"))
    print(store.events("run-42"))


if __name__ == "__main__":
    main()
