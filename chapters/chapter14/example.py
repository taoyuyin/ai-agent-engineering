"""Chapter 14: Planner

Minimal runtime-oriented sketch.
"""

from dataclasses import dataclass, field
from typing import List


@dataclass
class AgentState:
    goal: str
    events: List[str] = field(default_factory=list)


def run(goal: str) -> AgentState:
    state = AgentState(goal=goal)
    for step in ['任务拆解', 'Planning Algorithm', 'Plan Update', 'Plan Execution']:
        state.events.append(f"handle: {step}")
    return state


if __name__ == "__main__":
    result = run("demo goal for Planner")
    print(result)
