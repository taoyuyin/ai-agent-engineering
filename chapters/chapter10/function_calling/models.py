from dataclasses import dataclass
from typing import Any, Dict, Tuple


@dataclass(frozen=True)
class ToolDefinition:
    name: str
    description: str
    input_schema: Dict[str, Any]
    required_scopes: Tuple[str, ...] = ()
    side_effecting: bool = False


@dataclass(frozen=True)
class ToolCall:
    call_id: str
    name: str
    arguments: Dict[str, Any]


@dataclass(frozen=True)
class ExecutionContext:
    actor_id: str
    scopes: Tuple[str, ...] = ()
    approved_side_effects: bool = False


@dataclass(frozen=True)
class ToolResult:
    call_id: str
    ok: bool
    value: Any = None
    error: str = ""
