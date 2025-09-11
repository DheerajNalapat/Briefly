#!/usr/bin/env python3
"""
Test script for NewsAPI client-based collector
"""

import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "PoC", "news_source_quality_poc"))

from newsapi_client_collector import NewsAPIClientCollector, Category
from config import NEWSAPI_KEY


def test_newsapi_client():
    """Test the NewsAPI client-based collector"""

    if not NEWSAPI_KEY or NEWSAPI_KEY == "your_newsapi_key_here":
        print("Please set your NewsAPI key in the .env file")
        print("Add: NEWSAPI_KEY=your_actual_key")
        print("Get your free key at: https://newsapi.org/register")
        return

    # Define the query parameters
    news_query_params = {
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
    }

    collector = NewsAPIClientCollector(NEWSAPI_KEY, "test_client_news.json")

    print("=== Testing NewsAPI Client SDK Collector ===\n")

    # Test 1: Basic search
    print("1. Testing basic search...")
    collector.run_search("artificial intelligence", max_articles=3, sort_by="relevancy")

    # Test 2: Top headlines
    print("\n2. Testing top headlines...")
    collector.run_top_headlines(category="technology", max_articles=3)

    # Test 3: Search with specific sources
    print("\n3. Testing search with specific sources...")
    collector.run_search("AI", max_articles=2, sources="techcrunch,ars-technica")

    # Test 4: Fetch all categories
    print("\n4. Fetching news for all categories...")
    collector.fetch_news_by_categories(news_query_params, max_articles_per_category=2)

    # Test 5: Fetch specific category
    print("\n5. Fetching only technical news...")
    collector.fetch_news_by_single_category(Category.TECHNICAL, news_query_params, max_articles=3)

    # Test 6: Get sources
    print("\n6. Getting available sources...")
    collector.run_sources_search(category="technology")

    print(f"\n=== Final Results ===")
    print(f"Total articles collected: {len(collector.collected_articles)}")
    print(f"Articles saved to: {collector.output_file}")


if __name__ == "__main__":
    test_newsapi_client()
