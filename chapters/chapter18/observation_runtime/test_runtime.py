import unittest

from observation_runtime import ObservationBuilder, ToolResult


class ObservationTest(unittest.TestCase):
    def test_truncates_and_marks_external_data_untrusted(self) -> None:
        observation = ObservationBuilder(5).build(ToolResult("1", "t", True, "abcdefgh", "api"))
        self.assertIn("truncated", observation.summary)
        self.assertFalse(observation.trusted_as_instruction)

    def test_classifies_retryable_error(self) -> None:
        observation = ObservationBuilder().build(
            ToolResult("1", "t", False, None, "api", "TIMEOUT")
        )
        self.assertTrue(observation.retryable)

    def test_adapts_mcp_structured_content(self) -> None:
        observation = ObservationBuilder().from_mcp(
            "1", "sales", {"structuredContent": {"revenue": 10}, "isError": False}, "mcp://sales"
        )
        self.assertEqual("success", observation.status)
        self.assertEqual("mcp://sales", observation.source)
        self.assertFalse(observation.trusted_as_instruction)


if __name__ == "__main__":
    unittest.main()
