"""Governed knowledge assets with version, provenance and tenant isolation."""

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
import re


def _tokens(text: str) -> set:
    words = re.findall(r"[A-Za-z0-9_]+|[\u4e00-\u9fff]", text.lower())
    return set(words)


@dataclass(frozen=True)
class KnowledgeAsset:
    asset_id: str
    version: int
    tenant_id: str
    domain: str
    content: str
    source: str
    owner: str
    valid_from: str
    valid_to: Optional[str] = None
    tags: Tuple[str, ...] = ()

    def validate(self) -> None:
        required = (
            self.asset_id,
            self.tenant_id,
            self.domain,
            self.content,
            self.source,
            self.owner,
            self.valid_from,
        )
        if not all(required) or self.version < 1:
            raise ValueError("knowledge asset is missing governance metadata")
        if self.valid_to is not None and self.valid_to < self.valid_from:
            raise ValueError("valid_to must not precede valid_from")


class KnowledgeCatalog:
    def __init__(self) -> None:
        self._assets: Dict[str, Dict[int, KnowledgeAsset]] = {}

    def publish(self, asset: KnowledgeAsset) -> None:
        asset.validate()
        versions = self._assets.setdefault(asset.asset_id, {})
        if asset.version in versions:
            raise ValueError("knowledge versions are immutable")
        if versions and asset.version != max(versions) + 1:
            raise ValueError("versions must be contiguous")
        versions[asset.version] = asset

    def current(self, asset_id: str, as_of: str) -> KnowledgeAsset:
        candidates = [
            item
            for item in self._assets.get(asset_id, {}).values()
            if item.valid_from <= as_of and (item.valid_to is None or as_of <= item.valid_to)
        ]
        if not candidates:
            raise KeyError("no valid knowledge version")
        return max(candidates, key=lambda item: item.version)

    def search(
        self,
        query: str,
        tenant_id: str,
        domain: str,
        as_of: str = "9999-12-31",
        limit: int = 5,
    ) -> List[KnowledgeAsset]:
        query_tokens = _tokens(query)
        ranked = []
        for asset_id in self._assets:
            try:
                asset = self.current(asset_id, as_of)
            except KeyError:
                continue
            if asset.tenant_id != tenant_id or asset.domain != domain:
                continue
            score = len(query_tokens & _tokens(asset.content + " " + " ".join(asset.tags)))
            if score:
                ranked.append((score, asset.version, asset))
        ranked.sort(key=lambda row: (row[0], row[1]), reverse=True)
        return [row[2] for row in ranked[:limit]]
