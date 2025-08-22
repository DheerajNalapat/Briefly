"""Slack publisher for sending TLDR news summaries to Slack channels."""

import os
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime

try:
    from slack_bolt import App
    from slack_bolt.adapter.socket_mode import SocketModeHandler
    from slack_sdk.errors import SlackApiError
except ImportError:
    logging.error("slack-bolt not available. Install with: pip install slack-bolt")
    App = None
    SocketModeHandler = None
    SlackApiError = None

from slackbot.config import SLACK_CONFIG
from slackbot.summarizer.models import SlackMessage

logger = logging.getLogger(__name__)


class SlackPublisher:
    """Publishes TLDR news summaries to Slack channels."""

    def __init__(
        self, bot_token: Optional[str] = None, app_token: Optional[str] = None
    ):
        self.bot_token = bot_token or SLACK_CONFIG["bot_token"]
        self.app_token = app_token or SLACK_CONFIG["app_token"]
        self.default_channel = SLACK_CONFIG["default_channel"]
        self.app = None
        self.client = None

        if not self.bot_token:
            logger.error("No Slack bot token provided. Publisher will not work.")
            return

        try:
            self.app = App(token=self.bot_token)
            self.client = self.app.client
            logger.info("Slack publisher initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Slack app: {e}")
            self.app = None
            self.client = None

    def is_available(self) -> bool:
        return self.client is not None and self.bot_token is not None

    def publish_tldr_message(
        self,
        slack_message: SlackMessage,
        channel: Optional[str] = None,
        thread_ts: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Publish a TLDR message to Slack."""
        if not self.is_available():
            error_msg = (
                "Slack publisher not available - check bot token and configuration"
            )
            logger.error(error_msg)
            return {"error": error_msg, "success": False}

        target_channel = channel or self.default_channel

        try:
            payload = {
                "channel": target_channel,
                "text": slack_message.text,
                "blocks": slack_message.blocks,
                "attachments": slack_message.attachments,
            }

            if thread_ts:
                payload["thread_ts"] = thread_ts

            response = self.client.chat_postMessage(**payload)

            if response["ok"]:
                logger.info(f"TLDR message published to {target_channel}")
                return {
                    "success": True,
                    "channel": target_channel,
                    "ts": response["ts"],
                    "message_id": response.get("message", {}).get("client_msg_id"),
                    "response": response,
                }
            else:
                error_msg = f"Failed to publish message: {response.get('error', 'Unknown error')}"
                logger.error(error_msg)
                return {"error": error_msg, "success": False}

        except SlackApiError as e:
            error_msg = f"Slack API error: {e.response['error']}"
            logger.error(error_msg)
            return {"error": error_msg, "success": False, "slack_error": e.response}

        except Exception as e:
            error_msg = f"Unexpected error publishing message: {e}"
            logger.error(error_msg)
            return {"error": error_msg, "success": False}

    def test_connection(self) -> Dict[str, Any]:
        """Test the Slack connection and get basic info."""
        if not self.is_available():
            return {"success": False, "error": "Publisher not available"}

        try:
            # Test auth with auth.test endpoint
            auth_response = self.client.auth_test()

            if auth_response["ok"]:
                return {
                    "success": True,
                    "bot_team_name": auth_response.get("team"),
                    "bot_user_id": auth_response.get("user_id"),
                    "bot_team_id": auth_response.get("team_id"),
                    "bot_user_name": auth_response.get("user"),
                    "response": auth_response,
                }
            else:
                return {
                    "success": False,
                    "error": f"Auth test failed: {auth_response.get('error', 'Unknown error')}",
                    "response": auth_response,
                }

        except SlackApiError as e:
            return {
                "success": False,
                "error": f"Slack API error: {e.response['error']}",
                "slack_error": e.response,
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Unexpected error: {e}",
            }

    def get_channel_info(self, channel: str) -> Dict[str, Any]:
        """Get information about a Slack channel."""
        if not self.is_available():
            return {"success": False, "error": "Publisher not available"}

        try:
            # Try to get channel info
            if channel.startswith("#"):
                channel = channel[1:]  # Remove # prefix

            # First try to get by name
            try:
                response = self.client.conversations_info(channel=channel)
            except SlackApiError as e:
                if e.response["error"] == "channel_not_found":
                    # Try to get by ID
                    response = self.client.conversations_info(channel=channel)
                else:
                    raise e

            if response["ok"]:
                channel_info = response["channel"]
                return {
                    "success": True,
                    "channel_id": channel_info.get("id"),
                    "channel_name": channel_info.get("name"),
                    "member_count": channel_info.get("num_members", 0),
                    "topic": channel_info.get("topic", {}).get("value", "No topic set"),
                    "purpose": channel_info.get("purpose", {}).get(
                        "value", "No purpose set"
                    ),
                    "is_private": channel_info.get("is_private", False),
                    "is_archived": channel_info.get("is_archived", False),
                    "response": response,
                }
            else:
                return {
                    "success": False,
                    "error": f"Failed to get channel info: {response.get('error', 'Unknown error')}",
                    "response": response,
                }

        except SlackApiError as e:
            return {
                "success": False,
                "error": f"Slack API error: {e.response['error']}",
                "slack_error": e.response,
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Unexpected error: {e}",
            }


def create_slack_publisher(
    bot_token: Optional[str] = None, app_token: Optional[str] = None
) -> SlackPublisher:
    """Factory function to create a Slack publisher instance."""
    return SlackPublisher(bot_token=bot_token, app_token=app_token)
