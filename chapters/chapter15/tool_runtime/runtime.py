from dataclasses import dataclass
from typing import Callable, Dict, Set, Tuple


@dataclass(frozen=True)
class ToolDefinition:
    name: str
    capabilities: Tuple[str, ...]
    required_scopes: Tuple[str, ...]
    cost: int
    read_only: bool


class ToolRegistry:
    def __init__(self) -> None:
        self._tools = {}  # type: Dict[str, Tuple[ToolDefinition, Callable[..., object]]]

    def register(self, definition: ToolDefinition, function: Callable[..., object]) -> None:
        if definition.name in self._tools:
            raise ValueError("duplicate tool")
        self._tools[definition.name] = (definition, function)

    def route(self, required: Set[str], scopes: Set[str], require_read_only: bool = False) -> ToolDefinition:
        candidates = []
        for definition, _ in self._tools.values():
            if not required <= set(definition.capabilities):
                continue
            if not set(definition.required_scopes) <= scopes:
                continue
            if require_read_only and not definition.read_only:
                continue
            candidates.append(definition)
        if not candidates:
            raise LookupError("no authorized tool matches the task")
        return sorted(candidates, key=lambda item: (item.cost, item.name))[0]

    def call(self, name: str, arguments: Dict[str, object], scopes: Set[str]) -> object:
        definition, function = self._tools[name]
        if not set(definition.required_scopes) <= scopes:
            raise PermissionError("missing tool scope")
        return function(**arguments)
