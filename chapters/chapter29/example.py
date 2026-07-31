"""Chapter 29: run an offline release gate for an Agent."""

from evaluation_runtime import AgentResult, EvalCase, EvaluationSuite


def main() -> None:
    suite = EvaluationSuite(min_pass_rate=0.8)
    report = suite.run(
        [
            EvalCase(
                case_id="refund-policy",
                required_terms=("七日",),
                expected_tools=("policy.search",),
                require_citations=True,
                max_latency_ms=1200,
                max_cost_usd=0.02,
            )
        ],
        {
            "refund-policy": AgentResult(
                answer="退款须在七日内申请 [policy-7]",
                tools=("policy.search",),
                citations=("policy-7",),
                latency_ms=320,
                cost_usd=0.004,
            )
        },
    )
    print(report)


if __name__ == "__main__":
    main()
