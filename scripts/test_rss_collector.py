#!/usr/bin/env python3
"""
Test script for the new RSS collector

This script tests the RSSCollector to ensure it properly
collects articles from RSS feeds with AI/ML focus.
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


def test_rss_collector():
    """Test the RSSCollector functionality."""
    logger.info("🧪 Testing RSS Collector...")

    try:
        from slackbot.collectors.rss_collector import create_rss_collector

        # Create collector
        collector = create_rss_collector()

        if not collector.is_available():
            logger.error("❌ RSS collector is not available")
            return False

        logger.info("✅ RSS collector is available")

        # Show source status
        status = collector.get_source_status()
        logger.info(f"📡 Total sources: {status['total_sources']}")
        logger.info(f"✅ Enabled sources: {status['enabled_sources']}")

        # Show source details
        logger.info("📋 RSS Sources:")
        for source in status["sources"]:
            logger.info(f"  • {source['name']} (Priority: {source['priority']}, AI/ML Focus: {source['ai_ml_focus']})")

        # Test collection
        logger.info("🔄 Testing RSS collection...")
        articles = collector.collect(max_articles=5)

        if articles:
            logger.info(f"✅ Collected {len(articles)} articles from RSS")

            # Show sample articles
            logger.info("📰 Sample RSS articles:")
            for i, article in enumerate(articles[:3], 1):
                logger.info(f"  {i}. {article['title'][:60]}...")
                logger.info(f"     Source: {article['source']} | Category: {article['category']}")
                logger.info(f"     Source Type: {article.get('source_type', 'N/A')}")
                logger.info(
                    f"     Priority: {article.get('priority', 'N/A')} | AI/ML Focus: {article.get('ai_ml_focus', 'N/A')}"
                )
                logger.info("")

            return True
        else:
            logger.warning("⚠️ No articles collected from RSS")
            return False

    except Exception as e:
        logger.error(f"❌ Error testing RSS collector: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_aggregation_service_with_rss():
    """Test the AggregationService with RSS collector integrated."""
    logger.info("\n🧪 Testing AggregationService with RSS collector...")

    try:
        from slackbot.services import AggregationService

        # Create service
        service = AggregationService()

        if not service.is_healthy():
            logger.error("❌ AggregationService is not healthy")
            return False

        logger.info("✅ AggregationService is healthy")

        # Check available collectors
        collectors = service.get_available_collectors()
        logger.info(f"📊 Available collectors: {collectors}")

        # Test collection with RSS
        logger.info("🔄 Testing collection with RSS integration...")
        articles = service.collect_balanced(max_articles=6)

        if articles:
            logger.info(f"✅ Successfully collected {len(articles)} articles")

            # Show source distribution
            source_counts = {}
            for article in articles:
                source_type = article.get("source_type", "unknown")
                source_counts[source_type] = source_counts.get(source_type, 0) + 1

            logger.info("📊 Source distribution:")
            for source_type, count in source_counts.items():
                logger.info(f"  {source_type}: {count} articles")

            return True
        else:
            logger.warning("⚠️ No articles collected")
            return False

    except Exception as e:
        logger.error(f"❌ Error testing AggregationService: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_reranker_with_rss():
    """Test the reranker with RSS articles."""
    logger.info("\n🧪 Testing Reranker with RSS articles...")

    try:
        from slackbot.utils.reranker import create_article_reranker

        # Create reranker
        reranker = create_article_reranker()

        # Test articles including RSS
        test_articles = [
            {
                "title": "AI Breakthrough in Computer Vision",
                "source_type": "newsapi",
                "source": "Tech News",
                "category": "technology",
                "published_at": "2025-08-24T10:00:00Z",
                "summary": "A major breakthrough in computer vision technology has been announced...",
            },
            {
                "title": "New Research on Transformer Architecture",
                "source_type": "arxiv",
                "source": "ArXiv AI Papers",
                "category": "Research Papers",
                "published_at": "2025-08-23T15:30:00Z",
                "summary": "This paper presents novel findings on transformer architecture...",
            },
            {
                "title": "Revolutionary Agentic AI Systems for Autonomous Decision Making",
                "source_type": "rss",
                "source": "TechCrunch AI",
                "category": "AI/ML Technology",
                "published_at": "2025-08-24T12:00:00Z",
                "summary": "New autonomous agent systems that can make complex decisions without human intervention...",
            },
            {
                "title": "Multi-Agent Reinforcement Learning in Robotics",
                "source_type": "rss",
                "source": "Medium AI/ML",
                "category": "AI/ML Development",
                "published_at": "2025-08-24T09:00:00Z",
                "summary": "Advanced multi-agent systems learning complex robotic tasks through reinforcement learning...",
            },
        ]

        # Test reranking
        logger.info("🔄 Testing reranking with RSS articles...")
        ranked_articles = reranker.rerank_articles(test_articles, strategy="smart")

        if ranked_articles:
            logger.info("✅ Reranking successful")

            # Show ranked order
            logger.info("📊 Reranked article order:")
            for i, article in enumerate(ranked_articles, 1):
                score = reranker.calculate_total_score(article)
                logger.info(f"  {i}. {article['title'][:50]}... ({article['source_type']}) - Score: {score:.3f}")

            # Check if RSS articles are properly ranked
            rss_articles = [a for a in ranked_articles if a["source_type"] == "rss"]
            if rss_articles:
                logger.info(f"✅ RSS articles are included in ranking: {len(rss_articles)} articles")
            else:
                logger.warning("⚠️ No RSS articles in ranking results")

            return True
        else:
            logger.warning("⚠️ Reranking failed")
            return False

    except Exception as e:
        logger.error(f"❌ Error testing reranker: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    logger.info("🚀 Starting RSS Collector Tests")
    logger.info("=" * 50)

    # Test 1: Direct RSS collector functionality
    success1 = test_rss_collector()

    # Test 2: AggregationService integration
    success2 = test_aggregation_service_with_rss()

    # Test 3: Reranker with RSS articles
    success3 = test_reranker_with_rss()

    # Summary
    logger.info("\n📋 Test Summary")
    logger.info("=" * 30)
    logger.info(f"RSS Collector Tests: {'✅ PASSED' if success1 else '❌ FAILED'}")
    logger.info(f"AggregationService Integration: {'✅ PASSED' if success2 else '❌ FAILED'}")
    logger.info(f"Reranker with RSS: {'✅ PASSED' if success3 else '❌ FAILED'}")

    if success1 and success2 and success3:
        logger.info("\n🎉 All tests passed! The RSS collector is working correctly.")
        sys.exit(0)
    else:
        logger.error("\n❌ Some tests failed. Please check the logs above.")
        sys.exit(1)
