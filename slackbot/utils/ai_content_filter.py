#!/usr/bin/env python3
"""
AI Content Filter for Briefly Bot

This module provides intelligent filtering and scoring of content based on
AI/ML relevance, agentic systems, and developer interest. It serves as a
unified filtering layer for all content sources.
"""

import logging
import re
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


@dataclass
class FilteringConfig:
    """Configuration for AI content filtering."""

    # Minimum relevance score to include content (0.0 - 1.0)
    min_relevance_score: float = 0.3

    # Minimum content quality score (0.0 - 1.0)
    min_quality_score: float = 0.2

    # Maximum age in hours for content
    max_age_hours: int = 72

    # Enable strict filtering (higher thresholds)
    strict_mode: bool = False

    # Boost scores for recent content
    recency_boost_enabled: bool = True

    # Boost scores for high-quality sources
    source_quality_boost: bool = True


class AIContentFilter:
    """
    Intelligent AI/ML content filter and scorer.

    This class provides comprehensive filtering and scoring of content
    based on AI/ML relevance, agentic systems, and developer interest.
    """

    def __init__(self, config: Optional[FilteringConfig] = None):
        """
        Initialize the AI content filter.

        Args:
            config: Filtering configuration
        """
        self.config = config or FilteringConfig()

        # Initialize keyword weights
        self._initialize_keyword_weights()

        # Initialize source quality weights
        self._initialize_source_weights()

        logger.info("AI Content Filter initialized with config: %s", self.config)

    def _initialize_keyword_weights(self) -> None:
        """Initialize AI/ML keyword weights for relevance scoring."""

        # Core AI/ML terms (highest weight)
        self.core_ai_keywords = {
            # Primary AI/ML terms
            "artificial intelligence": 1.0,
            "ai": 1.0,
            "machine learning": 1.0,
            "ml": 1.0,
            "deep learning": 1.0,
            "neural network": 1.0,
            "neural networks": 1.0,
            "transformer": 1.0,
            "transformers": 1.0,
            "gpt": 1.0,
            "llm": 1.0,
            "large language model": 1.0,
            "large language models": 1.0,
            "generative ai": 1.0,
            "generative artificial intelligence": 1.0,
            # Agentic systems (highest priority for developers)
            "agentic": 1.0,
            "agentic ai": 1.0,
            "autonomous agent": 1.0,
            "autonomous agents": 1.0,
            "multi-agent": 1.0,
            "multi-agent system": 1.0,
            "agent-based": 1.0,
            "intelligent agent": 1.0,
            "intelligent agents": 1.0,
            "autonomous system": 1.0,
            "autonomous systems": 1.0,
            "agent framework": 1.0,
            "agent frameworks": 1.0,
            "agent orchestration": 1.0,
            "agent coordination": 1.0,
            "swarm intelligence": 1.0,
            "collective intelligence": 1.0,
            # RAG and Vector Systems (critical for developers)
            "rag": 1.0,
            "retrieval augmented generation": 1.0,
            "retrieval-augmented generation": 1.0,
            "vector database": 1.0,
            "vector databases": 1.0,
            "vector search": 1.0,
            "vector similarity": 1.0,
            "embedding": 1.0,
            "embeddings": 1.0,
            "semantic search": 1.0,
            "knowledge base": 1.0,
            "knowledge bases": 1.0,
            "document retrieval": 1.0,
            "context window": 1.0,
            "context windows": 1.0,
            "retrieval system": 1.0,
            "retrieval systems": 1.0,
            # AI Frameworks and Tools (high developer interest)
            "langchain": 1.0,
            "lang chain": 1.0,
            "llama index": 1.0,
            "haystack": 1.0,
            "hugging face": 1.0,
            "huggingface": 1.0,
            "openai": 1.0,
            "anthropic": 1.0,
            "claude": 1.0,
            "gemini": 1.0,
            "pytorch": 1.0,
            "tensorflow": 1.0,
            "keras": 1.0,
            "scikit-learn": 1.0,
            "pandas": 1.0,
            "numpy": 1.0,
            # AI Development and Engineering
            "ai development": 0.95,
            "ai engineering": 0.95,
            "ml engineering": 0.95,
            "mlops": 0.95,
            "aiops": 0.95,
            "model deployment": 0.95,
            "model serving": 0.95,
            "ai pipeline": 0.95,
            "ai pipelines": 0.95,
            "ai workflow": 0.95,
            "ai workflows": 0.95,
            "ai automation": 0.95,
            "ai integration": 0.95,
            "ai api": 0.95,
            "ai apis": 0.95,
            "ai sdk": 0.95,
            "ai sdks": 0.95,
            # Specific AI Applications (high relevance)
            "computer vision": 0.9,
            "cv": 0.9,
            "image recognition": 0.9,
            "object detection": 0.9,
            "natural language processing": 0.9,
            "nlp": 0.9,
            "text processing": 0.9,
            "speech recognition": 0.9,
            "speech synthesis": 0.9,
            "text-to-speech": 0.9,
            "speech-to-text": 0.9,
            "robotics": 0.9,
            "autonomous vehicle": 0.9,
            "autonomous vehicles": 0.9,
            "self-driving": 0.9,
            "recommendation system": 0.9,
            "recommendation systems": 0.9,
            "personalization": 0.9,
            "chatbot": 0.9,
            "chatbots": 0.9,
            "conversational ai": 0.9,
            "voice assistant": 0.9,
            "voice assistants": 0.9,
            # AI Research and Innovation
            "ai research": 0.85,
            "ml research": 0.85,
            "ai breakthrough": 0.85,
            "ai breakthroughs": 0.85,
            "ai innovation": 0.85,
            "ai innovations": 0.85,
            "ai advancement": 0.85,
            "ai advancements": 0.85,
            "ai progress": 0.85,
            "ai development": 0.85,
            "ai algorithm": 0.85,
            "ai algorithms": 0.85,
            "ai model": 0.85,
            "ai models": 0.85,
            "ai training": 0.85,
            "ai inference": 0.85,
            "ai optimization": 0.85,
            "ai performance": 0.85,
            "ai accuracy": 0.85,
            "ai efficiency": 0.85,
            "ai scalability": 0.85,
            # AI Infrastructure and Hardware
            "ai chip": 0.8,
            "ai chips": 0.8,
            "ai hardware": 0.8,
            "ai accelerator": 0.8,
            "ai accelerators": 0.8,
            "gpu": 0.8,
            "gpus": 0.8,
            "tpu": 0.8,
            "tpus": 0.8,
            "nvidia": 0.8,
            "ai compute": 0.8,
            "ai computing": 0.8,
            "ai infrastructure": 0.8,
            "ai data center": 0.8,
            "ai data centers": 0.8,
            "ai cloud": 0.8,
            "ai edge": 0.8,
            "edge ai": 0.8,
            # AI Ethics and Safety (important for developers)
            "ai ethics": 0.75,
            "ai safety": 0.75,
            "ai alignment": 0.75,
            "ai bias": 0.75,
            "ai fairness": 0.75,
            "ai transparency": 0.75,
            "ai explainability": 0.75,
            "ai interpretability": 0.75,
            "ai governance": 0.75,
            "ai regulation": 0.75,
            "ai policy": 0.75,
            "responsible ai": 0.75,
            "ai risk": 0.75,
            "ai risks": 0.75,
            # AI Business and Industry (moderate relevance)
            "ai startup": 0.7,
            "ai startups": 0.7,
            "ai company": 0.7,
            "ai companies": 0.7,
            "ai investment": 0.7,
            "ai investments": 0.7,
            "ai funding": 0.7,
            "ai venture": 0.7,
            "ai ventures": 0.7,
            "ai market": 0.7,
            "ai markets": 0.7,
            "ai industry": 0.7,
            "ai industries": 0.7,
            "ai adoption": 0.7,
            "ai implementation": 0.7,
            "ai deployment": 0.7,
            "ai integration": 0.7,
            "ai transformation": 0.7,
            "ai disruption": 0.7,
            "ai revolution": 0.7,
            # General tech terms (lower weight)
            "software development": 0.6,
            "programming": 0.6,
            "coding": 0.6,
            "algorithm": 0.6,
            "algorithms": 0.6,
            "data science": 0.6,
            "data scientist": 0.6,
            "data scientists": 0.6,
            "automation": 0.6,
            "optimization": 0.6,
            "scalability": 0.6,
            "performance": 0.6,
            "efficiency": 0.6,
            "innovation": 0.6,
            "technology": 0.5,
            "tech": 0.5,
            "digital": 0.5,
            "smart": 0.5,
            "intelligent": 0.5,
        }

        # Negative keywords (reduce score)
        self.negative_keywords = {
            "crypto": -0.3,
            "cryptocurrency": -0.3,
            "bitcoin": -0.3,
            "blockchain": -0.2,
            "nft": -0.3,
            "nfts": -0.3,
            "metaverse": -0.2,
            "web3": -0.2,
            "defi": -0.3,
            "trading": -0.2,
            "finance": -0.1,
            "banking": -0.1,
            "stock": -0.1,
            "stocks": -0.1,
            "market": -0.1,
            "economy": -0.1,
            "politics": -0.2,
            "political": -0.2,
            "election": -0.2,
            "elections": -0.2,
            "war": -0.3,
            "conflict": -0.3,
            "crime": -0.3,
            "criminal": -0.3,
            "sports": -0.2,
            "entertainment": -0.2,
            "celebrity": -0.2,
            "celebrity": -0.2,
            "gossip": -0.3,
            "fashion": -0.2,
            "food": -0.2,
            "travel": -0.2,
            "weather": -0.2,
            "health": -0.1,
            "medical": -0.1,
            "pharmaceutical": -0.1,
            "drug": -0.1,
            "drugs": -0.1,
        }

    def _initialize_source_weights(self) -> None:
        """Initialize source quality weights."""

        self.source_weights = {
            # High-quality AI/ML sources
            "arxiv": 1.0,
            "openai": 1.0,
            "anthropic": 1.0,
            "hugging face": 1.0,
            "huggingface": 1.0,
            "google ai": 1.0,
            "deepmind": 1.0,
            "mit technology review": 1.0,
            "nature": 1.0,
            "science": 1.0,
            # Good tech sources
            "techcrunch": 0.9,
            "venturebeat": 0.9,
            "the verge": 0.9,
            "ars technica": 0.9,
            "wired": 0.8,
            "medium": 0.8,
            "github": 0.9,
            "stack overflow": 0.8,
            # General news sources (lower weight)
            "newsapi": 0.7,
            "reuters": 0.6,
            "ap": 0.6,
            "bbc": 0.6,
            "cnn": 0.5,
            "fox": 0.5,
            "msnbc": 0.5,
        }

    def calculate_ai_relevance_score(self, content: Dict[str, Any]) -> float:
        """
        Calculate AI/ML relevance score for content.

        Args:
            content: Content dictionary with title, summary, etc.

        Returns:
            Relevance score between 0.0 and 1.0
        """
        title = content.get("title", "").lower()
        summary = content.get("summary", "").lower()
        category = content.get("category", "").lower()
        source = content.get("source", "").lower()

        # Combine all text content
        full_text = f"{title} {summary} {category} {source}"

        # Calculate positive keyword score
        positive_score = 0.0
        keyword_matches = []

        for keyword, weight in self.core_ai_keywords.items():
            if keyword in full_text:
                positive_score = max(positive_score, weight)
                keyword_matches.append(keyword)

        # Calculate negative keyword penalty
        negative_penalty = 0.0
        for keyword, penalty in self.negative_keywords.items():
            if keyword in full_text:
                negative_penalty += abs(penalty)

        # Apply negative penalty
        final_score = max(0.0, positive_score - negative_penalty)

        # Boost score for multiple keyword matches
        if len(keyword_matches) > 1:
            final_score = min(1.0, final_score * (1 + len(keyword_matches) * 0.1))

        # Boost score for high-quality sources
        if self.config.source_quality_boost:
            source_boost = self.source_weights.get(source, 0.5)
            final_score = min(1.0, final_score * (1 + source_boost * 0.2))

        return final_score

    def calculate_content_quality_score(self, content: Dict[str, Any]) -> float:
        """
        Calculate content quality score.

        Args:
            content: Content dictionary

        Returns:
            Quality score between 0.0 and 1.0
        """
        title = content.get("title", "")
        summary = content.get("summary", "")

        quality_score = 0.0

        # Title quality (length, clarity)
        if title:
            title_length = len(title)
            if 20 <= title_length <= 100:
                quality_score += 0.3
            elif 10 <= title_length < 20 or 100 < title_length <= 150:
                quality_score += 0.2
            else:
                quality_score += 0.1

        # Summary quality (length, completeness)
        if summary:
            summary_length = len(summary)
            if 100 <= summary_length <= 500:
                quality_score += 0.4
            elif 50 <= summary_length < 100 or 500 < summary_length <= 1000:
                quality_score += 0.3
            else:
                quality_score += 0.2

        # URL quality (valid URL)
        url = content.get("url", "")
        if url and url.startswith(("http://", "https://")):
            quality_score += 0.2

        # Published date quality
        published_at = content.get("published_at", "")
        if published_at:
            quality_score += 0.1

        return min(1.0, quality_score)

    def calculate_recency_score(self, content: Dict[str, Any]) -> float:
        """
        Calculate recency score based on publication date.

        Args:
            content: Content dictionary

        Returns:
            Recency score between 0.0 and 1.0
        """
        published_at = content.get("published_at", "")
        if not published_at:
            return 0.5  # Neutral score for unknown dates

        try:
            # Parse published date
            if isinstance(published_at, str):
                # Try different date formats
                for fmt in ["%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d", "%a, %d %b %Y %H:%M:%S %z"]:
                    try:
                        pub_date = datetime.strptime(published_at, fmt)
                        break
                    except ValueError:
                        continue
                else:
                    return 0.5  # Can't parse date
            else:
                pub_date = published_at

            # Calculate age in hours
            now = datetime.now(timezone.utc)
            if pub_date.tzinfo is None:
                pub_date = pub_date.replace(tzinfo=timezone.utc)

            age_hours = (now - pub_date).total_seconds() / 3600

            # Calculate recency score
            if age_hours <= 6:
                return 1.0
            elif age_hours <= 24:
                return 0.9
            elif age_hours <= 48:
                return 0.7
            elif age_hours <= 72:
                return 0.5
            else:
                return 0.2

        except Exception as e:
            logger.warning("Error calculating recency score: %s", e)
            return 0.5

    def calculate_total_score(self, content: Dict[str, Any]) -> float:
        """
        Calculate total content score.

        Args:
            content: Content dictionary

        Returns:
            Total score between 0.0 and 1.0
        """
        ai_score = self.calculate_ai_relevance_score(content)
        quality_score = self.calculate_content_quality_score(content)
        recency_score = self.calculate_recency_score(content)

        # Weighted combination
        total_score = (
            ai_score * 0.6  # 60% weight for AI relevance
            + quality_score * 0.25  # 25% weight for content quality
            + recency_score * 0.15  # 15% weight for recency
        )

        return min(1.0, total_score)

    def is_content_relevant(self, content: Dict[str, Any]) -> bool:
        """
        Check if content meets relevance criteria.

        Args:
            content: Content dictionary

        Returns:
            True if content is relevant, False otherwise
        """
        ai_score = self.calculate_ai_relevance_score(content)
        quality_score = self.calculate_content_quality_score(content)
        total_score = self.calculate_total_score(content)

        # Check age
        published_at = content.get("published_at", "")
        if published_at:
            try:
                if isinstance(published_at, str):
                    for fmt in ["%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d"]:
                        try:
                            pub_date = datetime.strptime(published_at, fmt)
                            break
                        except ValueError:
                            continue
                    else:
                        return False
                else:
                    pub_date = published_at

                now = datetime.now(timezone.utc)
                if pub_date.tzinfo is None:
                    pub_date = pub_date.replace(tzinfo=timezone.utc)

                age_hours = (now - pub_date).total_seconds() / 3600
                if age_hours > self.config.max_age_hours:
                    return False

            except Exception:
                pass  # If we can't parse date, don't filter by age

        # Check relevance thresholds
        if self.config.strict_mode:
            result = (
                ai_score >= self.config.min_relevance_score
                and quality_score >= self.config.min_quality_score
                and total_score >= 0.6
            )
            logger.debug(
                "Strict mode check: ai_score=%.2f >= %.2f=%s, quality_score=%.2f >= %.2f=%s, total_score=%.2f >= 0.6=%s, result=%s",
                ai_score,
                self.config.min_relevance_score,
                ai_score >= self.config.min_relevance_score,
                quality_score,
                self.config.min_quality_score,
                quality_score >= self.config.min_quality_score,
                total_score,
                total_score >= 0.6,
                result,
            )
            return result
        else:
            result = (
                ai_score >= self.config.min_relevance_score
                and quality_score >= self.config.min_quality_score
                and total_score >= 0.4
            )
            logger.debug(
                "Normal mode check: ai_score=%.2f >= %.2f=%s, quality_score=%.2f >= %.2f=%s, total_score=%.2f >= 0.4=%s, result=%s",
                ai_score,
                self.config.min_relevance_score,
                ai_score >= self.config.min_relevance_score,
                quality_score,
                self.config.min_quality_score,
                quality_score >= self.config.min_quality_score,
                total_score,
                total_score >= 0.4,
                result,
            )
            return result

    def filter_and_score_content(self, content_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Filter and score a list of content items.

        Args:
            content_list: List of content dictionaries

        Returns:
            List of filtered and scored content items
        """
        if not content_list:
            return []

        logger.info("🔍 Filtering %s content items...", len(content_list))

        filtered_content = []
        for content in content_list:
            if self.is_content_relevant(content):
                # Add scores to content
                content["ai_relevance_score"] = self.calculate_ai_relevance_score(content)
                content["content_quality_score"] = self.calculate_content_quality_score(content)
                content["recency_score"] = self.calculate_recency_score(content)
                content["total_score"] = self.calculate_total_score(content)
                content["filtered_at"] = datetime.now().isoformat()

                filtered_content.append(content)

        # Sort by total score (highest first)
        filtered_content.sort(key=lambda x: x["total_score"], reverse=True)

        logger.info(
            "✅ Filtered to %s relevant items (%.1f%% retention)",
            len(filtered_content),
            (len(filtered_content) / len(content_list)) * 100,
        )

        return filtered_content

    def get_filtering_summary(self, original_count: int, filtered_count: int) -> Dict[str, Any]:
        """
        Get filtering summary statistics.

        Args:
            original_count: Original number of items
            filtered_count: Number of items after filtering

        Returns:
            Summary dictionary
        """
        return {
            "original_count": original_count,
            "filtered_count": filtered_count,
            "retention_rate": filtered_count / original_count if original_count > 0 else 0,
            "filtered_out": original_count - filtered_count,
            "config": {
                "min_relevance_score": self.config.min_relevance_score,
                "min_quality_score": self.config.min_quality_score,
                "max_age_hours": self.config.max_age_hours,
                "strict_mode": self.config.strict_mode,
            },
            "timestamp": datetime.now().isoformat(),
        }


def create_ai_content_filter(config: Optional[FilteringConfig] = None) -> AIContentFilter:
    """
    Factory function to create an AI content filter.

    Args:
        config: Optional filtering configuration

    Returns:
        AIContentFilter instance
    """
    return AIContentFilter(config)


if __name__ == "__main__":
    # Test the AI content filter
    import logging

    # Set up logging
    logging.basicConfig(level=logging.INFO)

    # Create filter with normal mode
    filter_config = FilteringConfig(min_relevance_score=0.3, min_quality_score=0.2, strict_mode=False)
    ai_filter = create_ai_content_filter(filter_config)

    # Test content
    test_content = [
        {
            "title": "OpenAI Releases New GPT-4 Model with Enhanced Capabilities",
            "summary": "OpenAI has announced the release of GPT-4, featuring improved reasoning abilities and multimodal capabilities for AI developers.",
            "url": "https://openai.com/gpt-4",
            "source": "openai",
            "category": "AI Research",
            "published_at": "2025-10-08T10:00:00Z",
        },
        {
            "title": "New AI Framework Simplifies Agentic System Development",
            "summary": "A new open-source framework makes it easier for developers to build autonomous agents and multi-agent systems.",
            "url": "https://example.com/ai-framework",
            "source": "techcrunch",
            "category": "AI Development",
            "published_at": "2025-10-08T09:00:00Z",
        },
        {
            "title": "Stock Market Reaches New High",
            "summary": "The stock market has reached a new all-time high as investors remain optimistic about economic growth.",
            "url": "https://example.com/stock-news",
            "source": "cnn",
            "category": "Finance",
            "published_at": "2025-10-08T08:00:00Z",
        },
        {
            "title": "RAG Implementation Best Practices for Vector Databases",
            "summary": "Learn how to implement retrieval-augmented generation systems using vector databases for better AI applications.",
            "url": "https://example.com/rag-guide",
            "source": "medium",
            "category": "AI Development",
            "published_at": "2025-10-08T07:00:00Z",
        },
    ]

    print("🧪 Testing AI Content Filter...")
    print("=" * 50)

    # Filter and score content
    filtered_content = ai_filter.filter_and_score_content(test_content)

    print(f"📊 Filtered {len(test_content)} items to {len(filtered_content)} relevant items")
    print()

    for i, content in enumerate(filtered_content, 1):
        print(f"{i}. {content['title']}")
        print(f"   AI Relevance: {content['ai_relevance_score']:.2f}")
        print(f"   Quality: {content['content_quality_score']:.2f}")
        print(f"   Recency: {content['recency_score']:.2f}")
        print(f"   Total Score: {content['total_score']:.2f}")
        print()

    # Show summary
    summary = ai_filter.get_filtering_summary(len(test_content), len(filtered_content))
    print("📈 Filtering Summary:")
    print(f"   Retention Rate: {summary['retention_rate']:.1%}")
    print(f"   Filtered Out: {summary['filtered_out']} items")
