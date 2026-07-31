"""OpenAI Agents SDK: governed sales analysis agent."""

from __future__ import annotations

from dataclasses import dataclass
from json import dumps
from os import environ
from sys import argv

from agents import Agent, RunContextWrapper, Runner, function_tool
from pydantic import BaseModel, Field


SALES = {
    2025: {
        "east": {"net_revenue": 338_000.0, "order_count": 2},
        "north": {"net_revenue": 149_000.0, "order_count": 2},
        "south": {"net_revenue": 148_000.0, "order_count": 2},
    }
}


@dataclass(frozen=True)
class RequestContext:
    tenant_id: str
    actor_id: str
    scopes: frozenset[str]


class RegionResult(BaseModel):
    region: str
    net_revenue: float
    order_count: int


class SalesReport(BaseModel):
    year: int
    summary: str
    results: list[RegionResult]
    evidence_sources: list[str] = Field(min_length=1)


@function_tool
def query_sales(
    context: RunContextWrapper[RequestContext],
    year: int,
    region: str | None = None,
) -> str:
    """Return governed net revenue and order counts for a year and optional region."""
    if "sales:read" not in context.context.scopes:
        raise PermissionError("sales:read scope is required")

    rows = SALES.get(year, {})
    if region:
        rows = {region: rows[region]} if region in rows else {}
    payload = [
        {"region": name, **metrics}
        for name, metrics in sorted(
            rows.items(),
            key=lambda item: item[1]["net_revenue"],
            reverse=True,
        )
    ]
    return dumps(
        {
            "tenant_id": context.context.tenant_id,
            "metric": "net_revenue",
            "year": year,
            "rows": payload,
            "source": "demo.sales_orders",
        },
        ensure_ascii=False,
    )


def main() -> None:
    question = " ".join(argv[1:]) or "查询 2025 年各区域净销售额"
    model = environ.get("OPENAI_MODEL", "gpt-5-mini")
    agent = Agent[RequestContext](
        name="Governed Sales Analyst",
        model=model,
        instructions=(
            "你是企业销售分析 Agent。必须调用 query_sales 获取事实；"
            "不得猜测数据；最终输出必须包含 evidence_sources。"
        ),
        tools=[query_sales],
        output_type=SalesReport,
    )
    result = Runner.run_sync(
        agent,
        question,
        context=RequestContext(
            tenant_id="demo",
            actor_id="engineer-001",
            scopes=frozenset({"sales:read"}),
        ),
        max_turns=6,
    )
    print(result.final_output.model_dump_json(indent=2))


if __name__ == "__main__":
    main()
