from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Set


class RunStatus(Enum):
    CREATED = "created"
    VALIDATING = "validating"
    PLANNING = "planning"
    RUNNING = "running"
    WAITING = "waiting"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


TERMINAL = {RunStatus.COMPLETED, RunStatus.FAILED, RunStatus.CANCELLED}


@dataclass
class AgentRun:
    run_id: str
    goal: str
    max_steps: int = 8
    max_tokens: int = 4000
    status: RunStatus = RunStatus.CREATED
    steps: int = 0
    tokens_used: int = 0
    events: List[Dict[str, str]] = field(default_factory=list)


class LifecycleEngine:
    allowed = {
        RunStatus.CREATED: {RunStatus.VALIDATING, RunStatus.CANCELLED},
        RunStatus.VALIDATING: {RunStatus.PLANNING, RunStatus.FAILED, RunStatus.CANCELLED},
        RunStatus.PLANNING: {RunStatus.RUNNING, RunStatus.FAILED, RunStatus.CANCELLED},
        RunStatus.RUNNING: {
            RunStatus.RUNNING,
            RunStatus.WAITING,
            RunStatus.COMPLETED,
            RunStatus.FAILED,
            RunStatus.CANCELLED,
        },
        RunStatus.WAITING: {RunStatus.RUNNING, RunStatus.CANCELLED, RunStatus.FAILED},
    }  # type: Dict[RunStatus, Set[RunStatus]]

    def transition(self, run: AgentRun, target: RunStatus, reason: str) -> None:
        if run.status in TERMINAL:
            raise ValueError("terminal run cannot transition")
        if target not in self.allowed.get(run.status, set()):
            raise ValueError("illegal transition: {} -> {}".format(run.status.value, target.value))
        if target == RunStatus.RUNNING:
            run.steps += 1
            if run.steps > run.max_steps:
                target = RunStatus.FAILED
                reason = "step_budget_exhausted"
        previous = run.status
        run.status = target
        run.events.append({"from": previous.value, "to": target.value, "reason": reason})

    def record_model_usage(self, run: AgentRun, input_tokens: int, output_tokens: int) -> None:
        if input_tokens < 0 or output_tokens < 0:
            raise ValueError("token usage cannot be negative")
        run.tokens_used += input_tokens + output_tokens
        run.events.append(
            {
                "from": run.status.value,
                "to": run.status.value,
                "reason": "model_usage:{}+{}".format(input_tokens, output_tokens),
            }
        )
        if run.tokens_used > run.max_tokens and run.status not in TERMINAL:
            previous = run.status
            run.status = RunStatus.FAILED
            run.events.append(
                {
                    "from": previous.value,
                    "to": RunStatus.FAILED.value,
                    "reason": "token_budget_exhausted",
                }
            )
