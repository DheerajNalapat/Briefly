import os
import sys
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional


# Add project root to path
# Handle both local and Lambda environments
if os.getenv("AWS_LAMBDA_FUNCTION_NAME"):
    # Lambda environment - slackbot is at /var/task
    sys.path.insert(0, "/var/task")
else:
    # Local environment - use project root
    project_root = Path(__file__).parent
    sys.path.insert(0, str(project_root))

# Import Briefly Bot services
from slackbot.services import AggregationService, ContentProcessingService, PublisherService
from slackbot.summarizer.models import SlackMessage
from slackbot.utils.ai_content_filter import FilteringConfig
from slackbot.utils.llm_content_filter import LLMFilteringConfig


def setup_logging(verbose: bool = False) -> None:
    """Set up logging configuration."""
    log_level = logging.DEBUG if verbose else logging.INFO

    # Check if running in AWS Lambda
    is_lambda = os.getenv("LAMBDA_ENV") is not None

    if is_lambda:
        # Lambda environment - only use console logging
        logging.basicConfig(
            level=log_level,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[logging.StreamHandler(sys.stdout)],
        )
    else:
        # Local environment - use both console and file logging
        logs_dir = Path("logs")
        logs_dir.mkdir(exist_ok=True)

        logging.basicConfig(
            level=log_level,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[
                logging.StreamHandler(sys.stdout),
                logging.FileHandler(logs_dir / f'briefly_bot_{datetime.now().strftime("%Y%m%d")}.log'),
            ],
        )

    # Set specific logger levels
    logging.getLogger("arxiv").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)

    logger = logging.getLogger(__name__)
    logger.info("Briefly Bot logging initialized")


def collect_news(aggregation_service: AggregationService, max_articles: int = 20) -> List[Dict[str, Any]]:
    """
    Collect news using the AggregationService.

    Args:
        aggregation_service: Aggregation service instance
        max_articles: Maximum number of articles to collect

    Returns:
        List of collected news articles
    """
    logger = logging.getLogger(__name__)

    try:
        logger.info("🔍 Starting news collection...")

        # Use the service to collect news with prioritized sources (NewsAPI → RSS → ArXiv)
        articles = aggregation_service.collect_prioritized(max_articles=max_articles)

        if not articles:
            logger.warning("⚠️ No articles collected")
            return []

        logger.info("✅ Successfully collected %s articles", len(articles))

        # Log sample articles
        for i, article in enumerate(articles[:3], 1):
            logger.info("  %s. %s...", i, article.get("title", "No title")[:60])
            logger.info("     Source: %s (%s)", article.get("source", "Unknown"), article.get("source_type", "unknown"))
            logger.info("     Category: %s", article.get("category", "Unknown"))

        return articles

    except Exception as e:
        logger.error("❌ Error during news collection: %s", e)
        return []


