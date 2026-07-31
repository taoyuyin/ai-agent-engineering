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

    def test_semantic_relevance_changes_candidate_order(self) -> None:
        assembler = ContextAssembler(ContextPolicy(20, {"evidence": 20}))
        result = assembler.assemble_for(
            "销售收入",
            [
                ContextItem("inventory", "evidence", "库存数量", 1, True),
                ContextItem("sales", "evidence", "销售收入", 1, True),
            ],
        )
        self.assertEqual("sales", result.selected[0].item_id)


if __name__ == "__main__":
    unittest.main()
