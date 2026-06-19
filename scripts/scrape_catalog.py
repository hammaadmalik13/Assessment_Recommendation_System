from __future__ import annotations

import json
import re
from pathlib import Path

import httpx
from bs4 import BeautifulSoup

OUTPUT = Path("data/processed/catalog.json")
SOURCE_URL = "https://www.shl.com/solutions/products/product-catalog/"
SHL_PREFIX = "https://www.shl.com"


def normalize(text: str) -> str:
    return " ".join(text.split())


def scrape() -> dict:
    with httpx.Client(timeout=30.0, follow_redirects=True) as client:
        response = client.get(SOURCE_URL)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "lxml")

    items: list[dict] = []
    seen_urls: set[str] = set()
    links = soup.select("a[href*='product-catalog/view/']")
    for link in links:
        href = link.get("href") or ""
        if not href:
            continue
        if href.startswith("/"):
            href = f"{SHL_PREFIX}{href}"
        if not href.startswith("https://www.shl.com/"):
            continue
        if href in seen_urls:
            continue
        seen_urls.add(href)
        name = normalize(link.get_text(" ", strip=True)) or "Unknown Assessment"
        test_type = "K"
        lower = name.lower()
        if re.search(r"\b(opq|personality)\b", lower):
            test_type = "P"
        elif re.search(r"\b(reasoning|verify)\b", lower):
            test_type = "C"

        items.append(
            {
                "name": name,
                "url": href,
                "test_type": test_type,
                "description": f"SHL catalog assessment entry for {name}.",
                "tags": [],
                "levels": [],
            }
        )

    if not items:
        raise RuntimeError("No catalog items found from SHL catalog page.")
    return {"items": items}


def main() -> None:
    payload = scrape()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"Wrote {len(payload['items'])} items to {OUTPUT}")


if __name__ == "__main__":
    main()

