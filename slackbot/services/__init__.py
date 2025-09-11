"""
Briefly Bot Services Package

This package provides high-level service interfaces for:
- News aggregation from multiple sources
- Content processing including summarization and intelligent reranking
- Multi-platform publishing (Slack, etc.)
"""

from .aggregation_service import AggregationService
from .summarizer_service import ContentProcessingService
from .publisher_service import PublisherService

__all__ = ["AggregationService", "ContentProcessingService", "PublisherService"]
