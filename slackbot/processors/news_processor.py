"""
Briefly News Processor - Core news processing flow.

This module contains the main news processing logic that can be used
by both the main.py script and the Slack server.
"""

import os
import logging
from typing import List, Dict, Any, Optional

from slackbot.services import AggregationService, ContentProcessingService, PublisherService
from slackbot.summarizer.models import SlackMessage
from slackbot.utils.create_slack_message import create_slack_message

logger = logging.getLogger(__name__)


class BrieflyNewsProcessor:
    """Main news processing class that handles the complete flow."""

    def __init__(self, llm_provider: str = "openai"):
        """
        Initialize the news processor.

        Args:
            llm_provider: LLM provider to use ("openai" or "gemini")
        """
        self.llm_provider = llm_provider
        self.aggregation_service = None
        self.content_processing_service = None
        self.publisher_service = None
        self._initialized = False

    def initialize_services(self) -> bool:
        """
        Initialize all required services.

        Returns:
            True if all services initialized successfully, False otherwise
        """
        try:
            logger.info("🔧 Initializing services...")

            # Initialize aggregation service
            self.aggregation_service = AggregationService()
            if not self.aggregation_service.is_healthy():
                logger.error("❌ Failed to initialize AggregationService")
                return False

            # Initialize content processing service
            self.content_processing_service = ContentProcessingService(llm_provider=self.llm_provider)
            if not self.content_processing_service.is_healthy():
                logger.error("❌ Failed to initialize ContentProcessingService with %s", self.llm_provider)
                return False

            # Initialize publisher service
            self.publisher_service = PublisherService(default_platform="slack")
            if not self.publisher_service.is_healthy():
                logger.error("❌ Failed to initialize PublisherService")
                return False

            self._initialized = True
            logger.info("✅ All services initialized successfully")
            return True

        except Exception as e:
            logger.error("❌ Error initializing services: %s", e)
            return False

    def collect_news(self, max_articles: int = 20) -> List[Dict[str, Any]]:
        """
        Collect news using the AggregationService.

        Args:
            max_articles: Maximum number of articles to collect

        Returns:
            List of collected news articles
        """
        if not self._initialized:
            logger.error("❌ Services not initialized. Call initialize_services() first.")
            return []

        try:
            logger.info("🔍 Starting news collection...")

            # Use the service to collect news with prioritized sources (NewsAPI → RSS → ArXiv)
            articles = self.aggregation_service.collect_prioritized(max_articles=max_articles)

            if not articles:
                logger.warning("⚠️ No articles collected")
                return []

            logger.info("✅ Successfully collected %s articles", len(articles))

            # Log sample articles
            for i, article in enumerate(articles[:3], 1):
                logger.info("  %s. %s...", i, article.get("title", "No title")[:60])
                logger.info(
                    "     Source: %s (%s)", article.get("source", "Unknown"), article.get("source_type", "unknown")
                )
                logger.info("     Category: %s", article.get("category", "Unknown"))

            return articles

        except Exception as e:
            logger.error("❌ Error during news collection: %s", e)
            return []

    def create_tldr_summaries(self, articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Create TLDR summaries using the ContentProcessingService.

        Args:
            articles: List of news articles

        Returns:
            List of TLDR summaries
        """
        if not self._initialized:
            logger.error("❌ Services not initialized. Call initialize_services() first.")
            return []

        try:
            logger.info("🧠 Starting TLDR summarization...")

            # Use the service to process and rank articles, then create summaries
            # First rerank articles to prioritize NewsAPI over ArXiv
            ranked_articles = self.content_processing_service.rerank_articles(articles, strategy="smart")

            # Create summaries with individual strategy
            summaries = self.content_processing_service.summarize_with_strategy(
                articles=ranked_articles, strategy="individual"
            )

            if not summaries:
                logger.warning("⚠️ No summaries created")
                return []

            # Convert to summary dicts for Slack formatting
            summary_dicts = []
            for i, summary in enumerate(summaries):
                if summary is None:
                    logger.warning("    ⚠️ Summary %s is None, skipping", i + 1)
                    continue

                try:
                    # Get the corresponding ranked article data for metadata
                    # Summaries are created from ranked_articles, so we need to use the same index
                    original_article = ranked_articles[i] if i < len(ranked_articles) else {}

                    summary_dict = {
                        "title": original_article.get("title", "Unknown"),
                        "source": original_article.get("source", "Unknown"),
                        "category": (
                            summary.categories[0] if summary.categories else "Unknown"
                        ),  # Use LLM-generated category
                        "url": original_article.get("url", ""),
                        "tldr": summary.tldr_text,
                        "key_points": summary.key_points,
                        "impact_level": summary.impact_level,
                        "reading_time": summary.reading_time,
                        "model_used": summary.model_used,
                    }
                    summary_dicts.append(summary_dict)

                except Exception as e:
                    logger.warning("    ⚠️ Error processing summary %s: %s", i + 1, e)
                    continue

            logger.info("✅ Successfully created %s TLDR summaries", len(summary_dicts))
            return summary_dicts

        except Exception as e:
            logger.error("❌ Error during TLDR summarization: %s", e)
            return []

    def create_slack_message(self, summaries: List[Dict[str, Any]]) -> SlackMessage:
        """
        Create a Slack message from TLDR summaries.

        Args:
            summaries: List of TLDR summaries

        Returns:
            Formatted Slack message
        """
        try:
            logger.info("💬 Creating Slack message...")
            return create_slack_message(summaries)
        except Exception as e:
            logger.error("❌ Error creating Slack message: %s", e)
            raise

    def publish_to_slack(self, message: SlackMessage, channel: str, dry_run: bool = False) -> bool:
        """
        Publish the Slack message using the PublisherService.

        Args:
            message: Slack message to publish
            channel: Target Slack channel
            dry_run: If True, don't actually publish

        Returns:
            True if successful, False otherwise
        """
        if not self._initialized:
            logger.error("❌ Services not initialized. Call initialize_services() first.")
            return False

        try:
            if dry_run:
                logger.info("🔍 DRY RUN: Would publish to Slack")
                logger.info("   Channel: %s", channel)
                logger.info("   Message blocks: %s", len(message.blocks))
                return True

            logger.info("📤 Publishing to Slack channel %s...", channel)

            # Use the service to publish the message
            result = self.publisher_service.publish_message(message=message, platform="slack", channel=channel)

            if result.get("success"):
                logger.info("🎉 Successfully published to Slack!")
                logger.info("📺 Channel: %s", channel)
                logger.info("🆔 Message ID: %s", result.get("message_id", "Unknown"))
                return True
            else:
                logger.error("❌ Failed to publish: %s", result.get("error", "Unknown error"))
                return False

        except Exception as e:
            logger.error("❌ Error publishing to Slack: %s", e)
            return False

    def process_news_flow(
        self, max_articles: int = 20, channel: Optional[str] = None, dry_run: bool = False
    ) -> Dict[str, Any]:
        """
        Run the complete news processing flow.

        Args:
            max_articles: Maximum number of articles to process
            channel: Target Slack channel (uses env var if not specified)
            dry_run: If True, don't publish to Slack

        Returns:
            Dictionary with processing results and metadata
        """
        logger.info("🚀 Starting Briefly News Processing...")
        logger.info("=" * 60)

        # Initialize services if not already done
        if not self._initialized:
            if not self.initialize_services():
                return {"success": False, "error": "Failed to initialize services"}

        # Step 1: Collect news
        logger.info("\n📰 Step 1: Collecting News")
        logger.info("-" * 40)

        articles = self.collect_news(max_articles)
        if not articles:
            return {"success": False, "error": "No articles collected"}

        # Step 2: Create TLDR summaries
        logger.info("\n🧠 Step 2: Creating TLDR Summaries")
        logger.info("-" * 40)

        summaries = self.create_tldr_summaries(articles)
        if not summaries:
            return {"success": False, "error": "No summaries created"}

        # Step 3: Create Slack message
        logger.info("\n💬 Step 3: Creating Slack Message")
        logger.info("-" * 40)

        try:
            message = self.create_slack_message(summaries)
        except Exception as e:
            return {"success": False, "error": f"Failed to create Slack message: {e}"}

        # Step 4: Publish to Slack
        logger.info("\n📤 Step 4: Publishing to Slack")
        logger.info("-" * 40)

        # Use provided channel or default from env
        target_channel = channel or os.getenv("SLACK_CHANNEL_ID")
        if not target_channel:
            return {"success": False, "error": "No Slack channel specified"}

        success = self.publish_to_slack(message, target_channel, dry_run)

        if success:
            logger.info("\n🎉 Briefly News Processing completed successfully!")
            logger.info("📊 Summary:")
            logger.info("  • Articles collected: %s", len(articles))
            logger.info("  • TLDR summaries created: %s", len(summaries))
            if not dry_run:
                logger.info("  • Published to Slack: %s", target_channel)
            else:
                logger.info("  • Published to Slack: DRY RUN")

            return {
                "success": True,
                "articles_count": len(articles),
                "summaries_count": len(summaries),
                "channel": target_channel,
                "dry_run": dry_run,
                "message": message,
            }
        else:
            return {"success": False, "error": "Failed during Slack publishing"}

    def is_healthy(self) -> bool:
        """
        Check if the processor is healthy and ready to use.

        Returns:
            True if healthy, False otherwise
        """
        return self._initialized and all(
            [
                self.aggregation_service and self.aggregation_service.is_healthy(),
                self.content_processing_service and self.content_processing_service.is_healthy(),
                self.publisher_service and self.publisher_service.is_healthy(),
            ]
        )
