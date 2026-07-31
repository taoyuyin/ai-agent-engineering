"""SQL Agent application composition root."""

from __future__ import annotations

from pathlib import Path

from framework import AgentRequest, AgentResponse, AgentRuntime
from framework.config import RuntimeSettings
from framework.planner import DeterministicGoalCompiler
from sql_agent.answer import SQLAnswerSynthesizer
from sql_agent.database import SalesDatabase
from sql_agent.planner import SQLPlanner
from sql_agent.tools import SQLAgentTools


class SQLAgentApplication:
    def __init__(self, runtime: AgentRuntime, settings: RuntimeSettings) -> None:
        self.runtime = runtime
        self.settings = settings

    def ask(
        self,
        objective: str,
        *,
        tenant_id: str = "demo",
        actor_id: str = "local-engineer",
    ) -> AgentResponse:
        return self.runtime.run(
            AgentRequest(
                tenant_id=tenant_id,
                actor_id=actor_id,
                objective=objective,
                scopes=frozenset({"schema:read", "sales:read"}),
                max_steps=self.settings.default_max_steps,
                max_retries=self.settings.default_max_retries,
            )
        )


def build_application(settings: RuntimeSettings | None = None) -> SQLAgentApplication:
    settings = settings or RuntimeSettings.from_env()
    data_directory = Path(__file__).resolve().parent.parent / "data"
    database = SalesDatabase(settings.database_path, data_directory)
    database.initialize()
    tools = SQLAgentTools(database)
    runtime = AgentRuntime(
        goal_compiler=DeterministicGoalCompiler(),
        planner=SQLPlanner(),
        answer_synthesizer=SQLAnswerSynthesizer(),
        tools=tools.registry(),
    )
    return SQLAgentApplication(runtime, settings)
