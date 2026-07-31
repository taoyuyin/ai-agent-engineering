from pydantic import BaseModel

from framework import AgentRequest, AgentRuntime, ExecutionPlan, Goal, PlanStep, ToolCall
from framework.contracts import Evidence
from framework.planner import DeterministicGoalCompiler
from framework.tools import ToolDefinition, ToolRegistry


class EchoInput(BaseModel):
    text: str


class EchoPlanner:
    def create_plan(self, request: AgentRequest, goal: Goal) -> ExecutionPlan:
        return ExecutionPlan(
            steps=(
                PlanStep(
                    step_id="echo",
                    title="Echo objective",
                    call=ToolCall(name="echo", arguments={"text": goal.objective}),
                    required_scopes=frozenset({"echo:read"}),
                ),
            )
        )


class EchoAnswer:
    def synthesize(self, request, goal, observations):
        value = observations[0].data["text"]
        return value, (Evidence(source="echo", value=value),)


def test_runtime_executes_authorized_plan() -> None:
    tools = ToolRegistry()
    tools.register(
        ToolDefinition(
            name="echo",
            description="Echo validated text.",
            input_model=EchoInput,
            handler=lambda value: {"text": value.text},
            required_scopes=frozenset({"echo:read"}),
        )
    )
    runtime = AgentRuntime(
        goal_compiler=DeterministicGoalCompiler(),
        planner=EchoPlanner(),
        answer_synthesizer=EchoAnswer(),
        tools=tools,
    )

    response = runtime.run(
        AgentRequest(
            tenant_id="tenant-a",
            actor_id="engineer",
            objective="hello runtime",
            scopes=frozenset({"echo:read"}),
        )
    )

    assert response.answer == "hello runtime"
    assert response.evidence[0].source == "echo"
    assert [event.event_type for event in runtime.trace.list_run(response.run_id)][-1] == (
        "run.completed"
    )
