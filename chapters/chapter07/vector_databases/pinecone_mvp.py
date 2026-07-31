"""Pinecone Serverless MVP using externally generated vectors.

Required environment variable:
    PINECONE_API_KEY

Run from the repository root:
    pip install -r chapters/chapter07/vector_databases/requirements/pinecone.txt
    python chapters/chapter07/vector_databases/pinecone_mvp.py
"""

import os
import time

from pinecone import ServerlessSpec
from pinecone.grpc import PineconeGRPC as Pinecone

from common import DIMENSION, DOCUMENTS, QUERY, embed, print_hit


INDEX_NAME = os.getenv("PINECONE_INDEX", "chapter07-metrics")
NAMESPACE = "acme-demo"


def main() -> None:
    api_key = os.environ.get("PINECONE_API_KEY")
    if not api_key:
        raise SystemExit("Set PINECONE_API_KEY before running this example.")

    client = Pinecone(api_key=api_key)
    if not client.has_index(INDEX_NAME):
        client.create_index(
            name=INDEX_NAME,
            vector_type="dense",
            dimension=DIMENSION,
            metric="cosine",
            spec=ServerlessSpec(
                cloud=os.getenv("PINECONE_CLOUD", "aws"),
                region=os.getenv("PINECONE_REGION", "us-east-1"),
            ),
            deletion_protection="disabled",
            tags={"environment": "chapter07-demo"},
        )

    index = client.Index(INDEX_NAME)
    index.upsert(
        namespace=NAMESPACE,
        vectors=[
            {
                "id": document.id,
                "values": embed(document.text),
                "metadata": {
                    "text": document.text,
                    **document.metadata(),
                },
            }
            for document in DOCUMENTS
        ],
    )

    # Pinecone is eventually consistent. Poll index stats instead of relying on
    # a fixed production sleep; this short bounded loop keeps the MVP readable.
    for _ in range(10):
        stats = index.describe_index_stats()
        namespace_stats = stats.namespaces.get(NAMESPACE)
        if namespace_stats and namespace_stats.vector_count >= len(DOCUMENTS):
            break
        time.sleep(1)

    result = index.query(
        namespace=NAMESPACE,
        vector=embed(QUERY),
        filter={
            "$and": [
                {"tenant_id": {"$eq": "acme"}},
                {"doc_type": {"$eq": "metric"}},
            ]
        },
        top_k=2,
        include_metadata=True,
    )

    print("Query:", QUERY)
    for match in result.matches:
        metadata = match.metadata or {}
        print_hit(match.id, float(match.score), str(metadata.get("text", "")))

    index.delete(namespace=NAMESPACE, ids=["other-tenant-gmv"])


if __name__ == "__main__":
    main()
