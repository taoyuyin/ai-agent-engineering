"""Tenant-isolated memory port and in-memory reference adapter."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4


@dataclass(frozen=True)
class MemoryRecord:
    tenant_id: str
    run_id: str
    kind: str
    content: str
    metadata: dict[str, Any] = field(default_factory=dict)
    record_id: str = field(default_factory=lambda: str(uuid4()))
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class InMemoryStore:
    """Reference adapter; replace with PostgreSQL/vector storage in production."""

    def __init__(self) -> None:
        self._records: list[MemoryRecord] = []

    def append(self, record: MemoryRecord) -> None:
        if not record.tenant_id:
            raise ValueError("tenant_id is required")
        self._records.append(record)

    def list_run(self, tenant_id: str, run_id: str) -> tuple[MemoryRecord, ...]:
        return tuple(
            record
            for record in self._records
            if record.tenant_id == tenant_id and record.run_id == run_id
        )
