#!/usr/bin/env python3
"""
API-based News Collector PoC

This script demonstrates how to collect news and research papers using:
1. arXiv API - for research papers and academic content
2. NewsAPI.org - for general news articles

Features:
- Configurable API sources
- Rate limiting and error handling
- Data deduplication
- Structured output in JSON format
- Caching to avoid duplicate requests
"""

import os
import json
import logging
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
import time

# Third-party imports
try:
    import arxiv
    from newsapi import NewsApiClient
    import yaml

    DEPENDENCIES_AVAILABLE = True
except ImportError:
    logging.warning("Required dependencies not available. Install with: pip install arxiv newsapi-python pyyaml")
    DEPENDENCIES_AVAILABLE = False
    arxiv = None
    NewsApiClient = None
    yaml = None

from .base_collector import BaseCollector
from slackbot.config import NEWS_CONFIG

logger = logging.getLogger(__name__)


@dataclass
class APINewsSource:
    """Represents a configurable API news source."""

    name: str
    source_type: str  # 'arxiv' or 'newsapi'
    enabled: bool = True
    max_items: int = 10
    update_interval: int = 3600  # 1 hour in seconds
    last_fetch: Optional[datetime] = None

    # ArXiv specific fields
    query: Optional[str] = None
    max_results: Optional[int] = None
    sort_by: Optional[str] = None
    sort_order: Optional[str] = None

    # NewsAPI specific fields
    category: Optional[str] = None
    language: Optional[str] = None
    country: Optional[str] = None
    domains: Optional[str] = None

    def to_dict(self) -> Dict:
        """Convert source to dictionary for serialization."""
        data = asdict(self)
        if self.last_fetch:
            data["last_fetch"] = self.last_fetch.isoformat()
        return data

    @classmethod
    def from_dict(cls, data: Dict) -> "APINewsSource":
        """Create APINewsSource from dictionary."""
        source = cls(
            name=data["name"],
            source_type=data["source_type"],
            enabled=data.get("enabled", True),
            max_items=data.get("max_items", 10),
            update_interval=data.get("update_interval", 3600),
            query=data.get("query"),
            max_results=data.get("max_results"),
            sort_by=data.get("sort_by"),
            sort_order=data.get("sort_order"),
            category=data.get("category"),
            language=data.get("language"),
            country=data.get("country"),
            domains=data.get("domains"),
        )

        if data.get("last_fetch"):
            source.last_fetch = datetime.fromisoformat(data["last_fetch"])

        return source


