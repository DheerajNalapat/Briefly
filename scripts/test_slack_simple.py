#!/usr/bin/env python3
"""
Simple Slack connectivity test and dummy message publishing.
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


def test_slack_connection():
    """Test basic Slack connectivity."""
    print("🧪 Testing Slack Connection")
    print("=" * 50)

    # Check environment variables
    bot_token = os.getenv("SLACK_BOT_TOKEN")
    app_token = os.getenv("SLACK_APP_TOKEN")
    channel_id = os.getenv("SLACK_CHANNEL_ID")

    print(f"🔑 Bot Token: {'✅ Set' if bot_token and bot_token != 'xoxb-your-bot-token-here' else '❌ Not set'}")
    print(f"🔑 App Token: {'✅ Set' if app_token and app_token != 'xapp-your-app-token-here' else '❌ Not set'}")
    print(f"📺 Channel ID: {'✅ Set' if channel_id else '❌ Not set'}")

    if not bot_token or not app_token:
        print("\n❌ Missing Slack tokens. Cannot test connection.")
        return False

    try:
        from slackbot.slack.publisher import SlackPublisher

        print("\n🔌 Creating Slack publisher...")
        publisher = SlackPublisher(bot_token=bot_token, app_token=app_token)

        print("✅ Publisher created successfully")

        # Test connection
        print("\n🔍 Testing connection...")
        result = publisher.test_connection()

        if result.get("success"):
            print(f"✅ Connected to Slack team: {result.get('bot_team_name', 'Unknown')}")
            print(f"🤖 Bot user: {result.get('bot_user_name', 'Unknown')}")
            return True
        else:
            print(f"❌ Connection failed: {result.get('error', 'Unknown error')}")
            return False

    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_dummy_message():
    """Test publishing a dummy message."""
    print("\n💬 Testing Dummy Message Publishing")
    print("=" * 50)

    bot_token = os.getenv("SLACK_BOT_TOKEN")
    app_token = os.getenv("SLACK_APP_TOKEN")
    channel_id = os.getenv("SLACK_CHANNEL_ID")

    if not all([bot_token, app_token, channel_id]):
        print("❌ Missing required tokens or channel ID")
        return False

    try:
        from slackbot.slack.publisher import SlackPublisher
        from slackbot.summarizer.models import SlackMessage

        publisher = SlackPublisher(bot_token=bot_token, app_token=app_token)

        # Create a simple dummy message using SlackMessage model
        dummy_message = SlackMessage(
            text="🧪 Test message from Briefly Bot",
            blocks=[
                {"type": "header", "text": {"type": "plain_text", "text": "🧪 Test Message"}},
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "This is a test message to verify Slack publishing is working correctly.",
                    },
                },
                {"type": "context", "elements": [{"type": "mrkdwn", "text": "Sent by Briefly Bot test script"}]},
            ],
            attachments=[],
        )

        print("📝 Publishing dummy message...")
        result = publisher.publish_tldr_message(dummy_message, channel=channel_id)

        if result.get("success"):
            print("✅ Message published successfully!")
            print(f"📱 Message ID: {result.get('message_id', 'Unknown')}")
            print(f"📺 Channel: {result.get('channel', 'Unknown')}")
            print(f"⏰ Timestamp: {result.get('ts', 'Unknown')}")
            return True
        else:
            print(f"❌ Failed to publish: {result.get('error', 'Unknown error')}")
            if result.get("slack_error"):
                print(f"🔍 Slack error details: {result.get('slack_error')}")
            return False

    except Exception as e:
        print(f"❌ Error publishing message: {e}")
        return False


def main():
    """Main test function."""
    print("🧪 Slack Simple Test")
    print("=" * 50)

    # Test 1: Connection
    connection_ok = test_slack_connection()

    if connection_ok:
        # Test 2: Dummy message
        message_ok = test_dummy_message()

        print("\n📋 Test Results")
        print("=" * 50)
        print(f"  Connection: ✅ PASS")
        print(f"  Message Publishing: {'✅ PASS' if message_ok else '❌ FAIL'}")

        if message_ok:
            print("\n🎉 Slack integration is working perfectly!")
        else:
            print("\n⚠️ Connection works but message publishing failed.")
    else:
        print("\n❌ Cannot connect to Slack. Check your tokens and app configuration.")
        print("\n💡 Common issues:")
        print("   1. Invalid or expired tokens")
        print("   2. Missing app scopes (chat:write, chat:write.public)")
        print("   3. App not installed to workspace")
        print("   4. Bot not added to channel")


if __name__ == "__main__":
    main()
