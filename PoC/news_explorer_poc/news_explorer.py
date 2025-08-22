#!/usr/bin/env python3
"""
News Explorer PoC

Discover news and trends without predefined sources using:
- Tavily search for discovery (requires TAVILY_API_KEY)
- requests + trafilatura for content extraction
- Simple scoring, deduplication, and summarization
"""

import json
import logging
import hashlib
import time
import re
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import List, Dict, Optional
from urllib.parse import urlparse
import os

# Load environment variables from .env file
try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass  # python-dotenv not available

import requests
import trafilatura
from tavily import TavilyClient

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
)
HEADERS = {"User-Agent": USER_AGENT}

DEFAULT_QUERIES = [
    "latest ai news",
    "trending artificial intelligence",
    "machine learning breakthroughs",
    "deep learning research news",
    "ai startup funding news",
]

# Optional: Tavily API key (if set, we will use Tavily as an additional search provider)
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

BLOCKLIST_DOMAINS = {
    "facebook.com",
    "x.com",
    "twitter.com",
    "t.co",
    "reddit.com",
    "medium.com/@",  # author pages
}


@dataclass
class DiscoveredItem:
    title: str
    url: str
    source_domain: str
    summary: str
    published_at: Optional[str]
    topic: str
    score: float
    content_hash: str

    def to_dict(self) -> Dict:
        return asdict(self)


def normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip().lower()


def hash_content(text: str) -> str:
    return hashlib.md5(text.encode("utf-8")).hexdigest()


def is_blocked(url: str) -> bool:
    domain = urlparse(url).netloc.lower()
    return any(b in domain for b in BLOCKLIST_DOMAINS)


## DuckDuckGo support removed; Tavily is the sole search provider


def tavily_search(query: str, max_results: int = 10) -> List[str]:
    """Use Tavily search API if API key is present; return list of URLs."""
    if not TAVILY_API_KEY:
        logger.info("No TAVILY_API_KEY set, skipping Tavily search")
        return []
    try:
        logger.info(f"Using Tavily API key: {TAVILY_API_KEY[:10]}...")
        client = TavilyClient(api_key=TAVILY_API_KEY)
        logger.info(f"Tavily client created, searching for: {query}")
        res = client.search(query=query, max_results=max_results)
        logger.info(f"Tavily response: {res}")
        urls: List[str] = []
        # Tavily returns dict with 'results': [{"url": ..., "title": ...}, ...]
        for item in res.get("results", []):
            url = item.get("url")
            if url and url.startswith("http") and not is_blocked(url):
                urls.append(url)
            if len(urls) >= max_results:
                break
        logger.info(f"Extracted {len(urls)} URLs from Tavily response")
        return urls
    except Exception as e:
        logger.warning(f"Tavily search failed for '{query}': {e}")
        return []


def extract_content(url: str) -> Dict:
    """Fetch and extract article-like content using trafilatura."""
    try:
        # Use shorter timeout and better error handling
        downloaded = trafilatura.fetch_url(url, timeout=15)
        if not downloaded:
            return {}
        extracted = trafilatura.extract(
            downloaded,
            include_comments=False,
            include_tables=False,
            with_metadata=True,
            favor_recall=True,
        )
        if not extracted:
            return {}
        data = trafilatura.bare_extraction(downloaded, with_metadata=True)
        title = data.get("title") if data else None
        summary = (extracted[:1000] + "...") if extracted else ""
        date = data.get("date") if data else None
        # Normalize date
        published_at = None
        if date:
            try:
                published_at = (
                    datetime.fromisoformat(date).astimezone(timezone.utc).isoformat()
                )
            except Exception:
                published_at = date
        return {
            "title": title or "",
            "summary": summary or "",
            "published_at": published_at,
        }
    except Exception as e:
        logger.debug(f"Extraction error for {url}: {e}")
        return {}


def compute_score(published_at: Optional[str], serp_rank: int, domain: str) -> float:
    score = 0.0
    # Freshness
    if published_at:
        try:
            dt = datetime.fromisoformat(published_at.replace("Z", "+00:00"))
            age_days = (datetime.now(timezone.utc) - dt).total_seconds() / 86400.0
            score += max(0.0, 5.0 - min(5.0, age_days))  # up to +5
        except Exception:
            pass
    # SERP weight (higher rank => higher score)
    score += max(0.0, 3.0 - (serp_rank * 0.2))  # up to +3
    # Domain heuristic
    reputable = {
        "techcrunch.com",
        "theverge.com",
        "wired.com",
        "mit.edu",
        "arxiv.org",
        "nature.com",
        "venturebeat.com",
    }
    if any(d in domain for d in reputable):
        score += 1.0
    return round(score, 3)


