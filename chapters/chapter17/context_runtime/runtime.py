from dataclasses import dataclass, replace
from hashlib import sha256
from math import sqrt
from typing import Dict, List
import re


def estimate_tokens(text: str) -> int:
    return max(1, sum(1 if ord(char) > 127 else 0.25 for char in text))


def _embed(text: str, dimensions: int = 48) -> List[float]:
    vector = [0.0] * dimensions
    for token in re.findall(r"[a-z0-9_]+|[\u4e00-\u9fff]", text.lower()):
        digest = sha256(token.encode("utf-8")).digest()
        vector[int.from_bytes(digest[:2], "big") % dimensions] += 1.0
    norm = sqrt(sum(value * value for value in vector)) or 1.0
    return [value / norm for value in vector]


def _relevance(query: str, content: str) -> float:
    return sum(a * b for a, b in zip(_embed(query), _embed(content)))


@dataclass(frozen=True)
class ContextItem:
    item_id: str
    section: str
    content: str
    priority: int
    trusted: bool

    @property
    def tokens(self) -> int:
        return int(estimate_tokens(self.content))


@dataclass(frozen=True)
class ContextPolicy:
    total_budget: int
    section_budgets: Dict[str, int]


@dataclass(frozen=True)
class AssemblyResult:
    selected: List[ContextItem]
    dropped: Dict[str, str]

    def render(self) -> str:
        return "\n\n".join(
            "[{}|{}]\n{}".format(item.section, "trusted" if item.trusted else "untrusted", item.content)
            for item in self.selected
        )


class ContextAssembler:
    def __init__(self, policy: ContextPolicy) -> None:
        self.policy = policy

    def assemble(self, items: List[ContextItem]) -> AssemblyResult:
        selected = []
        dropped = {}
        total = 0
        section_used = {}  # type: Dict[str, int]
        for item in sorted(items, key=lambda value: (-value.priority, value.item_id)):
            section_limit = self.policy.section_budgets.get(item.section, 0)
            if section_used.get(item.section, 0) + item.tokens > section_limit:
                dropped[item.item_id] = "section_budget"
                continue
            if total + item.tokens > self.policy.total_budget:
                dropped[item.item_id] = "total_budget"
                continue
            selected.append(item)
            total += item.tokens
            section_used[item.section] = section_used.get(item.section, 0) + item.tokens
        return AssemblyResult(selected, dropped)

    def assemble_for(self, query: str, items: List[ContextItem]) -> AssemblyResult:
        ranked = [
            replace(item, priority=item.priority + int(max(0.0, _relevance(query, item.content)) * 100))
            for item in items
        ]
        return self.assemble(ranked)
