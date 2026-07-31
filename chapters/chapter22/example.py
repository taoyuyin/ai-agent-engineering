"""Chapter 22: Multi-Agent

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
    for step in ['Agent Communication', 'Task Delegation', '角色分工', '冲突']:
        state.events.append(f"handle: {step}")
    return state


if __name__ == "__main__":
    result = run("demo goal for Multi-Agent")
    print(result)
