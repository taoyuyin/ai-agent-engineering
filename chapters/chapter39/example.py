"""PydanticAI: type-safe dependencies, tools and structured sales output."""

from __future__ import annotations

from dataclasses import dataclass
from os import environ
from sys import argv

from pydantic import BaseModel
from pydantic_ai import Agent, RunContext


class RegionResult(BaseModel):
    region: str
    net_revenue: float
    order_count: int


class SalesReport(BaseModel):
    year: int
    summary: str
    results: list[RegionResult]
    evidence_source: str


@dataclass
class SalesRepository:
    tenant_id: str
    scopes: frozenset[str]

    def query(self, year: int, region: str | None) -> list[dict]:
        if "sales:read" not in self.scopes:
            raise PermissionError("sales:read scope is required")
        rows = {
            "east": {"net_revenue": 338_000.0, "order_count": 2},
            "north": {"net_revenue": 149_000.0, "order_count": 2},
            "south": {"net_revenue": 148_000.0, "order_count": 2},
        }
        if region:
            rows = {region: rows[region]} if region in rows else {}
        return [{"region": name, **value} for name, value in rows.items()]


agent = Agent(
    environ.get("PYDANTIC_AI_MODEL", "openai:gpt-5-mini"),
    deps_type=SalesRepository,
    output_type=SalesReport,
    retries={"tools": 1, "output": 2},
    system_prompt=(
        "You are a governed sales analyst. Always call query_sales. "
        "Never invent values and always retain the evidence source."
    ),
)


@agent.tool
def query_sales(
    context: RunContext[SalesRepository],
    year: int,
    region: str | None = None,
) -> dict:
    """Return authorized sales facts for a year and optional region."""
    return {
        "year": year,
        "metric": "net_revenue",
        "rows": context.deps.query(year, region),
        "source": "demo.sales_orders",
        "tenant_id": context.deps.tenant_id,
    }


def main() -> None:
    question = " ".join(argv[1:]) or "查询 2025 年各区域净销售额"
    result = agent.run_sync(
        question,
        deps=SalesRepository(
            tenant_id="demo",
            scopes=frozenset({"sales:read"}),
        ),
    )
    print(result.output.model_dump_json(indent=2))


if __name__ == "__main__":
    main()
