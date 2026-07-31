"""Minimal embedding retrieval MVP.

Run:
    python chapters/chapter07/example.py
"""

import math
import re
from collections import Counter


DOCUMENTS = {
    "gmv": "GMV 是成交总额，通常包含已下单但可能未最终确认收入的金额。",
    "revenue": "销售额是确认收入，通常需要排除退款、取消和未完成订单。",
    "inventory": "库存周转天数用于衡量库存消耗速度和供应链效率。",
}


def tokenize(text):
    return re.findall(r"[A-Za-z]+|[\u4e00-\u9fff]+", text.lower())


def vectorize(text, vocabulary):
    counts = Counter(tokenize(text))
    return [counts.get(term, 0) for term in vocabulary]


def cosine(a, b):
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(y * y for y in b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


def search(query, documents, top_k=2):
    vocabulary = sorted({token for text in [query, *documents.values()] for token in tokenize(text)})
    query_vector = vectorize(query, vocabulary)
    scored = []
    for doc_id, text in documents.items():
        score = cosine(query_vector, vectorize(text, vocabulary))
        scored.append((score, doc_id, text))
    return sorted(scored, reverse=True)[:top_k]


if __name__ == "__main__":
    query = "销售额和 GMV 的口径区别是什么？"
    print("Query:", query)
    for score, doc_id, text in search(query, DOCUMENTS):
        print(f"{score:.3f} | {doc_id}: {text}")
