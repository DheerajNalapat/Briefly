#!/usr/bin/env python3
"""
Test script for Event Registry API collector
"""

import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "PoC", "news_source_quality_poc"))

from eventregistry_collector import EventRegistryCollector


def test_eventregistry():
    """Test the Event Registry collector"""

    # You can set your API key here for testing
    API_KEY = "your_eventregistry_api_key_here"

    if API_KEY == "your_eventregistry_api_key_here":
        print("Please set your Event Registry API key in this script")
        print("Get your API key at: https://eventregistry.org/")
        return

    collector = EventRegistryCollector(API_KEY, "test_eventregistry.json")

    # Test the suggestSourcesFast endpoint as requested
    print("=== Testing Event Registry suggestSourcesFast endpoint ===")
    collector.run_suggest_sources("BBC")

    print("\n=== Testing with other prefixes ===")
    collector.run_suggest_sources("Tech")
    collector.run_suggest_sources("News")


if __name__ == "__main__":
    test_eventregistry()
