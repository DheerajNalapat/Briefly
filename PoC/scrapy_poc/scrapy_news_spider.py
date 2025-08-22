#!/usr/bin/env python3
"""
Scrapy News Spider for Briefly Bot

This script demonstrates using Scrapy framework for advanced web scraping
with better performance, middleware support, and pipeline processing.
"""

import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from scrapy import signals
from scrapy.signalmanager import SignalManager
import json
import logging
from datetime import datetime
from typing import List, Dict, Optional
import yaml
from urllib.parse import urljoin

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class NewsItem(scrapy.Item):
    """Scrapy Item for news data structure."""

    title = scrapy.Field()
    link = scrapy.Field()
    summary = scrapy.Field()
    source = scrapy.Field()
    category = scrapy.Field()
    published_at = scrapy.Field()
    extracted_at = scrapy.Field()
    content_hash = scrapy.Field()


class TechCrunchSpider(scrapy.Spider):
    """Spider for crawling TechCrunch AI news."""

    name = "techcrunch_ai"
    allowed_domains = ["techcrunch.com"]
    start_urls = ["https://techcrunch.com/tag/artificial-intelligence/"]

    custom_settings = {
        "ROBOTSTXT_OBEY": True,
        "DOWNLOAD_DELAY": 2,
        "CONCURRENT_REQUESTS_PER_DOMAIN": 1,
        "USER_AGENT": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    }

    def parse(self, response):
        """Parse the main page and extract article links."""
        logger.info(f"Parsing TechCrunch AI page: {response.url}")

        # Find article containers
        articles = response.css('article, div[class*="article"], div[class*="post"]')

        for article in articles[:10]:  # Limit to 10 articles
            try:
                # Extract title - get text content from title elements
                title_elem = article.css("h1, h2, h3, h4").get()
                if not title_elem:
                    continue

                # Extract clean text from the title element
                title = article.css("h1, h2, h3, h4 ::text").getall()
                title = " ".join([t.strip() for t in title if t.strip()])

                if not title:
                    continue

                # Extract link
                link = article.css("a::attr(href)").get()
                if not link:
                    continue
                link = urljoin(response.url, link)

                # Extract summary
                summary = article.css("p::text").get()
                summary = summary.strip() if summary else ""

                # Create news item
                news_item = NewsItem()
                news_item["title"] = title
                news_item["link"] = link
                news_item["summary"] = summary
                news_item["source"] = "TechCrunch AI"
                news_item["category"] = "Technology"
                news_item["extracted_at"] = datetime.now().isoformat()

                yield news_item

            except Exception as e:
                logger.warning(f"Error extracting article: {e}")
                continue


class VentureBeatSpider(scrapy.Spider):
    """Spider for crawling VentureBeat AI news."""

    name = "venturebeat_ai"
    allowed_domains = ["venturebeat.com"]
    start_urls = ["https://venturebeat.com/category/ai/"]

    custom_settings = {
        "ROBOTSTXT_OBEY": True,
        "DOWNLOAD_DELAY": 2,
        "CONCURRENT_REQUESTS_PER_DOMAIN": 1,
        "USER_AGENT": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    }

    def parse(self, response):
        """Parse the main page and extract article links."""
        logger.info(f"Parsing VentureBeat AI page: {response.url}")

        # Find article containers
        articles = response.css('article, div[class*="article"], div[class*="post"]')

        for article in articles[:10]:  # Limit to 10 articles
            try:
                # Extract title - get text content from title elements
                title_elem = article.css("h1, h2, h3, h4").get()
                if not title_elem:
                    continue

                # Extract clean text from the title element
                title = article.css("h1, h2, h3, h4 ::text").getall()
                title = " ".join([t.strip() for t in title if t.strip()])

                if not title:
                    continue

                # Extract link
                link = article.css("a::attr(href)").get()
                if not link:
                    continue
                link = urljoin(response.url, link)

                # Extract summary
                summary = article.css("p::text").get()
                summary = summary.strip() if summary else ""

                # Create news item
                news_item = NewsItem()
                news_item["title"] = title
                news_item["link"] = link
                news_item["summary"] = summary
                news_item["source"] = "VentureBeat AI"
                news_item["category"] = "Technology"
                news_item["extracted_at"] = datetime.now().isoformat()

                yield news_item

            except Exception as e:
                logger.warning(f"Error extracting article: {e}")
                continue


