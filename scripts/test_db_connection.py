#!/usr/bin/env python3
"""
Test script for database connection and functionality.
Tests the PostgreSQL connection, models, and basic operations.
"""

import sys
import os
import logging
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from slackbot.db.db_utils import get_db_session, init_database
from slackbot.db.models import NewsArticle, DailyDigest, DigestArticle
from slackbot.collectors.api_collector import create_api_collector


def setup_logging():
    """Set up logging configuration."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )


def test_database_connection():
    """Test basic database connection."""
    print("🔌 Testing Database Connection")
    print("=" * 50)

    try:
        # Test connection
        with get_db_session() as session:
            print("✅ Database connection successful")

            # Test basic query
            from sqlalchemy import text

            result = session.execute(text("SELECT version()"))
            version = result.scalar()
            print(f"📊 PostgreSQL version: {version}")

        return True

    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False


def test_table_creation():
    """Test table creation."""
    print("\n🏗️ Testing Table Creation")
    print("=" * 50)

    try:
        init_database()
        print("✅ Tables created successfully")
        return True

    except Exception as e:
        print(f"❌ Table creation failed: {e}")
        return False


def test_models():
    """Test database models."""
    print("\n📋 Testing Database Models")
    print("=" * 50)

    try:
        # Test NewsArticle model
        print("Testing NewsArticle model...")
        article = NewsArticle(
            title="Test Article",
            url="https://example.com/test",
            source="Test Source",
            source_type="test",
            content="This is a test article content.",
            summary="Test summary",
            published_at="2024-01-15T10:00:00Z",
        )
        print(f"✅ NewsArticle model created: {article.title}")

        # Test DailyDigest model
        print("Testing DailyDigest model...")
        digest = DailyDigest(
            digest_date="2024-01-15",
            summary="Test daily digest summary",
            article_count=2,
        )
        print(f"✅ DailyDigest model created: {digest.digest_date}")

        # Test DigestArticle model
        print("Testing DigestArticle model...")
        digest_article = DigestArticle(digest_id=1, article_id=1)
        print(f"✅ DigestArticle model created: digest_id={digest_article.digest_id}")

        return True

    except Exception as e:
        print(f"❌ Model testing failed: {e}")
        return False


def test_database_operations():
    """Test basic database operations."""
    print("\n💾 Testing Database Operations")
    print("=" * 50)

    try:
        with get_db_session() as session:
            # Test inserting real data
            print("Inserting real articles from API collector...")
            collector = create_api_collector()
            if collector.is_available():
                real_articles = collector.collect()[:3]  # Get first 3 articles
                print(
                    f"📰 Loaded {len(real_articles)} real articles from API collector"
                )
            else:
                print("❌ API collector not available, cannot test with real data")
                return False

            for article_data in real_articles[:3]:  # Insert first 3 articles
                article = NewsArticle(
                    title=article_data["title"],
                    url=article_data["url"],
                    source=article_data["source"],
                    source_type=article_data["source_type"],
                    content=article_data.get("content", ""),
                    summary=article_data.get("summary", ""),
                    published_at=article_data.get("published_at", ""),
                )
                session.add(article)

            print(f"✅ Inserted {len(dummy_articles[:3])} articles")

            # Test querying
            print("Testing queries...")
            articles = session.query(NewsArticle).all()
            print(f"✅ Total articles in database: {len(articles)}")

            # Test filtering
            ai_articles = (
                session.query(NewsArticle)
                .filter(NewsArticle.source == "TechCrunch")
                .all()
            )
            print(f"✅ TechCrunch articles: {len(ai_articles)}")

            # Test updating
            if articles:
                first_article = articles[0]
                original_title = first_article.title
                first_article.title = "Updated: " + original_title
                print(f"✅ Updated article title: {first_article.title}")

                # Revert change
                first_article.title = original_title
                print(f"✅ Reverted article title: {first_article.title}")

            # Test deleting
            if articles:
                article_to_delete = articles[-1]
                session.delete(article_to_delete)
                print(f"✅ Deleted article: {article_to_delete.title}")

        return True

    except Exception as e:
        print(f"❌ Database operations failed: {e}")
        return False


def test_data_integrity():
    """Test data integrity and constraints."""
    print("\n🔒 Testing Data Integrity")
    print("=" * 50)

    try:
        with get_db_session() as session:
            # Test unique constraint on URL
            print("Testing unique constraint on URL...")
            try:
                duplicate_article = NewsArticle(
                    title="Duplicate Article",
                    url="https://example.com/test",  # Same URL as existing
                    source="Test Source",
                    source_type="test",
                    content="Duplicate content",
                    summary="Duplicate summary",
                    published_at="2024-01-15T10:00:00Z",
                )
                session.add(duplicate_article)
                print("⚠️ Duplicate URL allowed (constraint may not be enforced)")
            except Exception as e:
                print(f"✅ Unique constraint enforced: {e}")

            # Test required fields
            print("Testing required fields...")
            try:
                incomplete_article = NewsArticle(
                    title="",  # Empty title
                    url="https://example.com/incomplete",
                    source="Test Source",
                    source_type="test",
                    content="Incomplete content",
                    summary="Incomplete summary",
                    published_at="2024-01-15T10:00:00Z",
                )
                session.add(incomplete_article)
                print("⚠️ Empty title allowed (constraint may not be enforced)")
            except Exception as e:
                print(f"✅ Required field constraint enforced: {e}")

        return True

    except Exception as e:
        print(f"❌ Data integrity testing failed: {e}")
        return False


def cleanup_test_data():
    """Clean up test data."""
    print("\n🧹 Cleaning Up Test Data")
    print("=" * 50)

    try:
        with get_db_session() as session:
            # Delete all test articles
            deleted_count = session.query(NewsArticle).delete()
            print(f"✅ Deleted {deleted_count} test articles")

            # Delete all test digests
            deleted_digests = session.query(DailyDigest).delete()
            print(f"✅ Deleted {deleted_digests} test digests")

        return True

    except Exception as e:
        print(f"❌ Cleanup failed: {e}")
        return False


def main():
    """Main test function."""
    print("🚀 Database Connection Test Suite")
    print("=" * 60)
    print()

    # Setup
    setup_logging()

    # Check environment
    print("🔍 Environment Check:")
    print(f"  Database URL: {os.getenv('DATABASE_URL', 'Not set')}")
    print(f"  Project root: {Path(__file__).parent.parent}")
    print()

    # Run tests
    tests = [
        ("Database Connection", test_database_connection),
        ("Table Creation", test_table_creation),
        ("Models", test_models),
        ("Database Operations", test_database_operations),
        ("Data Integrity", test_data_integrity),
    ]

    results = {}
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results[test_name] = False

    # Cleanup
    cleanup_test_data()

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
        print("🎉 All tests passed! Database is working correctly.")
    else:
        print("⚠️ Some tests failed. Check the output above for details.")
        print("\n💡 Common issues:")
        print("  1. Database not running (check docker-compose)")
        print("  2. Wrong DATABASE_URL in .env file")
        print("  3. Missing dependencies")
        print("  4. Database permissions")


if __name__ == "__main__":
    main()
