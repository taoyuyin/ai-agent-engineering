"""Chapter 32: route work to the cheapest capable model under budget."""

from cost_runtime import BudgetLedger, ModelProfile, ModelRouter, RouteRequest


def main() -> None:
    models = [
        ModelProfile("small", frozenset({"extract", "classify"}), 1, 0.20, 0.80),
        ModelProfile("reasoning", frozenset({"extract", "classify", "reason"}), 3, 2.00, 8.00),
    ]
    ledger = BudgetLedger(limit_usd=1.0)
    router = ModelRouter(models, ledger)
    decision = router.route(RouteRequest("classify", quality_tier=1, input_tokens=800, output_tokens=80))
    ledger.record(decision.estimated_cost_usd)
    print(decision)
    print(ledger)


if __name__ == "__main__":
    main()
