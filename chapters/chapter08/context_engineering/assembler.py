from dataclasses import dataclass
from typing import Dict, List

from .models import ContextBudget, ContextItem


@dataclass(frozen=True)
class AssemblyResult:
    selected: List[ContextItem]
    dropped: Dict[str, str]
    used_tokens: int

    def render(self) -> str:
        blocks = []
        for item in self.selected:
            trust = "trusted" if item.trusted else "untrusted-data"
            blocks.append(
                "[{section} | {trust} | source={source}]\n{content}".format(
                    section=item.section,
                    trust=trust,
                    source=item.source,
                    content=item.content,
                )
            )
        return "\n\n".join(blocks)


class ContextAssembler:
    """Select required and high-value items without exceeding the input budget."""

    def __init__(self, budget: ContextBudget) -> None:
        self.budget = budget

    def assemble(self, items: List[ContextItem]) -> AssemblyResult:
        unique = self._deduplicate(items)
        ordered = sorted(
            unique,
            key=lambda item: (not item.required, -item.priority, item.item_id),
        )
        selected = []
        dropped = {}
        used = 0

        for item in ordered:
            if item.tokens > self.budget.available_input:
                if item.required:
                    raise ValueError("required item exceeds input budget: " + item.item_id)
                dropped[item.item_id] = "item_too_large"
                continue
            if used + item.tokens > self.budget.available_input:
                dropped[item.item_id] = "budget_exceeded"
                continue
            selected.append(item)
            used += item.tokens

        return AssemblyResult(selected, dropped, used)

    @staticmethod
    def _deduplicate(items: List[ContextItem]) -> List[ContextItem]:
        by_content = {}
        for item in items:
            fingerprint = " ".join(item.content.lower().split())
            previous = by_content.get(fingerprint)
            if previous is None or (item.required, item.priority) > (
                previous.required,
                previous.priority,
            ):
                by_content[fingerprint] = item
        return list(by_content.values())
