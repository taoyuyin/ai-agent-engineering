"""Chapter 46: an ACL-first enterprise knowledge Agent MVP."""

from __future__ import annotations

import json
import math
import re
from collections import Counter
from dataclasses import dataclass
from datetime import date
from sys import argv


@dataclass(frozen=True)
class Document:
    doc_id: str
    title: str
    version: str
    effective_date: date
    status: str
    acl_groups: frozenset[str]
    content: str


DOCUMENTS = [
    Document(
        "travel-v3",
        "差旅报销制度",
        "3.0",
        date(2026, 1, 1),
        "active",
        frozenset({"all-employees"}),
        "国内差旅住宿费需要提供合规发票。单晚超过 800 元需要部门负责人审批。报销应在行程结束后 30 天内提交。",
    ),
    Document(
        "travel-v2",
        "差旅报销制度（旧版）",
        "2.0",
        date(2024, 1, 1),
        "superseded",
        frozenset({"all-employees"}),
        "旧制度规定住宿标准为每晚 600 元。",
    ),
    Document(
        "finance-close-v1",
        "财务关账操作手册",
        "1.0",
        date(2025, 8, 1),
        "active",
        frozenset({"finance"}),
        "月度关账由财务团队执行，包含总账核对和异常凭证复核。",
    ),
]


def tokens(text: str) -> list[str]:
    lowered = text.lower()
    words = re.findall(r"[a-z0-9]+", lowered)
    cjk = "".join(re.findall(r"[\u4e00-\u9fff]", lowered))
    return words + [cjk[index : index + 2] for index in range(max(0, len(cjk) - 1))]


def retrieve(query: str, groups: frozenset[str], top_k: int = 3) -> list[tuple[Document, float]]:
    visible = [
        doc for doc in DOCUMENTS
        if doc.status == "active" and doc.acl_groups.intersection(groups)
    ]
    query_terms = Counter(tokens(query))
    document_terms = [Counter(tokens(doc.title + doc.content)) for doc in visible]
    document_frequency = {
        term: sum(term in terms for terms in document_terms) for term in query_terms
    }
    ranked: list[tuple[Document, float]] = []
    for doc, terms in zip(visible, document_terms):
        score = 0.0
        for term, query_count in query_terms.items():
            if terms[term]:
                inverse_frequency = math.log((len(visible) + 1) / (document_frequency[term] + 0.5)) + 1
                score += query_count * terms[term] * inverse_frequency
        if score > 0:
            ranked.append((doc, score))
    return sorted(ranked, key=lambda item: item[1], reverse=True)[:top_k]


def answer(query: str, groups: frozenset[str]) -> dict:
    ranked = retrieve(query, groups)
    if not ranked:
        return {"status": "not_found", "answer": "未找到有权限且有效的制度。", "citations": []}
    evidence = ranked[0][0]
    return {
        "status": "answered",
        "answer": evidence.content,
        "citations": [
            {
                "doc_id": doc.doc_id,
                "title": doc.title,
                "version": doc.version,
                "effective_date": doc.effective_date.isoformat(),
                "score": round(score, 3),
            }
            for doc, score in ranked
        ],
        "retrieval_policy": {
            "acl_before_retrieval": True,
            "active_versions_only": True,
            "groups": sorted(groups),
        },
    }


def main() -> None:
    query = " ".join(argv[1:]) or "住宿费超过 800 元如何报销？"
    print(json.dumps(answer(query, frozenset({"all-employees"})), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
