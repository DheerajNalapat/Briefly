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

# Load environment variables from .env file
try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass  # python-dotenv not available

# Third-party imports
import arxiv
from newsapi import NewsApiClient
import yaml

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
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
    link: str
    source: str
    source_type: str
    category: str
    summary: str
    published_date: Optional[str] = None
    content_hash: Optional[str] = None
    api_data: Optional[Dict] = None

    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization."""
        return asdict(self)


class APINewsCollector:
    """Main class for collecting news from multiple API sources."""

    def __init__(self, config_file: Optional[str] = None):
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

    def initialize_apis(self):
        """Initialize API clients with environment variables."""
        try:
            # Initialize NewsAPI client
            newsapi_key = os.getenv("NEWSAPI_KEY")
            if newsapi_key:
                self.newsapi_client = NewsApiClient(api_key=newsapi_key)
                logger.info("NewsAPI client initialized successfully")
            else:
                logger.warning(
                    "NEWSAPI_KEY environment variable not set. NewsAPI features will be disabled."
                )

            # ArXiv doesn't require an API key
            self.arxiv_client = True  # Just mark as available
            logger.info("ArXiv client available")

        except Exception as e:
            logger.error(f"Error initializing API clients: {e}")

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
            logger.warning(
                f"Config file {config_file} not found. Using default sources."
            )
            self.load_default_sources()
        except Exception as e:
            logger.error(f"Error loading config file: {e}")
            self.load_default_sources()

    def load_default_sources(self):
        """Load default news sources."""
        default_sources = [
            # ArXiv sources for research papers
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
            # NewsAPI sources for general news
            APINewsSource(
                name="Tech News AI",
                source_type="newsapi",
                query="artificial intelligence OR AI",
                category="technology",
                language="en",
                country="us",
                max_items=15,
            ),
            APINewsSource(
                name="Business AI News",
                source_type="newsapi",
                query="AI business OR artificial intelligence business",
                category="business",
                language="en",
                country="us",
                max_items=10,
            ),
            APINewsSource(
                name="Science AI News",
                source_type="newsapi",
                query="AI research OR artificial intelligence research",
                category="science",
                language="en",
                country="us",
                max_items=10,
            ),
        ]

        self.sources = default_sources
        logger.info(f"Loaded {len(self.sources)} default sources")

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
                max_results=source.max_results or 10,
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
                    link=result.entry_id,
                    source=source.name,
                    source_type="arxiv",
                    category=source.category,
                    summary=result.summary,
                    published_date=(
                        result.published.strftime("%Y-%m-%d")
                        if result.published
                        else None
                    ),
                    content_hash=content_hash,
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
            return []

    def fetch_newsapi_articles(self, source: APINewsSource) -> List[NewsItem]:
        """Fetch articles from NewsAPI."""
        if not self.newsapi_client:
            logger.warning("NewsAPI client not available")
            return []

        try:
            # Build query parameters
            params = {}
            if source.query:
                params["q"] = source.query
            if source.category:
                params["category"] = source.category
            if source.language:
                params["language"] = source.language
            if source.country:
                params["country"] = source.country
            if source.domains:
                params["domains"] = source.domains

            # Get top headlines if category is specified, otherwise search everything
            if source.category:
                response = self.newsapi_client.get_top_headlines(
                    **params, page_size=source.max_items
                )
            else:
                response = self.newsapi_client.get_everything(
                    **params, page_size=source.max_items, sort_by="publishedAt"
                )

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
                    link=article.get("url", ""),
                    source=source.name,
                    source_type="newsapi",
                    category=source.category or "General",
                    summary=article.get("description", "No description available"),
                    published_date=article.get("publishedAt", ""),
                    content_hash=content_hash,
                    api_data={
                        "author": article.get("author"),
                        "source_name": article.get("source", {}).get("name"),
                        "url_to_image": article.get("urlToImage"),
                        "content": article.get("content"),
                    },
                )

                articles.append(news_item)
                self.news_cache[content_hash] = news_item

            logger.info(f"Fetched {len(articles)} articles from {source.name}")
            return articles

        except Exception as e:
            logger.error(f"Error fetching from NewsAPI {source.name}: {e}")
            return []

    def fetch_from_source(self, source: APINewsSource) -> List[NewsItem]:
        """Fetch news from a specific source."""
        if not source.enabled:
            logger.info(f"Source {source.name} is disabled, skipping")
            return []

        if not self.should_update_source(source):
            logger.info(f"Source {source.name} was recently updated, skipping")
            return []

        logger.info(f"Fetching from {source.name} ({source.source_type})")

        try:
            if source.source_type == "arxiv":
                items = self.fetch_arxiv_papers(source)
            elif source.source_type == "newsapi":
                items = self.fetch_newsapi_articles(source)

            else:
                logger.warning(f"Unknown source type: {source.source_type}")
                return []

            # Update last fetch time
            source.last_fetch = datetime.now()

            return items

        except Exception as e:
            logger.error(f"Error fetching from {source.name}: {e}")
            return []

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
            "categories_summary": {
                cat: len(items) for cat, items in categories.items()
            },
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


def main():
    """Main function to run the API news collector."""
    print("🚀 API News Collector PoC")
    print("=" * 50)

    # Check for required environment variables
    print("\n📋 Environment Check:")
    newsapi_key = os.getenv("NEWSAPI_KEY")
    if newsapi_key:
        print("✅ NEWSAPI_KEY found")
    else:
        print("⚠️  NEWSAPI_KEY not set - NewsAPI features will be disabled")
        print("   Set it with: export NEWSAPI_KEY='your_api_key_here'")

    print("✅ ArXiv API available (no key required)")

    # Initialize collector
    print("\n🔧 Initializing API News Collector...")
    collector = APINewsCollector()

    # Save initial configuration
    collector.save_sources_config()

    # Fetch news from all sources
    print("\n📡 Fetching news from all sources...")
    items = collector.fetch_all_sources()

    if not items:
        print("❌ No news items found. Check your configuration and API keys.")
        return

    # Create and save summary
    print(f"\n📊 Creating summary for {len(items)} items...")
    summary = collector.create_api_summary(items)

    # Save summary
    collector.save_summary(summary)

    # Display summary
    print("\n📈 Summary:")
    print(f"   Total items: {summary['total_items']}")
    print(f"   ArXiv papers: {summary['sources_summary']['arxiv']['count']}")
    print(f"   NewsAPI articles: {summary['sources_summary']['newsapi']['count']}")

    print("\n📁 Files created:")
    print("   - api_news_summary_YYYYMMDD_HHMMSS.json (news data)")
    print("   - api_sources_config.yaml (source configuration)")

    print("\n✨ API News Collector PoC completed successfully!")

    # Cleanup
    collector.cleanup_cache()


if __name__ == "__main__":
    main()
