"""Milvus Lite MVP: create, upsert, scalar filter, search, and delete.

Run from the repository root:
    pip install -r chapters/chapter07/vector_databases/requirements/milvus.txt
    python chapters/chapter07/vector_databases/milvus_mvp.py
"""

import os
from pathlib import Path

from pymilvus import MilvusClient

from common import DIMENSION, DOCUMENTS, QUERY, embed, print_hit


COLLECTION_NAME = "chapter07_metrics"
POINT_IDS = {
    "gmv": 1,
    "revenue": 2,
    "inventory": 3,
    "other-tenant-gmv": 4,
}


def main() -> None:
    default_path = Path(__file__).resolve().parent / ".data" / "milvus.db"
    configured_uri = os.getenv("MILVUS_URI")
    database_uri = configured_uri or str(default_path)
    if not configured_uri:
        default_path.parent.mkdir(parents=True, exist_ok=True)
    token = os.getenv("MILVUS_TOKEN")
    client_options = {"uri": database_uri}
    if token:
        client_options["token"] = token
    client = MilvusClient(**client_options)

    if not client.has_collection(COLLECTION_NAME):
        client.create_collection(
            collection_name=COLLECTION_NAME,
            dimension=DIMENSION,
            metric_type="COSINE",
            consistency_level="Strong",
        )

    client.upsert(
        collection_name=COLLECTION_NAME,
        data=[
            {
                "id": POINT_IDS[document.id],
                "vector": embed(document.text),
                "document_id": document.id,
                "text": document.text,
                **document.metadata(),
            }
            for document in DOCUMENTS
        ],
    )

    result = client.search(
        collection_name=COLLECTION_NAME,
        data=[embed(QUERY)],
        filter='tenant_id == "acme" and doc_type == "metric"',
        limit=2,
        output_fields=["document_id", "text", "tenant_id", "doc_type"],
    )

    print("Query:", QUERY)
    for hit in result[0]:
        entity = hit.get("entity", {})
        print_hit(
            str(entity.get("document_id", hit["id"])),
            float(hit["distance"]),
            str(entity.get("text", "")),
        )

    client.delete(
        collection_name=COLLECTION_NAME,
        ids=[POINT_IDS["other-tenant-gmv"]],
    )
    client.close()


if __name__ == "__main__":
    main()
