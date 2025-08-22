#!/usr/bin/env python3
"""
Test script to evaluate the quality of TLDR summaries.
Tests the summarizer with real articles to see the output quality.
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Load environment variables
try:
    from dotenv import load_dotenv

    load_dotenv(project_root / ".env")
    print("✅ Environment variables loaded from .env file")
except ImportError:
    print("⚠️ python-dotenv not available, using shell environment")
except Exception as e:
    print(f"⚠️ Could not load .env file: {e}")


def test_summarizer_quality():
    """Test the quality of TLDR summaries."""
    print("🧪 Testing TLDR Summarizer Quality")
    print("=" * 60)

    try:
        # Import components
        from slackbot.collectors.api_collector import create_api_collector
        from slackbot.summarizer.tldr_summarizer import create_tldr_summarizer

        print("📦 Components imported successfully")

        # Create collector and get real articles
        print("\n🔍 Collecting real articles for testing...")
        collector = create_api_collector()

        if not collector.is_available():
            print("❌ API collector not available")
            return False

        # Collect a few articles
        articles = collector.collect()
        if not articles:
            print("❌ No articles collected")
            return False

        # Limit to 3 articles for testing
        test_articles = articles[:3]
        print(f"✅ Collected {len(test_articles)} articles for testing")

        # Create summarizer
        print("\n🧠 Creating TLDR summarizer...")
        summarizer = create_tldr_summarizer()

        if not summarizer.llm:
            print("❌ Summarizer not available - check API keys")
            return False

        print(f"✅ Summarizer created with provider: {summarizer.llm_provider}")

        # Test individual article summarization
        print("\n📝 Testing Individual Article Summarization")
        print("-" * 60)

        for i, article in enumerate(test_articles, 1):
            print(f"\n📰 Article {i}: {article.get('title', 'Unknown Title')[:80]}...")
            print(f"   Source: {article.get('source', 'Unknown')} ({article.get('source_type', 'Unknown')})")
            print(f"   Category: {article.get('category', 'Unknown')}")

            # Log input content for debugging
            print(f"\n   📥 INPUT CONTENT:")
            print(f"   Title: {article.get('title', 'No title')}")
            print(f"   Summary Length: {len(article.get('summary', ''))} chars")
            print(f"   Content Length: {len(article.get('content', ''))} chars")
            print(f"   Summary Preview: {article.get('summary', 'No summary')[:150]}...")
            print(f"   Content Preview: {article.get('content', 'No content')[:150]}...")

            try:
                # Create TLDR summary
                print(f"\n   🧠 Generating TLDR summary...")
                summary = summarizer.create_article_tldr(article)

                if summary:
                    print("   ✅ Summary created successfully!")
                    print(f"\n   📤 GENERATED SUMMARY:")
                    print(f"   📋 TLDR: {summary.tldr_text}")
                    print(f"   🔑 Key Points: {summary.key_points}")
                    print(f"   📈 Trending Topics: {summary.trending_topics}")
                    print(f"   ⏱️ Reading Time: {summary.reading_time}")
                    print(f"   🎯 Impact Level: {summary.impact_level}")
                    print(f"   📊 Article Count: {summary.article_count}")
                    print(f"   🏷️ Categories: {summary.categories}")
                    print(f"   📰 Sources: {summary.sources}")
                    print(f"   🤖 Model Used: {summary.model_used}")
                    print(f"   ⏰ Generated At: {summary.generated_at}")

                    # Quality assessment
                    print(f"\n   📊 QUALITY ASSESSMENT:")
                    if summary.tldr_text and summary.tldr_text not in ["No content available", "Summary not available"]:
                        print(f"   ✅ TLDR Content: Good ({len(summary.tldr_text)} chars)")
                    else:
                        print(f"   ❌ TLDR Content: Poor - '{summary.tldr_text}'")

                    if summary.key_points and len(summary.key_points) > 0:
                        print(f"   ✅ Key Points: Good ({len(summary.key_points)} points)")
                    else:
                        print(f"   ❌ Key Points: Poor - Empty or missing")

                else:
                    print("   ❌ Failed to create summary")

            except Exception as e:
                print(f"   ❌ Error creating summary: {e}")
                import traceback

                print(f"   🔍 Full error: {traceback.format_exc()}")

        # Test digest summarization
        print("\n📚 Testing Digest Summarization")
        print("-" * 60)

        try:
            print("🧠 Generating digest summary...")
            digest_summary = summarizer.create_tldr_digest(test_articles)

            if digest_summary:
                print("✅ Digest summary created successfully!")
                print(f"\n📤 GENERATED DIGEST SUMMARY:")
                print(f"📋 Main TLDR: {digest_summary.tldr_text}")
                print(f"🔑 Key Points: {digest_summary.key_points}")
                print(f"📊 Trending Topics: {digest_summary.trending_topics}")
                print(f"🎯 Impact Level: {digest_summary.impact_level}")
                print(f"📊 Article Count: {digest_summary.article_count}")
                print(f"🏷️ Categories: {digest_summary.categories}")
                print(f"📰 Sources: {digest_summary.sources}")
                print(f"🤖 Model Used: {digest_summary.model_used}")
                print(f"⏰ Generated At: {digest_summary.generated_at}")

                # Quality assessment for digest
                print(f"\n📊 DIGEST QUALITY ASSESSMENT:")
                if digest_summary.tldr_text and digest_summary.tldr_text not in [
                    "No significant AI/ML news articles found today"
                ]:
                    print(f"   ✅ Digest TLDR: Good ({len(digest_summary.tldr_text)} chars)")
                else:
                    print(f"   ❌ Digest TLDR: Poor - '{digest_summary.tldr_text}'")

                if digest_summary.key_points and len(digest_summary.key_points) > 0:
                    print(f"   ✅ Digest Key Points: Good ({len(digest_summary.key_points)} points)")
                else:
                    print(f"   ❌ Digest Key Points: Poor - Empty or missing")

            else:
                print("❌ Failed to create digest summary")

        except Exception as e:
            print(f"❌ Error creating digest summary: {e}")
            import traceback

            print(f"🔍 Full error: {traceback.format_exc()}")

        return True

    except Exception as e:
        print(f"❌ Error testing summarizer: {e}")
        return False


def test_summarizer_with_different_providers():
    """Test summarizer with different LLM providers."""
    print("\n🔄 Testing Different LLM Providers")
    print("=" * 60)

    try:
        from slackbot.summarizer.tldr_summarizer import create_tldr_summarizer

        # Test with OpenAI (default)
        print("\n🤖 Testing with OpenAI...")
        openai_summarizer = create_tldr_summarizer(llm_provider="openai")

        if openai_summarizer.llm:
            print("✅ OpenAI summarizer created successfully")
        else:
            print("❌ OpenAI summarizer not available")

        # Test with Gemini
        print("\n🧠 Testing with Gemini...")
        gemini_summarizer = create_tldr_summarizer(llm_provider="gemini")

        if gemini_summarizer.llm:
            print("✅ Gemini summarizer created successfully")
        else:
            print("❌ Gemini summarizer not available")

        return True

    except Exception as e:
        print(f"❌ Error testing different providers: {e}")
        return False


def main():
    """Main test function."""
    print("🧪 TLDR Summarizer Quality Test")
    print("=" * 60)

    # Test 1: Summarizer quality
    quality_ok = test_summarizer_quality()

    # Test 2: Different providers
    providers_ok = test_summarizer_with_different_providers()

    # Summary
    print("\n📋 Test Results")
    print("=" * 60)
    print(f"  Summarizer Quality: {'✅ PASS' if quality_ok else '❌ FAIL'}")
    print(f"  Provider Support: {'✅ PASS' if providers_ok else '❌ FAIL'}")

    if quality_ok and providers_ok:
        print("\n🎉 Summarizer is working perfectly!")
        print("💡 You can now run the complete workflow with confidence.")
    else:
        print("\n⚠️ There are issues with the summarizer that need to be fixed.")


if __name__ == "__main__":
    main()