def create_tldr_summaries(
    content_processing_service: ContentProcessingService, articles: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    Create TLDR summaries using the ContentProcessingService.

    Args:
        content_processing_service: Content processing service instance
        articles: List of news articles

    Returns:
        List of TLDR summaries
    """
    logger = logging.getLogger(__name__)

    try:
        logger.info("🧠 Starting TLDR summarization...")

        if not content_processing_service.is_available():
            logger.error("❌ Content processing service not available")
            return []

        # Use the service to process and rank articles, then create summaries
        # First rerank articles to prioritize NewsAPI over ArXiv
        ranked_articles = content_processing_service.rerank_articles(articles, strategy="smart")

        # Create summaries with individual strategy
        summaries = content_processing_service.summarize_with_strategy(articles=ranked_articles, strategy="individual")

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


def create_slack_message(summaries: List[Dict[str, Any]]) -> SlackMessage:
    """
    Create a Slack message from TLDR summaries.

    Args:
        summaries: List of TLDR summaries

    Returns:
        Formatted Slack message
    """
    logger = logging.getLogger(__name__)

    try:
        logger.info("💬 Creating Slack message...")

        # Create message blocks
        blocks = [
            {"type": "header", "text": {"type": "plain_text", "text": "🚀 AI/ML News TLDR - Daily Digest"}},
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Today's AI/ML News Summary*\nCollected {len(summaries)} articles and created TLDR summaries.",
                },
            },
            {"type": "divider"},
        ]

        # Add summary blocks
        for i, summary in enumerate(summaries, 1):
            # Access dictionary keys directly
            title = summary.get("title", "Unknown Title")
            tldr_text = summary.get("tldr", "No summary available")
            url = summary.get("url", "#")
            source = summary.get("source", "Unknown Source")
            category = summary.get("category", "Unknown Category")

            blocks.append(
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*{i}. {title}*\n{tldr_text}\n\n📰 *Source:* {source} | 🏷️ *Category:* {category}\n<{url}|Read more>",
                    },
                }
            )

            if i < len(summaries):
                blocks.append({"type": "divider"})

        # Add footer
        blocks.append(
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": f"📊 *{len(summaries)}* articles summarized • Generated at {datetime.now().strftime('%H:%M:%S')}",
                    }
                ],
            }
        )

        # Create Slack message
        message = SlackMessage(
            text=f"🚀 AI/ML News TLDR - {len(summaries)} articles summarized", blocks=blocks, attachments=[]
        )

        logger.info("✅ Slack message created with %s blocks", len(blocks))
        return message

    except Exception as e:
        logger.error("❌ Error creating Slack message: %s", e)
        raise


def publish_to_channels(
    publisher_service: PublisherService, message: SlackMessage, channel: str, dry_run: bool = False
) -> bool:
    """
    Publish the Slack message using the PublisherService.

    Args:
        publisher_service: Publisher service instance
        message: Slack message to publish
        channel: Target Slack channel

    Returns:
        True if successful, False otherwise
    """
    logger = logging.getLogger(__name__)

    try:
        if dry_run:
            logger.info("🔍 DRY RUN: Would publish to Slack")
            logger.info("   Channel: %s", channel)
            logger.info("   Message blocks: %s", len(message.blocks))
            return True

        logger.info("📤 Publishing to Slack channel %s...", channel)

        # Use the service to publish the message
        result = publisher_service.publish_message(message=message, platform="slack", channel=channel)

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


def run_briefly_bot(
    dry_run: bool = False,
    max_articles: int = 20,
    channel: Optional[str] = None,
    llm_provider: str = "openai",
    strict_filtering: bool = False,
    use_llm_filtering: bool = True,
) -> bool:
    """
    Run the complete Briefly Bot flow.

    Args:
        dry_run: If True, don't publish to Slack
        max_articles: Maximum number of articles to process
        channel: Target Slack channel (uses env var if not specified)
        llm_provider: LLM provider to use ("openai" or "gemini")
        strict_filtering: If True, use strict AI/ML filtering
        use_llm_filtering: If True, use LLM-based filtering (recommended)

    Returns:
        True if successful, False otherwise
    """
    logger = logging.getLogger(__name__)

    try:
        logger.info("🚀 Starting Briefly Bot...")
        logger.info("=" * 60)

        # Step 1: Initialize services
        logger.info("🔧 Initializing services...")

        # Configure AI content filtering (fallback)
        filtering_config = FilteringConfig(
            min_relevance_score=0.4 if strict_filtering else 0.3,
            min_quality_score=0.3 if strict_filtering else 0.2,
            max_age_hours=48 if strict_filtering else 72,
            strict_mode=strict_filtering,
            recency_boost_enabled=True,
            source_quality_boost=True,
        )

        # Configure LLM filtering (primary)
        llm_filtering_config = LLMFilteringConfig(
            llm_provider=llm_provider,
            confidence_threshold=0.8 if strict_filtering else 0.75,  # Higher thresholds
            fallback_to_keywords=True,
            enable_batch_processing=True,
            batch_size=5,
        )

        logger.info("🔍 Filtering Configuration:")
        logger.info("   Use LLM Filtering: %s", use_llm_filtering)
        logger.info("   LLM Provider: %s", llm_provider)
        logger.info("   Confidence Threshold: %.1f", llm_filtering_config.confidence_threshold)
        logger.info("   Fallback to Keywords: %s", llm_filtering_config.fallback_to_keywords)
        logger.info("   Strict Mode: %s", strict_filtering)

        aggregation_service = AggregationService(
            filtering_config=filtering_config if not use_llm_filtering else None,
            llm_filtering_config=llm_filtering_config if use_llm_filtering else None,
        )
        if not aggregation_service.is_healthy():
            logger.error("❌ Failed to initialize AggregationService")
            return False

        content_processing_service = ContentProcessingService(llm_provider=llm_provider)
        if not content_processing_service.is_healthy():
            logger.error("❌ Failed to initialize ContentProcessingService with %s", llm_provider)
            return False

        publisher_service = PublisherService(default_platform="slack")
        if not publisher_service.is_healthy():
            if dry_run:
                logger.warning("⚠️ PublisherService not available - dry run will test collection and summarization only")
            else:
                logger.error("❌ Failed to initialize PublisherService")
                return False

        logger.info("✅ All services initialized successfully")

        # Step 2: Collect news
        logger.info("\n📰 Step 2: Collecting News")
        logger.info("-" * 40)

        articles = collect_news(aggregation_service, max_articles)
        if not articles:
            logger.error("❌ No articles collected - stopping")
            return False

        # Step 3: Create TLDR summaries
        logger.info("\n🧠 Step 3: Creating TLDR Summaries")
        logger.info("-" * 40)

        summaries = create_tldr_summaries(content_processing_service, articles)
        if not summaries:
            logger.error("❌ No summaries created - stopping")
            return False

        # Step 4: Create Slack message
        logger.info("\n💬 Step 4: Creating Slack Message")
        logger.info("-" * 40)

        message = create_slack_message(summaries)

        # Step 5: Publish to Slack
        logger.info("\n📤 Step 5: Publishing to Slack")
        logger.info("-" * 40)

        # Use provided channel or default from env
        target_channel = channel or os.getenv("SLACK_CHANNEL_ID")
        if not target_channel:
            logger.error("❌ No Slack channel specified")
            return False

        success = publish_to_channels(publisher_service, message, target_channel, dry_run)

        if success:
            logger.info("\n🎉 Briefly Bot completed successfully!")
            logger.info("📊 Summary:")
            logger.info("  • Articles collected: %s", len(articles))
            logger.info("  • TLDR summaries created: %s", len(summaries))
            if not dry_run:
                logger.info("  • Published to Slack: %s", target_channel)
            else:
                logger.info("  • Published to Slack: DRY RUN")
            return True
        else:
            logger.error("❌ Briefly Bot failed during Slack publishing")
            return False

    except Exception as e:
        logger.error("❌ Unexpected error in Briefly Bot: %s", e)
        import traceback

        traceback.print_exc()
        return False


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Lambda handler."""
    setup_logging(verbose=True)
    logger = logging.getLogger(__name__)
    logger.info("🚀 Starting Briefly Bot Lambda handler...")
    logger.info("=" * 60)
    logger.info("Event: %s", event)
    logger.info("Context: %s", context)
    logger.info("=" * 60)

    success = run_briefly_bot(
        dry_run=event.get("dry_run", False),
        max_articles=event.get("max_articles", 15),
        channel=event.get("channel", os.getenv("SLACK_CHANNEL_ID")),
        llm_provider=event.get("llm_provider", "openai"),
        strict_filtering=event.get("strict_filtering", True),  # Default to strict filtering for Lambda
        use_llm_filtering=event.get("use_llm_filtering", True),  # Default to LLM filtering for Lambda
    )
    if success:
        logger.info("🎉 Briefly Bot completed successfully!")
        return {"statusCode": 200, "body": "Briefly Bot completed successfully!"}
    else:
        logger.error("❌ Briefly Bot failed")
        return {"statusCode": 500, "body": "Briefly Bot failed"}
