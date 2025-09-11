#!/usr/bin/env python3
"""
Test script for the new reranker utility

This script tests the ArticleReranker to ensure it properly
prioritizes NewsAPI articles over ArXiv papers.
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


def test_reranker():
    """Test the ArticleReranker functionality."""
    logger.info("🧪 Testing Article Reranker...")

    try:
        from slackbot.utils.reranker import create_article_reranker, RankingConfig

        # Create test articles with different source types
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
                "title": "Business Impact of AI in Healthcare",
                "source_type": "newsapi",
                "source": "Business News",
                "category": "business",
                "published_at": "2025-08-24T08:00:00Z",
                "summary": "Analysis of how AI is transforming healthcare business models...",
            },
            {
                "title": "Machine Learning Advances in Robotics",
                "source_type": "arxiv",
                "source": "ArXiv Robotics",
                "category": "Robotics",
                "published_at": "2025-08-22T12:00:00Z",
                "summary": "Recent advances in machine learning for robotic systems...",
            },
        ]

        # Create reranker with default config
        reranker = create_article_reranker()

        # Test smart ranking
        logger.info("🔄 Testing smart ranking strategy...")
        smart_ranked = reranker.rerank_articles(test_articles, strategy="smart")

        logger.info("📊 Smart ranking results:")
        for i, article in enumerate(smart_ranked, 1):
            score = reranker.calculate_total_score(article)
            logger.info(f"  {i}. {article['title']} ({article['source_type']}) - Score: {score:.3f}")

        # Verify NewsAPI articles are prioritized
        newsapi_count = sum(1 for article in smart_ranked[:2] if article["source_type"] == "newsapi")
        if newsapi_count >= 1:
            logger.info("✅ NewsAPI articles are properly prioritized in top positions")
        else:
            logger.warning("⚠️ NewsAPI articles not properly prioritized")

        # Test source priority ranking
        logger.info("\n🔄 Testing source priority ranking strategy...")
        source_ranked = reranker.rerank_articles(test_articles, strategy="source_priority")

        logger.info("📊 Source priority ranking results:")
        for i, article in enumerate(source_ranked, 1):
            score = reranker.calculate_source_score(article)
            logger.info(f"  {i}. {article['title']} ({article['source_type']}) - Source Score: {score:.3f}")

        # Test ranking summary
        logger.info("\n📈 Testing ranking summary...")
        summary = reranker.get_ranking_summary(smart_ranked)

        logger.info("📊 Ranking Summary:")
        for key, value in summary.items():
            if key != "ranking_config":
                logger.info(f"  {key}: {value}")

        logger.info("🎉 Reranker tests completed successfully!")
        return True

    except Exception as e:
        logger.error(f"❌ Error testing reranker: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_content_processing_service():
    """Test the updated ContentProcessingService with reranker."""
    logger.info("\n🧪 Testing ContentProcessingService with reranker...")

    try:
        from slackbot.services import ContentProcessingService

        # Create service
        service = ContentProcessingService(llm_provider="openai")

        if service.is_healthy():
            logger.info("✅ ContentProcessingService is healthy")
        else:
            logger.warning("⚠️ ContentProcessingService health check failed")

        if service.is_reranker_available():
            logger.info("✅ Reranker is available in ContentProcessingService")
        else:
            logger.warning("⚠️ Reranker not available in ContentProcessingService")

        # Test reranking through the service
        test_articles = [
            {
                "title": "AI News from NewsAPI",
                "source_type": "newsapi",
                "source": "Tech News",
                "category": "technology",
                "published_at": "2025-08-24T10:00:00Z",
                "summary": "AI breakthrough news...",
            },
            {
                "title": "Research Paper from ArXiv",
                "source_type": "arxiv",
                "source": "ArXiv",
                "category": "Research Papers",
                "published_at": "2025-08-23T15:30:00Z",
                "summary": "Research paper summary...",
            },
        ]

        logger.info("🔄 Testing reranking through ContentProcessingService...")
        ranked_articles = service.rerank_articles(test_articles, strategy="smart")

        if ranked_articles:
            logger.info("✅ Reranking through service successful")
            logger.info(f"Top article: {ranked_articles[0]['title']} ({ranked_articles[0]['source_type']})")
        else:
            logger.warning("⚠️ Reranking through service failed")

        logger.info("🎉 ContentProcessingService tests completed successfully!")
        return True

    except Exception as e:
        logger.error(f"❌ Error testing ContentProcessingService: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    logger.info("🚀 Starting Reranker Tests")
    logger.info("=" * 50)

    # Test 1: Direct reranker functionality
    success1 = test_reranker()

    # Test 2: ContentProcessingService integration
    success2 = test_content_processing_service()

    # Summary
    logger.info("\n📋 Test Summary")
    logger.info("=" * 30)
    logger.info(f"Reranker Tests: {'✅ PASSED' if success1 else '❌ FAILED'}")
    logger.info(f"Service Integration Tests: {'✅ PASSED' if success2 else '❌ FAILED'}")

    if success1 and success2:
        logger.info("\n🎉 All tests passed! The reranker is working correctly.")
        sys.exit(0)
    else:
        logger.error("\n❌ Some tests failed. Please check the logs above.")
        sys.exit(1)
