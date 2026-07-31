from dataclasses import dataclass
from hashlib import sha256
from math import sqrt
from typing import Callable, Dict, List, Tuple
import re


def _embed(text: str, dimensions: int = 48) -> Tuple[float, ...]:
    vector = [0.0] * dimensions
    for token in re.findall(r"[a-z0-9_]+|[\u4e00-\u9fff]", text.lower()):
        digest = sha256(token.encode("utf-8")).digest()
        vector[int.from_bytes(digest[:2], "big") % dimensions] += 1.0
    norm = sqrt(sum(value * value for value in vector)) or 1.0
    return tuple(value / norm for value in vector)


@dataclass(frozen=True)
class AgentCard:
    agent_id: str
    capabilities: Tuple[str, ...]
    scopes: Tuple[str, ...]
    description: str = ""


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
        self._vectors = {}  # type: Dict[str, Tuple[float, ...]]
        self._delegations = 0

    def register(self, card: AgentCard, handler: Callable[[TaskEnvelope], Dict[str, object]]) -> None:
        self._agents[card.agent_id] = (card, handler)
        text = "{} {} {}".format(card.agent_id, card.description, " ".join(card.capabilities))
        self._vectors[card.agent_id] = _embed(text)

    def discover(
        self, objective: str, delegated_scopes: Tuple[str, ...], limit: int = 3
    ) -> List[AgentCard]:
        query = _embed(objective)
        candidates = []
        for card, _ in self._agents.values():
            if not set(delegated_scopes) <= set(card.scopes):
                continue
            score = sum(a * b for a, b in zip(query, self._vectors[card.agent_id]))
            candidates.append((score, card.agent_id, card))
        candidates.sort(reverse=True)
        return [item[2] for item in candidates[:limit]]

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
