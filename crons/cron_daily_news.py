#!/usr/bin/env python3
"""
Briefly Bot - Cron Job Runner

This script is designed to be run by cron for daily news processing.
It runs the complete Briefly Bot flow and handles logging appropriately.
"""

import os
import sys
import logging
from datetime import datetime
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import Briefly Bot processor
from slackbot.processors import BrieflyNewsProcessor


# Set up logging for cron
def setup_cron_logging():
    """Set up logging specifically for cron execution."""
    # Create logs directory if it doesn't exist
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)

    # Create a specific log file for cron jobs
    log_file = logs_dir / f'briefly_cron_{datetime.now().strftime("%Y%m%d")}.log'

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout),  # Also log to stdout for cron
        ],
    )

    # Set specific logger levels
    logging.getLogger("arxiv").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)

    return logging.getLogger(__name__)


def run_daily_news():
    """Run the daily news processing."""
    logger = setup_cron_logging()

    try:
        logger.info("🚀 Starting Daily Briefly Bot - Cron Job")
        logger.info("=" * 60)
        logger.info("📅 Started at: %s", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        logger.info("🕐 Scheduled time: 8:30 AM")
        logger.info("=" * 60)

        # Check required environment variables
        required_env_vars = ["NEWSAPI_KEY", "SLACK_BOT_TOKEN", "SLACK_CHANNEL_ID"]
        missing_vars = [var for var in required_env_vars if not os.getenv(var)]

        if missing_vars:
            logger.error("❌ Missing required environment variables: %s", ", ".join(missing_vars))
            logger.error("❌ Cron job failed due to missing environment variables")
            return 1

        logger.info("✅ All required environment variables are set")

        # Create and run the news processor
        logger.info("🔧 Initializing Briefly News Processor...")
        processor = BrieflyNewsProcessor(llm_provider="openai")

        # Run the complete news processing flow
        logger.info("🔄 Starting daily news processing...")
        result = processor.process_news_flow(
            max_articles=20,  # Default number of articles for daily digest
            channel=os.getenv("SLACK_CHANNEL_ID"),
            dry_run=False,  # Always publish for cron jobs
        )

        if result["success"]:
            logger.info("🎉 Daily Briefly Bot completed successfully!")
            logger.info("📊 Summary:")
            logger.info("  • Articles collected: %s", result.get("articles_count", 0))
            logger.info("  • TLDR summaries created: %s", result.get("summaries_count", 0))
            logger.info("  • Published to Slack: %s", result.get("channel", "Unknown"))
            logger.info("✅ Cron job completed successfully")
            return 0
        else:
            logger.error("❌ Daily Briefly Bot failed: %s", result.get("error", "Unknown error"))
            logger.error("❌ Cron job failed")
            return 1

    except Exception as e:
        logger.error("❌ Unexpected error in cron job: %s", e)
        import traceback

        traceback.print_exc()
        logger.error("❌ Cron job failed with exception")
        return 1


if __name__ == "__main__":
    exit_code = run_daily_news()
    sys.exit(exit_code)
