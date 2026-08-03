"""Chapter 54: an evidence gate for agent-generated software changes."""

from dataclasses import asdict, dataclass
from enum import Enum
import json


class GateStatus(str, Enum):
    PASS = "pass"
    FAIL = "fail"
    REVIEW = "review"


@dataclass(frozen=True)
class ChangeProposal:
    change_id: str
    goal: str
    agent: str
    model: str
    files_changed: tuple[str, ...]
    risk: str
    assumptions: tuple[str, ...]


@dataclass(frozen=True)
class Evidence:
    tests_passed: bool
    type_check_passed: bool
    security_findings: int
    requirements_covered: float
    reviewer_approved: bool
    trace_id: str


@dataclass(frozen=True)
class GateDecision:
    status: GateStatus
    reasons: tuple[str, ...]
    trust_score: int


def verify(proposal: ChangeProposal, evidence: Evidence) -> GateDecision:
    failures = []
    score = 0
    if evidence.tests_passed:
        score += 25
    else:
        failures.append("tests failed")
    if evidence.type_check_passed:
        score += 15
    else:
        failures.append("type check failed")
    if evidence.security_findings == 0:
        score += 20
    else:
        failures.append(f"{evidence.security_findings} security finding(s)")
    score += round(evidence.requirements_covered * 25)
    if evidence.requirements_covered < 0.9:
        failures.append("requirements coverage is below 90%")
    if evidence.reviewer_approved:
        score += 15

    if failures:
        status = GateStatus.FAIL
        reasons = tuple(failures)
    elif proposal.risk in {"high", "critical"} and not evidence.reviewer_approved:
        status = GateStatus.REVIEW
        reasons = ("high-risk change requires human approval",)
    else:
        status = GateStatus.PASS
        reasons = ("all required evidence is present",)
    return GateDecision(status, reasons, score)


def main() -> None:
    proposal = ChangeProposal(
        change_id="chg-54-001",
        goal="为订单 API 增加租户级幂等键",
        agent="coding-agent/2.1",
        model="model-route:reasoning",
        files_changed=("orders/api.py", "orders/idempotency.py", "tests/test_orders.py"),
        risk="high",
        assumptions=("Redis is the idempotency store", "keys expire after 24 hours"),
    )
    evidence = Evidence(
        tests_passed=True,
        type_check_passed=True,
        security_findings=0,
        requirements_covered=1.0,
        reviewer_approved=True,
        trace_id="trace-54-9f2a",
    )
    decision = verify(proposal, evidence)
    print(json.dumps({
        "workflow": ["executable_spec", "agent_candidate", "automated_evidence", "human_review", "release_gate"],
        "proposal": asdict(proposal),
        "evidence": asdict(evidence),
        "decision": asdict(decision),
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
