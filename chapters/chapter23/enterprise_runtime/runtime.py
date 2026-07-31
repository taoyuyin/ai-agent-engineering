"""Composition root showing how Part II capabilities enter an Agent Runtime."""

from dataclasses import dataclass
from hashlib import sha256
from math import sqrt
from typing import Dict, List, Tuple
import re


def _tokens(text: str) -> List[str]:
    return re.findall(r"[a-z0-9_]+|[\u4e00-\u9fff]", text.lower())


@dataclass(frozen=True)
class AgentRequest:
    run_id: str
    tenant_id: str
    actor_id: str
    objective: str
    scopes: Tuple[str, ...]
    max_context_tokens: int = 120


@dataclass(frozen=True)
class RetrievalRecord:
    record_id: str
    tenant_id: str
    content: str
    source: str


class AuditSink:
    def __init__(self) -> None:
        self.events = []  # type: List[Dict[str, str]]

    def emit(self, run_id: str, event: str, outcome: str) -> None:
        self.events.append({"run_id": run_id, "event": event, "outcome": outcome})


class PolicyEnforcer:
    def authorize(self, request: AgentRequest, required_scope: str) -> None:
        if not request.tenant_id or required_scope not in request.scopes:
            raise PermissionError("request is outside the policy boundary")


class EmbeddingGateway:
    """A deterministic teaching model; production uses a versioned embedding API."""

    model = "hash-embedding-v1"

    def encode(self, text: str, dimensions: int = 64) -> Tuple[float, ...]:
        vector = [0.0] * dimensions
        for token in _tokens(text):
            digest = sha256(token.encode("utf-8")).digest()
            index = int.from_bytes(digest[:2], "big") % dimensions
            vector[index] += 1.0
        norm = sqrt(sum(value * value for value in vector)) or 1.0
        return tuple(value / norm for value in vector)


class RetrievalService:
    def __init__(self, embedding: EmbeddingGateway, records: List[RetrievalRecord]) -> None:
        self.embedding = embedding
        self.records = records
        self.vectors = {
            record.record_id: embedding.encode(record.content) for record in records
        }

    def search(self, request: AgentRequest, limit: int = 3) -> List[RetrievalRecord]:
        query = self.embedding.encode(request.objective)
        ranked = []
        for record in self.records:
            if record.tenant_id != request.tenant_id:
                continue
            score = sum(
                left * right for left, right in zip(query, self.vectors[record.record_id])
            )
            ranked.append((score, record.record_id, record))
        ranked.sort(reverse=True)
        return [item[2] for item in ranked[:limit]]


class ContextCompiler:
    def compile(self, records: List[RetrievalRecord], max_tokens: int) -> str:
        selected = []
        used = 0
        for record in records:
            estimated = max(1, len(_tokens(record.content)))
            if used + estimated > max_tokens:
                continue
            selected.append("[{}] {}".format(record.record_id, record.content))
            used += estimated
        return "\n".join(selected)


class ToolGateway:
    def __init__(self) -> None:
        self.sales = {"tenant-a": {"east": 218000}, "tenant-b": {"east": 91000}}

    def query_sales(self, tenant_id: str, region: str) -> int:
        value = self.sales.get(tenant_id, {}).get(region)
        if value is None:
            raise LookupError("tenant data not found")
        return value


class EnterpriseAgentRuntime:
    """Small but complete retrieval → context → tool → evidence composition root."""

    def __init__(self) -> None:
        self.audit = AuditSink()
        self.policy = PolicyEnforcer()
        self.embedding = EmbeddingGateway()
        self.retrieval = RetrievalService(
            self.embedding,
            [
                RetrievalRecord(
                    "metric-net-revenue",
                    "tenant-a",
                    "销售摘要使用净收入指标，区域字段采用 east、south、north。",
                    "semantic_catalog.net_revenue",
                ),
                RetrievalRecord(
                    "policy-read-only",
                    "tenant-a",
                    "经营分析 Agent 只能读取销售数据，不得修改订单。",
                    "policy.sales_agent",
                ),
                RetrievalRecord(
                    "tenant-b-secret",
                    "tenant-b",
                    "tenant-b 的内部经营规则。",
                    "policy.tenant_b",
                ),
            ],
        )
        self.context = ContextCompiler()
        self.tools = ToolGateway()

    def run(self, request: AgentRequest) -> Dict[str, object]:
        self.audit.emit(request.run_id, "run_started", "accepted")
        try:
            self.policy.authorize(request, "sales:read")

            records = self.retrieval.search(request)
            compiled_context = self.context.compile(records, request.max_context_tokens)
            self.audit.emit(
                request.run_id,
                "context_compiled",
                "{}:{}".format(self.embedding.model, len(records)),
            )

            evidence = self.tools.query_sales(request.tenant_id, "east")
            self.audit.emit(request.run_id, "tool_called", "sales_summary")

            response = {
                "run_id": request.run_id,
                "status": "completed",
                "answer": "华东销售额为 {} CNY".format(evidence),
                "context": compiled_context,
                "embedding_model": self.embedding.model,
                "evidence": [
                    {"source": "sales_monthly", "value": evidence},
                    *[
                        {"source": record.source, "record_id": record.record_id}
                        for record in records
                    ],
                ],
            }
            self.audit.emit(request.run_id, "run_completed", "success")
            return response
        except (PermissionError, LookupError) as error:
            self.audit.emit(request.run_id, "run_failed", type(error).__name__)
            raise
