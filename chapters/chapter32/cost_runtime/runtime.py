"""Capability-aware model routing with explicit token cost and budget checks."""

from dataclasses import dataclass
from typing import FrozenSet, Iterable


@dataclass(frozen=True)
class ModelProfile:
    name: str
    capabilities: FrozenSet[str]
    quality_tier: int
    input_usd_per_million: float
    output_usd_per_million: float
    cached_input_usd_per_million: float = 0.0

    def estimate(self, input_tokens: int, output_tokens: int, cached_input_tokens: int = 0) -> float:
        cached = min(max(0, cached_input_tokens), input_tokens)
        uncached = input_tokens - cached
        return (
            uncached * self.input_usd_per_million
            + cached * self.cached_input_usd_per_million
            + output_tokens * self.output_usd_per_million
        ) / 1_000_000


@dataclass(frozen=True)
class RouteRequest:
    capability: str
    quality_tier: int
    input_tokens: int
    output_tokens: int
    cached_input_tokens: int = 0


@dataclass(frozen=True)
class RouteDecision:
    model: str
    estimated_cost_usd: float
    reason: str


@dataclass
class BudgetLedger:
    limit_usd: float
    spent_usd: float = 0.0

    @property
    def remaining_usd(self) -> float:
        return max(0.0, self.limit_usd - self.spent_usd)

    def record(self, amount: float) -> None:
        if amount > self.remaining_usd:
            raise RuntimeError("budget exceeded")
        self.spent_usd += amount


class ModelRouter:
    def __init__(self, models: Iterable[ModelProfile], ledger: BudgetLedger) -> None:
        self.models = tuple(models)
        self.ledger = ledger

    def route(self, request: RouteRequest) -> RouteDecision:
        candidates = []
        for model in self.models:
            if request.capability not in model.capabilities or model.quality_tier < request.quality_tier:
                continue
            cost = model.estimate(
                request.input_tokens, request.output_tokens, request.cached_input_tokens
            )
            if cost <= self.ledger.remaining_usd:
                candidates.append((cost, model))
        if not candidates:
            raise RuntimeError("no capable model fits the remaining budget")
        cost, model = min(candidates, key=lambda item: (item[0], item[1].quality_tier))
        return RouteDecision(model.name, cost, "cheapest capable model within budget")
