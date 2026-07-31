from dataclasses import dataclass
from typing import Dict, List, Tuple


@dataclass(frozen=True)
class AgentRequest:
    run_id: str
    tenant_id: str
    actor_id: str
    objective: str
    scopes: Tuple[str, ...]


class AuditSink:
    def __init__(self) -> None:
        self.events = []  # type: List[Dict[str, str]]

    def emit(self, run_id: str, event: str, outcome: str) -> None:
        self.events.append({"run_id": run_id, "event": event, "outcome": outcome})


class PolicyEnforcer:
    def authorize(self, request: AgentRequest, required_scope: str) -> None:
        if not request.tenant_id or required_scope not in request.scopes:
            raise PermissionError("request is outside the policy boundary")


class EnterpriseAgentRuntime:
    """A small composition root, not a model simulation."""

    def __init__(self) -> None:
        self.audit = AuditSink()
        self.policy = PolicyEnforcer()
        self.sales = {"tenant-a": {"east": 218000}}

    def run(self, request: AgentRequest) -> Dict[str, object]:
        self.audit.emit(request.run_id, "run_started", "accepted")
        try:
            self.policy.authorize(request, "sales:read")
            evidence = self.sales.get(request.tenant_id, {}).get("east")
            if evidence is None:
                raise LookupError("tenant data not found")
            response = {
                "run_id": request.run_id,
                "status": "completed",
                "answer": "华东销售额为 {} CNY".format(evidence),
                "evidence": [{"source": "sales_monthly", "value": evidence}],
            }
            self.audit.emit(request.run_id, "run_completed", "success")
            return response
        except (PermissionError, LookupError) as error:
            self.audit.emit(request.run_id, "run_failed", type(error).__name__)
            raise
