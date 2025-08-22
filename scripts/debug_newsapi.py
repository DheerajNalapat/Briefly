#!/usr/bin/env python3
"""Debug script for NewsAPI issues."""

import os
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from newsapi import NewsApiClient


def test_newsapi():
    """Test NewsAPI directly."""
    print("🔍 Testing NewsAPI directly...")

    # Get API key
    api_key = os.getenv("NEWSAPI_KEY")
    if not api_key:
        print("❌ NEWSAPI_KEY not set")
        return

    print(f"✅ API key found: {api_key[:10]}...")

    try:
        # Create client
        client = NewsApiClient(api_key=api_key)
        print("✅ NewsAPI client created")

        # Test different queries
        test_cases = [
            {
                "name": "Tech AI Headlines",
                "params": {
                    "q": "AI",
                    "category": "technology",
                    "language": "en",
                    "country": "us",
                    "page_size": 5,
                },
            },
            {
                "name": "Business AI Headlines",
                "params": {
                    "q": "AI",
                    "category": "business",
                    "language": "en",
                    "country": "us",
                    "page_size": 5,
                },
            },
            {
                "name": "Science AI Headlines",
                "params": {
                    "q": "AI",
                    "category": "science",
                    "language": "en",
                    "country": "us",
                    "page_size": 5,
                },
            },
            {
                "name": "Health AI Headlines",
                "params": {
                    "q": "AI",
                    "category": "health",
                    "language": "en",
                    "country": "us",
                    "page_size": 5,
                },
            },
        ]

        for test_case in test_cases:
            print(f"\n📰 Testing: {test_case['name']}")
            print(f"   Params: {test_case['params']}")

            try:
                response = client.get_top_headlines(**test_case["params"])

                print(f"   Status: {response.get('status')}")
                print(f"   Total Results: {response.get('totalResults', 0)}")
                print(f"   Articles: {len(response.get('articles', []))}")

                if response.get("status") == "ok" and response.get("articles"):
                    article = response["articles"][0]
                    print(f"   Sample: {article.get('title', 'N/A')[:60]}...")
                    print(f"   URL: {article.get('url', 'N/A')[:80]}...")
                else:
                    print(f"   Error: {response.get('message', 'Unknown error')}")

            except Exception as e:
                print(f"   ❌ Exception: {e}")

    except Exception as e:
        print(f"❌ Error creating NewsAPI client: {e}")


if __name__ == "__main__":
    test_newsapi()
