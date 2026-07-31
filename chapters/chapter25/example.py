"""Chapter 25: publish and retrieve governed enterprise knowledge."""

from knowledge_runtime import KnowledgeAsset, KnowledgeCatalog


def main() -> None:
    catalog = KnowledgeCatalog()
    catalog.publish(
        KnowledgeAsset(
            asset_id="refund-policy",
            version=1,
            tenant_id="retail",
            domain="service",
            content="退款申请须在签收后七日内提交。",
            source="policy://customer-service/refund",
            owner="customer-service",
            valid_from="2026-01-01",
            tags=("退款", "售后"),
        )
    )
    print(catalog.search("退款 七日", tenant_id="retail", domain="service"))


if __name__ == "__main__":
    main()
