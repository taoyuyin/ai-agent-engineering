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

    def test_semantic_discovery_filters_scope_before_ranking(self) -> None:
        registry = ToolRegistry()
        registry.register(
            ToolDefinition("sales", ("read",), ("sales:read",), 1, True, "查询销售收入趋势"),
            lambda: 1,
        )
        registry.register(
            ToolDefinition("admin", ("sql",), ("admin:sql",), 1, True, "查询销售收入趋势"),
            lambda: 2,
        )
        self.assertEqual(["sales"], [tool.name for tool in registry.search("销售趋势", {"sales:read"})])


if __name__ == "__main__":
    unittest.main()
