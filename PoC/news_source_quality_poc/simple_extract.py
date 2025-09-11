#!/usr/bin/env python3
"""
Simple script to extract just titles and descriptions from client_categorized_news_articles.json
"""

import json
import os


def main():
    """Extract just titles and descriptions"""
    # Get the directory of this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    input_file = os.path.join(script_dir, "client_categorized_news_articles.json")

    print("=== Simple Title and Description Extraction ===")

    try:
        # Load articles
        with open(input_file, "r", encoding="utf-8") as f:
            articles = json.load(f)

        print(f"Found {len(articles)} articles\n")

        # Extract and display titles and descriptions
        for i, article in enumerate(articles, 1):
            title = article.get("title", "No title")
            description = article.get("description", "No description")
            category = article.get("category", "unknown")

            print(f"{i}. [{category.upper()}] {title}")
            print(f"   {description}")
            print()

    except FileNotFoundError:
        print(f"File not found: {input_file}")
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}")


if __name__ == "__main__":
    main()
