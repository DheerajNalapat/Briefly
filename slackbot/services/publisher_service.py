"""
Publisher Service for Briefly Bot

This service provides a unified interface for publishing messages to different
platforms (Slack, Discord, etc.). It handles message formatting, platform
selection, and delivery confirmation.
"""

import logging
from typing import List, Dict, Any, Optional, Union
from datetime import datetime

from slackbot.slack.publisher import create_slack_publisher, SlackPublisher
from slackbot.summarizer.models import SlackMessage


logger = logging.getLogger(__name__)


class PublisherService:
    """
    High-level service for publishing messages to different platforms.

    This service provides a unified interface for publishing content to
    various platforms with configurable formatting and delivery options.
    """

    def __init__(self, default_platform: str = "slack"):
        """
        Initialize the publisher service.

        Args:
            default_platform: Default platform to use for publishing
        """
        self.default_platform = default_platform
        self.publishers: Dict[str, Any] = {}

        logger.info(f"Initializing PublisherService with default platform: {default_platform}")
        self._initialize_publishers()

    def _initialize_publishers(self) -> None:
        """Initialize available publishers."""
        try:
            # Initialize Slack publisher
            slack_publisher = create_slack_publisher()
            if slack_publisher and slack_publisher.is_available():
                self.publishers["slack"] = slack_publisher
                logger.info("✅ Slack publisher initialized successfully")
            else:
                logger.warning("⚠️ Slack publisher not available")

            logger.info(f"📤 PublisherService initialized with {len(self.publishers)} publishers")

        except Exception as e:
            logger.error(f"❌ Failed to initialize publishers: {e}")
            raise

    def get_available_platforms(self) -> List[str]:
        """
        Get list of available publishing platforms.

        Returns:
            List of available platform names
        """
        return list(self.publishers.keys())

    def get_platform_status(self) -> Dict[str, Dict[str, Any]]:
        """
        Get status of all publishing platforms.

        Returns:
            Dictionary with platform status information
        """
        status = {}
        for name, publisher in self.publishers.items():
            if hasattr(publisher, "is_available"):
                status[name] = {"available": publisher.is_available(), "platform": name}
            else:
                status[name] = {"available": False, "platform": name, "error": "No availability check method"}
        return status

    def publish_message(
        self,
        message: Union[str, Dict[str, Any], SlackMessage],
        platform: Optional[str] = None,
        channel: Optional[str] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Publish a message to the specified platform.

        Args:
            message: Message content (string, dict, or SlackMessage object)
            platform: Platform to publish to (defaults to default_platform)
            channel: Channel/recipient for the message
            **kwargs: Additional arguments for publishing

        Returns:
            Dictionary with publishing results
        """
        platform = platform or self.default_platform

        if platform not in self.publishers:
            return {
                "success": False,
                "error": f"Platform '{platform}' not available. Available: {self.get_available_platforms()}",
                "platform": platform,
                "timestamp": datetime.now().isoformat(),
            }

        publisher = self.publishers[platform]

        if not publisher.is_available():
            return {
                "success": False,
                "error": f"Platform '{platform}' is not available",
                "platform": platform,
                "timestamp": datetime.now().isoformat(),
            }

        logger.info(f"📤 Publishing message to {platform}")

        try:
            # Handle different message formats
            if platform == "slack":
                result = self._publish_to_slack(publisher, message, channel, **kwargs)
            else:
                result = {
                    "success": False,
                    "error": f"Platform '{platform}' not yet implemented",
                    "platform": platform,
                    "timestamp": datetime.now().isoformat(),
                }

            if result.get("success"):
                logger.info(f"✅ Message published successfully to {platform}")
            else:
                logger.error(f"❌ Failed to publish to {platform}: {result.get('error')}")

            return result

        except Exception as e:
            logger.error(f"❌ Error publishing to {platform}: {e}")
            return {"success": False, "error": str(e), "platform": platform, "timestamp": datetime.now().isoformat()}

    def _publish_to_slack(
        self,
        publisher: SlackPublisher,
        message: Union[str, Dict[str, Any], SlackMessage],
        channel: Optional[str] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Publish a message to Slack.

        Args:
            publisher: Slack publisher instance
            message: Message content
            channel: Slack channel ID
            **kwargs: Additional arguments

        Returns:
            Dictionary with publishing results
        """
        try:
            # Convert message to SlackMessage if needed
            if isinstance(message, str):
                # Simple text message
                slack_message = SlackMessage(text=message, blocks=[], attachments=[])
            elif isinstance(message, dict):
                # Dictionary message - try to create SlackMessage
                slack_message = SlackMessage(**message)
            elif isinstance(message, SlackMessage):
                # Already a SlackMessage
                slack_message = message
            else:
                return {
                    "success": False,
                    "error": f"Unsupported message type: {type(message)}",
                    "platform": "slack",
                    "timestamp": datetime.now().isoformat(),
                }

            # Publish the message
            result = publisher.publish_tldr_message(slack_message)

            return {
                "success": True,
                "platform": "slack",
                "channel": channel,
                "message_id": getattr(result, "ts", None),
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            return {"success": False, "error": str(e), "platform": "slack", "timestamp": datetime.now().isoformat()}

    def publish_tldr_digest(
        self, digest_data: Dict[str, Any], platform: Optional[str] = None, channel: Optional[str] = None, **kwargs
    ) -> Dict[str, Any]:
        """
        Publish a TLDR digest to the specified platform.

        Args:
            digest_data: TLDR digest data
            platform: Platform to publish to
            channel: Channel/recipient for the message
            **kwargs: Additional arguments

        Returns:
            Dictionary with publishing results
        """
        logger.info(f"📊 Publishing TLDR digest to {platform or self.default_platform}")

        # Convert digest data to appropriate message format
        if platform == "slack" or not platform:
            # For Slack, we expect the digest to already be formatted
            message = digest_data
        else:
            # For other platforms, we might need to format differently
            message = self._format_message_for_platform(digest_data, platform)

        return self.publish_message(message, platform, channel, **kwargs)

    def _format_message_for_platform(self, content: Dict[str, Any], platform: str) -> Union[str, Dict[str, Any]]:
        """
        Format message content for a specific platform.

        Args:
            content: Raw message content
            platform: Target platform

        Returns:
            Formatted message for the platform
        """
        # This is a placeholder for future platform-specific formatting
        # For now, return the content as-is
        return content

    def publish_batch(
        self,
        messages: List[Union[str, Dict[str, Any], SlackMessage]],
        platform: Optional[str] = None,
        channel: Optional[str] = None,
        **kwargs,
    ) -> List[Dict[str, Any]]:
        """
        Publish multiple messages in batch.

        Args:
            messages: List of messages to publish
            platform: Platform to publish to
            channel: Channel/recipient for the messages
            **kwargs: Additional arguments

        Returns:
            List of publishing results for each message
        """
        logger.info(f"📦 Publishing batch of {len(messages)} messages to {platform or self.default_platform}")

        results = []
        for i, message in enumerate(messages):
            try:
                logger.info(f"  Publishing message {i+1}/{len(messages)}")
                result = self.publish_message(message, platform, channel, **kwargs)
                results.append(result)

                if result.get("success"):
                    logger.info(f"    ✅ Message {i+1} published successfully")
                else:
                    logger.error(f"    ❌ Message {i+1} failed: {result.get('error')}")

            except Exception as e:
                logger.error(f"    ❌ Error publishing message {i+1}: {e}")
                results.append(
                    {
                        "success": False,
                        "error": str(e),
                        "platform": platform or self.default_platform,
                        "timestamp": datetime.now().isoformat(),
                    }
                )

        success_count = sum(1 for r in results if r.get("success"))
        logger.info(f"✅ Batch publishing complete: {success_count}/{len(messages)} successful")

        return results

    def test_connection(self, platform: Optional[str] = None, channel: Optional[str] = None) -> Dict[str, Any]:
        """
        Test connection to a publishing platform.

        Args:
            platform: Platform to test (defaults to default_platform)
            channel: Channel to test with

        Returns:
            Dictionary with connection test results
        """
        platform = platform or self.default_platform

        if platform not in self.publishers:
            return {
                "success": False,
                "error": f"Platform '{platform}' not available",
                "platform": platform,
                "timestamp": datetime.now().isoformat(),
            }

        publisher = self.publishers[platform]

        try:
            if hasattr(publisher, "test_connection"):
                result = publisher.test_connection()
                return {
                    "success": True,
                    "platform": platform,
                    "connection_test": result,
                    "timestamp": datetime.now().isoformat(),
                }
            else:
                # Basic availability check
                is_available = publisher.is_available() if hasattr(publisher, "is_available") else False
                return {
                    "success": is_available,
                    "platform": platform,
                    "connection_test": {"available": is_available},
                    "timestamp": datetime.now().isoformat(),
                }

        except Exception as e:
            return {"success": False, "error": str(e), "platform": platform, "timestamp": datetime.now().isoformat()}

    def get_publishing_summary(self) -> Dict[str, Any]:
        """
        Get a summary of the publisher service status.

        Returns:
            Dictionary with publisher service summary
        """
        return {
            "service": "PublisherService",
            "timestamp": datetime.now().isoformat(),
            "default_platform": self.default_platform,
            "available_platforms": self.get_available_platforms(),
            "platform_status": self.get_platform_status(),
        }

    def is_healthy(self) -> bool:
        """
        Check if the publisher service is healthy.

        Returns:
            True if healthy, False otherwise
        """
        if not self.publishers:
            return False

        # Check if at least one platform is available
        return any(
            publisher.is_available() for publisher in self.publishers.values() if hasattr(publisher, "is_available")
        )

    def add_publisher(self, name: str, publisher: Any) -> None:
        """
        Add a custom publisher to the service.

        Args:
            name: Name for the publisher
            publisher: Publisher instance
        """
        if name in self.publishers:
            logger.warning(f"⚠️ Publisher '{name}' already exists, replacing")

        self.publishers[name] = publisher
        logger.info(f"✅ Added publisher '{name}' to PublisherService")

    def remove_publisher(self, name: str) -> bool:
        """
        Remove a publisher from the service.

        Args:
            name: Name of the publisher to remove

        Returns:
            True if removed, False if not found
        """
        if name in self.publishers:
            del self.publishers[name]
            logger.info(f"✅ Removed publisher '{name}' from PublisherService")
            return True
        return False
