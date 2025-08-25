"""
News collectors package for the Briefly Bot.
Provides various methods for collecting news and research content.
"""

from .base_collector import BaseCollector
from .arxiv_collector import ArXivCollector, create_arxiv_collector
from .newsapi_org_collector import NewsAPICollector, create_newsapi_collector

__all__ = [
    "BaseCollector",
    "ArXivCollector",
    "create_arxiv_collector",
    "NewsAPICollector",
    "create_newsapi_collector",
]
