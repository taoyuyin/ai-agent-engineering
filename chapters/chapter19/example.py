"""Chapter 19: Reflection

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
    for step in ['Reflection', 'Retry', 'Repair', 'Failure Recovery']:
        state.events.append(f"handle: {step}")
    return state


if __name__ == "__main__":
    result = run("demo goal for Reflection")
    print(result)
