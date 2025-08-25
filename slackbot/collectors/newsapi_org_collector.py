#!/usr/bin/env python3
"""
NewsAPI.org News Collector

This collector fetches news articles from NewsAPI.org API.
Specialized for general news content and current events.
"""

import os
import logging
import hashlib
import time
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict

# Third-party imports
try:
    from newsapi import NewsApiClient

    DEPENDENCIES_AVAILABLE = True
except ImportError:
    logging.warning("Required dependencies not available. Install with: pip install newsapi-python")
    DEPENDENCIES_AVAILABLE = False
    NewsApiClient = None

from .base_collector import BaseCollector

logger = logging.getLogger(__name__)


@dataclass
class NewsAPISource:
    """Represents a configurable NewsAPI source."""

    name: str
    query: str
    enabled: bool = True
    max_items: int = 10
    category: Optional[str] = None
    language: str = "en"
    country: str = "us"
    domains: Optional[str] = None
    update_interval: int = 3600  # 1 hour in seconds
    last_fetch: Optional[datetime] = None

    def to_dict(self) -> Dict:
        """Convert source to dictionary for serialization."""
        data = asdict(self)
        if self.last_fetch:
            data["last_fetch"] = self.last_fetch.isoformat()
        return data

    @classmethod
    def from_dict(cls, data: Dict) -> "NewsAPISource":
        """Create NewsAPISource from dictionary."""
        source = cls(
            name=data["name"],
            query=data["query"],
            enabled=data.get("enabled", True),
            max_items=data.get("max_items", 10),
            category=data.get("category"),
            language=data.get("language", "en"),
            country=data.get("country", "us"),
            domains=data.get("domains"),
            update_interval=data.get("update_interval", 3600),
        )

        if data.get("last_fetch"):
            source.last_fetch = datetime.fromisoformat(data["last_fetch"])

        return source


