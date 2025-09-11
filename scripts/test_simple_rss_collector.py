#!/usr/bin/env python3
"""
Simple test script for the RSS collector
Run this to test collecting from different sources separately
"""

import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "PoC", "news_source_quality_poc"))

from rss_collector import SimpleRSSCollector


def test_single_source():
    """Test collecting from a single source"""
    collector = SimpleRSSCollector("test_articles.json")

    # Test with Medium AI feed
    print("=== Testing Medium AI Feed ===")
    collector.run_single_source(source_name="Medium AI", rss_url="https://medium.com/feed/agentic-ai", max_items=3)

    print("\n=== Testing TechCrunch Feed ===")
    collector.run_single_source(source_name="TechCrunch", rss_url="https://techcrunch.com/feed/", max_items=3)


if __name__ == "__main__":
    test_single_source()
