"""Environment-backed runtime configuration with explicit defaults."""

from __future__ import annotations

from os import environ
from pathlib import Path

from pydantic import BaseModel, Field


class RuntimeSettings(BaseModel):
    environment: str = "development"
    log_level: str = "INFO"
    database_path: Path = Path("var/sql-agent.db")
    default_max_steps: int = Field(default=8, ge=1, le=64)
    default_max_retries: int = Field(default=1, ge=0, le=5)

    @classmethod
    def from_env(cls) -> "RuntimeSettings":
        return cls(
            environment=environ.get("AGENT_ENV", "development"),
            log_level=environ.get("LOG_LEVEL", "INFO"),
            database_path=Path(environ.get("SQL_AGENT_DATABASE", "var/sql-agent.db")),
            default_max_steps=int(environ.get("AGENT_MAX_STEPS", "8")),
            default_max_retries=int(environ.get("AGENT_MAX_RETRIES", "1")),
        )
