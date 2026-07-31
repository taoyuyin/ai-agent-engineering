"""Real MCP SDK 2.x in-memory client."""

import asyncio

from mcp import Client
from server import mcp


async def main() -> None:
    async with Client(mcp) as client:
        print(await client.list_tools())
        result = await client.call_tool("get_metric", {"name": "revenue"})
        print(result.structured_content)
        print(await client.read_resource("metric://definitions/revenue"))


if __name__ == "__main__":
    asyncio.run(main())
