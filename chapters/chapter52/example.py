"""Chapter 52: a safe, offline Computer Use action harness."""

from dataclasses import asdict, dataclass
from enum import Enum
import json
from urllib.parse import urlparse


class Decision(str, Enum):
    ALLOW = "allow"
    CONFIRM = "confirm"
    BLOCK = "block"


@dataclass(frozen=True)
class Observation:
    screen_id: str
    url: str
    visible_text: str
    contains_untrusted_instruction: bool = False


@dataclass(frozen=True)
class Action:
    kind: str
    target: str
    value: str = ""
    sensitive: bool = False


@dataclass(frozen=True)
class PolicyResult:
    decision: Decision
    reason: str


class ComputerPolicy:
    def __init__(self, allowed_domains: set[str]) -> None:
        self.allowed_domains = allowed_domains

    def evaluate(self, observation: Observation, action: Action) -> PolicyResult:
        parsed = urlparse(observation.url)
        if parsed.scheme not in {"https", "about"}:
            return PolicyResult(Decision.BLOCK, "local files and non-HTTPS protocols are forbidden")
        if parsed.hostname and parsed.hostname not in self.allowed_domains:
            return PolicyResult(Decision.BLOCK, "domain is outside the allowlist")
        if observation.contains_untrusted_instruction and action.kind != "screenshot":
            return PolicyResult(Decision.BLOCK, "page instruction is untrusted and cannot authorize actions")
        if action.sensitive and action.kind == "type":
            return PolicyResult(Decision.CONFIRM, "typing sensitive data transmits it to a third party")
        if action.kind in {"submit", "purchase", "delete"}:
            return PolicyResult(Decision.CONFIRM, "external side effect requires approval at execution time")
        if action.kind not in {"screenshot", "click", "type", "scroll"}:
            return PolicyResult(Decision.BLOCK, "unknown action type")
        return PolicyResult(Decision.ALLOW, "action is read-only or reversible")


def main() -> None:
    policy = ComputerPolicy({"travel.example.com"})
    observation = Observation(
        screen_id="screen-003",
        url="https://travel.example.com/checkout",
        visible_text="Flight selected. Enter card number and click Purchase.",
    )
    proposed_actions = [
        Action("screenshot", "viewport"),
        Action("click", "input[name=card_number]"),
        Action("type", "input[name=card_number]", "4111 **** **** 1111", sensitive=True),
        Action("purchase", "button#purchase"),
    ]

    trace = []
    for action in proposed_actions:
        result = policy.evaluate(observation, action)
        trace.append({"action": asdict(action), "policy": asdict(result)})
        if result.decision is not Decision.ALLOW:
            break

    print(json.dumps({
        "observation": asdict(observation),
        "trace": trace,
        "run_status": "waiting_for_human" if trace[-1]["policy"]["decision"] == "confirm" else "stopped",
        "executed_actions": sum(item["policy"]["decision"] == "allow" for item in trace),
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
