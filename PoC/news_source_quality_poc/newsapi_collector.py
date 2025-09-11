from unicodedata import category
import requests
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


class SimpleNewsAPICollector:
    def __init__(self, api_key: str, output_file: str = "newsapi_articles.json"):
        self.api_key = api_key
        # Ensure output file is in the same directory as this script
        import os

        script_dir = os.path.dirname(os.path.abspath(__file__))
        self.output_file = os.path.join(script_dir, output_file)
        self.collected_articles = self.load_existing_articles()
        self.base_url = "https://newsapi.org/v2"

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
        category: str = None,
        domains: str = None,
        sources: str = None,
    ) -> List[Dict]:
        """Search for news articles using the Everything endpoint with improved parameters"""
        print(f"Searching for: '{query}'...")

        try:
            params = {
                "q": query,
                "apiKey": self.api_key,
                "pageSize": max_articles,
                "sortBy": sort_by,
                "language": language,
                "category": category,
            }

            # Add optional parameters
            if domains:
                params["domains"] = domains
            if sources:
                params["sources"] = sources

            response = requests.get(f"{self.base_url}/everything", params=params)
            response.raise_for_status()

            data = response.json()

            # Check for API errors
            if data.get("status") != "ok":
                print(f"NewsAPI error: {data.get('message', 'Unknown error')}")
                return []

            articles = []

            for article in data.get("articles", []):
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

        except requests.exceptions.RequestException as e:
            print(f"Error searching NewsAPI: {e}")
            return []
        except Exception as e:
            print(f"Unexpected error: {e}")
            return []

    def get_top_headlines(
        self, query: str = None, category: str = None, country: str = "us", max_articles: int = 10, sources: str = None
    ) -> List[Dict]:
        """Get top headlines using the Top Headlines endpoint - more accurate for breaking news"""
        print(f"Getting top headlines for: '{query or category or 'general'}'...")

        try:
            params = {
                "apiKey": self.api_key,
                "pageSize": max_articles,
                "country": country,
            }

            # Add optional parameters
            if query:
                params["q"] = query
            if category:
                params["category"] = category
            if sources:
                params["sources"] = sources

            response = requests.get(f"{self.base_url}/top-headlines", params=params)
            response.raise_for_status()

            data = response.json()

            # Check for API errors
            if data.get("status") != "ok":
                print(f"NewsAPI error: {data.get('message', 'Unknown error')}")
                return []

            articles = []

            for article in data.get("articles", []):
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

        except requests.exceptions.RequestException as e:
            print(f"Error getting top headlines: {e}")
            return []
        except Exception as e:
            print(f"Unexpected error: {e}")
            return []

    def get_sources(self, category: str = None, country: str = "in", language: str = "en") -> List[Dict]:
        """Get available news sources"""
        print(f"Getting news sources...")

        try:
            params = {
                "apiKey": self.api_key,
                "language": language,
            }

            # Add optional parameters
            if category:
                params["category"] = category
            if country:
                params["country"] = country

            response = requests.get(f"{self.base_url}/top-headlines/sources", params=params)
            response.raise_for_status()

            data = response.json()

            # Check for API errors
            if data.get("status") != "ok":
                print(f"NewsAPI error: {data.get('message', 'Unknown error')}")
                return []

            sources = data.get("sources", [])
            print(f"Found {len(sources)} news sources")
            return sources

        except requests.exceptions.RequestException as e:
            print(f"Error getting sources: {e}")
            return []
        except Exception as e:
            print(f"Unexpected error: {e}")
            return []

    def get_suggest_sources(self, query: str):
        """Get suggested news sources"""
        print(f"Getting news sources...")

        try:
            params = {"apiKey": self.api_key, "prefix": query}

            response = requests.get("https://eventregistry.org/api/v1/suggestSourcesFast", params=params)
            response.raise_for_status()

            data = response.json()

            # Check for API errors
            if data.get("status") != "ok":
                print(f"NewsAPI error: {data.get('message', 'Unknown error')}")
                return []

            sources = data.get("sources", [])
            print(f"Found {len(sources)} news sources")
            return sources

        except requests.exceptions.RequestException as e:
            print(f"Error getting sources: {e}")
            return []
        except Exception as e:
            print(f"Unexpected error: {e}")
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
            for source in sources[:100]:  # Show first 10 sources
                print(
                    f"- {source.get('name', 'Unknown')} ({source.get('id', 'no-id')}) - {source.get('category', 'no-category')}"
                )
            if len(sources) > 10:
                print(f"... and {len(sources) - 10} more sources")
        return sources

    def run_suggest_sources(self, query: str):
        """Run suggest sources and save results"""
        sources = self.get_suggest_sources(query)
        if sources:
            self.save_articles()
            print(f"Saved {len(sources)} new sources. Total sources: {len(sources)}")
        else:
            print(f"No sources found for query: '{query}'")

    def fetch_news_by_categories(self, query_params: dict, max_articles_per_category: int = 5):
        """Fetch news for all categories defined in query_params"""
        print("=== Fetching News by Categories ===")
        total_articles = 0

        for category, params in query_params.items():
            print(f"\n--- Fetching {category.value.upper()} News ---")
            print(f"Query: {params['query']}")
            print(f"Keywords: {', '.join(params['keywords'][:5])}...")  # Show first 5 keywords

            # Fetch articles for this category
            articles = self.search_news(
                query=params["query"],
                max_articles=max_articles_per_category,
                sort_by="relevancy",
                category=category.value,
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
        """Fetch news for a single category"""
        if category not in query_params:
            print(f"Category {category.value} not found in query_params")
            return []

        params = query_params[category]
        print(f"=== Fetching {category.value.upper()} News ===")
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
        Category.INDUSTRY: {
            "query": "AI business news OR AI company announcement OR AI industry update",
            "keywords": [
                "partnership",
                "launch",
                "market",
                "business",
                "company",
                "startup",
                "funding",
                "investment",
                "acquisition",
                "strategy",
                "growth",
            ],
        },
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
        Category.ECONOMIC: {
            "query": "AI economic impact OR AI job market OR AI workforce changes",
            "keywords": [
                "job",
                "workforce",
                "employment",
                "productivity",
                "efficiency",
                "labor",
                "skill",
                "training",
                "economy",
                "market",
            ],
        },
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
        collector = SimpleNewsAPICollector(API_KEY, "categorized_news_articles.json")

        # Fetch news using the defined query parameters
        print("=== Fetching News by Categories ===")
        collector.fetch_news_by_categories(news_query_params, max_articles_per_category=3)

        # Example: Fetch news for a specific category
        print("\n=== Fetching Technical News Only ===")
        collector.fetch_news_by_single_category(Category.TECHNICAL, news_query_params, max_articles=5)

        # Example: Get available sources
        print("\n=== Available Technology Sources ===")
        collector.run_sources_search(category="technology")
