"""Planner extension points and deterministic default goal compilation."""

from __future__ import annotations

from typing import Protocol, Sequence

from framework.contracts import AgentRequest, Evidence, ExecutionPlan, Goal, ToolObservation


class GoalCompiler(Protocol):
    def compile(self, request: AgentRequest) -> Goal: ...


class Planner(Protocol):
    def create_plan(self, request: AgentRequest, goal: Goal) -> ExecutionPlan: ...


class AnswerSynthesizer(Protocol):
    def synthesize(
        self,
        request: AgentRequest,
        goal: Goal,
        observations: Sequence[ToolObservation],
    ) -> tuple[str, tuple[Evidence, ...]]: ...


class DeterministicGoalCompiler:
    """Turns user text into a bounded runtime goal before model/tool execution."""

    def compile(self, request: AgentRequest) -> Goal:
        return Goal(
            objective=request.objective.strip(),
            success_criteria=(
                "answer is grounded in successful tool observations",
                "every tool call is authorized by tenant and scope",
                "the run stays within the configured step and retry budgets",
            ),
            constraints={
                "tenant_id": request.tenant_id,
                "max_steps": request.max_steps,
                "context_token_budget": request.context_token_budget,
            },
        )
