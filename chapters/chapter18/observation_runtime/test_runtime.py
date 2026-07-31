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


if __name__ == "__main__":
    unittest.main()
