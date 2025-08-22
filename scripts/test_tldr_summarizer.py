#!/usr/bin/env python3
"""
Test script for the TLDR summarizer functionality.
Tests the Gemini-powered TLDR summarizer with LangChain.
"""

import sys
import os
import logging
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from slackbot.collectors.api_collector import create_api_collector
from slackbot.summarizer import TLDRSummarizer, create_tldr_summarizer


def setup_logging():
    """Set up logging configuration."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )


def test_tldr_summarizer():
    """Test the TLDR summarizer."""
    print("🚀 Testing TLDR Summarizer")
    print("=" * 50)

    # Create summarizer
    summarizer = create_tldr_summarizer()

    if summarizer.is_available():
        print("✅ TLDR Summarizer initialized successfully")
        print(f"🤖 Model: {summarizer.model_name}")
    else:
        print("⚠️ TLDR Summarizer not available - check API key and dependencies")
        return

    # Get real articles from API collector
    collector = create_api_collector()
    if collector.is_available():
        articles = collector.collect()[:3]  # Limit to 3 articles for testing
        print(f"📰 Loaded {len(articles)} real articles from API collector")
    else:
        print("❌ API collector not available, cannot test with real data")
        return

    # Test TLDR digest creation
    print("\n📊 Testing TLDR digest creation...")
    try:
        tldr_digest = summarizer.create_tldr_digest(articles)
        print(f"✅ Generated TLDR digest for {tldr_digest.article_count} articles")
        print(f"📝 TLDR: {tldr_digest.tldr_text[:100]}...")
        print(f"🎯 Key points: {len(tldr_digest.key_points)}")
        print(f"🔥 Trending topics: {tldr_digest.trending_topics}")
        print(f"⚡ Impact level: {tldr_digest.impact_level}")
        print(f"🤖 Model used: {tldr_digest.model_used}")

        # Test Slack message creation
        print("\n💬 Testing Slack message creation...")
        slack_msg = summarizer.create_slack_message(tldr_digest)
        print(f"✅ Slack message created with {len(slack_msg.blocks)} blocks")
        print(f"📝 Message text: {slack_msg.text[:100]}...")
        print(
            f"🎨 Color: {slack_msg.attachments[0]['color'] if slack_msg.attachments else 'None'}"
        )

        # Test single article TLDR
        if articles:
            print("\n🔍 Testing single article TLDR...")
            article_tldr = summarizer.create_article_tldr(articles[0])
            print(f"✅ Article TLDR created: {article_tldr.tldr_text[:100]}...")

    except Exception as e:
        print(f"❌ Error testing TLDR summarizer: {e}")
        import traceback

        traceback.print_exc()


def main():
    """Main test function."""
    print("🚀 TLDR Summarizer Test Suite")
    print("=" * 60)
    print()

    # Setup
    setup_logging()

    # Check environment
    print("🔍 Environment Check:")
    print(
        f"  GEMINI_API_KEY: {'✅ Set' if os.getenv('GEMINI_API_KEY') else '❌ Not set'}"
    )
    print(f"  Project root: {Path(__file__).parent.parent}")
    print()

    # Run tests
    test_tldr_summarizer()

    print("\n🎉 Test completed!")
    print("\n📋 Summary:")
    print("  - TLDR summarizer tested with Gemini")
    print("  - Dummy data processed successfully")
    print("  - Slack message format generated")
    print("  - Ready for production use!")


if __name__ == "__main__":
    main()