def explore_news(
    queries: List[str], per_query: int = 8, delay_sec: float = 1.0
) -> List[DiscoveredItem]:
    seen_urls = set()
    seen_titles = set()
    items: List[DiscoveredItem] = []

    for query in queries:
        logger.info(f"Searching: {query}")
        links = []
        tavily_results = []

        # Use Tavily as the sole search provider
        tavily_links = tavily_search(query, max_results=per_query)
        logger.info(f"Tavily returned {len(tavily_links)} links for '{query}'")

        # Store Tavily results for fallback
        if TAVILY_API_KEY:
            try:
                client = TavilyClient(api_key=TAVILY_API_KEY)
                res = client.search(query=query, max_results=per_query)
                tavily_results = res.get("results", [])
            except Exception as e:
                logger.warning(f"Failed to get Tavily results for fallback: {e}")

        for u in tavily_links:
            if u not in links:
                links.append(u)
        logger.info(f"Combined unique links: {len(links)}")

        for idx, url in enumerate(links):
            if url in seen_urls:
                continue
            seen_urls.add(url)
            domain = urlparse(url).netloc
            logger.info(f"Processing {idx+1}/{len(links)}: {domain}")

            try:
                content = extract_content(url)
                logger.info(
                    f"Content extraction result for {url}: {bool(content)}, title: {content.get('title', 'N/A')[:50] if content else 'N/A'}, summary: {bool(content.get('summary')) if content else False}"
                )

                # If content extraction failed, try to use Tavily content as fallback
                if (
                    not content
                    or not content.get("title")
                    or not content.get("summary")
                ):
                    logger.info(
                        f"Content extraction failed, trying Tavily fallback for {url}"
                    )
                    tavily_fallback = None
                    for result in tavily_results:
                        if result.get("url") == url:
                            tavily_fallback = result
                            break

                    if (
                        tavily_fallback
                        and tavily_fallback.get("title")
                        and tavily_fallback.get("content")
                    ):
                        logger.info(f"Using Tavily fallback for {url}")
                        content = {
                            "title": tavily_fallback["title"],
                            "summary": (
                                tavily_fallback["content"][:1000] + "..."
                                if len(tavily_fallback["content"]) > 1000
                                else tavily_fallback["content"]
                            ),
                            "published_at": None,
                        }
                    else:
                        logger.debug(
                            f"Skipping {url}: no content/title/summary and no Tavily fallback"
                        )
                        continue

                title_norm = normalize_text(content["title"])
                if title_norm in seen_titles:
                    logger.debug(f"Skipping {url}: duplicate title")
                    continue
                seen_titles.add(title_norm)

                score = compute_score(content.get("published_at"), idx, domain)
                content_hash = hash_content(f"{content['title']}|{url}")
                items.append(
                    DiscoveredItem(
                        title=content["title"],
                        url=url,
                        source_domain=domain,
                        summary=content["summary"],
                        published_at=content.get("published_at"),
                        topic=query,
                        score=score,
                        content_hash=content_hash,
                    )
                )
                logger.info(f"Added item: {content['title'][:50]}...")
            except Exception as e:
                logger.warning(f"Error processing {url}: {e}")
                continue

            time.sleep(0.2)
        time.sleep(delay_sec)
    return items


def summarize_topics(items: List[DiscoveredItem]) -> Dict[str, int]:
    counts: Dict[str, int] = {}
    for it in items:
        counts[it.topic] = counts.get(it.topic, 0) + 1
    return counts


def save_results(items: List[DiscoveredItem]) -> str:
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = f"explorer_output_{ts}.json"
    payload = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "total_items": len(items),
        "topics": summarize_topics(items),
        "items": [it.to_dict() for it in items],
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)
    logger.info(f"Saved results to {path}")
    return path


def main():
    logger.info("News Explorer PoC starting...")
    items = explore_news(DEFAULT_QUERIES, per_query=6, delay_sec=1.0)
    if not items:
        logger.warning("No items discovered.")
    save_results(items)
    logger.info("Done.")


if __name__ == "__main__":
    main()
