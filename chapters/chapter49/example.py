"""Chapter 49: a governed Multi-Agent platform control-plane MVP."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from sys import argv
from typing import Callable
from uuid import uuid4


@dataclass(frozen=True)
class AgentDescriptor:
    name: str
    version: str
    capabilities: frozenset[str]
    required_scopes: frozenset[str]
    cost_units: int


@dataclass(frozen=True)
class TaskEnvelope:
    task_id: str
    tenant_id: str
    actor_id: str
    objective: str
    scopes: frozenset[str]
    budget_units: int
    max_hops: int = 4


@dataclass
class RunState:
    spent_units: int = 0
    hops: int = 0
    trace: list[dict] = field(default_factory=list)


class AgentRegistry:
    def __init__(self) -> None:
        self._agents: dict[str, tuple[AgentDescriptor, Callable[[TaskEnvelope], dict]]] = {}

    def register(self, descriptor: AgentDescriptor, handler: Callable[[TaskEnvelope], dict]) -> None:
        key = f"{descriptor.name}:{descriptor.version}"
        if key in self._agents:
            raise ValueError(f"duplicate agent version: {key}")
        self._agents[key] = (descriptor, handler)

    def resolve(self, capability: str) -> tuple[AgentDescriptor, Callable[[TaskEnvelope], dict]]:
        candidates = [item for item in self._agents.values() if capability in item[0].capabilities]
        if not candidates:
            raise LookupError(f"no agent provides {capability}")
        return sorted(candidates, key=lambda item: item[0].version, reverse=True)[0]


def sales_handler(task: TaskEnvelope) -> dict:
    return {"metric": "net_revenue", "year": 2025, "value": 635000.0, "source": "sales-mart-v3"}


def policy_handler(task: TaskEnvelope) -> dict:
    return {"policy": "Only aggregated regional sales may be shared.", "source": "data-policy-v2"}


def risk_handler(task: TaskEnvelope) -> dict:
    return {"decision": "allow", "conditions": ["retain evidence", "no customer-level rows"]}


class PlatformRuntime:
    def __init__(self, registry: AgentRegistry) -> None:
        self.registry = registry

    def call(self, capability: str, task: TaskEnvelope, state: RunState) -> dict:
        descriptor, handler = self.registry.resolve(capability)
        if not descriptor.required_scopes.issubset(task.scopes):
            raise PermissionError(f"missing scopes for {descriptor.name}")
        if state.hops + 1 > task.max_hops:
            raise RuntimeError("maximum delegation hops exceeded")
        if state.spent_units + descriptor.cost_units > task.budget_units:
            raise RuntimeError("task budget exceeded")
        state.hops += 1
        state.spent_units += descriptor.cost_units
        result = handler(task)
        state.trace.append(
            {
                "hop": state.hops,
                "agent": descriptor.name,
                "version": descriptor.version,
                "capability": capability,
                "cost_units": descriptor.cost_units,
                "evidence": result.get("source"),
            }
        )
        return result

    def run(self, task: TaskEnvelope) -> dict:
        state = RunState()
        policy = self.call("policy.lookup", task, state)
        data = self.call("sales.aggregate", task, state)
        risk = self.call("risk.review", task, state)
        return {
            "status": "completed" if risk["decision"] == "allow" else "blocked",
            "task": asdict(task) | {"scopes": sorted(task.scopes)},
            "result": {"policy": policy, "data": data, "risk": risk},
            "governance": {"spent_units": state.spent_units, "hops": state.hops},
            "trace": state.trace,
        }


def build_registry() -> AgentRegistry:
    registry = AgentRegistry()
    registry.register(AgentDescriptor("policy-agent", "1.0", frozenset({"policy.lookup"}), frozenset({"policy:read"}), 1), policy_handler)
    registry.register(AgentDescriptor("sales-agent", "2.1", frozenset({"sales.aggregate"}), frozenset({"sales:read"}), 3), sales_handler)
    registry.register(AgentDescriptor("risk-agent", "1.2", frozenset({"risk.review"}), frozenset({"risk:review"}), 2), risk_handler)
    return registry


def main() -> None:
    objective = " ".join(argv[1:]) or "汇总 2025 年销售并检查对外共享策略"
    task = TaskEnvelope(
        str(uuid4()),
        "demo",
        "engineer-001",
        objective,
        frozenset({"policy:read", "sales:read", "risk:review"}),
        budget_units=8,
    )
    print(json.dumps(PlatformRuntime(build_registry()).run(task), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
