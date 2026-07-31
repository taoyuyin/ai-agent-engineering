"""CrewAI: a two-role governed sales analysis crew."""

from __future__ import annotations

from os import environ
from sys import argv

from crewai import Agent, Crew, Process, Task
from crewai.tools import tool
from pydantic import BaseModel


SALES = {
    "east": {"net_revenue": 338_000.0, "order_count": 2},
    "north": {"net_revenue": 149_000.0, "order_count": 2},
    "south": {"net_revenue": 148_000.0, "order_count": 2},
}


class SalesReport(BaseModel):
    year: int
    summary: str
    evidence_source: str


@tool("query_governed_sales")
def query_governed_sales(year: int) -> dict:
    """Return authorized net revenue and order counts by region."""
    scopes = set(environ.get("AGENT_SCOPES", "").split(","))
    if "sales:read" not in scopes:
        raise PermissionError("sales:read scope is required")
    return {
        "year": year,
        "metric": "net_revenue",
        "rows": [{"region": name, **value} for name, value in SALES.items()],
        "source": "demo.sales_orders",
    }


def main() -> None:
    question = " ".join(argv[1:]) or "查询 2025 年各区域净销售额"
    model = environ.get("CREWAI_MODEL", "openai/gpt-5-mini")

    data_agent = Agent(
        role="Governed Data Analyst",
        goal="Retrieve authorized sales facts with evidence.",
        backstory="You operate under enterprise data access policy.",
        tools=[query_governed_sales],
        llm=model,
        allow_delegation=False,
        max_iter=4,
        verbose=True,
    )
    reporting_agent = Agent(
        role="Sales Reporting Engineer",
        goal="Turn verified sales facts into a concise structured report.",
        backstory="You never invent metrics and always retain evidence.",
        llm=model,
        allow_delegation=False,
        max_iter=3,
        verbose=True,
    )
    retrieve = Task(
        description=f"Answer this request using query_governed_sales: {question}",
        expected_output="Authorized rows, year, metric and evidence source.",
        agent=data_agent,
    )
    report = Task(
        description="Summarize the verified task output. Preserve year and evidence source.",
        expected_output="A SalesReport object.",
        agent=reporting_agent,
        context=[retrieve],
        output_pydantic=SalesReport,
    )
    result = Crew(
        agents=[data_agent, reporting_agent],
        tasks=[retrieve, report],
        process=Process.sequential,
        verbose=True,
    ).kickoff()
    print(result.pydantic or result.raw)


if __name__ == "__main__":
    main()
