"""Chapter 42: a governed, evidence-producing SQL Agent MVP."""

from __future__ import annotations

import json
import re
import sqlite3
from dataclasses import dataclass
from sys import argv


@dataclass(frozen=True)
class RequestContext:
    tenant_id: str
    actor_id: str
    scopes: frozenset[str]


@dataclass(frozen=True)
class QueryPlan:
    metric: str
    year: int
    region: str | None
    sql: str
    parameters: tuple[object, ...]


METRICS = {
    "net_revenue": {
        "label": "净销售额",
        "expression": "SUM(gross_amount - refund_amount)",
        "unit": "CNY",
        "version": "sales-metrics-v1",
    }
}
REGION_ALIASES = {"华东": "east", "华北": "north", "华南": "south"}


def create_database() -> sqlite3.Connection:
    connection = sqlite3.connect(":memory:")
    connection.row_factory = sqlite3.Row
    connection.executescript(
        """
        CREATE TABLE sales_orders (
            tenant_id TEXT NOT NULL,
            order_id TEXT PRIMARY KEY,
            order_year INTEGER NOT NULL,
            region TEXT NOT NULL,
            gross_amount REAL NOT NULL,
            refund_amount REAL NOT NULL
        );
        INSERT INTO sales_orders VALUES
          ('demo', 'o-001', 2025, 'east', 200000, 12000),
          ('demo', 'o-002', 2025, 'east', 160000, 10000),
          ('demo', 'o-003', 2025, 'north', 155000, 6000),
          ('demo', 'o-004', 2025, 'south', 152000, 4000),
          ('other', 'o-005', 2025, 'east', 999999, 0);
        """
    )
    return connection


def understand(question: str) -> tuple[int, str | None]:
    year_match = re.search(r"\b(20\d{2})\b", question)
    year = int(year_match.group(1)) if year_match else 2025
    region = next((code for name, code in REGION_ALIASES.items() if name in question), None)
    return year, region


def build_plan(question: str, context: RequestContext) -> QueryPlan:
    if "sales:read" not in context.scopes:
        raise PermissionError("sales:read scope is required")
    year, region = understand(question)
    metric = METRICS["net_revenue"]
    sql = (
        "SELECT region, " + metric["expression"] + " AS net_revenue, COUNT(*) AS order_count "
        "FROM sales_orders WHERE tenant_id = ? AND order_year = ?"
    )
    parameters: list[object] = [context.tenant_id, year]
    if region:
        sql += " AND region = ?"
        parameters.append(region)
    sql += " GROUP BY region ORDER BY net_revenue DESC LIMIT 20"
    return QueryPlan("net_revenue", year, region, sql, tuple(parameters))


def validate_plan(plan: QueryPlan) -> None:
    normalized = " ".join(plan.sql.lower().split())
    forbidden = (" insert ", " update ", " delete ", " drop ", " alter ", ";")
    if not normalized.startswith("select ") or any(token in f" {normalized} " for token in forbidden):
        raise ValueError("only one read-only SELECT statement is allowed")
    if " from sales_orders " not in f" {normalized} ":
        raise ValueError("query references a non-allowlisted table")
    if "tenant_id = ?" not in normalized:
        raise ValueError("tenant predicate is mandatory")
    if plan.metric not in METRICS:
        raise ValueError("unknown semantic metric")


def run_agent(question: str, context: RequestContext) -> dict:
    plan = build_plan(question, context)
    validate_plan(plan)
    connection = create_database()
    try:
        rows = [dict(row) for row in connection.execute(plan.sql, plan.parameters)]
    finally:
        connection.close()
    metric = METRICS[plan.metric]
    return {
        "status": "completed",
        "question": question,
        "metric": {"name": plan.metric, **metric},
        "filters": {"tenant_id": context.tenant_id, "year": plan.year, "region": plan.region},
        "rows": rows,
        "evidence": {
            "source": "sqlite.sales_orders",
            "sql": plan.sql,
            "parameters": list(plan.parameters),
            "row_count": len(rows),
        },
        "audit": {"actor_id": context.actor_id, "scopes": sorted(context.scopes)},
    }


def main() -> None:
    question = " ".join(argv[1:]) or "查询 2025 年各区域净销售额"
    report = run_agent(
        question,
        RequestContext("demo", "engineer-001", frozenset({"sales:read"})),
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
