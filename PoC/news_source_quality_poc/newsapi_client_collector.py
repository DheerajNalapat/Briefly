from newsapi import NewsApiClient
import json
from datetime import datetime
from typing import List, Dict
from config import NEWSAPI_KEY
from enum import Enum


class Category(Enum):
    TECHNICAL = "technical"
    INDUSTRY = "industry"
    APPLICATIONS = "applications"
    ECONOMIC = "economic"
    INFRASTRUCTURE = "infrastructure"


class NewsAPIClientCollector:
    def __init__(self, api_key: str, output_file: str = "newsapi_client_articles.json"):
        self.api_key = api_key
        # Initialize the NewsAPI client
        self.client = NewsApiClient(api_key=api_key)

        # Ensure output file is in the same directory as this script
        import os

        script_dir = os.path.dirname(os.path.abspath(__file__))
        self.output_file = os.path.join(script_dir, output_file)
        self.collected_articles = self.load_existing_articles()

    def load_existing_articles(self) -> List[Dict]:
        """Load existing articles from the output file"""
        try:
            with open(self.output_file, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            return []

    def save_articles(self):
        """Save all collected articles to the output file"""
        with open(self.output_file, "w") as f:
            json.dump(self.collected_articles, f, indent=2, default=str)

    def search_news(
        self,
        query: str,
        max_articles: int = 10,
        sort_by: str = "publishedAt",
        language: str = "en",
        domains: str = None,
        sources: str = None,
        from_date: str = None,
        to_date: str = None,
    ) -> List[Dict]:
        """Search for news articles using the Everything endpoint with client SDK"""
        print(f"Searching for: '{query}'...")

        try:
            # Convert sources string to list if provided
            sources_list = sources.split(",") if sources else None

            # Convert domains string to list if provided
            domains_list = domains.split(",") if domains else None

            # Use the client SDK to get everything
            response = self.client.get_everything(
                q=query,
                sources=sources_list,
                domains=domains_list,
                from_param=from_date,
                to=to_date,
                language=language,
                sort_by=sort_by,
                page_size=max_articles,
            )

            # Check for API errors
            if response.get("status") != "ok":
                print(f"NewsAPI error: {response.get('message', 'Unknown error')}")
                return []

            articles = []

            for article in response.get("articles", []):
                # Skip articles without title or URL
                if not article.get("title") or not article.get("url"):
                    continue

                news_article = {
                    "title": article.get("title", ""),
                    "description": article.get("description", ""),
                    "url": article.get("url", ""),
                    "publishedAt": article.get("publishedAt", ""),
                    "source": article.get("source", {}).get("name", "Unknown"),
                    "author": article.get("author", ""),
                    "urlToImage": article.get("urlToImage", ""),
                    "content": article.get("content", ""),
                    "query": query,
                    "endpoint": "everything",
                    "collected_at": datetime.now().isoformat(),
                }
                articles.append(news_article)

            # Append new articles to existing collection
            self.collected_articles.extend(articles)

            print(f"Found {len(articles)} articles for query: '{query}'")
            return articles

        except Exception as e:
            print(f"Error searching NewsAPI: {e}")
            return []

    def get_top_headlines(
        self, query: str = None, category: str = None, country: str = "us", max_articles: int = 10, sources: str = None
    ) -> List[Dict]:
        """Get top headlines using the Top Headlines endpoint with client SDK"""
        print(f"Getting top headlines for: '{query or category or 'general'}'...")

        try:
            # Convert sources string to list if provided
            sources_list = sources.split(",") if sources else None

            # Use the client SDK to get top headlines
            response = self.client.get_top_headlines(
                q=query, sources=sources_list, category=category, language="en", country=country, page_size=max_articles
            )

            # Check for API errors
            if response.get("status") != "ok":
                print(f"NewsAPI error: {response.get('message', 'Unknown error')}")
                return []

            articles = []

            for article in response.get("articles", []):
                # Skip articles without title or URL
                if not article.get("title") or not article.get("url"):
                    continue

                news_article = {
                    "title": article.get("title", ""),
                    "description": article.get("description", ""),
                    "url": article.get("url", ""),
                    "publishedAt": article.get("publishedAt", ""),
                    "source": article.get("source", {}).get("name", "Unknown"),
                    "author": article.get("author", ""),
                    "urlToImage": article.get("urlToImage", ""),
                    "content": article.get("content", ""),
                    "query": query or category or "top-headlines",
                    "endpoint": "top-headlines",
                    "collected_at": datetime.now().isoformat(),
                }
                articles.append(news_article)

            # Append new articles to existing collection
            self.collected_articles.extend(articles)

            print(f"Found {len(articles)} top headlines")
            return articles

        except Exception as e:
            print(f"Error getting top headlines: {e}")
            return []

    def get_sources(self, category: str = None, country: str = "us", language: str = "en") -> List[Dict]:
        """Get available news sources using client SDK"""
        print(f"Getting news sources...")

        try:
            # Use the client SDK to get sources
            response = self.client.get_sources(category=category, language=language, country=country)

            # Check for API errors
            if response.get("status") != "ok":
                print(f"NewsAPI error: {response.get('message', 'Unknown error')}")
                return []

            sources = response.get("sources", [])
            print(f"Found {len(sources)} news sources")
            return sources

        except Exception as e:
            print(f"Error getting sources: {e}")
            return []

    def run_search(
        self, query: str, max_articles: int = 10, sort_by: str = "publishedAt", domains: str = None, sources: str = None
    ):
        """Run a search using the Everything endpoint and save results"""
        articles = self.search_news(query, max_articles, sort_by, domains=domains, sources=sources)
        if articles:
            self.save_articles()
            print(f"Saved {len(articles)} new articles. Total articles: {len(self.collected_articles)}")
        else:
            print(f"No articles found for query: '{query}'")

    def run_top_headlines(
        self, query: str = None, category: str = None, country: str = "us", max_articles: int = 10, sources: str = None
    ):
        """Run top headlines search and save results"""
        articles = self.get_top_headlines(query, category, country, max_articles, sources)
        if articles:
            self.save_articles()
            print(f"Saved {len(articles)} new articles. Total articles: {len(self.collected_articles)}")
        else:
            print(f"No top headlines found")

    def run_sources_search(self, category: str = None, country: str = None):
        """Get and display available news sources"""
        sources = self.get_sources(category, country)
        if sources:
            print(f"\nAvailable sources:")
            for source in sources[:10]:  # Show first 10 sources
                print(
                    f"- {source.get('name', 'Unknown')} ({source.get('id', 'no-id')}) - {source.get('category', 'no-category')}"
                )
            if len(sources) > 10:
                print(f"... and {len(sources) - 10} more sources")
        return sources

    def fetch_news_by_categories(self, query_params: dict, max_articles_per_category: int = 5):
        """Fetch news for all categories defined in query_params using client SDK"""
        print("=== Fetching News by Categories (Client SDK) ===")
        total_articles = 0

        for category, params in query_params.items():
            print(f"\n--- Fetching {category.value.upper()} News ---")
            print(f"Query: {params['query']}")
            print(f"Keywords: {', '.join(params['keywords'][:5])}...")  # Show first 5 keywords

            # Fetch articles for this category
            articles = self.search_news(
                query=params["query"], max_articles=max_articles_per_category, sort_by="relevancy"
            )

            # Add category information to each article
            for article in articles:
                article["category"] = category.value
                article["keywords"] = params["keywords"]

            total_articles += len(articles)
            print(f"Found {len(articles)} articles for {category.value}")

        # Save all articles
        if total_articles > 0:
            self.save_articles()
            print(f"\n=== Summary ===")
            print(f"Total articles collected: {total_articles}")
            print(f"Total articles in collection: {len(self.collected_articles)}")
        else:
            print("No articles found for any category")

    def fetch_news_by_single_category(self, category: Category, query_params: dict, max_articles: int = 10):
        """Fetch news for a single category using client SDK"""
        if category not in query_params:
            print(f"Category {category.value} not found in query_params")
            return []

        params = query_params[category]
        print(f"=== Fetching {category.value.upper()} News (Client SDK) ===")
        print(f"Query: {params['query']}")

        articles = self.search_news(query=params["query"], max_articles=max_articles, sort_by="relevancy")

        # Add category information to each article
        for article in articles:
            article["category"] = category.value
            article["keywords"] = params["keywords"]

        if articles:
            self.save_articles()
            print(f"Found {len(articles)} articles for {category.value}")
        else:
            print(f"No articles found for {category.value}")

        return articles


# Example usage
if __name__ == "__main__":
    # Define the query parameters (same as before)
    news_query_params = {
        Category.TECHNICAL: {
            "query": "AI model breakthrough OR AI research advancement OR language model improvement",
            "keywords": [
                "gpt",
                "claude",
                "gemini",
                "model",
                "breakthrough",
                "research",
                "capability",
                "advancement",
                "algorithm",
                "neural",
                "training",
            ],
        },
        # Category.INDUSTRY: {
        #     "query": "AI business news OR AI company announcement OR AI industry update",
        #     "keywords": [
        #         "partnership",
        #         "launch",
        #         "market",
        #         "business",
        #         "company",
        #         "startup",
        #         "funding",
        #         "investment",
        #         "acquisition",
        #         "strategy",
        #         "growth",
        #     ],
        # },
        Category.APPLICATIONS: {
            "query": "AI implementation success OR AI use case OR AI solution deployment",
            "keywords": [
                "implementation",
                "solution",
                "use case",
                "deployment",
                "automation",
                "industry",
                "transform",
                "adopt",
                "integrate",
            ],
        },
        # Category.ECONOMIC: {
        #     "query": "AI economic impact OR AI job market OR AI workforce changes",
        #     "keywords": [
        #         "job",
        #         "workforce",
        #         "employment",
        #         "productivity",
        #         "efficiency",
        #         "labor",
        #         "skill",
        #         "training",
        #         "economy",
        #         "market",
        #     ],
        # },
        Category.INFRASTRUCTURE: {
            "query": "AI chip development OR AI hardware OR AI infrastructure news",
            "keywords": [
                "chip",
                "nvidia",
                "semiconductor",
                "hardware",
                "compute",
                "data center",
                "server",
                "gpu",
                "processor",
            ],
        },
    }

    # You need to set your NewsAPI key here
    API_KEY = NEWSAPI_KEY

    if API_KEY == "your_newsapi_key_here" or not API_KEY:
        print("Please set your NewsAPI key in the config.py file")
        print("Get your free key at: https://newsapi.org/register")
    else:
        collector = NewsAPIClientCollector(API_KEY, "client_categorized_news_articles.json")

        # Fetch news using the defined query parameters with client SDK
        print("=== Fetching News by Categories (Client SDK) ===")
        collector.fetch_news_by_categories(news_query_params, max_articles_per_category=5)

        # Example: Fetch news for a specific category
        print("\n=== Fetching Technical News Only (Client SDK) ===")
        # collector.fetch_news_by_single_category(Category.TECHNICAL, news_query_params, max_articles=5)

        # Example: Get available sources
        print("\n=== Available Technology Sources (Client SDK) ===")
        # collector.run_sources_search(category="technology")
