#!/usr/bin/env python3
"""
Test script for LLM-generated article categories.

This script tests the new category generation feature where the LLM
categorizes articles using predefined categories from an enum.
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


def test_llm_categories():
    """Test LLM-generated categories for articles."""
    try:
        from slackbot.services.aggregation_service import AggregationService
        from slackbot.services.summarizer_service import ContentProcessingService

        logger.info("🧪 Testing LLM-Generated Categories")
        logger.info("=" * 50)

        # Initialize services
        aggregation_service = AggregationService()
        content_processing_service = ContentProcessingService()

        # Collect a few articles
        logger.info("📰 Collecting test articles...")
        articles = aggregation_service.collect_prioritized(max_articles=3)

        if not articles:
            logger.warning("⚠️ No articles collected for testing")
            return

        logger.info(f"✅ Collected {len(articles)} articles")

        # Create summaries with LLM-generated categories
        logger.info("🧠 Creating summaries with LLM-generated categories...")
        summaries = content_processing_service.summarize_with_strategy(articles=articles, strategy="individual")

        if not summaries:
            logger.warning("⚠️ No summaries created")
            return

        logger.info(f"✅ Created {len(summaries)} summaries")

        # Display results
        logger.info("\n📊 Category Analysis:")
        logger.info("-" * 30)

        for i, (article, summary) in enumerate(zip(articles, summaries), 1):
            if summary is None:
                logger.warning(f"  {i}. Summary is None, skipping")
                continue

            title = article.get("title", "Unknown Title")[:60]
            original_category = article.get("category", "Unknown")
            llm_category = summary.categories[0] if summary.categories else "Unknown"

            logger.info(f"  {i}. {title}...")
            logger.info(f"     Original Category: {original_category}")
            logger.info(f"     LLM Category: {llm_category}")
            logger.info(f"     Source: {article.get('source', 'Unknown')}")
            logger.info(f"     Model: {summary.model_used}")
            logger.info("")

        # Test category distribution
        categories = {}
        for summary in summaries:
            if summary and summary.categories:
                category = summary.categories[0]
                categories[category] = categories.get(category, 0) + 1

        logger.info("📈 Category Distribution:")
        for category, count in categories.items():
            logger.info(f"  {category}: {count} articles")

        logger.info(f"\n🎉 LLM category generation test completed!")

    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        raise


def test_category_enum():
    """Test the category enum and helper functions."""
    try:
        from slackbot.summarizer.categories import ArticleCategory, get_category_choices, get_category_descriptions

        logger.info("\n🔧 Testing Category Enum")
        logger.info("=" * 30)

        # Test enum values
        logger.info(f"Total categories: {len(list(ArticleCategory))}")

        # Test some specific categories
        test_categories = [
            ArticleCategory.AI_RESEARCH,
            ArticleCategory.MACHINE_LEARNING,
            ArticleCategory.AI_APPLICATIONS,
            ArticleCategory.AI_ETHICS,
            ArticleCategory.AGENTIC_AI,
        ]

        logger.info("Sample categories:")
        for category in test_categories:
            logger.info(f"  {category.value}")

        # Test descriptions
        descriptions = get_category_descriptions()
        logger.info(f"\nCategory descriptions available: {len(descriptions)}")

        # Test category choices string
        choices = get_category_choices()
        logger.info(f"Category choices string length: {len(choices)} characters")
        logger.info(f"First 200 characters: {choices[:200]}...")

        logger.info("✅ Category enum test completed!")

    except Exception as e:
        logger.error(f"❌ Category enum test failed: {e}")
        raise


if __name__ == "__main__":
    # Load environment variables
    from dotenv import load_dotenv

    load_dotenv()

    # Test category enum
    test_category_enum()

    # Test LLM categories
    test_llm_categories()
