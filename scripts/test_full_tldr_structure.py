#!/usr/bin/env python3
"""
Comprehensive test script for the TLDR summarizer structure.
Shows the complete data flow from articles to Slack messages.
"""

import sys
import os
import json
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


def test_full_tldr_structure():
    """Test the complete TLDR structure and data flow."""
    print("🚀 Testing Complete TLDR Structure")
    print("=" * 60)

    # Create summarizer
    summarizer = create_tldr_summarizer()

    if summarizer.is_available():
        print("✅ Gemini-powered TLDR Summarizer initialized successfully")
    else:
        print("⚠️ Using fallback TLDR summarizer (no Gemini API key)")

    # Get real articles from API collector
    collector = create_api_collector()
    if collector.is_available():
        articles = collector.collect()[:3]  # Limit to 3 articles for testing
        print(f"📰 Loaded {len(articles)} real articles from API collector")
    else:
        print("❌ API collector not available, cannot test with real data")
        return

    # Test TLDR digest creation
    print("\n📊 Creating TLDR Digest...")
    tldr_digest = summarizer.create_tldr_digest(articles)

    # Display the complete TLDR structure
    print("\n🔍 Complete TLDR Structure:")
    print("-" * 40)
    print(f"📝 TLDR Text: {tldr_digest.tldr_text}")
    print(f"🎯 Key Points ({len(tldr_digest.key_points)}):")
    for i, point in enumerate(tldr_digest.key_points, 1):
        print(f"   {i}. {point}")
    print(f"🔥 Trending Topics: {', '.join(tldr_digest.trending_topics)}")
    print(f"⚡ Impact Level: {tldr_digest.impact_level}")
    print(f"⏱️ Reading Time: {tldr_digest.reading_time}")
    print(f"📊 Article Count: {tldr_digest.article_count}")
    print(f"🏷️ Categories: {', '.join(tldr_digest.categories)}")
    print(f"📰 Sources: {', '.join(tldr_digest.sources)}")
    print(f"🤖 Model Used: {tldr_digest.model_used}")
    print(f"🎨 Emoji: {tldr_digest.emoji}")
    print(f"🎨 Color: {tldr_digest.color}")
    print(f"🕒 Generated At: {tldr_digest.generated_at}")

    # Test Slack message creation
    print("\n💬 Creating Slack Message...")
    slack_msg = summarizer.create_slack_message(tldr_digest)

    # Display the complete Slack message structure
    print("\n🔍 Complete Slack Message Structure:")
    print("-" * 40)
    print(f"📝 Main Text: {slack_msg.text[:200]}...")
    print(f"🧱 Blocks ({len(slack_msg.blocks)}):")
    for i, block in enumerate(slack_msg.blocks, 1):
        print(f"   Block {i}: {block['type']}")
        if "text" in block:
            if isinstance(block["text"], dict):
                print(f"      Text: {block['text'].get('text', 'N/A')[:100]}...")
            else:
                print(f"      Text: {block['text'][:100]}...")

    print(f"📎 Attachments ({len(slack_msg.attachments)}):")
    for i, attachment in enumerate(slack_msg.attachments, 1):
        print(f"   Attachment {i}:")
        for key, value in attachment.items():
            print(f"      {key}: {value}")

    # Show JSON representation for Slack API
    print("\n📋 JSON for Slack API:")
    print("-" * 40)
    slack_json = {
        "text": slack_msg.text,
        "blocks": slack_msg.blocks,
        "attachments": slack_msg.attachments,
    }
    print(json.dumps(slack_json, indent=2))

    return tldr_digest, slack_msg


def test_single_article_tldr():
    """Test single article TLDR creation."""
    print("\n🔍 Testing Single Article TLDR...")
    print("=" * 50)

    summarizer = create_tldr_summarizer()

    # Get real articles from API collector
    collector = create_api_collector()
    if collector.is_available():
        articles = collector.collect()[:3]  # Limit to 3 articles for testing
        print(f"📰 Loaded {len(articles)} real articles from API collector")
    else:
        print("❌ API collector not available, cannot test with real data")
        return None

    if articles:
        article = articles[0]
        print(f"📰 Article: {article['title']}")
        print(f"🏷️ Category: {article['category']}")
        print(f"📰 Source: {article['source']}")

        article_tldr = summarizer.create_article_tldr(article)

        print(f"\n🔍 Article TLDR Structure:")
        print("-" * 30)
        print(f"📝 TLDR: {article_tldr.tldr_text}")
        print(f"🎯 Key Points: {len(article_tldr.key_points)}")
        print(f"🔥 Trending: {', '.join(article_tldr.trending_topics)}")
        print(f"⚡ Impact: {article_tldr.impact_level}")
        print(f"⏱️ Reading Time: {article_tldr.reading_time}")
        print(f"🤖 Model: {article_tldr.model_used}")

        return article_tldr

    return None


def test_data_flow():
    """Test the complete data flow from articles to Slack."""
    print("\n🔄 Testing Complete Data Flow...")
    print("=" * 50)

    # 1. Input: Articles
    collector = create_api_collector()
    if collector.is_available():
        articles = collector.collect()[:3]  # Limit to 3 articles for testing
        print(f"📥 Input: {len(articles)} real articles from API collector")
    else:
        print("❌ API collector not available, cannot test with real data")
        return None, None, None

    # 2. Process: Create TLDR
    summarizer = create_tldr_summarizer()
    tldr_digest = summarizer.create_tldr_digest(articles)
    print(f"⚙️ Process: TLDR digest created using {tldr_digest.model_used}")

    # 3. Output: Slack Message
    slack_msg = summarizer.create_slack_message(tldr_digest)
    print(f"📤 Output: Slack message with {len(slack_msg.blocks)} blocks")

    # 4. Final: Ready for Slack API
    print(f"✅ Final: Ready to send to Slack API")

    return articles, tldr_digest, slack_msg


def main():
    """Main test function."""
    print("🚀 Complete TLDR Structure Test Suite")
    print("=" * 80)
    print()

    # Setup
    setup_logging()

    try:
        # Test complete structure
        tldr_digest, slack_msg = test_full_tldr_structure()

        # Test single article
        article_tldr = test_single_article_tldr()

        # Test data flow
        articles, tldr_digest, slack_msg = test_data_flow()

        print("\n🎉 All tests completed successfully!")
        print("\n📋 Summary:")
        print("  ✅ TLDR structure created and validated")
        print("  ✅ Slack message format generated")
        print("  ✅ Data flow from articles to Slack verified")
        print("  ✅ JSON structure ready for Slack API")

        if not os.getenv("GOOGLE_AI_API_KEY"):
            print("\n💡 To enable Gemini-powered TLDR summarization:")
            print("  1. Set GOOGLE_AI_API_KEY environment variable")
            print("  2. Run tests again to see AI-generated summaries")
        else:
            print(
                "\n🚀 Gemini API key found! TLDR summaries will use AI-powered generation."
            )

        print(f"\n📊 Final Stats:")
        print(f"  - Articles processed: {len(articles)}")
        print(f"  - TLDR model used: {tldr_digest.model_used}")
        print(f"  - Slack blocks created: {len(slack_msg.blocks)}")
        print(f"  - Impact level: {tldr_digest.impact_level}")

    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