@dataclass
class NewsItem:
    """Represents a news item from any API source."""

    title: str
    url: str
    source: str
    source_type: str
    category: str
    summary: str
    published_at: Optional[str] = None
    content: Optional[str] = None
    api_data: Optional[Dict] = None

    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization."""
        return asdict(self)


class APINewsCollector(BaseCollector):
    """API-based news collector service."""

    def __init__(self, config_file: Optional[str] = None, name: str = "API News Collector"):
        super().__init__(name=name)

        self.sources = []
        self.news_cache = {}  # Cache for deduplication
        self.config_file = config_file

        # Initialize API clients
        self.arxiv_client = None
        self.newsapi_client = None

        # Load configuration
        if config_file:
            self.load_sources_from_config(config_file)
        else:
            self.load_default_sources()

        # Initialize APIs
        self.initialize_apis()

    def initialize_apis(self):
        """Initialize API clients with environment variables."""
        try:
            # Initialize NewsAPI client
            newsapi_key = os.getenv("NEWSAPI_KEY")
            if newsapi_key:
                self.newsapi_client = NewsApiClient(api_key=newsapi_key)
                logger.info("NewsAPI client initialized successfully")
            else:
                logger.warning("NEWSAPI_KEY environment variable not set. NewsAPI features will be disabled.")

            # ArXiv doesn't require an API key
            self.arxiv_client = True  # Just mark as available
            logger.info("ArXiv client available")

        except Exception as e:
            logger.error(f"Error initializing API clients: {e}")

    def is_available(self) -> bool:
        """Check if the collector is available and ready to use."""
        return DEPENDENCIES_AVAILABLE and (self.arxiv_client or self.newsapi_client)

    def load_sources_from_config(self, config_file: str):
        """Load news sources from YAML configuration file."""
        try:
            with open(config_file, "r") as f:
                config = yaml.safe_load(f)

            sources = config.get("sources", [])
            for source_data in sources:
                source = APINewsSource.from_dict(source_data)
                self.sources.append(source)

            logger.info(f"Loaded {len(self.sources)} sources from {config_file}")

        except FileNotFoundError:
            logger.warning(f"Config file {config_file} not found. Using default sources.")
            self.load_default_sources()
        except Exception as e:
            logger.error(f"Error loading config file: {e}")
            self.load_default_sources()

    def load_default_sources(self):
        """Load default news sources."""
        # Try to load from the sources folder first
        default_config_path = os.path.join(os.path.dirname(__file__), "sources", "api_sources_config.yaml")

        if os.path.exists(default_config_path):
            self.load_sources_from_config(default_config_path)
            return

        # Fallback to hardcoded sources if config file doesn't exist
        default_sources = [
            APINewsSource(
                name="ArXiv AI Papers",
                source_type="arxiv",
                query="AI OR artificial intelligence OR machine learning",
                max_results=20,
                sort_by="submittedDate",
                sort_order="descending",
                category="Research Papers",
            ),
            APINewsSource(
                name="ArXiv Computer Vision",
                source_type="arxiv",
                query="computer vision OR image recognition",
                max_results=15,
                sort_by="submittedDate",
                sort_order="descending",
                category="Computer Vision",
            ),
            APINewsSource(
                name="ArXiv NLP Papers",
                source_type="arxiv",
                query="natural language processing OR NLP OR transformers",
                max_results=15,
                sort_by="submittedDate",
                sort_order="descending",
                category="Natural Language Processing",
            ),
            APINewsSource(
                name="Tech News AI",
                source_type="newsapi",
                query="artificial intelligence OR AI",
                category="technology",
                language="en",
                country="us",
                max_items=15,
            ),
        ]

        self.sources = default_sources
        logger.info(f"Loaded {len(default_sources)} fallback sources")

    def should_update_source(self, source: APINewsSource) -> bool:
        """Check if a source should be updated based on its interval."""
        if not source.last_fetch:
            return True

        time_since_last = datetime.now() - source.last_fetch
        return time_since_last.total_seconds() >= source.update_interval

    def generate_content_hash(self, content: str) -> str:
        """Generate a hash for content deduplication."""
        return hashlib.md5(content.encode("utf-8")).hexdigest()

    def fetch_arxiv_papers(self, source: APINewsSource) -> List[NewsItem]:
        """Fetch papers from ArXiv API."""
        if not self.arxiv_client:
            logger.warning("ArXiv client not available")
            return []

        try:
            # Create search query using the newer Client approach
            client = arxiv.Client()
            search = arxiv.Search(
                query=source.query,
                max_results=min(source.max_results or 10, 20),  # Limit to avoid pagination issues
                sort_by=arxiv.SortCriterion.SubmittedDate,
                sort_order=arxiv.SortOrder.Descending,
            )

            papers = []
            for result in client.results(search):
                # Generate content hash for deduplication
                content = f"{result.title} {result.summary}"
                content_hash = self.generate_content_hash(content)

                # Check if we've seen this content before
                if content_hash in self.news_cache:
                    continue

                # Create news item
                paper = NewsItem(
                    title=result.title,
                    url=result.entry_id,
                    source=source.name,
                    source_type="arxiv",
                    category=source.category,
                    summary=result.summary,
                    published_at=(result.published.strftime("%Y-%m-%d") if result.published else None),
                    content=result.summary,
                    api_data={
                        "authors": [author.name for author in result.authors],
                        "pdf_url": result.pdf_url,
                        "journal_ref": result.journal_ref,
                        "doi": result.doi,
                    },
                )

                papers.append(paper)
                self.news_cache[content_hash] = paper

                # Rate limiting
                time.sleep(0.1)

            logger.info(f"Fetched {len(papers)} papers from {source.name}")
            return papers

        except Exception as e:
            logger.error(f"Error fetching from ArXiv {source.name}: {e}")
            # Return any papers we managed to collect before the error
            if papers:
                logger.info(f"Returning {len(papers)} papers collected before error from {source.name}")
            return papers

    def fetch_newsapi_articles(self, source: APINewsSource) -> List[NewsItem]:
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
                    # Remove category and try get_everything
                    params_without_category = params.copy()
                    params_without_category.pop("category", None)
                    response = self.newsapi_client.get_everything(**params_without_category, sort_by="publishedAt")
            else:
                response = self.newsapi_client.get_everything(**params, sort_by="publishedAt")

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
                if content_hash in self.news_cache:
                    continue

                # Create news item
                news_item = NewsItem(
                    title=article.get("title", "No Title"),
                    url=article.get("url", ""),
                    source=source.name,
                    source_type="newsapi",
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
                self.news_cache[content_hash] = news_item

            logger.info(f"Fetched {len(articles)} articles from {source.name}")
            return articles

        except Exception as e:
            logger.error(f"Error fetching from NewsAPI {source.name}: {e}")
            import traceback

            logger.debug(f"Traceback: {traceback.format_exc()}")
            return []

    def collect(self, **kwargs) -> List[Dict[str, Any]]:
        """Collect news items from all enabled sources."""
        all_items = []

        for source in self.sources:
            if not source.enabled:
                continue

            if not self.should_update_source(source) and not kwargs.get("force", False):
                logger.debug(f"Skipping source {source.name} - not due for update")
                continue

            try:
                if source.source_type == "arxiv":
                    items = self.fetch_arxiv_papers(source)
                elif source.source_type == "newsapi":
                    items = self.fetch_newsapi_articles(source)
                else:
                    logger.warning(f"Unknown source type: {source.source_type}")
                    continue

                source.last_fetch = datetime.now()

                for item in items:
                    item_dict = item.to_dict()
                    item_dict["collector"] = self.name
                    item_dict["collected_at"] = datetime.now().isoformat()
                    all_items.append(item_dict)

            except Exception as e:
                logger.error(f"Error collecting from source {source.name}: {e}")
                continue

        max_items = NEWS_CONFIG.get("max_articles_per_digest", 20)
        if len(all_items) > max_items:
            # Ensure balanced representation of both ArXiv and NewsAPI articles
            arxiv_items = [item for item in all_items if item.get("source_type") == "arxiv"]
            newsapi_items = [item for item in all_items if item.get("source_type") == "newsapi"]

            # Calculate balanced distribution
            arxiv_limit = min(len(arxiv_items), max_items // 2)
            newsapi_limit = max_items - arxiv_limit

            # Take balanced samples
            balanced_items = arxiv_items[:arxiv_limit] + newsapi_items[:newsapi_limit]

            # If we still have room, add remaining items
            if len(balanced_items) < max_items:
                remaining_items = [item for item in all_items if item not in balanced_items]
                balanced_items.extend(remaining_items[: max_items - len(balanced_items)])

            all_items = balanced_items
            logger.info(
                f"Limited results to {len(all_items)} items (balanced: {len([i for i in all_items if i.get('source_type') == 'arxiv'])} ArXiv, {len([i for i in all_items if i.get('source_type') == 'newsapi'])} NewsAPI)"
            )

        logger.info(f"Collected {len(all_items)} total items from {self.name}")
        return all_items

    def get_source_status(self) -> List[Dict[str, Any]]:
        """Get status of all sources."""
        return [source.to_dict() for source in self.sources]

    def add_source(self, source: APINewsSource):
        """Add a new source to the collector."""
        self.sources.append(source)
        logger.info(f"Added source: {source.name}")

    def remove_source(self, name: str):
        """Remove a source by name."""
        self.sources = [s for s in self.sources if s.name != name]
        logger.info(f"Removed source: {name}")

    def enable_source(self, name: str):
        """Enable a source by name."""
        for source in self.sources:
            if source.name == name:
                source.enabled = True
                logger.info(f"Enabled source: {name}")
                break

    def disable_source(self, name: str):
        """Disable a source by name."""
        for source in self.sources:
            if source.name == name:
                source.enabled = False
                logger.info(f"Disabled source: {name}")
                break

    def fetch_all_sources(self) -> List[NewsItem]:
        """Fetch news from all enabled sources."""
        all_items = []

        # Initialize APIs if not already done
        if not self.arxiv_client or not self.newsapi_client:
            self.initialize_apis()

        for source in self.sources:
            try:
                items = self.fetch_from_source(source)
                all_items.extend(items)

                # Rate limiting between sources
                time.sleep(1)

            except Exception as e:
                logger.error(f"Error processing source {source.name}: {e}")
                continue

        logger.info(f"Total items collected: {len(all_items)}")
        return all_items

    def create_api_summary(self, items: List[NewsItem]) -> Dict:
        """Create a structured summary of collected news items."""
        if not items:
            return {"message": "No news items found"}

        # Group by source type
        arxiv_items = [item for item in items if item.source_type == "arxiv"]
        newsapi_items = [item for item in items if item.source_type == "newsapi"]

        # Group by category
        categories = {}
        for item in items:
            cat = item.category
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(item)

        # Create summary
        summary = {
            "timestamp": datetime.now().isoformat(),
            "total_items": len(items),
            "sources_summary": {
                "arxiv": {
                    "count": len(arxiv_items),
                    "sources": list(set(item.source for item in arxiv_items)),
                },
                "newsapi": {
                    "count": len(newsapi_items),
                    "sources": list(set(item.source for item in newsapi_items)),
                },
            },
            "categories_summary": {cat: len(items) for cat, items in categories.items()},
            "items": [item.to_dict() for item in items],
        }

        return summary

    def save_summary(self, summary: Dict, filename: Optional[str] = None):
        """Save summary to JSON file."""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"api_news_summary_{timestamp}.json"

        try:
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(summary, f, indent=2, ensure_ascii=False)

            logger.info(f"Summary saved to {filename}")

        except Exception as e:
            logger.error(f"Error saving summary: {e}")

    def save_sources_config(self, filename: Optional[str] = None):
        """Save current sources configuration to YAML file."""
        if not filename:
            filename = "api_sources_config.yaml"

        try:
            config = {"sources": [source.to_dict() for source in self.sources]}

            with open(filename, "w", encoding="utf-8") as f:
                yaml.dump(config, f, default_flow_style=False, indent=2)

            logger.info(f"Sources configuration saved to {filename}")

        except Exception as e:
            logger.error(f"Error saving sources configuration: {e}")

    def cleanup_cache(self):
        """Clean up old items from cache to prevent memory issues."""
        # Keep only the last 1000 items
        if len(self.news_cache) > 1000:
            # Remove oldest items (simple approach: keep last 1000)
            cache_items = list(self.news_cache.items())
            self.news_cache = dict(cache_items[-1000:])
            logger.info("Cleaned up cache, kept last 1000 items")


def create_api_collector(config_file: Optional[str] = None, name: str = "API News Collector") -> APINewsCollector:
    """Factory function to create an API news collector instance."""
    return APINewsCollector(config_file=config_file, name=name)


if __name__ == "__main__":
    # Test the API collector
    import logging

    # Set up logging
    logging.basicConfig(level=logging.INFO)

    # Create collector
    collector = create_api_collector()

    if collector.is_available():
        print("✅ API News Collector initialized successfully")

        # Test collection
        print("\n📊 Testing news collection...")
        results = collector.collect()

        print(f"✅ Collected {len(results)} news items")

        # Show sample items
        if results:
            print("\n📰 Sample items:")
            for i, item in enumerate(results[:3], 1):
                print(f"  {i}. {item['title'][:60]}...")
                print(f"     Source: {item['source']} ({item['source_type']})")
                print(f"     Category: {item['category']}")
                print()

        # Show source status
        print("\n🔍 Source Status:")
        for source in collector.get_source_status():
            status = "✅ Enabled" if source["enabled"] else "❌ Disabled"
            print(f"  {source['name']}: {status}")

    else:
        print("⚠️ API News Collector not available - check dependencies and API keys")
