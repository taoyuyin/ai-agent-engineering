"""Chroma MVP: persist, upsert, filter, vector search, and delete.

Run from the repository root:
    pip install -r chapters/chapter07/vector_databases/requirements/chroma.txt
    python chapters/chapter07/vector_databases/chroma_mvp.py
"""

import os
from pathlib import Path

import chromadb

from common import DOCUMENTS, QUERY, embed, print_hit


COLLECTION_NAME = "chapter07_metrics"


def main() -> None:
    default_path = Path(__file__).resolve().parent / ".data" / "chroma"
    database_path = os.getenv("CHROMA_PATH", str(default_path))
    Path(database_path).mkdir(parents=True, exist_ok=True)
    client = chromadb.PersistentClient(path=database_path)
    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        configuration={"hnsw": {"space": "cosine"}},
    )

    collection.upsert(
        ids=[document.id for document in DOCUMENTS],
        embeddings=[embed(document.text) for document in DOCUMENTS],
        documents=[document.text for document in DOCUMENTS],
        metadatas=[document.metadata() for document in DOCUMENTS],
    )

    result = collection.query(
        query_embeddings=[embed(QUERY)],
        n_results=2,
        where={
            "$and": [
                {"tenant_id": {"$eq": "acme"}},
                {"doc_type": {"$eq": "metric"}},
            ]
        },
        include=["documents", "metadatas", "distances"],
    )

    print("Query:", QUERY)
    ids = result["ids"][0]
    documents = result["documents"][0]
    distances = result["distances"][0]
    for doc_id, text, distance in zip(ids, documents, distances):
        print_hit(doc_id, 1.0 - float(distance), text)

    collection.delete(ids=["other-tenant-gmv"])


if __name__ == "__main__":
    main()
