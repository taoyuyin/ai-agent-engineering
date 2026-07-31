from dataclasses import dataclass
from typing import Any, Dict, List

from .tools import ToolRegistry


@dataclass(frozen=True)
class TraceEvent:
    kind: str
    detail: str


@dataclass(frozen=True)
class RunResult:
    answer: str
    trace: List[TraceEvent]


class ReasoningController:
    """Deterministic teaching runtime: plan, act, observe, verify, repair."""

    def __init__(self, tools: ToolRegistry, max_steps: int = 4, max_repairs: int = 1) -> None:
        self.tools = tools
        self.max_steps = max_steps
        self.max_repairs = max_repairs

    def run(self, goal: str, segment: str) -> RunResult:
        trace = [TraceEvent("goal", goal)]
        observations = {}  # type: Dict[str, Dict[str, Any]]
        plan = ["get_churn_rate", "get_ticket_rate"]
        trace.append(TraceEvent("plan", " -> ".join(plan)))

        for step, tool_name in enumerate(plan, start=1):
            if step > self.max_steps:
                raise RuntimeError("step budget exhausted")
            trace.append(TraceEvent("action", "{}({})".format(tool_name, segment)))
            for attempt in range(self.max_repairs + 1):
                try:
                    observations[tool_name] = self.tools.call(tool_name, segment=segment)
                    break
                except (RuntimeError, TimeoutError) as error:
                    trace.append(
                        TraceEvent(
                            "repair",
                            "{} attempt={} error={}".format(
                                tool_name,
                                attempt + 1,
                                type(error).__name__,
                            ),
                        )
                    )
                    if attempt == self.max_repairs:
                        raise
            trace.append(TraceEvent("observation", repr(observations[tool_name])))

        missing = [name for name in plan if name not in observations]
        if missing:
            trace.append(TraceEvent("verification", "missing=" + ",".join(missing)))
            raise RuntimeError("evidence incomplete after repair budget")

        churn = observations["get_churn_rate"]["rate"]
        tickets = observations["get_ticket_rate"]["rate"]
        trace.append(TraceEvent("verification", "evidence_complete=true"))
        answer = (
            "{} 客户流失率为 {:.0%}，工单率为 {:.0%}；工单相关性是假设，"
            "需用客户级数据做进一步验证。"
        ).format(segment, churn, tickets)
        return RunResult(answer, trace)
