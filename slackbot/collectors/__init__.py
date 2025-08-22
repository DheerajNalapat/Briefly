"""
News collectors package for the Briefly Bot.
Provides various methods for collecting news and research content.
"""

from .base_collector import BaseCollector
from .api_collector import APINewsCollector, create_api_collector

__all__ = [
    "BaseCollector",
    "APINewsCollector",
    "create_api_collector",
]
