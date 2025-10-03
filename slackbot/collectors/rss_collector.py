#!/usr/bin/env python3
"""
RSS News Collector for Briefly Bot

This collector fetches news articles from RSS feeds, specializing in
AI/ML, agentic systems, and technology development content.
"""

import os
import logging
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

# Third-party imports
try:
    import feedparser

    DEPENDENCIES_AVAILABLE = True
except ImportError:
    logging.warning("Required dependencies not available. Install with: pip install feedparser")
    DEPENDENCIES_AVAILABLE = False

from .base_collector import BaseCollector

logger = logging.getLogger(__name__)


@dataclass
class RSSSource:
    """Represents an RSS feed source configuration."""

    name: str
    url: str
    category: str
    max_items: int = 10
    update_interval: int = 3600  # 1 hour in seconds
    enabled: bool = True
    priority: float = 1.0  # Higher priority for AI/ML focused sources
    ai_ml_focus: bool = True  # Whether this source focuses on AI/ML content

    def __post_init__(self):
        # Auto-detect AI/ML focus based on name and category
        ai_keywords = ["ai", "ml", "artificial intelligence", "machine learning", "agentic", "llm", "gpt"]
        if not self.ai_ml_focus:
            self.ai_ml_focus = any(
                keyword in self.name.lower() or keyword in self.category.lower() for keyword in ai_keywords
            )


