from dataclasses import dataclass, replace
from hashlib import sha256
from math import sqrt
from typing import Dict, List, Tuple
import re


MEMORY_TYPES = {"working", "episodic", "semantic", "procedural"}
EMBEDDING_MODEL = "hash-embedding-v1"


def _tokens(text: str) -> List[str]:
    return re.findall(r"[a-z0-9_]+|[\u4e00-\u9fff]", text.lower())


def _embed(text: str, dimensions: int = 64) -> Tuple[float, ...]:
    vector = [0.0] * dimensions
    for token in _tokens(text):
        digest = sha256(token.encode("utf-8")).digest()
        index = int.from_bytes(digest[:2], "big") % dimensions
        vector[index] += 1.0 if digest[2] % 2 else -1.0
    norm = sqrt(sum(value * value for value in vector)) or 1.0
    return tuple(value / norm for value in vector)


def _cosine(left: Tuple[float, ...], right: Tuple[float, ...]) -> float:
    return sum(a * b for a, b in zip(left, right))


@dataclass(frozen=True)
class MemoryRecord:
    memory_id: str
    tenant_id: str
    subject_id: str
    memory_type: str
    content: str
    confidence: float
    version: int = 1
    embedding_model: str = EMBEDDING_MODEL


class MemoryStore:
    def __init__(self) -> None:
        self._records = {}  # type: Dict[Tuple[str, str, str], MemoryRecord]
        self._vectors = {}  # type: Dict[Tuple[str, str, str], Tuple[float, ...]]

    def put(self, record: MemoryRecord) -> None:
        if record.memory_type not in MEMORY_TYPES:
            raise ValueError("unsupported memory type")
        if not 0 <= record.confidence <= 1:
            raise ValueError("confidence must be between zero and one")
        key = (record.tenant_id, record.subject_id, record.memory_id)
        previous = self._records.get(key)
        if previous:
            record = replace(record, version=previous.version + 1)
        self._records[key] = record
        self._vectors[key] = _embed(record.content)

    def search(self, tenant_id: str, subject_id: str, query: str, limit: int = 5) -> List[MemoryRecord]:
        terms = set(query.lower().split())
        query_vector = _embed(query)
        candidates = []
        for key, record in self._records.items():
            tenant, subject, _ = key
            if (tenant, subject) != (tenant_id, subject_id):
                continue
            overlap = sum(1 for term in terms if term in record.content.lower())
            semantic = _cosine(query_vector, self._vectors[key])
            score = overlap + max(0.0, semantic) * 2 + record.confidence
            candidates.append((score, record))
        return [item[1] for item in sorted(candidates, key=lambda item: (-item[0], item[1].memory_id))[:limit]]

    def forget(self, tenant_id: str, subject_id: str, memory_id: str) -> None:
        key = (tenant_id, subject_id, memory_id)
        self._records.pop(key, None)
        self._vectors.pop(key, None)
