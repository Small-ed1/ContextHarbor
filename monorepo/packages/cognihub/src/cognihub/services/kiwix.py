from __future__ import annotations

from typing import Any

import httpx
from bs4 import BeautifulSoup


async def search(base_url: str, query: str, top_k: int = 5) -> list[dict[str, Any]]:
    base_url = (base_url or "").rstrip("/")
    q = (query or "").strip()
    if not base_url or not q:
        return []

    url = f"{base_url}/search"
    params = {"pattern": q, "format": "json", "size": str(top_k)}
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            r = await client.get(url, params=params)
            r.raise_for_status()
            data = r.json()
            raw = data.get("results") or data.get("matches") or []
            return _normalize_results(base_url, raw)[:top_k]
        except Exception:
            try:
                r = await client.get(url, params={"pattern": q})
                r.raise_for_status()
                return _parse_html_results(base_url, r.text, top_k)
            except Exception:
                return []


async def fetch_page(base_url: str, path: str) -> dict[str, Any] | None:
    base_url = (base_url or "").rstrip("/")
    if not base_url:
        return None
    p = (path or "").strip()
    if not p:
        return None
    url = p if p.startswith("http") else f"{base_url}/{p.lstrip('/')}"
    async with httpx.AsyncClient(timeout=12.0, follow_redirects=True) as client:
        try:
            r = await client.get(url)
            r.raise_for_status()
            text = _extract_text(r.text)
            if not text:
                return None
            return {"url": url, "path": p, "text": text}
        except Exception:
            return None


def _normalize_results(base_url: str, raw: list[dict]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for item in raw:
        if not isinstance(item, dict):
            continue
        title = (item.get("title") or item.get("label") or "").strip()
        path = (item.get("url") or item.get("path") or item.get("article") or "").strip()
        if not title and not path:
            continue
        out.append({
            "title": title or path,
            "path": path,
            "url": path if path.startswith("http") else f"{base_url}/{path.lstrip('/')}"
        })
    return out


def _parse_html_results(base_url: str, html: str, top_k: int) -> list[dict[str, Any]]:
    soup = BeautifulSoup(html or "", "lxml")
    items: list[dict[str, Any]] = []
    for a in soup.select("a"):
        href = str(a.get("href") or "").strip()
        title = (a.get_text() or "").strip()
        if not href or href.startswith("#"):
            continue
        if "/search" in href:
            continue
        items.append({
            "title": title or href,
            "path": href,
            "url": href if href.startswith("http") else f"{base_url}/{href.lstrip('/')}"
        })
        if len(items) >= top_k:
            break
    return items


def _extract_text(html: str) -> str:
    soup = BeautifulSoup(html or "", "lxml")
    for tag in soup(["script", "style", "noscript", "svg", "header", "footer", "nav", "aside"]):
        try:
            tag.decompose()
        except Exception:
            pass
    text = soup.get_text("\n")
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    return "\n".join(lines)
