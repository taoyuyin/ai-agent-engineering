from dataclasses import dataclass
from typing import Optional


def estimate_tokens(text: str) -> int:
    """Portable estimate for budget decisions; replace with the model tokenizer."""
    ascii_chars = sum(1 for char in text if ord(char) < 128)
    non_ascii_chars = len(text) - ascii_chars
    return max(1, ascii_chars // 4 + non_ascii_chars)


@dataclass(frozen=True)
class ContextItem:
    item_id: str
    section: str
    content: str
    priority: int
    required: bool = False
    trusted: bool = True
    source: str = "runtime"
    token_count: Optional[int] = None

    @property
    def tokens(self) -> int:
        return self.token_count if self.token_count is not None else estimate_tokens(self.content)


@dataclass(frozen=True)
class ContextBudget:
    model_window: int
    reserved_output: int
    fixed_overhead: int = 0

    @property
    def available_input(self) -> int:
        available = self.model_window - self.reserved_output - self.fixed_overhead
        if available <= 0:
            raise ValueError("reserved_output and fixed_overhead exhaust the model window")
        return available
