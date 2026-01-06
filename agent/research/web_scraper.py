"""
Web Scraping System for Research Data Collection
Comprehensive web scraping with rate limiting, content filtering, and quality assessment.
"""

import asyncio
import hashlib
import json
import logging
import os
import random
import re
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple, Union
from urllib.parse import quote_plus, urljoin, urlparse
from urllib.robotparser import RobotFileParser

import aiohttp
import requests  # type: ignore
from bs4 import BeautifulSoup

try:
    from fake_useragent import UserAgent
except ImportError:
    UserAgent = None  # type: ignore
try:
    import lxml.html
except ImportError:
    lxml = None
try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.support.ui import WebDriverWait
    from webdriver_manager.chrome import ChromeDriverManager
except ImportError:
    webdriver = None
    Options = None
    By = None
    WebDriverWait = None
    EC = None
    ChromeDriverManager = None

from ..utils.memory_manager import MemoryAwareMixin, MemoryManager


@dataclass
class ScrapingConfig:
    """Configuration for web scraping operations."""

    max_concurrent_requests: int = 3
    request_delay: float = 2.0  # seconds between requests
    max_pages_per_domain: int = 5
    timeout: int = 30
    max_content_length: int = 5_000_000  # 5MB
    user_agent_rotation: bool = True
    respect_robots_txt: bool = True
    max_redirects: int = 3
    retry_attempts: int = 2
    retry_delay: float = 1.0

    # Content filtering
    min_content_length: int = 500
    filter_max_content_length: int = 50000
    required_keywords: List[str] = field(default_factory=list)
    blocked_keywords: List[str] = field(
        default_factory=lambda: ["login", "signup", "advertisement", "cookie"]
    )

    # Quality thresholds
    min_relevance_score: float = 0.3
    min_quality_score: float = 0.4


@dataclass
class ScrapedContent:
    """Structure for scraped web content."""

    url: str
    title: str
    content: str
    summary: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    scraped_at: datetime = field(default_factory=datetime.now)
    content_type: str = "html"
    word_count: int = 0
    relevance_score: float = 0.0
    quality_score: float = 0.0
    source_domain: str = ""
    content_hash: str = ""
    links: List[str] = field(default_factory=list)
    images: List[str] = field(default_factory=list)
    headers: Dict[str, str] = field(default_factory=dict)


@dataclass
class SearchQuery:
    """Search query configuration."""

    query: str
    search_engine: str = "google"  # google, bing, duckduckgo
    num_results: int = 20
    time_filter: Optional[str] = None  # day, week, month, year
    language: str = "en"
    region: str = "us"


@dataclass
class ScrapingSession:
    """Session tracking for scraping operations."""

    session_id: str
    start_time: datetime = field(default_factory=datetime.now)
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    domains_scraped: Set[str] = field(default_factory=set)
    content_collected: int = 0
    errors: List[str] = field(default_factory=list)


