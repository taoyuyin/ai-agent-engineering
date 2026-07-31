"""ADK project contract: exports root_agent."""

from __future__ import annotations

from os import environ

from google.adk.agents.llm_agent import Agent


SALES = {
    "east": {"net_revenue": 338_000.0, "order_count": 2},
    "north": {"net_revenue": 149_000.0, "order_count": 2},
    "south": {"net_revenue": 148_000.0, "order_count": 2},
}


def query_sales(year: int, region: str | None = None) -> dict:
    """Return governed sales data for a year and optional region."""
    scopes = set(environ.get("AGENT_SCOPES", "").split(","))
    if "sales:read" not in scopes:
        return {"status": "forbidden", "error": "sales:read scope is required"}
    rows = SALES
    if region:
        rows = {region: SALES[region]} if region in SALES else {}
    return {
        "status": "success",
        "year": year,
        "metric": "net_revenue",
        "rows": [{"region": name, **value} for name, value in rows.items()],
        "source": "demo.sales_orders",
    }


root_agent = Agent(
    model=environ.get("GOOGLE_ADK_MODEL", "gemini-flash-latest"),
    name="governed_sales_agent",
    description="Queries governed sales metrics and returns evidence.",
    instruction=(
        "You are a governed enterprise sales analyst. Always call query_sales. "
        "Never invent values. Include the source and metric in the final answer."
    ),
    tools=[query_sales],
)
