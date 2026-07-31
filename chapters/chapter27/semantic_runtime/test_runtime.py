import unittest

from semantic_runtime import MetricDefinition, MetricRequest, SemanticLayer


class SemanticLayerTest(unittest.TestCase):
    def setUp(self):
        self.layer = SemanticLayer()
        self.layer.register(
            MetricDefinition(
                "revenue", "SUM(amount)", "analytics.orders",
                ("region", "product"), "order_date", "finance", "CNY"
            )
        )

    def test_compiles_parameterized_metric_sql(self):
        plan = self.layer.compile(MetricRequest("revenue", ("region",), {"region": "east"}))
        self.assertIn("SUM(amount) AS revenue", plan.sql)
        self.assertIn("region = ?", plan.sql)
        self.assertEqual(("east",), plan.parameters)

    def test_rejects_unknown_dimension(self):
        with self.assertRaises(PermissionError):
            self.layer.compile(MetricRequest("revenue", ("customer_phone",), {}))

    def test_rejects_unsafe_catalog_identifier(self):
        with self.assertRaises(ValueError):
            self.layer.register(
                MetricDefinition("bad;drop", "SUM(x)", "t", (), "day", "owner", "CNY")
            )


if __name__ == "__main__":
    unittest.main()
