#!/usr/bin/env python3
"""
Briefly Bot - Main Application

This is the main entry point for the Briefly Bot application.
It orchestrates the complete flow: News Collection → TLDR Summarization → Slack Publishing

Usage:
    python main.py                    # Run with default settings
    python main.py --dry-run         # Test without publishing to Slack
    python main.py --verbose         # Enable verbose logging
    python main.py --help            # Show help
"""

import os
import sys
import logging
import argparse
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import Briefly Bot components
from slackbot.collectors.api_collector import create_api_collector
from slackbot.summarizer.tldr_summarizer import create_tldr_summarizer
from slackbot.slack.publisher import create_slack_publisher
from slackbot.summarizer.models import SlackMessage


def setup_logging(verbose: bool = False) -> None:
    """Set up logging configuration."""
    log_level = logging.DEBUG if verbose else logging.INFO

    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(f'briefly_bot_{datetime.now().strftime("%Y%m%d")}.log'),
        ],
    )

    # Set specific logger levels
    logging.getLogger("arxiv").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)

    logger = logging.getLogger(__name__)
    logger.info("Briefly Bot logging initialized")


def collect_news(collector, max_articles: int = 20) -> List[Dict[str, Any]]:
    """
    Collect news from configured sources.

    Args:
        collector: API news collector instance
        max_articles: Maximum number of articles to collect

    Returns:
        List of collected news articles
    """
    logger = logging.getLogger(__name__)

    try:
        logger.info("🔍 Starting news collection...")

        if not collector.is_available():
            logger.error("❌ News collector not available")
            return []

        # Collect news articles
        articles = collector.collect()

        if not articles:
            logger.warning("⚠️ No articles collected")
            return []

        # Limit to max_articles with balanced sampling
        if len(articles) > max_articles:
            # Ensure balanced representation of both ArXiv and NewsAPI articles
            arxiv_articles = [article for article in articles if article.get("source_type") == "arxiv"]
            newsapi_articles = [article for article in articles if article.get("source_type") == "newsapi"]

            # Calculate balanced distribution
            arxiv_limit = min(len(arxiv_articles), max_articles // 2)
            newsapi_limit = max_articles - arxiv_limit

            # Take balanced samples
            balanced_articles = arxiv_articles[:arxiv_limit] + newsapi_articles[:newsapi_limit]

            # If we still have room, add remaining articles
            if len(balanced_articles) < max_articles:
                remaining_articles = [article for article in articles if article not in balanced_articles]
                balanced_articles.extend(remaining_articles[: max_articles - len(balanced_articles)])

            articles = balanced_articles
            logger.info(
                f"📊 Limited collection to {len(articles)} articles (balanced: {len([a for a in articles if a.get('source_type') == 'arxiv'])} ArXiv, {len([a for a in articles if a.get('source_type') == 'newsapi'])} NewsAPI)"
            )

        logger.info(f"✅ Successfully collected {len(articles)} articles")

        # Log sample articles
        for i, article in enumerate(articles[:3], 1):
            logger.info(f"  {i}. {article['title'][:60]}...")
            logger.info(f"     Source: {article['source']} ({article['source_type']})")
            logger.info(f"     Category: {article['category']}")

        return articles

    except Exception as e:
        logger.error(f"❌ Error during news collection: {e}")
        return []


def create_tldr_summaries(summarizer, articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Create TLDR summaries for collected articles.

    Args:
        summarizer: TLDR summarizer instance
        articles: List of news articles

    Returns:
        List of TLDR summaries
    """
    logger = logging.getLogger(__name__)

    try:
        logger.info("🧠 Starting TLDR summarization...")

        if not summarizer.is_available():
            logger.warning("⚠️ TLDR summarizer not available - using fallback mode")

        summaries = []
        total_articles = len(articles)

        for i, article in enumerate(articles, 1):
            try:
                logger.info(f"  Processing {i}/{total_articles}: {article['title'][:50]}...")

                # Create TLDR summary for the article
                article_tldr = summarizer.create_article_tldr(article)

                # Convert to summary dict
                summary = {
                    "title": article["title"],
                    "source": article["source"],
                    "category": article["category"],
                    "url": article["url"],
                    "tldr": article_tldr.tldr_text,
                    "key_points": article_tldr.key_points,
                    "impact_level": article_tldr.impact_level,
                    "reading_time": article_tldr.reading_time,
                    "model_used": article_tldr.model_used,
                }

                summaries.append(summary)
                logger.info(f"    ✅ Summary created using {article_tldr.model_used}")

            except Exception as e:
                logger.warning(f"    ⚠️ Error creating summary for article {i}: {e}")
                continue

        logger.info(f"✅ Successfully created {len(summaries)} TLDR summaries")
        return summaries

    except Exception as e:
        logger.error(f"❌ Error during TLDR summarization: {e}")
        return []


def create_slack_message(summaries: List[Dict[str, Any]]) -> SlackMessage:
    """
    Create a Slack message from TLDR summaries.

    Args:
        summaries: List of TLDR summaries

    Returns:
        Formatted Slack message
    """
    logger = logging.getLogger(__name__)

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

            blocks.append(
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*{i}. {title}*\n{tldr_text}\n<{url}|Read more>",
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

        logger.info(f"✅ Slack message created with {len(blocks)} blocks")
        return message

    except Exception as e:
        logger.error(f"❌ Error creating Slack message: {e}")
        raise


def publish_to_slack(publisher, message: SlackMessage, channel: str) -> bool:
    """
    Publish the Slack message.

    Args:
        publisher: Slack publisher instance
        message: Slack message to publish
        channel: Target Slack channel

    Returns:
        True if successful, False otherwise
    """
    logger = logging.getLogger(__name__)

    try:
        logger.info(f"📤 Publishing to Slack channel {channel}...")

        if not publisher.is_available():
            logger.error("❌ Slack publisher not available")
            return False

        # Publish the message
        result = publisher.publish_tldr_message(message, channel=channel)

        if result.get("success"):
            logger.info("🎉 Successfully published to Slack!")
            logger.info(f"📺 Channel: {channel}")
            logger.info(f"🆔 Message ID: {result.get('message_id', 'Unknown')}")
            return True
        else:
            logger.error(f"❌ Failed to publish: {result.get('error', 'Unknown error')}")
            return False

    except Exception as e:
        logger.error(f"❌ Error publishing to Slack: {e}")
        return False


def run_briefly_bot(
    dry_run: bool = False, max_articles: int = 20, channel: Optional[str] = None, llm_provider: str = "openai"
) -> bool:
    """
    Run the complete Briefly Bot flow.

    Args:
        dry_run: If True, don't publish to Slack
        max_articles: Maximum number of articles to process
        channel: Target Slack channel (uses env var if not specified)
        llm_provider: LLM provider to use ("openai" or "gemini")

    Returns:
        True if successful, False otherwise
    """
    logger = logging.getLogger(__name__)

    try:
        logger.info("🚀 Starting Briefly Bot...")
        logger.info("=" * 60)

        # Step 1: Initialize components
        logger.info("🔧 Initializing components...")

        collector = create_api_collector()
        if not collector.is_available():
            logger.error("❌ Failed to initialize news collector")
            return False

        summarizer = create_tldr_summarizer(llm_provider=llm_provider)
        if not summarizer.is_available():
            logger.warning(f"⚠️ {llm_provider.upper()} TLDR summarizer not available - will use fallback mode")

        publisher = create_slack_publisher()
        if not publisher.is_available():
            if dry_run:
                logger.warning("⚠️ Slack publisher not available - dry run will test collection and summarization only")
            else:
                logger.error("❌ Failed to initialize Slack publisher")
                return False

        logger.info("✅ All components initialized successfully")

        # Step 2: Collect news
        logger.info("\n📰 Step 2: Collecting News")
        logger.info("-" * 40)

        articles = collect_news(collector, max_articles)
        if not articles:
            logger.error("❌ No articles collected - stopping")
            return False

        # Step 3: Create TLDR summaries
        logger.info("\n🧠 Step 3: Creating TLDR Summaries")
        logger.info("-" * 40)

        summaries = create_tldr_summaries(summarizer, articles)
        if not summaries:
            logger.error("❌ No summaries created - stopping")
            return False

        # Step 4: Create Slack message
        logger.info("\n💬 Step 4: Creating Slack Message")
        logger.info("-" * 40)

        message = create_slack_message(summaries)

        # Step 5: Publish to Slack (if not dry run)
        if dry_run:
            logger.info("\n🧪 DRY RUN: Would publish to Slack")
            logger.info(f"📝 Message text: {message.text[:100]}...")
            logger.info(f"🧱 Blocks: {len(message.blocks)}")
            logger.info("✅ Dry run completed successfully")
            return True
        else:
            logger.info("\n📤 Step 5: Publishing to Slack")
            logger.info("-" * 40)

            # Use provided channel or default from env
            target_channel = channel or os.getenv("SLACK_CHANNEL_ID")
            if not target_channel:
                logger.error("❌ No Slack channel specified")
                return False

            success = publish_to_slack(publisher, message, target_channel)

            if success:
                logger.info("\n🎉 Briefly Bot completed successfully!")
                logger.info("📊 Summary:")
                logger.info(f"  • Articles collected: {len(articles)}")
                logger.info(f"  • TLDR summaries created: {len(summaries)}")
                logger.info(f"  • Published to Slack: {target_channel}")
                return True
            else:
                logger.error("❌ Briefly Bot failed during Slack publishing")
                return False

    except Exception as e:
        logger.error(f"❌ Unexpected error in Briefly Bot: {e}")
        import traceback

        traceback.print_exc()
        return False


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Briefly Bot - AI/ML News Aggregator and TLDR Generator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py                    # Run with default settings (OpenAI)
  python main.py --dry-run         # Test without publishing to Slack
  python main.py --verbose         # Enable verbose logging
  python main.py --max-articles 10 # Limit to 10 articles
  python main.py --channel C123456 # Specify Slack channel
  python main.py --llm-provider gemini # Use Gemini instead of OpenAI
        """,
    )

    parser.add_argument("--dry-run", action="store_true", help="Test the flow without publishing to Slack")

    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose logging")

    parser.add_argument(
        "--max-articles", type=int, default=20, help="Maximum number of articles to process (default: 20)"
    )

    parser.add_argument("--channel", type=str, help="Target Slack channel ID (overrides SLACK_CHANNEL_ID env var)")

    parser.add_argument(
        "--llm-provider",
        type=str,
        choices=["openai", "gemini"],
        default="openai",
        help="LLM provider to use for TLDR summarization (default: openai)",
    )

    args = parser.parse_args()

    # Setup logging
    setup_logging(args.verbose)
    logger = logging.getLogger(__name__)

    # Print startup banner
    logger.info("🚀 Briefly Bot - AI/ML News Aggregator")
    logger.info("=" * 50)
    logger.info(f"📅 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"🔧 Dry run: {'Yes' if args.dry_run else 'No'}")
    logger.info(f"📊 Max articles: {args.max_articles}")
    logger.info(f"🧠 LLM Provider: {args.llm_provider}")
    logger.info(f"📺 Target channel: {args.channel or os.getenv('SLACK_CHANNEL_ID', 'Not specified')}")
    logger.info("=" * 50)

    # Check environment variables
    required_env_vars = ["NEWSAPI_KEY"]
    missing_vars = [var for var in required_env_vars if not os.getenv(var)]

    if missing_vars:
        logger.error(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
        return 1

    # Check Slack variables for non-dry-run
    slack_vars = ["SLACK_BOT_TOKEN", "SLACK_APP_TOKEN", "SLACK_CHANNEL_ID"]
    missing_slack_vars = [var for var in slack_vars if not os.getenv(var)]

    if missing_slack_vars and not args.dry_run:
        logger.error(f"❌ Cannot run without Slack environment variables: {', '.join(missing_slack_vars)}")
        return 1
    elif missing_slack_vars and args.dry_run:
        logger.warning(
            f"⚠️ Missing Slack environment variables: {', '.join(missing_slack_vars)} - dry run will test collection and summarization only"
        )

    # Run the bot
    success = run_briefly_bot(
        dry_run=args.dry_run, max_articles=args.max_articles, channel=args.channel, llm_provider=args.llm_provider
    )

    if success:
        logger.info("✅ Briefly Bot completed successfully")
        return 0
    else:
        logger.error("❌ Briefly Bot failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
