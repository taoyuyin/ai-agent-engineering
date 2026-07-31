"""Composition root for the deterministic control plane of an Agent run."""

from __future__ import annotations

from datetime import datetime, timezone

from framework.contracts import (
    AgentRequest,
    AgentResponse,
    PlanStep,
    RunStatus,
    StepStatus,
    ToolObservation,
)
from framework.executor import ToolExecutor
from framework.memory import InMemoryStore, MemoryRecord
from framework.observability import InMemoryTraceSink
from framework.planner import AnswerSynthesizer, GoalCompiler, Planner
from framework.policy import PolicyEngine
from framework.tools import ToolRegistry
from framework.workflow import RunStateMachine


class AgentRuntime:
    """Runs a validated plan while keeping policy and state outside the model."""

    def __init__(
        self,
        *,
        goal_compiler: GoalCompiler,
        planner: Planner,
        answer_synthesizer: AnswerSynthesizer,
        tools: ToolRegistry,
        policy: PolicyEngine | None = None,
        executor: ToolExecutor | None = None,
        memory: InMemoryStore | None = None,
        trace: InMemoryTraceSink | None = None,
    ) -> None:
        self.goal_compiler = goal_compiler
        self.planner = planner
        self.answer_synthesizer = answer_synthesizer
        self.tools = tools
        self.policy = policy or PolicyEngine()
        self.executor = executor or ToolExecutor()
        self.memory = memory or InMemoryStore()
        self.trace = trace or InMemoryTraceSink()

    def run(self, request: AgentRequest) -> AgentResponse:
        started_at = datetime.now(timezone.utc)
        state = RunStateMachine()
        observations: list[ToolObservation] = []
        self.trace.emit(
            request.run_id,
            "run.accepted",
            tenant_id=request.tenant_id,
            actor_id=request.actor_id,
        )

        try:
            state.transition(RunStatus.RUNNING)
            goal = self.goal_compiler.compile(request)
            self.trace.emit(
                request.run_id,
                "goal.compiled",
                objective=goal.objective,
                success_criteria=list(goal.success_criteria),
            )

            plan = self.planner.create_plan(request, goal)
            self._validate_plan(plan.steps, request.max_steps)
            self.trace.emit(
                request.run_id,
                "plan.created",
                plan_id=plan.plan_id,
                steps=[step.step_id for step in plan.steps],
            )

            completed_steps: set[str] = set()
            for step in plan.steps:
                if not set(step.depends_on).issubset(completed_steps):
                    raise RuntimeError(f"dependencies not completed for step: {step.step_id}")

                tool = self.tools.resolve(step.call.name)
                self.policy.authorize(request, step, tool)
                self.trace.emit(
                    request.run_id,
                    "tool.started",
                    step_id=step.step_id,
                    tool_name=tool.name,
                )

                observation = self.executor.execute(step, tool, request.max_retries)
                observations.append(observation)
                self.memory.append(
                    MemoryRecord(
                        tenant_id=request.tenant_id,
                        run_id=request.run_id,
                        kind="observation",
                        content=observation.model_dump_json(),
                        metadata={"step_id": step.step_id, "tool_name": tool.name},
                    )
                )
                self.trace.emit(
                    request.run_id,
                    "tool.completed",
                    step_id=step.step_id,
                    tool_name=tool.name,
                    status=observation.status.value,
                    attempt=observation.attempt,
                    duration_ms=observation.duration_ms,
                )
                if observation.status != StepStatus.COMPLETED:
                    raise RuntimeError(observation.error or f"step failed: {step.step_id}")
                completed_steps.add(step.step_id)

            answer, evidence = self.answer_synthesizer.synthesize(
                request,
                goal,
                observations,
            )
            state.transition(RunStatus.COMPLETED)
            self.trace.emit(
                request.run_id,
                "run.completed",
                observation_count=len(observations),
                evidence_count=len(evidence),
            )
            return AgentResponse(
                run_id=request.run_id,
                status=state.status,
                answer=answer,
                observations=tuple(observations),
                evidence=evidence,
                started_at=started_at,
            )
        except Exception as error:
            if state.status in (RunStatus.ACCEPTED, RunStatus.RUNNING):
                state.transition(RunStatus.FAILED)
            self.trace.emit(
                request.run_id,
                "run.failed",
                error_type=type(error).__name__,
                error=str(error),
            )
            raise

    @staticmethod
    def _validate_plan(steps: tuple[PlanStep, ...], max_steps: int) -> None:
        if not steps:
            raise ValueError("plan must contain at least one step")
        if len(steps) > max_steps:
            raise ValueError(f"plan has {len(steps)} steps; budget is {max_steps}")

        seen: set[str] = set()
        for step in steps:
            if step.step_id in seen:
                raise ValueError(f"duplicate step id: {step.step_id}")
            unknown_dependencies = set(step.depends_on) - seen
            if unknown_dependencies:
                raise ValueError(
                    "step {} has forward or unknown dependencies: {}".format(
                        step.step_id,
                        ", ".join(sorted(unknown_dependencies)),
                    )
                )
            seen.add(step.step_id)
