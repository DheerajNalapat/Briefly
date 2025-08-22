#!/usr/bin/env python3
"""
Demo script for API News Collector

This script demonstrates various ways to use the API collector:
1. Using default sources
2. Loading from YAML configuration
3. Adding sources programmatically
4. Custom filtering and processing
"""

import os
import json
from datetime import datetime
from api_news_collector import APINewsCollector, APINewsSource


def demo_default_sources():
    """Demonstrate using default sources."""
    print("🎯 Demo 1: Default Sources")
    print("-" * 40)

    collector = APINewsCollector()

    print(f"Loaded {len(collector.sources)} default sources:")
    for source in collector.sources:
        status = "✅" if source.enabled else "❌"
        print(f"  {status} {source.name} ({source.source_type}) - {source.category}")

    print(f"\nSource breakdown:")
    arxiv_count = len([s for s in collector.sources if s.source_type == "arxiv"])
    newsapi_count = len([s for s in collector.sources if s.source_type == "newsapi"])

    print(f"  - ArXiv sources: {arxiv_count}")
    print(f"  - NewsAPI sources: {newsapi_count}")

    return collector


def demo_yaml_configuration():
    """Demonstrate loading from YAML configuration."""
    print("\n🎯 Demo 2: YAML Configuration")
    print("-" * 40)

    try:
        # Load from example configuration
        collector = APINewsCollector("example_api_sources.yaml")

        print(f"Loaded {len(collector.sources)} sources from YAML:")
        for source in collector.sources[:5]:  # Show first 5
            print(f"  📍 {source.name} ({source.source_type})")
            print(f"     Query: {source.query or 'N/A'}")
            print(f"     Category: {source.category}")
            print(f"     Update Interval: {source.update_interval} seconds")
            print()

        return collector

    except Exception as e:
        print(f"❌ Error loading YAML config: {e}")
        print("Falling back to default sources...")
        return APINewsCollector()


def demo_programmatic_sources():
    """Demonstrate adding sources programmatically."""
    print("\n🎯 Demo 3: Programmatic Sources")
    print("-" * 40)

    collector = APINewsCollector()

    # Add custom ArXiv source
    custom_arxiv = APINewsSource(
        name="Custom Deep Learning Papers",
        source_type="arxiv",
        query="deep learning OR neural networks OR transformers",
        max_results=25,
        sort_by="submittedDate",
        sort_order="descending",
        category="Deep Learning",
        update_interval=7200,  # 2 hours
    )

    # Add custom NewsAPI source
    custom_news = APINewsSource(
        name="Custom AI Business News",
        source_type="newsapi",
        query="AI startup OR artificial intelligence investment",
        category="business",
        language="en",
        country="us",
        max_items=12,
        update_interval=1800,  # 30 minutes
    )

    # Add to collector
    collector.sources.extend([custom_arxiv, custom_news])

    print(f"Added custom sources. Total sources: {len(collector.sources)}")
    print("New sources:")
    print(f"  📍 {custom_arxiv.name} ({custom_arxiv.source_type})")
    print(f"  📍 {custom_news.name} ({custom_news.source_type})")

    return collector


def demo_source_filtering():
    """Demonstrate filtering and querying sources."""
    print("\n🎯 Demo 4: Source Filtering")
    print("-" * 40)

    collector = APINewsCollector()

    # Filter sources by type
    arxiv_sources = [s for s in collector.sources if s.source_type == "arxiv"]
    newsapi_sources = [s for s in collector.sources if s.source_type == "newsapi"]

    print(f"ArXiv sources ({len(arxiv_sources)}):")
    for source in arxiv_sources:
        print(f"  📄 {source.name}: {source.query}")

    print(f"\nNewsAPI sources ({len(newsapi_sources)}):")
    for source in newsapi_sources:
        print(f"  📰 {source.name}: {source.category}")

    # Filter by category
    ai_sources = [
        s
        for s in collector.sources
        if "AI" in s.name or (s.query and "artificial intelligence" in s.query.lower())
    ]
    print(f"\nAI-related sources ({len(ai_sources)}):")
    for source in ai_sources:
        print(f"  🤖 {source.name}")

    return collector


def demo_configuration_management():
    """Demonstrate configuration management features."""
    print("\n🎯 Demo 5: Configuration Management")
    print("-" * 40)

    collector = APINewsCollector()

    # Save current configuration
    config_file = "demo_sources_config.yaml"
    collector.save_sources_config(config_file)
    print(f"✅ Configuration saved to {config_file}")

    # Modify a source
    if collector.sources:
        source = collector.sources[0]
        print(f"\nModifying source: {source.name}")
        print(f"  Before: enabled={source.enabled}, max_items={source.max_items}")

        source.enabled = False
        source.max_items = 5

        print(f"  After: enabled={source.enabled}, max_items={source.max_items}")

    # Save modified configuration
    collector.save_sources_config("demo_modified_config.yaml")
    print("✅ Modified configuration saved")

    return collector


def demo_error_handling():
    """Demonstrate error handling scenarios."""
    print("\n🎯 Demo 6: Error Handling")
    print("-" * 40)

    # Test with missing API key
    print("Testing without NewsAPI key...")
    os.environ.pop("NEWSAPI_KEY", None)  # Remove if exists

    collector = APINewsCollector()
    collector.initialize_apis()

    # Test with invalid source type
    print("\nTesting invalid source type...")
    invalid_source = APINewsSource(
        name="Invalid Source", source_type="invalid_type", query="test"
    )

    try:
        items = collector.fetch_from_source(invalid_source)
        print(f"Result: {len(items)} items")
    except Exception as e:
        print(f"✅ Error handled: {e}")

    return collector


def demo_output_formats():
    """Demonstrate different output formats."""
    print("\n🎯 Demo 7: Output Formats")
    print("-" * 40)

    # Create sample data structure
    sample_summary = {
        "timestamp": datetime.now().isoformat(),
        "total_items": 0,
        "sources_summary": {
            "arxiv": {"count": 0, "sources": []},
            "newsapi": {"count": 0, "sources": []},
        },
        "categories_summary": {},
        "items": [],
    }

    # Save in different formats
    collector = APINewsCollector()

    # JSON output
    json_file = "demo_output.json"
    collector.save_summary(sample_summary, json_file)
    print(f"✅ JSON output saved to {json_file}")

    # YAML configuration
    yaml_file = "demo_output_config.yaml"
    collector.save_sources_config(yaml_file)
    print(f"✅ YAML configuration saved to {json_file}")

    return collector


def main():
    """Run all demos."""
    print("🚀 API News Collector - Demo Suite")
    print("=" * 60)

    try:
        # Run all demos
        demo_default_sources()
        demo_yaml_configuration()
        demo_programmatic_sources()
        demo_source_filtering()
        demo_configuration_management()
        demo_error_handling()
        demo_output_formats()

        print("\n" + "=" * 60)
        print("✅ All demos completed successfully!")

        print("\n📋 Generated Files:")
        print("  - demo_sources_config.yaml (original configuration)")
        print("  - demo_modified_config.yaml (modified configuration)")
        print("  - demo_output.json (sample JSON output)")
        print("  - demo_output_config.yaml (sample YAML config)")

        print("\n🔑 To test with real APIs:")
        print("1. Get NewsAPI key: https://newsapi.org/")
        print("2. Set: export NEWSAPI_KEY='your_key'")
        print("3. Run: python api_news_collector.py")

        print("\n✨ Demo suite completed!")

    except Exception as e:
        print(f"\n❌ Demo failed with error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
