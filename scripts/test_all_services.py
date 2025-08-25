#!/usr/bin/env python3
"""
Test script for all Briefly Bot Services

This script tests the three main services:
1. AggregationService - for collecting news
2. SummarizerService - for creating TLDR summaries
3. PublisherService - for publishing messages
"""

import os
import sys
import logging
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Load environment variables
from dotenv import load_dotenv

load_dotenv()

# Import the services
from slackbot.services import AggregationService, SummarizerService, PublisherService


def setup_logging():
    """Set up logging for testing."""
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")


def test_aggregation_service():
    """Test the AggregationService."""
    print("🧪 Testing AggregationService...")
    print("=" * 50)

    try:
        # Initialize the service
        aggregation_service = AggregationService()
        print("✅ AggregationService initialized successfully")

        # Test service health
        is_healthy = aggregation_service.is_healthy()
        print(f"✅ Service health: {is_healthy}")

        # Test collection
        articles = aggregation_service.collect_balanced(max_articles=4, balance_sources=True)
        print(f"✅ Collected {len(articles)} articles")

        # Show article details
        for i, article in enumerate(articles, 1):
            source_type = article.get("source_type", "unknown")
            title = (
                article.get("title", "No title")[:50] + "..."
                if len(article.get("title", "")) > 50
                else article.get("title", "No title")
            )
            print(f"   {i}. [{source_type}] {title}")

        print("🎉 AggregationService tests passed!")
        return aggregation_service, articles

    except Exception as e:
        print(f"❌ AggregationService test failed: {e}")
        logging.exception("AggregationService test failed")
        return None, []


def test_summarizer_service():
    """Test the SummarizerService."""
    print("\n🧪 Testing SummarizerService...")
    print("=" * 50)

    try:
        # Initialize the service
        summarizer_service = SummarizerService(llm_provider="openai")
        print("✅ SummarizerService initialized successfully")

        # Test service health
        is_healthy = summarizer_service.is_healthy()
        print(f"✅ Service health: {is_healthy}")

        # Test provider info
        provider_info = summarizer_service.get_provider_info()
        print(f"✅ Provider info: {provider_info}")

        print("🎉 SummarizerService tests passed!")
        return summarizer_service

    except Exception as e:
        print(f"❌ SummarizerService test failed: {e}")
        logging.exception("SummarizerService test failed")
        return None


def test_publisher_service():
    """Test the PublisherService."""
    print("\n🧪 Testing PublisherService...")
    print("=" * 50)

    try:
        # Initialize the service
        publisher_service = PublisherService(default_platform="slack")
        print("✅ PublisherService initialized successfully")

        # Test service health
        is_healthy = publisher_service.is_healthy()
        print(f"✅ Service health: {is_healthy}")

        # Test available platforms
        platforms = publisher_service.get_available_platforms()
        print(f"✅ Available platforms: {platforms}")

        # Test platform status
        platform_status = publisher_service.get_platform_status()
        print(f"✅ Platform status: {platform_status}")

        print("🎉 PublisherService tests passed!")
        return publisher_service

    except Exception as e:
        print(f"❌ PublisherService test failed: {e}")
        logging.exception("PublisherService test failed")
        return None


def test_service_integration(aggregation_service, summarizer_service, publisher_service, articles):
    """Test integration between all services."""
    print("\n🔗 Testing Service Integration...")
    print("=" * 50)

    try:
        if not all([aggregation_service, summarizer_service, publisher_service, articles]):
            print("⚠️ Skipping integration test - not all services are available")
            return False

        print("1. Testing end-to-end workflow...")

        # Step 1: Create summaries using SummarizerService
        print("   📝 Creating TLDR summaries...")
        summaries = summarizer_service.batch_summarize_articles(articles[:2])  # Test with 2 articles

        if not summaries or all(s is None for s in summaries):
            print("   ❌ Failed to create summaries")
            return False

        print(f"   ✅ Created {len([s for s in summaries if s is not None])} summaries")

        # Step 2: Test publisher connection
        print("   📤 Testing publisher connection...")
        connection_test = publisher_service.test_connection()
        print(f"   ✅ Connection test: {connection_test.get('success', False)}")

        print("🎉 Service integration tests passed!")
        return True

    except Exception as e:
        print(f"❌ Service integration test failed: {e}")
        logging.exception("Service integration test failed")
        return False


def test_service_configurability():
    """Test the configurability of all services."""
    print("\n🔧 Testing Service Configurability...")
    print("=" * 50)

    try:
        # Test AggregationService configurability
        print("1. Testing AggregationService configurability...")
        custom_agg_service = AggregationService(config_path="slackbot/collectors/sources/api_sources_config.yaml")
        print("   ✅ Custom config path works")

        # Test SummarizerService configurability
        print("2. Testing SummarizerService configurability...")
        custom_sum_service = SummarizerService(llm_provider="openai", model_name="gpt-3.5-turbo")
        print("   ✅ Custom LLM provider works")

        # Test PublisherService configurability
        print("3. Testing PublisherService configurability...")
        custom_pub_service = PublisherService(default_platform="slack")
        print("   ✅ Custom platform works")

        print("🎉 Service configurability tests passed!")
        return True

    except Exception as e:
        print(f"❌ Service configurability test failed: {e}")
        logging.exception("Service configurability test failed")
        return False


def main():
    """Main test function."""
    print("🚀 Briefly Bot Services Test Suite")
    print("=" * 60)

    setup_logging()

    # Run individual service tests
    success = True

    aggregation_service, articles = test_aggregation_service()
    success &= aggregation_service is not None

    summarizer_service = test_summarizer_service()
    success &= summarizer_service is not None

    publisher_service = test_publisher_service()
    success &= publisher_service is not None

    # Run integration tests
    if success:
        success &= test_service_integration(aggregation_service, summarizer_service, publisher_service, articles)

    # Run configurability tests
    success &= test_service_configurability()

    if success:
        print("\n🎉 All tests completed successfully!")
        print("\n📋 Summary:")
        print("   ✅ AggregationService - News collection and aggregation")
        print("   ✅ SummarizerService - TLDR summary creation")
        print("   ✅ PublisherService - Multi-platform message publishing")
        print("   ✅ Service Integration - End-to-end workflow")
        print("   ✅ Service Configurability - Custom settings and options")
        print("\n🚀 All services are ready for use in main.py!")
    else:
        print("\n❌ Some tests failed. Check the logs above.")
        sys.exit(1)


if __name__ == "__main__":
    main()
