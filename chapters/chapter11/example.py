"""Dependency-free MCP data-layer simulation for the chapter's default run."""

from mcp_runtime.protocol import InProcessMCPClient, MetricsMCPServer


def main() -> None:
    client = InProcessMCPClient(MetricsMCPServer())
    print("Discovery:", client.discover())
    print("Tools:", client.list_tools())
    print("Call:", client.call_tool("get_metric", {"name": "revenue"}))
    print("Resource:", client.read_resource("metric://definitions/revenue"))


if __name__ == "__main__":
    main()
