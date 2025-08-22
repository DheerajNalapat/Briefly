#!/usr/bin/env python3
"""
Test script for API News Collector

This script tests the basic functionality without requiring actual API keys.
It demonstrates the structure and configuration loading capabilities.
"""

import json
import yaml
from datetime import datetime
from api_news_collector import APINewsCollector, APINewsSource, NewsItem


def test_configuration_loading():
    """Test loading sources from configuration."""
    print("🧪 Testing Configuration Loading...")

    # Test default sources
    collector = APINewsCollector()
    print(f"✅ Loaded {len(collector.sources)} default sources")

    # Test source types
    arxiv_sources = [s for s in collector.sources if s.source_type == "arxiv"]
    newsapi_sources = [s for s in collector.sources if s.source_type == "newsapi"]

    print(f"   - ArXiv sources: {len(arxiv_sources)}")
    print(f"   - NewsAPI sources: {len(newsapi_sources)}")

    # Display source details
    for source in collector.sources[:3]:  # Show first 3 sources
        print(f"   📍 {source.name} ({source.source_type}) - {source.category}")

    return collector


def test_source_serialization():
    """Test source serialization to/from dictionaries."""
    print("\n🧪 Testing Source Serialization...")

    # Create a test source
    test_source = APINewsSource(
        name="Test ArXiv Source",
        source_type="arxiv",
        query="test query",
        max_results=5,
        category="Test Category",
    )

    # Convert to dictionary
    source_dict = test_source.to_dict()
    print(f"✅ Source converted to dictionary: {source_dict['name']}")

    # Convert back from dictionary
    reconstructed_source = APINewsSource.from_dict(source_dict)
    print(f"✅ Source reconstructed from dictionary: {reconstructed_source.name}")

    # Verify they're the same
    assert test_source.name == reconstructed_source.name
    assert test_source.source_type == reconstructed_source.source_type
    print("✅ Serialization test passed!")


def test_news_item_creation():
    """Test creating and serializing news items."""
    print("\n🧪 Testing News Item Creation...")

    # Create a test news item
    test_item = NewsItem(
        title="Test Research Paper",
        link="https://arxiv.org/abs/test123",
        source="Test ArXiv Source",
        source_type="arxiv",
        category="Test Category",
        summary="This is a test summary for the research paper.",
        published_date="2024-01-01",
        content_hash="abc123",
        api_data={
            "authors": ["Test Author 1", "Test Author 2"],
            "pdf_url": "https://arxiv.org/pdf/test123.pdf",
        },
    )

    # Convert to dictionary
    item_dict = test_item.to_dict()
    print(f"✅ News item created: {item_dict['title']}")
    print(f"   - Source: {item_dict['source']}")
    print(f"   - Category: {item_dict['category']}")
    print(f"   - Authors: {item_dict['api_data']['authors']}")

    return test_item


def test_yaml_configuration():
    """Test YAML configuration file handling."""
    print("\n🧪 Testing YAML Configuration...")

    try:
        # Try to load the example configuration
        with open("example_api_sources.yaml", "r") as f:
            config = yaml.safe_load(f)

        sources = config.get("sources", [])
        print(f"✅ Loaded {len(sources)} sources from YAML configuration")

        # Show some configuration details
        for source in sources[:2]:
            print(f"   📍 {source['name']} ({source['source_type']})")
            print(f"      Query: {source.get('query', 'N/A')}")
            print(f"      Category: {source.get('category', 'N/A')}")
            print(
                f"      Update Interval: {source.get('update_interval', 'N/A')} seconds"
            )

        return True

    except FileNotFoundError:
        print("⚠️  example_api_sources.yaml not found")
        return False
    except Exception as e:
        print(f"❌ Error loading YAML: {e}")
        return False


def test_collector_methods():
    """Test collector utility methods."""
    print("\n🧪 Testing Collector Methods...")

    collector = APINewsCollector()

    # Test content hash generation
    test_content = "This is test content for hashing"
    content_hash = collector.generate_content_hash(test_content)
    print(f"✅ Content hash generated: {content_hash[:10]}...")

    # Test update interval checking
    source = collector.sources[0]
    should_update = collector.should_update_source(source)
    print(f"✅ Source update check: {should_update}")

    # Test cache cleanup
    collector.cleanup_cache()
    print("✅ Cache cleanup method available")


def create_sample_output():
    """Create a sample output file to demonstrate the structure."""
    print("\n🧪 Creating Sample Output...")

    # Create sample news items
    sample_items = [
        NewsItem(
            title="Sample ArXiv Paper: Advances in AI",
            link="https://arxiv.org/abs/sample123",
            source="Sample ArXiv Source",
            source_type="arxiv",
            category="Research Papers",
            summary="This is a sample research paper about advances in artificial intelligence.",
            published_date="2024-01-15",
            content_hash="sample_hash_1",
            api_data={
                "authors": ["Sample Author 1", "Sample Author 2"],
                "pdf_url": "https://arxiv.org/pdf/sample123.pdf",
            },
        ),
        NewsItem(
            title="Sample News Article: AI in Business",
            link="https://example.com/ai-business",
            source="Sample News Source",
            source_type="newsapi",
            category="Business",
            summary="A sample news article about AI applications in business.",
            published_date="2024-01-15T10:00:00Z",
            content_hash="sample_hash_2",
            api_data={
                "author": "Sample Journalist",
                "source_name": "Sample News",
                "url_to_image": "https://example.com/image.jpg",
            },
        ),
    ]

    # Create sample summary
    sample_summary = {
        "timestamp": datetime.now().isoformat(),
        "total_items": len(sample_items),
        "sources_summary": {
            "arxiv": {"count": 1, "sources": ["Sample ArXiv Source"]},
            "newsapi": {"count": 1, "sources": ["Sample News Source"]},
        },
        "categories_summary": {"Research Papers": 1, "Business": 1},
        "items": [item.to_dict() for item in sample_items],
    }

    # Save sample output
    try:
        with open("sample_api_output.json", "w", encoding="utf-8") as f:
            json.dump(sample_summary, f, indent=2, ensure_ascii=False)
        print("✅ Sample output saved to sample_api_output.json")

        # Display summary
        print(f"   - Total items: {sample_summary['total_items']}")
        print(
            f"   - ArXiv papers: {sample_summary['sources_summary']['arxiv']['count']}"
        )
        print(
            f"   - NewsAPI articles: {sample_summary['sources_summary']['newsapi']['count']}"
        )

    except Exception as e:
        print(f"❌ Error saving sample output: {e}")


def main():
    """Run all tests."""
    print("🚀 API News Collector - Test Suite")
    print("=" * 50)

    try:
        # Run all tests
        collector = test_configuration_loading()
        test_source_serialization()
        test_news_item_creation()
        yaml_loaded = test_yaml_configuration()
        test_collector_methods()
        create_sample_output()

        print("\n" + "=" * 50)
        print("✅ All tests completed successfully!")

        if yaml_loaded:
            print("\n📋 Next Steps:")
            print("1. Get a NewsAPI key from https://newsapi.org/")
            print("2. Set environment variable: export NEWSAPI_KEY='your_key'")
            print("3. Run: python api_news_collector.py")
        else:
            print("\n⚠️  Note: YAML configuration not loaded. Check file paths.")

        print("\n✨ Test suite completed!")

    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
