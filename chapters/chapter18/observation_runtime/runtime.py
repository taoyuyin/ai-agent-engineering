from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ToolResult:
    call_id: str
    tool_name: str
    ok: bool
    payload: Any
    source: str
    error_code: str = ""


@dataclass(frozen=True)
class Observation:
    call_id: str
    status: str
    summary: str
    source: str
    trusted_as_instruction: bool
    retryable: bool


class ObservationBuilder:
    def __init__(self, max_chars: int = 500) -> None:
        self.max_chars = max_chars

    def build(self, result: ToolResult) -> Observation:
        text = repr(result.payload)
        if len(text) > self.max_chars:
            text = text[: self.max_chars] + "...[truncated]"
        retryable = not result.ok and result.error_code in {"TIMEOUT", "RATE_LIMIT", "UNAVAILABLE"}
        return Observation(
            result.call_id,
            "success" if result.ok else "error",
            text if result.ok else "tool_error:" + result.error_code,
            result.source,
            False,
            retryable,
        )