class WebScraper(MemoryAwareMixin):
    """Advanced web scraper with rate limiting, content filtering, and quality assessment."""

    def __init__(
        self,
        config: ScrapingConfig,
        memory_manager: MemoryManager,
        cache_dir: str = "./cache",
    ):
        super().__init__(memory_manager)
        self.config = config
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)

        self.logger = logging.getLogger(__name__)
        self.ua = UserAgent() if UserAgent is not None and config.user_agent_rotation else None

        # Session tracking
        self.session: Optional[aiohttp.ClientSession] = None
        self.current_session: Optional[ScrapingSession] = None

        # Rate limiting
        self.request_times: Dict[str, List[datetime]] = {}
        self.domain_counts: Dict[str, int] = {}

        # Robots.txt cache
        self.robots_cache: Dict[str, Tuple[RobotFileParser, datetime]] = {}

        # Content cache
        self.content_cache: Dict[str, ScrapedContent] = {}
        self.cache_expiry = timedelta(hours=24)

        # Selenium for JavaScript-heavy sites
        self.selenium_driver: Optional[Any] = None

    async def __aenter__(self):
        timeout = aiohttp.ClientTimeout(total=self.config.timeout)
        self.session = aiohttp.ClientSession(timeout=timeout)

        # Initialize new scraping session
        self.current_session = ScrapingSession(session_id=f"scrape_{int(time.time())}")

        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

        if self.selenium_driver:
            self.selenium_driver.quit()

    async def research_topic(
        self, topic: str, search_queries: List[SearchQuery], max_results: int = 50
    ) -> List[ScrapedContent]:
        """
        Comprehensive research scraping for a topic.

        Args:
            topic: Research topic
            search_queries: List of search queries to execute
            max_results: Maximum number of results to return

        Returns:
            List of scraped content with relevance and quality scores
        """

        if not self.current_session:
            raise RuntimeError("Scraper not properly initialized")

        self.logger.info(f"Starting research on topic: {topic}")

        # Generate search URLs and collect candidate URLs
        candidate_urls = await self._execute_searches(search_queries)

        # Filter and prioritize URLs
        filtered_urls = self._filter_candidate_urls(candidate_urls, topic)

        # Scrape content with rate limiting and quality checks
        scraped_content = await self._scrape_content_batch(
            filtered_urls, topic, max_results
        )

        # Score and rank content
        scored_content = []
        for content in scraped_content:
            content.relevance_score = self._calculate_relevance_score(content, topic)
            content.quality_score = self._assess_content_quality(content)
            scored_content.append(content)

        # Sort by combined score and return top results
        scored_content.sort(
            key=lambda x: (x.relevance_score + x.quality_score) / 2, reverse=True
        )

        top_content = scored_content[:max_results]

        self.logger.info(
            f"Research completed: {len(top_content)} high-quality results collected"
        )
        return top_content

    async def _execute_searches(self, search_queries: List[SearchQuery]) -> List[str]:
        """Execute search queries and collect candidate URLs."""
        candidate_urls = []

        for query in search_queries:
            try:
                if query.search_engine == "google":
                    urls = await self._search_google(query)
                elif query.search_engine == "bing":
                    urls = await self._search_bing(query)
                elif query.search_engine == "duckduckgo":
                    urls = await self._search_duckduckgo(query)
                else:
                    self.logger.warning(
                        f"Unsupported search engine: {query.search_engine}"
                    )
                    continue

                candidate_urls.extend(urls)
                await asyncio.sleep(self.config.request_delay)

            except Exception as e:
                self.logger.error(f"Search failed for query '{query.query}': {e}")
                continue

        # Remove duplicates while preserving order
        seen = set()
        unique_urls = []
        for url in candidate_urls:
            if url not in seen:
                seen.add(url)
                unique_urls.append(url)

        return unique_urls

    async def _search_google(self, query: SearchQuery) -> List[str]:
        """Search using Google Custom Search API or fallback to scraping."""
        urls = []

        # Try API first if available
        api_key = os.getenv("GOOGLE_SEARCH_API_KEY")
        cx = os.getenv("GOOGLE_SEARCH_CX")

        if api_key and cx and self.session:
            try:
                api_url = "https://www.googleapis.com/customsearch/v1"
                params: Dict[str, Union[str, int]] = {
                    "key": api_key,
                    "cx": cx,
                    "q": query.query,
                    "num": min(query.num_results, 10),
                    "hl": query.language,
                    "gl": query.region,
                }

                if query.time_filter:
                    date_restrict = {
                        "day": "d1",
                        "week": "w1",
                        "month": "m1",
                        "year": "y1",
                    }
                    params["dateRestrict"] = date_restrict.get(query.time_filter, "")

                async with self.session.get(api_url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        urls = [item["link"] for item in data.get("items", [])]
                        self.logger.info(f"Google API returned {len(urls)} results")
                        return urls

            except Exception as e:
                self.logger.warning(f"Google API search failed: {e}")

        # Fallback to scraping Google results
        return await self._scrape_google_results(query)

    async def _scrape_google_results(self, query: SearchQuery) -> List[str]:
        """Scrape Google search results (use carefully to avoid blocking)."""
        urls = []

        try:
            search_url = f"https://www.google.com/search?q={quote_plus(query.query)}&num={query.num_results}"

            headers = {"User-Agent": self._get_user_agent()}

            if self.session:
                async with self.session.get(search_url, headers=headers) as response:
                    if response.status == 200:
                        html = await response.text()
                        soup = BeautifulSoup(html, "html.parser")

                        # Extract result URLs
                        for link in soup.find_all("a", href=True):
                            href = str(link["href"])
                            if href.startswith("/url?q="):
                                url = href.split("/url?q=")[1].split("&")[0]
                                if url.startswith("http") and not any(
                                    skip in url for skip in ["google", "youtube.com"]
                                ):
                                    urls.append(url)

                        urls = urls[: query.num_results]  # Limit results

        except Exception as e:
            self.logger.error(f"Google scraping failed: {e}")

        return urls

    async def _search_bing(self, query: SearchQuery) -> List[str]:
        """Search using Bing Web Search API or fallback."""
        urls = []

        # Try API first
        api_key = os.getenv("BING_SEARCH_API_KEY")
        if api_key and self.session:
            try:
                api_url = "https://api.bing.microsoft.com/v7.0/search"
                headers = {"Ocp-Apim-Subscription-Key": api_key}
                params: Dict[str, Union[str, int]] = {
                    "q": query.query,
                    "count": min(query.num_results, 50),
                    "mkt": f"{query.language}-{query.region}",
                }

                async with self.session.get(
                    api_url, headers=headers, params=params
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        urls = [
                            result["url"]
                            for result in data.get("webPages", {}).get("value", [])
                        ]
                        return urls

            except Exception as e:
                self.logger.warning(f"Bing API search failed: {e}")

        # Fallback to scraping
        return await self._scrape_bing_results(query)

    async def _scrape_bing_results(self, query: SearchQuery) -> List[str]:
        """Scrape Bing search results."""
        assert self.session is not None
        urls = []

        try:
            search_url = f"https://www.bing.com/search?q={quote_plus(query.query)}&count={query.num_results}"

            headers = {"User-Agent": self._get_user_agent()}

            async with self.session.get(search_url, headers=headers) as response:
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, "html.parser")

                    for link in soup.find_all("a", {"class": "tilk"}):
                        href = link.get("href")
                        if href and str(href).startswith("http"):
                            urls.append(str(href))

        except Exception as e:
            self.logger.error(f"Bing scraping failed: {e}")

        return urls

    async def _search_duckduckgo(self, query: SearchQuery) -> List[str]:
        """Search using DuckDuckGo (no API key required)."""
        urls = []

        try:
            search_url = f"https://duckduckgo.com/html/?q={quote_plus(query.query)}"

            headers = {"User-Agent": self._get_user_agent()}

            if self.session:
                async with self.session.get(search_url, headers=headers) as response:
                    if response.status == 200:
                        html = await response.text()
                        soup = BeautifulSoup(html, "html.parser")

                        for link in soup.find_all("a", {"class": "result__url"}):
                            href = link.get("href")
                            if href and str(href).startswith("http"):
                                urls.append(str(href))

                        # Also check for regular links
                        for link in soup.find_all("a", href=True):
                            href = str(link["href"])
                            if href.startswith("//"):
                                href = "https:" + href
                            if href.startswith("http") and "duckduckgo" not in href:
                                urls.append(href)

        except Exception as e:
            self.logger.error(f"DuckDuckGo search failed: {e}")

        return list(set(urls))[: query.num_results]  # Remove duplicates

    def _filter_candidate_urls(self, urls: List[str], topic: str) -> List[str]:
        """Filter and prioritize candidate URLs."""
        filtered = []

        for url in urls:
            try:
                parsed = urlparse(url)
                domain = parsed.netloc

                # Skip if we've already scraped too many pages from this domain
                if (
                    self.domain_counts.get(domain, 0)
                    >= self.config.max_pages_per_domain
                ):
                    continue

                # Basic URL validation
                if not self._is_valid_url(url):
                    continue

                # Check robots.txt if enabled
                if self.config.respect_robots_txt and not self._can_fetch_url(url):
                    continue

                filtered.append(url)

            except Exception:
                continue

        # Prioritize URLs based on topic relevance in URL
        topic_words = set(topic.lower().split())
        prioritized = sorted(
            filtered,
            key=lambda u: len(topic_words.intersection(set(u.lower().split("/")))),
            reverse=True,
        )

        return prioritized[:100]  # Reasonable limit

    async def _scrape_content_batch(
        self, urls: List[str], topic: str, max_results: int
    ) -> List[ScrapedContent]:
        """Scrape content from URLs in batches with rate limiting."""
        assert self.current_session is not None
        session = self.current_session
        scraped_content: List[ScrapedContent] = []
        semaphore = asyncio.Semaphore(self.config.max_concurrent_requests)

        async def scrape_with_semaphore(url: str) -> Optional[ScrapedContent]:
            async with semaphore:
                content = await self._scrape_single_url(url, topic)
                if content:
                    session.total_requests += 1
                    session.successful_requests += 1
                    return content
                else:
                    session.total_requests += 1
                    session.failed_requests += 1
                    return None

        # Create tasks for batch processing
        tasks = [
            scrape_with_semaphore(url) for url in urls[: max_results * 2]
        ]  # Get more than needed for quality filtering

        # Process in smaller batches to avoid overwhelming
        batch_size = self.config.max_concurrent_requests * 2
        all_results = []

        for i in range(0, len(tasks), batch_size):
            batch = tasks[i : i + batch_size]
            batch_results = await asyncio.gather(*batch, return_exceptions=True)

            for result in batch_results:
                if isinstance(result, ScrapedContent):
                    all_results.append(result)

            # Rate limiting between batches
            await asyncio.sleep(self.config.request_delay)

        # Filter for quality and relevance
        quality_content = [
            content
            for content in all_results
            if content and len(content.content) >= self.config.min_content_length
        ]

        return quality_content[:max_results]

    async def _scrape_single_url(
        self, url: str, topic: str
    ) -> Optional[ScrapedContent]:
        """Scrape content from a single URL with comprehensive error handling."""

        # Check cache first
        cache_key = hashlib.md5(url.encode()).hexdigest()
        cache_file = self.cache_dir / f"{cache_key}.json"

        if cache_file.exists():
            try:
                with open(cache_file, "r") as f:
                    cached_data = json.load(f)
                    cached_time = datetime.fromisoformat(cached_data["scraped_at"])

                    if datetime.now() - cached_time < self.cache_expiry:
                        self.logger.debug(f"Using cached content for {url}")
                        return ScrapedContent(**cached_data)
            except Exception:
                pass  # Cache miss

        # Rate limiting
        await self._enforce_rate_limit(url)

        # Try multiple scraping methods
        content = None

        # Method 1: Standard HTTP request
        content = await self._scrape_with_requests(url)
        if not content:
            # Method 2: Selenium for JavaScript-heavy sites
            content = await self._scrape_with_selenium(url)

        if content:
            # Post-process content
            content = self._post_process_content(content, url)

            # Cache the result
            try:
                cache_data = {
                    "url": content.url,
                    "title": content.title,
                    "content": content.content,
                    "summary": content.summary,
                    "metadata": content.metadata,
                    "scraped_at": content.scraped_at.isoformat(),
                    "content_type": content.content_type,
                    "word_count": content.word_count,
                    "relevance_score": content.relevance_score,
                    "quality_score": content.quality_score,
                    "source_domain": content.source_domain,
                    "content_hash": content.content_hash,
                    "links": content.links,
                    "images": content.images,
                    "headers": content.headers,
                }

                with open(cache_file, "w") as f:
                    json.dump(cache_data, f, indent=2)

            except Exception as e:
                self.logger.warning(f"Failed to cache content for {url}: {e}")

        return content

    async def _scrape_with_requests(self, url: str) -> Optional[ScrapedContent]:
        """Scrape using standard HTTP requests."""
        for attempt in range(self.config.retry_attempts + 1):
            try:
                headers = {"User-Agent": self._get_user_agent()}

                if self.session:
                    async with self.session.get(
                        url, headers=headers, allow_redirects=True
                    ) as response:
                        if response.status != 200:
                            return None

                        # Check content type
                        content_type = response.headers.get("content-type", "").lower()
                        if not any(
                            ct in content_type for ct in ["text/html", "text/plain"]
                        ):
                            return None

                        # Check content length
                        content_length = response.headers.get("content-length")
                        if (
                            content_length
                            and int(content_length) > self.config.max_content_length
                        ):
                            return None

                        html = await response.text()

                        # Parse content
                        soup = BeautifulSoup(html, "lxml")

                        # Extract title
                        title = self._extract_title(soup)

                        # Extract main content
                        content = self._extract_main_content(soup)

                        if not content or len(content) < self.config.min_content_length:
                            return None

                        # Extract metadata
                        metadata = self._extract_metadata(soup, dict(response.headers))

                    # Extract links and images
                    links = self._extract_links(soup, url)
                    images = self._extract_images(soup, url)

                    # Create content hash
                    content_hash = hashlib.md5(content.encode()).hexdigest()

                    # Update domain count
                    domain = urlparse(url).netloc
                    self.domain_counts[domain] = self.domain_counts.get(domain, 0) + 1

                    return ScrapedContent(
                        url=url,
                        title=title,
                        content=content,
                        metadata=metadata,
                        content_type="html",
                        word_count=len(content.split()),
                        source_domain=domain,
                        content_hash=content_hash,
                        links=links,
                        images=images,
                        headers=dict(response.headers),
                    )

            except Exception as e:
                if attempt == self.config.retry_attempts:
                    self.logger.debug(
                        f"Failed to scrape {url} after {attempt + 1} attempts: {e}"
                    )
                    return None
                await asyncio.sleep(self.config.retry_delay * (2**attempt))

        return None

    async def _scrape_with_selenium(self, url: str) -> Optional[ScrapedContent]:
        """Scrape using Selenium for JavaScript-heavy sites."""
        if not self.selenium_driver and webdriver and ChromeDriverManager and Options:
            try:
                options = Options()
                options.add_argument("--headless")
                options.add_argument("--no-sandbox")
                options.add_argument("--disable-dev-shm-usage")
                options.add_argument("--disable-gpu")
                options.add_argument(f"--user-agent={self._get_user_agent()}")

                self.selenium_driver = webdriver.Chrome(
                    ChromeDriverManager().install(), options=options
                )
            except Exception as e:
                self.logger.warning(f"Failed to initialize Selenium: {e}")
                return None

        if not self.selenium_driver:
            return None

        try:
            self.selenium_driver.get(url)

            # Wait for content to load
            if WebDriverWait:
                WebDriverWait(self.selenium_driver, 10).until(
                    lambda driver: driver.execute_script("return document.readyState")
                    == "complete"
                )

            # Get page source
            html = self.selenium_driver.page_source
            soup = BeautifulSoup(html, "lxml")

            # Extract content as in regular scraping
            title = self._extract_title(soup)
            content = self._extract_main_content(soup)

            if not content or len(content) < self.config.min_content_length:
                return None

            metadata = self._extract_metadata(soup, {})
            links = self._extract_links(soup, url)
            images = self._extract_images(soup, url)
            content_hash = hashlib.md5(content.encode()).hexdigest()
            domain = urlparse(url).netloc

            return ScrapedContent(
                url=url,
                title=title,
                content=content,
                metadata=metadata,
                content_type="html",
                word_count=len(content.split()),
                source_domain=domain,
                content_hash=content_hash,
                links=links,
                images=images,
            )

        except Exception as e:
            self.logger.warning(f"Selenium scraping failed for {url}: {e}")
            return None

    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extract page title."""
        title_tag = soup.find("title")
        if title_tag and title_tag.get_text().strip():
            return title_tag.get_text().strip()

        # Fallback to h1
        h1_tag = soup.find("h1")
        if h1_tag and h1_tag.get_text().strip():
            return h1_tag.get_text().strip()

        return "Untitled Page"

    def _extract_main_content(self, soup: BeautifulSoup) -> str:
        """Extract main content from HTML."""
        # Remove unwanted elements
        for selector in [
            "script",
            "style",
            "nav",
            "header",
            "footer",
            "aside",
            "advertisement",
            ".ad",
            ".ads",
        ]:
            for element in soup.select(selector):
                element.decompose()

        # Try to find main content areas
        content_selectors = [
            "main",
            '[role="main"]',
            ".content",
            ".post-content",
            ".entry-content",
            "article",
            ".article-content",
            ".post",
            ".entry",
        ]

        for selector in content_selectors:
            main_content = soup.select_one(selector)
            if main_content:
                text = main_content.get_text(separator=" ", strip=True)
                if len(text) > self.config.min_content_length:
                    return text

        # Fallback to body text with filtering
        body = soup.find("body")
        if body:
            # Remove common non-content elements
            for tag in body.find_all(
                ["nav", "header", "footer", "aside", "script", "style"]
            ):
                tag.decompose()

            text = body.get_text(separator=" ", strip=True)

            # Clean up whitespace
            text = re.sub(r"\s+", " ", text).strip()

            return text

        return ""

    def _extract_metadata(
        self, soup: BeautifulSoup, headers: Dict[str, str]
    ) -> Dict[str, Any]:
        """Extract metadata from page."""
        metadata: Dict[str, Any] = {}

        # Meta tags
        meta_tags = soup.find_all("meta")
        for tag in meta_tags:
            name = str(tag.get("name") or tag.get("property") or "")
            content = tag.get("content")
            if name and content:
                metadata[name] = content

        # Open Graph tags
        og_tags = soup.find_all("meta", property=lambda x: x is not None and x.startswith("og:"))
        for tag in og_tags:
            prop = tag["property"][3:]  # Remove 'og:' prefix
            content = tag.get("content")
            if prop and content:
                metadata[f"og_{prop}"] = content

        # Headers
        metadata["content_type"] = headers.get("content-type")
        metadata["last_modified"] = headers.get("last-modified")

        # Page info
        metadata["has_title"] = bool(soup.find("title"))
        metadata["has_h1"] = bool(soup.find("h1"))
        metadata["paragraph_count"] = len(soup.find_all("p"))
        metadata["link_count"] = len(soup.find_all("a", href=True))

        return metadata

    def _extract_links(self, soup: BeautifulSoup, base_url: str) -> List[str]:
        """Extract all links from the page."""
        links = []
        for link in soup.find_all("a", href=True):
            href = str(link["href"])
            absolute_url = urljoin(base_url, href)
            if (
                absolute_url.startswith("http")
                and urlparse(absolute_url).netloc != urlparse(base_url).netloc
            ):
                links.append(absolute_url)
        return links[:50]  # Limit to avoid excessive data

    def _extract_images(self, soup: BeautifulSoup, base_url: str) -> List[str]:
        """Extract image URLs from the page."""
        images = []
        for img in soup.find_all("img", src=True):
            src = str(img["src"])
            absolute_url = urljoin(base_url, src)
            if absolute_url.startswith("http"):
                images.append(absolute_url)
        return images[:20]  # Reasonable limit

    def _post_process_content(
        self, content: ScrapedContent, url: str
    ) -> ScrapedContent:
        """Post-process scraped content."""
        # Clean content
        content.content = self._clean_content(content.content)

        # Generate summary if needed
        if not content.summary and len(content.content) > 1000:
            content.summary = self._generate_summary(content.content)

        return content

    def _clean_content(self, text: str) -> str:
        """Clean and normalize content text."""
        # Remove excessive whitespace
        text = re.sub(r"\s+", " ", text)

        # Remove common artifacts
        text = re.sub(r"\[.*?\]", "", text)  # Remove [text] patterns
        text = re.sub(r"https?://\S+", "", text)  # Remove URLs
        text = re.sub(r"\b\d{1,2}/\d{1,2}/\d{2,4}\b", "", text)  # Remove dates

        # Normalize quotes
        text = text.replace('"', '"').replace('"', '"')
        text = text.replace(""", "'").replace(""", "'")

        return text.strip()

    def _generate_summary(self, content: str, max_length: int = 300) -> str:
        """Generate a simple extractive summary."""
        sentences = re.split(r"[.!?]+", content)
        sentences = [s.strip() for s in sentences if len(s.strip()) > 20]

        # Simple scoring based on position and length
        scored_sentences = []
        for i, sentence in enumerate(sentences[:10]):  # First 10 sentences
            score = (10 - i) * 0.1 + len(
                sentence
            ) * 0.001  # Prefer early, longer sentences
            scored_sentences.append((score, sentence))

        # Select top sentences
        scored_sentences.sort(reverse=True)
        summary_sentences = [sentence for _, sentence in scored_sentences[:3]]

        summary = ". ".join(summary_sentences)
        if len(summary) > max_length:
            summary = summary[:max_length].rsplit(" ", 1)[0] + "..."

        return summary

    def _calculate_relevance_score(self, content: ScrapedContent, topic: str) -> float:
        """Calculate relevance score for content."""
        score = 0.0

        # Title relevance
        title_lower = content.title.lower()
        topic_lower = topic.lower()

        if topic_lower in title_lower:
            score += 0.3

        # Content relevance
        content_lower = content.content.lower()
        topic_words = set(topic_lower.split())

        # Exact matches
        exact_matches = sum(1 for word in topic_words if word in content_lower)
        score += min(exact_matches * 0.1, 0.4)

        # Partial matches (stemming would be better here)
        partial_matches = sum(
            1
            for word in topic_words
            if any(word in token for token in content_lower.split())
        )
        score += min(partial_matches * 0.05, 0.2)

        # Content quality indicators
        if len(content.content) > 2000:
            score += 0.1

        # Metadata quality
        if content.metadata.get("description"):
            score += 0.1

        # Recency bonus (if available)
        if "last-modified" in content.metadata:
            score += 0.05

        return min(score, 1.0)

    def _assess_content_quality(self, content: ScrapedContent) -> float:
        """Assess overall content quality."""
        score = 0.0

        # Length check
        if len(content.content) > 1000:
            score += 0.2

        # Structure indicators
        if content.metadata.get("has_h1"):
            score += 0.15

        if content.metadata.get("paragraph_count", 0) > 3:
            score += 0.15

        # Link diversity
        if len(content.links) > 5:
            score += 0.1

        # Metadata completeness
        metadata_score = sum(
            1
            for key in ["description", "keywords", "author"]
            if content.metadata.get(key)
        )
        score += metadata_score * 0.05

        # Content readability (simple heuristic)
        avg_word_length = sum(len(word) for word in content.content.split()) / max(
            len(content.content.split()), 1
        )
        if 4 < avg_word_length < 8:
            score += 0.1

        # No spam indicators
        spam_indicators = ["buy now", "click here", "subscribe", "free trial"]
        spam_count = sum(
            1 for indicator in spam_indicators if indicator in content.content.lower()
        )
        score -= spam_count * 0.1

        return max(0.0, min(score, 1.0))

    async def _enforce_rate_limit(self, url: str):
        """Enforce rate limiting for requests."""
        domain = urlparse(url).netloc
        now = datetime.now()

        if domain not in self.request_times:
            self.request_times[domain] = []

        # Clean old timestamps
        cutoff = now - timedelta(seconds=self.config.request_delay)
        self.request_times[domain] = [
            t for t in self.request_times[domain] if t > cutoff
        ]

        # Check if we need to wait
        if len(self.request_times[domain]) >= self.config.max_concurrent_requests:
            oldest_request = min(self.request_times[domain])
            wait_time = (
                self.config.request_delay - (now - oldest_request).total_seconds()
            )
            if wait_time > 0:
                await asyncio.sleep(wait_time)

        self.request_times[domain].append(now)

    def _is_valid_url(self, url: str) -> bool:
        """Check if URL is valid and suitable for scraping."""
        try:
            parsed = urlparse(url)

            # Basic validation
            if not parsed.scheme or not parsed.netloc:
                return False

            if parsed.scheme not in ["http", "https"]:
                return False

            # Skip common non-content domains
            skip_domains = [
                "google",
                "facebook",
                "twitter",
                "instagram",
                "youtube",
                "amazon",
                "ebay",
            ]
            if any(domain in parsed.netloc for domain in skip_domains):
                return False

            # Skip file extensions that aren't HTML
            skip_extensions = [
                ".pdf",
                ".doc",
                ".docx",
                ".xls",
                ".xlsx",
                ".ppt",
                ".pptx",
                ".zip",
                ".rar",
                ".7z",
                ".tar",
                ".gz",
                ".mp3",
                ".mp4",
                ".avi",
            ]
            if any(url.lower().endswith(ext) for ext in skip_extensions):
                return False

            return True

        except Exception:
            return False

    def _can_fetch_url(self, url: str) -> bool:
        """Check if we can fetch URL according to robots.txt."""
        try:
            parsed = urlparse(url)
            robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"

            # Check cache first
            if robots_url in self.robots_cache:
                rp, cache_time = self.robots_cache[robots_url]
                if datetime.now() - cache_time < timedelta(hours=24):
                    return rp.can_fetch("*", url)

            # Fetch and parse robots.txt
            rp = RobotFileParser()
            rp.set_url(robots_url)
            rp.read()

            # Cache the result
            self.robots_cache[robots_url] = (rp, datetime.now())

            return rp.can_fetch("*", url)

        except Exception:
            # If we can't read robots.txt, assume we can fetch
            return True

    def _get_user_agent(self) -> str:
        """Get a user agent string."""
        if self.ua:
            return self.ua.random
        return "LifePlanResearchBot/1.0 (https://lifeplan.ai/research)"

    def get_session_stats(self) -> Dict[str, Any]:
        """Get statistics for the current scraping session."""
        if not self.current_session:
            return {}

        session = self.current_session
        duration = datetime.now() - session.start_time

        return {
            "session_id": session.session_id,
            "duration_seconds": duration.total_seconds(),
            "total_requests": session.total_requests if session else 0,
            "successful_requests": session.successful_requests if session else 0,
            "failed_requests": session.failed_requests if session else 0,
            "success_rate": session.successful_requests
            / max(session.total_requests if session else 1, 1),
            "domains_scraped": len(session.domains_scraped) if session else 0,
            "content_collected": session.content_collected if session else 0,
            "errors": session.errors if session else [],
        }

    def cleanup_cache(self, max_age_hours: int = 24):
        """Clean up old cache entries to prevent memory leaks."""
        from datetime import datetime, timedelta
        cutoff_time = datetime.now() - timedelta(hours=max_age_hours)

        # Clean content cache
        urls_to_remove = []
        for url, content in self.content_cache.items():
            if content.scraped_at < cutoff_time:
                urls_to_remove.append(url)

        for url in urls_to_remove:
            del self.content_cache[url]

        # Clean robots cache
        robots_to_remove = []
        for url, (rp, cache_time) in self.robots_cache.items():
            if cache_time < cutoff_time:
                robots_to_remove.append(url)

        for url in robots_to_remove:
            del self.robots_cache[url]

        # Clean old cache files
        if hasattr(self, 'cache_dir') and self.cache_dir.exists():
            for cache_file in self.cache_dir.glob("*.json"):
                if cache_file.stat().st_mtime < cutoff_time.timestamp():
                    cache_file.unlink()

        self.logger.info(f"Cleaned up {len(urls_to_remove)} content cache entries, "
                        f"{len(robots_to_remove)} robots cache entries")
