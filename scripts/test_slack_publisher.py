#!/usr/bin/env python3
"""
Test script for the Slack publisher functionality.
Tests publishing TLDR messages to Slack.
"""

import sys
import os
import logging
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from slackbot.slack.publisher import create_slack_publisher
from slackbot.summarizer import create_tldr_summarizer
from slackbot.collectors.api_collector import create_api_collector


def setup_logging():
    """Set up logging configuration."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )


def test_slack_publisher():
    """Test the Slack publisher functionality."""
    print("🚀 Testing Slack Publisher")
    print("=" * 50)

    # Create publisher
    publisher = create_slack_publisher()

    if not publisher.is_available():
        print("⚠️ Slack Publisher not available - check bot token and configuration")
        print("💡 Make sure SLACK_BOT_TOKEN is set in your .env file")
        return False

    print("✅ Slack Publisher initialized successfully")

    # Test connection
    print("\n🔌 Testing Slack connection...")
    test_result = publisher.test_connection()

    if test_result["success"]:
        print(f"✅ Connected to Slack team: {test_result['bot_team_name']}")
        print(f"🤖 Bot user: {test_result['bot_user_name']}")
        print(f"📺 Default channel: {test_result['default_channel']}")
    else:
        print(f"❌ Connection test failed: {test_result['error']}")
        return False

    return True


def test_tldr_message_publishing():
    """Test publishing TLDR messages to Slack."""
    print("\n📤 Testing TLDR Message Publishing")
    print("=" * 50)

    # Create TLDR summarizer and get real data
    summarizer = create_tldr_summarizer()

    # Get real articles from API collector
    collector = create_api_collector()
    if collector.is_available():
        articles = collector.collect()[:3]  # Limit to 3 articles for testing
        print(f"📰 Loaded {len(articles)} real articles from API collector")
    else:
        print("❌ API collector not available, cannot test with real data")
        return False

    if not summarizer.is_available():
        print("⚠️ TLDR Summarizer not available - using fallback mode")

    # Create TLDR digest
    print("📊 Creating TLDR digest...")
    tldr_digest = summarizer.create_tldr_digest(articles)

    # Create Slack message
    print("💬 Creating Slack message...")
    slack_msg = summarizer.create_slack_message(tldr_digest)

    print(f"✅ Created Slack message with {len(slack_msg.blocks)} blocks")

    # Test publishing (without actually sending to Slack)
    print("\n🧪 Testing message structure (dry run)...")

    # Simulate the publish operation
    publisher = create_slack_publisher()

    # Check if we can create the payload
    try:
        payload = {
            "channel": publisher.default_channel,
            "text": slack_msg.text,
            "blocks": slack_msg.blocks,
            "attachments": slack_msg.attachments,
        }

        print("✅ Message payload created successfully")
        print(f"📺 Target channel: {payload['channel']}")
        print(f"📝 Text length: {len(payload['text'])} characters")
        print(f"🧱 Blocks: {len(payload['blocks'])}")
        print(f"📎 Attachments: {len(payload['attachments'])}")

        # Show first block as example
        if payload["blocks"]:
            first_block = payload["blocks"][0]
            print(f"🔍 First block type: {first_block['type']}")
            if "text" in first_block:
                if isinstance(first_block["text"], dict):
                    print(f"   Text: {first_block['text'].get('text', 'N/A')[:50]}...")
                else:
                    print(f"   Text: {first_block['text'][:50]}...")

        return True

    except Exception as e:
        print(f"❌ Error creating message payload: {e}")
        return False


def test_channel_info():
    """Test getting channel information."""
    print("\n📺 Testing Channel Information")
    print("=" * 50)

    publisher = create_slack_publisher()

    if not publisher.is_available():
        print("⚠️ Publisher not available")
        return False

    # Test getting channel info
    try:
        channel_info = publisher.get_channel_info(publisher.default_channel)

        if channel_info["success"]:
            print(f"✅ Channel: {channel_info['channel_name']}")
            print(f"🆔 Channel ID: {channel_info['channel_id']}")
            print(f"👥 Members: {channel_info['member_count']}")
            print(f"📋 Topic: {channel_info['topic'][:50]}...")
            print(f"🎯 Purpose: {channel_info['purpose'][:50]}...")
            return True
        else:
            print(f"❌ Failed to get channel info: {channel_info['error']}")
            return False

    except Exception as e:
        print(f"❌ Error getting channel info: {e}")
        return False


def main():
    """Main test function."""
    print("🚀 Slack Publisher Test Suite")
    print("=" * 60)
    print()

    # Setup
    setup_logging()

    # Check environment
    print("🔍 Environment Check:")
    print(
        f"  SLACK_BOT_TOKEN: {'✅ Set' if os.getenv('SLACK_BOT_TOKEN') else '❌ Not set'}"
    )
    print(
        f"  SLACK_APP_TOKEN: {'✅ Set' if os.getenv('SLACK_APP_TOKEN') else '❌ Not set'}"
    )
    print(
        f"  SLACK_SIGNING_SECRET: {'✅ Set' if os.getenv('SLACK_SIGNING_SECRET') else '❌ Not set'}"
    )
    print(f"  Project root: {Path(__file__).parent.parent}")
    print()

    # Run tests
    tests = [
        ("Slack Publisher Initialization", test_slack_publisher),
        ("TLDR Message Publishing", test_tldr_message_publishing),
        ("Channel Information", test_channel_info),
    ]

    results = {}
    for test_name, test_func in tests:
        try:
            print(f"\n{'='*20} {test_name} {'='*20}")
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results[test_name] = False

    # Summary
    print("\n📋 Test Results Summary")
    print("=" * 50)

    passed = sum(1 for result in results.values() if result)
    total = len(results)

    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {test_name}: {status}")

    print(f"\nOverall: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All tests passed! Slack publisher is ready for use.")
        print("\n💡 Next steps:")
        print("  1. Set up your Slack app with proper permissions")
        print("  2. Configure your bot token and app token")
        print("  3. Test with a real Slack workspace")
    else:
        print("⚠️ Some tests failed. Check the output above for details.")
        print("\n💡 Common issues:")
        print("  1. Missing Slack tokens in .env file")
        print("  2. Invalid bot token or app token")
        print("  3. Bot not added to workspace")
        print("  4. Insufficient bot permissions")


if __name__ == "__main__":
    main()
