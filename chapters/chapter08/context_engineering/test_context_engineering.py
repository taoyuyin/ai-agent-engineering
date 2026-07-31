import unittest

from context_engineering import ContextAssembler, ContextBudget, ContextItem


class ContextAssemblerTest(unittest.TestCase):
    def test_required_first_and_budget_never_exceeded(self) -> None:
        budget = ContextBudget(40, reserved_output=10)
        result = ContextAssembler(budget).assemble(
            [
                ContextItem("optional", "history", "x" * 160, 1),
                ContextItem("goal", "goal", "must keep", 100, required=True),
            ]
        )
        self.assertEqual(["goal"], [item.item_id for item in result.selected])
        self.assertLessEqual(result.used_tokens, budget.available_input)

    def test_deduplicates_content(self) -> None:
        budget = ContextBudget(100, reserved_output=10)
        result = ContextAssembler(budget).assemble(
            [
                ContextItem("low", "memory", "same fact", 1),
                ContextItem("high", "policy", "same  fact", 9),
            ]
        )
        self.assertEqual(["high"], [item.item_id for item in result.selected])


if __name__ == "__main__":
    unittest.main()
