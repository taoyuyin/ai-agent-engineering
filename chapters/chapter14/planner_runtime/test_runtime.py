import unittest

from planner_runtime import Plan, PlanStep


class PlanTest(unittest.TestCase):
    def test_dependency_order(self) -> None:
        plan = Plan([PlanStep("a", "A"), PlanStep("b", "B", ("a",))])
        self.assertEqual(["a"], [step.step_id for step in plan.ready_steps()])
        plan.mark_completed("a", {})
        self.assertEqual(["b"], [step.step_id for step in plan.ready_steps()])

    def test_rejects_cycle(self) -> None:
        with self.assertRaises(ValueError):
            Plan([PlanStep("a", "A", ("b",)), PlanStep("b", "B", ("a",))])


if __name__ == "__main__":
    unittest.main()
