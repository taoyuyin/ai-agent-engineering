from typing import Any, Dict


PROTOCOL_VERSION = "2026-07-28"


class ProtocolError(Exception):
    pass


class MetricsMCPServer:
    """Small data-layer model; use server.py for the official SDK implementation."""

    def discover(self, version: str) -> Dict[str, Any]:
        if version != PROTOCOL_VERSION:
            raise ProtocolError("unsupported protocol version")
        return {
            "supportedVersions": [PROTOCOL_VERSION],
            "capabilities": {"tools": {}, "resources": {}, "prompts": {}},
            "serverInfo": {"name": "enterprise-metrics", "version": "1.0.0"},
        }

    def list_tools(self):
        return [
            {
                "name": "get_metric",
                "description": "Return a governed enterprise metric",
                "inputSchema": {
                    "type": "object",
                    "properties": {"name": {"type": "string"}},
                    "required": ["name"],
                    "additionalProperties": False,
                },
            }
        ]

    def call_tool(self, name: str, arguments: Dict[str, Any]):
        if name != "get_metric":
            raise ProtocolError("unknown tool")
        if set(arguments) != {"name"} or not isinstance(arguments["name"], str):
            raise ProtocolError("invalid arguments")
        definitions = {"revenue": {"value": 218000, "currency": "CNY"}}
        if arguments["name"] not in definitions:
            raise ProtocolError("metric not found")
        return {"content": [{"type": "text", "text": str(definitions[arguments["name"]])}]}

    def read_resource(self, uri: str):
        if uri != "metric://definitions/revenue":
            raise ProtocolError("resource not found")
        return "revenue = sum(valid_order_amount), excluding cancelled orders"


class InProcessMCPClient:
    def __init__(self, server: MetricsMCPServer) -> None:
        self.server = server
        self.ready = False

    def discover(self):
        result = self.server.discover(PROTOCOL_VERSION)
        self.ready = True
        return result

    def list_tools(self):
        self._require_ready()
        return self.server.list_tools()

    def call_tool(self, name: str, arguments: Dict[str, Any]):
        self._require_ready()
        return self.server.call_tool(name, arguments)

    def read_resource(self, uri: str):
        self._require_ready()
        return self.server.read_resource(uri)

    def _require_ready(self) -> None:
        if not self.ready:
            raise ProtocolError("call discover before using server capabilities")
