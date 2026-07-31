"""Real MCP SDK 2.x server. Run with: uv run mcp dev server.py"""

from mcp.server import MCPServer

mcp = MCPServer("Enterprise Metrics")

METRICS = {
    "revenue": {
        "definition": "sum(valid_order_amount), excluding cancelled orders",
        "value": 218000,
        "unit": "CNY",
    }
}


@mcp.tool()
def get_metric(name: str) -> dict:
    """Return a governed metric value and its definition."""
    if name not in METRICS:
        raise ValueError("unknown metric")
    return METRICS[name]


@mcp.resource("metric://definitions/{name}")
def metric_definition(name: str) -> str:
    """Read a governed metric definition."""
    if name not in METRICS:
        raise ValueError("unknown metric")
    return METRICS[name]["definition"]


@mcp.prompt()
def analyze_metric(name: str) -> str:
    """Build a reusable prompt for metric analysis."""
    return "Analyze metric {!r}; cite its governed definition before conclusions.".format(name)
