"""Deterministic offline evaluation and release gating for Agent results."""

from dataclasses import dataclass
from typing import Dict, Iterable, Mapping, Tuple


@dataclass(frozen=True)
class EvalCase:
    case_id: str
    required_terms: Tuple[str, ...]
    expected_tools: Tuple[str, ...]
    require_citations: bool
    max_latency_ms: float
    max_cost_usd: float


@dataclass(frozen=True)
class AgentResult:
    answer: str
    tools: Tuple[str, ...]
    citations: Tuple[str, ...]
    latency_ms: float
    cost_usd: float


@dataclass(frozen=True)
class CaseScore:
    case_id: str
    passed: bool
    checks: Mapping[str, bool]


@dataclass(frozen=True)
class EvaluationReport:
    pass_rate: float
    released: bool
    scores: Tuple[CaseScore, ...]


class EvaluationSuite:
    def __init__(self, min_pass_rate: float = 0.9) -> None:
        if not 0 <= min_pass_rate <= 1:
            raise ValueError("min_pass_rate must be between 0 and 1")
        self.min_pass_rate = min_pass_rate

    def score(self, case: EvalCase, result: AgentResult) -> CaseScore:
        checks: Dict[str, bool] = {
            "content": all(term in result.answer for term in case.required_terms),
            "tools": tuple(result.tools) == tuple(case.expected_tools),
            "citations": bool(result.citations) if case.require_citations else True,
            "latency": result.latency_ms <= case.max_latency_ms,
            "cost": result.cost_usd <= case.max_cost_usd,
        }
        return CaseScore(case.case_id, all(checks.values()), checks)

    def run(
        self,
        cases: Iterable[EvalCase],
        results: Mapping[str, AgentResult],
    ) -> EvaluationReport:
        scores = []
        for case in cases:
            if case.case_id not in results:
                scores.append(
                    CaseScore(case.case_id, False, {"result_present": False})
                )
            else:
                scores.append(self.score(case, results[case.case_id]))
        rate = sum(score.passed for score in scores) / max(1, len(scores))
        return EvaluationReport(rate, rate >= self.min_pass_rate, tuple(scores))
