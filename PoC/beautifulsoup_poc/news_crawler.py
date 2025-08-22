#!/usr/bin/env python3
"""
Generalized News Crawler Script for Briefly Bot

This script uses BeautifulSoup to crawl various news sources and extract
structured information. Sources are configurable and easily extensible.
"""

import requests
from bs4 import BeautifulSoup
import json
import time
from datetime import datetime
from typing import List, Dict, Optional, Callable
import logging
from urllib.parse import urljoin
import yaml

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class NewsSource:
    """Represents a configurable news source."""

    def __init__(
        self,
        name: str,
        url: str,
        base_url: str,
        title_selectors: List[str],
        link_selectors: List[str],
        summary_selectors: Optional[List[str]] = None,
        category: str = "General",
        delay: int = 2,
    ):
        self.name = name
        self.url = url
        self.base_url = base_url
        self.title_selectors = title_selectors
        self.link_selectors = link_selectors
        self.summary_selectors = summary_selectors or []
        self.category = category
        self.delay = delay

    def to_dict(self) -> Dict:
        """Convert source to dictionary for serialization."""
        return {
            "name": self.name,
            "url": self.url,
            "base_url": self.base_url,
            "title_selectors": self.title_selectors,
            "link_selectors": self.link_selectors,
            "summary_selectors": self.summary_selectors,
            "category": self.category,
            "delay": self.delay,
        }


