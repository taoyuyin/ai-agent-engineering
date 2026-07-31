import unittest

from context_runtime import ContextAssembler, ContextItem, ContextPolicy


class ContextRuntimeTest(unittest.TestCase):
    def test_enforces_section_budget(self) -> None:
        result = ContextAssembler(ContextPolicy(20, {"history": 2})).assemble(
            [ContextItem("h", "history", "too long history", 1, False)]
        )
        self.assertEqual({"h": "section_budget"}, result.dropped)

    def test_marks_trust_boundary(self) -> None:
        result = ContextAssembler(ContextPolicy(20, {"evidence": 20})).assemble(
            [ContextItem("e", "evidence", "external data", 1, False)]
        )
        self.assertIn("untrusted", result.render())


if __name__ == "__main__":
    unittest.main()
