import unittest

from tool_runtime import ToolDefinition, ToolRegistry


class ToolRegistryTest(unittest.TestCase):
    def test_routes_lowest_cost_authorized_tool(self) -> None:
        registry = ToolRegistry()
        registry.register(ToolDefinition("b", ("read",), ("r",), 4, True), lambda: 2)
        registry.register(ToolDefinition("a", ("read",), ("r",), 1, True), lambda: 1)
        self.assertEqual("a", registry.route({"read"}, {"r"}).name)

    def test_fails_closed_without_scope(self) -> None:
        registry = ToolRegistry()
        registry.register(ToolDefinition("a", ("read",), ("r",), 1, True), lambda: 1)
        with self.assertRaises(LookupError):
            registry.route({"read"}, set())


if __name__ == "__main__":
    unittest.main()
