"""LlamaIndex: FunctionAgent over a governed analytical data tool."""

from __future__ import annotations

import asyncio
from json import dumps
from os import environ
from sys import argv

from llama_index.core.agent.workflow import FunctionAgent
from llama_index.llms.openai import OpenAI


SALES = {
    "east": {"net_revenue": 338_000.0, "order_count": 2},
    "north": {"net_revenue": 149_000.0, "order_count": 2},
    "south": {"net_revenue": 148_000.0, "order_count": 2},
}


def query_sales(year: int, region: str | None = None) -> str:
    """Return authorized net revenue and order counts with evidence."""
    scopes = set(environ.get("AGENT_SCOPES", "").split(","))
    if "sales:read" not in scopes:
        raise PermissionError("sales:read scope is required")
    rows = SALES
    if region:
        rows = {region: SALES[region]} if region in SALES else {}
    return dumps(
        {
            "year": year,
            "metric": "net_revenue",
            "rows": [{"region": name, **value} for name, value in rows.items()],
            "source": "demo.sales_orders",
        },
        ensure_ascii=False,
    )


async def run() -> None:
    question = " ".join(argv[1:]) or "查询 2025 年各区域净销售额"
    llm = OpenAI(model=environ.get("LLAMAINDEX_MODEL", "gpt-5-mini"))
    agent = FunctionAgent(
        tools=[query_sales],
        llm=llm,
        system_prompt=(
            "You are a governed sales analyst. Always call query_sales. "
            "Do not invent values. Include metric and source in the answer."
        ),
    )
    response = await agent.run(user_msg=question)
    print(str(response))


if __name__ == "__main__":
    asyncio.run(run())
