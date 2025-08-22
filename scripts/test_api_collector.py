#!/usr/bin/env python3
"""
Test script for the API News Collector service.
Tests the API-based news collection functionality.
"""

import sys
import os
import logging
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from slackbot.collectors import create_api_collector


def setup_logging():
    """Set up logging configuration."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )


def test_api_collector():
    """Test the API news collector."""
    print("🚀 Testing API News Collector")
    print("=" * 50)

    # Create collector
    collector = create_api_collector()

    if not collector.is_available():
        print("⚠️ API News Collector not available - check dependencies and API keys")
        print(
            "💡 Make sure you have installed: pip install arxiv newsapi-python pyyaml"
        )
        return False

    print("✅ API News Collector initialized successfully")
    print(f"📊 Sources loaded: {len(collector.sources)}")

    # Show source status
    print("\n🔍 Source Status:")
    for source in collector.get_source_status():
        status = "✅ Enabled" if source["enabled"] else "❌ Disabled"
        print(f"  {source['name']}: {status} ({source['source_type']})")

    # Test collection
    print("\n📊 Testing news collection...")
    try:
        results = collector.collect()

        if results:
            print(f"✅ Collected {len(results)} news items")

            # Show sample items
            print("\n📰 Sample items:")
            for i, item in enumerate(results[:3], 1):
                print(f"  {i}. {item['title'][:60]}...")
                print(f"     Source: {item['source']} ({item['source_type']})")
                print(f"     Category: {item['category']}")
                print(f"     URL: {item['url'][:80]}...")
                print()

            # Show collection statistics
            source_counts = {}
            type_counts = {}
            for item in results:
                source_counts[item["source"]] = source_counts.get(item["source"], 0) + 1
                type_counts[item["source_type"]] = (
                    type_counts.get(item["source_type"], 0) + 1
                )

            print("📊 Collection Statistics:")
            print("  By Source:")
            for source, count in source_counts.items():
                print(f"    {source}: {count} items")

            print("  By Type:")
            for type_name, count in type_counts.items():
                print(f"    {type_name}: {count} items")

        else:
            print("⚠️ No news items collected")

        return True

    except Exception as e:
        print(f"❌ Error during collection: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_collector_manager():
    """Test the collector manager functionality."""
    print("\n🔧 Testing Collector Manager")
    print("=" * 50)

    try:
        from slackbot.collectors.base_collector import CollectorManager
        from slackbot.collectors import create_api_collector

        # Create manager
        manager = CollectorManager()
        print("✅ CollectorManager initialized")

        # Add API collector
        api_collector = create_api_collector()
        manager.add_collector(api_collector)
        print(f"✅ Added collector: {api_collector.name}")

        # Show all collectors
        print(f"📊 Total collectors: {len(manager.collectors)}")
        print(f"🔍 Available collectors: {manager.get_available_collectors()}")
        print(f"✅ Enabled collectors: {manager.get_enabled_collectors()}")

        # Test running all collectors
        print("\n🚀 Testing run all collectors...")
        all_results = manager.run_all_collectors()

        if all_results["success"]:
            print(f"✅ Successfully ran {all_results['collectors_run']} collectors")
            print(f"📰 Total items collected: {all_results['total_items']}")
        else:
            print("⚠️ Some collectors failed")

        return True

    except Exception as e:
        print(f"❌ Error testing collector manager: {e}")
        import traceback

        traceback.print_exc()
        return False


def main():
    """Main test function."""
    print("🚀 API News Collector Test Suite")
    print("=" * 60)
    print()

    # Setup
    setup_logging()

    # Check environment
    print("🔍 Environment Check:")
    print(f"  NEWSAPI_KEY: {'✅ Set' if os.getenv('NEWSAPI_KEY') else '❌ Not set'}")
    print(f"  Project root: {Path(__file__).parent.parent}")
    print()

    # Run tests
    tests = [
        ("API News Collector", test_api_collector),
        ("Collector Manager", test_collector_manager),
    ]

    results = {}
    for test_name, test_func in tests:
        try:
            print(f"\n{'='*20} {test_name} {'='*20}")
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results[test_name] = False

    # Summary
    print("\n📋 Test Results Summary")
    print("=" * 50)

    passed = sum(1 for result in results.values() if result)
    total = len(results)

    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {test_name}: {status}")

    print(f"\nOverall: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All tests passed! API collector is ready for use.")
        print("\n💡 Next steps:")
        print("  1. Set up your NewsAPI key for news articles")
        print("  2. Configure custom sources in YAML if needed")
        print("  3. Integrate with the summarizer and Slack publisher")
    else:
        print("⚠️ Some tests failed. Check the output above for details.")
        print("\n💡 Common issues:")
        print("  1. Missing dependencies (arxiv, newsapi-python, pyyaml)")
        print("  2. Missing NEWSAPI_KEY environment variable")
        print("  3. Network connectivity issues")
        print("  4. API rate limiting")


if __name__ == "__main__":
    main()
