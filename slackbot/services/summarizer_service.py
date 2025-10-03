"""
Content Processing Service for Briefly Bot

This service provides a unified interface for content processing including
TLDR summarization, intelligent reranking, and content optimization.
It handles summarization strategy selection, content processing, and result formatting.
"""

import logging
from typing import List, Dict, Any, Optional, Union
from datetime import datetime

from slackbot.summarizer.tldr_summarizer import create_tldr_summarizer, TLDRSummarizer
from slackbot.summarizer.models import DailyDigestTLDR, ArticleTLDR
from slackbot.utils.reranker import ArticleReranker, RankingConfig, create_article_reranker


logger = logging.getLogger(__name__)


class ContentProcessingService:
    """
    High-level service for content processing including TLDR summarization and intelligent reranking.

    This service provides a unified interface for content processing using
    different LLM providers, output formats, and ranking strategies.
    """

    def __init__(
        self,
        llm_provider: str = "openai",
        api_key: Optional[str] = None,
        model_name: Optional[str] = None,
        ranking_config: Optional[RankingConfig] = None,
    ):
        """
        Initialize the content processing service.

        Args:
            llm_provider: LLM provider to use ('openai', 'gemini', 'auto')
            api_key: API key for the LLM provider
            model_name: Specific model name to use
            ranking_config: Configuration for article ranking
        """
        self.llm_provider = llm_provider
        self.api_key = api_key
        self.model_name = model_name
        self.summarizer: Optional[TLDRSummarizer] = None
        self.reranker: Optional[ArticleReranker] = None

        logger.info("Initializing ContentProcessingService with provider: %s", llm_provider)
        self._initialize_summarizer()
        self._initialize_reranker(ranking_config)

    def _initialize_summarizer(self) -> None:
        """Initialize the TLDR summarizer."""
        try:
            self.summarizer = create_tldr_summarizer(
                llm_provider=self.llm_provider, api_key=self.api_key, model_name=self.model_name
            )

            if self.summarizer and self.summarizer.is_available():
                logger.info("✅ Summarizer initialized successfully with %s", self.llm_provider)
            else:
                logger.warning("⚠️ Summarizer not available with %s", self.llm_provider)

        except Exception as e:
            logger.error("❌ Failed to initialize summarizer: %s", e)
            self.summarizer = None

    def _initialize_reranker(self, ranking_config: Optional[RankingConfig] = None) -> None:
        """Initialize the article reranker."""
        try:
            self.reranker = create_article_reranker(ranking_config)
            logger.info("✅ Article reranker initialized successfully")
        except Exception as e:
            logger.error("❌ Failed to initialize reranker: %s", e)
            self.reranker = None

    def is_available(self) -> bool:
        """
        Check if the content processing service is available.

        Returns:
            True if available, False otherwise
        """
        return self.summarizer is not None and self.summarizer.is_available()

    def is_reranker_available(self) -> bool:
        """
        Check if the reranker is available.

        Returns:
            True if available, False otherwise
        """
        return self.reranker is not None

    def get_provider_info(self) -> Dict[str, Any]:
        """
        Get information about the current LLM provider.

        Returns:
            Dictionary with provider information
        """
        if not self.summarizer:
            return {"provider": "none", "available": False, "model": None}

        return {
            "provider": self.llm_provider,
            "available": self.summarizer.is_available(),
            "model": getattr(self.summarizer, "model_name", None),
        }

    def create_article_tldr(self, article: Dict[str, Any], **kwargs) -> Optional[ArticleTLDR]:
        """
        Create a TLDR summary for a single article.

        Args:
            article: Article data dictionary
            **kwargs: Additional arguments for summarization

        Returns:
            ArticleTLDR object if successful, None otherwise
        """
        if not self.is_available():
            logger.error("❌ Summarizer service not available")
            return None

        try:
            logger.info("📝 Creating TLDR for article: %s...", article.get("title", "Unknown")[:50])

            tldr = self.summarizer.create_article_tldr(article, **kwargs)

            if tldr:
                logger.info("✅ TLDR created successfully for article")
                return tldr
            else:
                logger.warning("⚠️ Failed to create TLDR for article")
                return None

        except Exception as e:
            logger.error("❌ Error creating article TLDR: %s", e)
            return None

    def create_daily_digest_tldr(self, articles: List[Dict[str, Any]], **kwargs) -> Optional[DailyDigestTLDR]:
        """
        Create a TLDR summary for a daily digest of articles.

        Args:
            articles: List of article data dictionaries
            **kwargs: Additional arguments for summarization

        Returns:
            DailyDigestTLDR object if successful, None otherwise
        """
        if not self.is_available():
            logger.error("❌ Summarizer service not available")
            return None

        if not articles:
            logger.warning("⚠️ No articles provided for daily digest")
            return None

        try:
            logger.info("📊 Creating daily digest TLDR for %s articles", len(articles))

            digest = self.summarizer.create_tldr_digest(articles, **kwargs)

            if digest:
                logger.info("✅ Daily digest TLDR created successfully")
                return digest
            else:
                logger.warning("⚠️ Failed to create daily digest TLDR")
                return None

        except Exception as e:
            logger.error("❌ Error creating daily digest TLDR: %s", e)
            return None

    def batch_summarize_articles(
        self, articles: List[Dict[str, Any]], max_concurrent: int = 3, **kwargs
    ) -> List[Optional[ArticleTLDR]]:
        """
        Create TLDR summaries for multiple articles in batches.

        Args:
            articles: List of article data dictionaries
            max_concurrent: Maximum concurrent summarization operations
            **kwargs: Additional arguments for summarization

        Returns:
            List of ArticleTLDR objects (None for failed summaries)
        """
        if not self.is_available():
            logger.error("❌ Summarizer service not available")
            return [None] * len(articles)

        if not articles:
            logger.warning("⚠️ No articles provided for batch summarization")
            return []

        logger.info("📝 Batch summarizing %s articles", len(articles))

        results = []
        for i, article in enumerate(articles):
            try:
                logger.info("  Processing %s/%s: %s...", i + 1, len(articles), article.get("title", "Unknown")[:50])

                tldr = self.create_article_tldr(article, **kwargs)
                results.append(tldr)

                if tldr:
                    logger.info("    ✅ Summary created using %s", self.get_provider_info()["provider"])
                else:
                    logger.warning("    ⚠️ Summary creation failed")

            except Exception as e:
                logger.error("    ❌ Error processing article %s: %s", i + 1, e)
                results.append(None)

        success_count = sum(1 for r in results if r is not None)
        logger.info("✅ Batch summarization complete: %s/%s successful", success_count, len(articles))

        return results

    def summarize_with_strategy(
        self, articles: List[Dict[str, Any]], strategy: str = "individual", **kwargs
    ) -> Union[List[ArticleTLDR], DailyDigestTLDR, None]:
        """
        Summarize articles using a specified strategy.

        Args:
            articles: List of article data dictionaries
            strategy: Summarization strategy ('individual', 'digest', 'hybrid')
            **kwargs: Additional arguments for summarization

        Returns:
            Summarization results based on strategy
        """
        if not self.is_available():
            logger.error("❌ Summarizer service not available")
            return None

        logger.info("🎯 Using summarization strategy: %s", strategy)

        if strategy == "individual":
            return self.batch_summarize_articles(articles, **kwargs)

        elif strategy == "digest":
            return self.create_daily_digest_tldr(articles, **kwargs)

        elif strategy == "hybrid":
            # Create both individual summaries and a digest
            individual_summaries = self.batch_summarize_articles(articles, **kwargs)
            digest_summary = self.create_daily_digest_tldr(articles, **kwargs)

            return {"individual": individual_summaries, "digest": digest_summary}

        else:
            logger.error("❌ Unknown summarization strategy: %s", strategy)
            return None

    def get_summarization_summary(self) -> Dict[str, Any]:
        """
        Get a summary of the summarizer service status.

        Returns:
            Dictionary with summarizer service summary
        """
        return {
            "service": "ContentProcessingService",
            "timestamp": datetime.now().isoformat(),
            "provider_info": self.get_provider_info(),
            "available": self.is_available(),
            "reranker_available": self.is_reranker_available(),
            "llm_provider": self.llm_provider,
            "model_name": self.model_name,
        }

    def rerank_articles(self, articles: List[Dict[str, Any]], strategy: str = "smart") -> List[Dict[str, Any]]:
        """
        Rerank articles using the integrated reranker.

        Args:
            articles: List of article dictionaries
            strategy: Ranking strategy ('smart', 'source_priority', 'recency', 'custom')

        Returns:
            Reranked list of articles
        """
        if not self.is_reranker_available():
            logger.warning("⚠️ Reranker not available, returning original order")
            return articles

        if not articles:
            logger.warning("⚠️ No articles provided for reranking")
            return articles

        try:
            logger.info("🔄 Reranking %s articles using strategy: %s", len(articles), strategy)
            reranked = self.reranker.rerank_articles(articles, strategy=strategy)

            # Log ranking summary
            if reranked:
                summary = self.reranker.get_ranking_summary(reranked)
                logger.info("📊 Reranking complete. Top source: %s", reranked[0].get("source_type", "unknown"))

                # Log source distribution
                source_dist = summary.get("source_distribution", {})
                for source_type, count in source_dist.items():
                    logger.info("  %s: %s articles", source_type, count)

            return reranked

        except Exception as e:
            logger.error("❌ Error during reranking: %s", e)
            return articles

    def process_and_rank_articles(
        self, articles: List[Dict[str, Any]], ranking_strategy: str = "smart", **kwargs
    ) -> List[Dict[str, Any]]:
        """
        Process articles with both reranking and summarization.

        Args:
            articles: List of article dictionaries
            ranking_strategy: Strategy for reranking
            **kwargs: Additional arguments for summarization

        Returns:
            Processed and ranked articles
        """
        if not articles:
            return []

        logger.info("🎯 Processing and ranking %s articles", len(articles))

        # Step 1: Rerank articles
        ranked_articles = self.rerank_articles(articles, strategy=ranking_strategy)

        # Step 2: Create summaries (if requested)
        if kwargs.get("create_summaries", True):
            summaries = self.batch_summarize_articles(ranked_articles, **kwargs)

            # Merge summaries back with articles
            for i, summary in enumerate(summaries):
                if summary and i < len(ranked_articles):
                    ranked_articles[i]["tldr_summary"] = summary

        return ranked_articles

    def switch_provider(
        self, new_provider: str, new_api_key: Optional[str] = None, new_model_name: Optional[str] = None
    ) -> bool:
        """
        Switch to a different LLM provider.

        Args:
            new_provider: New LLM provider to use
            new_api_key: New API key for the provider
            new_model_name: New model name to use

        Returns:
            True if switch successful, False otherwise
        """
        logger.info("🔄 Switching from %s to %s", self.llm_provider, new_provider)

        try:
            self.llm_provider = new_provider
            if new_api_key:
                self.api_key = new_api_key
            if new_model_name:
                self.model_name = new_model_name

            self._initialize_summarizer()

            if self.is_available():
                logger.info("✅ Successfully switched to %s", new_provider)
                return True
            else:
                logger.error("❌ Failed to switch to %s", new_provider)
                return False

        except Exception as e:
            logger.error("❌ Error switching providers: %s", e)
            return False

    def is_healthy(self) -> bool:
        """
        Check if the content processing service is healthy.

        Returns:
            True if healthy, False otherwise
        """
        return self.is_available() and self.is_reranker_available()
