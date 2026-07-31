import unittest

from cost_runtime import BudgetLedger, ModelProfile, ModelRouter, RouteRequest


SMALL = ModelProfile("small", frozenset({"classify"}), 1, 1.0, 2.0)
LARGE = ModelProfile("large", frozenset({"classify", "reason"}), 3, 5.0, 10.0)


class ModelRouterTest(unittest.TestCase):
    def test_selects_cheapest_capable_model(self):
        router = ModelRouter([LARGE, SMALL], BudgetLedger(1.0))
        decision = router.route(RouteRequest("classify", 1, 1000, 100))
        self.assertEqual("small", decision.model)

    def test_quality_constraint_selects_stronger_model(self):
        router = ModelRouter([SMALL, LARGE], BudgetLedger(1.0))
        decision = router.route(RouteRequest("reason", 3, 1000, 100))
        self.assertEqual("large", decision.model)

    def test_cached_tokens_reduce_estimate_and_budget_is_enforced(self):
        self.assertLess(LARGE.estimate(1000, 100, 900), LARGE.estimate(1000, 100))
        router = ModelRouter([LARGE], BudgetLedger(0.000001))
        with self.assertRaises(RuntimeError):
            router.route(RouteRequest("reason", 3, 1000, 100))


if __name__ == "__main__":
    unittest.main()
