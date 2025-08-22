"""
TLDR summary models for Slack-friendly news summaries.
"""

from typing import List, Optional
from datetime import datetime
from dataclasses import dataclass
from pydantic import BaseModel, Field


@dataclass
class TLDRSummary:
    """TLDR summary result for news articles."""

    # Core summary data
    tldr_text: str  # Main TLDR summary (2-3 sentences)
    key_points: List[str]  # Bullet points of key developments
    trending_topics: List[str]  # What's hot right now
    impact_level: str  # "High", "Medium", "Low" impact
    reading_time: str  # Estimated reading time

    # Metadata
    article_count: int
    categories: List[str]
    sources: List[str]
    generated_at: str
    model_used: str

    # Slack-specific formatting
    emoji: str = "📰"  # Default emoji for the summary
    color: str = "#36a64f"  # Green color for Slack attachments


class SlackMessage(BaseModel):
    """Structured Slack message format."""

    text: str = Field(description="Main message text (can be empty if using blocks)")
    blocks: List[dict] = Field(description="Slack block kit components")
    attachments: List[dict] = Field(description="Slack attachments for rich formatting")

    class Config:
        extra = "forbid"


class DailyDigestTLDR(BaseModel):
    """Structured TLDR output for daily digest summaries."""

    tldr_summary: str = Field(
        description="A concise 2-3 sentence TLDR of the day's most important AI/ML news"
    )
    top_headlines: List[str] = Field(
        description="List of 3-5 most important headlines in TLDR format"
    )
    trending_topics: List[str] = Field(
        description="List of 3-5 trending topics or emerging patterns"
    )
    impact_assessment: str = Field(
        description="Brief assessment of potential impact (High/Medium/Low) with 1 sentence explanation"
    )
    must_read: List[str] = Field(
        description="List of 2-3 most important articles to read with brief reason why"
    )
    slack_format: str = Field(
        description="Pre-formatted Slack message with emojis and proper formatting"
    )


class ArticleTLDR(BaseModel):
    """Structured TLDR output for individual articles."""

    tldr: str = Field(description="2-3 sentence TLDR summary of the article")
    key_facts: List[str] = Field(description="3-5 key facts or takeaways")
    why_matters: str = Field(
        description="1-2 sentences explaining why this matters to AI/ML professionals"
    )
    reading_time: str = Field(description="Estimated reading time (e.g., '2 min read')")
    difficulty: str = Field(
        description="Content difficulty level: 'Beginner', 'Intermediate', or 'Advanced'"
    )
