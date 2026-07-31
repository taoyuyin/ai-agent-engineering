"""Minimal function-calling runtime MVP.

Run:
    python chapters/chapter10/example.py
"""

from dataclasses import dataclass


SALES = {
    ("east", "2026Q2"): 1250000,
    ("north", "2026Q2"): 880000,
}


@dataclass
class Tool:
    name: str
    required: dict
    handler: object


def query_sales(region, quarter):
    return {"region": region, "quarter": quarter, "sales": SALES[(region, quarter)]}


TOOLS = {
    "query_sales": Tool(
        name="query_sales",
        required={"region": str, "quarter": str},
        handler=query_sales,
    )
}


def validate_call(call):
    if call["tool"] not in TOOLS:
        raise ValueError(f"Unknown tool: {call['tool']}")
    tool = TOOLS[call["tool"]]
    arguments = call.get("arguments", {})
    for name, expected_type in tool.required.items():
        if name not in arguments:
            raise ValueError(f"Missing argument: {name}")
        if not isinstance(arguments[name], expected_type):
            raise TypeError(f"{name} must be {expected_type.__name__}")
    return tool, arguments


def execute_tool_call(call):
    tool, arguments = validate_call(call)
    return tool.handler(**arguments)


if __name__ == "__main__":
    # Pretend this structured call was produced by a model.
    model_tool_call = {
        "tool": "query_sales",
        "arguments": {"region": "east", "quarter": "2026Q2"},
    }
    print("Tool call:", model_tool_call)
    print("Observation:", execute_tool_call(model_tool_call))
