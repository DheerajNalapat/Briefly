#!/usr/bin/env python3
"""
Script to extract titles and descriptions from client_categorized_news_articles.json
Can be run from the scripts folder
"""

import sys
import os
import json

# Add the POC directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "PoC", "news_source_quality_poc"))


def extract_news_data():
    """Extract titles and descriptions from the news articles"""

    # Path to the articles file
    articles_file = os.path.join(
        os.path.dirname(__file__), "..", "PoC", "news_source_quality_poc", "client_categorized_news_articles.json"
    )

    print("=== News Data Extraction ===")
    print(f"Reading from: {articles_file}")

    try:
        # Load articles
        with open(articles_file, "r", encoding="utf-8") as f:
            articles = json.load(f)

        print(f"Found {len(articles)} articles\n")

        # Group by category
        categories = {}
        for article in articles:
            category = article.get("category", "unknown")
            if category not in categories:
                categories[category] = []
            categories[category].append(article)

        # Display articles by category
        for category, category_articles in categories.items():
            print(f"=== {category.upper()} ({len(category_articles)} articles) ===")
            for i, article in enumerate(category_articles, 1):
                title = article.get("title", "No title")
                description = article.get("description", "No description")
                source = article.get("source", "Unknown")

                print(f"{i}. {title}")
                print(f"   Source: {source}")
                print(f"   {description}")
                print()

        # Summary
        print("=== Summary ===")
        for category, count in categories.items():
            print(f"{category}: {count} articles")

    except FileNotFoundError:
        print(f"File not found: {articles_file}")
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    extract_news_data()
