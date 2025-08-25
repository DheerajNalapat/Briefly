#!/usr/bin/env python3
"""
ArXiv Research Papers Collector

This collector fetches research papers from ArXiv API.
Specialized for academic and research content.
"""

import os
import logging
import hashlib
import time
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict

# Third-party imports
try:
    import arxiv

    DEPENDENCIES_AVAILABLE = True
except ImportError:
    logging.warning("Required dependencies not available. Install with: pip install arxiv")
    DEPENDENCIES_AVAILABLE = False
    arxiv = None

from .base_collector import BaseCollector

logger = logging.getLogger(__name__)


@dataclass
class ArXivSource:
    """Represents a configurable ArXiv source."""

    name: str
    query: str
    enabled: bool = True
    max_results: int = 20
    sort_by: str = "submittedDate"
    sort_order: str = "descending"
    category: str = "Research Papers"
    update_interval: int = 3600  # 1 hour in seconds
    last_fetch: Optional[datetime] = None

    def to_dict(self) -> Dict:
        """Convert source to dictionary for serialization."""
        data = asdict(self)
        if self.last_fetch:
            data["last_fetch"] = self.last_fetch.isoformat()
        return data

    @classmethod
    def from_dict(cls, data: Dict) -> "ArXivSource":
        """Create ArXivSource from dictionary."""
        source = cls(
            name=data["name"],
            query=data["query"],
            enabled=data.get("enabled", True),
            max_results=data.get("max_results", 20),
            sort_by=data.get("sort_by", "submittedDate"),
            sort_order=data.get("sort_order", "descending"),
            category=data.get("category", "Research Papers"),
            update_interval=data.get("update_interval", 3600),
        )

        if data.get("last_fetch"):
            source.last_fetch = datetime.fromisoformat(data["last_fetch"])

        return source


