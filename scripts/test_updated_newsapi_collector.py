#!/usr/bin/env python3
"""
Test script for the updated NewsAPI collector with query params
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


def test_newsapi_collector():
    """Test the updated NewsAPI collector."""

    # Set up logging
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    print("=== Testing Updated NewsAPI Collector ===")

    # Create collector
    collector = NewsAPICollector(name="Test NewsAPI Collector")

    if not collector.is_available():
        print("❌ NewsAPI Collector not available - check dependencies and API keys")
        print("Make sure NEWSAPI_KEY environment variable is set")
        return

    print("✅ NewsAPI Collector initialized successfully")

    # Test 1: Show query params structure
    print("\n📋 Available Query Parameters:")
    for category, params in NEWS_QUERY_PARAMS.items():
        print(f"  {category.value.upper()}:")
        print(f"    Query: {params['query']}")
        print(f"    Keywords: {', '.join(params['keywords'][:5])}...")
        print()

    # Test 2: Test traditional collection
    print("📊 Testing traditional NewsAPI collection...")
    try:
        results = collector.collect()
        print(f"✅ Collected {len(results)} articles from traditional sources")

        if results:
            print("\n📰 Sample traditional articles:")
            for i, item in enumerate(results[:2], 1):
                print(f"  {i}. {item['title'][:60]}...")
                print(f"     Source: {item['source']}")
                print(f"     Category: {item['category']}")
                print()
    except Exception as e:
        print(f"❌ Error in traditional collection: {e}")

    # Test 3: Test categorized collection
    print("📊 Testing categorized NewsAPI collection...")
    try:
        categorized_results = collector.fetch_news_by_categories(max_articles_per_category=2)
        print(f"✅ Collected {len(categorized_results)} categorized articles")

        if categorized_results:
            print("\n📰 Sample categorized articles:")
            for i, item in enumerate(categorized_results[:3], 1):
                print(f"  {i}. {item['title'][:60]}...")
                print(f"     Source: {item['source']}")
                print(f"     Category: {item['category']}")
                print(f"     Keywords: {', '.join(item.get('keywords', [])[:3])}...")
                print()
    except Exception as e:
        print(f"❌ Error in categorized collection: {e}")

    # Test 4: Test single category collection
    print("📊 Testing single category collection (Technical)...")
    try:
        technical_results = collector.fetch_news_by_single_category(Category.TECHNICAL, max_articles=3)
        print(f"✅ Collected {len(technical_results)} technical articles")

        if technical_results:
            print("\n📰 Sample technical articles:")
            for i, item in enumerate(technical_results[:2], 1):
                print(f"  {i}. {item['title'][:60]}...")
                print(f"     Source: {item['source']}")
                print(f"     Keywords: {', '.join(item.get('keywords', [])[:3])}...")
                print()
    except Exception as e:
        print(f"❌ Error in single category collection: {e}")

    # Test 5: Show source status
    print("\n🔍 Source Status:")
    try:
        sources = collector.get_source_status()
        for source in sources:
            status = "✅ Enabled" if source["enabled"] else "❌ Disabled"
            print(f"  {source['name']}: {status}")
            print(f"    Query: {source['query'][:50]}...")
            print(f"    Category: {source['category']}")
            print()
    except Exception as e:
        print(f"❌ Error getting source status: {e}")

    print("=== Test Complete ===")


if __name__ == "__main__":
    test_newsapi_collector()
