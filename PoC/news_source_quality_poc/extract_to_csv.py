#!/usr/bin/env python3
"""
Script to extract titles and descriptions to CSV format
"""

import json
import csv
import os
from datetime import datetime


def main():
    """Extract titles and descriptions to CSV"""
    # Get the directory of this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    input_file = os.path.join(script_dir, "client_categorized_news_articles.json")
    output_file = os.path.join(script_dir, "extracted_articles.csv")

    print("=== Extracting to CSV ===")

    try:
        # Load articles
        with open(input_file, "r", encoding="utf-8") as f:
            articles = json.load(f)

        print(f"Found {len(articles)} articles")

        # Write to CSV
        with open(output_file, "w", newline="", encoding="utf-8") as csvfile:
            fieldnames = ["id", "title", "description", "category", "source", "publishedAt", "url"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            # Write header
            writer.writeheader()

            # Write articles
            for i, article in enumerate(articles, 1):
                writer.writerow(
                    {
                        "id": i,
                        "title": article.get("title", ""),
                        "description": article.get("description", ""),
                        "category": article.get("category", ""),
                        "source": article.get("source", ""),
                        "publishedAt": article.get("publishedAt", ""),
                        "url": article.get("url", ""),
                    }
                )

        print(f"CSV file created: {output_file}")

        # Show summary
        categories = {}
        for article in articles:
            category = article.get("category", "unknown")
            categories[category] = categories.get(category, 0) + 1

        print("\nArticles by category:")
        for category, count in categories.items():
            print(f"  {category}: {count} articles")

    except FileNotFoundError:
        print(f"File not found: {input_file}")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
