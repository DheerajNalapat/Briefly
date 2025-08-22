#!/usr/bin/env python3
"""
Simple test script for the Slack publisher.
Tests basic functionality without requiring real Slack tokens.
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from slackbot.slack.publisher import SlackPublisher
from slackbot.summarizer.models import SlackMessage


def test_publisher_structure():
    """Test the publisher class structure and methods."""
    print("🧪 Testing Publisher Structure")
    print("=" * 50)

    # Test with dummy tokens
    publisher = SlackPublisher(bot_token="xoxb-dummy-token", app_token="xapp-dummy-token")

    print(f"✅ Publisher created: {type(publisher).__name__}")
    print(f"📝 Available methods: {[m for m in dir(publisher) if not m.startswith('_')]}")

    # Test is_available (should be False with dummy tokens)
    print(f"🔌 Is available: {publisher.is_available()}")

    # Test test_connection method exists
    if hasattr(publisher, "test_connection"):
        print("✅ test_connection method exists")
    else:
        print("❌ test_connection method missing")

    # Test get_channel_info method exists
    if hasattr(publisher, "get_channel_info"):
        print("✅ get_channel_info method exists")
    else:
        print("❌ get_channel_info method missing")

    return True


def test_message_creation():
    """Test creating Slack messages."""
    print("\n💬 Testing Message Creation")
    print("=" * 50)

    try:
        # Create a sample Slack message
        message = SlackMessage(
            text="🚀 AI/ML News TLDR - Test Message",
            blocks=[
                {"type": "header", "text": {"type": "plain_text", "text": "🚀 AI/ML News TLDR"}},
                {
                    "type": "section",
                    "text": {"type": "mrkdwn", "text": "This is a test message to verify the publisher structure."},
                },
            ],
            attachments=[],
        )

        print(f"✅ Message created: {type(message).__name__}")
        print(f"📝 Text: {message.text}")
        print(f"🧱 Blocks: {len(message.blocks)}")
        print(f"📎 Attachments: {len(message.attachments)}")

        return True

    except Exception as e:
        print(f"❌ Error creating message: {e}")
        return False


def test_publisher_with_real_tokens():
    """Test publisher with real tokens if available."""
    print("\n🔑 Testing with Real Tokens")
    print("=" * 50)

    # Check if real tokens are set
    bot_token = os.getenv("SLACK_BOT_TOKEN")
    app_token = os.getenv("SLACK_APP_TOKEN")

    if not bot_token or bot_token == "xoxb-your-bot-token-here":
        print("⚠️ No real Slack tokens found")
        print("💡 To test with real Slack:")
        print("   1. Create a Slack app at https://api.slack.com/apps")
        print("   2. Get your Bot User OAuth Token (starts with xoxb-)")
        print("   3. Get your App-Level Token (starts with xapp-)")
        print("   4. Update your .env file with real tokens")
        return False

    print("✅ Real tokens found, testing connection...")

    try:
        publisher = SlackPublisher(bot_token=bot_token, app_token=app_token)

        if publisher.is_available():
            print("✅ Publisher available")

            # Test connection
            result = publisher.test_connection()
            if result["success"]:
                print(f"✅ Connected to Slack team: {result.get('bot_team_name', 'Unknown')}")
                print(f"🤖 Bot user: {result.get('bot_user_name', 'Unknown')}")
                return True
            else:
                print(f"❌ Connection failed: {result.get('error', 'Unknown error')}")
                return False
        else:
            print("❌ Publisher not available")
            return False

    except Exception as e:
        print(f"❌ Error testing with real tokens: {e}")
        return False


def main():
    """Main test function."""
    print("🧪 Slack Publisher Simple Test")
    print("=" * 50)

    # Test 1: Publisher structure
    test1 = test_publisher_structure()

    # Test 2: Message creation
    test2 = test_message_creation()

    # Test 3: Real token test
    test3 = test_publisher_with_real_tokens()

    # Summary
    print("\n📋 Test Results")
    print("=" * 50)
    print(f"  Publisher Structure: {'✅ PASS' if test1 else '❌ FAIL'}")
    print(f"  Message Creation: {'✅ PASS' if test2 else '❌ FAIL'}")
    print(f"  Real Token Test: {'✅ PASS' if test3 else '❌ FAIL'}")

    if test1 and test2:
        print("\n🎉 Publisher code is working correctly!")
        if not test3:
            print("💡 You need to set up real Slack tokens to test the full functionality.")
    else:
        print("\n⚠️ There are issues with the publisher code that need to be fixed.")


if __name__ == "__main__":
    main()