@dataclass
class NewsAPIArticle:
    """Represents a NewsAPI article."""

    title: str
    url: str
    source: str
    category: str
    summary: str
    published_at: Optional[str] = None
    content: Optional[str] = None
    api_data: Optional[Dict] = None

    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization."""
        return asdict(self)


class NewsAPICollector(BaseCollector):
    """NewsAPI.org news collector service."""

    def __init__(self, name: str = "NewsAPI Collector"):
        super().__init__(name=name)

        self.sources = []
        self.articles_cache = {}  # Cache for deduplication
        self.newsapi_client = None

        # Load default NewsAPI sources
        self.load_default_sources()
        self.initialize_newsapi_client()

    def initialize_newsapi_client(self):
        """Initialize NewsAPI client."""
        try:
            # Initialize NewsAPI client
            newsapi_key = os.getenv("NEWSAPI_KEY")
            if newsapi_key:
                self.newsapi_client = NewsApiClient(api_key=newsapi_key)
                logger.info("NewsAPI client initialized successfully")
            else:
                logger.warning("NEWSAPI_KEY environment variable not set. NewsAPI features will be disabled.")

        except Exception as e:
            logger.error(f"Error initializing NewsAPI client: {e}")

    def is_available(self) -> bool:
        """Check if the collector is available and ready to use."""
        return DEPENDENCIES_AVAILABLE and self.newsapi_client

    def load_default_sources(self):
        """Load default NewsAPI sources."""
        default_sources = [
            NewsAPISource(
                name="Tech News AI",
                query="artificial intelligence OR AI",
                category="technology",
                language="en",
                country="us",
                max_items=15,
            ),
            NewsAPISource(
                name="Business AI News",
                query="AI",
                category="business",
                language="en",
                country="us",
                max_items=10,
            ),
            NewsAPISource(
                name="Science AI News",
                query="AI",
                category="science",
                language="en",
                country="us",
                max_items=10,
            ),
            NewsAPISource(
                name="Health AI News",
                query="AI",
                category="health",
                language="en",
                country="us",
                max_items=10,
            ),
        ]

        self.sources = default_sources
        logger.info(f"Loaded {len(default_sources)} NewsAPI sources")

    def should_update_source(self, source: NewsAPISource) -> bool:
        """Check if a source should be updated based on its interval."""
        if not source.last_fetch:
            return True

        time_since_last = datetime.now() - source.last_fetch
        return time_since_last.total_seconds() >= source.update_interval

    def generate_content_hash(self, content: str) -> str:
        """Generate a hash for content deduplication."""
        return hashlib.md5(content.encode("utf-8")).hexdigest()

    def fetch_articles(self, source: NewsAPISource) -> List[NewsAPIArticle]:
        """Fetch articles from NewsAPI."""
        if not self.newsapi_client:
            logger.warning("NewsAPI client not available")
            return []

        try:
            # Build query parameters - NewsAPI requires at least a query or category
            params = {}

            # Ensure we have a query - use category as fallback if no query specified
            if source.query:
                params["q"] = source.query
            elif source.category:
                # If no query but category exists, use category as query
                params["q"] = source.category
            else:
                # Default query if neither is specified
                params["q"] = "artificial intelligence"

            if source.category:
                params["category"] = source.category
            if source.language:
                params["language"] = source.language
            if source.country:
                params["country"] = source.country
            if source.domains:
                params["domains"] = source.domains

            # Set page size
            params["page_size"] = source.max_items or 10

            logger.info(f"NewsAPI params for {source.name}: {params}")

            # Try get_top_headlines first, then fallback to get_everything if no results
            if source.category:
                response = self.newsapi_client.get_top_headlines(**params)

                # If no results with category, try without category using get_everything
                if response.get("status") == "ok" and response.get("totalResults", 0) == 0:
                    logger.info(f"No results with category for {source.name}, trying broader search...")
                    # Remove category and country (not supported by get_everything) and try get_everything
                    params_without_category = params.copy()
                    params_without_category.pop("category", None)
                    params_without_category.pop("country", None)  # country is not supported by get_everything
                    response = self.newsapi_client.get_everything(**params_without_category, sort_by="publishedAt")
            else:
                # For get_everything, remove country parameter as it's not supported
                params_for_everything = params.copy()
                params_for_everything.pop("country", None)  # country is not supported by get_everything
                response = self.newsapi_client.get_everything(**params_for_everything, sort_by="publishedAt")

            # Log response status for debugging
            logger.info(
                f"NewsAPI response for {source.name}: status={response.get('status')}, totalResults={response.get('totalResults', 0)}, articles={len(response.get('articles', []))}"
            )

            if response.get("status") != "ok":
                logger.warning(f"NewsAPI error for {source.name}: {response.get('message', 'Unknown error')}")
                logger.info(f"Full response: {response}")
                return []

            articles = []
            for article in response.get("articles", []):
                # Generate content hash for deduplication
                content = f"{article.get('title', '')} {article.get('description', '')}"
                content_hash = self.generate_content_hash(content)

                # Check if we've seen this content before
                if content_hash in self.articles_cache:
                    continue

                # Create news item
                news_item = NewsAPIArticle(
                    title=article.get("title", "No Title"),
                    url=article.get("url", ""),
                    source=source.name,
                    category=source.category or "General",
                    summary=article.get("description", "No description available"),
                    published_at=article.get("publishedAt", ""),
                    content=article.get("content", ""),
                    api_data={
                        "author": article.get("author"),
                        "source_name": article.get("source", {}).get("name"),
                        "url_to_image": article.get("urlToImage"),
                        "content_hash": content_hash,
                    },
                )

                articles.append(news_item)
                self.articles_cache[content_hash] = news_item

            logger.info(f"Fetched {len(articles)} articles from {source.name}")
            return articles

        except Exception as e:
            logger.error(f"Error fetching from NewsAPI {source.name}: {e}")
            import traceback

            logger.debug(f"Traceback: {traceback.format_exc()}")
            return []

    def collect(self, **kwargs) -> List[Dict[str, Any]]:
        """Collect articles from all enabled NewsAPI sources."""
        all_articles = []

        for source in self.sources:
            if not source.enabled:
                continue

            if not self.should_update_source(source) and not kwargs.get("force", False):
                logger.debug(f"Skipping source {source.name} - not due for update")
                continue

            try:
                articles = self.fetch_articles(source)
                source.last_fetch = datetime.now()

                for article in articles:
                    article_dict = article.to_dict()
                    article_dict["collector"] = self.name
                    article_dict["collected_at"] = datetime.now().isoformat()
                    article_dict["source_type"] = "newsapi"  # Add source type for compatibility
                    all_articles.append(article_dict)

            except Exception as e:
                logger.error(f"Error collecting from source {source.name}: {e}")
                continue

        logger.info(f"Collected {len(all_articles)} total articles from {self.name}")
        return all_articles

    def get_source_status(self) -> List[Dict[str, Any]]:
        """Get status of all NewsAPI sources."""
        return [source.to_dict() for source in self.sources]

    def add_source(self, source: NewsAPISource):
        """Add a new NewsAPI source to the collector."""
        self.sources.append(source)
        logger.info(f"Added NewsAPI source: {source.name}")

    def remove_source(self, name: str):
        """Remove a NewsAPI source by name."""
        self.sources = [s for s in self.sources if s.name != name]
        logger.info(f"Removed NewsAPI source: {name}")

    def enable_source(self, name: str):
        """Enable a NewsAPI source by name."""
        for source in self.sources:
            if source.name == name:
                source.enabled = True
                logger.info(f"Enabled NewsAPI source: {name}")
                break

    def disable_source(self, name: str):
        """Disable a NewsAPI source by name."""
        for source in self.sources:
            if source.name == name:
                source.enabled = False
                logger.info(f"Disabled NewsAPI source: {name}")
                break

    def cleanup_cache(self):
        """Clean up old items from cache to prevent memory issues."""
        # Keep only the last 1000 items
        if len(self.articles_cache) > 1000:
            # Remove oldest items (simple approach: keep last 1000)
            cache_items = list(self.articles_cache.items())
            self.articles_cache = dict(cache_items[-1000:])
            logger.info("Cleaned up NewsAPI cache, kept last 1000 items")


def create_newsapi_collector(name: str = "NewsAPI Collector") -> NewsAPICollector:
    """Factory function to create a NewsAPI collector instance."""
    return NewsAPICollector(name=name)


if __name__ == "__main__":
    # Test the NewsAPI collector
    import logging

    # Set up logging
    logging.basicConfig(level=logging.INFO)

    # Create collector
    collector = create_newsapi_collector()

    if collector.is_available():
        print("✅ NewsAPI Collector initialized successfully")

        # Test collection
        print("\n📊 Testing NewsAPI collection...")
        results = collector.collect()

        print(f"✅ Collected {len(results)} articles")

        # Show sample items
        if results:
            print("\n📰 Sample articles:")
            for i, item in enumerate(results[:3], 1):
                print(f"  {i}. {item['title'][:60]}...")
                print(f"     Source: {item['source']}")
                print(f"     Category: {item['category']}")
                print()

        # Show source status
        print("\n🔍 Source Status:")
        for source in collector.get_source_status():
            status = "✅ Enabled" if source["enabled"] else "❌ Disabled"
            print(f"  {source['name']}: {status}")

    else:
        print("⚠️ NewsAPI Collector not available - check dependencies and API keys")
