#!/usr/bin/env python3
"""
Briefly Bot Server - Slack Event Listener

This server runs the Briefly Bot as a Slack app that responds to @Briefly mentions
and slash commands in Slack channels.

Usage:
    python server.py                    # Run the server
    python server.py --verbose         # Enable verbose logging
    python server.py --help            # Show help
"""

import os
import sys
import logging
import argparse
import signal
from datetime import datetime
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from slackbot.config import validate_config
from slackbot.slack.listener import create_slack_listener


def setup_logging(verbose: bool = False) -> None:
    """Set up logging configuration."""
    log_level = logging.DEBUG if verbose else logging.INFO

    # Create logs directory if it doesn't exist
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)

    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(logs_dir / f'briefly_server_{datetime.now().strftime("%Y%m%d")}.log'),
        ],
    )

    # Set specific logger levels
    logging.getLogger("arxiv").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)

    logger = logging.getLogger(__name__)
    logger.info("Briefly Bot Server logging initialized")


def signal_handler(signum, frame):
    """Handle shutdown signals gracefully."""
    logger = logging.getLogger(__name__)
    logger.info("🛑 Received shutdown signal (%s), stopping server...", signum)
    sys.exit(0)


def main():
    """Main server entry point."""
    parser = argparse.ArgumentParser(description="Briefly Bot Server - Slack Event Listener")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose logging")
    parser.add_argument("--dry-run", action="store_true", help="Test configuration without starting server")

    args = parser.parse_args()

    # Set up logging
    setup_logging(verbose=args.verbose)
    logger = logging.getLogger(__name__)

    # Set up signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    logger.info("🚀 Briefly Bot Server - Slack Event Listener")
    logger.info("=" * 60)
    logger.info("📅 Started at: %s", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    logger.info("🔧 Verbose logging: %s", "Yes" if args.verbose else "No")
    logger.info("🔧 Dry run: %s", "Yes" if args.dry_run else "No")
    logger.info("=" * 60)

    # Validate configuration
    logger.info("🔧 Validating configuration...")
    if not validate_config():
        logger.error("❌ Configuration validation failed")
        return 1

    logger.info("✅ Configuration validation passed")

    if args.dry_run:
        logger.info("🔍 DRY RUN: Configuration is valid, server would start successfully")
        return 0

    # Create and start the Slack listener
    logger.info("🔧 Initializing Slack event listener...")
    try:
        listener = create_slack_listener()

        if not listener.start():
            logger.error("❌ Failed to start Slack event listener")
            return 1

        logger.info("✅ Slack event listener started successfully")
        logger.info("🎉 Briefly Bot Server is now running!")
        logger.info("📱 The bot will respond to @Briefly mentions and /Briefly commands")
        logger.info("🛑 Press Ctrl+C to stop the server")

        # Keep the server running
        try:
            while True:
                import time

                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("🛑 Received keyboard interrupt, shutting down...")
            listener.stop()
            logger.info("✅ Server stopped gracefully")
            return 0

    except Exception as e:
        logger.error("❌ Unexpected error starting server: %s", e)
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
