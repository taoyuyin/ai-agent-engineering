"""A small BM25 RAG retriever that keeps document provenance."""

from collections import Counter
from dataclasses import dataclass
from math import log
from typing import Dict, Iterable, List, Tuple
import re


def tokenize(text: str) -> List[str]:
    return re.findall(r"[a-z0-9_]+|[\u4e00-\u9fff]", text.lower())


@dataclass(frozen=True)
class Document:
    document_id: str
    text: str
    source: str


@dataclass(frozen=True)
class Chunk:
    chunk_id: str
    document_id: str
    text: str
    source: str


@dataclass(frozen=True)
class RetrievalResult:
    chunks: Tuple[Chunk, ...]
    context: str
    citations: Tuple[str, ...]


class RAGPipeline:
    def __init__(self, chunk_size: int = 120, overlap: int = 20) -> None:
        if chunk_size < 1 or overlap < 0 or overlap >= chunk_size:
            raise ValueError("invalid chunk settings")
        self.chunk_size = chunk_size
        self.overlap = overlap
        self._chunks: List[Chunk] = []
        self._term_frequencies: List[Counter] = []
        self._document_frequency: Dict[str, int] = {}

    def _split(self, document: Document) -> Iterable[Chunk]:
        step = self.chunk_size - self.overlap
        for start in range(0, len(document.text), step):
            text = document.text[start : start + self.chunk_size]
            if text.strip():
                yield Chunk(
                    "%s:%d" % (document.document_id, start),
                    document.document_id,
                    text,
                    document.source,
                )
            if start + self.chunk_size >= len(document.text):
                break

    def index(self, documents: Iterable[Document]) -> None:
        self._chunks = [chunk for document in documents for chunk in self._split(document)]
        self._term_frequencies = [Counter(tokenize(chunk.text)) for chunk in self._chunks]
        self._document_frequency = {}
        for frequencies in self._term_frequencies:
            for term in frequencies:
                self._document_frequency[term] = self._document_frequency.get(term, 0) + 1

    def _score(self, query: List[str], index: int) -> float:
        frequencies = self._term_frequencies[index]
        length = max(1, sum(frequencies.values()))
        average = sum(sum(item.values()) for item in self._term_frequencies) / max(
            1, len(self._term_frequencies)
        )
        score = 0.0
        for term in query:
            frequency = frequencies.get(term, 0)
            if not frequency:
                continue
            document_frequency = self._document_frequency.get(term, 0)
            inverse = log(1 + (len(self._chunks) - document_frequency + 0.5) / (document_frequency + 0.5))
            score += inverse * frequency * 2.2 / (frequency + 1.2 * (0.25 + 0.75 * length / average))
        return score

    def retrieve(self, query: str, top_k: int = 3) -> RetrievalResult:
        if not self._chunks:
            raise RuntimeError("index is empty")
        scored = [
            (self._score(tokenize(query), index), chunk)
            for index, chunk in enumerate(self._chunks)
        ]
        selected = [chunk for score, chunk in sorted(scored, key=lambda row: row[0], reverse=True) if score > 0][
            :top_k
        ]
        context = "\n\n".join("[%s] %s" % (chunk.chunk_id, chunk.text) for chunk in selected)
        citations = tuple(dict.fromkeys(chunk.source for chunk in selected))
        return RetrievalResult(tuple(selected), context, citations)
