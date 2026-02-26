from __future__ import annotations

import os
import logging
from typing import Dict, List, Tuple, Any

import httpx
from bs4 import BeautifulSoup

from ..stores import webstore
from .. import config as ch_config
from .search_cache import get_search_cache, get_rate_limiter

logger = logging.getLogger(__name__)


class SearchError(Exception):
    """Raised when search provider blocks or fails."""
    pass


async def ddg_search(http: httpx.AsyncClient, query: str, n: int = 8) -> list[str]:
    """DuckDuckGo HTML search with proper failure detection."""
    q = (query or "").strip()
    if not q:
        return []
    
    url = "https://html.duckduckgo.com/html/"  # Use the final redirect target
    headers = {
        "User-Agent": str(ch_config.config.web_user_agent or "ContextHarbor/1.0"),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate",
        "Content-Type": "application/x-www-form-urlencoded",
        "Origin": "https://duckduckgo.com",
        "Referer": "https://duckduckgo.com/",
    }
    
    try:
        r = await http.post(
            url, 
            data={"q": q}, 
            headers=headers, 
            timeout=15.0, 
            follow_redirects=False  # Don't auto-follow redirects
        )
        
        # Log response details for debugging
        logger.info(
            f"DDG response: status={r.status_code}, url={str(r.url)}, "
            f"content_len={len(r.text)}, location={r.headers.get('Location', 'None')}"
        )
        
        # Check for redirects that go outside DDG (likely blocking)
        if r.status_code in (301, 302, 303, 307, 308):
            location = r.headers.get("Location", "")
            if location and "duckduckgo.com" not in location.lower():
                raise SearchError(
                    f"DDG redirected to external site (likely blocked): status={r.status_code}, location={location}"
                )
        
        # Check for non-200 responses
        if r.status_code != 200:
            raise SearchError(
                f"DDG returned non-200 status: {r.status_code}"
            )
        
        # Check for tiny responses or captcha/redirect pages
        if len(r.text) < 1000:
            if any(phrase in r.text.lower() for phrase in ["captcha", "robot", "blocked", "access denied"]):
                raise SearchError(
                    f"DDG returned blocking page: {len(r.text)} bytes"
                )
            else:
                logger.warning(f"DDG returned suspiciously small response: {len(r.text)} bytes")
        
        # Parse HTML
        soup = BeautifulSoup(r.text, "lxml")
        links: list[str] = []
        for a in soup.select("a.result__a"):
            href = str(a.get("href", ""))
            if href and href.startswith("http") and not webstore._is_blocked_url(href):
                links.append(href)
            if len(links) >= n:
                break
        
        return links
        
    except httpx.HTTPStatusError as e:
        raise SearchError(f"DDG HTTP error: {e}")
    except httpx.RequestError as e:
        raise SearchError(f"DDG request failed: {e}")


async def searxng_search(
    http: httpx.AsyncClient,
    *,
    query: str,
    n: int = 8,
    searxng_url: str,
) -> list[str]:
    """SearxNG JSON search.

    searxng_url may be either a base URL (http://host:port) or a full endpoint
    (http://host:port/search).
    """

    q = (query or "").strip()
    if not q:
        return []

    base = (searxng_url or "").strip().rstrip("/")
    if not base:
        return []

    endpoint = base if base.endswith("/search") else f"{base}/search"
    headers = {"User-Agent": str(ch_config.config.web_user_agent or "ContextHarbor/1.0")}
    params = {
        "q": q,
        "format": "json",
        "language": "en",
        "count": max(1, min(int(n), 20)),
    }

    try:
        r = await http.get(endpoint, params=params, headers=headers, timeout=15.0)
        r.raise_for_status()
        data: Any = r.json()
    except httpx.HTTPStatusError as e:
        raise SearchError(f"SearxNG HTTP error: {e}")
    except httpx.RequestError as e:
        raise SearchError(f"SearxNG request failed: {e}")
    except Exception as e:
        raise SearchError(f"SearxNG invalid response: {e}")

    results = data.get("results") if isinstance(data, dict) else None
    if not isinstance(results, list):
        return []

    links: list[str] = []
    for item in results:
        if not isinstance(item, dict):
            continue
        u = str(item.get("url") or "").strip()
        if not u or not u.startswith("http"):
            continue
        if webstore._is_blocked_url(u):
            continue
        if u in links:
            continue
        links.append(u)
        if len(links) >= n:
            break

    return links


async def web_search_with_fallback(
    http: httpx.AsyncClient, 
    query: str, 
    n: int = 8
) -> tuple[list[str], str]:
    """Web search with caching + rate limiting.

    Supports:
    - ddg (DuckDuckGo HTML)
    - searxng (JSON)
    - fallback between them when configured.
    """
    
    # Check cache first
    cache = get_search_cache()
    provider = str(ch_config.config.search_provider or "ddg").strip().lower()
    cached_results = cache.get(query, n, provider=provider)
    if cached_results is not None:
        logger.info(f"Returning cached results for query: {query[:50]}...")
        return cached_results, "cache_success"

    searxng_url = str(getattr(ch_config.config, "searxng_url", "") or "").strip().rstrip("/")
    
    rate_limiter = get_rate_limiter()

    if provider in {"", "auto"}:
        provider = "searxng" if searxng_url else "ddg"

    async def _run_ddg() -> list[str]:
        await rate_limiter.wait_if_needed("ddg")
        return await ddg_search(http, query, n)

    async def _run_searxng() -> list[str]:
        if not searxng_url:
            return []
        await rate_limiter.wait_if_needed("searxng")
        return await searxng_search(http, query=query, n=n, searxng_url=searxng_url)

    results: list[str] = []
    used = provider

    try:
        if provider == "searxng":
            results = await _run_searxng()
            used = "searxng"
            if not results:
                results = await _run_ddg()
                used = "ddg_fallback"
        elif provider == "ddg":
            results = await _run_ddg()
            used = "ddg"
            if not results and searxng_url:
                results = await _run_searxng()
                used = "searxng_fallback"
        else:
            raise SearchError(f"Unsupported search provider: {provider}")
    except SearchError:
        # If the primary provider fails hard, try the other when possible.
        if provider == "ddg" and searxng_url:
            results = await _run_searxng()
            used = "searxng_fallback"
        elif provider == "searxng":
            results = await _run_ddg()
            used = "ddg_fallback"
        else:
            raise

    if results:
        cache.set(query, n, results, provider=provider)
    return results, f"{used}_success" if results else f"{used}_empty"
