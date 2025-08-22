#!/usr/bin/env python3
"""
RSS News Aggregator for Briefly Bot

This script uses feedparser to fetch news from RSS feeds and provides
a unified interface for both RSS and web crawling sources.
"""

import feedparser
import json
import time
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Union
import logging
from urllib.parse import urlparse
import hashlib
import yaml

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class RSSSource:
    """Represents a configurable RSS feed source."""

    def __init__(
        self,
        name: str,
        url: str,
        category: str = "General",
        max_items: int = 10,
        update_interval: int = 3600,  # 1 hour in seconds
        enabled: bool = True,
    ):
        self.name = name
        self.url = url
        self.category = category
        self.max_items = max_items
        self.update_interval = update_interval
        self.enabled = enabled
        self.last_fetch = None
        self.last_hash = None

    def to_dict(self) -> Dict:
        """Convert source to dictionary for serialization."""
        return {
            "name": self.name,
            "url": self.url,
            "category": self.category,
            "max_items": self.max_items,
            "update_interval": self.update_interval,
            "enabled": self.enabled,
            "last_fetch": self.last_fetch.isoformat() if self.last_fetch else None,
            "last_hash": self.last_hash,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "RSSSource":
        """Create RSSSource from dictionary."""
        source = cls(
            name=data["name"],
            url=data["url"],
            category=data.get("category", "General"),
            max_items=data.get("max_items", 10),
            update_interval=data.get("update_interval", 3600),
            enabled=data.get("enabled", True),
        )

        if data.get("last_fetch"):
            source.last_fetch = datetime.fromisoformat(data["last_fetch"])
        source.last_hash = data.get("last_hash")

        return source


class RSSNewsAggregator:
    """RSS-based news aggregator with caching and deduplication."""

    def __init__(self, config_file: Optional[str] = None):
        self.sources = []
        self.news_cache = {}  # Cache for deduplication
        self.config_file = config_file

        if config_file:
            self.load_sources_from_config(config_file)
        else:
            self.load_default_sources()

    def load_sources_from_config(self, config_file: str):
        """Load RSS sources from a YAML configuration file."""
        try:
            with open(config_file, "r") as f:
                config = yaml.safe_load(f)

            for source_config in config.get("rss_sources", []):
                source = RSSSource.from_dict(source_config)
                self.sources.append(source)

            logger.info(f"Loaded {len(self.sources)} RSS sources from {config_file}")

        except Exception as e:
            logger.error(f"Error loading RSS config file {config_file}: {e}")
            logger.info("Falling back to default RSS sources")
            self.load_default_sources()

    def load_default_sources(self):
        """Load default RSS sources for AI/tech news."""
        default_sources = [
            RSSSource(
                name="MIT Technology Review AI",
                url="https://www.technologyreview.com/feed/ai/",
                category="Technology",
                max_items=8,
                update_interval=3600,
            ),
            RSSSource(
                name="TechCrunch AI",
                url="https://techcrunch.com/tag/artificial-intelligence/feed/",
                category="Technology",
                max_items=8,
                update_interval=1800,  # 30 minutes
            ),
            RSSSource(
                name="VentureBeat AI",
                url="https://venturebeat.com/category/ai/feed/",
                category="Technology",
                max_items=8,
                update_interval=1800,
            ),
            RSSSource(
                name="Ars Technica AI",
                url="https://feeds.arstechnica.com/arstechnica/technology-lab",
                category="Technology",
                max_items=6,
                update_interval=3600,
            ),
            RSSSource(
                name="Wired AI",
                url="https://www.wired.com/feed/rss",
                category="Technology",
                max_items=6,
                update_interval=3600,
            ),
        ]

        self.sources = default_sources
        logger.info(f"Loaded {len(self.sources)} default RSS sources")

    def add_source(self, source: RSSSource):
        """Add a new RSS source."""
        self.sources.append(source)
        logger.info(f"Added RSS source: {source.name}")

    def remove_source(self, source_name: str):
        """Remove an RSS source by name."""
        self.sources = [s for s in self.sources if s.name != source_name]
        logger.info(f"Removed RSS source: {source_name}")

    def list_sources(self) -> List[Dict]:
        """List all configured RSS sources."""
        return [source.to_dict() for source in self.sources]

    def fetch_rss_feed(self, source: RSSSource) -> List[Dict]:
        """Fetch news from a single RSS feed."""
        news_items = []

        try:
            logger.info(f"Fetching RSS feed: {source.name}")

            # Parse the RSS feed
            feed = feedparser.parse(source.url)

            if feed.bozo:  # Check for parsing errors
                logger.warning(f"RSS parsing issues for {source.name}: {feed.bozo_exception}")

            if not feed.entries:
                logger.warning(f"No entries found in RSS feed: {source.name}")
                return news_items

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
                            published_date = datetime.fromisoformat(entry.published.replace("Z", "+00:00"))
                        except:
                            published_date = datetime.now()

                    # Create content hash for deduplication
                    content_hash = self.generate_content_hash(title + summary)

                    # Check if we've seen this content before
                    if content_hash in self.news_cache:
                        continue

                    # Create news item
                    news_item = {
                        "title": title,
                        "link": link,
                        "summary": summary,
                        "source": source.name,
                        "category": source.category,
                        "published_at": (published_date.isoformat() if published_date else None),
                        "fetched_at": datetime.now().isoformat(),
                        "content_hash": content_hash,
                        "feed_url": source.url,
                    }

                    news_items.append(news_item)

                    # Cache the content hash
                    self.news_cache[content_hash] = datetime.now()

                except Exception as e:
                    logger.debug(f"Error processing RSS entry from {source.name}: {e}")
                    continue

            # Update source metadata
            source.last_fetch = datetime.now()
            if news_items:
                source.last_hash = self.generate_content_hash(str([item["title"] for item in news_items]))

            logger.info(f"Extracted {len(news_items)} items from {source.name}")

        except Exception as e:
            logger.error(f"Error fetching RSS feed {source.name}: {e}")

        return news_items

    def generate_content_hash(self, content: str) -> str:
        """Generate a hash for content to help with deduplication."""
        return hashlib.md5(content.encode("utf-8")).hexdigest()

    def should_update_source(self, source: RSSSource) -> bool:
        """Check if a source should be updated based on its interval."""
        if not source.last_fetch:
            return True

        time_since_last = datetime.now() - source.last_fetch
        return time_since_last.total_seconds() >= source.update_interval

    def fetch_all_feeds(self, force_update: bool = False) -> List[Dict]:
        """Fetch news from all RSS sources."""
        all_news = []

        if not self.sources:
            logger.warning("No RSS sources configured. Loading default sources.")
            self.load_default_sources()

        for source in self.sources:
            if not source.enabled:
                logger.info(f"Skipping disabled source: {source.name}")
                continue

            if not force_update and not self.should_update_source(source):
                logger.info(f"Skipping {source.name} - not due for update yet")
                continue

            try:
                news_items = self.fetch_rss_feed(source)
                all_news.extend(news_items)

                # Be respectful - small delay between feeds
                if len(self.sources) > 1:
                    time.sleep(1)

            except Exception as e:
                logger.error(f"Error processing RSS source {source.name}: {e}")
                continue

        return all_news

    def create_rss_summary(self, news_items: List[Dict]) -> Dict:
        """Create a structured summary of RSS news items."""
        if not news_items:
            return {
                "date": datetime.now().isoformat(),
                "summary": "No RSS news items found.",
                "total_items": 0,
                "sources_summary": {},
                "categories_summary": {},
                "top_stories": [],
                "feed_stats": {},
            }

        # Group by source and category
        sources_summary = {}
        categories_summary = {}
        feed_stats = {}

        for item in news_items:
            source = item.get("source", "Unknown")
            category = item.get("category", "General")
            feed_url = item.get("feed_url", "Unknown")

            sources_summary[source] = sources_summary.get(source, 0) + 1
            categories_summary[category] = categories_summary.get(category, 0) + 1

            if feed_url not in feed_stats:
                feed_stats[feed_url] = {
                    "source": source,
                    "count": 0,
                    "last_update": item.get("fetched_at"),
                }
            feed_stats[feed_url]["count"] += 1

        # Select top stories (limit to 10)
        top_stories = sorted(news_items, key=lambda x: x.get("published_at", ""), reverse=True)[:10]

        summary = {
            "date": datetime.now().isoformat(),
            "summary": f"Found {len(news_items)} RSS news items from {len(sources_summary)} sources",
            "total_items": len(news_items),
            "sources_summary": sources_summary,
            "categories_summary": categories_summary,
            "feed_stats": feed_stats,
            "top_stories": [
                {
                    "title": story["title"],
                    "source": story["source"],
                    "category": story.get("category", "General"),
                    "link": story["link"],
                    "summary": (
                        story.get("summary", "")[:200] + "..."
                        if len(story.get("summary", "")) > 200
                        else story.get("summary", "")
                    ),
                    "published_at": story.get("published_at"),
                    "fetched_at": story.get("fetched_at"),
                }
                for story in top_stories
            ],
            "all_items": news_items,
        }

        return summary

    def save_summary(self, summary: Dict, filename: str = None) -> str:
        """Save the RSS summary to a JSON file."""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"rss_summary_{timestamp}.json"

        try:
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(summary, f, indent=2, ensure_ascii=False)
            logger.info(f"RSS summary saved to {filename}")
            return filename
        except Exception as e:
            logger.error(f"Error saving RSS summary: {e}")
            return ""

    def save_sources_config(self, filename: str = "rss_sources_config.yaml"):
        """Save current RSS sources configuration to a YAML file."""
        try:
            config = {"rss_sources": [source.to_dict() for source in self.sources]}

            with open(filename, "w") as f:
                yaml.dump(config, f, default_flow_style=False, indent=2)

            logger.info(f"RSS sources configuration saved to {filename}")
            return filename

        except Exception as e:
            logger.error(f"Error saving RSS sources configuration: {e}")
            return ""

    def cleanup_cache(self, max_age_hours: int = 24):
        """Clean up old entries from the news cache."""
        cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
        old_hashes = [hash_key for hash_key, timestamp in self.news_cache.items() if timestamp < cutoff_time]

        for hash_key in old_hashes:
            del self.news_cache[hash_key]

        logger.info(f"Cleaned up {len(old_hashes)} old cache entries")


def main():
    """Main function to run the RSS news aggregator."""
    logger.info("Starting RSS News Aggregator...")

    # You can specify a config file here
    # aggregator = RSSNewsAggregator("rss_sources_config.yaml")
    aggregator = RSSNewsAggregator()

    try:
        # List current RSS sources
        print("\n" + "=" * 60)
        print("CONFIGURED RSS SOURCES")
        print("=" * 60)
        sources = aggregator.list_sources()
        for i, source in enumerate(sources, 1):
            print(f"{i}. {source['name']}")
            print(f"   URL: {source['url']}")
            print(f"   Category: {source['category']}")
            print(f"   Max Items: {source['max_items']}")
            print(f"   Update Interval: {source['update_interval']}s")
            print(f"   Enabled: {source['enabled']}")
            if source.get("last_fetch"):
                print(f"   Last Fetch: {source['last_fetch']}")
            print()

        # Fetch all RSS feeds
        news_items = aggregator.fetch_all_feeds(force_update=True)

        if news_items:
            summary = aggregator.create_rss_summary(news_items)
            saved_file = aggregator.save_summary(summary)

            print("\n" + "=" * 60)
            print("RSS NEWS SUMMARY")
            print("=" * 60)
            print(f"Date: {summary['date']}")
            print(f"Total Items: {summary['total_items']}")

            print(f"\nSources: {', '.join(summary['sources_summary'].keys())}")
            print(f"Categories: {', '.join(summary['categories_summary'].keys())}")

            print("\nFEED STATISTICS:")
            for feed_url, stats in summary["feed_stats"].items():
                print(f"  {stats['source']}: {stats['count']} items")

            print("\nTOP STORIES:")
            for i, story in enumerate(summary["top_stories"], 1):
                print(f"{i}. {story['title']}")
                print(f"   Source: {story['source']} | Category: {story['category']}")
                if story.get("summary"):
                    print(f"   Summary: {story['summary']}")
                if story.get("published_at"):
                    print(f"   Published: {story['published_at']}")
                print(f"   Link: {story['link']}")
                print()

            if saved_file:
                print(f"RSS summary saved to: {saved_file}")

            # Save RSS sources configuration
            config_file = aggregator.save_sources_config()
            if config_file:
                print(f"RSS sources configuration saved to: {config_file}")
        else:
            print("No RSS news items found.")

        # Clean up old cache entries
        aggregator.cleanup_cache(max_age_hours=24)

    except Exception as e:
        logger.error(f"Error in main execution: {e}")
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
