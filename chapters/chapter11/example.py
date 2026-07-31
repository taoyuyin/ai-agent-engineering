"""Minimal MCP-style tool server MVP.

Run:
    python chapters/chapter11/example.py
"""


class MiniMCPServer:
    def __init__(self):
        self.tools = {}

    def tool(self, name, description, schema):
        def decorator(func):
            self.tools[name] = {
                "description": description,
                "schema": schema,
                "handler": func,
            }
            return func
        return decorator

    def list_tools(self):
        return {
            name: {
                "description": spec["description"],
                "schema": spec["schema"],
            }
            for name, spec in self.tools.items()
        }

    def call_tool(self, name, arguments):
        if name not in self.tools:
            raise ValueError(f"Unknown tool: {name}")
        schema = self.tools[name]["schema"]
        for required in schema.get("required", []):
            if required not in arguments:
                raise ValueError(f"Missing argument: {required}")
        return self.tools[name]["handler"](**arguments)


server = MiniMCPServer()


@server.tool(
    name="get_metric_definition",
    description="Return enterprise metric definition",
    schema={"required": ["metric_name"]},
)
def get_metric_definition(metric_name):
    definitions = {
        "gmv": "GMV 是成交总额，不等同于确认收入。",
        "revenue": "Revenue 是确认收入，需要排除退款和取消订单。",
    }
    return definitions.get(metric_name.lower(), "Unknown metric")


if __name__ == "__main__":
    print("Available tools:")
    print(server.list_tools())

    print("\nCall result:")
    result = server.call_tool("get_metric_definition", {"metric_name": "gmv"})
    print(result)
