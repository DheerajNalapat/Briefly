#!/usr/bin/env python3
"""
Debug script for NewsAPI collector to see why categorized fetching returns 0 articles
"""

import sys
import os
import logging

# Add the project root to the path
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from slackbot.collectors.newsapi_org_collector import NewsAPICollector, Category, NEWS_QUERY_PARAMS

# Set the API key from config
try:
    from PoC.news_source_quality_poc.config import NEWSAPI_KEY

    os.environ["NEWSAPI_KEY"] = NEWSAPI_KEY
except ImportError:
    print("Warning: Could not import NEWSAPI_KEY from config")


def debug_newsapi_collector():
    """Debug the NewsAPI collector."""

    # Set up logging
    logging.basicConfig(level=logging.DEBUG, format="%(levelname)s: %(message)s")

    print("=== Debugging NewsAPI Collector ===")

    # Create collector
    collector = NewsAPICollector(name="Debug NewsAPI Collector")

    if not collector.is_available():
        print("❌ NewsAPI Collector not available")
        return

    print("✅ NewsAPI Collector initialized successfully")

    # Test 1: Test a single source directly
    print("\n🔍 Testing single source directly...")
    sources = collector.get_source_status()
    if sources:
        first_source = sources[0]
        print(f"Testing source: {first_source['name']}")
        print(f"Query: {first_source['query']}")
        print(f"Category: {first_source['category']}")

        # Create a NewsAPISource object from the dict
        from slackbot.collectors.newsapi_org_collector import NewsAPISource

        test_source = NewsAPISource(
            name=first_source["name"],
            query=first_source["query"],
            category=first_source["category"],
            max_items=3,
            enabled=True,
        )

        print(f"\nFetching articles for: {test_source.name}")
        articles = collector.fetch_articles(test_source)
        print(f"✅ Fetched {len(articles)} articles directly")

        if articles:
            print("\n📰 Sample articles:")
            for i, article in enumerate(articles[:2], 1):
                print(f"  {i}. {article.title[:60]}...")
                print(f"     Source: {article.source}")
                print(f"     Category: {article.category}")
                print()

    # Test 2: Test categorized fetching with debug
    print("\n🔍 Testing categorized fetching with debug...")
    try:
        categorized_results = collector.fetch_news_by_categories(max_articles_per_category=2)
        print(f"✅ Categorized results: {len(categorized_results)} articles")

        if categorized_results:
            print("\n📰 Sample categorized articles:")
            for i, item in enumerate(categorized_results[:2], 1):
                print(f"  {i}. {item['title'][:60]}...")
                print(f"     Source: {item['source']}")
                print(f"     Category: {item['category']}")
                print()
    except Exception as e:
        print(f"❌ Error in categorized collection: {e}")
        import traceback

        traceback.print_exc()

    print("\n=== Debug Complete ===")


if __name__ == "__main__":
    debug_newsapi_collector()
