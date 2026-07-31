import unittest

from mcp_runtime import InProcessMCPClient, MetricsMCPServer, ProtocolError


class ProtocolTest(unittest.TestCase):
    def test_requires_discovery(self) -> None:
        with self.assertRaises(ProtocolError):
            InProcessMCPClient(MetricsMCPServer()).list_tools()

    def test_discovers_and_calls_tool(self) -> None:
        client = InProcessMCPClient(MetricsMCPServer())
        client.discover()
        result = client.call_tool("get_metric", {"name": "revenue"})
        self.assertIn("218000", result["content"][0]["text"])


if __name__ == "__main__":
    unittest.main()
