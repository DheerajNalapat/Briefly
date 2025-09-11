#!/usr/bin/env python3
"""
Comprehensive RSS Collector Test Script

This script tests the RSSCollector and outputs ALL collected articles to JSON
for comprehensive review. Focuses on software development, AI, RAG, and agentic systems.
"""

import sys
import os
import json
import logging
from pathlib import Path
from datetime import datetime

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

logger = logging.getLogger(__name__)


def test_rss_collector_comprehensive():
    """Test the RSSCollector and collect ALL articles for review."""
    logger.info("🧪 Testing RSS Collector - Comprehensive Collection...")

    try:
        from slackbot.collectors.rss_collector import create_rss_collector

        # Create collector
        collector = create_rss_collector()

        if not collector.is_available():
            logger.error("❌ RSS collector is not available")
            return None

        logger.info("✅ RSS collector is available")

        # Show source status
        status = collector.get_source_status()
        logger.info(f"📡 Total sources: {status['total_sources']}")
        logger.info(f"✅ Enabled sources: {status['enabled_sources']}")

        # Show source details
        logger.info("📋 RSS Sources:")
        for source in status["sources"]:
            logger.info(f"  • {source['name']} (Priority: {source['priority']}, AI/ML Focus: {source['ai_ml_focus']})")

        # Test comprehensive collection (no max_articles limit)
        logger.info("🔄 Testing comprehensive RSS collection...")
        articles = collector.collect()  # No max_articles limit

        if articles:
            logger.info(f"✅ Collected {len(articles)} total articles from RSS")

            # Show source distribution
            source_counts = {}
            category_counts = {}
            for article in articles:
                source = article.get("source", "unknown")
                category = article.get("category", "unknown")
                source_counts[source] = source_counts.get(source, 0) + 1
                category_counts[category] = category_counts.get(category, 0) + 1

            logger.info("📊 Source distribution:")
            for source, count in sorted(source_counts.items(), key=lambda x: x[1], reverse=True):
                logger.info(f"  {source}: {count} articles")

            logger.info("📊 Category distribution:")
            for category, count in sorted(category_counts.items(), key=lambda x: x[1], reverse=True):
                logger.info(f"  {category}: {count} articles")

            return articles
        else:
            logger.warning("⚠️ No articles collected from RSS")
            return None

    except Exception as e:
        logger.error(f"❌ Error testing RSS collector: {e}")
        import traceback

        traceback.print_exc()
        return None


def test_aggregation_service_comprehensive():
    """Test the AggregationService with comprehensive collection."""
    logger.info("\n🧪 Testing AggregationService - Comprehensive Collection...")

    try:
        from slackbot.services import AggregationService

        # Create service
        service = AggregationService()

        if not service.is_healthy():
            logger.error("❌ AggregationService is not healthy")
            return None

        logger.info("✅ AggregationService is healthy")

        # Check available collectors
        collectors = service.get_available_collectors()
        logger.info(f"📊 Available collectors: {collectors}")

        # Test comprehensive collection (no max_articles limit)
        logger.info("🔄 Testing comprehensive collection with all services...")
        articles = service.collect_balanced(max_articles=None)  # No limit

        if articles:
            logger.info(f"✅ Successfully collected {len(articles)} total articles")

            # Show source distribution
            source_counts = {}
            for article in articles:
                source_type = article.get("source_type", "unknown")
                source_counts[source_type] = source_counts.get(source_type, 0) + 1

            logger.info("📊 Source distribution:")
            for source_type, count in sorted(source_counts.items(), key=lambda x: x[1], reverse=True):
                logger.info(f"  {source_type}: {count} articles")

            return articles
        else:
            logger.warning("⚠️ No articles collected")
            return None

    except Exception as e:
        logger.error(f"❌ Error testing AggregationService: {e}")
        import traceback

        traceback.print_exc()
        return None


def test_reranker_comprehensive(articles):
    """Test the reranker with comprehensive article set."""
    logger.info("\n🧪 Testing Reranker - Comprehensive Ranking...")

    try:
        from slackbot.utils.reranker import create_article_reranker

        # Create reranker
        reranker = create_article_reranker()

        # Test reranking
        logger.info("🔄 Testing reranking with comprehensive article set...")
        ranked_articles = reranker.rerank_articles(articles, strategy="smart")

        if ranked_articles:
            logger.info("✅ Reranking successful")

            # Show top 10 ranked articles
            logger.info("📊 Top 10 ranked articles:")
            for i, article in enumerate(ranked_articles[:10], 1):
                score = reranker.calculate_total_score(article)
                title = article.get("title", "No title")[:80]
                source = article.get("source", "Unknown")
                category = article.get("category", "Unknown")
                logger.info(f"  {i}. {title}... ({source}) - Score: {score:.3f} - Category: {category}")

            # Show ranking summary
            summary = reranker.get_ranking_summary(ranked_articles)
            logger.info("📈 Ranking Summary:")
            for key, value in summary.items():
                if key != "ranking_config":
                    logger.info(f"  {key}: {value}")

            return ranked_articles
        else:
            logger.warning("⚠️ Reranking failed")
            return None

    except Exception as e:
        logger.error(f"❌ Error testing reranker: {e}")
        import traceback

        traceback.print_exc()
        return None