class RSSCollector(BaseCollector):
    """
    RSS feed collector for news articles.

    Specializes in AI/ML, agentic systems, and technology development content.
    """

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the RSS collector.

        Args:
            config_path: Path to RSS sources configuration file
        """
        super().__init__("RSS Collector")

        if not DEPENDENCIES_AVAILABLE:
            logger.error("❌ RSS collector dependencies not available")
            self.available = False
            return

        self.sources: List[RSSSource] = []
        self.news_cache = {}  # For deduplication
        self.last_fetch_times = {}

        # Load RSS sources
        if config_path and os.path.exists(config_path):
            self._load_sources_from_config(config_path)
        else:
            self._load_default_sources()

        logger.info("✅ RSS Collector initialized with %s sources", len(self.sources))
        self.available = True

    def is_available(self) -> bool:
        """
        Check if the RSS collector is available.

        Returns:
            True if available, False otherwise
        """
        return self.available

    def _load_default_sources(self) -> None:
        """Load default RSS sources focused on AI/ML and technology."""
        default_sources = [
            # High-priority AI/ML focused sources
            RSSSource(
                name="TechCrunch AI",
                url="https://techcrunch.com/tag/artificial-intelligence/feed/",
                category="AI/ML Technology",
                max_items=15,
                update_interval=1800,  # 30 minutes
                priority=1.0,
                ai_ml_focus=True,
            ),
            RSSSource(
                name="Medium AI",
                url="https://medium.com/feed/tag/ai",
                category="AI/ML Development",
                max_items=12,
                update_interval=3600,
                priority=0.9,
                ai_ml_focus=True,
            ),
            RSSSource(
                name="Medium Artificial Intelligence",
                url="https://medium.com/feed/tag/artificial-intelligence",
                category="AI/ML Development",
                max_items=12,
                update_interval=3600,
                priority=0.9,
                ai_ml_focus=True,
            ),
            RSSSource(
                name="Medium Machine Learning",
                url="https://medium.com/feed/tag/machine-learning",
                category="AI/ML Development",
                max_items=12,
                update_interval=3600,
                priority=0.9,
                ai_ml_focus=True,
            ),
            RSSSource(
                name="Medium Deep Learning",
                url="https://medium.com/feed/tag/deep-learning",
                category="AI/ML Development",
                max_items=12,
                update_interval=3600,
                priority=0.9,
                ai_ml_focus=True,
            ),
            RSSSource(
                name="Medium Neural Networks",
                url="https://medium.com/feed/tag/neural-networks",
                category="AI/ML Development",
                max_items=10,
                update_interval=3600,
                priority=0.85,
                ai_ml_focus=True,
            ),
            RSSSource(
                name="Medium Computer Vision",
                url="https://medium.com/feed/tag/computer-vision",
                category="AI/ML Development",
                max_items=10,
                update_interval=3600,
                priority=0.85,
                ai_ml_focus=True,
            ),
            RSSSource(
                name="Medium NLP",
                url="https://medium.com/feed/tag/natural-language-processing",
                category="AI/ML Development",
                max_items=10,
                update_interval=3600,
                priority=0.85,
                ai_ml_focus=True,
            ),
            # Software Development & AI Engineering
            RSSSource(
                name="Medium Software Development",
                url="https://medium.com/feed/tag/software-development",
                category="Software Development",
                max_items=10,
                update_interval=3600,
                priority=0.9,
                ai_ml_focus=True,
            ),
            RSSSource(
                name="Medium Programming",
                url="https://medium.com/feed/tag/programming",
                category="Software Development",
                max_items=10,
                update_interval=3600,
                priority=0.9,
                ai_ml_focus=True,
            ),
            RSSSource(
                name="Medium Python",
                url="https://medium.com/feed/tag/python",
                category="Software Development",
                max_items=10,
                update_interval=3600,
                priority=0.85,
                ai_ml_focus=True,
            ),
            RSSSource(
                name="Medium JavaScript",
                url="https://medium.com/feed/tag/javascript",
                category="Software Development",
                max_items=10,
                update_interval=3600,
                priority=0.85,
                ai_ml_focus=True,
            ),
            RSSSource(
                name="Medium Data Science",
                url="https://medium.com/feed/tag/data-science",
                category="AI/ML Development",
                max_items=10,
                update_interval=3600,
                priority=0.9,
                ai_ml_focus=True,
            ),
            RSSSource(
                name="Medium RAG",
                url="https://medium.com/feed/tag/retrieval-augmented-generation",
                category="AI/ML Development",
                max_items=8,
                update_interval=3600,
                priority=0.95,
                ai_ml_focus=True,
            ),
            RSSSource(
                name="Medium Agentic AI",
                url="https://medium.com/feed/tag/agentic-ai",
                category="AI/ML Development",
                max_items=8,
                update_interval=3600,
                priority=0.95,
                ai_ml_focus=True,
            ),
            RSSSource(
                name="Medium LangChain",
                url="https://medium.com/feed/tag/langchain",
                category="AI/ML Development",
                max_items=8,
                update_interval=3600,
                priority=0.9,
                ai_ml_focus=True,
            ),
            RSSSource(
                name="Medium Vector Database",
                url="https://medium.com/feed/tag/vector-database",
                category="AI/ML Development",
                max_items=8,
                update_interval=3600,
                priority=0.9,
                ai_ml_focus=True,
            ),
            RSSSource(
                name="Medium LLM",
                url="https://medium.com/feed/tag/large-language-models",
                category="AI/ML Development",
                max_items=8,
                update_interval=3600,
                priority=0.9,
                ai_ml_focus=True,
            ),
            RSSSource(
                name="Medium OpenAI",
                url="https://medium.com/feed/tag/openai",
                category="AI/ML Development",
                max_items=8,
                update_interval=3600,
                priority=0.9,
                ai_ml_focus=True,
            ),
            RSSSource(
                name="Medium API Development",
                url="https://medium.com/feed/tag/api-development",
                category="Software Development",
                max_items=8,
                update_interval=3600,
                priority=0.85,
                ai_ml_focus=True,
            ),
            RSSSource(
                name="Medium DevOps",
                url="https://medium.com/feed/tag/devops",
                category="Software Development",
                max_items=8,
                update_interval=3600,
                priority=0.8,
                ai_ml_focus=False,
            ),
            RSSSource(
                name="Medium Cloud Computing",
                url="https://medium.com/feed/tag/cloud-computing",
                category="Software Development",
                max_items=8,
                update_interval=3600,
                priority=0.8,
                ai_ml_focus=False,
            ),
            RSSSource(
                name="VentureBeat AI",
                url="https://venturebeat.com/category/ai/feed/",
                category="AI Business & Technology",
                max_items=10,
                update_interval=1800,
                priority=0.9,
                ai_ml_focus=True,
            ),
            RSSSource(
                name="MIT Technology Review AI",
                url="https://www.technologyreview.com/feed/ai/",
                category="AI Research & Development",
                max_items=8,
                update_interval=3600,
                priority=0.8,
                ai_ml_focus=True,
            ),
            RSSSource(
                name="Ars Technica AI",
                url="https://feeds.arstechnica.com/arstechnica/technology-lab",
                category="Technology & AI",
                max_items=8,
                update_interval=3600,
                priority=0.8,
                ai_ml_focus=True,
            ),
            RSSSource(
                name="Wired Technology",
                url="https://www.wired.com/feed/rss",
                category="Technology & Innovation",
                max_items=6,
                update_interval=3600,
                priority=0.7,
                ai_ml_focus=False,
            ),
            RSSSource(
                name="The Verge AI",
                url="https://www.theverge.com/rss/ai/index.xml",
                category="AI Technology",
                max_items=8,
                update_interval=3600,
                priority=0.8,
                ai_ml_focus=True,
            ),
            RSSSource(
                name="AI News",
                url="https://artificialintelligence-news.com/feed/",
                category="AI Industry News",
                max_items=10,
                update_interval=3600,
                priority=0.9,
                ai_ml_focus=True,
            ),
            RSSSource(
                name="Synced AI",
                url="https://syncedreview.com/feed/",
                category="AI Research & Industry",
                max_items=8,
                update_interval=3600,
                priority=0.8,
                ai_ml_focus=True,
            ),
            RSSSource(
                name="DeepAI",
                url="https://deepai.org/feed",
                category="AI Research & Tools",
                max_items=6,
                update_interval=7200,  # 2 hours
                priority=0.7,
                ai_ml_focus=True,
            ),
        ]

        self.sources = default_sources
        logger.info("📡 Loaded %s default RSS sources", len(self.sources))

    def _load_sources_from_config(self, config_path: str) -> None:
        """Load RSS sources from configuration file."""
        try:
            import yaml

            with open(config_path, "r") as f:
                config = yaml.safe_load(f)

            for source_config in config.get("rss_sources", []):
                source = RSSSource(**source_config)
                self.sources.append(source)

            logger.info("📡 Loaded %s RSS sources from %s", len(self.sources), config_path)

        except Exception as e:
            logger.error("❌ Error loading RSS config from %s: %s", config_path, e)
            logger.info("🔄 Falling back to default RSS sources")
            self._load_default_sources()

    def _should_update_source(self, source: RSSSource) -> bool:
        """Check if a source should be updated based on interval."""
        if source.name not in self.last_fetch_times:
            return True

        last_fetch = self.last_fetch_times[source.name]
        time_since_last = datetime.now() - last_fetch

        return time_since_last.total_seconds() >= source.update_interval

    def _generate_content_hash(self, title: str, summary: str) -> str:
        """Generate a hash for content deduplication."""
        content = f"{title}:{summary}".lower().strip()
        return hashlib.md5(content.encode("utf-8")).hexdigest()

    def _is_ai_ml_relevant(self, title: str, summary: str, category: str) -> bool:
        """Check if content is relevant to AI/ML and agentic systems."""
        ai_ml_keywords = [
            # Core AI/ML terms
            "artificial intelligence",
            "ai",
            "machine learning",
            "ml",
            "deep learning",
            "neural network",
            "transformer",
            "gpt",
            "llm",
            "large language model",
            "agentic",
            "autonomous agent",
            "multi-agent",
            "reinforcement learning",
            # Technology development terms
            "software development",
            "programming",
            "coding",
            "algorithm",
            "data science",
            "computer vision",
            "natural language processing",
            "nlp",
            "robotics",
            "automation",
            "optimization",
            "scalability",
            "performance",
            # Industry terms
            "startup",
            "venture capital",
            "investment",
            "innovation",
            "research",
            "academic",
            "paper",
            "conference",
            "workshop",
            "competition",
        ]

        content = f"{title} {summary} {category}".lower()
        return any(keyword in content for keyword in ai_ml_keywords)

    def _fetch_rss_feed(self, source: RSSSource) -> List[Dict[str, Any]]:
        """Fetch articles from a single RSS feed."""
        articles = []

        try:
            logger.info("📡 Fetching RSS feed: %s", source.name)

            # Parse the RSS feed
            feed = feedparser.parse(source.url)

            if feed.bozo:
                logger.warning("⚠️ RSS parsing issues for %s: %s", source.name, feed.bozo_exception)

            if not feed.entries:
                logger.warning("⚠️ No entries found in RSS feed: %s", source.name)
                return articles

            # Process feed entries
            for entry in feed.entries[: source.max_items]:
                try:
                    # Extract basic information
                    title = getattr(entry, "title", "").strip()
                    link = getattr(entry, "link", "")
                    summary = getattr(entry, "summary", "").strip()

                    # Handle different date formats
                    published_date = None
                    if hasattr(entry, "published_parsed") and entry.published_parsed:
                        published_date = datetime(*entry.published_parsed[:6])
                    elif hasattr(entry, "published"):
                        try:
                            # Try to parse various date formats
                            date_str = entry.published.replace("Z", "+00:00")
                            for fmt in ["%a, %d %b %Y %H:%M:%S %z", "%Y-%m-%dT%H:%M:%S%z"]:
                                try:
                                    published_date = datetime.strptime(date_str, fmt)
                                    break
                                except ValueError:
                                    continue
                            if not published_date:
                                published_date = datetime.now()
                        except:
                            published_date = datetime.now()
                    else:
                        published_date = datetime.now()

                    # Check AI/ML relevance
                    if not self._is_ai_ml_relevant(title, summary, source.category):
                        continue

                    # Generate content hash for deduplication
                    content_hash = self._generate_content_hash(title, summary)

                    # Check if we've seen this content before
                    if content_hash in self.news_cache:
                        continue

                    # Create article dictionary
                    article = {
                        "title": title,
                        "summary": summary,
                        "url": link,
                        "source": source.name,
                        "source_type": "rss",
                        "category": source.category,
                        "published_at": published_date.isoformat(),
                        "priority": source.priority,
                        "ai_ml_focus": source.ai_ml_focus,
                        "content_hash": content_hash,
                        "collected_at": datetime.now().isoformat(),
                    }

                    articles.append(article)

                    # Cache the content hash
                    self.news_cache[content_hash] = datetime.now()

                except Exception as e:
                    logger.warning("⚠️ Error processing RSS entry from %s: %s", source.name, e)
                    continue

            # Update last fetch time
            self.last_fetch_times[source.name] = datetime.now()

            logger.info("✅ Fetched %s articles from %s", len(articles), source.name)

        except Exception as e:
            logger.error("❌ Error fetching RSS feed %s: %s", source.name, e)

        return articles

    def collect(self, max_articles: Optional[int] = None, **kwargs) -> List[Dict[str, Any]]:
        """
        Collect articles from RSS feeds.

        Args:
            max_articles: Maximum number of articles to collect
            **kwargs: Additional arguments

        Returns:
            List of collected articles
        """
        if not self.available:
            logger.error("❌ RSS collector not available")
            return []

        logger.info("📡 Collecting articles from %s RSS sources...", len(self.sources))

        all_articles = []

        # Collect from each source
        for source in self.sources:
            if not source.enabled:
                continue

            if not self._should_update_source(source):
                logger.debug("⏰ Skipping %s (not due for update)", source.name)
                continue

            articles = self._fetch_rss_feed(source)
            all_articles.extend(articles)

        # Sort by priority and recency
        all_articles.sort(key=lambda x: (x.get("priority", 0), x.get("published_at", "")), reverse=True)

        # Apply max_articles limit
        if max_articles:
            all_articles = all_articles[:max_articles]

        # Clean up old cache entries (older than 24 hours)
        self._cleanup_cache()

        logger.info("✅ RSS collection complete: %s articles", len(all_articles))
        return all_articles

    def _cleanup_cache(self) -> None:
        """Clean up old cache entries to prevent memory bloat."""
        cutoff_time = datetime.now() - timedelta(hours=24)
        old_hashes = [hash_key for hash_key, timestamp in self.news_cache.items() if timestamp < cutoff_time]

        for hash_key in old_hashes:
            del self.news_cache[hash_key]

        if old_hashes:
            logger.debug("🧹 Cleaned up %s old cache entries", len(old_hashes))

    def get_source_status(self) -> Dict[str, Any]:
        """Get status of all RSS sources."""
        status = {
            "total_sources": len(self.sources),
            "enabled_sources": len([s for s in self.sources if s.enabled]),
            "sources": [],
        }

        for source in self.sources:
            source_status = {
                "name": source.name,
                "enabled": source.enabled,
                "priority": source.priority,
                "ai_ml_focus": source.ai_ml_focus,
                "last_fetch": self.last_fetch_times.get(source.name, "Never"),
                "update_interval": source.update_interval,
            }
            status["sources"].append(source_status)

        return status

    def add_source(self, source: RSSSource) -> bool:
        """Add a new RSS source."""
        try:
            self.sources.append(source)
            logger.info("✅ Added RSS source: %s", source.name)
            return True
        except Exception as e:
            logger.error("❌ Error adding RSS source %s: %s", source.name, e)
            return False

    def remove_source(self, source_name: str) -> bool:
        """Remove an RSS source by name."""
        try:
            self.sources = [s for s in self.sources if s.name != source_name]
            logger.info("✅ Removed RSS source: %s", source_name)
            return True
        except Exception as e:
            logger.error("❌ Error removing RSS source %s: %s", source_name, e)
            return False


def create_rss_collector(config_path: Optional[str] = None) -> RSSCollector:
    """
    Factory function to create an RSS collector instance.

    Args:
        config_path: Optional path to RSS sources configuration file

    Returns:
        RSSCollector instance
    """
    return RSSCollector(config_path)


if __name__ == "__main__":
    # Test the RSS collector
    import logging

    # Set up logging
    logging.basicConfig(level=logging.INFO)

    # Create collector
    collector = create_rss_collector()

    # Test collection
    print("🧪 Testing RSS Collector...")
    print("=" * 50)

    # Show source status
    status = collector.get_source_status()
    print(f"📡 Total sources: {status['total_sources']}")
    print(f"✅ Enabled sources: {status['enabled_sources']}")

    # Test collection
    articles = collector.collect(max_articles=5)

    if articles:
        print(f"\n📰 Collected {len(articles)} articles:")
        for i, article in enumerate(articles, 1):
            print(f"  {i}. {article['title'][:60]}...")
            print(f"     Source: {article['source']} | Category: {article['category']}")
            print(f"     Priority: {article.get('priority', 'N/A')} | AI/ML Focus: {article.get('ai_ml_focus', 'N/A')}")
            print()
    else:
        print("❌ No articles collected")
