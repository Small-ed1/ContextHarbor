from __future__ import annotations

import os
import re
import ipaddress
import socket
from concurrent.futures import ThreadPoolExecutor, TimeoutError
from typing import Any
from urllib.parse import quote, quote_plus, urlparse

import requests
from bs4 import BeautifulSoup
from pydantic import BaseModel, Field

try:
    from ddgs import DDGS
except Exception:
    DDGS = None

from ollama_tools.toolcore import ToolRegistry, ToolSpec


def _env_int(name: str, default: int) -> int:
    value = os.getenv(name)
    if value is None:
        return default
    try:
        return int(value)
    except ValueError:
        return default


def _env_list(name: str) -> list[str]:
    raw = os.getenv(name, "")
    return [item.strip().lower() for item in raw.split(",") if item.strip()]


UA = "ollama-tools/0.2 (+https://localhost)"
SEARCH_TIMEOUT = _env_int("WEB_SEARCH_TIMEOUT", 15)
FETCH_TIMEOUT = _env_int("WEB_FETCH_TIMEOUT", 15)
MAX_REDIRECTS = _env_int("WEB_MAX_REDIRECTS", 5)
ALLOWED_HOSTS = _env_list("WEB_ALLOWED_HOSTS")
BLOCKED_HOSTS = _env_list("WEB_BLOCKED_HOSTS")


def _is_http_url(url: str) -> bool:
    try:
        parsed = urlparse(url)
        return parsed.scheme in {"http", "https"} and bool(parsed.netloc)
    except Exception:
        return False


def _host_matches(hostname: str, pattern: str) -> bool:
    if hostname == pattern:
        return True
    return hostname.endswith("." + pattern)


def _is_private_ip(hostname: str) -> bool:
    try:
        ip = ipaddress.ip_address(hostname)
        return ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved
    except ValueError:
        pass

    ips_found = set()
    try:
        addr_info = socket.getaddrinfo(hostname, None, family=socket.AF_INET)
        for info in addr_info[:3]:
            ip = ipaddress.ip_address(info[4][0])
            if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved:
                return True
            ips_found.add(str(ip))
    except (socket.gaierror, OSError, ValueError):
        pass

    if len(ips_found) > 1:
        return True

    return False


def _is_blocked_url(url: str) -> bool:
    parsed = urlparse(url)
    scheme = parsed.scheme.lower()
    hostname = (parsed.hostname or "").lower()

    if scheme not in {"http", "https"}:
        return True
    if not hostname:
        return True
    if _is_private_ip(hostname):
        return True

    if BLOCKED_HOSTS:
        for pattern in BLOCKED_HOSTS:
            if _host_matches(hostname, pattern):
                return True

    if ALLOWED_HOSTS:
        if not any(_host_matches(hostname, pattern) for pattern in ALLOWED_HOSTS):
            return True

    return False


def _clean_text(s: str) -> str:
    s = re.sub(r"\s+\n", "\n", s)
    s = re.sub(r"\n\s+", "\n", s)
    s = re.sub(r"[ \t]+", " ", s)
    return s.strip()


def _extract_readable_text(html: str, max_chars: int) -> dict[str, Any]:
    soup = BeautifulSoup(html, "html.parser")

    for tag in soup(["script", "style", "noscript", "svg", "img"]):
        tag.decompose()

    title = ""
    if soup.title and soup.title.string:
        title = soup.title.string.strip()

    text = soup.get_text("\n")
    text = _clean_text(text)

    if len(text) > max_chars:
        text = text[:max_chars] + "..."

    return {"title": title, "text": text}


class WebSearchArgs(BaseModel):
    query: str = Field(..., description="Search query")
    max_results: int = Field(5, ge=1, le=15, description="Number of results (1-15)")


def _ddgs_search(query: str, max_results: int) -> list[dict[str, str]]:
    if DDGS is None:
        raise RuntimeError("ddgs is not available")

    ddgs_cls = DDGS
    out: list[dict[str, str]] = []
    with ddgs_cls() as ddgs:
        for result in ddgs.text(query, max_results=max_results):
            out.append(
                {
                    "title": result.get("title", ""),
                    "url": result.get("href", ""),
                    "snippet": result.get("body", ""),
                }
            )
    return out


def _ddg_html_search(query: str, max_results: int) -> list[dict[str, str]]:
    url = f"https://duckduckgo.com/html/?q={quote_plus(query)}"
    response = requests.get(url, headers={"User-Agent": UA}, timeout=SEARCH_TIMEOUT)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")

    results: list[dict[str, str]] = []
    for result in soup.select("div.result"):
        link = result.select_one("a.result__a")
        if not link:
            continue
        title = link.get_text(" ", strip=True)
        href = str(link.get("href", ""))
        snippet_tag = result.select_one(".result__snippet")
        snippet = snippet_tag.get_text(" ", strip=True) if snippet_tag else ""
        results.append({"title": title, "url": href, "snippet": snippet})
        if len(results) >= max_results:
            break

    return results


