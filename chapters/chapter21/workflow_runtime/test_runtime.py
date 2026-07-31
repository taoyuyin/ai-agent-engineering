import unittest

from workflow_runtime import Task, Workflow


class WorkflowTest(unittest.TestCase):
    def test_pauses_at_approval_gate(self) -> None:
        flow = Workflow([Task("a", lambda state: {"a": 1}, approval=True)])
        flow.run_until_blocked()
        self.assertEqual("pending", flow.statuses()["a"])
        flow.approve("a")
        flow.run_until_blocked()
        self.assertEqual("completed", flow.statuses()["a"])

    def test_dependency_order(self) -> None:
        flow = Workflow(
            [Task("a", lambda state: {"a": 1}), Task("b", lambda state: {"b": state["a"]}, ("a",))]
        )
        flow.run_until_blocked()
        self.assertEqual({"a": 1, "b": 1}, flow.state)


if __name__ == "__main__":
    unittest.main()