class NewsCrawler:
    """Generalized news crawler that can handle multiple configurable sources."""

    def __init__(self, config_file: Optional[str] = None):
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            }
        )
        self.sources = []
        self.config_file = config_file

        if config_file:
            self.load_sources_from_config(config_file)
        else:
            self.load_default_sources()

    def load_sources_from_config(self, config_file: str):
        """Load news sources from a YAML configuration file."""
        try:
            with open(config_file, "r") as f:
                config = yaml.safe_load(f)

            for source_config in config.get("sources", []):
                source = NewsSource(
                    name=source_config["name"],
                    url=source_config["url"],
                    base_url=source_config["base_url"],
                    title_selectors=source_config["title_selectors"],
                    link_selectors=source_config["link_selectors"],
                    summary_selectors=source_config.get("summary_selectors", []),
                    category=source_config.get("category", "General"),
                    delay=source_config.get("delay", 2),
                )
                self.sources.append(source)

            logger.info(f"Loaded {len(self.sources)} sources from {config_file}")

        except Exception as e:
            logger.error(f"Error loading config file {config_file}: {e}")
            logger.info("Falling back to default sources")
            self.load_default_sources()

    def load_default_sources(self):
        """Load default news sources."""
        default_sources = [
            NewsSource(
                name="TechCrunch AI",
                url="https://techcrunch.com/tag/artificial-intelligence/",
                base_url="https://techcrunch.com",
                title_selectors=["h1", "h2", "h3", "h4"],
                link_selectors=["a"],
                summary_selectors=["p"],
                category="Technology",
                delay=2,
            ),
            NewsSource(
                name="VentureBeat AI",
                url="https://venturebeat.com/category/ai/",
                base_url="https://venturebeat.com",
                title_selectors=["h1", "h2", "h3", "h4"],
                link_selectors=["a"],
                summary_selectors=["p"],
                category="Technology",
                delay=2,
            ),
            NewsSource(
                name="MIT Technology Review",
                url="https://www.technologyreview.com/topic/artificial-intelligence/",
                base_url="https://www.technologyreview.com",
                title_selectors=["h1", "h2", "h3", "h4"],
                link_selectors=["a"],
                summary_selectors=["p"],
                category="Technology",
                delay=3,
            ),
        ]

        self.sources = default_sources
        logger.info(f"Loaded {len(self.sources)} default sources")

    def add_source(self, source: NewsSource):
        """Add a new news source."""
        self.sources.append(source)
        logger.info(f"Added source: {source.name}")

    def remove_source(self, source_name: str):
        """Remove a news source by name."""
        self.sources = [s for s in self.sources if s.name != source_name]
        logger.info(f"Removed source: {source_name}")

    def list_sources(self) -> List[Dict]:
        """List all configured sources."""
        return [source.to_dict() for source in self.sources]

    def fetch_page(self, url: str) -> Optional[BeautifulSoup]:
        """Fetch a web page and return BeautifulSoup object."""
            try:
            logger.info(f"Fetching: {url}")
            response = self.session.get(url, timeout=10)
                response.raise_for_status()

                # Check if content is HTML
                content_type = response.headers.get("content-type", "").lower()
                if "text/html" not in content_type:
                    logger.warning(f"Non-HTML content type: {content_type}")
                    return None

                return BeautifulSoup(response.content, "lxml")

            except requests.RequestException as e:
            logger.error(f"Error fetching {url}: {e}")
                    return None
            except Exception as e:
                logger.error(f"Unexpected error fetching {url}: {e}")
        return None

    def extract_news_from_source(
        self, soup: BeautifulSoup, source: NewsSource
    ) -> List[Dict]:
        """Extract news from a source using its configuration."""
        news_items = []

        try:
            # Find article containers - look for common patterns
            article_selectors = [
                "article",
                "div[class*='article']",
                "div[class*='post']",
                "div[class*='story']",
                "div[class*='entry']",
                "div[class*='item']",
            ]

            articles = []
            for selector in article_selectors:
                articles.extend(soup.select(selector))

            # Remove duplicates while preserving order
            seen = set()
            unique_articles = []
            for article in articles:
                article_id = id(article)
                if article_id not in seen:
                    seen.add(article_id)
                    unique_articles.append(article)

            # Limit to reasonable number of articles
            articles_to_process = unique_articles[:15]

            for article in articles_to_process:
                try:
                    # Extract title
                    title = None
                    for selector in source.title_selectors:
                        title_elem = article.select_one(selector)
                        if title_elem:
                            title = title_elem.get_text(strip=True)
                            if title and len(title) > 10:  # Basic validation
                                break

                    if not title:
                        continue

                    # Extract link
                    link = None
                    for selector in source.link_selectors:
                        link_elem = article.select_one(selector)
                        if link_elem and link_elem.get("href"):
                            link = link_elem["href"]
                            if not link.startswith("http"):
                                link = urljoin(source.base_url, link)
                            if link.startswith("http"):
                                break

                    if not link:
                        continue

                    # Extract summary
                    summary = ""
                    for selector in source.summary_selectors:
                        summary_elem = article.select_one(selector)
                        if summary_elem:
                            summary = summary_elem.get_text(strip=True)
                            if summary and len(summary) > 20:  # Basic validation
                                break

                    # Create news item
                    news_item = {
                        "title": title,
                        "link": link,
                        "summary": summary,
                        "source": source.name,
                        "category": source.category,
                        "extracted_at": datetime.now().isoformat(),
                    }

                        news_items.append(news_item)

                except Exception as e:
                    logger.debug(f"Error extracting article from {source.name}: {e}")
                    continue

        except Exception as e:
            logger.error(f"Error extracting from {source.name}: {e}")

        return news_items

    def crawl_sources(self, max_items_per_source: int = 10) -> List[Dict]:
        """Crawl all configured news sources."""
        all_news = []

        if not self.sources:
            logger.warning("No sources configured. Loading default sources.")
            self.load_default_sources()

        for source in self.sources:
            logger.info(f"Crawling {source.name}")

            try:
                soup = self.fetch_page(source.url)
                if soup:
                    news_items = self.extract_news_from_source(soup, source)

                    # Limit items per source
                    if len(news_items) > max_items_per_source:
                        news_items = news_items[:max_items_per_source]

                    all_news.extend(news_items)
                    logger.info(f"Extracted {len(news_items)} items from {source.name}")

                    # Respect source-specific delay
                    if source.delay > 0:
                        time.sleep(source.delay)
                else:
                    logger.warning(f"Failed to fetch {source.name}")

            except Exception as e:
                logger.error(f"Error crawling {source.name}: {e}")
                continue

        return all_news

    def create_daily_summary(self, news_items: List[Dict]) -> Dict:
        """Create a structured daily summary of the news."""
        if not news_items:
            return {
                "date": datetime.now().isoformat(),
                "summary": "No news items found today.",
                "total_items": 0,
                "sources_summary": {},
                "categories_summary": {},
                "top_stories": [],
            }

        # Group by source and category
        sources_summary = {}
        categories_summary = {}

        for item in news_items:
            source = item.get("source", "Unknown")
            category = item.get("category", "General")

            sources_summary[source] = sources_summary.get(source, 0) + 1
            categories_summary[category] = categories_summary.get(category, 0) + 1

        # Select top stories (limit to 8)
        top_stories = sorted(
            news_items, key=lambda x: len(x.get("summary", "")), reverse=True
        )[:8]

        summary = {
            "date": datetime.now().isoformat(),
            "summary": f"Found {len(news_items)} news items from {len(sources_summary)} sources",
            "total_items": len(news_items),
            "sources_summary": sources_summary,
            "categories_summary": categories_summary,
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
                }
                for story in top_stories
            ],
            "all_items": news_items,
        }

        return summary

    def save_summary(self, summary: Dict, filename: str = None) -> str:
        """Save the daily summary to a JSON file."""
        if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"daily_summary_{timestamp}.json"

        try:
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(summary, f, indent=2, ensure_ascii=False)
            logger.info(f"Summary saved to {filename}")
            return filename
        except Exception as e:
            logger.error(f"Error saving summary: {e}")
            return ""

    def save_sources_config(self, filename: str = "sources_config.yaml"):
        """Save current sources configuration to a YAML file."""
        try:
            config = {"sources": [source.to_dict() for source in self.sources]}

            with open(filename, "w") as f:
                yaml.dump(config, f, default_flow_style=False, indent=2)

            logger.info(f"Sources configuration saved to {filename}")
            return filename

        except Exception as e:
            logger.error(f"Error saving sources configuration: {e}")
            return ""


