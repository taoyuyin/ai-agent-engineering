"""Chapter 18: normalize a raw tool response into an Observation."""

from observation_runtime import ObservationBuilder, ToolResult


def main() -> None:
    raw = ToolResult(
        call_id="call-7",
        tool_name="query_sales",
        ok=True,
        payload={"region": "east", "revenue": 218000},
        source="warehouse.sales_monthly",
    )
    builder = ObservationBuilder(max_chars=120)
    print(builder.build(raw))
    print(
        builder.from_mcp(
            "call-8",
            "query_sales",
            {"structuredContent": {"region": "east", "revenue": 218000}, "isError": False},
            "mcp://analytics/query_sales",
        )
    )


if __name__ == "__main__":
    main()
