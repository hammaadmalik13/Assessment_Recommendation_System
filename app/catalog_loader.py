from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


CATALOG_PATH = Path("data/processed/catalog.json")
SHL_PREFIX = "https://www.shl.com/"


@dataclass(frozen=True)
class CatalogItem:
    name: str
    url: str
    test_type: str
    description: str
    tags: tuple[str, ...]
    levels: tuple[str, ...]


def _normalize_text(value: str) -> str:
    return " ".join(value.strip().lower().split())


def _validate_item(raw: dict[str, Any]) -> CatalogItem:
    required = ["name", "url", "test_type", "description"]
    for key in required:
        if key not in raw or not str(raw[key]).strip():
            raise ValueError(f"catalog item missing required field: {key}")

    url = str(raw["url"]).strip()
    if not url.startswith(SHL_PREFIX):
        raise ValueError(f"non-SHL url found in catalog: {url}")

    tags = tuple(_normalize_text(x) for x in raw.get("tags", []) if str(x).strip())
    levels = tuple(_normalize_text(x) for x in raw.get("levels", []) if str(x).strip())
    return CatalogItem(
        name=str(raw["name"]).strip(),
        url=url,
        test_type=str(raw["test_type"]).strip(),
        description=str(raw["description"]).strip(),
        tags=tags,
        levels=levels,
    )


def load_catalog(path: Path = CATALOG_PATH) -> list[CatalogItem]:
    if not path.exists():
        raise FileNotFoundError(
            f"Catalog file not found at '{path}'. Run scripts/scrape_catalog.py first."
        )
    payload = json.loads(path.read_text(encoding="utf-8"))
    items = payload["items"] if isinstance(payload, dict) else payload
    if not isinstance(items, list) or not items:
        raise ValueError("catalog data is empty or invalid")

    result: list[CatalogItem] = []
    seen_urls: set[str] = set()
    for raw in items:
        item = _validate_item(raw)
        if item.url in seen_urls:
            continue
        seen_urls.add(item.url)
        result.append(item)

    if not result:
        raise ValueError("no usable catalog items were loaded")
    return result

