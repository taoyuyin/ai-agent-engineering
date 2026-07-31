"""Deterministic authorization boundary between model proposals and tools."""

from framework.contracts import AgentRequest, PlanStep, ToolRisk
from framework.tools import ToolDefinition


class PolicyEngine:
    def authorize(
        self,
        request: AgentRequest,
        step: PlanStep,
        tool: ToolDefinition,
    ) -> None:
        required = set(step.required_scopes) | set(tool.required_scopes)
        missing = required - set(request.scopes)
        if missing:
            raise PermissionError(
                "missing scopes for {}: {}".format(tool.name, ", ".join(sorted(missing)))
            )
        if tool.risk == ToolRisk.WRITE and "agent:write" not in request.scopes:
            raise PermissionError("write tool requires agent:write")
        if tool.risk == ToolRisk.PRIVILEGED and "agent:privileged" not in request.scopes:
            raise PermissionError("privileged tool requires agent:privileged")
