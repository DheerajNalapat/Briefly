#!/usr/bin/env python3
"""
Demo script showing the TLDR structure and Slack message format.
"""

import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from slackbot.collectors.api_collector import create_api_collector
from slackbot.summarizer import create_tldr_summarizer


def main():
    """Demo the TLDR structure."""
    print("🚀 TLDR Structure Demo")
    print("=" * 50)

    # Create summarizer
    summarizer = create_tldr_summarizer()

    # Get real articles from API collector
    collector = create_api_collector()
    if collector.is_available():
        articles = collector.collect()[:3]  # Limit to 3 articles for testing
        print(f"📰 Loaded {len(articles)} real articles from API collector")
    else:
        print("❌ API collector not available, cannot test with real data")
        return

    # Create TLDR digest
    print("\n📊 Creating TLDR Digest...")
    tldr_digest = summarizer.create_tldr_digest(articles)

    # Show TLDR structure
    print("\n🔍 TLDR Structure:")
    print(f"  📝 Text: {tldr_digest.tldr_text[:100]}...")
    print(f"  🎯 Key Points: {len(tldr_digest.key_points)}")
    print(f"  🔥 Trending: {tldr_digest.trending_topics}")
    print(f"  ⚡ Impact: {tldr_digest.impact_level}")
    print(f"  🤖 Model: {tldr_digest.model_used}")

    # Create Slack message
    print("\n💬 Creating Slack Message...")
    slack_msg = summarizer.create_slack_message(tldr_digest)

    # Show Slack structure
    print(f"\n📱 Slack Message Structure:")
    print(f"  📝 Text: {slack_msg.text[:100]}...")
    print(f"  🧱 Blocks: {len(slack_msg.blocks)}")
    print(f"  📎 Attachments: {len(slack_msg.attachments)}")

    if slack_msg.attachments:
        print(f"  🎨 Color: {slack_msg.attachments[0]['color']}")

    print("\n✅ Demo completed!")


if __name__ == "__main__":
    main()
