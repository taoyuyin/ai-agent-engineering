"""Chapter 13: Goal

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
    for step in ['目标理解', '目标转换', 'Goal Planning', '约束']:
        state.events.append(f"handle: {step}")
    return state


if __name__ == "__main__":
    result = run("demo goal for Goal")
    print(result)
