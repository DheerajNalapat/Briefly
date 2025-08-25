"""
Aggregation Service for Briefly Bot

This service provides a unified interface for collecting news from multiple sources
using different collectors. It handles source selection, data normalization, and
result aggregation.
"""

import logging
from typing import List, Dict, Any, Optional, Union
from datetime import datetime
from pathlib import Path

from slackbot.collectors.base_collector import BaseCollector, CollectorManager
from slackbot.collectors.arxiv_collector import create_arxiv_collector
from slackbot.collectors.newsapi_org_collector import create_newsapi_collector


logger = logging.getLogger(__name__)


class AggregationService:
    """
    High-level service for aggregating news from multiple sources.

    This service provides a unified interface for collecting news using different
    collectors and normalizing the data into a common format.
    """

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the aggregation service.

        Args:
            config_path: Path to the collector configuration file
        """
        self.config_path = config_path or "slackbot/collectors/sources/api_sources_config.yaml"
        self.collectors: Dict[str, BaseCollector] = {}
        self.collector_manager: Optional[CollectorManager] = None

        logger.info("Initializing AggregationService")
        self._initialize_collectors()

    def _initialize_collectors(self) -> None:
        """Initialize available collectors."""
        try:
            # Initialize ArXiv collector
            arxiv_collector = create_arxiv_collector()
            if arxiv_collector.is_available():
                self.collectors["arxiv"] = arxiv_collector
                logger.info("✅ ArXiv collector initialized successfully")
            else:
                logger.warning("⚠️ ArXiv collector not available")

            # Initialize NewsAPI collector
            newsapi_collector = create_newsapi_collector()
            if newsapi_collector.is_available():
                self.collectors["newsapi"] = newsapi_collector
                logger.info("✅ NewsAPI collector initialized successfully")
            else:
                logger.warning("⚠️ NewsAPI collector not available")

            # Initialize collector manager for future extensibility
            self.collector_manager = CollectorManager()

            logger.info(f"📊 AggregationService initialized with {len(self.collectors)} collectors")

        except Exception as e:
            logger.error(f"❌ Failed to initialize collectors: {e}")
            raise

    def get_available_collectors(self) -> List[str]:
        """
        Get list of available collector names.

        Returns:
            List of available collector names
        """
        return list(self.collectors.keys())

    def get_collector_status(self) -> Dict[str, Dict[str, Any]]:
        """
        Get status of all collectors.

        Returns:
            Dictionary with collector status information
        """
        status = {}
        for name, collector in self.collectors.items():
            status[name] = {
                "enabled": collector.enabled,
                "available": collector.is_available(),
                "last_run": collector.last_run,
                "run_count": collector.run_count,
                "success_count": collector.success_count,
                "error_count": collector.error_count,
            }
        return status

    def collect_from_source(self, source_name: str, **kwargs) -> List[Dict[str, Any]]:
        """
        Collect news from a specific source.

        Args:
            source_name: Name of the collector to use
            **kwargs: Additional arguments for collection

        Returns:
            List of collected news items

        Raises:
            ValueError: If source is not available
        """
        if source_name not in self.collectors:
            raise ValueError(f"Collector '{source_name}' not available. Available: {self.get_available_collectors()}")

        collector = self.collectors[source_name]

        if not collector.is_available():
            raise ValueError(f"Collector '{source_name}' is not available")

        logger.info(f"🔍 Collecting from {source_name}")

        try:
            articles = collector.collect(**kwargs)
            logger.info(f"✅ Collected {len(articles)} articles from {source_name}")
            return articles

        except Exception as e:
            logger.error(f"❌ Failed to collect from {source_name}: {e}")
            collector.error_count += 1
            raise

    def collect_from_all_sources(self, max_articles_per_source: Optional[int] = None, **kwargs) -> List[Dict[str, Any]]:
        """
        Collect news from all available sources.

        Args:
            max_articles_per_source: Maximum articles per source
            **kwargs: Additional arguments for collection

        Returns:
            List of collected news items from all sources
        """
        all_articles = []

        for source_name in self.get_available_collectors():
            try:
                source_kwargs = kwargs.copy()
                if max_articles_per_source:
                    source_kwargs["max_articles"] = max_articles_per_source

                articles = self.collect_from_source(source_name, **source_kwargs)
                all_articles.extend(articles)

            except Exception as e:
                logger.error(f"❌ Failed to collect from {source_name}: {e}")
                continue

        logger.info(f"📊 Total articles collected from all sources: {len(all_articles)}")
        return all_articles

    def collect_balanced(self, max_articles: int = 20, balance_sources: bool = True, **kwargs) -> List[Dict[str, Any]]:
        """
        Collect news with balanced representation from different sources.

        Args:
            max_articles: Maximum total articles to collect
            balance_sources: Whether to balance articles across sources
            **kwargs: Additional arguments for collection

        Returns:
            List of collected news items with balanced representation
        """
        logger.info(f"🎯 Collecting {max_articles} articles with balanced sources: {balance_sources}")

        if not balance_sources:
            # Simple collection without balancing
            return self.collect_from_all_sources(max_articles_per_source=max_articles, **kwargs)[:max_articles]

        # Balanced collection
        available_sources = self.get_available_collectors()
        if not available_sources:
            logger.warning("⚠️ No collectors available")
            return []

        # Calculate articles per source
        articles_per_source = max_articles // len(available_sources)
        remaining_articles = max_articles % len(available_sources)

        balanced_articles = []

        for i, source_name in enumerate(available_sources):
            try:
                # Add extra articles to first few sources if there are remaining
                source_limit = articles_per_source + (1 if i < remaining_articles else 0)

                source_kwargs = kwargs.copy()
                source_kwargs["max_articles"] = source_limit

                articles = self.collect_from_source(source_name, **source_kwargs)
                balanced_articles.extend(articles[:source_limit])

                logger.info(f"📊 {source_name}: collected {len(articles[:source_limit])} articles")

            except Exception as e:
                logger.error(f"❌ Failed to collect from {source_name}: {e}")
                continue

        # Ensure we don't exceed max_articles
        final_articles = balanced_articles[:max_articles]

        logger.info(
            f"✅ Balanced collection complete: {len(final_articles)} articles from {len(available_sources)} sources"
        )
        return final_articles

    def get_collection_summary(self) -> Dict[str, Any]:
        """
        Get a summary of the collection service status.

        Returns:
            Dictionary with collection service summary
        """
        return {
            "service": "AggregationService",
            "timestamp": datetime.now().isoformat(),
            "available_collectors": self.get_available_collectors(),
            "collector_status": self.get_collector_status(),
            "config_path": self.config_path,
        }

    def is_healthy(self) -> bool:
        """
        Check if the aggregation service is healthy.

        Returns:
            True if healthy, False otherwise
        """
        if not self.collectors:
            return False

        # Check if at least one collector is available
        return any(collector.is_available() for collector in self.collectors.values())

    def add_collector(self, name: str, collector: BaseCollector) -> None:
        """
        Add a custom collector to the service.

        Args:
            name: Name for the collector
            collector: Collector instance
        """
        if name in self.collectors:
            logger.warning(f"⚠️ Collector '{name}' already exists, replacing")

        self.collectors[name] = collector
        logger.info(f"✅ Added collector '{name}' to AggregationService")

    def remove_collector(self, name: str) -> bool:
        """
        Remove a collector from the service.

        Args:
            name: Name of the collector to remove

        Returns:
            True if removed, False if not found
        """
        if name in self.collectors:
            del self.collectors[name]
            logger.info(f"✅ Removed collector '{name}' from AggregationService")
            return True
        return False
