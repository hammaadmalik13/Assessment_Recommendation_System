from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from typing import Iterable

from app.catalog_loader import CatalogItem


def _tokenize(text: str) -> list[str]:
    return [tok for tok in "".join(ch if ch.isalnum() else " " for ch in text.lower()).split() if tok]


@dataclass(frozen=True)
class ScoredItem:
    item: CatalogItem
    score: float


def score_catalog_items(
    query: str, catalog: Iterable[CatalogItem], additional_constraints: str = ""
) -> list[ScoredItem]:
    query_tokens = _tokenize(query + " " + additional_constraints)
    token_counts = Counter(query_tokens)

    scored: list[ScoredItem] = []
    for item in catalog:
        haystack = " ".join(
            [
                item.name.lower(),
                item.description.lower(),
                " ".join(item.tags),
                " ".join(item.levels),
            ]
        )
        haystack_tokens = set(_tokenize(haystack))
        overlap = sum(token_counts[tok] for tok in haystack_tokens if tok in token_counts)
        if overlap > 0:
            scored.append(ScoredItem(item=item, score=float(overlap)))

    scored.sort(key=lambda x: (-x.score, x.item.name))
    return scored