def main():
    """Main function to run the news crawler."""
    logger.info("Starting Generalized News Crawler...")

    # You can specify a config file here
    # crawler = NewsCrawler("sources_config.yaml")
    crawler = NewsCrawler()

    try:
        # List current sources
        print("\n" + "=" * 60)
        print("CONFIGURED NEWS SOURCES")
        print("=" * 60)
        sources = crawler.list_sources()
        for i, source in enumerate(sources, 1):
            print(f"{i}. {source['name']}")
            print(f"   URL: {source['url']}")
            print(f"   Category: {source['category']}")
            print(f"   Delay: {source['delay']}s")
            print()

        # Crawl all sources
        news_items = crawler.crawl_sources(max_items_per_source=8)

        if news_items:
            summary = crawler.create_daily_summary(news_items)
            saved_file = crawler.save_summary(summary)

            print("\n" + "=" * 60)
            print("DAILY NEWS SUMMARY")
            print("=" * 60)
            print(f"Date: {summary['date']}")
            print(f"Total Items: {summary['total_items']}")

            print(f"\nSources: {', '.join(summary['sources_summary'].keys())}")
            print(f"Categories: {', '.join(summary['categories_summary'].keys())}")

            print("\nTOP STORIES:")
            for i, story in enumerate(summary["top_stories"], 1):
                print(f"{i}. {story['title']}")
                print(f"   Source: {story['source']} | Category: {story['category']}")
                if story.get("summary"):
                    print(f"   Summary: {story['summary']}")
                print(f"   Link: {story['link']}")
                print()

            if saved_file:
                print(f"Summary saved to: {saved_file}")

            # Save sources configuration
            config_file = crawler.save_sources_config()
            if config_file:
                print(f"Sources configuration saved to: {config_file}")
        else:
            print("No news items found.")

    except Exception as e:
        logger.error(f"Error in main execution: {e}")
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
