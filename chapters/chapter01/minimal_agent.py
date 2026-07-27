"""A tiny rule-based agent loop for Chapter 01.

This example intentionally avoids model calls so the core Agent loop is visible:
observe -> decide -> act -> stop.
"""

from dataclasses import dataclass, field
from typing import List


@dataclass
class AgentState:
    goal: str
    steps: List[str] = field(default_factory=list)
    done: bool = False


class MinimalAgent:
    def run(self, goal: str) -> AgentState:
        state = AgentState(goal=goal)

        while not state.done:
            observation = self.observe(state)
            action = self.decide(observation)
            self.act(action, state)

        return state

    def observe(self, state: AgentState) -> str:
        if not state.steps:
            return f"Need to start: {state.goal}"
        return f"Progress so far: {len(state.steps)} step(s)"

    def decide(self, observation: str) -> str:
        if observation.startswith("Need to start"):
            return "write_plan"
        return "finish"

    def act(self, action: str, state: AgentState) -> None:
        if action == "write_plan":
            state.steps.append(f"Create a simple plan for: {state.goal}")
        elif action == "finish":
            state.done = True
        else:
            raise ValueError(f"Unknown action: {action}")


if __name__ == "__main__":
    agent = MinimalAgent()
    result = agent.run("Explain what an AI Agent is")

    print("Goal:", result.goal)
    print("Steps:")
    for index, step in enumerate(result.steps, start=1):
        print(f"{index}. {step}")
