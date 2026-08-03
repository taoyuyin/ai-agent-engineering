"""Chapter 50: an offline Agent Platform release and routing control plane."""

from dataclasses import asdict, dataclass, field
from enum import Enum
import json


class ReleaseStatus(str, Enum):
    REJECTED = "rejected"
    APPROVED = "approved"


@dataclass(frozen=True)
class AgentManifest:
    name: str
    version: str
    owner: str
    capabilities: tuple[str, ...]
    required_scopes: tuple[str, ...]
    model_tier: str
    evaluation_score: float
    estimated_cost: float


@dataclass(frozen=True)
class ReleaseDecision:
    status: ReleaseStatus
    reasons: tuple[str, ...]


@dataclass(frozen=True)
class TaskEnvelope:
    task_id: str
    tenant: str
    capability: str
    granted_scopes: tuple[str, ...]
    cost_budget: float


@dataclass
class AgentRegistry:
    releases: dict[str, AgentManifest] = field(default_factory=dict)

    def publish(self, manifest: AgentManifest, decision: ReleaseDecision) -> None:
        if decision.status is not ReleaseStatus.APPROVED:
            raise ValueError(f"release rejected: {', '.join(decision.reasons)}")
        self.releases[f"{manifest.name}:{manifest.version}"] = manifest

    def route(self, task: TaskEnvelope) -> AgentManifest:
        candidates = []
        granted = set(task.granted_scopes)
        for manifest in self.releases.values():
            if task.capability not in manifest.capabilities:
                continue
            if not set(manifest.required_scopes).issubset(granted):
                continue
            if manifest.estimated_cost > task.cost_budget:
                continue
            candidates.append(manifest)
        if not candidates:
            raise LookupError("no governed agent can satisfy the task")
        return max(candidates, key=lambda item: (item.evaluation_score, -item.estimated_cost))


def evaluate_release(manifest: AgentManifest) -> ReleaseDecision:
    reasons = []
    if not manifest.owner.strip():
        reasons.append("owner is required")
    if manifest.evaluation_score < 0.85:
        reasons.append("evaluation score is below 0.85")
    if not manifest.required_scopes:
        reasons.append("least-privilege scopes are missing")
    if manifest.model_tier not in {"standard", "reasoning"}:
        reasons.append("model tier is not approved")
    status = ReleaseStatus.REJECTED if reasons else ReleaseStatus.APPROVED
    return ReleaseDecision(status=status, reasons=tuple(reasons) or ("all release gates passed",))


def main() -> None:
    registry = AgentRegistry()
    manifests = [
        AgentManifest(
            name="finance-analysis-agent",
            version="1.2.0",
            owner="data-platform",
            capabilities=("analyze_revenue", "explain_variance"),
            required_scopes=("warehouse:read",),
            model_tier="reasoning",
            evaluation_score=0.93,
            estimated_cost=0.18,
        ),
        AgentManifest(
            name="experimental-agent",
            version="0.1.0",
            owner="lab",
            capabilities=("analyze_revenue",),
            required_scopes=("warehouse:admin",),
            model_tier="unreviewed",
            evaluation_score=0.72,
            estimated_cost=0.09,
        ),
    ]

    audit_log = []
    for manifest in manifests:
        decision = evaluate_release(manifest)
        audit_log.append({"agent": manifest.name, "decision": asdict(decision)})
        if decision.status is ReleaseStatus.APPROVED:
            registry.publish(manifest, decision)

    task = TaskEnvelope(
        task_id="task-2026-001",
        tenant="north-region",
        capability="analyze_revenue",
        granted_scopes=("warehouse:read",),
        cost_budget=0.25,
    )
    selected = registry.route(task)
    print(json.dumps({
        "published": sorted(registry.releases),
        "release_audit": audit_log,
        "task": asdict(task),
        "route": f"{selected.name}:{selected.version}",
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
