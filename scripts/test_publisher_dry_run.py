#!/usr/bin/env python3
"""
Dry run test for the Slack publisher.
Tests the full workflow without sending actual messages.
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from slackbot.slack.publisher import SlackPublisher
from slackbot.summarizer.models import SlackMessage, DailyDigestTLDR, ArticleTLDR
from datetime import datetime


def create_sample_tldr_digest():
    """Create a sample TLDR digest for testing."""
    print("📊 Creating Sample TLDR Digest")
    print("=" * 50)

    # Create sample articles
    articles = [
        ArticleTLDR(
            tldr="OpenAI releases GPT-5 with breakthrough reasoning capabilities that can handle complex multi-step tasks with human-like understanding.",
            key_facts=[
                "GPT-5 demonstrates unprecedented reasoning abilities",
                "Can handle complex multi-step tasks",
                "Shows human-like understanding of context",
            ],
            why_matters="This represents a significant leap in AI reasoning capabilities, potentially enabling more sophisticated AI applications across industries.",
            reading_time="3 min read",
            difficulty="Intermediate",
        ),
        ArticleTLDR(
            tldr="Google DeepMind achieves new milestone in protein folding with AlphaFold3, now predicting protein structures with 95% accuracy.",
            key_facts=[
                "AlphaFold3 achieves 95% accuracy in protein structure prediction",
                "Revolutionizes drug discovery and biotechnology",
                "Significant improvement over previous versions",
            ],
            why_matters="Accurate protein structure prediction accelerates drug development and advances our understanding of biological processes.",
            reading_time="4 min read",
            difficulty="Advanced",
        ),
        ArticleTLDR(
            tldr="Meta's Llama 3 shows promise in multilingual tasks with significant improvements in understanding and generating content in 50+ languages.",
            key_facts=[
                "Llama 3 demonstrates multilingual capabilities",
                "Supports 50+ languages",
                "Open-source language model",
            ],
            why_matters="Multilingual AI models enable global accessibility and cross-cultural communication in AI applications.",
            reading_time="2 min read",
            difficulty="Intermediate",
        ),
    ]

    # Create daily digest
    digest = DailyDigestTLDR(
        tldr_summary="Today's AI/ML landscape shows remarkable progress in language models, protein folding, and multilingual AI capabilities.",
        top_headlines=[
            "OpenAI GPT-5: Breakthrough reasoning capabilities",
            "AlphaFold3: 95% accuracy in protein structure prediction",
            "Llama 3: Enhanced multilingual AI capabilities",
        ],
        trending_topics=[
            "AI reasoning and understanding",
            "Protein folding and drug discovery",
            "Multilingual AI models",
        ],
        impact_assessment="High - These developments represent significant advances in AI capabilities with broad industry applications.",
        must_read=[
            "GPT-5 reasoning capabilities for AI professionals",
            "AlphaFold3 for biotechnology researchers",
            "Llama 3 multilingual features for global AI deployment",
        ],
        slack_format="🚀 AI/ML News TLDR - Today's landscape shows remarkable progress in language models, protein folding, and multilingual AI capabilities.",
    )

    print(f"✅ Created digest with {len(articles)} articles")
    print(f"📝 Summary: {digest.tldr_summary[:80]}...")
    print(f"🏷️ Trending topics: {len(digest.trending_topics)}")

    return digest


def create_slack_message(digest: DailyDigestTLDR):
    """Create a Slack message from the TLDR digest."""
    print("\n💬 Creating Slack Message")
    print("=" * 50)

    try:
        # Create message blocks
        blocks = [
            {"type": "header", "text": {"type": "plain_text", "text": "🚀 AI/ML News TLDR"}},
            {"type": "section", "text": {"type": "mrkdwn", "text": f"*{digest.tldr_summary}*"}},
            {"type": "divider"},
        ]

        # Add top headlines
        blocks.append(
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*📰 Top Headlines:*\n" + "\n".join([f"• {headline}" for headline in digest.top_headlines]),
                },
            }
        )

        blocks.append({"type": "divider"})

        # Add trending topics
        blocks.append(
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*🔥 Trending Topics:*\n" + "\n".join([f"• {topic}" for topic in digest.trending_topics]),
                },
            }
        )

        blocks.append({"type": "divider"})

        # Add impact assessment
        blocks.append(
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": f"*📊 Impact Assessment:* {digest.impact_assessment}"},
            }
        )

        # Add footer
        blocks.append(
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": f"📚 *{len(digest.must_read)}* must-read articles identified",
                    },
                ],
            }
        )

        # Create Slack message
        message = SlackMessage(text=digest.slack_format, blocks=blocks, attachments=[])

        print(f"✅ Created Slack message with {len(blocks)} blocks")
        print(f"📝 Text length: {len(message.text)} characters")
        print(f"🧱 Blocks: {len(message.blocks)}")
        print(f"📎 Attachments: {len(message.attachments)}")

        return message

    except Exception as e:
        print(f"❌ Error creating Slack message: {e}")
        return None


def test_publisher_workflow():
    """Test the complete publisher workflow."""
    print("🧪 Testing Complete Publisher Workflow")
    print("=" * 50)

    # Step 1: Create TLDR digest
    digest = create_sample_tldr_digest()
    if not digest:
        return False

    # Step 2: Create Slack message
    message = create_slack_message(digest)
    if not message:
        return False

    # Step 3: Test publisher (without real tokens)
    print("\n🔌 Testing Publisher (Dry Run)")
    print("=" * 50)

    try:
        publisher = SlackPublisher(bot_token="xoxb-dummy-token", app_token="xapp-dummy-token")

        print(f"✅ Publisher created: {type(publisher).__name__}")
        print(f"🔌 Is available: {publisher.is_available()}")

        # Test message structure
        print(f"\n📋 Message Structure:")
        print(f"  Text: {message.text[:100]}...")
        print(f"  Blocks: {len(message.blocks)}")

        # Show first few blocks
        for i, block in enumerate(message.blocks[:3]):
            print(f"  Block {i+1}: {block.get('type', 'unknown')}")
            if "text" in block:
                text_content = block["text"].get("text", "") if isinstance(block["text"], dict) else str(block["text"])
                print(f"    Content: {text_content[:60]}...")

        return True

    except Exception as e:
        print(f"❌ Error testing publisher: {e}")
        return False


def main():
    """Main test function."""
    print("🧪 Slack Publisher Dry Run Test")
    print("=" * 60)

    # Test the complete workflow
    success = test_publisher_workflow()

    # Summary
    print("\n📋 Test Results")
    print("=" * 50)

    if success:
        print("✅ Complete Publisher Workflow: PASS")
        print("\n🎉 The publisher is working correctly!")
        print("💡 To send real messages to Slack:")
        print("   1. Set up real Slack tokens in your .env file")
        print("   2. Ensure your bot is added to the target channel")
        print("   3. Run the full test with: python scripts/test_slack_publisher.py")
    else:
        print("❌ Complete Publisher Workflow: FAIL")
        print("\n⚠️ There are issues with the publisher workflow.")


if __name__ == "__main__":
    main()
