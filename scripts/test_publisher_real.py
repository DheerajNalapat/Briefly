#!/usr/bin/env python3
"""
Test script for the Slack publisher with real tokens.
Sends a simple dummy message to test the connection.
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from slackbot.slack.publisher import SlackPublisher
from slackbot.summarizer.models import SlackMessage


def test_real_publisher():
    """Test the publisher with real Slack tokens."""
    print("🧪 Testing Publisher with Real Slack Tokens")
    print("=" * 60)

    # Check environment variables
    channel_id = os.getenv("SLACK_CHANNEL_ID")
    app_token = os.getenv("SLACK_APP_TOKEN")

    print("🔍 Environment Check:")
    print(f"  SLACK_CHANNEL_ID: {'✅ Set' if channel_id else '❌ Not set'}")
    print(f"  SLACK_APP_TOKEN: {'✅ Set' if app_token else '❌ Not set'}")

    if not channel_id or not app_token:
        print("\n❌ Missing required environment variables!")
        print("💡 Please set both SLACK_CHANNEL_ID and SLACK_APP_TOKEN")
        return False

    print(f"\n📺 Target Channel ID: {channel_id}")
    print(f"🔑 App Token: {app_token[:10]}...")

    try:
        # Create publisher with real tokens
        print("\n🚀 Creating Slack Publisher...")
        publisher = SlackPublisher(bot_token=app_token, app_token=app_token)  # Using app token as bot token for testing

        if not publisher.is_available():
            print("❌ Publisher not available")
            return False

        print("✅ Publisher created successfully")

        # Test connection
        print("\n🔌 Testing Slack Connection...")
        connection_result = publisher.test_connection()

        if connection_result["success"]:
            print(f"✅ Connected to Slack!")
            print(f"🤖 Bot User: {connection_result.get('bot_user_name', 'Unknown')}")
            print(f"🏢 Team: {connection_result.get('bot_team_name', 'Unknown')}")
        else:
            print(f"⚠️ Connection test failed: {connection_result.get('error', 'Unknown error')}")
            print("💡 This might be expected if using app token instead of bot token")

        # Create a simple dummy message
        print("\n💬 Creating Dummy Message...")
        dummy_message = SlackMessage(
            text="🧪 Test message from Briefly Bot - Publisher Test",
            blocks=[
                {"type": "header", "text": {"type": "plain_text", "text": "🧪 Briefly Bot Test"}},
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "This is a test message to verify the Slack publisher is working correctly! 🎉",
                    },
                },
                {
                    "type": "section",
                    "fields": [
                        {"type": "mrkdwn", "text": "*Test Type:* Publisher Functionality"},
                        {"type": "mrkdwn", "text": "*Status:* Running Tests"},
                        {"type": "mrkdwn", "text": "*Time:* " + str(Path(__file__).parent.parent.name)},
                        {"type": "mrkdwn", "text": "*Version:* 1.0.0"},
                    ],
                },
                {"type": "divider"},
                {
                    "type": "context",
                    "elements": [{"type": "mrkdwn", "text": "✅ Publisher test completed successfully!"}],
                },
            ],
            attachments=[],
        )

        print(f"✅ Message created with {len(dummy_message.blocks)} blocks")

        # Send the message
        print(f"\n📤 Sending message to channel {channel_id}...")

        # Try to send to the specific channel ID
        result = publisher.publish_tldr_message(slack_message=dummy_message, channel=channel_id)

        if result.get("success"):
            print("🎉 Message sent successfully!")
            print(f"📺 Channel: {result.get('channel', 'Unknown')}")
            print(f"🆔 Message ID: {result.get('ts', 'Unknown')}")
            print(f"📝 Response: {result.get('response', {}).get('ok', 'Unknown')}")
            return True
        else:
            print(f"❌ Failed to send message: {result.get('error', 'Unknown error')}")

            # Try alternative approach - send to default channel
            print("\n🔄 Trying alternative approach...")
            alt_result = publisher.publish_tldr_message(dummy_message)

            if alt_result.get("success"):
                print("✅ Message sent to default channel!")
                return True
            else:
                print(f"❌ Alternative approach also failed: {alt_result.get('error', 'Unknown error')}")
                return False

    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback

        traceback.print_exc()
        return False


def main():
    """Main test function."""
    print("🚀 Briefly Bot - Slack Publisher Real Test")
    print("=" * 60)
    print()

    # Run the real test
    success = test_real_publisher()

    # Summary
    print("\n📋 Test Results")
    print("=" * 50)

    if success:
        print("✅ Publisher Test: PASS")
        print("\n🎉 Congratulations! The Slack publisher is working correctly!")
        print("💡 You can now:")
        print("   1. Send real TLDR summaries to Slack")
        print("   2. Integrate with the news collector")
        print("   3. Set up automated daily news digests")
    else:
        print("❌ Publisher Test: FAIL")
        print("\n⚠️ There are issues with the Slack publisher.")
        print("💡 Common solutions:")
        print("   1. Check your Slack app permissions")
        print("   2. Ensure the bot is added to the target channel")
        print("   3. Verify your tokens are correct")
        print("   4. Check if the channel ID is valid")


if __name__ == "__main__":
    main()
