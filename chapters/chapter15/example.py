"""Chapter 15: route a task to the safest matching tool."""

from tool_runtime import ToolDefinition, ToolRegistry


def main() -> None:
    registry = ToolRegistry()
    registry.register(
        ToolDefinition("sales_summary", ("sales", "read"), ("sales:read",), 2, True),
        lambda region: {"region": region, "revenue": 218000},
    )
    registry.register(
        ToolDefinition("raw_sql", ("sales", "sql"), ("admin:sql",), 9, True),
        lambda region: {"region": region},
    )
    tool = registry.route({"sales", "read"}, scopes={"sales:read"}, require_read_only=True)
    print(tool.name, registry.call(tool.name, {"region": "east"}, {"sales:read"}))


if __name__ == "__main__":
    main()
