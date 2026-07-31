"""Chapter 27: compile a governed metric request into parameterized SQL."""

from semantic_runtime import MetricDefinition, MetricRequest, SemanticLayer


def main() -> None:
    layer = SemanticLayer()
    layer.register(
        MetricDefinition(
            name="net_revenue",
            expression="SUM(order_amount - refund_amount)",
            source_table="analytics.orders",
            dimensions=("region", "product"),
            time_dimension="order_date",
            owner="finance",
            unit="CNY",
        )
    )
    plan = layer.compile(MetricRequest("net_revenue", ("region",), {"region": "华东"}))
    print(plan.sql)
    print(plan.parameters)


if __name__ == "__main__":
    main()
