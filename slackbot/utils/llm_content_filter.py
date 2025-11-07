#!/usr/bin/env python3
"""
LLM Content Filter for Briefly Bot

This module provides intelligent content filtering using LLM-based classification
to determine if content is relevant to AI developers. It uses a binary classification
approach where the LLM returns True/False for content relevance.
"""

import logging
import json
import os
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


@dataclass
class LLMFilteringConfig:
    """Configuration for LLM-based content filtering."""

    # LLM provider settings
    llm_provider: str = "openai"  # "openai", "gemini", "auto"
    model_name: Optional[str] = None  # Specific model to use
    api_key: Optional[str] = None

    # Filtering settings
    confidence_threshold: float = 0.75  # Minimum confidence for classification
    max_retries: int = 3  # Max retries for failed LLM calls
    timeout_seconds: int = 30  # Timeout for LLM calls

    # Batch processing
    batch_size: int = 5  # Process articles in batches
    enable_batch_processing: bool = True

    # Fallback settings
    fallback_to_keywords: bool = True  # Use keyword filtering if LLM fails
    max_age_hours: int = 72  # Filter out old content regardless of LLM decision


class LLMContentFilter:
    """
    LLM-based content filter for AI developer relevance.

    Uses an LLM to classify content as relevant (True) or not relevant (False)
    for AI developers, with intelligent prompting and confidence scoring.
    """

    def __init__(self, config: Optional[LLMFilteringConfig] = None):
        """
        Initialize the LLM content filter.

        Args:
            config: LLM filtering configuration
        """
        self.config = config or LLMFilteringConfig()
        self.llm_client = None
        self.fallback_filter = None

        logger.info("Initializing LLM Content Filter with provider: %s", self.config.llm_provider)
        self._initialize_llm_client()
        self._initialize_fallback_filter()

    def _initialize_llm_client(self) -> None:
        """Initialize the LLM client based on provider."""
        try:
            if self.config.llm_provider == "openai":
                self._initialize_openai_client()
            elif self.config.llm_provider == "gemini":
                self._initialize_gemini_client()
            elif self.config.llm_provider == "auto":
                self._initialize_auto_client()
            else:
                raise ValueError(f"Unsupported LLM provider: {self.config.llm_provider}")

            logger.info("✅ LLM client initialized successfully")

        except Exception as e:
            logger.error("❌ Failed to initialize LLM client: %s", e)
            self.llm_client = None

    def _initialize_openai_client(self) -> None:
        """Initialize OpenAI client."""
        try:
            import openai

            api_key = self.config.api_key or os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OpenAI API key not found")

            self.llm_client = openai.OpenAI(api_key=api_key)
            logger.info("OpenAI client initialized")

        except ImportError:
            raise ImportError("OpenAI library not installed. Install with: pip install openai")

    def _initialize_gemini_client(self) -> None:
        """Initialize Gemini client."""
        try:
            import google.generativeai as genai

            api_key = self.config.api_key or os.getenv("GEMINI_API_KEY")
            if not api_key:
                raise ValueError("Gemini API key not found")

            genai.configure(api_key=api_key)
            self.llm_client = genai.GenerativeModel("gemini-pro")
            logger.info("Gemini client initialized")

        except ImportError:
            raise ImportError("Gemini library not installed. Install with: pip install google-generativeai")

    def _initialize_auto_client(self) -> None:
        """Initialize client automatically based on available API keys."""
        if os.getenv("OPENAI_API_KEY"):
            self.config.llm_provider = "openai"
            self._initialize_openai_client()
        elif os.getenv("GEMINI_API_KEY"):
            self.config.llm_provider = "gemini"
            self._initialize_gemini_client()
        else:
            raise ValueError("No LLM API keys found. Set OPENAI_API_KEY or GEMINI_API_KEY")

    def _initialize_fallback_filter(self) -> None:
        """Initialize fallback keyword-based filter."""
        if self.config.fallback_to_keywords:
            try:
                from slackbot.utils.ai_content_filter import create_ai_content_filter, FilteringConfig

                fallback_config = FilteringConfig(
                    min_relevance_score=0.8,  # Much higher threshold
                    min_quality_score=0.5,  # Higher quality threshold
                    strict_mode=True,
                    max_age_hours=48,  # Stricter age limit
                )
                self.fallback_filter = create_ai_content_filter(fallback_config)
                logger.info("✅ Fallback keyword filter initialized")

            except Exception as e:
                logger.warning("⚠️ Failed to initialize fallback filter: %s", e)
                self.fallback_filter = None

    def is_available(self) -> bool:
        """Check if the LLM filter is available."""
        return self.llm_client is not None

    def _create_classification_prompt(self, content: Dict[str, Any]) -> str:
        """
        Create a prompt for LLM-based content classification.

        Args:
            content: Content dictionary with title, summary, etc.

        Returns:
            Formatted prompt string
        """
        title = content.get("title", "")
        summary = content.get("summary", "")
        source = content.get("source", "")
        category = content.get("category", "")

        prompt = f"""You are an expert AI content classifier. Your task is to determine if a news article is relevant to AI developers and practitioners.

AI DEVELOPER RELEVANCE CRITERIA (MUST BE EXPLICITLY AI-RELATED):
- Core AI/ML technologies (machine learning, deep learning, neural networks, LLMs, GPT, transformers)
- AI frameworks and tools (LangChain, OpenAI, Hugging Face, PyTorch, TensorFlow)
- Agentic systems and autonomous agents
- RAG (Retrieval Augmented Generation) and vector databases
- AI research breakthroughs and model releases
- AI engineering practices (MLOps, model deployment, AI APIs)
- Computer vision, NLP, robotics applications
- AI ethics, safety, and governance
- AI business applications and industry adoption
- Software development with AI integration
- Prompt engineering, AI prompting techniques, and LLM optimization
- AI skills, AI career development, and AI professional practices

STRICT NOT RELEVANT (MUST BE FILTERED OUT):
- General technology news without explicit AI focus
- Sales training, CRM systems, business processes without AI
- Payroll solutions, HR systems, administrative tools
- General education technology without AI
- Water treatment, infrastructure, utilities
- Politics, entertainment, sports, general news
- Cryptocurrency, blockchain, NFTs
- General business news without AI context
- Market reports for non-AI industries
- Non-technical content

ARTICLE TO CLASSIFY:
Title: {title}
Summary: {summary}
Source: {source}
Category: {category}

INSTRUCTIONS:
1. Analyze the content for EXPLICIT AI developer relevance
2. Look for specific AI technologies, frameworks, or applications
3. If the article mentions "AI" but it's just general business/technology, it's NOT relevant
4. Return ONLY a JSON response with this exact format:
{{"relevant": true/false, "confidence": 0.0-1.0, "reasoning": "brief explanation"}}

Examples:
- "OpenAI releases GPT-5" → {{"relevant": true, "confidence": 0.95, "reasoning": "Direct AI model release"}}
- "Sales training improves performance" → {{"relevant": false, "confidence": 0.90, "reasoning": "General sales training, no AI focus"}}
- "AI-powered chatbot improves customer service" → {{"relevant": true, "confidence": 0.85, "reasoning": "AI application in business"}}
- "CRM system reduces admin time" → {{"relevant": false, "confidence": 0.85, "reasoning": "General CRM system, no AI mentioned"}}
- "Water treatment market grows" → {{"relevant": false, "confidence": 0.90, "reasoning": "Water treatment industry, no AI relevance"}}
- "French politics and party formation" → {{"relevant": false, "confidence": 0.95, "reasoning": "Political news, no AI relevance"}}
- "Prompt engineering is essential for AI developers" → {{"relevant": true, "confidence": 0.90, "reasoning": "AI skill development for developers"}}

RESPONSE:"""

        return prompt

    def _classify_content_with_llm(self, content: Dict[str, Any]) -> Tuple[bool, float, str]:
        """
        Classify content using LLM.

        Args:
            content: Content dictionary

        Returns:
            Tuple of (is_relevant, confidence, reasoning)
        """
        if not self.is_available():
            raise RuntimeError("LLM client not available")

        prompt = self._create_classification_prompt(content)

        for attempt in range(self.config.max_retries):
            try:
                if self.config.llm_provider == "openai":
                    response = self._call_openai(prompt)
                elif self.config.llm_provider == "gemini":
                    response = self._call_gemini(prompt)
                else:
                    raise ValueError(f"Unsupported provider: {self.config.llm_provider}")

                # Parse JSON response
                result = json.loads(response)

                is_relevant = bool(result.get("relevant", False))
                confidence = float(result.get("confidence", 0.0))
                reasoning = str(result.get("reasoning", ""))

                logger.debug(
                    "LLM classification: relevant=%s, confidence=%.2f, reasoning=%s", is_relevant, confidence, reasoning
                )

                return is_relevant, confidence, reasoning

            except json.JSONDecodeError as e:
                logger.warning("⚠️ Failed to parse LLM response (attempt %d): %s", attempt + 1, e)
                if attempt == self.config.max_retries - 1:
                    raise
                continue

            except Exception as e:
                logger.warning("⚠️ LLM call failed (attempt %d): %s", attempt + 1, e)
                if attempt == self.config.max_retries - 1:
                    raise
                continue

        raise RuntimeError("All LLM classification attempts failed")

    def _call_openai(self, prompt: str) -> str:
        """Call OpenAI API."""
        model = self.config.model_name or "gpt-3.5-turbo"

        response = self.llm_client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert AI content classifier. Always respond with valid JSON.",
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.1,  # Low temperature for consistent classification
            max_tokens=200,  # Short response for classification
            timeout=self.config.timeout_seconds,
        )

        return response.choices[0].message.content.strip()

    def _call_gemini(self, prompt: str) -> str:
        """Call Gemini API."""
        response = self.llm_client.generate_content(
            prompt,
            generation_config={"temperature": 0.1, "max_output_tokens": 200, "timeout": self.config.timeout_seconds},
        )

        return response.text.strip()

    def _is_content_recent(self, content: Dict[str, Any]) -> bool:
        """Check if content is recent enough."""
        published_at = content.get("published_at", "")
        if not published_at:
            return True  # If no date, assume recent

        try:
            if isinstance(published_at, str):
                for fmt in ["%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d"]:
                    try:
                        pub_date = datetime.strptime(published_at, fmt)
                        break
                    except ValueError:
                        continue
                else:
                    return True  # Can't parse date, assume recent
            else:
                pub_date = published_at

            now = datetime.now()
            if pub_date.tzinfo is None:
                pub_date = pub_date.replace(tzinfo=None)

            age_hours = (now - pub_date).total_seconds() / 3600
            return age_hours <= self.config.max_age_hours

        except Exception:
            return True  # If we can't parse date, assume recent

    def classify_content(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """
        Classify a single content item.

        Args:
            content: Content dictionary

        Returns:
            Classification result with scores and metadata
        """
        result = {
            "content": content,
            "is_relevant": False,
            "confidence": 0.0,
            "reasoning": "",
            "method": "fallback",
            "timestamp": datetime.now().isoformat(),
        }

        # Check if content is recent enough
        if not self._is_content_recent(content):
            result["reasoning"] = "Content too old"
            result["method"] = "age_filter"
            return result

        # Try LLM classification first
        if self.is_available():
            try:
                is_relevant, confidence, reasoning = self._classify_content_with_llm(content)

                # Only accept if confidence is above threshold
                if confidence >= self.config.confidence_threshold:
                    result.update(
                        {"is_relevant": is_relevant, "confidence": confidence, "reasoning": reasoning, "method": "llm"}
                    )
                else:
                    # Low confidence, fall back to keyword filtering
                    if self.fallback_filter:
                        is_relevant_fallback = self.fallback_filter.is_content_relevant(content)
                        result.update(
                            {
                                "is_relevant": is_relevant_fallback,
                                "confidence": 0.5,  # Medium confidence for fallback
                                "reasoning": f"Low LLM confidence ({confidence:.2f}), used keyword filtering",
                                "method": "llm_fallback",
                            }
                        )
                    else:
                        result.update(
                            {
                                "is_relevant": False,
                                "confidence": confidence,
                                "reasoning": f"Low LLM confidence ({confidence:.2f}), no fallback available",
                                "method": "llm_low_confidence",
                            }
                        )

            except Exception as e:
                logger.warning("⚠️ LLM classification failed: %s", e)

                # Fall back to keyword filtering
                if self.fallback_filter:
                    is_relevant_fallback = self.fallback_filter.is_content_relevant(content)
                    result.update(
                        {
                            "is_relevant": is_relevant_fallback,
                            "confidence": 0.5,
                            "reasoning": f"LLM failed ({str(e)}), used keyword filtering",
                            "method": "llm_error_fallback",
                        }
                    )
                else:
                    result.update(
                        {
                            "is_relevant": False,
                            "confidence": 0.0,
                            "reasoning": f"LLM failed ({str(e)}), no fallback available",
                            "method": "llm_error",
                        }
                    )

        # Use fallback filter if LLM is not available
        elif self.fallback_filter:
            is_relevant_fallback = self.fallback_filter.is_content_relevant(content)
            result.update(
                {
                    "is_relevant": is_relevant_fallback,
                    "confidence": 0.5,
                    "reasoning": "LLM not available, used keyword filtering",
                    "method": "fallback_only",
                }
            )

        else:
            result.update(
                {
                    "is_relevant": False,
                    "confidence": 0.0,
                    "reasoning": "No classification method available",
                    "method": "none",
                }
            )

        return result

    def filter_content_batch(self, content_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Filter a batch of content items using LLM classification.

        Args:
            content_list: List of content dictionaries

        Returns:
            List of filtered and classified content items
        """
        if not content_list:
            return []

        logger.info("🤖 LLM filtering %s content items...", len(content_list))

        filtered_content = []
        classification_stats = {
            "total": len(content_list),
            "llm_classified": 0,
            "fallback_classified": 0,
            "filtered_out": 0,
            "age_filtered": 0,
            "errors": 0,
        }

        # Process in batches if enabled
        if self.config.enable_batch_processing and len(content_list) > self.config.batch_size:
            batches = [
                content_list[i : i + self.config.batch_size]
                for i in range(0, len(content_list), self.config.batch_size)
            ]

            for batch_idx, batch in enumerate(batches):
                logger.info("📦 Processing batch %d/%d (%s items)", batch_idx + 1, len(batches), len(batch))

                for content in batch:
                    result = self.classify_content(content)
                    self._update_classification_stats(classification_stats, result)

                    if result["is_relevant"]:
                        # Add classification metadata to content
                        content["llm_classification"] = result
                        content["filtered_at"] = datetime.now().isoformat()
                        filtered_content.append(content)

        else:
            # Process all items individually
            for content in content_list:
                result = self.classify_content(content)
                self._update_classification_stats(classification_stats, result)

                if result["is_relevant"]:
                    # Add classification metadata to content
                    content["llm_classification"] = result
                    content["filtered_at"] = datetime.now().isoformat()
                    filtered_content.append(content)

        # Log classification statistics
        logger.info("📊 LLM Classification Results:")
        logger.info("   Total processed: %s", classification_stats["total"])
        logger.info("   LLM classified: %s", classification_stats["llm_classified"])
        logger.info("   Fallback classified: %s", classification_stats["fallback_classified"])
        logger.info("   Age filtered: %s", classification_stats["age_filtered"])
        logger.info("   Errors: %s", classification_stats["errors"])
        logger.info("   Final filtered: %s", len(filtered_content))
        logger.info("   Retention rate: %.1f%%", (len(filtered_content) / len(content_list)) * 100)

        return filtered_content

    def _update_classification_stats(self, stats: Dict[str, int], result: Dict[str, Any]) -> None:
        """Update classification statistics."""
        method = result.get("method", "unknown")

        if method == "age_filter":
            stats["age_filtered"] += 1
        elif method in ["llm", "llm_low_confidence"]:
            stats["llm_classified"] += 1
        elif method in ["fallback", "llm_fallback", "llm_error_fallback", "fallback_only"]:
            stats["fallback_classified"] += 1
        elif method in ["llm_error", "none"]:
            stats["errors"] += 1

        if not result["is_relevant"]:
            stats["filtered_out"] += 1

    def get_filter_stats(self) -> Dict[str, Any]:
        """Get filtering statistics and configuration."""
        return {
            "llm_filter_available": self.is_available(),
            "fallback_filter_available": self.fallback_filter is not None,
            "config": {
                "llm_provider": self.config.llm_provider,
                "model_name": self.config.model_name,
                "confidence_threshold": self.config.confidence_threshold,
                "max_retries": self.config.max_retries,
                "timeout_seconds": self.config.timeout_seconds,
                "batch_size": self.config.batch_size,
                "enable_batch_processing": self.config.enable_batch_processing,
                "fallback_to_keywords": self.config.fallback_to_keywords,
                "max_age_hours": self.config.max_age_hours,
            },
            "timestamp": datetime.now().isoformat(),
        }


def create_llm_content_filter(config: Optional[LLMFilteringConfig] = None) -> LLMContentFilter:
    """
    Factory function to create an LLM content filter.

    Args:
        config: Optional LLM filtering configuration

    Returns:
        LLMContentFilter instance
    """
    return LLMContentFilter(config)


if __name__ == "__main__":
    # Test the LLM content filter
    import os
    import logging

    # Set up logging
    logging.basicConfig(level=logging.INFO)

    # Create filter
    config = LLMFilteringConfig(llm_provider="openai", confidence_threshold=0.7, fallback_to_keywords=True)
    llm_filter = create_llm_content_filter(config)

    # Test content
    test_content = [
        {
            "title": "OpenAI Releases GPT-5 with Enhanced Reasoning Capabilities",
            "summary": "OpenAI has announced the release of GPT-5, featuring improved reasoning abilities and multimodal capabilities for AI developers.",
            "url": "https://openai.com/gpt-5",
            "source": "openai",
            "category": "AI Research",
            "published_at": "2025-10-08T10:00:00Z",
        },
        {
            "title": "New LangChain Update Simplifies Agent Development",
            "summary": "LangChain has released version 0.2.0 with new features for building autonomous agents and multi-agent systems.",
            "url": "https://langchain.com/updates",
            "source": "langchain",
            "category": "AI Development",
            "published_at": "2025-10-08T09:00:00Z",
        },
        {
            "title": "Stock Market Reaches New All-Time High",
            "summary": "The S&P 500 has reached a new all-time high as investors remain optimistic about economic growth and corporate earnings.",
            "url": "https://example.com/stock-news",
            "source": "cnn",
            "category": "Finance",
            "published_at": "2025-10-08T08:00:00Z",
        },
        {
            "title": "Vector Database Performance Optimization Techniques",
            "summary": "Learn advanced techniques for optimizing vector database performance in RAG applications and semantic search systems.",
            "url": "https://example.com/vector-db-guide",
            "source": "medium",
            "category": "AI Development",
            "published_at": "2025-10-08T07:00:00Z",
        },
    ]

    print("🧪 Testing LLM Content Filter...")
    print("=" * 50)

    if llm_filter.is_available():
        print("✅ LLM Filter is available")

        # Test individual classification
        print("\n🔍 Testing individual classifications:")
        for i, content in enumerate(test_content, 1):
            result = llm_filter.classify_content(content)
            print(f"{i}. {content['title'][:50]}...")
            print(f"   Relevant: {result['is_relevant']}")
            print(f"   Confidence: {result['confidence']:.2f}")
            print(f"   Method: {result['method']}")
            print(f"   Reasoning: {result['reasoning']}")
            print()

        # Test batch filtering
        print("\n📦 Testing batch filtering:")
        filtered_content = llm_filter.filter_content_batch(test_content)

        print(f"📊 Filtered {len(test_content)} items to {len(filtered_content)} relevant items")

        # Show filtered results
        for i, content in enumerate(filtered_content, 1):
            classification = content.get("llm_classification", {})
            print(f"{i}. {content['title']}")
            print(f"   Confidence: {classification.get('confidence', 0):.2f}")
            print(f"   Method: {classification.get('method', 'unknown')}")
            print()

    else:
        print("❌ LLM Filter is not available")
        print("   Make sure you have:")
        print("   - OPENAI_API_KEY or GEMINI_API_KEY environment variable set")
        print("   - Required libraries installed (openai or google-generativeai)")

    # Show filter stats
    stats = llm_filter.get_filter_stats()
    print("\n📈 Filter Statistics:")
    print(f"   LLM Available: {stats['llm_filter_available']}")
    print(f"   Fallback Available: {stats['fallback_filter_available']}")
    print(f"   Provider: {stats['config']['llm_provider']}")
    print(f"   Confidence Threshold: {stats['config']['confidence_threshold']}")
