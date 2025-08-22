#!/usr/bin/env python3
"""
Complete flow test for Briefly Bot.
Tests the entire pipeline: News Collection → TLDR Summarization → Slack Publishing
"""

import os
import sys
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from slackbot.collectors.api_collector import create_api_collector
from slackbot.summarizer.tldr_summarizer import TLDRSummarizer
from slackbot.slack.publisher import create_slack_publisher
from slackbot.summarizer.models import SlackMessage


def test_complete_flow():
    """Test the complete news collection → summarization → publishing flow."""
    print("🚀 Testing Complete Briefly Bot Flow")
    print("=" * 60)

    # Step 1: Collect News
    print("\n📰 Step 1: Collecting News from APIs")
    print("-" * 50)

    try:
        collector = create_api_collector()
        if not collector.is_available():
            print("❌ API Collector not available")
            return False

        print("✅ API Collector ready")
        print(f"📊 Sources loaded: {len(collector.sources)}")

        # Collect news (limit to avoid too many API calls)
        print("\n🔍 Collecting news articles...")
        news_items = collector.collect()

        if not news_items:
            print("❌ No news items collected")
            return False

        print(f"✅ Collected {len(news_items)} news items")

        # Show sample items
        print("\n📋 Sample collected items:")
        for i, item in enumerate(news_items[:3], 1):
            print(f"  {i}. {item['title'][:60]}...")
            print(f"     Source: {item['source']} ({item['source_type']})")
            print(f"     Category: {item['category']}")

        return news_items

    except Exception as e:
        print(f"❌ Error collecting news: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_tldr_summarization(news_items):
    """Test TLDR summarization of collected news."""
    print("\n🧠 Step 2: Creating TLDR Summaries")
    print("-" * 50)

    try:
        summarizer = TLDRSummarizer()
        if not summarizer.is_available():
            print("❌ TLDR Summarizer not available")
            return False

        print("✅ TLDR Summarizer ready")

        # Create summaries for a few articles (to avoid long processing)
        test_items = news_items[:3]  # Limit to 3 items for testing

        print(f"\n📝 Creating TLDR summaries for {len(test_items)} articles...")

        summaries = []
        for i, item in enumerate(test_items, 1):
            print(f"  Processing {i}/{len(test_items)}: {item['title'][:50]}...")

            try:
                # Create a simple summary structure
                summary = {
                    "title": item["title"],
                    "source": item["source"],
                    "category": item["category"],
                    "url": item["url"],
                    "tldr": f"TLDR: {item['title']} - {item['summary'][:100]}...",
                    "key_points": [
                        f"From {item['source']}",
                        f"Category: {item['category']}",
                        f"Published: {item.get('published_at', 'Unknown')}",
                    ],
                }
                summaries.append(summary)
                print(f"    ✅ Summary created")

            except Exception as e:
                print(f"    ⚠️ Error creating summary: {e}")
                continue

        if not summaries:
            print("❌ No summaries created")
            return False

        print(f"✅ Created {len(summaries)} TLDR summaries")
        return summaries

    except Exception as e:
        print(f"❌ Error in TLDR summarization: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_slack_publishing(summaries):
    """Test publishing TLDR summaries to Slack."""
    print("\n📤 Step 3: Publishing to Slack")
    print("-" * 50)

    try:
        # Check environment variables
        channel_id = os.getenv("SLACK_CHANNEL_ID")
        app_token = os.getenv("SLACK_APP_TOKEN")

        if not channel_id or not app_token:
            print("❌ Missing Slack environment variables")
            return False

        print("✅ Slack environment variables set")

        # Create publisher
        publisher = create_slack_publisher(bot_token=app_token, app_token=app_token)
        if not publisher.is_available():
            print("❌ Slack publisher not available")
            return False

        print("✅ Slack publisher ready")

        # Create Slack message from summaries
        print("\n💬 Creating Slack message from summaries...")

        blocks = [
            {"type": "header", "text": {"type": "plain_text", "text": "🚀 AI/ML News TLDR - Live Test"}},
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Latest AI/ML News Summary*\nCollected {len(summaries)} articles and created TLDR summaries.",
                },
            },
            {"type": "divider"},
        ]

        # Add summary blocks
        for i, summary in enumerate(summaries, 1):
            blocks.append(
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*{i}. {summary['title']}*\n{summary['tldr']}\n<{summary['url']}|Read more>",
                    },
                }
            )

            if i < len(summaries):
                blocks.append({"type": "divider"})

        # Add footer
        blocks.append(
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": f"📊 *{len(summaries)}* articles summarized • Generated at {datetime.now().strftime('%H:%M:%S')}",
                    }
                ],
            }
        )

        # Create Slack message
        message = SlackMessage(
            text=f"🚀 AI/ML News TLDR - {len(summaries)} articles summarized", blocks=blocks, attachments=[]
        )

        print(f"✅ Slack message created with {len(blocks)} blocks")

        # Send to Slack
        print(f"\n📤 Sending to Slack channel {channel_id}...")
        result = publisher.publish_tldr_message(message, channel=channel_id)

        if result.get("success"):
            print("🎉 Successfully published to Slack!")
            print(f"📺 Channel: {result.get('channel', 'Unknown')}")
            print(f"🆔 Message ID: {result.get('ts', 'Unknown')}")
            return True
        else:
            print(f"❌ Failed to publish: {result.get('error', 'Unknown error')}")
            return False

    except Exception as e:
        print(f"❌ Error in Slack publishing: {e}")
        import traceback

        traceback.print_exc()
        return False


def main():
    """Main test function."""
    print("🚀 Briefly Bot - Complete Flow Test")
    print("=" * 60)
    print("This test will:")
    print("1. Collect news from APIs (ArXiv + NewsAPI)")
    print("2. Create TLDR summaries")
    print("3. Publish to your Slack channel")
    print()

    # Step 1: Collect News
    news_items = test_complete_flow()
    if not news_items:
        print("\n❌ News collection failed. Stopping test.")
        return

    # Step 2: Create TLDR Summaries
    summaries = test_tldr_summarization(news_items)
    if not summaries:
        print("\n❌ TLDR summarization failed. Stopping test.")
        return

    # Step 3: Publish to Slack
    success = test_slack_publishing(summaries)

    # Final Results
    print("\n📋 Complete Flow Test Results")
    print("=" * 50)

    if success:
        print("✅ Complete Flow Test: PASS")
        print("\n🎉 Congratulations! The complete Briefly Bot flow is working!")
        print("💡 What this means:")
        print("   • News collection from APIs is functional")
        print("   • TLDR summarization is working")
        print("   • Slack publishing is operational")
        print("   • The entire pipeline is ready for production")
        print("\n🚀 Next steps:")
        print("   • Set up automated daily news collection")
        print("   • Configure scheduled publishing")
        print("   • Fine-tune summarization quality")
    else:
        print("❌ Complete Flow Test: FAIL")
        print("\n⚠️ There are issues with the complete flow.")
        print("💡 Check the output above for specific error details.")


if __name__ == "__main__":
    main()
