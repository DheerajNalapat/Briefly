"""
Database models for the News Finder Slack Bot.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import (
    Column,
    String,
    Text,
    Integer,
    DateTime,
    Date,
    ForeignKey,
    Index,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

Base = declarative_base()


class NewsArticle(Base):
    """Model for news articles."""

    __tablename__ = "news_articles"

    id = Column(PostgresUUID(as_uuid=True), primary_key=True, default=uuid4)
    title = Column(String(500), nullable=False)
    url = Column(Text, unique=True, nullable=False)
    source = Column(String(100), nullable=False)
    source_type = Column(String(50), nullable=False)  # 'rss', 'api', 'scraper'
    content = Column(Text)
    summary = Column(Text)
    published_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    digest_articles = relationship("DigestArticle", back_populates="article")

    def __repr__(self):
        return f"<NewsArticle(id={self.id}, title='{self.title[:50]}...', source='{self.source}')>"


class DailyDigest(Base):
    """Model for daily news digests."""

    __tablename__ = "daily_digests"

    id = Column(PostgresUUID(as_uuid=True), primary_key=True, default=uuid4)
    digest_date = Column(Date, unique=True, nullable=False)
    summary = Column(Text, nullable=False)
    article_count = Column(Integer, nullable=False, default=0)
    slack_message_ts = Column(String(50))  # Slack message timestamp
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    digest_articles = relationship("DigestArticle", back_populates="digest")

    def __repr__(self):
        return f"<DailyDigest(id={self.id}, date={self.digest_date}, articles={self.article_count})>"


class DigestArticle(Base):
    """Model for linking articles to digests."""

    __tablename__ = "digest_articles"

    id = Column(PostgresUUID(as_uuid=True), primary_key=True, default=uuid4)
    digest_id = Column(
        PostgresUUID(as_uuid=True),
        ForeignKey("daily_digests.id", ondelete="CASCADE"),
        nullable=False,
    )
    article_id = Column(
        PostgresUUID(as_uuid=True),
        ForeignKey("news_articles.id", ondelete="CASCADE"),
        nullable=False,
    )
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    digest = relationship("DailyDigest", back_populates="digest_articles")
    article = relationship("NewsArticle", back_populates="digest_articles")

    # Constraints
    __table_args__ = (
        UniqueConstraint("digest_id", "article_id", name="uq_digest_article"),
    )

    def __repr__(self):
        return (
            f"<DigestArticle(digest_id={self.digest_id}, article_id={self.article_id})>"
        )
