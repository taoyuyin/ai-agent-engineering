from dataclasses import dataclass
from typing import Dict, Tuple


@dataclass(frozen=True)
class GoalSpec:
    objective: str
    constraints: Tuple[str, ...]
    success_criteria: Tuple[str, ...]
    allowed_tools: Tuple[str, ...]
    risk_level: str


class GoalCompiler:
    def compile(self, payload: Dict[str, object]) -> GoalSpec:
        objective = str(payload.get("objective", "")).strip()
        criteria = tuple(payload.get("success_criteria", ()))
        risk = str(payload.get("risk_level", "medium"))
        if not objective:
            raise ValueError("objective is required")
        if not criteria:
            raise ValueError("at least one success criterion is required")
        if risk not in {"low", "medium", "high"}:
            raise ValueError("unsupported risk level")
        return GoalSpec(
            objective,
            tuple(payload.get("constraints", ())),
            criteria,
            tuple(payload.get("allowed_tools", ())),
            risk,
        )


class GoalEvaluator:
    def evaluate(self, goal: GoalSpec, evidence: Dict[str, bool]) -> Dict[str, object]:
        missing = [criterion for criterion in goal.success_criteria if not evidence.get(criterion)]
        return {"complete": not missing, "missing": missing}
