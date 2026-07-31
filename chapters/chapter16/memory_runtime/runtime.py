from dataclasses import dataclass, replace
from typing import Dict, List, Tuple


MEMORY_TYPES = {"working", "episodic", "semantic", "procedural"}


@dataclass(frozen=True)
class MemoryRecord:
    memory_id: str
    tenant_id: str
    subject_id: str
    memory_type: str
    content: str
    confidence: float
    version: int = 1


class MemoryStore:
    def __init__(self) -> None:
        self._records = {}  # type: Dict[Tuple[str, str, str], MemoryRecord]

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

    def search(self, tenant_id: str, subject_id: str, query: str, limit: int = 5) -> List[MemoryRecord]:
        terms = set(query.lower().split())
        candidates = []
        for (tenant, subject, _), record in self._records.items():
            if (tenant, subject) != (tenant_id, subject_id):
                continue
            overlap = sum(1 for term in terms if term in record.content.lower())
            score = overlap + record.confidence
            candidates.append((score, record))
        return [item[1] for item in sorted(candidates, key=lambda item: (-item[0], item[1].memory_id))[:limit]]

    def forget(self, tenant_id: str, subject_id: str, memory_id: str) -> None:
        self._records.pop((tenant_id, subject_id, memory_id), None)
