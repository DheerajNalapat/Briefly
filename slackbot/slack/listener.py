"""
Slack event listener for handling @Briefly mentions.
"""

import logging
import asyncio
from typing import Optional
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

from slackbot.config import SLACK_CONFIG
from slackbot.processors import BrieflyNewsProcessor

logger = logging.getLogger(__name__)


class SlackEventListener:
    """Handles Slack events and mentions."""

    def __init__(self, bot_token: Optional[str] = None, app_token: Optional[str] = None):
        self.bot_token = bot_token or SLACK_CONFIG["bot_token"]
        self.app_token = app_token or SLACK_CONFIG["app_token"]

        # Initialize Slack app
        self.app = App(token=self.bot_token)
        self.handler = None

        # Initialize news processor
        self.news_processor = BrieflyNewsProcessor(llm_provider="openai")

        self._setup_event_handlers()

    def _setup_event_handlers(self):
        """Set up Slack event handlers."""

        @self.app.event("app_mention")
        def handle_app_mention(event, say, client):
            """Handle @Briefly mentions."""
            logger.info("Received app mention: %s", event)

            # Extract the mention text
            text = event.get("text", "")
            channel = event.get("channel")
            user = event.get("user")
            thread_ts = event.get("thread_ts")

            # Check if this is a @Briefly mention
            if "briefly" in text.lower():
                logger.info("Processing @Briefly mention from user %s in channel %s", user, channel)

                # Send immediate acknowledgment
                say(
                    text="🤖 Collecting the latest AI/ML news for you... This may take a moment.",
                    channel=channel,
                    thread_ts=thread_ts,
                )

                # Process the news collection asynchronously
                asyncio.create_task(self._process_briefly_request(channel, user, thread_ts))

    async def _process_briefly_request(self, channel: str, user: str, thread_ts: Optional[str] = None):
        """Process a @Briefly request asynchronously."""
        try:
            logger.info("🔄 Processing @Briefly request for user %s in channel %s", user, channel)

            # Initialize processor if not already done
            if not self.news_processor.is_healthy():
                if not self.news_processor.initialize_services():
                    await self._send_error_message(
                        channel, "Failed to initialize news processor. Please try again later.", thread_ts
                    )
                    return

            # Run the complete news processing flow
            result = self.news_processor.process_news_flow(max_articles=10, channel=channel, dry_run=False)

            if result["success"]:
                logger.info("🎉 Successfully processed @Briefly request for user %s", user)
            else:
                await self._send_error_message(
                    channel, f"Failed to process news: {result.get('error', 'Unknown error')}", thread_ts
                )

        except Exception as e:
            logger.error("❌ Error processing @Briefly request: %s", e)
            await self._send_error_message(channel, f"Sorry, I encountered an error: {str(e)}", thread_ts)

    async def _send_error_message(self, channel: str, message: str, thread_ts: Optional[str] = None):
        """Send an error message to Slack."""
        try:
            if thread_ts:
                self.app.client.chat_postMessage(channel=channel, text=f"❌ {message}", thread_ts=thread_ts)
            else:
                self.app.client.chat_postMessage(channel=channel, text=f"❌ {message}")
        except Exception as e:
            logger.error("Failed to send error message: %s", e)

    def start(self):
        """Start the Slack event listener."""
        if not self.app_token:
            logger.error("No app token provided. Cannot start Socket Mode handler.")
            return False

        try:
            self.handler = SocketModeHandler(self.app, self.app_token)
            logger.info("🚀 Starting Slack event listener...")
            self.handler.start()
            return True
        except Exception as e:
            logger.error("Failed to start Slack event listener: %s", e)
            return False

    def stop(self):
        """Stop the Slack event listener."""
        if self.handler:
            self.handler.close()
            logger.info("🛑 Slack event listener stopped")


def create_slack_listener(bot_token: Optional[str] = None, app_token: Optional[str] = None) -> SlackEventListener:
    """Factory function to create a Slack event listener."""
    return SlackEventListener(bot_token=bot_token, app_token=app_token)
