import unittest

from multi_agent_runtime import AgentCard, Coordinator, TaskEnvelope


class CoordinatorTest(unittest.TestCase):
    def test_delegates_only_with_matching_scope(self) -> None:
        coordinator = Coordinator()
        coordinator.register(AgentCard("a", ("read",), ("r",)), lambda task: {"evidence": ["1"]})
        with self.assertRaises(LookupError):
            coordinator.delegate(TaskEnvelope("1", "x", ("read",), ("admin",)))

    def test_requires_evidence(self) -> None:
        coordinator = Coordinator()
        coordinator.register(AgentCard("a", ("read",), ("r",)), lambda task: {"answer": "x"})
        with self.assertRaises(ValueError):
            coordinator.delegate(TaskEnvelope("1", "x", ("read",), ("r",)))

    def test_semantic_discovery_applies_scope_first(self) -> None:
        coordinator = Coordinator()
        coordinator.register(
            AgentCard("sales", ("analysis",), ("sales:read",), "分析销售收入"),
            lambda task: {"evidence": ["1"]},
        )
        coordinator.register(
            AgentCard("admin", ("analysis",), ("admin",), "分析销售收入"),
            lambda task: {"evidence": ["2"]},
        )
        cards = coordinator.discover("销售趋势分析", ("sales:read",))
        self.assertEqual(["sales"], [card.agent_id for card in cards])


if __name__ == "__main__":
    unittest.main()