class MITTechReviewSpider(scrapy.Spider):
    """Spider for crawling MIT Technology Review AI news."""

    name = "mit_tech_review"
    allowed_domains = ["technologyreview.com"]
    start_urls = ["https://www.technologyreview.com/topic/artificial-intelligence/"]

    custom_settings = {
        "ROBOTSTXT_OBEY": True,
        "DOWNLOAD_DELAY": 3,
        "CONCURRENT_REQUESTS_PER_DOMAIN": 1,
        "USER_AGENT": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    }

    def parse(self, response):
        """Parse the main page and extract article links."""
        logger.info(f"Parsing MIT Tech Review AI page: {response.url}")

        # Find article containers
        articles = response.css('article, div[class*="article"], div[class*="post"]')

        for article in articles[:8]:  # Limit to 8 articles
            try:
                # Extract title - get text content from title elements
                title_elem = article.css("h1, h2, h3, h4").get()
                if not title_elem:
                    continue

                # Extract clean text from the title element
                title = article.css("h1, h2, h3, h4 ::text").getall()
                title = " ".join([t.strip() for t in title if t.strip()])

                if not title:
                    continue

                # Extract link
                link = article.css("a::attr(href)").get()
                if not link:
                    continue
                link = urljoin(response.url, link)

                # Extract summary
                summary = article.css("p::text").get()
                summary = summary.strip() if summary else ""

                # Create news item
                news_item = NewsItem()
                news_item["title"] = title
                news_item["link"] = link
                news_item["summary"] = summary
                news_item["source"] = "MIT Technology Review AI"
                news_item["category"] = "Technology"
                news_item["extracted_at"] = datetime.now().isoformat()

                yield news_item

            except Exception as e:
                logger.warning(f"Error extracting article: {e}")
                continue


class NewsPipeline:
    """Pipeline for processing and cleaning news items."""

    # Class-level storage for collected items
    news_items = []
    seen_titles = set()

    @classmethod
    def from_crawler(cls, crawler):
        pipeline = cls()
        crawler.signals.connect(pipeline.spider_closed, signal=signals.spider_closed)
        return pipeline

    def __init__(self):
        # Reset class-level storage for new runs
        NewsPipeline.news_items = []
        NewsPipeline.seen_titles = set()

    def process_item(self, item, spider):
        """Process each news item."""
        # Basic validation
        if not item.get("title") or not item.get("link"):
            return item

        # Check for duplicates based on title
        title_normalized = self.normalize_title(item["title"])
        if title_normalized in self.seen_titles:
            return item

            # Add to seen titles
        NewsPipeline.seen_titles.add(title_normalized)

        # Generate content hash
        content = item.get("title", "") + item.get("summary", "")
        item["content_hash"] = self.generate_content_hash(content)

        # Add to collection
        NewsPipeline.news_items.append(dict(item))

        return item

    def normalize_title(self, title: str) -> str:
        """Normalize title for duplicate detection."""
        stop_words = {
            "the",
            "a",
            "an",
            "and",
            "or",
            "but",
            "in",
            "on",
            "at",
            "to",
            "for",
            "of",
            "with",
            "by",
        }
        words = title.lower().split()
        filtered_words = [word for word in words if word not in stop_words and len(word) > 2]
        return " ".join(filtered_words)

    def generate_content_hash(self, content: str) -> str:
        """Generate a hash for content."""
        import hashlib

        return hashlib.md5(content.encode("utf-8")).hexdigest()

    def spider_closed(self, spider):
        """Called when spider is closed."""
        logger.info(f"Spider {spider.name} closed. Collected {len(NewsPipeline.news_items)} items.")


