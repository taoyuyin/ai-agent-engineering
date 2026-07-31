"""Shared data and a deterministic teaching embedding for vector DB MVPs.

The hashing embedder keeps every database example offline and reproducible.
It demonstrates API shape only; it is not a semantic embedding model.
"""

import hashlib
import math
import re
from dataclasses import dataclass
from typing import Dict, Iterable, List


DIMENSION = 64
QUERY = "GMV 和销售额的口径区别是什么？"


@dataclass(frozen=True)
class Document:
    id: str
    text: str
    tenant_id: str
    doc_type: str

    def metadata(self) -> Dict[str, str]:
        return {
            "tenant_id": self.tenant_id,
            "doc_type": self.doc_type,
        }


DOCUMENTS = [
    Document(
        id="gmv",
        text="GMV 是成交总额，通常包含已下单但可能尚未确认收入的金额。",
        tenant_id="acme",
        doc_type="metric",
    ),
    Document(
        id="revenue",
        text="销售额是确认收入，通常需要排除退款、取消和未完成订单。",
        tenant_id="acme",
        doc_type="metric",
    ),
    Document(
        id="inventory",
        text="库存周转天数用于衡量库存消耗速度和供应链效率。",
        tenant_id="acme",
        doc_type="supply_chain",
    ),
    Document(
        id="other-tenant-gmv",
        text="另一个租户的 GMV 指标定义，不应被当前租户检索到。",
        tenant_id="other",
        doc_type="metric",
    ),
]


def _tokens(text: str) -> Iterable[str]:
    """Yield lowercase English tokens and overlapping Chinese character bigrams."""
    for token in re.findall(r"[A-Za-z0-9_]+", text.lower()):
        yield token

    for sequence in re.findall(r"[\u4e00-\u9fff]+", text):
        if len(sequence) == 1:
            yield sequence
        else:
            for index in range(len(sequence) - 1):
                yield sequence[index : index + 2]


def embed(text: str, dimension: int = DIMENSION) -> List[float]:
    """Create a stable, normalized hashing vector without external services."""
    vector = [0.0] * dimension
    for token in _tokens(text):
        digest = hashlib.blake2b(token.encode("utf-8"), digest_size=8).digest()
        bucket = int.from_bytes(digest[:4], "big") % dimension
        sign = 1.0 if digest[4] % 2 == 0 else -1.0
        vector[bucket] += sign

    norm = math.sqrt(sum(value * value for value in vector))
    if norm == 0:
        return vector
    return [value / norm for value in vector]


def print_hit(doc_id: str, score: float, text: str) -> None:
    print("{:.4f} | {} | {}".format(score, doc_id, text))


if __name__ == "__main__":
    query_vector = embed(QUERY)
    assert len(query_vector) == DIMENSION
    assert abs(math.sqrt(sum(value * value for value in query_vector)) - 1.0) < 1e-9
    assert embed(QUERY) == query_vector
    print("Deterministic embedding OK: dimension={}".format(DIMENSION))
