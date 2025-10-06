"""
Utility functions for creating Slack messages.
"""

import logging
from typing import List, Dict, Any
from datetime import datetime

from slackbot.summarizer.models import SlackMessage

logger = logging.getLogger(__name__)


def create_slack_message(summaries: List[Dict[str, Any]]) -> SlackMessage:
    """
    Create a Slack message from TLDR summaries.

    Args:
        summaries: List of TLDR summaries

    Returns:
        Formatted Slack message
    """
    try:
        logger.info("💬 Creating Slack message...")

        # Create message blocks
        blocks = [
            {"type": "header", "text": {"type": "plain_text", "text": "🚀 AI/ML News TLDR - Daily Digest"}},
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Today's AI/ML News Summary*\nCollected {len(summaries)} articles and created TLDR summaries.",
                },
            },
            {"type": "divider"},
        ]

        # Add summary blocks
        for i, summary in enumerate(summaries, 1):
            # Access dictionary keys directly
            title = summary.get("title", "Unknown Title")
            tldr_text = summary.get("tldr", "No summary available")
            url = summary.get("url", "#")
            source = summary.get("source", "Unknown Source")
            category = summary.get("category", "Unknown Category")

            blocks.append(
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*{i}. {title}*\n{tldr_text}\n\n📰 *Source:* {source} | 🏷️ *Category:* {category}\n<{url}|Read more>",
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

        logger.info("✅ Slack message created with %s blocks", len(blocks))
        return message

    except Exception as e:
        logger.error("❌ Error creating Slack message: %s", e)
        raise
