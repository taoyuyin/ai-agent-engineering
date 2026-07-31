import unittest

from goal_runtime import GoalCompiler, GoalEvaluator


class GoalTest(unittest.TestCase):
    def test_requires_testable_success_criteria(self) -> None:
        with self.assertRaises(ValueError):
            GoalCompiler().compile({"objective": "help me"})

    def test_evaluates_evidence(self) -> None:
        goal = GoalCompiler().compile({"objective": "report", "success_criteria": ["has_total"]})
        self.assertTrue(GoalEvaluator().evaluate(goal, {"has_total": True})["complete"])


if __name__ == "__main__":
    unittest.main()
