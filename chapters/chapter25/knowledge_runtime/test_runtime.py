import unittest

from knowledge_runtime import KnowledgeAsset, KnowledgeCatalog


def asset(asset_id="a", version=1, tenant="t1", valid_from="2026-01-01", valid_to=None):
    return KnowledgeAsset(
        asset_id, version, tenant, "support", "退款 七日内", "policy://refund",
        "support-team", valid_from, valid_to, ("售后",)
    )


class KnowledgeCatalogTest(unittest.TestCase):
    def test_search_is_tenant_isolated_and_preserves_source(self):
        catalog = KnowledgeCatalog()
        catalog.publish(asset())
        catalog.publish(asset("b", tenant="t2"))
        result = catalog.search("退款", "t1", "support")
        self.assertEqual(["a"], [item.asset_id for item in result])
        self.assertEqual("policy://refund", result[0].source)

    def test_selects_version_by_effective_date(self):
        catalog = KnowledgeCatalog()
        catalog.publish(asset(valid_to="2026-06-30"))
        catalog.publish(asset(version=2, valid_from="2026-07-01"))
        self.assertEqual(1, catalog.current("a", "2026-05-01").version)
        self.assertEqual(2, catalog.current("a", "2026-07-01").version)

    def test_rejects_missing_provenance(self):
        catalog = KnowledgeCatalog()
        with self.assertRaises(ValueError):
            catalog.publish(KnowledgeAsset("a", 1, "t", "d", "x", "", "o", "2026-01-01"))


if __name__ == "__main__":
    unittest.main()
