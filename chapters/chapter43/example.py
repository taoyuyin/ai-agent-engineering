"""Chapter 43: a data-quality-aware analytical Agent MVP."""

from __future__ import annotations

import json
from dataclasses import dataclass
from statistics import fmean, pstdev
from sys import argv


ROWS = [
    {"month": "2025-01", "region": "east", "revenue": 102000.0, "orders": 101},
    {"month": "2025-02", "region": "east", "revenue": 105000.0, "orders": 104},
    {"month": "2025-03", "region": "east", "revenue": 109000.0, "orders": 108},
    {"month": "2025-04", "region": "east", "revenue": 108000.0, "orders": 107},
    {"month": "2025-05", "region": "east", "revenue": 112000.0, "orders": 110},
    {"month": "2025-06", "region": "east", "revenue": 151000.0, "orders": 116},
]


@dataclass(frozen=True)
class AnalysisRequest:
    metric: str
    region: str
    scopes: frozenset[str]


def validate_data(rows: list[dict]) -> dict:
    required = {"month", "region", "revenue", "orders"}
    missing_cells = sum(value is None for row in rows for value in row.values())
    invalid_rows = [index for index, row in enumerate(rows) if set(row) != required]
    duplicate_keys = len(rows) - len({(row["month"], row["region"]) for row in rows})
    return {
        "passed": not missing_cells and not invalid_rows and not duplicate_keys,
        "row_count": len(rows),
        "missing_cells": missing_cells,
        "invalid_schema_rows": invalid_rows,
        "duplicate_business_keys": duplicate_keys,
    }


def analyze(request: AnalysisRequest) -> dict:
    if "data:analyze" not in request.scopes:
        raise PermissionError("data:analyze scope is required")
    if request.metric not in {"revenue", "orders"}:
        raise ValueError("metric is not registered")
    selected = [row for row in ROWS if row["region"] == request.region]
    quality = validate_data(selected)
    if not quality["passed"]:
        return {"status": "blocked", "reason": "data_quality_failed", "quality": quality}

    values = [float(row[request.metric]) for row in selected]
    baseline = values[:-1]
    mean = fmean(baseline)
    deviation = pstdev(baseline) or 1.0
    latest = values[-1]
    z_score = (latest - mean) / deviation
    first = values[0]
    growth = (latest - first) / first
    anomalies = [
        {"month": selected[-1]["month"], "value": latest, "z_score": round(z_score, 2)}
    ] if abs(z_score) >= 2.0 else []
    return {
        "status": "completed",
        "metric": request.metric,
        "region": request.region,
        "quality": quality,
        "analysis": {
            "period_start": selected[0]["month"],
            "period_end": selected[-1]["month"],
            "first_value": first,
            "latest_value": latest,
            "growth_rate": round(growth, 4),
            "baseline_mean": round(mean, 2),
            "anomalies": anomalies,
        },
        "interpretation": (
            "Latest value is statistically unusual; investigate price, mix and one-off orders."
            if anomalies else "No statistical anomaly was detected."
        ),
        "evidence": {"dataset": "demo.monthly_sales", "business_key": ["month", "region"]},
    }


def main() -> None:
    metric = argv[1] if len(argv) > 1 else "revenue"
    result = analyze(AnalysisRequest(metric, "east", frozenset({"data:analyze"})))
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
