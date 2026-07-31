"""SQL execution policy for the MVP.

Production systems should additionally parse an AST and apply database-native
row/column security. String validation is intentionally a first boundary, not
the final security claim.
"""

from __future__ import annotations

import re


class ReadOnlySQLPolicy:
    forbidden = re.compile(
        r"\b(insert|update|delete|drop|alter|create|attach|detach|pragma|vacuum|replace)\b",
        re.IGNORECASE,
    )
    table_reference = re.compile(r"\b(?:from|join)\s+([a-zA-Z_][a-zA-Z0-9_]*)", re.IGNORECASE)

    def __init__(self, allowed_tables: frozenset[str], max_limit: int = 200) -> None:
        self.allowed_tables = allowed_tables
        self.max_limit = max_limit

    def validate(self, sql: str) -> str:
        normalized = sql.strip().rstrip(";").strip()
        if not normalized:
            raise ValueError("SQL is empty")
        if ";" in normalized:
            raise ValueError("only one SQL statement is allowed")
        if not re.match(r"^(select|with)\b", normalized, re.IGNORECASE):
            raise ValueError("only SELECT or WITH queries are allowed")
        if self.forbidden.search(normalized):
            raise ValueError("SQL contains a forbidden operation")

        referenced_tables = {name.lower() for name in self.table_reference.findall(normalized)}
        unknown_tables = referenced_tables - self.allowed_tables
        if unknown_tables:
            raise ValueError("table is outside allowlist: {}".format(", ".join(unknown_tables)))

        limit_match = re.search(r"\blimit\s+(\d+)\b", normalized, re.IGNORECASE)
        if limit_match and int(limit_match.group(1)) > self.max_limit:
            raise ValueError(f"LIMIT exceeds maximum {self.max_limit}")
        if not limit_match:
            normalized = f"{normalized}\nLIMIT {self.max_limit}"
        return normalized
