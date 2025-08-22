"""
News summarizer package for the Briefly Bot.
Provides TLDR-style summaries suitable for Slack messages.
"""

from .tldr_summarizer import TLDRSummarizer, create_tldr_summarizer
from .models import TLDRSummary, SlackMessage

__all__ = ["TLDRSummarizer", "create_tldr_summarizer", "TLDRSummary", "SlackMessage"]
