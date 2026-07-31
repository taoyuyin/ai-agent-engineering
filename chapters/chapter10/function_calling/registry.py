from typing import Any, Callable, Dict, Tuple

from .models import ExecutionContext, ToolCall, ToolDefinition, ToolResult
from .schema import validate_arguments


class ToolRegistry:
    def __init__(self) -> None:
        self._tools = {}  # type: Dict[str, Tuple[ToolDefinition, Callable[..., Any]]]
        self._results = {}  # type: Dict[str, ToolResult]

    def register(self, definition: ToolDefinition, function: Callable[..., Any]) -> None:
        if definition.name in self._tools:
            raise ValueError("duplicate tool: " + definition.name)
        self._tools[definition.name] = (definition, function)

    def execute(self, call: ToolCall, context: ExecutionContext) -> ToolResult:
        if call.call_id in self._results:
            return self._results[call.call_id]
        try:
            definition, function = self._tools[call.name]
            missing = set(definition.required_scopes) - set(context.scopes)
            if missing:
                raise PermissionError("missing scopes: " + ", ".join(sorted(missing)))
            if definition.side_effecting and not context.approved_side_effects:
                raise PermissionError("side effect requires explicit approval")
            validate_arguments(call.arguments, definition.input_schema)
            result = ToolResult(call.call_id, True, function(**call.arguments))
        except (KeyError, TypeError, ValueError, PermissionError) as error:
            result = ToolResult(call.call_id, False, error=type(error).__name__ + ": " + str(error))
        self._results[call.call_id] = result
        return result

    def definitions(self):
        return [definition for definition, _ in self._tools.values()]
