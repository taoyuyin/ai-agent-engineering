"""Chapter 48: a human-gated manufacturing diagnostic Agent MVP."""

from __future__ import annotations

import json
from dataclasses import dataclass
from statistics import fmean
from sys import argv


TELEMETRY = {
    "motor-7": {
        "plant": "plant-a",
        "model": "M-200",
        "bearing_temperature_c": [71.0, 75.0, 82.0, 89.0],
        "vibration_mm_s": [3.1, 3.8, 5.7, 7.4],
        "rpm": [1480, 1482, 1479, 1481],
    }
}
LIMITS = {"bearing_temperature_c": 85.0, "vibration_mm_s": 7.1}


@dataclass(frozen=True)
class OperatorContext:
    actor_id: str
    plants: frozenset[str]
    scopes: frozenset[str]


def read_telemetry(asset_id: str, context: OperatorContext) -> dict:
    if "telemetry:read" not in context.scopes:
        raise PermissionError("telemetry:read scope is required")
    asset = TELEMETRY.get(asset_id)
    if not asset or asset["plant"] not in context.plants:
        raise PermissionError("asset is outside the operator plant boundary")
    return asset


def diagnose(asset_id: str, context: OperatorContext) -> dict:
    asset = read_telemetry(asset_id, context)
    violations = []
    for signal, limit in LIMITS.items():
        readings = asset[signal]
        if readings[-1] > limit:
            violations.append(
                {
                    "signal": signal,
                    "latest": readings[-1],
                    "limit": limit,
                    "recent_mean": round(fmean(readings), 2),
                    "increasing": all(a < b for a, b in zip(readings, readings[1:])),
                }
            )
    severity = "high" if len(violations) >= 2 else "medium" if violations else "normal"
    proposal = None
    if severity != "normal":
        proposal = {
            "type": "maintenance_work_order_proposal",
            "asset_id": asset_id,
            "recommended_action": "Inspect bearing lubrication, alignment and mounting before restart.",
            "lockout_tagout_required": True,
            "approval_status": "pending_maintenance_supervisor",
        }
    return {
        "status": "awaiting_human_approval" if proposal else "monitoring",
        "asset": {"asset_id": asset_id, "plant": asset["plant"], "model": asset["model"]},
        "diagnosis": {"severity": severity, "violations": violations},
        "proposal": proposal,
        "automatic_control_command_sent": False,
        "evidence": {"source": "demo.telemetry", "limits_version": "motor-safety-v2"},
        "audit": {"actor_id": context.actor_id, "scopes": sorted(context.scopes)},
    }


def main() -> None:
    asset_id = argv[1] if len(argv) > 1 else "motor-7"
    result = diagnose(
        asset_id,
        OperatorContext("operator-001", frozenset({"plant-a"}), frozenset({"telemetry:read"})),
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