def _filter_blocked_results(results: list[dict[str, str]]) -> list[dict[str, str]]:
    if not results:
        return []
    out: list[dict[str, str]] = []
    for r in results:
        url = r.get("url") or ""
        if not url:
            continue
        if _is_blocked_url(url):
            continue
        out.append(r)
    return out


def web_search(args: WebSearchArgs) -> list[dict[str, str]]:
    if DDGS is None:
        return _filter_blocked_results(_ddg_html_search(args.query, args.max_results))

    executor = ThreadPoolExecutor(max_workers=1)
    try:
        future = executor.submit(_ddgs_search, args.query, args.max_results)
        return _filter_blocked_results(future.result(timeout=SEARCH_TIMEOUT))
    except TimeoutError:
        return _filter_blocked_results(_ddg_html_search(args.query, args.max_results))
    except Exception:
        return _filter_blocked_results(_ddg_html_search(args.query, args.max_results))
    finally:
        executor.shutdown(wait=False, cancel_futures=True)


WEB_SEARCH = ToolSpec(
    name="web_search",
    description="Search the live internet (DuckDuckGo). Returns title/url/snippet list.",
    args_schema=WebSearchArgs,
    handler=web_search,
)


class SiteSearchArgs(BaseModel):
    site: str = Field(..., description="Domain like wikipedia.org or archlinux.org")
    query: str = Field(..., description="Search query")
    max_results: int = Field(5, ge=1, le=15, description="Number of results (1-15)")


def _normalize_site(site: str) -> str:
    site = (site or "").strip().lower()
    if not site:
        return ""
    if "://" in site:
        parsed = urlparse(site)
        site = parsed.netloc
    site = site.split("/")[0]
    return site


def site_search(args: SiteSearchArgs) -> list[dict[str, str]]:
    site = _normalize_site(args.site)
    if not site:
        raise ValueError("site is required")
    query = f"site:{site} {args.query}"
    return web_search(WebSearchArgs(query=query, max_results=args.max_results))


SITE_SEARCH = ToolSpec(
    name="site_search",
    description="Search the live internet but restricted to a single site/domain.",
    args_schema=SiteSearchArgs,
    handler=site_search,
)


class FetchUrlArgs(BaseModel):
    url: str = Field(..., description="HTTP/HTTPS URL to fetch")
    mode: str = Field("readable", description="readable | html")
    max_chars: int = Field(8000, ge=1000, le=50000, description="Clamp output size")


def fetch_url(args: FetchUrlArgs) -> dict[str, Any]:
    if not _is_http_url(args.url):
        raise ValueError("Only http/https URLs are allowed.")
    if _is_blocked_url(args.url):
        raise ValueError("URL blocked by policy")

    session = requests.Session()
    session.max_redirects = MAX_REDIRECTS
    response = session.get(args.url, headers={"User-Agent": UA}, timeout=FETCH_TIMEOUT, allow_redirects=True)
    response.raise_for_status()
    if _is_blocked_url(response.url):
        raise ValueError("Redirect target blocked by policy")

    if args.mode == "html":
        html = response.text
        if len(html) > args.max_chars:
            html = html[: args.max_chars] + "..."
        return {"url": args.url, "html": html}

    parsed = _extract_readable_text(response.text, max_chars=args.max_chars)
    parsed["url"] = args.url
    return parsed


FETCH_URL = ToolSpec(
    name="fetch_url",
    description="Fetch a URL. mode=readable extracts clean text; mode=html returns raw HTML.",
    args_schema=FetchUrlArgs,
    handler=fetch_url,
)


class WikipediaSummaryArgs(BaseModel):
    title: str | None = Field(None, description="Wikipedia page title (ex: '2017 World's Strongest Man')")
    query: str | None = Field(None, description="Alias for title")


def wikipedia_summary(args: WikipediaSummaryArgs) -> dict[str, Any]:
    title = args.title or args.query
    if not title:
        raise ValueError("title is required")

    safe_title = quote(title.replace(" ", "_"), safe="")
    url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{safe_title}"
    if _is_blocked_url(url):
        raise ValueError("URL blocked by policy")

    response = requests.get(url, headers={"User-Agent": UA}, timeout=FETCH_TIMEOUT)
    response.raise_for_status()
    data = response.json()

    return {
        "title": data.get("title", title),
        "extract": data.get("extract", ""),
        "url": data.get("content_urls", {}).get("desktop", {}).get("page", ""),
    }


WIKIPEDIA_SUMMARY = ToolSpec(
    name="wikipedia_summary",
    description="Get a quick live Wikipedia summary for a page title.",
    args_schema=WikipediaSummaryArgs,
    handler=wikipedia_summary,
)


def register_internet_tools(reg: ToolRegistry) -> None:
    reg.register(WEB_SEARCH)
    reg.register(SITE_SEARCH)
    reg.register(FETCH_URL)
    reg.register(WIKIPEDIA_SUMMARY)
