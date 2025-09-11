#!/usr/bin/env python3
"""
Test script for the NewsAPI collector
"""

import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "PoC", "news_source_quality_poc"))

from newsapi_collector import SimpleNewsAPICollector


def test_newsapi_collector():
    """Test the NewsAPI collector with a sample query"""

    # You need to set your NewsAPI key here
    API_KEY = "your_newsapi_key_here"

    if API_KEY == "your_newsapi_key_here":
        print("Please set your NewsAPI key in the script")
        print("Get your free key at: https://newsapi.org/register")
        print("Then update the API_KEY variable in this script")
        return

    collector = SimpleNewsAPICollector(API_KEY, "test_newsapi_articles.json")

    # Test with a simple query
    print("=== Testing NewsAPI Collector ===")
    collector.run_search("artificial intelligence", max_articles=5)

    # Test with another query to show appending
    print("\n=== Testing with another query ===")
    collector.run_search("machine learning", max_articles=3)


if __name__ == "__main__":
    test_newsapi_collector()
