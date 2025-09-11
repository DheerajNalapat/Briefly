#!/usr/bin/env python3
"""
Simple script to extract titles and descriptions from client_categorized_news_articles.json
"""

import json
import os
from typing import List, Dict


def load_articles(file_path: str) -> List[Dict]:
    """Load articles from JSON file"""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"File not found: {file_path}")
        return []
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}")
        return []


def extract_titles_descriptions(articles: List[Dict]) -> List[Dict]:
    """Extract title and description from articles"""
    extracted = []

    for article in articles:
        extracted_article = {
            "title": article.get("title", ""),
            "description": article.get("description", ""),
            "category": article.get("category", ""),
            "source": article.get("source", ""),
            "publishedAt": article.get("publishedAt", ""),
            "url": article.get("url", ""),
        }
        extracted.append(extracted_article)

    return extracted


def save_extracted_data(data: List[Dict], output_file: str):
    """Save extracted data to JSON file"""
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def print_articles_summary(articles: List[Dict]):
    """Print a summary of articles"""
    print(f"Total articles: {len(articles)}")

    # Group by category
    categories = {}
    for article in articles:
        category = article.get("category", "unknown")
        if category not in categories:
            categories[category] = 0
        categories[category] += 1

    print("\nArticles by category:")
    for category, count in categories.items():
        print(f"  {category}: {count} articles")

    print("\nSample articles:")
    for i, article in enumerate(articles[:3]):  # Show first 3
        print(f"\n{i+1}. {article.get('title', 'No title')}")
        print(f"   Category: {article.get('category', 'Unknown')}")
        print(f"   Source: {article.get('source', 'Unknown')}")
        print(f"   Description: {article.get('description', 'No description')[:100]}...")


def main():
    """Main function"""
    # Get the directory of this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    input_file = os.path.join(script_dir, "client_categorized_news_articles.json")
    output_file = os.path.join(script_dir, "extracted_titles_descriptions.json")

    print("=== Extracting Titles and Descriptions ===")
    print(f"Input file: {input_file}")
    print(f"Output file: {output_file}")

    # Load articles
    articles = load_articles(input_file)
    if not articles:
        print("No articles found or error loading file")
        return

    # Extract titles and descriptions
    extracted_data = extract_titles_descriptions(articles)

    # Save extracted data
    save_extracted_data(extracted_data, output_file)

    # Print summary
    print_articles_summary(extracted_data)

    print(f"\nExtracted data saved to: {output_file}")


if __name__ == "__main__":
    main()
