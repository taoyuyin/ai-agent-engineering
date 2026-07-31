from dataclasses import dataclass
from typing import Dict, List


def estimate_tokens(text: str) -> int:
    return max(1, sum(1 if ord(char) > 127 else 0.25 for char in text))


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
