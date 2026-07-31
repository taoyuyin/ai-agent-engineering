"""Typed tool registry. Models may propose calls; the registry owns execution contracts."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from pydantic import BaseModel

from framework.contracts import ToolRisk


ToolHandler = Callable[[BaseModel], Any]


@dataclass(frozen=True)
class ToolDefinition:
    name: str
    description: str
    input_model: type[BaseModel]
    handler: ToolHandler
    required_scopes: frozenset[str] = frozenset()
    risk: ToolRisk = ToolRisk.READ


class ToolRegistry:
    def __init__(self) -> None:
        self._tools: dict[str, ToolDefinition] = {}

    def register(self, definition: ToolDefinition) -> None:
        if definition.name in self._tools:
            raise ValueError(f"tool already registered: {definition.name}")
        self._tools[definition.name] = definition

    def resolve(self, name: str) -> ToolDefinition:
        try:
            return self._tools[name]
        except KeyError as error:
            raise LookupError(f"unknown tool: {name}") from error

    def describe(self) -> tuple[dict[str, Any], ...]:
        return tuple(
            {
                "name": tool.name,
                "description": tool.description,
                "input_schema": tool.input_model.model_json_schema(),
                "required_scopes": sorted(tool.required_scopes),
                "risk": tool.risk.value,
            }
            for tool in self._tools.values()
        )