class ScrapyNewsCrawler:
    """Main class for managing Scrapy-based news crawling."""

    def __init__(self, config_file: Optional[str] = None):
        self.config_file = config_file
        self.spiders = []
        self.news_items = []
        self.settings = self.get_scrapy_settings()

        if config_file:
            self.load_spiders_from_config(config_file)
        else:
            self.load_default_spiders()

    def get_scrapy_settings(self) -> Dict:
        """Get Scrapy settings for the crawler."""
        return {
            "ITEM_PIPELINES": {
                "__main__.NewsPipeline": 300,
            },
            "ROBOTSTXT_OBEY": True,
            "DOWNLOAD_DELAY": 2,
            "CONCURRENT_REQUESTS_PER_DOMAIN": 1,
            "USER_AGENT": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "LOG_LEVEL": "INFO",
        }

    def load_spiders_from_config(self, config_file: str):
        """Load spider configurations from YAML file."""
        try:
            with open(config_file, "r") as f:
                config = yaml.safe_load(f)

            for spider_config in config.get("scrapy_spiders", []):
                spider_class = self.get_spider_class(spider_config["name"])
                if spider_class:
                    self.spiders.append(spider_class)
                    logger.info(f"Loaded spider: {spider_config['name']}")

        except Exception as e:
            logger.error(f"Error loading spider config file {config_file}: {e}")
            logger.info("Falling back to default spiders")
            self.load_default_spiders()

    def load_default_spiders(self):
        """Load default spiders."""
        self.spiders = [TechCrunchSpider, VentureBeatSpider, MITTechReviewSpider]
        logger.info(f"Loaded {len(self.spiders)} default spiders")

    def get_spider_class(self, spider_name: str):
        """Get spider class by name."""
        spider_map = {
            "techcrunch_ai": TechCrunchSpider,
            "venturebeat_ai": VentureBeatSpider,
            "mit_tech_review": MITTechReviewSpider,
        }
        return spider_map.get(spider_name)

    def crawl_with_scrapy(self) -> List[Dict]:
        """Run Scrapy crawler and collect news items."""
        try:
            # Create a custom pipeline instance to collect items
            pipeline = NewsPipeline()

            # Create crawler process
            process = CrawlerProcess(self.settings)

            # Add spiders to the process
            for spider_class in self.spiders:
                process.crawl(spider_class)

            # Start the crawling process
            process.start()

            # Get collected items from pipeline class
            self.news_items = NewsPipeline.news_items
            logger.info(f"Scrapy crawling completed. Collected {len(self.news_items)} items.")

            return self.news_items

        except Exception as e:
            logger.error(f"Error during Scrapy crawling: {e}")
            return []

    def create_summary(self, news_items: List[Dict]) -> Dict:
        """Create a structured summary of the news."""
        if not news_items:
            return {
                "date": datetime.now().isoformat(),
                "summary": "No news items found.",
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
        top_stories = sorted(news_items, key=lambda x: len(x.get("summary", "")), reverse=True)[:8]

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
                    "extracted_at": story.get("extracted_at"),
                }
                for story in top_stories
            ],
            "all_items": news_items,
        }

        return summary

    def save_summary(self, summary: Dict, filename: str = None) -> str:
        """Save the summary to a JSON file."""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"scrapy_summary_{timestamp}.json"

        try:
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(summary, f, indent=2, ensure_ascii=False)
            logger.info(f"Scrapy summary saved to {filename}")
            return filename
        except Exception as e:
            logger.error(f"Error saving Scrapy summary: {e}")
            return ""


def main():
    """Main function to run the Scrapy news crawler."""
    logger.info("Starting Scrapy News Crawler...")

    # You can specify a config file here
    # crawler = ScrapyNewsCrawler("scrapy_spiders_config.yaml")
    crawler = ScrapyNewsCrawler()

    try:
        # List current spiders
        print("\n" + "=" * 60)
        print("CONFIGURED SCRAPY SPIDERS")
        print("=" * 60)
        for i, spider_class in enumerate(crawler.spiders, 1):
            print(f"{i}. {spider_class.name}")
            print(f"   Domain: {spider_class.allowed_domains[0]}")
            print(f"   Start URL: {spider_class.start_urls[0]}")
            print()

        # Run Scrapy crawling
        news_items = crawler.crawl_with_scrapy()

        if news_items:
            summary = crawler.create_summary(news_items)
            saved_file = crawler.save_summary(summary)

            print("\n" + "=" * 60)
            print("SCRAPY NEWS SUMMARY")
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
                print(f"Scrapy summary saved to: {saved_file}")
        else:
            print("No news items found.")

    except Exception as e:
        logger.error(f"Error in main execution: {e}")
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
