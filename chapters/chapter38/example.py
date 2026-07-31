"""AutoGen AgentChat: typed sales analyst with a governed function tool."""

from __future__ import annotations

import asyncio
from os import environ
from sys import argv

from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import StructuredMessage
from autogen_ext.models.openai import OpenAIChatCompletionClient
from pydantic import BaseModel


SALES = {
    "east": {"net_revenue": 338_000.0, "order_count": 2},
    "north": {"net_revenue": 149_000.0, "order_count": 2},
    "south": {"net_revenue": 148_000.0, "order_count": 2},
}


class RegionResult(BaseModel):
    region: str
    net_revenue: float
    order_count: int


class SalesReport(BaseModel):
    year: int
    summary: str
    results: list[RegionResult]
    evidence_source: str


async def query_sales(year: int, region: str | None = None) -> str:
    """Return governed net revenue and order count facts."""
    scopes = set(environ.get("AGENT_SCOPES", "").split(","))
    if "sales:read" not in scopes:
        raise PermissionError("sales:read scope is required")
    rows = SALES
    if region:
        rows = {region: SALES[region]} if region in SALES else {}
    return str(
        {
            "year": year,
            "metric": "net_revenue",
            "rows": [{"region": name, **value} for name, value in rows.items()],
            "source": "demo.sales_orders",
        }
    )


async def run() -> None:
    question = " ".join(argv[1:]) or "查询 2025 年各区域净销售额"
    model_client = OpenAIChatCompletionClient(
        model=environ.get("AUTOGEN_MODEL", "gpt-5-mini"),
        parallel_tool_calls=False,
    )
    agent = AssistantAgent(
        name="governed_sales_analyst",
        description="Retrieves governed sales facts and produces typed reports.",
        model_client=model_client,
        tools=[query_sales],
        system_message=(
            "Always use query_sales. Never invent values. "
            "Return a SalesReport with the evidence source."
        ),
        output_content_type=SalesReport,
        max_tool_iterations=4,
    )
    try:
        result = await agent.run(task=question)
        message = result.messages[-1]
        if not isinstance(message, StructuredMessage):
            raise TypeError("expected a StructuredMessage")
        print(message.content.model_dump_json(indent=2))
    finally:
        await model_client.close()


if __name__ == "__main__":
    asyncio.run(run())