@dataclass
class ArXivPaper:
    """Represents an ArXiv research paper."""

    title: str
    url: str
    source: str
    category: str
    summary: str
    published_at: Optional[str] = None
    content: Optional[str] = None
    api_data: Optional[Dict] = None

    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization."""
        return asdict(self)


class ArXivCollector(BaseCollector):
    """ArXiv research papers collector service."""

    def __init__(self, name: str = "ArXiv Collector"):
        super().__init__(name=name)

        self.sources = []
        self.papers_cache = {}  # Cache for deduplication
        self.arxiv_client = None

        # Load default ArXiv sources
        self.load_default_sources()
        self.initialize_arxiv_client()

    def initialize_arxiv_client(self):
        """Initialize ArXiv client."""
        try:
            # ArXiv doesn't require an API key
            self.arxiv_client = True  # Just mark as available
            logger.info("ArXiv client available")
        except Exception as e:
            logger.error(f"Error initializing ArXiv client: {e}")

    def is_available(self) -> bool:
        """Check if the collector is available and ready to use."""
        return DEPENDENCIES_AVAILABLE and self.arxiv_client

    def load_default_sources(self):
        """Load default ArXiv sources."""
        default_sources = [
            ArXivSource(
                name="ArXiv AI Papers",
                query="AI OR artificial intelligence OR machine learning",
                max_results=20,
                sort_by="submittedDate",
                sort_order="descending",
                category="Research Papers",
            ),
            ArXivSource(
                name="ArXiv Computer Vision",
                query="computer vision OR image recognition",
                max_results=15,
                sort_by="submittedDate",
                sort_order="descending",
                category="Computer Vision",
            ),
            ArXivSource(
                name="ArXiv NLP Papers",
                query="natural language processing OR NLP OR transformers",
                max_results=15,
                sort_by="submittedDate",
                sort_order="descending",
                category="Natural Language Processing",
            ),
            ArXivSource(
                name="ArXiv Robotics",
                query="robotics OR autonomous systems",
                max_results=10,
                sort_by="submittedDate",
                sort_order="descending",
                category="Robotics",
            ),
        ]

        self.sources = default_sources
        logger.info(f"Loaded {len(default_sources)} ArXiv sources")

    def should_update_source(self, source: ArXivSource) -> bool:
        """Check if a source should be updated based on its interval."""
        if not source.last_fetch:
            return True

        time_since_last = datetime.now() - source.last_fetch
        return time_since_last.total_seconds() >= source.update_interval

    def generate_content_hash(self, content: str) -> str:
        """Generate a hash for content deduplication."""
        return hashlib.md5(content.encode("utf-8")).hexdigest()

    def fetch_papers(self, source: ArXivSource) -> List[ArXivPaper]:
        """Fetch papers from ArXiv API."""
        if not self.arxiv_client:
            logger.warning("ArXiv client not available")
            return []

        try:
            # Create search query using the newer Client approach
            client = arxiv.Client()
            search = arxiv.Search(
                query=source.query,
                max_results=min(source.max_results, 20),  # Limit to avoid pagination issues
                sort_by=arxiv.SortCriterion.SubmittedDate,
                sort_order=arxiv.SortOrder.Descending,
            )

            papers = []
            for result in client.results(search):
                # Generate content hash for deduplication
                content = f"{result.title} {result.summary}"
                content_hash = self.generate_content_hash(content)

                # Check if we've seen this content before
                if content_hash in self.papers_cache:
                    continue

                # Create paper item
                paper = ArXivPaper(
                    title=result.title,
                    url=result.entry_id,
                    source=source.name,
                    category=source.category,
                    summary=result.summary,
                    published_at=(result.published.strftime("%Y-%m-%d") if result.published else None),
                    content=result.summary,
                    api_data={
                        "authors": [author.name for author in result.authors],
                        "pdf_url": result.pdf_url,
                        "journal_ref": result.journal_ref,
                        "doi": result.doi,
                    },
                )

                papers.append(paper)
                self.papers_cache[content_hash] = paper

                # Rate limiting
                time.sleep(0.1)

            logger.info(f"Fetched {len(papers)} papers from {source.name}")
            return papers

        except Exception as e:
            logger.error(f"Error fetching from ArXiv {source.name}: {e}")
            # Return any papers we managed to collect before the error
            if "papers" in locals() and papers:
                logger.info(f"Returning {len(papers)} papers collected before error from {source.name}")
                return papers
            return []

    def collect(self, **kwargs) -> List[Dict[str, Any]]:
        """Collect papers from all enabled ArXiv sources."""
        all_papers = []

        for source in self.sources:
            if not source.enabled:
                continue

            if not self.should_update_source(source) and not kwargs.get("force", False):
                logger.debug(f"Skipping source {source.name} - not due for update")
                continue

            try:
                papers = self.fetch_papers(source)
                source.last_fetch = datetime.now()

                for paper in papers:
                    paper_dict = paper.to_dict()
                    paper_dict["collector"] = self.name
                    paper_dict["collected_at"] = datetime.now().isoformat()
                    paper_dict["source_type"] = "arxiv"  # Add source type for compatibility
                    all_papers.append(paper_dict)

            except Exception as e:
                logger.error(f"Error collecting from source {source.name}: {e}")
                continue

        logger.info(f"Collected {len(all_papers)} total papers from {self.name}")
        return all_papers

    def get_source_status(self) -> List[Dict[str, Any]]:
        """Get status of all ArXiv sources."""
        return [source.to_dict() for source in self.sources]

    def add_source(self, source: ArXivSource):
        """Add a new ArXiv source to the collector."""
        self.sources.append(source)
        logger.info(f"Added ArXiv source: {source.name}")

    def remove_source(self, name: str):
        """Remove an ArXiv source by name."""
        self.sources = [s for s in self.sources if s.name != name]
        logger.info(f"Removed ArXiv source: {name}")

    def enable_source(self, name: str):
        """Enable an ArXiv source by name."""
        for source in self.sources:
            if source.name == name:
                source.enabled = True
                logger.info(f"Enabled ArXiv source: {name}")
                break

    def disable_source(self, name: str):
        """Disable an ArXiv source by name."""
        for source in self.sources:
            if source.name == name:
                source.enabled = False
                logger.info(f"Disabled ArXiv source: {name}")
                break

    def cleanup_cache(self):
        """Clean up old items from cache to prevent memory issues."""
        # Keep only the last 1000 items
        if len(self.papers_cache) > 1000:
            # Remove oldest items (simple approach: keep last 1000)
            cache_items = list(self.papers_cache.items())
            self.papers_cache = dict(cache_items[-1000:])
            logger.info("Cleaned up ArXiv cache, kept last 1000 items")


def create_arxiv_collector(name: str = "ArXiv Collector") -> ArXivCollector:
    """Factory function to create an ArXiv collector instance."""
    return ArXivCollector(name=name)


if __name__ == "__main__":
    # Test the ArXiv collector
    import logging

    # Set up logging
    logging.basicConfig(level=logging.INFO)

    # Create collector
    collector = create_arxiv_collector()

    if collector.is_available():
        print("✅ ArXiv Collector initialized successfully")

        # Test collection
        print("\n📊 Testing ArXiv collection...")
        results = collector.collect()

        print(f"✅ Collected {len(results)} papers")

        # Show sample items
        if results:
            print("\n📰 Sample papers:")
            for i, item in enumerate(results[:3], 1):
                print(f"  {i}. {item['title'][:60]}...")
                print(f"     Source: {item['source']}")
                print(f"     Category: {item['category']}")
                print()

        # Show source status
        print("\n🔍 Source Status:")
        for source in collector.get_source_status():
            status = "✅ Enabled" if source["enabled"] else "❌ Disabled"
            print(f"  {source['name']}: {status}")

    else:
        print("⚠️ ArXiv Collector not available - check dependencies")
