"""A small tracing runtime with nesting, status and attribute redaction."""

from contextlib import contextmanager
from dataclasses import asdict, dataclass
from time import perf_counter
from typing import Dict, Iterator, List, Mapping, Optional
from uuid import uuid4
import json


@dataclass
class Span:
    trace_id: str
    span_id: str
    parent_span_id: Optional[str]
    name: str
    start_ms: float
    duration_ms: float
    status: str
    attributes: Mapping[str, object]


class TraceRecorder:
    REDACT_KEYS = {"api_key", "authorization", "password", "token", "secret"}

    def __init__(self, trace_id: Optional[str] = None) -> None:
        self.trace_id = trace_id or uuid4().hex
        self.spans: List[Span] = []
        self._stack: List[str] = []

    def _redact(self, attributes: Mapping[str, object]) -> Dict[str, object]:
        return {
            key: "[REDACTED]" if key.lower() in self.REDACT_KEYS else value
            for key, value in attributes.items()
        }

    @contextmanager
    def span(self, name: str, attributes: Optional[Mapping[str, object]] = None) -> Iterator[Span]:
        started = perf_counter()
        item = Span(
            trace_id=self.trace_id,
            span_id=uuid4().hex[:16],
            parent_span_id=self._stack[-1] if self._stack else None,
            name=name,
            start_ms=started * 1000,
            duration_ms=0.0,
            status="ok",
            attributes=self._redact(attributes or {}),
        )
        self._stack.append(item.span_id)
        try:
            yield item
        except Exception:
            item.status = "error"
            raise
        finally:
            item.duration_ms = (perf_counter() - started) * 1000
            self._stack.pop()
            self.spans.append(item)

    def to_json(self) -> str:
        return json.dumps([asdict(span) for span in self.spans], ensure_ascii=False, sort_keys=True)

    def metrics(self) -> Mapping[str, object]:
        return {
            "span_count": len(self.spans),
            "error_count": sum(span.status == "error" for span in self.spans),
            "total_duration_ms": round(sum(span.duration_ms for span in self.spans), 3),
        }
