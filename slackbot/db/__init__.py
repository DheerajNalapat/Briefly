"""
Database package for the News Finder Slack Bot.
"""

from .models import Base, NewsArticle, DailyDigest, DigestArticle
from .db_utils import (
    init_database,
    get_engine,
    get_session,
    get_db_session,
    test_database_connection,
    close_database_connection,
)

__all__ = [
    "Base",
    "NewsArticle",
    "DailyDigest",
    "DigestArticle",
    "init_database",
    "get_engine",
    "get_session",
    "get_db_session",
    "test_database_connection",
    "close_database_connection",
]
