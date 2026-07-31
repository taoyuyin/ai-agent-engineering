from dataclasses import dataclass
from typing import Dict


@dataclass(frozen=True)
class Failure:
    code: str
    detail: str


@dataclass(frozen=True)
class RepairDecision:
    action: str
    reason: str


class RepairController:
    transient = {"TIMEOUT", "RATE_LIMIT", "UNAVAILABLE"}

    def __init__(self, max_retries: int = 2) -> None:
        self.max_retries = max_retries
        self.attempts = {}  # type: Dict[str, int]

    def decide(self, step_id: str, failure: Failure) -> RepairDecision:
        if failure.code == "PERMISSION_DENIED":
            return RepairDecision("abort", "authorization cannot be repaired by retry")
        if failure.code == "INVALID_SCHEMA":
            return RepairDecision("repair_arguments", "tool input must be regenerated")
        if failure.code == "QUALITY_FAILED":
            return RepairDecision("replan", "evidence does not satisfy success criteria")
        if failure.code in self.transient:
            attempts = self.attempts.get(step_id, 0)
            if attempts < self.max_retries:
                self.attempts[step_id] = attempts + 1
                return RepairDecision("retry", "transient failure")
            return RepairDecision("escalate", "retry budget exhausted")
        return RepairDecision("escalate", "unknown failure")
