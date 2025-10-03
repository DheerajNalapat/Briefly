#!/usr/bin/env python3
"""
NewsAPI.org News Collector

This collector fetches news articles from NewsAPI.org API.
Specialized for general news content and current events.
"""

import os
import logging
import hashlib
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum

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


class Category(Enum):
    """News categories for structured querying."""

    TECHNICAL = "technical"
    INDUSTRY = "industry"
    APPLICATIONS = "applications"
    ECONOMIC = "economic"
    INFRASTRUCTURE = "infrastructure"


# Comprehensive query parameters for different news categories
NEWS_QUERY_PARAMS = {
    Category.TECHNICAL: {
        "query": "AI model breakthrough OR AI research advancement OR language model improvement",
        "keywords": [
            "gpt",
            "claude",
            "gemini",
            "model",
            "breakthrough",
            "research",
            "capability",
            "advancement",
            "algorithm",
            "neural",
            "training",
        ],
    },
    Category.INDUSTRY: {
        "query": "AI business news OR AI company announcement OR AI industry update",
        "keywords": [
            "partnership",
            "launch",
            "market",
            "business",
            "company",
            "startup",
            "funding",
            "investment",
            "acquisition",
            "strategy",
            "growth",
        ],
    },
    Category.APPLICATIONS: {
        "query": "AI implementation success OR AI use case OR AI solution deployment",
        "keywords": [
            "implementation",
            "solution",
            "use case",
            "deployment",
            "automation",
            "industry",
            "transform",
            "adopt",
            "integrate",
        ],
    },
    Category.ECONOMIC: {
        "query": "AI economic impact OR AI job market OR AI workforce changes",
        "keywords": [
            "job",
            "workforce",
            "employment",
            "productivity",
            "efficiency",
            "labor",
            "skill",
            "training",
            "economy",
            "market",
        ],
    },
    Category.INFRASTRUCTURE: {
        "query": "AI chip development OR AI hardware OR AI infrastructure news",
        "keywords": [
            "chip",
            "nvidia",
            "semiconductor",
            "hardware",
            "compute",
            "data center",
            "server",
            "gpu",
            "processor",
        ],
    },
}


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
            logger.error("Error initializing NewsAPI client: %s", e)

    def is_available(self) -> bool:
        """Check if the collector is available and ready to use."""
        return DEPENDENCIES_AVAILABLE and self.newsapi_client

    def load_default_sources(self):
        """Load default NewsAPI sources using the comprehensive query params."""
        default_sources = []

        # Create sources based on NEWS_QUERY_PARAMS
        for category, params in NEWS_QUERY_PARAMS.items():
            source = NewsAPISource(
                name=f"{category.value.title()} AI News",
                query=params["query"],
                category=None,  # Use get_everything for all categories like POC
                language="en",
                country="us",
                max_items=10,
                enabled=True,
            )
            default_sources.append(source)

        self.sources = default_sources
        logger.info("Loaded %s NewsAPI sources with comprehensive query params", len(default_sources))

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

            logger.info("NewsAPI params for %s: %s", source.name, params)

            # Use get_everything for all categories like the POC approach
            # Remove country parameter as it's not supported by get_everything
            params_for_everything = params.copy()
            params_for_everything.pop("country", None)  # country is not supported by get_everything
            params_for_everything.pop("category", None)  # Remove category as we use custom queries
            response = self.newsapi_client.get_everything(**params_for_everything, sort_by="publishedAt")

            # Log response status for debugging
            logger.info(
                "NewsAPI response for %s: status=%s, totalResults=%s, articles=%s",
                source.name,
                response.get("status"),
                response.get("totalResults", 0),
                len(response.get("articles", [])),
            )

            if response.get("status") != "ok":
                logger.warning("NewsAPI error for %s: %s", source.name, response.get("message", "Unknown error"))
                logger.info("Full response: %s", response)
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

            logger.info("Fetched %s articles from %s", len(articles), source.name)
            return articles

        except Exception as e:
            logger.error("Error fetching from NewsAPI %s: %s", source.name, e)
            import traceback

            logger.debug("Traceback: %s", traceback.format_exc())
            return []

    def collect(self, **kwargs) -> List[Dict[str, Any]]:
        """Collect articles from all enabled NewsAPI sources."""
        all_articles = []

        for source in self.sources:
            if not source.enabled:
                continue

            if not self.should_update_source(source) and not kwargs.get("force", False):
                logger.debug("Skipping source %s - not due for update", source.name)
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
                logger.error("Error collecting from source %s: %s", source.name, e)
                continue

        logger.info("Collected %s total articles from %s", len(all_articles), self.name)
        return all_articles

    def get_source_status(self) -> List[Dict[str, Any]]:
        """Get status of all NewsAPI sources."""
        return [source.to_dict() for source in self.sources]

    def add_source(self, source: NewsAPISource):
        """Add a new NewsAPI source to the collector."""
        self.sources.append(source)
        logger.info("Added NewsAPI source: %s", source.name)

    def remove_source(self, name: str):
        """Remove a NewsAPI source by name."""
        self.sources = [s for s in self.sources if s.name != name]
        logger.info("Removed NewsAPI source: %s", name)

    def enable_source(self, name: str):
        """Enable a NewsAPI source by name."""
        for source in self.sources:
            if source.name == name:
                source.enabled = True
                logger.info("Enabled NewsAPI source: %s", name)
                break

    def disable_source(self, name: str):
        """Disable a NewsAPI source by name."""
        for source in self.sources:
            if source.name == name:
                source.enabled = False
                logger.info("Disabled NewsAPI source: %s", name)
                break

    def fetch_news_by_categories(
        self, query_params: Dict[Category, Dict] = None, max_articles_per_category: int = 5
    ) -> List[Dict[str, Any]]:
        """Fetch news for all categories defined in query_params."""
        if query_params is None:
            query_params = NEWS_QUERY_PARAMS

        logger.info("=== Fetching News by Categories ===")

        # Clear cache to avoid deduplication issues with categorized fetching
        original_cache_size = len(self.articles_cache)
        self.articles_cache.clear()
        logger.info("Cleared cache (was %s items) for categorized fetching", original_cache_size)

        all_articles = []
        total_articles = 0

        for category, params in query_params.items():
            logger.info("--- Fetching %s News ---", category.value.upper())
            logger.info("Query: %s", params["query"])
            logger.info("Keywords: %s...", ", ".join(params["keywords"][:5]))  # Show first 5 keywords

            # Create a temporary source for this category
            temp_source = NewsAPISource(
                name=f"{category.value}_news",
                query=params["query"],
                category=None,  # Use get_everything like POC
                max_items=max_articles_per_category,
                enabled=True,
            )

            # Fetch articles for this category
            articles = self.fetch_articles(temp_source)

            # Add category information to each article
            for article in articles:
                article_dict = article.to_dict()
                article_dict["category"] = category.value
                article_dict["keywords"] = params["keywords"]
                article_dict["collector"] = self.name
                article_dict["collected_at"] = datetime.now().isoformat()
                article_dict["source_type"] = "newsapi"
                all_articles.append(article_dict)

            total_articles += len(articles)
            logger.info("Found %s articles for %s", len(articles), category.value)

        logger.info("=== Summary ===")
        logger.info("Total articles collected: %s", total_articles)
        return all_articles

    def fetch_news_by_single_category(
        self, category: Category, query_params: Dict[Category, Dict] = None, max_articles: int = 10
    ) -> List[Dict[str, Any]]:
        """Fetch news for a single category."""
        if query_params is None:
            query_params = NEWS_QUERY_PARAMS

        if category not in query_params:
            logger.warning("Category %s not found in query_params", category.value)
            return []

        params = query_params[category]
        logger.info("=== Fetching %s News ===", category.value.upper())
        logger.info("Query: %s", params["query"])

        # Clear cache to avoid deduplication issues with single category fetching
        original_cache_size = len(self.articles_cache)
        self.articles_cache.clear()
        logger.info("Cleared cache (was %s items) for single category fetching", original_cache_size)

        # Create a temporary source for this category
        temp_source = NewsAPISource(
            name=f"{category.value}_news",
            query=params["query"],
            category=None,  # Use get_everything like POC
            max_items=max_articles,
            enabled=True,
        )

        articles = self.fetch_articles(temp_source)
        all_articles = []

        # Add category information to each article
        for article in articles:
            article_dict = article.to_dict()
            article_dict["category"] = category.value
            article_dict["keywords"] = params["keywords"]
            article_dict["collector"] = self.name
            article_dict["collected_at"] = datetime.now().isoformat()
            article_dict["source_type"] = "newsapi"
            all_articles.append(article_dict)

        if all_articles:
            logger.info("Found %s articles for %s", len(all_articles), category.value)
        else:
            logger.info("No articles found for %s", category.value)

        return all_articles

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
    # Set up logging
    logging.basicConfig(level=logging.INFO)

    # Create collector
    collector = create_newsapi_collector()

    if collector.is_available():
        print("✅ NewsAPI Collector initialized successfully")

        # Test traditional collection
        print("\n📊 Testing traditional NewsAPI collection...")
        results = collector.collect()

        print(f"✅ Collected {len(results)} articles")

        # Test categorized collection
        print("\n📊 Testing categorized NewsAPI collection...")
        categorized_results = collector.fetch_news_by_categories(max_articles_per_category=3)
        print(f"✅ Collected {len(categorized_results)} categorized articles")

        # Test single category collection
        print("\n📊 Testing single category collection...")
        technical_results = collector.fetch_news_by_single_category(Category.TECHNICAL, max_articles=5)
        print(f"✅ Collected {len(technical_results)} technical articles")

        # Show sample items
        if results:
            print("\n📰 Sample articles (traditional):")
            for i, item in enumerate(results[:3], 1):
                print(f"  {i}. {item['title'][:60]}...")
                print(f"     Source: {item['source']}")
                print(f"     Category: {item['category']}")
                print()

        if categorized_results:
            print("\n📰 Sample categorized articles:")
            for i, item in enumerate(categorized_results[:3], 1):
                print(f"  {i}. {item['title'][:60]}...")
                print(f"     Source: {item['source']}")
                print(f"     Category: {item['category']}")
                print(f"     Keywords: {', '.join(item.get('keywords', [])[:3])}...")
                print()

        # Show source status
        print("\n🔍 Source Status:")
        for source in collector.get_source_status():
            status = "✅ Enabled" if source["enabled"] else "❌ Disabled"
            print(f"  {source['name']}: {status}")

    else:
        print("⚠️ NewsAPI Collector not available - check dependencies and API keys")
