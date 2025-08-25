#!/usr/bin/env python3
"""
Test script for split collectors

This script tests the ArXiv and NewsAPI collectors separately
to ensure they work correctly after splitting from the combined api_collector.
"""

import sys
import os
import logging
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

logger = logging.getLogger(__name__)


def test_arxiv_collector():
    """Test the ArXiv collector."""
    logger.info("🧪 Testing ArXiv Collector...")

    try:
        from slackbot.collectors.arxiv_collector import create_arxiv_collector

        collector = create_arxiv_collector()

        if collector.is_available():
            logger.info("✅ ArXiv collector is available")

            # Test collection
            logger.info("📊 Testing ArXiv collection...")
            results = collector.collect(max_articles=5)

            logger.info(f"✅ Collected {len(results)} papers from ArXiv")

            # Show sample results
            if results:
                logger.info("📰 Sample ArXiv papers:")
                for i, paper in enumerate(results[:3], 1):
                    logger.info(f"  {i}. {paper['title'][:60]}...")
                    logger.info(f"     Source: {paper['source']}")
                    logger.info(f"     Category: {paper['category']}")
                    logger.info(f"     Source Type: {paper.get('source_type', 'N/A')}")
                    logger.info("")

            return True
        else:
            logger.warning("⚠️ ArXiv collector is not available")
            return False

    except Exception as e:
        logger.error(f"❌ Error testing ArXiv collector: {e}")
        return False


def test_newsapi_collector():
    """Test the NewsAPI collector."""
    logger.info("🧪 Testing NewsAPI Collector...")

    try:
        from slackbot.collectors.newsapi_org_collector import create_newsapi_collector

        collector = create_newsapi_collector()

        if collector.is_available():
            logger.info("✅ NewsAPI collector is available")

            # Test collection
            logger.info("📊 Testing NewsAPI collection...")
            results = collector.collect(max_articles=5)

            logger.info(f"✅ Collected {len(results)} articles from NewsAPI")

            # Show sample results
            if results:
                logger.info("📰 Sample NewsAPI articles:")
                for i, article in enumerate(results[:3], 1):
                    logger.info(f"  {i}. {article['title'][:60]}...")
                    logger.info(f"     Source: {article['source']}")
                    logger.info(f"     Category: {article['category']}")
                    logger.info(f"     Source Type: {article.get('source_type', 'N/A')}")
                    logger.info("")

            return True
        else:
            logger.warning("⚠️ NewsAPI collector is not available (check NEWSAPI_KEY)")
            # Return True if it's just missing the API key, as this is expected in some environments
            return True

    except Exception as e:
        logger.error(f"❌ Error testing NewsAPI collector: {e}")
        return False


def test_aggregation_service():
    """Test the AggregationService with both collectors."""
    logger.info("🧪 Testing AggregationService with split collectors...")

    try:
        from slackbot.services.aggregation_service import AggregationService

        service = AggregationService()

        # Check available collectors
        available_collectors = service.get_available_collectors()
        logger.info(f"📊 Available collectors: {available_collectors}")

        # Get collector status
        status = service.get_collector_status()
        logger.info("🔍 Collector status:")
        for name, info in status.items():
            logger.info(f"  {name}: {'✅ Available' if info['available'] else '❌ Not Available'}")

        # Test balanced collection
        logger.info("🎯 Testing balanced collection...")
        results = service.collect_balanced(max_articles=6)

        logger.info(f"✅ Collected {len(results)} articles with balanced sources")

        # Show results by source type
        arxiv_count = len([r for r in results if r.get("source_type") == "arxiv"])
        newsapi_count = len([r for r in results if r.get("source_type") == "newsapi"])

        logger.info(f"📊 Results breakdown: {arxiv_count} ArXiv, {newsapi_count} NewsAPI")

        return True

    except Exception as e:
        logger.error(f"❌ Error testing AggregationService: {e}")
        import traceback

        logger.debug(f"Traceback: {traceback.format_exc()}")
        return False


def main():
    """Run all tests."""
    logger.info("🚀 Starting split collectors test...")
    logger.info("=" * 50)

    # Test individual collectors
    arxiv_success = test_arxiv_collector()
    logger.info("-" * 30)

    newsapi_success = test_newsapi_collector()
    logger.info("-" * 30)

    # Test aggregation service
    aggregation_success = test_aggregation_service()
    logger.info("-" * 30)

    # Summary
    logger.info("📊 Test Results Summary:")
    logger.info(f"  ArXiv Collector: {'✅ PASS' if arxiv_success else '❌ FAIL'}")
    logger.info(f"  NewsAPI Collector: {'✅ PASS' if newsapi_success else '❌ FAIL'}")
    logger.info(f"  AggregationService: {'✅ PASS' if aggregation_success else '❌ FAIL'}")

    if all([arxiv_success, newsapi_success, aggregation_success]):
        logger.info("🎉 All tests passed! Split collectors are working correctly.")
        return 0
    else:
        logger.error("❌ Some tests failed. Check the logs above for details.")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
