#!/usr/bin/env python3
"""
Demo script for improved NewsAPI collector
Shows how to use different endpoints and parameters for more accurate results
"""

from newsapi_collector import SimpleNewsAPICollector
from config import NEWSAPI_KEY


def demo_newsapi():
    """Demo the improved NewsAPI collector functionality"""

    if NEWSAPI_KEY == "your_newsapi_key_here":
        print("Please set your NewsAPI key in the config.py file")
        print("Get your free key at: https://newsapi.org/register")
        return

    # Create collector
    collector = SimpleNewsAPICollector(NEWSAPI_KEY, "demo_newsapi_articles.json")

    print("=== NewsAPI Collector Demo ===\n")

    # Demo 1: Everything endpoint with different sorting
    print("1. Everything Search - Sort by Relevancy")
    collector.run_search("artificial intelligence", max_articles=2, sort_by="relevancy")

    print("\n2. Everything Search - Sort by Popularity")
    collector.run_search("machine learning", max_articles=2, sort_by="popularity")

    # Demo 2: Top Headlines (more accurate for breaking news)
    print("\n3. Top Headlines - Technology Category")
    collector.run_top_headlines(category="technology", max_articles=2)

    print("\n4. Top Headlines - Business Category")
    collector.run_top_headlines(category="business", max_articles=2)

    # Demo 3: Search with specific sources (more accurate)
    print("\n5. Search with Specific Tech Sources")
    collector.run_search("AI", max_articles=2, sources="techcrunch,ars-technica")

    # Demo 4: Get available sources
    print("\n6. Available Technology Sources")
    collector.run_sources_search(category="technology")

    print(f"\n{'='*50}")
    print(f"Total articles collected: {len(collector.collected_articles)}")
    print(f"Articles saved to: {collector.output_file}")


if __name__ == "__main__":
    demo_newsapi()
