#!/usr/bin/env python3
"""
Test script for the new prioritized collection method.

This script tests the new collect_prioritized method that prioritizes:
1. NewsAPI articles (70% of total, minimum 5)
2. RSS articles (limited to 5)
3. ArXiv papers (maximum 3)
"""

import sys
import os
import logging
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def test_prioritized_collection():
    """Test the new prioritized collection method."""
    try:
        from slackbot.services.aggregation_service import AggregationService

        logger.info("🧪 Testing Prioritized Collection Method")
        logger.info("=" * 50)

        # Initialize the aggregation service
        aggregation_service = AggregationService()

        # Test with different article limits
        test_limits = [10, 15, 20]

        for max_articles in test_limits:
            logger.info(f"\n📊 Testing with max_articles = {max_articles}")
            logger.info("-" * 30)

            # Collect articles using the new prioritized method
            articles = aggregation_service.collect_prioritized(max_articles=max_articles)

            if not articles:
                logger.warning(f"⚠️ No articles collected for limit {max_articles}")
                continue

            # Analyze the results
            source_counts = {}
            for article in articles:
                source_type = article.get("source_type", "unknown")
                source_counts[source_type] = source_counts.get(source_type, 0) + 1

            logger.info(f"✅ Collected {len(articles)} articles:")
            for source_type, count in source_counts.items():
                percentage = (count / len(articles)) * 100
                logger.info(f"  📰 {source_type}: {count} articles ({percentage:.1f}%)")

            # Verify prioritization rules
            newsapi_count = source_counts.get("newsapi", 0)
            rss_count = source_counts.get("rss", 0)
            arxiv_count = source_counts.get("arxiv", 0)

            # Check NewsAPI gets most articles (70% or at least 5)
            expected_newsapi_min = max(5, int(max_articles * 0.7))
            if newsapi_count >= expected_newsapi_min:
                logger.info(f"✅ NewsAPI priority: {newsapi_count} >= {expected_newsapi_min} (expected minimum)")
            else:
                logger.warning(f"⚠️ NewsAPI priority: {newsapi_count} < {expected_newsapi_min} (expected minimum)")

            # Check RSS is limited to 5
            if rss_count <= 5:
                logger.info(f"✅ RSS limit: {rss_count} <= 5 (as expected)")
            else:
                logger.warning(f"⚠️ RSS limit: {rss_count} > 5 (unexpected)")

            # Check ArXiv is limited to 3
            if arxiv_count <= 3:
                logger.info(f"✅ ArXiv limit: {arxiv_count} <= 3 (as expected)")
            else:
                logger.warning(f"⚠️ ArXiv limit: {arxiv_count} > 3 (unexpected)")

            # Show sample articles
            logger.info(f"\n📋 Sample articles (first 3):")
            for i, article in enumerate(articles[:3], 1):
                title = article.get("title", "No title")[:60]
                source_type = article.get("source_type", "unknown")
                source = article.get("source", "unknown")
                logger.info(f"  {i}. [{source_type}] {title}... ({source})")

        logger.info(f"\n🎉 Prioritized collection test completed!")

    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        raise


def test_balanced_vs_prioritized():
    """Compare balanced vs prioritized collection methods."""
    try:
        from slackbot.services.aggregation_service import AggregationService

        logger.info("\n🔄 Comparing Balanced vs Prioritized Collection")
        logger.info("=" * 50)

        aggregation_service = AggregationService()
        max_articles = 15

        # Test balanced collection
        logger.info(f"\n📊 Balanced Collection (max_articles = {max_articles})")
        balanced_articles = aggregation_service.collect_balanced(max_articles=max_articles, balance_sources=True)

        balanced_counts = {}
        for article in balanced_articles:
            source_type = article.get("source_type", "unknown")
            balanced_counts[source_type] = balanced_counts.get(source_type, 0) + 1

        logger.info(f"Balanced results: {len(balanced_articles)} articles")
        for source_type, count in balanced_counts.items():
            percentage = (count / len(balanced_articles)) * 100 if balanced_articles else 0
            logger.info(f"  📰 {source_type}: {count} articles ({percentage:.1f}%)")

        # Test prioritized collection
        logger.info(f"\n📊 Prioritized Collection (max_articles = {max_articles})")
        prioritized_articles = aggregation_service.collect_prioritized(max_articles=max_articles)

        prioritized_counts = {}
        for article in prioritized_articles:
            source_type = article.get("source_type", "unknown")
            prioritized_counts[source_type] = prioritized_counts.get(source_type, 0) + 1

        logger.info(f"Prioritized results: {len(prioritized_articles)} articles")
        for source_type, count in prioritized_counts.items():
            percentage = (count / len(prioritized_articles)) * 100 if prioritized_articles else 0
            logger.info(f"  📰 {source_type}: {count} articles ({percentage:.1f}%)")

        # Compare results
        logger.info(f"\n📈 Comparison Summary:")
        logger.info(f"  Balanced: {len(balanced_articles)} articles")
        logger.info(f"  Prioritized: {len(prioritized_articles)} articles")

        # Check if prioritization rules are followed
        newsapi_prioritized = prioritized_counts.get("newsapi", 0)
        rss_prioritized = prioritized_counts.get("rss", 0)
        arxiv_prioritized = prioritized_counts.get("arxiv", 0)

        logger.info(f"\n✅ Prioritization Rules Check:")
        logger.info(f"  NewsAPI: {newsapi_prioritized} articles (should be highest)")
        logger.info(f"  RSS: {rss_prioritized} articles (should be ≤ 5)")
        logger.info(f"  ArXiv: {arxiv_prioritized} articles (should be ≤ 3)")

    except Exception as e:
        logger.error(f"❌ Comparison test failed: {e}")
        raise


if __name__ == "__main__":
    # Load environment variables
    from dotenv import load_dotenv

    load_dotenv()

    # Test prioritized collection
    test_prioritized_collection()

    # Compare with balanced collection
    test_balanced_vs_prioritized()
