"""FastAPI transport for the SQL Agent reference application."""

from __future__ import annotations

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from sql_agent.application import build_application


class RunRequest(BaseModel):
    objective: str = Field(min_length=3)
    tenant_id: str = "demo"
    actor_id: str = "api-user"


app = FastAPI(title="AI Agent Engineering SQL Agent", version="0.1.0")
application = build_application()


@app.get("/healthz")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/readyz")
def readiness() -> dict[str, str]:
    return {"status": "ready"}


@app.post("/runs")
def create_run(payload: RunRequest) -> dict:
    try:
        response = application.ask(
            payload.objective,
            tenant_id=payload.tenant_id,
            actor_id=payload.actor_id,
        )
        return response.model_dump(mode="json")
    except (PermissionError, ValueError, RuntimeError, LookupError) as error:
        raise HTTPException(status_code=400, detail=str(error)) from error


@app.get("/runs/{run_id}/trace")
def get_trace(run_id: str) -> list[dict]:
    events = application.runtime.trace.list_run(run_id)
    if not events:
        raise HTTPException(status_code=404, detail="run not found")
    return [event.model_dump(mode="json") for event in events]
