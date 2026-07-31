import unittest

from function_calling import ExecutionContext, ToolCall, ToolDefinition, ToolRegistry


class ToolRuntimeTest(unittest.TestCase):
    def setUp(self) -> None:
        self.registry = ToolRegistry()
        self.registry.register(
            ToolDefinition(
                "read",
                "read value",
                {
                    "type": "object",
                    "properties": {"key": {"type": "string"}},
                    "required": ["key"],
                    "additionalProperties": False,
                },
                ("data:read",),
            ),
            lambda key: {"key": key},
        )

    def test_authorized_call_and_idempotency(self) -> None:
        call = ToolCall("1", "read", {"key": "revenue"})
        context = ExecutionContext("u1", ("data:read",))
        self.assertIs(self.registry.execute(call, context), self.registry.execute(call, context))

    def test_rejects_extra_arguments(self) -> None:
        result = self.registry.execute(
            ToolCall("2", "read", {"key": "x", "admin": True}),
            ExecutionContext("u1", ("data:read",)),
        )
        self.assertFalse(result.ok)


if __name__ == "__main__":
    unittest.main()
