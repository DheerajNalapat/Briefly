"""
Configuration for the News Finder Slack Bot.
"""

import os
from pathlib import Path
from typing import Optional

# Load environment variables from .env file
try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

# Base directory
BASE_DIR = Path(__file__).parent.parent

# Database configuration
DATABASE_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", "5432")),
    "database": os.getenv("DB_NAME", "news_finder"),
    "username": os.getenv("DB_USER", "news_finder_user"),
    "password": os.getenv("DB_PASSWORD", "news_finder_password"),
}

# Database URL for SQLAlchemy
DATABASE_URL = (
    f"postgresql://{DATABASE_CONFIG['username']}:{DATABASE_CONFIG['password']}"
    f"@{DATABASE_CONFIG['host']}:{DATABASE_CONFIG['port']}/{DATABASE_CONFIG['database']}"
)

# Slack configuration
SLACK_CONFIG = {
    "bot_token": os.getenv("SLACK_BOT_TOKEN"),
    "app_token": os.getenv("SLACK_APP_TOKEN"),
    "signing_secret": os.getenv("SLACK_SIGNING_SECRET"),
    "default_channel": os.getenv("SLACK_DEFAULT_CHANNEL", "#ai-updates"),
}

# OpenAI configuration
OPENAI_CONFIG = {
    "api_key": os.getenv("OPENAI_API_KEY"),
    "model": os.getenv("OPENAI_MODEL", "gpt-3.5-turbo"),
    "max_tokens": int(os.getenv("OPENAI_MAX_TOKENS", "1000")),
}

# Google AI configuration
GEMINI_CONFIG = {
    "api_key": os.getenv("GEMINI_API_KEY"),
    "model": os.getenv("GEMINI_MODEL", "gemini-1.5-flash"),
}

# Logging configuration
LOGGING_CONFIG = {
    "level": os.getenv("LOG_LEVEL", "INFO"),
    "file": os.getenv("LOG_FILE", str(BASE_DIR / "logs" / "news_finder_bot.log")),
    "console": os.getenv("LOG_CONSOLE", "true").lower() == "true",
}

# News collection configuration
NEWS_CONFIG = {
    "max_articles_per_source": int(os.getenv("MAX_ARTICLES_PER_SOURCE", "10")),
    "max_articles_per_digest": int(os.getenv("MAX_ARTICLES_PER_DIGEST", "20")),
    "digest_schedule_hour": int(os.getenv("DIGEST_SCHEDULE_HOUR", "9")),  # 9 AM
    "digest_schedule_minute": int(os.getenv("DIGEST_SCHEDULE_MINUTE", "0")),
}


# Validate required configuration
def validate_config() -> bool:
    """Validate that all required configuration is present."""
    required_vars = [
        "SLACK_BOT_TOKEN",
        "SLACK_APP_TOKEN",
        "SLACK_SIGNING_SECRET",
        "OPENAI_API_KEY",
    ]

    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)

    if missing_vars:
        print(f"Missing required environment variables: {', '.join(missing_vars)}")
        return False

    return True
