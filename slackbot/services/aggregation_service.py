"""
Aggregation Service for Briefly Bot

This service provides a unified interface for collecting news from multiple sources
using different collectors. It handles source selection, data normalization, and
result aggregation.
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

from slackbot.collectors.base_collector import BaseCollector, CollectorManager
from slackbot.collectors.arxiv_collector import create_arxiv_collector
from slackbot.collectors.newsapi_org_collector import create_newsapi_collector
from slackbot.collectors.rss_collector import create_rss_collector
from slackbot.utils.ai_content_filter import FilteringConfig, create_ai_content_filter
from slackbot.utils.llm_content_filter import LLMFilteringConfig, create_llm_content_filter


logger = logging.getLogger(__name__)


class AggregationService:
    """
    High-level service for aggregating news from multiple sources.

    This service provides a unified interface for collecting news using different
    collectors and normalizing the data into a common format.
    """

    def __init__(
        self,
        config_path: Optional[str] = None,
        filtering_config: Optional[FilteringConfig] = None,
        llm_filtering_config: Optional[LLMFilteringConfig] = None,
    ):
        """
        Initialize the aggregation service.

        Args:
            config_path: Path to the collector configuration file
            filtering_config: Configuration for AI content filtering
            llm_filtering_config: Configuration for LLM-based filtering
        """
        self.config_path = config_path or "slackbot/collectors/sources/api_sources_config.yaml"
        self.collectors: Dict[str, BaseCollector] = {}
        self.collector_manager: Optional[CollectorManager] = None

        # Initialize AI content filter (fallback)
        self.ai_filter = create_ai_content_filter(filtering_config)
        logger.info("AI Content Filter initialized with config: %s", filtering_config)

        # Initialize LLM content filter (primary)
        self.llm_filter = create_llm_content_filter(llm_filtering_config)
        logger.info("LLM Content Filter initialized with config: %s", llm_filtering_config)

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

            # Initialize RSS collector
            rss_collector = create_rss_collector()
            if rss_collector.is_available():
                self.collectors["rss"] = rss_collector
                logger.info("✅ RSS collector initialized successfully")
            else:
                logger.warning("⚠️ RSS collector not available")

            # Initialize collector manager for future extensibility
            self.collector_manager = CollectorManager()

            logger.info("📊 AggregationService initialized with %s collectors", len(self.collectors))

        except Exception as e:
            logger.error("❌ Failed to initialize collectors: %s", e)
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

        logger.info("🔍 Collecting from %s", source_name)

        try:
            articles = collector.collect(**kwargs)
            logger.info("✅ Collected %s articles from %s", len(articles), source_name)
            return articles

        except Exception as e:
            logger.error("❌ Failed to collect from %s: %s", source_name, e)
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
                logger.error("❌ Failed to collect from %s: %s", source_name, e)
                continue

        logger.info("📊 Total articles collected from all sources: %s", len(all_articles))
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
        logger.info("🎯 Collecting %s articles with balanced sources: %s", max_articles, balance_sources)

        if not balance_sources:
            # Simple collection without balancing
            return self.collect_from_all_sources(max_articles_per_source=max_articles, **kwargs)[:max_articles]

        # Balanced collection
        available_sources = self.get_available_collectors()
        if not available_sources:
            logger.warning("⚠️ No collectors available")
            return []

        # Calculate articles per source
        if max_articles is None:
            # No limit - collect all available articles
            articles_per_source = None
        else:
            articles_per_source = max_articles // len(available_sources)
        if max_articles is not None:
            remaining_articles = max_articles % len(available_sources)
        else:
            remaining_articles = 0

        balanced_articles = []

        for i, source_name in enumerate(available_sources):
            try:
                if articles_per_source is None:
                    # No limit - collect all available articles
                    source_limit = None
                else:
                    # Add extra articles to first few sources if there are remaining
                    source_limit = articles_per_source + (1 if i < remaining_articles else 0)

                source_kwargs = kwargs.copy()
                source_kwargs["max_articles"] = source_limit

                articles = self.collect_from_source(source_name, **source_kwargs)

                if source_limit is not None:
                    balanced_articles.extend(articles[:source_limit])
                    logger.info("📊 %s: collected %s articles", source_name, len(articles[:source_limit]))
                else:
                    balanced_articles.extend(articles)
                    logger.info("📊 %s: collected %s articles", source_name, len(articles))

            except Exception as e:
                logger.error("❌ Failed to collect from %s: %s", source_name, e)
                continue

        # Ensure we don't exceed max_articles if specified
        if max_articles is not None:
            final_articles = balanced_articles[:max_articles]
        else:
            final_articles = balanced_articles

        # Apply intelligent content filtering to all collected articles
        logger.info("🤖 Applying intelligent content filtering to %s articles...", len(final_articles))

        # Try LLM filtering first, fall back to keyword filtering if not available
        if self.llm_filter.is_available():
            logger.info("🧠 Using LLM-based filtering (primary method)")
            filtered_articles = self.llm_filter.filter_content_batch(final_articles)
        else:
            logger.info("🔍 Using keyword-based filtering (LLM not available)")
            filtered_articles = self.ai_filter.filter_and_score_content(final_articles)

        # Log filtering results
        if final_articles:
            filtering_summary = self._get_filtering_summary(len(final_articles), len(filtered_articles))
            logger.info("📊 Filtering Results:")
            logger.info("   Original: %s articles", filtering_summary["original_count"])
            logger.info("   Filtered: %s articles", filtering_summary["filtered_count"])
            logger.info("   Retention: %.1f%%", filtering_summary["retention_rate"] * 100)
            logger.info("   Filtered Out: %s articles", filtering_summary["filtered_out"])
            logger.info("   Method: %s", filtering_summary["method"])

        logger.info(
            "✅ Balanced collection complete: %s articles from %s sources",
            len(filtered_articles),
            len(available_sources),
        )
        return filtered_articles

    def collect_prioritized(self, max_articles: int = 20, **kwargs) -> List[Dict[str, Any]]:
        """
        Collect news with prioritized source ordering: NewsAPI first, then limited RSS, then max 3 ArXiv.

        Args:
            max_articles: Maximum total articles to collect
            **kwargs: Additional arguments for collection

        Returns:
            List of collected news items with prioritized representation
        """
        logger.info("🎯 Collecting %s articles with prioritized sources (NewsAPI → RSS → ArXiv)", max_articles)

        available_sources = self.get_available_collectors()
        if not available_sources:
            logger.warning("⚠️ No collectors available")
            return []

        prioritized_articles = []
        remaining_articles = max_articles

        # Priority 1: NewsAPI articles (get most of the articles)
        if "newsapi" in available_sources and remaining_articles > 0:
            try:
                # Allocate 70% of articles to NewsAPI, but at least 5
                newsapi_limit = max(5, int(remaining_articles * 0.7))
                newsapi_kwargs = kwargs.copy()
                newsapi_kwargs["max_articles"] = newsapi_limit
                newsapi_kwargs["force"] = True  # Force collection even if not due for update

                # Clear cache before collecting to ensure fresh articles
                newsapi_collector = self.collectors["newsapi"]
                if hasattr(newsapi_collector, "articles_cache"):
                    newsapi_collector.articles_cache.clear()
                    logger.info("🧹 Cleared NewsAPI cache for fresh collection")

                newsapi_articles = self.collect_from_source("newsapi", **newsapi_kwargs)
                prioritized_articles.extend(newsapi_articles)
                remaining_articles -= len(newsapi_articles)
                logger.info(
                    "📊 newsapi: collected %s articles (remaining: %s)", len(newsapi_articles), remaining_articles
                )

            except Exception as e:
                logger.error("❌ Failed to collect from newsapi: %s", e)

        # Priority 2: RSS articles (limited to remaining space)
        if "rss" in available_sources and remaining_articles > 0:
            try:
                # Allocate remaining articles to RSS, but cap at 5
                rss_limit = min(5, remaining_articles)
                rss_kwargs = kwargs.copy()
                rss_kwargs["max_articles"] = rss_limit
                rss_kwargs["force"] = True  # Force collection even if not due for update

                rss_articles = self.collect_from_source("rss", **rss_kwargs)
                prioritized_articles.extend(rss_articles)
                remaining_articles -= len(rss_articles)
                logger.info("📊 rss: collected %s articles (remaining: %s)", len(rss_articles), remaining_articles)

            except Exception as e:
                logger.error("❌ Failed to collect from rss: %s", e)

        # Priority 3: ArXiv papers (maximum 3)
        if "arxiv" in available_sources and remaining_articles > 0:
            try:
                # Cap ArXiv at 3 articles maximum
                arxiv_limit = min(3, remaining_articles)
                arxiv_kwargs = kwargs.copy()
                arxiv_kwargs["max_articles"] = arxiv_limit
                arxiv_kwargs["force"] = True  # Force collection even if not due for update

                arxiv_articles = self.collect_from_source("arxiv", **arxiv_kwargs)
                prioritized_articles.extend(arxiv_articles)
                remaining_articles -= len(arxiv_articles)
                logger.info("📊 arxiv: collected %s articles (remaining: %s)", len(arxiv_articles), remaining_articles)

            except Exception as e:
                logger.error("❌ Failed to collect from arxiv: %s", e)

        # Ensure we don't exceed max_articles
        final_articles = prioritized_articles[:max_articles]

        # Apply intelligent content filtering to all collected articles
        logger.info("🤖 Applying intelligent content filtering to %s articles...", len(final_articles))

        # Try LLM filtering first, fall back to keyword filtering if not available
        if self.llm_filter.is_available():
            logger.info("🧠 Using LLM-based filtering (primary method)")
            filtered_articles = self.llm_filter.filter_content_batch(final_articles)
        else:
            logger.info("🔍 Using keyword-based filtering (LLM not available)")
            filtered_articles = self.ai_filter.filter_and_score_content(final_articles)

        # Log filtering results
        if final_articles:
            filtering_summary = self._get_filtering_summary(len(final_articles), len(filtered_articles))
            logger.info("📊 Filtering Results:")
            logger.info("   Original: %s articles", filtering_summary["original_count"])
            logger.info("   Filtered: %s articles", filtering_summary["filtered_count"])
            logger.info("   Retention: %.1f%%", filtering_summary["retention_rate"] * 100)
            logger.info("   Filtered Out: %s articles", filtering_summary["filtered_out"])
            logger.info("   Method: %s", filtering_summary["method"])

        logger.info("✅ Prioritized collection complete: %s articles (NewsAPI → RSS → ArXiv)", len(filtered_articles))
        return filtered_articles

    def _get_filtering_summary(self, original_count: int, filtered_count: int) -> Dict[str, Any]:
        """Get filtering summary with method information."""
        method = "llm" if self.llm_filter.is_available() else "keyword"

        return {
            "original_count": original_count,
            "filtered_count": filtered_count,
            "retention_rate": filtered_count / original_count if original_count > 0 else 0,
            "filtered_out": original_count - filtered_count,
            "method": method,
            "timestamp": datetime.now().isoformat(),
        }

    def get_collection_service_summary(self) -> Dict[str, Any]:
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
            "ai_filter_config": {
                "min_relevance_score": self.ai_filter.config.min_relevance_score,
                "min_quality_score": self.ai_filter.config.min_quality_score,
                "max_age_hours": self.ai_filter.config.max_age_hours,
                "strict_mode": self.ai_filter.config.strict_mode,
            },
            "llm_filter_config": {
                "available": self.llm_filter.is_available(),
                "provider": self.llm_filter.config.llm_provider,
                "confidence_threshold": self.llm_filter.config.confidence_threshold,
                "fallback_available": self.llm_filter.fallback_filter is not None,
            },
        }

    def get_filtering_stats(self) -> Dict[str, Any]:
        """
        Get AI filtering statistics and configuration.

        Returns:
            Dictionary with filtering statistics
        """
        return {
            "ai_filter_available": True,
            "filtering_config": {
                "min_relevance_score": self.ai_filter.config.min_relevance_score,
                "min_quality_score": self.ai_filter.config.min_quality_score,
                "max_age_hours": self.ai_filter.config.max_age_hours,
                "strict_mode": self.ai_filter.config.strict_mode,
                "recency_boost_enabled": self.ai_filter.config.recency_boost_enabled,
                "source_quality_boost": self.ai_filter.config.source_quality_boost,
            },
            "keyword_counts": {
                "core_ai_keywords": len(self.ai_filter.core_ai_keywords),
                "negative_keywords": len(self.ai_filter.negative_keywords),
                "source_weights": len(self.ai_filter.source_weights),
            },
            "timestamp": datetime.now().isoformat(),
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
            logger.warning("⚠️ Collector '%s' already exists, replacing", name)

        self.collectors[name] = collector
        logger.info("✅ Added collector '%s' to AggregationService", name)

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
            logger.info("✅ Removed collector '%s' from AggregationService", name)
            return True
        return False
