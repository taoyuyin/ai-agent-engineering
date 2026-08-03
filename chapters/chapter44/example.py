"""Chapter 44: a semantic-layer-first BI Agent MVP."""

from __future__ import annotations

import json
from dataclasses import dataclass
from sys import argv


FACTS = [
    {"month": "2025-01", "region": "east", "gross": 180000.0, "refund": 8000.0, "orders": 172},
    {"month": "2025-02", "region": "east", "gross": 176000.0, "refund": 10000.0, "orders": 165},
    {"month": "2025-01", "region": "north", "gross": 151000.0, "refund": 7000.0, "orders": 140},
    {"month": "2025-02", "region": "north", "gross": 155000.0, "refund": 6000.0, "orders": 145},
    {"month": "2025-01", "region": "south", "gross": 149000.0, "refund": 5000.0, "orders": 138},
    {"month": "2025-02", "region": "south", "gross": 153000.0, "refund": 5000.0, "orders": 141},
]

METRICS = {
    "net_revenue": {
        "label": "净销售额",
        "unit": "CNY",
        "definition": "sum(gross - refund)",
        "owner": "finance-analytics",
        "version": "metric-v1",
    },
    "order_count": {
        "label": "订单量",
        "unit": "order",
        "definition": "sum(orders)",
        "owner": "sales-ops",
        "version": "metric-v1",
    },
}


@dataclass(frozen=True)
class BIRequest:
    metric: str
    group_by: str
    allowed_regions: frozenset[str]


def metric_value(metric: str, row: dict) -> float:
    return row["gross"] - row["refund"] if metric == "net_revenue" else float(row["orders"])


def execute(request: BIRequest) -> dict:
    if request.metric not in METRICS:
        raise ValueError("metric is not defined in the semantic layer")
    if request.group_by not in {"region", "month"}:
        raise ValueError("dimension is not allowlisted")
    authorized = [row for row in FACTS if row["region"] in request.allowed_regions]
    grouped: dict[str, float] = {}
    for row in authorized:
        key = str(row[request.group_by])
        grouped[key] = grouped.get(key, 0.0) + metric_value(request.metric, row)
    results = [
        {request.group_by: key, request.metric: round(value, 2)}
        for key, value in sorted(grouped.items(), key=lambda item: item[1], reverse=True)
    ]
    top = results[0] if results else None
    return {
        "status": "completed",
        "semantic_metric": {"name": request.metric, **METRICS[request.metric]},
        "query": {"group_by": request.group_by, "authorized_regions": sorted(request.allowed_regions)},
        "results": results,
        "insight": f"Top {request.group_by}: {top}" if top else "No authorized data.",
        "dashboard_spec": {
            "title": METRICS[request.metric]["label"],
            "visual": "bar",
            "category": request.group_by,
            "measure": request.metric,
            "drilldown_dimensions": ["month", "region"],
        },
        "evidence": {"source": "demo.sales_mart", "visible_row_count": len(authorized)},
    }


def main() -> None:
    metric = argv[1] if len(argv) > 1 else "net_revenue"
    group_by = argv[2] if len(argv) > 2 else "region"
    result = execute(BIRequest(metric, group_by, frozenset({"east", "north"})))
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
