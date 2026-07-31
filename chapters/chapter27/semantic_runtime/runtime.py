"""A governed semantic layer that compiles safe metric queries."""

from dataclasses import dataclass
from typing import Dict, Mapping, Tuple
import re


IDENTIFIER = re.compile(r"^[A-Za-z_][A-Za-z0-9_.]*$")


@dataclass(frozen=True)
class MetricDefinition:
    name: str
    expression: str
    source_table: str
    dimensions: Tuple[str, ...]
    time_dimension: str
    owner: str
    unit: str
    version: int = 1

    def validate(self) -> None:
        identifiers = (self.name, self.source_table, self.time_dimension) + self.dimensions
        if not all(IDENTIFIER.match(item) for item in identifiers):
            raise ValueError("unsafe semantic identifier")
        if not self.expression or not self.owner or self.version < 1:
            raise ValueError("metric governance metadata is required")


@dataclass(frozen=True)
class MetricRequest:
    metric: str
    dimensions: Tuple[str, ...]
    filters: Mapping[str, object]


@dataclass(frozen=True)
class QueryPlan:
    sql: str
    parameters: Tuple[object, ...]
    metric_version: int
    owner: str
    unit: str


class SemanticLayer:
    def __init__(self) -> None:
        self._metrics: Dict[str, MetricDefinition] = {}

    def register(self, metric: MetricDefinition) -> None:
        metric.validate()
        if metric.name in self._metrics:
            raise ValueError("metric names are immutable; publish a new catalog")
        self._metrics[metric.name] = metric

    def compile(self, request: MetricRequest) -> QueryPlan:
        if request.metric not in self._metrics:
            raise KeyError("unknown metric")
        metric = self._metrics[request.metric]
        allowed = set(metric.dimensions) | {metric.time_dimension}
        if not set(request.dimensions).issubset(allowed):
            raise PermissionError("unsupported dimension")
        if not set(request.filters).issubset(allowed):
            raise PermissionError("unsupported filter")
        select = list(request.dimensions) + ["%s AS %s" % (metric.expression, metric.name)]
        sql = "SELECT %s FROM %s" % (", ".join(select), metric.source_table)
        parameters = tuple(request.filters.values())
        if request.filters:
            where = ["%s = ?" % name for name in request.filters]
            sql += " WHERE " + " AND ".join(where)
        if request.dimensions:
            sql += " GROUP BY " + ", ".join(request.dimensions)
        return QueryPlan(sql, parameters, metric.version, metric.owner, metric.unit)
