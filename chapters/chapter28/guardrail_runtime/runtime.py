"""Layered deterministic guardrails around an untrusted model."""

from dataclasses import dataclass
from typing import Dict, Mapping, Optional, Set
import re


@dataclass(frozen=True)
class ToolProposal:
    tool_name: str
    arguments: Mapping[str, object]


@dataclass(frozen=True)
class Decision:
    action: str
    reason: str
    value: Optional[object] = None


class GuardrailPipeline:
    INJECTION_PATTERNS = (
        re.compile(r"ignore (all|previous) instructions", re.I),
        re.compile(r"忽略.{0,8}(之前|系统|以上).{0,8}(指令|提示)", re.I),
        re.compile(r"reveal.{0,8}(system prompt|secret)", re.I),
    )

    def __init__(self, allowed_tools: Set[str], sensitive_fields: Set[str]) -> None:
        self.allowed_tools = set(allowed_tools)
        self.sensitive_fields = set(sensitive_fields)
        self.audit = []

    def _record(self, stage: str, decision: Decision) -> Decision:
        self.audit.append({"stage": stage, "action": decision.action, "reason": decision.reason})
        return decision

    def check_input(self, text: str) -> Decision:
        if any(pattern.search(text) for pattern in self.INJECTION_PATTERNS):
            return self._record("input", Decision("block", "suspected prompt injection"))
        return self._record("input", Decision("allow", "input policy passed", text))

    def check_context(self, text: str, source: str) -> Decision:
        if not source:
            return self._record("context", Decision("block", "context lacks provenance"))
        cleaned = "\n".join(
            line for line in text.splitlines() if not any(p.search(line) for p in self.INJECTION_PATTERNS)
        )
        action = "transform" if cleaned != text else "allow"
        return self._record("context", Decision(action, "untrusted instructions removed", cleaned))

    def check_tool(self, proposal: ToolProposal) -> Decision:
        if proposal.tool_name not in self.allowed_tools:
            return self._record("tool", Decision("block", "tool is outside actor scope"))
        if any(key.lower() in {"shell", "sql", "command"} for key in proposal.arguments):
            return self._record("tool", Decision("review", "high-risk raw command argument"))
        return self._record("tool", Decision("allow", "tool policy passed", proposal))

    def check_output(self, output: Mapping[str, object]) -> Decision:
        if "answer" not in output:
            return self._record("output", Decision("block", "required answer field is missing"))
        redacted: Dict[str, object] = dict(output)
        changed = False
        for field in self.sensitive_fields:
            if field in redacted:
                redacted[field] = "[REDACTED]"
                changed = True
        return self._record(
            "output",
            Decision("transform" if changed else "allow", "output schema and DLP passed", redacted),
        )
