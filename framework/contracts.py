"""Stable contracts shared by the Runtime and business Agent implementations."""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class RunStatus(str, Enum):
    ACCEPTED = "accepted"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class StepStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class ToolRisk(str, Enum):
    READ = "read"
    WRITE = "write"
    PRIVILEGED = "privileged"


class AgentRequest(BaseModel):
    model_config = ConfigDict(frozen=True)

    run_id: str = Field(default_factory=lambda: str(uuid4()))
    tenant_id: str = Field(min_length=1)
    actor_id: str = Field(min_length=1)
    objective: str = Field(min_length=3)
    scopes: frozenset[str] = Field(default_factory=frozenset)
    max_steps: int = Field(default=8, ge=1, le=64)
    max_retries: int = Field(default=1, ge=0, le=5)
    context_token_budget: int = Field(default=1600, ge=128, le=128_000)
    metadata: dict[str, str] = Field(default_factory=dict)


class Goal(BaseModel):
    model_config = ConfigDict(frozen=True)

    objective: str
    success_criteria: tuple[str, ...]
    constraints: dict[str, Any] = Field(default_factory=dict)


class ToolCall(BaseModel):
    model_config = ConfigDict(frozen=True)

    name: str
    arguments: dict[str, Any] = Field(default_factory=dict)


class PlanStep(BaseModel):
    model_config = ConfigDict(frozen=True)

    step_id: str
    title: str
    call: ToolCall
    depends_on: tuple[str, ...] = ()
    required_scopes: frozenset[str] = Field(default_factory=frozenset)
    max_retries: int | None = Field(default=None, ge=0, le=5)


class ExecutionPlan(BaseModel):
    model_config = ConfigDict(frozen=True)

    plan_id: str = Field(default_factory=lambda: str(uuid4()))
    steps: tuple[PlanStep, ...]


class ToolObservation(BaseModel):
    model_config = ConfigDict(frozen=True)

    step_id: str
    tool_name: str
    status: StepStatus
    data: Any = None
    error: str | None = None
    duration_ms: float = 0
    attempt: int = 1


class Evidence(BaseModel):
    model_config = ConfigDict(frozen=True)

    source: str
    value: Any
    metadata: dict[str, Any] = Field(default_factory=dict)


class AgentResponse(BaseModel):
    model_config = ConfigDict(frozen=True)

    run_id: str
    status: RunStatus
    answer: str
    observations: tuple[ToolObservation, ...]
    evidence: tuple[Evidence, ...] = ()
    started_at: datetime
    completed_at: datetime = Field(default_factory=utc_now)


class TraceEvent(BaseModel):
    model_config = ConfigDict(frozen=True)

    sequence: int
    run_id: str
    event_type: str
    timestamp: datetime = Field(default_factory=utc_now)
    attributes: dict[str, Any] = Field(default_factory=dict)
