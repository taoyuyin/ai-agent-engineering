"""A production-shaped Agent service boundary with health and run resources."""

from threading import Lock
from typing import Dict, Mapping
from uuid import uuid4


class AgentService:
    def __init__(self, model_endpoint: str, max_request_chars: int = 10000) -> None:
        if not model_endpoint:
            raise ValueError("MODEL_ENDPOINT is required")
        self.model_endpoint = model_endpoint
        self.max_request_chars = max_request_chars
        self._ready = False
        self._accepting = True
        self._runs: Dict[str, Dict[str, object]] = {}
        self._lock = Lock()

    def mark_ready(self) -> None:
        self._ready = True

    def health(self) -> Mapping[str, object]:
        return {"live": True, "ready": self._ready and self._accepting}

    def create_run(self, request: Mapping[str, object]) -> Mapping[str, object]:
        if not self._ready or not self._accepting:
            raise RuntimeError("service is not ready")
        tenant_id = request.get("tenant_id")
        goal = request.get("goal")
        if not isinstance(tenant_id, str) or not tenant_id:
            raise ValueError("tenant_id is required")
        if not isinstance(goal, str) or not goal or len(goal) > self.max_request_chars:
            raise ValueError("goal is invalid")
        run_id = uuid4().hex
        run = {
            "run_id": run_id,
            "tenant_id": tenant_id,
            "status": "queued",
            "goal": goal,
        }
        with self._lock:
            self._runs[run_id] = run
        return dict(run)

    def get_run(self, run_id: str) -> Mapping[str, object]:
        with self._lock:
            if run_id not in self._runs:
                raise KeyError("run not found")
            return dict(self._runs[run_id])

    def begin_shutdown(self) -> None:
        self._accepting = False
        self._ready = False
