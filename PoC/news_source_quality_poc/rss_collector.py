import feedparser
import json
from datetime import datetime
from typing import List, Dict
import html2text


class SimpleRSSCollector:
    def __init__(self, output_file: str = "collected_articles.json"):
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

    def parse_html_to_text(self, html: str) -> str:
        """Parse HTML to clean text"""
        if not html or html.strip() == "":
            return ""

        # Configure html2text for better RSS summary parsing
        h = html2text.HTML2Text()
        h.ignore_links = False
        h.ignore_images = True
        h.ignore_emphasis = False
        h.body_width = 0  # Don't wrap text
        h.unicode_snob = True

        # Convert HTML to text
        text = h.handle(html)

        # Clean up the text
        text = text.strip()
        text = text.replace("\n\n\n", "\n\n")  # Remove excessive newlines
        text = text.replace("  ", " ")  # Remove double spaces

        return text

    def save_articles(self):
        """Save all collected articles to the output file"""
        with open(self.output_file, "w") as f:
            json.dump(self.collected_articles, f, indent=2, default=str)

    def collect_from_source(self, source_name: str, rss_url: str, max_items: int = 10) -> List[Dict]:
        """Collect articles from a single RSS source"""
        print(f"Collecting from {source_name}...")

        try:
            feed = feedparser.parse(rss_url)
            articles = []

            for entry in feed.entries[:max_items]:
                # Try different possible summary fields
                summary = ""
                if hasattr(entry, "summary") and entry.summary:
                    summary = entry.summary
                elif hasattr(entry, "description") and entry.description:
                    summary = entry.description
                elif hasattr(entry, "content") and entry.content:
                    # Some feeds use content field
                    summary = entry.content[0].value if entry.content else ""

                # Parse HTML to clean text
                clean_summary = self.parse_html_to_text(summary)

                article = {
                    "title": entry.title,
                    "link": entry.link,
                    "published": getattr(entry, "published", "Unknown"),
                    "summary": clean_summary,
                    "source": source_name,
                    "rss_url": rss_url,
                    "collected_at": datetime.now().isoformat(),
                }
                articles.append(article)

            # Append new articles to existing collection
            self.collected_articles.extend(articles)

            print(f"Collected {len(articles)} articles from {source_name}")
            return articles

        except Exception as e:
            print(f"Error collecting from {source_name}: {e}")
            return []

    def run_single_source(self, source_name: str, rss_url: str, max_items: int = 10):
        """Run collection for a single source and save results"""
        articles = self.collect_from_source(source_name, rss_url, max_items)
        if articles:
            self.save_articles()
            print(f"Saved {len(articles)} new articles. Total articles: {len(self.collected_articles)}")
        else:
            print(f"No articles collected from {source_name}")


# Example usage
if __name__ == "__main__":
    collector = SimpleRSSCollector()

    # Example sources - you can modify these or run them separately
    sources = [
        # {"name": "Medium AI", "url": "https://medium.com/feed/tag/retrieval-augmented-generation", "max_items": 5},
        # {"name": "Medium AI", "url": "https://medium.com/feed/tag/agentic-ai", "max_items": 5},
        # {"name": "Medium AI", "url": "https://medium.com/feed/tag/llm", "max_items": 5},
        {"name": "Medium AI", "url": "https://medium.com/feed/tag/llm-agents", "max_items": 5},
    ]

    # Collect from first source only
    if sources:
        source = sources[0]
        collector.run_single_source(source["name"], source["url"], source["max_items"])
