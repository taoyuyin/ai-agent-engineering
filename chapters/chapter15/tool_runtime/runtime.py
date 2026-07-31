from dataclasses import dataclass
from hashlib import sha256
from math import sqrt
from typing import Callable, Dict, List, Set, Tuple
import re


def _tokens(text: str) -> List[str]:
    return re.findall(r"[a-z0-9_]+|[\u4e00-\u9fff]", text.lower())


def _embed(text: str, dimensions: int = 48) -> Tuple[float, ...]:
    vector = [0.0] * dimensions
    for token in _tokens(text):
        digest = sha256(token.encode("utf-8")).digest()
        index = int.from_bytes(digest[:2], "big") % dimensions
        vector[index] += 1.0 if digest[2] % 2 else -1.0
    norm = sqrt(sum(value * value for value in vector)) or 1.0
    return tuple(value / norm for value in vector)


def _similarity(left: Tuple[float, ...], right: Tuple[float, ...]) -> float:
    return sum(a * b for a, b in zip(left, right))


@dataclass(frozen=True)
class ToolDefinition:
    name: str
    capabilities: Tuple[str, ...]
    required_scopes: Tuple[str, ...]
    cost: int
    read_only: bool
    description: str = ""


class ToolRegistry:
    def __init__(self) -> None:
        self._tools = {}  # type: Dict[str, Tuple[ToolDefinition, Callable[..., object]]]
        self._vectors = {}  # type: Dict[str, Tuple[float, ...]]

    def register(self, definition: ToolDefinition, function: Callable[..., object]) -> None:
        if definition.name in self._tools:
            raise ValueError("duplicate tool")
        self._tools[definition.name] = (definition, function)
        searchable = "{} {} {}".format(
            definition.name, definition.description, " ".join(definition.capabilities)
        )
        self._vectors[definition.name] = _embed(searchable)

    def search(self, query: str, scopes: Set[str], limit: int = 5) -> List[ToolDefinition]:
        query_vector = _embed(query)
        candidates = []
        for definition, _ in self._tools.values():
            if not set(definition.required_scopes) <= scopes:
                continue
            score = _similarity(query_vector, self._vectors[definition.name])
            candidates.append((score, -definition.cost, definition.name, definition))
        candidates.sort(reverse=True)
        return [item[3] for item in candidates[:limit]]

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
