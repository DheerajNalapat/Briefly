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

# Import Briefly Bot services
from slackbot.processors import BrieflyNewsProcessor


def setup_logging(verbose: bool = False) -> None:
    """Set up logging configuration."""
    log_level = logging.DEBUG if verbose else logging.INFO

    # Create logs directory if it doesn't exist
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)

    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(logs_dir / f'briefly_bot_{datetime.now().strftime("%Y%m%d")}.log'),
        ],
    )

    # Set specific logger levels
    logging.getLogger("arxiv").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)

    logger = logging.getLogger(__name__)
    logger.info("Briefly Bot logging initialized")


def run_briefly_bot(
    dry_run: bool = False, max_articles: int = 20, channel: Optional[str] = None, llm_provider: str = "openai"
) -> bool:
    """
    Run the complete Briefly Bot flow using the BrieflyNewsProcessor.

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
        # Create and run the news processor
        processor = BrieflyNewsProcessor(llm_provider=llm_provider)

        result = processor.process_news_flow(max_articles=max_articles, channel=channel, dry_run=dry_run)

        if result["success"]:
            logger.info("✅ Briefly Bot completed successfully")
            return True
        else:
            logger.error("❌ Briefly Bot failed: %s", result.get("error", "Unknown error"))
            return False

    except Exception as e:
        logger.error("❌ Unexpected error in Briefly Bot: %s", e)
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
    logger.info("📅 Started at: %s", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    logger.info("🔧 Dry run: %s", "Yes" if args.dry_run else "No")
    logger.info("📊 Max articles: %s", args.max_articles)
    logger.info("🧠 LLM Provider: %s", args.llm_provider)
    logger.info("📺 Target channel: %s", args.channel or os.getenv("SLACK_CHANNEL_ID", "Not specified"))
    logger.info("=" * 50)

    # Check environment variables
    required_env_vars = ["NEWSAPI_KEY"]
    missing_vars = [var for var in required_env_vars if not os.getenv(var)]

    if missing_vars:
        logger.error("❌ Missing required environment variables: %s", ", ".join(missing_vars))
        return 1

    # Check Slack variables for non-dry-run
    slack_vars = ["SLACK_BOT_TOKEN", "SLACK_APP_TOKEN", "SLACK_CHANNEL_ID"]
    missing_slack_vars = [var for var in slack_vars if not os.getenv(var)]

    if missing_slack_vars and not args.dry_run:
        logger.error("❌ Cannot run without Slack environment variables: %s", ", ".join(missing_slack_vars))
        return 1
    elif missing_slack_vars and args.dry_run:
        logger.warning(
            "⚠️ Missing Slack environment variables: %s - dry run will test collection and summarization only",
            ", ".join(missing_slack_vars),
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
