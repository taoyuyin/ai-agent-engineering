"""Google ADK: run the sales agent with an in-memory Runner."""

from __future__ import annotations

import asyncio
from sys import argv

from google.adk.runners import InMemoryRunner

from agent import root_agent


async def run() -> None:
    question = " ".join(argv[1:]) or "查询 2025 年各区域净销售额"
    runner = InMemoryRunner(agent=root_agent, app_name="governed_sales_agent")
    try:
        response = await runner.run_debug(question)
        print(response)
    finally:
        await runner.close()


if __name__ == "__main__":
    asyncio.run(run())