def save_articles_to_json(articles, filename_prefix="rss_collection"):
    """Save all articles to a JSON file for review."""
    if not articles:
        logger.warning("⚠️ No articles to save")
        return None

    try:
        # Create timestamp for filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{filename_prefix}_{timestamp}.json"

        # Prepare articles for JSON serialization
        serializable_articles = []
        for article in articles:
            # Convert any non-serializable objects to strings
            serializable_article = {}
            for key, value in article.items():
                if isinstance(value, (datetime, type)):
                    serializable_article[key] = str(value)
                else:
                    serializable_article[key] = value
            serializable_articles.append(serializable_article)

        # Save to JSON file
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "collection_info": {
                        "timestamp": timestamp,
                        "total_articles": len(articles),
                        "description": "Comprehensive RSS collection for software developers focusing on AI, RAG, and agentic systems",
                    },
                    "articles": serializable_articles,
                },
                f,
                indent=2,
                ensure_ascii=False,
            )

        logger.info(f"✅ Articles saved to {filename}")
        return filename

    except Exception as e:
        logger.error(f"❌ Error saving articles to JSON: {e}")
        import traceback

        traceback.print_exc()
        return None


def analyze_articles_for_developers(articles):
    """Analyze articles for software development relevance."""
    logger.info("\n🔍 Analyzing articles for software development relevance...")

    if not articles:
        return

    # Keywords relevant to software developers
    dev_keywords = [
        "rag",
        "retrieval augmented generation",
        "vector database",
        "embedding",
        "langchain",
        "llama index",
        "openai",
        "anthropic",
        "claude",
        "python",
        "javascript",
        "typescript",
        "api",
        "rest",
        "graphql",
        "docker",
        "kubernetes",
        "devops",
        "cloud",
        "aws",
        "azure",
        "software development",
        "programming",
        "coding",
        "algorithm",
        "machine learning",
        "ai",
        "ml",
        "neural network",
        "transformer",
        "agentic",
        "autonomous agent",
        "multi-agent",
        "llm",
        "gpt",
    ]

    # Count articles with developer-relevant keywords
    dev_relevant_count = 0
    dev_relevant_articles = []

    for article in articles:
        title = article.get("title", "").lower()
        summary = article.get("summary", "").lower()
        category = article.get("category", "").lower()

        content = f"{title} {summary} {category}"

        # Check if article contains developer-relevant keywords
        is_dev_relevant = any(keyword in content for keyword in dev_keywords)

        if is_dev_relevant:
            dev_relevant_count += 1
            dev_relevant_articles.append(
                {
                    "title": article.get("title", "No title"),
                    "source": article.get("source", "Unknown"),
                    "category": article.get("category", "Unknown"),
                    "url": article.get("url", ""),
                    "summary": article.get("summary", "")[:200] + "..." if article.get("summary") else "No summary",
                }
            )

    logger.info(
        f"📊 Developer-relevant articles: {dev_relevant_count}/{len(articles)} ({dev_relevant_count/len(articles)*100:.1f}%)"
    )

    # Show top developer-relevant articles
    if dev_relevant_articles:
        logger.info("🚀 Top Developer-Relevant Articles:")
        for i, article in enumerate(dev_relevant_articles[:10], 1):
            logger.info(f"  {i}. {article['title']}")
            logger.info(f"     Source: {article['source']} | Category: {article['category']}")
            logger.info(f"     Summary: {article['summary']}")
            logger.info("")

    return dev_relevant_articles


if __name__ == "__main__":
    logger.info("🚀 Starting Comprehensive RSS Collector Tests")
    logger.info("=" * 60)

    # Test 1: Direct RSS collector functionality
    logger.info("📡 Testing RSS Collector...")
    rss_articles = test_rss_collector_comprehensive()

    # Test 2: AggregationService integration
    logger.info("🔄 Testing AggregationService...")
    all_articles = test_aggregation_service_comprehensive()

    # Test 3: Reranker with comprehensive articles
    if all_articles:
        logger.info("🎯 Testing Reranker...")
        ranked_articles = test_reranker_comprehensive(all_articles)
    else:
        ranked_articles = None

    # Test 4: Analyze articles for developer relevance
    if all_articles:
        dev_relevant = analyze_articles_for_developers(all_articles)
    else:
        dev_relevant = None

    # Save all articles to JSON for review
    if all_articles:
        logger.info("💾 Saving articles to JSON for review...")
        json_filename = save_articles_to_json(all_articles, "comprehensive_rss_collection")
    else:
        json_filename = None

    # Summary
    logger.info("\n📋 Test Summary")
    logger.info("=" * 30)
    logger.info(f"RSS Collector: {'✅ PASSED' if rss_articles else '❌ FAILED'}")
    logger.info(f"AggregationService: {'✅ PASSED' if all_articles else '❌ FAILED'}")
    logger.info(f"Reranker: {'✅ PASSED' if ranked_articles else '❌ FAILED'}")
    logger.info(f"Developer Analysis: {'✅ PASSED' if dev_relevant else '❌ FAILED'}")
    logger.info(f"JSON Export: {'✅ PASSED' if json_filename else '❌ FAILED'}")

    if json_filename:
        logger.info(f"\n📁 All articles saved to: {json_filename}")
        logger.info("🔍 You can now review the complete collection in the JSON file")

    if all_articles:
        logger.info(f"\n📊 Total articles collected: {len(all_articles)}")
        logger.info("🎉 Comprehensive RSS collection test completed successfully!")
        sys.exit(0)
    else:
        logger.error("\n❌ Some tests failed. Please check the logs above.")
        sys.exit(1)
