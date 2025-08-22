#!/usr/bin/env python3
"""
Debug script to see what content is actually being passed to the summarizer.
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Load environment variables
try:
    from dotenv import load_dotenv

    load_dotenv(project_root / ".env")
    print("✅ Environment variables loaded from .env file")
except ImportError:
    print("⚠️ python-dotenv not available, using shell environment")
except Exception as e:
    print(f"⚠️ Could not load .env file: {e}")


def debug_article_content():
    """Debug what content is being passed to the summarizer."""
    print("🔍 Debugging Article Content")
    print("=" * 60)

    try:
        from slackbot.collectors.api_collector import create_api_collector

        # Create collector and get real articles
        collector = create_api_collector()

        if not collector.is_available():
            print("❌ API collector not available")
            return False

        # Collect a few articles
        articles = collector.collect()
        if not articles:
            print("❌ No articles collected")
            return False

        # Show detailed content of first article
        article = articles[0]
        print(f"\n📰 Article: {article.get('title', 'Unknown Title')}")
        print(f"🔗 URL: {article.get('url', 'No URL')}")
        print(f"📅 Published: {article.get('published_at', 'Unknown')}")
        print(f"🏷️ Category: {article.get('category', 'Unknown')}")
        print(f"📰 Source: {article.get('source', 'Unknown')}")
        print(f"🔍 Source Type: {article.get('source_type', 'Unknown')}")

        print(f"\n📝 Summary/Abstract:")
        summary = article.get("summary", "No summary")
        if summary:
            print(f"   Length: {len(summary)} characters")
            print(f"   Content: {summary[:200]}...")
        else:
            print("   ❌ No summary available")

        print(f"\n📄 Content:")
        content = article.get("content", "No content")
        if content:
            print(f"   Length: {len(content)} characters")
            print(f"   Content: {content[:200]}...")
        else:
            print("   ❌ No content available")

        print(f"\n🔧 API Data:")
        api_data = article.get("api_data", {})
        if api_data:
            print(f"   Keys: {list(api_data.keys())}")
            for key, value in list(api_data.items())[:5]:  # Show first 5
                if isinstance(value, str) and len(value) > 100:
                    print(f"   {key}: {value[:100]}...")
                else:
                    print(f"   {key}: {value}")
        else:
            print("   ❌ No API data available")

        return True

    except Exception as e:
        print(f"❌ Error debugging article content: {e}")
        return False


def main():
    """Main debug function."""
    print("🔍 Article Content Debug")
    print("=" * 60)

    debug_article_content()


if __name__ == "__main__":
    main()
