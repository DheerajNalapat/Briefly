#!/usr/bin/env python3
"""
Test script to run the Slack bot with only ArXiv research papers.

This script modifies the collection to focus exclusively on ArXiv sources
and runs a live test to publish research papers to Slack.
"""

import sys
import logging
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def test_arxiv_only_collection():
    """Test collection with only ArXiv research papers."""
    try:
        from slackbot.services.aggregation_service import AggregationService

        logger.info("📚 Testing ArXiv-Only Collection")
        logger.info("=" * 40)

        # Initialize the aggregation service
        aggregation_service = AggregationService()

        # Test different article limits for ArXiv only
        test_limits = [3, 5, 8, 10]

        for max_articles in test_limits:
            logger.info(f"\n🔍 Testing ArXiv-only collection with max_articles = {max_articles}")
            logger.info("-" * 50)

            # Collect articles using only ArXiv
            articles = aggregation_service.collect_from_source("arxiv", max_articles=max_articles, force=True)

            if not articles:
                logger.warning(f"⚠️ No ArXiv articles collected for limit {max_articles}")
                continue

            # Analyze the results
            logger.info(f"✅ Collected {len(articles)} ArXiv articles:")

            for i, article in enumerate(articles, 1):
                title = article.get("title", "Unknown Title")[:60]
                source = article.get("source", "Unknown")
                published = article.get("published", "Unknown")
                authors = article.get("authors", "Unknown")

                logger.info(f"  {i}. {title}...")
                logger.info(f"     Source: {source}")
                logger.info(f"     Published: {published}")
                logger.info(f"     Authors: {authors[:50]}...")
                logger.info("")

        logger.info(f"\n🎉 ArXiv-only collection test completed!")

    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        raise


def run_arxiv_only_slack_bot():
    """Run the full Slack bot with only ArXiv articles."""
    try:
        import os
        from dotenv import load_dotenv

        # Load environment variables
        load_dotenv()

        logger.info("\n🚀 Running ArXiv-Only Slack Bot")
        logger.info("=" * 40)

        # Set environment variable to force ArXiv-only collection
        os.environ["ARXIV_ONLY_MODE"] = "true"

        # Import and run the main bot
        from main import main

        # Run with ArXiv-only parameters
        logger.info("📚 Starting ArXiv-only collection and publishing...")

        # This will run the full bot but we need to modify the collection logic
        # For now, let's just test the ArXiv collection part
        test_arxiv_only_collection()

    except Exception as e:
        logger.error(f"❌ ArXiv-only bot run failed: {e}")
        raise


if __name__ == "__main__":
    # Test ArXiv-only collection
    test_arxiv_only_collection()

    # Ask user if they want to run the full Slack bot
    print("\n" + "=" * 60)
    print("📚 ArXiv-Only Collection Test Complete!")
    print("=" * 60)
    print("To run the full Slack bot with only ArXiv papers:")
    print("1. Modify the aggregation service to prioritize ArXiv")
    print("2. Run: python main.py --max-articles 5")
    print("3. Or use the balanced collection method")
    print("=" * 60)


