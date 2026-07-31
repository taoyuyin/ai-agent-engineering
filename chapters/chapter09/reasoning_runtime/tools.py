from typing import Any, Callable, Dict


class ToolRegistry:
    def __init__(self) -> None:
        self._tools = {}  # type: Dict[str, Callable[..., Any]]

    def register(self, name: str, function: Callable[..., Any]) -> None:
        if name in self._tools:
            raise ValueError("duplicate tool: " + name)
        self._tools[name] = function

    def call(self, name: str, **arguments: Any) -> Any:
        if name not in self._tools:
            raise ValueError("unknown tool: " + name)
        return self._tools[name](**arguments)
