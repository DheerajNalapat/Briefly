#!/usr/bin/env python3
"""
Test script to analyze article distribution across different sources.

This script tests the prioritized collection method and shows the exact
breakdown of articles from NewsAPI, RSS, and ArXiv sources.
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


def test_source_distribution():
    """Test article distribution across different sources."""
    try:
        from slackbot.services.aggregation_service import AggregationService

        logger.info("📊 Testing Source Distribution Analysis")
        logger.info("=" * 50)

        # Initialize the aggregation service
        aggregation_service = AggregationService()

        # Test with different article limits to see source distribution
        test_limits = [5, 10, 15, 20, 25]

        for max_articles in test_limits:
            logger.info(f"\n🔍 Testing with max_articles = {max_articles}")
            logger.info("-" * 40)

            # Collect articles using the prioritized method
            articles = aggregation_service.collect_prioritized(max_articles=max_articles)

            if not articles:
                logger.warning(f"⚠️ No articles collected for limit {max_articles}")
                continue

            # Analyze source distribution
            source_counts = {}
            source_types = {}

            for article in articles:
                source_type = article.get("source_type", "unknown")
                source_name = article.get("source", "Unknown")

                source_counts[source_type] = source_counts.get(source_type, 0) + 1

                if source_type not in source_types:
                    source_types[source_type] = set()
                source_types[source_type].add(source_name)

            logger.info(f"✅ Collected {len(articles)} articles:")

            # Show detailed breakdown
            for source_type, count in source_counts.items():
                percentage = (count / len(articles)) * 100
                sources = list(source_types[source_type])
                logger.info(f"  📰 {source_type.upper()}: {count} articles ({percentage:.1f}%)")
                logger.info(f"     Sources: {', '.join(sources[:3])}{'...' if len(sources) > 3 else ''}")

            # Show sample articles from each source
            logger.info(f"\n📋 Sample articles by source:")
            for source_type in source_counts.keys():
                source_articles = [a for a in articles if a.get("source_type") == source_type]
                logger.info(f"  {source_type.upper()}:")
                for i, article in enumerate(source_articles[:2], 1):  # Show first 2 from each source
                    title = article.get("title", "Unknown Title")[:50]
                    logger.info(f"    {i}. {title}...")

        logger.info(f"\n🎉 Source distribution analysis completed!")

    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        raise


def test_balanced_vs_prioritized_distribution():
    """Compare balanced vs prioritized collection source distribution."""
    try:
        from slackbot.services.aggregation_service import AggregationService

        logger.info("\n🔄 Comparing Balanced vs Prioritized Source Distribution")
        logger.info("=" * 60)

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
        logger.info(f"\n📈 Distribution Comparison:")
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


def test_individual_collectors():
    """Test each collector individually to see their capacity."""
    try:
        from slackbot.services.aggregation_service import AggregationService

        logger.info("\n🔧 Testing Individual Collectors")
        logger.info("=" * 40)

        aggregation_service = AggregationService()

        # Test NewsAPI collector
        logger.info("\n📰 Testing NewsAPI Collector:")
        newsapi_articles = aggregation_service.collect_from_source("newsapi", max_articles=10, force=True)
        logger.info(f"  NewsAPI: {len(newsapi_articles)} articles")

        # Test RSS collector
        logger.info("\n📡 Testing RSS Collector:")
        rss_articles = aggregation_service.collect_from_source("rss", max_articles=10, force=True)
        logger.info(f"  RSS: {len(rss_articles)} articles")

        # Test ArXiv collector
        logger.info("\n📚 Testing ArXiv Collector:")
        arxiv_articles = aggregation_service.collect_from_source("arxiv", max_articles=10, force=True)
        logger.info(f"  ArXiv: {len(arxiv_articles)} articles")

        logger.info(f"\n✅ Individual collector test completed!")

    except Exception as e:
        logger.error(f"❌ Individual collector test failed: {e}")
        raise


if __name__ == "__main__":
    # Load environment variables
    from dotenv import load_dotenv

    load_dotenv()

    # Test source distribution
    test_source_distribution()

    # Compare balanced vs prioritized
    test_balanced_vs_prioritized_distribution()

    # Test individual collectors
    test_individual_collectors()
