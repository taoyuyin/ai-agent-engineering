"""Structured trace events with deterministic ordering."""

from __future__ import annotations

from typing import Any

from framework.contracts import TraceEvent


class InMemoryTraceSink:
    def __init__(self) -> None:
        self._events: dict[str, list[TraceEvent]] = {}

    def emit(self, run_id: str, event_type: str, **attributes: Any) -> TraceEvent:
        events = self._events.setdefault(run_id, [])
        event = TraceEvent(
            sequence=len(events) + 1,
            run_id=run_id,
            event_type=event_type,
            attributes=attributes,
        )
        events.append(event)
        return event

    def list_run(self, run_id: str) -> tuple[TraceEvent, ...]:
        events = self._events.get(run_id)
        return tuple(events) if events else ()
