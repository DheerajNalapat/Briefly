"""
Briefly Bot Services Package

This package provides high-level service interfaces for:
- News aggregation from multiple sources
- Content summarization using different LLM providers
- Multi-platform publishing (Slack, etc.)
"""

from .aggregation_service import AggregationService
from .summarizer_service import SummarizerService
from .publisher_service import PublisherService

__all__ = ["AggregationService", "SummarizerService", "PublisherService"]
