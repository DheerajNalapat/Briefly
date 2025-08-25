"""
Summarizer Service for Briefly Bot

This service provides a unified interface for creating TLDR summaries using
different LLM providers and output formats. It handles summarization strategy
selection, content processing, and result formatting.
"""

import logging
from typing import List, Dict, Any, Optional, Union
from datetime import datetime

from slackbot.summarizer.tldr_summarizer import create_tldr_summarizer, TLDRSummarizer
from slackbot.summarizer.models import DailyDigestTLDR, ArticleTLDR


logger = logging.getLogger(__name__)


class SummarizerService:
    """
    High-level service for creating TLDR summaries.

    This service provides a unified interface for summarizing content using
    different LLM providers and output formats.
    """

    def __init__(self, llm_provider: str = "openai", api_key: Optional[str] = None, model_name: Optional[str] = None):
        """
        Initialize the summarizer service.

        Args:
            llm_provider: LLM provider to use ('openai', 'gemini', 'auto')
            api_key: API key for the LLM provider
            model_name: Specific model name to use
        """
        self.llm_provider = llm_provider
        self.api_key = api_key
        self.model_name = model_name
        self.summarizer: Optional[TLDRSummarizer] = None

        logger.info(f"Initializing SummarizerService with provider: {llm_provider}")
        self._initialize_summarizer()

    def _initialize_summarizer(self) -> None:
        """Initialize the TLDR summarizer."""
        try:
            self.summarizer = create_tldr_summarizer(
                llm_provider=self.llm_provider, api_key=self.api_key, model_name=self.model_name
            )

            if self.summarizer and self.summarizer.is_available():
                logger.info(f"✅ Summarizer initialized successfully with {self.llm_provider}")
            else:
                logger.warning(f"⚠️ Summarizer not available with {self.llm_provider}")

        except Exception as e:
            logger.error(f"❌ Failed to initialize summarizer: {e}")
            self.summarizer = None

    def is_available(self) -> bool:
        """
        Check if the summarizer service is available.

        Returns:
            True if available, False otherwise
        """
        return self.summarizer is not None and self.summarizer.is_available()

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
            logger.info(f"📝 Creating TLDR for article: {article.get('title', 'Unknown')[:50]}...")

            tldr = self.summarizer.create_article_tldr(article, **kwargs)

            if tldr:
                logger.info(f"✅ TLDR created successfully for article")
                return tldr
            else:
                logger.warning(f"⚠️ Failed to create TLDR for article")
                return None

        except Exception as e:
            logger.error(f"❌ Error creating article TLDR: {e}")
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
            logger.info(f"📊 Creating daily digest TLDR for {len(articles)} articles")

            digest = self.summarizer.create_tldr_digest(articles, **kwargs)

            if digest:
                logger.info(f"✅ Daily digest TLDR created successfully")
                return digest
            else:
                logger.warning(f"⚠️ Failed to create daily digest TLDR")
                return None

        except Exception as e:
            logger.error(f"❌ Error creating daily digest TLDR: {e}")
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

        logger.info(f"📝 Batch summarizing {len(articles)} articles")

        results = []
        for i, article in enumerate(articles):
            try:
                logger.info(f"  Processing {i+1}/{len(articles)}: {article.get('title', 'Unknown')[:50]}...")

                tldr = self.create_article_tldr(article, **kwargs)
                results.append(tldr)

                if tldr:
                    logger.info(f"    ✅ Summary created using {self.get_provider_info()['provider']}")
                else:
                    logger.warning(f"    ⚠️ Summary creation failed")

            except Exception as e:
                logger.error(f"    ❌ Error processing article {i+1}: {e}")
                results.append(None)

        success_count = sum(1 for r in results if r is not None)
        logger.info(f"✅ Batch summarization complete: {success_count}/{len(articles)} successful")

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

        logger.info(f"🎯 Using summarization strategy: {strategy}")

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
            logger.error(f"❌ Unknown summarization strategy: {strategy}")
            return None

    def get_summarization_summary(self) -> Dict[str, Any]:
        """
        Get a summary of the summarizer service status.

        Returns:
            Dictionary with summarizer service summary
        """
        return {
            "service": "SummarizerService",
            "timestamp": datetime.now().isoformat(),
            "provider_info": self.get_provider_info(),
            "available": self.is_available(),
            "llm_provider": self.llm_provider,
            "model_name": self.model_name,
        }

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
        logger.info(f"🔄 Switching from {self.llm_provider} to {new_provider}")

        try:
            self.llm_provider = new_provider
            if new_api_key:
                self.api_key = new_api_key
            if new_model_name:
                self.model_name = new_model_name

            self._initialize_summarizer()

            if self.is_available():
                logger.info(f"✅ Successfully switched to {new_provider}")
                return True
            else:
                logger.error(f"❌ Failed to switch to {new_provider}")
                return False

        except Exception as e:
            logger.error(f"❌ Error switching providers: {e}")
            return False

    def is_healthy(self) -> bool:
        """
        Check if the summarizer service is healthy.

        Returns:
            True if healthy, False otherwise
        """
        return self.is_available()
