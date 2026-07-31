"""Grounded answer synthesis from normalized observations."""

from __future__ import annotations

from collections.abc import Sequence

from framework import AgentRequest, Goal, ToolObservation
from framework.contracts import Evidence


class SQLAnswerSynthesizer:
    region_labels = {"east": "华东", "south": "华南", "north": "华北"}

    def synthesize(
        self,
        request: AgentRequest,
        goal: Goal,
        observations: Sequence[ToolObservation],
    ) -> tuple[str, tuple[Evidence, ...]]:
        query_observation = next(item for item in observations if item.tool_name == "sql.query")
        result = query_observation.data
        rows = result["rows"]

        if not rows:
            answer = "在当前授权数据和筛选条件下没有查询到记录。"
        else:
            lines = [
                "- {}：净销售额 {:,.2f} CNY，订单 {} 笔".format(
                    self.region_labels.get(row["region"], row["region"]),
                    row["net_revenue"],
                    row["order_count"],
                )
                for row in rows
            ]
            answer = "查询结果如下：\n" + "\n".join(lines)

        evidence = (
            Evidence(
                source="sqlite.sales_orders",
                value=rows,
                metadata={
                    "sql": result["sql"],
                    "parameters": result["parameters"],
                    "row_count": result["row_count"],
                },
            ),
        )
        return answer, evidence
