from dataclasses import dataclass
from typing import Callable, Dict, List, Tuple


@dataclass(frozen=True)
class AgentCard:
    agent_id: str
    capabilities: Tuple[str, ...]
    scopes: Tuple[str, ...]


@dataclass(frozen=True)
class TaskEnvelope:
    task_id: str
    objective: str
    required_capabilities: Tuple[str, ...]
    delegated_scopes: Tuple[str, ...]


class Coordinator:
    def __init__(self, max_delegations: int = 4) -> None:
        self.max_delegations = max_delegations
        self._agents = {}  # type: Dict[str, Tuple[AgentCard, Callable[[TaskEnvelope], Dict[str, object]]]]
        self._delegations = 0

    def register(self, card: AgentCard, handler: Callable[[TaskEnvelope], Dict[str, object]]) -> None:
        self._agents[card.agent_id] = (card, handler)

    def delegate(self, task: TaskEnvelope) -> Dict[str, object]:
        if self._delegations >= self.max_delegations:
            raise RuntimeError("delegation budget exhausted")
        candidates = []
        for card, handler in self._agents.values():
            if not set(task.required_capabilities) <= set(card.capabilities):
                continue
            if not set(task.delegated_scopes) <= set(card.scopes):
                continue
            candidates.append((card.agent_id, handler))
        if not candidates:
            raise LookupError("no authorized specialist")
        self._delegations += 1
        agent_id, handler = sorted(candidates, key=lambda item: item[0])[0]
        result = handler(task)
        if not result.get("evidence"):
            raise ValueError("subagent result requires evidence")
        return {"agent_id": agent_id, "task_id": task.task_id, "result": result}

    @staticmethod
    def resolve(results: List[Dict[str, object]]) -> Dict[str, object]:
        with_evidence = [result for result in results if result.get("evidence")]
        if not with_evidence:
            raise ValueError("cannot resolve without evidence")
        return max(with_evidence, key=lambda result: float(result.get("confidence", 0)))
