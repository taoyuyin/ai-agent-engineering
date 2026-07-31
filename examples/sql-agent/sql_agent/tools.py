"""Business tools exposed to the generic Agent Runtime."""

from __future__ import annotations

from sqlite3 import DatabaseError
from typing import Any

from pydantic import BaseModel, Field

from framework.contracts import ToolRisk
from framework.tools import ToolDefinition, ToolRegistry
from sql_agent.database import SalesDatabase
from sql_agent.guardrails import ReadOnlySQLPolicy


class SearchSchemaInput(BaseModel):
    query: str = Field(min_length=2)


class ExecuteSQLInput(BaseModel):
    sql: str = Field(min_length=6)
    parameters: list[Any] = Field(default_factory=list)


class SQLAgentTools:
    catalog = {
        "sales_orders": {
            "description": "Sales orders at order grain.",
            "columns": {
                "order_id": "Unique order identifier.",
                "order_date": "Order date in ISO-8601 format.",
                "region": "Business region: east, south or north.",
                "customer_name": "Customer display name.",
                "product": "Product name.",
                "quantity": "Sold units.",
                "net_revenue": "Revenue after discount, in CNY.",
            },
            "metric": "net_revenue = SUM(sales_orders.net_revenue)",
        }
    }

    def __init__(self, database: SalesDatabase) -> None:
        self.database = database
        self.sql_policy = ReadOnlySQLPolicy(frozenset(self.catalog))

    def search_schema(self, value: SearchSchemaInput) -> dict[str, Any]:
        query = value.query.lower()
        selected = {
            name: metadata
            for name, metadata in self.catalog.items()
            if any(
                term in query
                for term in ("销售", "收入", "订单", "sales", "revenue", "order")
            )
        }
        return {"query": value.query, "tables": selected or self.catalog}

    def execute_sql(self, value: ExecuteSQLInput) -> dict[str, Any]:
        safe_sql = self.sql_policy.validate(value.sql)
        connection = self.database.read_only_connection()
        try:
            try:
                rows = connection.execute(safe_sql, value.parameters).fetchall()
            except DatabaseError as error:
                raise RuntimeError(f"database query failed: {error}") from error
            return {
                "sql": safe_sql,
                "parameters": value.parameters,
                "row_count": len(rows),
                "rows": rows,
            }
        finally:
            connection.close()

    def registry(self) -> ToolRegistry:
        registry = ToolRegistry()
        registry.register(
            ToolDefinition(
                name="schema.search",
                description="Retrieve governed tables, columns and metric definitions.",
                input_model=SearchSchemaInput,
                handler=self.search_schema,
                required_scopes=frozenset({"schema:read"}),
                risk=ToolRisk.READ,
            )
        )
        registry.register(
            ToolDefinition(
                name="sql.query",
                description="Execute one parameterized, read-only SQL query.",
                input_model=ExecuteSQLInput,
                handler=self.execute_sql,
                required_scopes=frozenset({"sales:read"}),
                risk=ToolRisk.READ,
            )
        )
        return registry
