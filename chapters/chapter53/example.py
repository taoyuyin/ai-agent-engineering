"""Chapter 53: an offline goal-to-capability planner for AI Native software."""

from dataclasses import asdict, dataclass
import json


@dataclass(frozen=True)
class Goal:
    text: str
    budget: float
    constraints: tuple[str, ...]


@dataclass(frozen=True)
class Capability:
    name: str
    produces: str
    requires: tuple[str, ...]
    cost: float
    side_effect: bool = False


@dataclass(frozen=True)
class PlanStep:
    capability: str
    produces: str
    approval_required: bool


class CapabilityPlanner:
    def __init__(self, capabilities: list[Capability]) -> None:
        self.capabilities = capabilities

    def compile(self, goal: Goal, desired_outputs: tuple[str, ...]) -> list[PlanStep]:
        produced = {"goal"}
        plan = []
        targets = set(desired_outputs)
        needed_outputs = set(targets)
        changed = True
        while changed:
            changed = False
            for capability in self.capabilities:
                if capability.produces not in needed_outputs:
                    continue
                for requirement in capability.requires:
                    if requirement != "goal" and requirement not in needed_outputs:
                        needed_outputs.add(requirement)
                        changed = True
        spent = 0.0
        while not targets.issubset(produced):
            candidates = [
                capability for capability in self.capabilities
                if capability.produces in needed_outputs
                and capability.produces not in produced
                and set(capability.requires).issubset(produced)
            ]
            if not candidates:
                missing = sorted(targets - produced)
                raise RuntimeError(f"cannot satisfy outputs: {missing}")
            selected = min(candidates, key=lambda item: item.cost)
            spent += selected.cost
            if spent > goal.budget:
                raise RuntimeError("goal exceeds the declared cost budget")
            plan.append(PlanStep(selected.name, selected.produces, selected.side_effect))
            produced.add(selected.produces)
        return plan


def main() -> None:
    goal = Goal(
        text="为华东工厂选择三家备件供应商并生成询价草案",
        budget=1.00,
        constraints=("只使用合格供应商", "不自动发送询价"),
    )
    capabilities = [
        Capability("retrieve_approved_suppliers", "supplier_list", ("goal",), 0.12),
        Capability("compare_price_and_risk", "comparison", ("supplier_list",), 0.25),
        Capability("draft_request_for_quote", "rfq_draft", ("comparison",), 0.18),
        Capability("send_request_for_quote", "rfq_sent", ("rfq_draft",), 0.05, side_effect=True),
    ]
    plan = CapabilityPlanner(capabilities).compile(goal, ("rfq_draft",))
    ui_projection = [
        {"type": "progress", "label": step.capability, "status": "pending"}
        for step in plan
    ]
    print(json.dumps({
        "goal": asdict(goal),
        "plan": [asdict(step) for step in plan],
        "adaptive_ui": ui_projection,
        "invariant": "deterministic services enforce scope, budget and approval",
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
