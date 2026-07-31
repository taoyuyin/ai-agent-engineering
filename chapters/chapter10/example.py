"""Chapter 10 entry point: validate and authorize a model-generated tool call."""

from function_calling import ExecutionContext, ToolCall, ToolDefinition, ToolRegistry


def query_sales(region: str, limit: int = 10):
    rows = [{"region": region, "revenue": 120000}, {"region": region, "revenue": 98000}]
    return rows[:limit]


def main() -> None:
    registry = ToolRegistry()
    registry.register(
        ToolDefinition(
            name="query_sales",
            description="查询指定区域的销售汇总",
            input_schema={
                "type": "object",
                "properties": {
                    "region": {"type": "string", "enum": ["east", "west"]},
                    "limit": {"type": "integer", "minimum": 1, "maximum": 100},
                },
                "required": ["region"],
                "additionalProperties": False,
            },
            required_scopes=("sales:read",),
        ),
        query_sales,
    )

    context = ExecutionContext("user-42", scopes=("sales:read",))
    result = registry.execute(ToolCall("call-1", "query_sales", {"region": "east", "limit": 1}), context)
    print(result)

    rejected = registry.execute(
        ToolCall("call-2", "query_sales", {"region": "north", "debug": True}), context
    )
    print(rejected)


if __name__ == "__main__":
    main()
