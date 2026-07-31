"""Dependency-free exact vector search baseline for Chapter 7.

Run:
    python chapters/chapter07/example.py
"""

import math
from typing import List, Tuple

from vector_databases.common import DOCUMENTS, QUERY, Document, embed


def cosine(left: List[float], right: List[float]) -> float:
    dot = sum(x * y for x, y in zip(left, right))
    left_norm = math.sqrt(sum(value * value for value in left))
    right_norm = math.sqrt(sum(value * value for value in right))
    if left_norm == 0 or right_norm == 0:
        return 0.0
    return dot / (left_norm * right_norm)


def search(
    query: str,
    documents: List[Document],
    tenant_id: str,
    doc_type: str,
    top_k: int = 2,
) -> List[Tuple[float, Document]]:
    """Run exact search after applying tenant and document-type filters."""
    query_vector = embed(query)
    candidates = [
        document
        for document in documents
        if document.tenant_id == tenant_id and document.doc_type == doc_type
    ]
    scored = [
        (cosine(query_vector, embed(document.text)), document)
        for document in candidates
    ]
    return sorted(scored, key=lambda item: item[0], reverse=True)[:top_k]


if __name__ == "__main__":
    print("Query:", QUERY)
    for score, document in search(
        query=QUERY,
        documents=DOCUMENTS,
        tenant_id="acme",
        doc_type="metric",
    ):
        print("{:.4f} | {}: {}".format(score, document.id, document.text))
