import unittest

from reasoning_runtime import ReasoningController, ToolRegistry


class ReasoningControllerTest(unittest.TestCase):
    def test_produces_auditable_evidence(self) -> None:
        tools = ToolRegistry()
        tools.register("get_churn_rate", lambda segment: {"rate": 0.1})
        tools.register("get_ticket_rate", lambda segment: {"rate": 0.2})
        result = ReasoningController(tools).run("diagnose", "SMB")
        self.assertIn("10%", result.answer)
        self.assertEqual("verification", result.trace[-1].kind)

    def test_unknown_tool_fails_closed(self) -> None:
        with self.assertRaises(ValueError):
            ToolRegistry().call("missing")

    def test_repairs_a_transient_tool_failure(self) -> None:
        attempts = {"churn": 0}

        def churn(segment):
            attempts["churn"] += 1
            if attempts["churn"] == 1:
                raise TimeoutError("temporary")
            return {"rate": 0.1}

        tools = ToolRegistry()
        tools.register("get_churn_rate", churn)
        tools.register("get_ticket_rate", lambda segment: {"rate": 0.2})
        result = ReasoningController(tools, max_repairs=1).run("diagnose", "SMB")
        self.assertIn("repair", [event.kind for event in result.trace])


if __name__ == "__main__":
    unittest.main()
