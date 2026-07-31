"""Qdrant Local MVP: collection, payload indexes, upsert, filter, and query.

Run from the repository root:
    pip install -r chapters/chapter07/vector_databases/requirements/qdrant.txt
    python chapters/chapter07/vector_databases/qdrant_mvp.py
"""

import os
from pathlib import Path

from qdrant_client import QdrantClient, models

from common import DIMENSION, DOCUMENTS, QUERY, embed, print_hit


COLLECTION_NAME = "chapter07_metrics"
POINT_IDS = {
    "gmv": 1,
    "revenue": 2,
    "inventory": 3,
    "other-tenant-gmv": 4,
}


def main() -> None:
    default_path = Path(__file__).resolve().parent / ".data" / "qdrant"
    database_path = os.getenv("QDRANT_PATH", str(default_path))
    Path(database_path).mkdir(parents=True, exist_ok=True)
    client = QdrantClient(path=database_path)

    if not client.collection_exists(COLLECTION_NAME):
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=models.VectorParams(
                size=DIMENSION,
                distance=models.Distance.COSINE,
            ),
        )
        for field_name in ("tenant_id", "doc_type"):
            client.create_payload_index(
                collection_name=COLLECTION_NAME,
                field_name=field_name,
                field_schema=models.PayloadSchemaType.KEYWORD,
            )

    client.upsert(
        collection_name=COLLECTION_NAME,
        wait=True,
        points=[
            models.PointStruct(
                id=POINT_IDS[document.id],
                vector=embed(document.text),
                payload={
                    "document_id": document.id,
                    "text": document.text,
                    **document.metadata(),
                },
            )
            for document in DOCUMENTS
        ],
    )

    query_filter = models.Filter(
        must=[
            models.FieldCondition(
                key="tenant_id",
                match=models.MatchValue(value="acme"),
            ),
            models.FieldCondition(
                key="doc_type",
                match=models.MatchValue(value="metric"),
            ),
        ]
    )
    response = client.query_points(
        collection_name=COLLECTION_NAME,
        query=embed(QUERY),
        query_filter=query_filter,
        with_payload=True,
        limit=2,
    )

    print("Query:", QUERY)
    for point in response.points:
        payload = point.payload or {}
        print_hit(
            str(payload.get("document_id", point.id)),
            float(point.score),
            str(payload.get("text", "")),
        )

    client.delete(
        collection_name=COLLECTION_NAME,
        points_selector=models.PointIdsList(
            points=[POINT_IDS["other-tenant-gmv"]]
        ),
        wait=True,
    )
    client.close()


if __name__ == "__main__":
    main()
