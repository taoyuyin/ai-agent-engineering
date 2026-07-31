import unittest

from state_machine_runtime import AgentStateMachine, EventStore


class StateMachineTest(unittest.TestCase):
    def test_replay_rebuilds_terminal_state(self) -> None:
        machine = AgentStateMachine(EventStore())
        for event in ("goal_validated", "plan_created", "completed"):
            machine.apply("1", event)
        self.assertEqual("completed", machine.rebuild("1"))

    def test_illegal_event_does_not_mutate_stream(self) -> None:
        store = EventStore()
        with self.assertRaises(ValueError):
            AgentStateMachine(store).apply("1", "completed")
        self.assertEqual([], store.events("1"))


if __name__ == "__main__":
    unittest.main()
