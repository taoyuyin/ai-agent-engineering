"""Chapter 51: an offline scheduler for Agent OS workloads."""

from dataclasses import asdict, dataclass
import json


@dataclass(frozen=True)
class Workload:
    run_id: str
    tenant: str
    priority: int
    required_capabilities: tuple[str, ...]
    required_region: str
    model_tier: str
    token_budget: int
    cost_budget: float


@dataclass
class RuntimeNode:
    name: str
    region: str
    capabilities: tuple[str, ...]
    model_tiers: tuple[str, ...]
    token_capacity: int
    available_tokens: int
    cost_per_1k_tokens: float
    latency_ms: int


@dataclass(frozen=True)
class Placement:
    run_id: str
    node: str
    score: float
    reserved_tokens: int
    estimated_cost: float
    capability_token: str


class Scheduler:
    def schedule(self, workload: Workload, nodes: list[RuntimeNode]) -> Placement:
        feasible = []
        required = set(workload.required_capabilities)
        for node in nodes:
            estimated_cost = workload.token_budget / 1000 * node.cost_per_1k_tokens
            if node.region != workload.required_region:
                continue
            if workload.model_tier not in node.model_tiers:
                continue
            if not required.issubset(node.capabilities):
                continue
            if node.available_tokens < workload.token_budget:
                continue
            if estimated_cost > workload.cost_budget:
                continue
            score = workload.priority * 10 - node.latency_ms / 20 - estimated_cost * 10
            feasible.append((score, estimated_cost, node))

        if not feasible:
            raise RuntimeError("no node satisfies region, capability, resource and budget constraints")

        score, estimated_cost, node = max(feasible, key=lambda item: item[0])
        node.available_tokens -= workload.token_budget
        token = f"cap:{workload.tenant}:{workload.run_id}:{','.join(workload.required_capabilities)}"
        return Placement(
            run_id=workload.run_id,
            node=node.name,
            score=round(score, 2),
            reserved_tokens=workload.token_budget,
            estimated_cost=round(estimated_cost, 4),
            capability_token=token,
        )


def main() -> None:
    nodes = [
        RuntimeNode("runtime-cn-a", "cn", ("browser", "retrieval"), ("standard",), 100_000, 50_000, 0.008, 140),
        RuntimeNode("runtime-cn-b", "cn", ("browser", "retrieval", "code"), ("standard", "reasoning"), 80_000, 30_000, 0.015, 90),
        RuntimeNode("runtime-us-a", "us", ("browser", "retrieval", "code"), ("reasoning",), 150_000, 90_000, 0.012, 60),
    ]
    workload = Workload(
        run_id="run-51-001",
        tenant="manufacturing",
        priority=8,
        required_capabilities=("retrieval", "code"),
        required_region="cn",
        model_tier="reasoning",
        token_budget=12_000,
        cost_budget=0.25,
    )
    placement = Scheduler().schedule(workload, nodes)
    print(json.dumps({
        "state_transitions": ["queued", "scheduled", "running"],
        "workload": asdict(workload),
        "placement": asdict(placement),
        "remaining_tokens": {node.name: node.available_tokens for node in nodes},
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
