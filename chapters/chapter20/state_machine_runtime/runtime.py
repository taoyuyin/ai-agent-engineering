from dataclasses import dataclass
from typing import Dict, List, Tuple


@dataclass(frozen=True)
class Event:
    sequence: int
    event_type: str


class EventStore:
    def __init__(self) -> None:
        self._streams = {}  # type: Dict[str, List[Event]]

    def append(self, run_id: str, event_type: str, expected_sequence: int) -> Event:
        stream = self._streams.setdefault(run_id, [])
        if len(stream) != expected_sequence:
            raise RuntimeError("concurrent state update")
        event = Event(len(stream) + 1, event_type)
        stream.append(event)
        return event

    def events(self, run_id: str) -> List[Event]:
        return list(self._streams.get(run_id, []))


class AgentStateMachine:
    transitions = {
        ("created", "goal_validated"): "planning",
        ("planning", "plan_created"): "ready",
        ("ready", "tool_requested"): "running",
        ("running", "tool_succeeded"): "ready",
        ("ready", "completed"): "completed",
    }  # type: Dict[Tuple[str, str], str]

    def __init__(self, store: EventStore) -> None:
        self.store = store

    def apply(self, run_id: str, event_type: str) -> str:
        events = self.store.events(run_id)
        current = self._reduce(events)
        if (current, event_type) not in self.transitions:
            raise ValueError("illegal event for state")
        self.store.append(run_id, event_type, len(events))
        return self.transitions[(current, event_type)]

    def rebuild(self, run_id: str) -> str:
        return self._reduce(self.store.events(run_id))

    def _reduce(self, events: List[Event]) -> str:
        state = "created"
        for event in events:
            state = self.transitions[(state, event.event_type)]
        return state
