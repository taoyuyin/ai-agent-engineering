"""Deterministic SQL planner used as an offline reference model adapter."""

from __future__ import annotations

import re

from framework import AgentRequest, ExecutionPlan, Goal, PlanStep, ToolCall


class SQLPlanner:
    region_aliases = {
        "华东": "east",
        "华南": "south",
        "华北": "north",
        "east": "east",
        "south": "south",
        "north": "north",
    }

    def create_plan(self, request: AgentRequest, goal: Goal) -> ExecutionPlan:
        query, parameters = self._compile_query(goal.objective)
        return ExecutionPlan(
            steps=(
                PlanStep(
                    step_id="discover-schema",
                    title="Retrieve governed schema and metric definitions",
                    call=ToolCall(
                        name="schema.search",
                        arguments={"query": goal.objective},
                    ),
                    required_scopes=frozenset({"schema:read"}),
                ),
                PlanStep(
                    step_id="query-database",
                    title="Execute authorized read-only analytical SQL",
                    call=ToolCall(
                        name="sql.query",
                        arguments={"sql": query, "parameters": parameters},
                    ),
                    depends_on=("discover-schema",),
                    required_scopes=frozenset({"sales:read"}),
                ),
            )
        )

    def _compile_query(self, objective: str) -> tuple[str, list[str]]:
        lowered = objective.lower()
        if not any(term in lowered for term in ("销售", "收入", "sales", "revenue")):
            raise ValueError("MVP currently supports sales and net revenue questions")

        year_match = re.search(r"(20\d{2})", objective)
        year = int(year_match.group(1)) if year_match else 2025
        parameters: list[str] = [f"{year}-01-01", f"{year + 1}-01-01"]

        filters = ["order_date >= ?", "order_date < ?"]
        for alias, region in self.region_aliases.items():
            if alias in lowered:
                filters.append("region = ?")
                parameters.append(region)
                break

        where_clause = " AND ".join(filters)
        sql = f"""
SELECT
    region,
    ROUND(SUM(net_revenue), 2) AS net_revenue,
    COUNT(DISTINCT order_id) AS order_count
FROM sales_orders
WHERE {where_clause}
GROUP BY region
ORDER BY net_revenue DESC
LIMIT 100
""".strip()
        return sql, parameters
