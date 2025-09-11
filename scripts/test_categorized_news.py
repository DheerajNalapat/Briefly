#!/usr/bin/env python3
"""
Test script for categorized news fetching using NewsAPI
"""

import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "PoC", "news_source_quality_poc"))

from newsapi_collector import SimpleNewsAPICollector, Category
from config import NEWSAPI_KEY


def test_categorized_news():
    """Test fetching news by categories"""

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

    collector = SimpleNewsAPICollector(NEWSAPI_KEY, "test_categorized_news.json")

    print("=== Testing Categorized News Fetching ===\n")

    # Test 1: Fetch all categories
    print("1. Fetching news for all categories...")
    collector.fetch_news_by_categories(news_query_params, max_articles_per_category=2)

    # Test 2: Fetch specific category
    print("\n2. Fetching only technical news...")
    collector.fetch_news_by_single_category(Category.TECHNICAL, news_query_params, max_articles=3)

    print(f"\n=== Final Results ===")
    print(f"Total articles collected: {len(collector.collected_articles)}")
    print(f"Articles saved to: {collector.output_file}")


if __name__ == "__main__":
    test_categorized_news()
