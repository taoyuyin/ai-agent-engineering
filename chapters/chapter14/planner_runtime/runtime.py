from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Tuple


class StepStatus(Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class PlanStep:
    step_id: str
    description: str
    depends_on: Tuple[str, ...] = ()
    status: StepStatus = StepStatus.PENDING
    result: Dict[str, object] = field(default_factory=dict)


class Plan:
    def __init__(self, steps: List[PlanStep]) -> None:
        self.steps = {step.step_id: step for step in steps}
        if len(self.steps) != len(steps):
            raise ValueError("duplicate step id")
        self._validate_dependencies()

    def ready_steps(self) -> List[PlanStep]:
        completed = {key for key, value in self.steps.items() if value.status == StepStatus.COMPLETED}
        return [
            step
            for step in self.steps.values()
            if step.status == StepStatus.PENDING and set(step.depends_on) <= completed
        ]

    def mark_completed(self, step_id: str, result: Dict[str, object]) -> None:
        step = self.steps[step_id]
        if step not in self.ready_steps():
            raise ValueError("step dependencies are not complete")
        step.status = StepStatus.COMPLETED
        step.result = result

    def mark_failed(self, step_id: str) -> None:
        self.steps[step_id].status = StepStatus.FAILED

    def repair(self, step_id: str, description: str) -> None:
        step = self.steps[step_id]
        if step.status != StepStatus.FAILED:
            raise ValueError("only failed steps can be repaired")
        step.description = description
        step.status = StepStatus.PENDING

    @property
    def complete(self) -> bool:
        return all(step.status == StepStatus.COMPLETED for step in self.steps.values())

    def _validate_dependencies(self) -> None:
        for step in self.steps.values():
            if not set(step.depends_on) <= set(self.steps):
                raise ValueError("unknown dependency")
        visiting = set()
        visited = set()

        def visit(step_id: str) -> None:
            if step_id in visiting:
                raise ValueError("cyclic plan")
            if step_id in visited:
                return
            visiting.add(step_id)
            for dependency in self.steps[step_id].depends_on:
                visit(dependency)
            visiting.remove(step_id)
            visited.add(step_id)

        for key in self.steps:
            visit(key)
