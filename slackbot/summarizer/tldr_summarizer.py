"""
TLDR summarizer using OpenAI (default) and Google Gemini (fallback) with LangChain support.
Creates Slack-friendly TLDR summaries of news articles.
"""

import os
import logging
from typing import List, Any, Optional, Literal
from datetime import datetime
import time

from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import ChatPromptTemplate
from langchain.output_parsers import PydanticOutputParser

from .models import TLDRSummary, SlackMessage, DailyDigestTLDR, ArticleTLDR
from .categories import ArticleCategory, get_category_choices
from slackbot.config import OPENAI_CONFIG, GEMINI_CONFIG

logger = logging.getLogger(__name__)


class TLDRSummarizer:
    """TLDR summarizer using OpenAI (default) and Gemini (fallback) with LangChain."""

    def __init__(
        self,
        llm_provider: Literal["openai", "gemini"] = "openai",
        api_key: Optional[str] = None,
        model_name: Optional[str] = None,
    ):
        """
        Initialize the TLDR summarizer.

        Args:
            llm_provider: LLM provider to use ("openai" or "gemini")
            api_key: API key for the specified provider. If None, will try to get from config
            model_name: Model to use. If None, will use default from config
        """
        self.llm_provider = llm_provider
        self.api_key = api_key
        self.model_name = model_name
        self.llm = None
        self.digest_parser = None
        self.article_parser = None
        self.fallback_llm = None

        # Initialize output parsers for structured summaries
        self.digest_parser = PydanticOutputParser(pydantic_object=DailyDigestTLDR)
        self.article_parser = PydanticOutputParser(pydantic_object=ArticleTLDR)

        # Initialize primary LLM
        self._initialize_primary_llm()

        # Initialize fallback LLM if different from primary
        if llm_provider == "openai":
            self._initialize_gemini_fallback()
        elif llm_provider == "gemini":
            self._initialize_openai_fallback()

    def _initialize_primary_llm(self):
        """Initialize the primary LLM based on the selected provider."""
        try:
            if self.llm_provider == "openai":
                self._initialize_openai_llm()
            elif self.llm_provider == "gemini":
                self._initialize_gemini_llm()
        except Exception as e:
            logger.error(f"Failed to initialize {self.llm_provider} LLM: {e}")
            self.llm = None

    def _initialize_openai_llm(self):
        """Initialize OpenAI LLM."""
        if not self.api_key:
            self.api_key = OPENAI_CONFIG["api_key"]

        if not self.model_name:
            self.model_name = OPENAI_CONFIG["model"]

        if not self.api_key:
            logger.warning("No OpenAI API key provided.")
            return

        if not self.model_name:
            logger.warning("No OpenAI model name provided.")
            return

        self.llm = ChatOpenAI(
            model=self.model_name,
            openai_api_key=self.api_key,
            temperature=0.3,
            max_tokens=2048,
        )

        logger.info(f"Initialized OpenAI TLDR summarizer with model: {self.model_name}")

    def _initialize_gemini_llm(self):
        """Initialize Gemini LLM."""
        if not self.api_key:
            self.api_key = GEMINI_CONFIG["api_key"]

        if not self.model_name:
            self.model_name = GEMINI_CONFIG["model"]

        if not self.api_key:
            logger.warning("No Google AI API key provided.")
            return

        if not self.model_name:
            logger.warning("No Gemini model name provided.")
            return

        self.llm = ChatGoogleGenerativeAI(
            model=self.model_name,
            google_api_key=self.api_key,
            temperature=0.3,
            max_output_tokens=2048,
        )

        logger.info(f"Initialized Gemini TLDR summarizer with model: {self.model_name}")

    def _initialize_openai_fallback(self):
        """Initialize OpenAI as fallback LLM."""
        try:
            if OPENAI_CONFIG["api_key"]:
                self.fallback_llm = ChatOpenAI(
                    model=OPENAI_CONFIG["model"],
                    openai_api_key=OPENAI_CONFIG["api_key"],
                    temperature=0.3,
                    max_tokens=2048,
                )
                logger.info(f"Initialized OpenAI fallback with model: {OPENAI_CONFIG['model']}")
        except Exception as e:
            logger.warning(f"Failed to initialize OpenAI fallback: {e}")

    def _initialize_gemini_fallback(self):
        """Initialize Gemini as fallback LLM."""
        try:
            if GEMINI_CONFIG["api_key"]:
                self.fallback_llm = ChatGoogleGenerativeAI(
                    model=GEMINI_CONFIG["model"],
                    google_api_key=GEMINI_CONFIG["api_key"],
                    temperature=0.3,
                    max_output_tokens=2048,
                )
                logger.info(f"Initialized Gemini fallback with model: {GEMINI_CONFIG['model']}")
        except Exception as e:
            logger.warning(f"Failed to initialize Gemini fallback: {e}")

    def is_available(self) -> bool:
        """Check if the summarizer is available and ready to use."""
        return self.llm is not None

    def _try_fallback_llm(self) -> bool:
        """Try to use fallback LLM if primary LLM fails."""
        if self.fallback_llm and not self.llm:
            logger.info(f"Switching to {self.llm_provider} fallback LLM")
            self.llm = self.fallback_llm
            return True
        return False

    def create_tldr_digest(self, articles: List[Any]) -> TLDRSummary:
        """
        Create a TLDR daily digest summary from multiple articles using Gemini.

        Args:
            articles: List of articles to summarize

        Returns:
            TLDRSummary with Slack-friendly format
        """
        if not articles:
            return self._create_empty_tldr()

        if not self.is_available():
            # Try fallback LLM first
            if self._try_fallback_llm():
                logger.info(f"Using {self.llm_provider} fallback LLM")
            else:
                logger.warning("No LLM available, using basic fallback TLDR")
                return self._create_basic_tldr(articles)

        try:
            start_time = time.time()

            # Prepare articles for summarization
            articles_text = self._prepare_articles_for_tldr(articles)

            # Create structured TLDR using Gemini
            prompt = ChatPromptTemplate.from_messages(
                [
                    (
                        "system",
                        "You are an expert AI news analyst creating TLDR summaries for Slack. "
                        "Focus on brevity, clarity, and actionable insights. Use casual, engaging language "
                        "suitable for busy professionals. Always provide concise, scannable summaries.",
                    ),
                    (
                        "human",
                        "Create a TLDR daily digest for these AI/ML news articles:\n\n{articles_text}\n\n{format_instructions}",
                    ),
                ]
            )

            # Create the chain and invoke it
            chain = prompt | self.llm | self.digest_parser
            result = chain.invoke(
                {
                    "articles_text": articles_text,
                    "format_instructions": self.digest_parser.get_format_instructions(),
                }
            )
            print(f"🔍 Result type: {type(result)}")
            processing_time = time.time() - start_time

            # Extract key information
            categories = list(set(article.get("category", "Unknown") for article in articles))
            sources = list(set(article.get("source", "Unknown") for article in articles))

            # Create TLDR summary
            return TLDRSummary(
                tldr_text=result.tldr_summary,
                key_points=result.top_headlines,
                trending_topics=result.trending_topics,
                impact_level=self._extract_impact_level(result.impact_assessment),
                reading_time=f"{len(articles) * 2} min read",
                article_count=len(articles),
                categories=categories,
                sources=sources,
                generated_at=datetime.now().isoformat(),
                model_used=self.model_name,
                emoji="🚀",
                color="#ff6b6b",  # Red for daily digest
            )

        except Exception as e:
            logger.error(f"Error creating TLDR digest with {self.llm_provider}: {e}")

            # Try fallback LLM if available
            if self._try_fallback_llm():
                logger.info(f"Retrying with {self.llm_provider} fallback LLM")
                try:
                    # Retry with fallback LLM
                    chain = prompt | self.llm | self.digest_parser
                    result = chain.invoke(
                        {
                            "articles_text": articles_text,
                            "format_instructions": self.digest_parser.get_format_instructions(),
                        }
                    )

                    # Extract key information
                    categories = list(set(article.get("category", "Unknown") for article in articles))
                    sources = list(set(article.get("source", "Unknown") for article in articles))

                    # Create TLDR summary
                    return TLDRSummary(
                        tldr_text=result.tldr_summary,
                        key_points=result.top_headlines,
                        trending_topics=result.trending_topics,
                        impact_level=self._extract_impact_level(result.impact_assessment),
                        reading_time=f"{len(articles) * 2} min read",
                        article_count=len(articles),
                        categories=categories,
                        sources=sources,
                        generated_at=datetime.now().isoformat(),
                        model_used=f"{self.llm_provider}_fallback",
                        emoji="🚀",
                        color="#ff6b6b",  # Red for daily digest
                    )
                except Exception as fallback_e:
                    logger.error(f"Fallback LLM also failed: {fallback_e}")
                    return self._create_basic_tldr(articles)
            else:
                return self._create_basic_tldr(articles)

    def create_article_tldr(self, article: Any) -> TLDRSummary:
        """
        Create a TLDR summary for a single article using Gemini.

        Args:
            article: Article to summarize

        Returns:
            TLDRSummary for the article
        """
        if not self.is_available():
            # Try fallback LLM first
            if self._try_fallback_llm():
                logger.info(f"Using {self.llm_provider} fallback LLM")
            else:
                logger.warning("No LLM available, using basic fallback TLDR")
                return self._create_single_article_basic_tldr(article)

        try:
            # Create structured TLDR using the LLM
            prompt = ChatPromptTemplate.from_messages(
                [
                    (
                        "system",
                        "You are an expert AI news analyst creating TLDR summaries. "
                        "Focus on the key facts, why it matters, and make it engaging for busy professionals. "
                        "Keep it concise and actionable. "
                        "You must also categorize the article into one of the predefined categories.",
                    ),
                    (
                        "human",
                        "Create a TLDR summary for this article:\n\nTitle: {title}\nContent: {content}\n\n"
                        "Available categories:\n{category_choices}\n\n"
                        "Choose the most appropriate category for this article.\n\n"
                        "{format_instructions}",
                    ),
                ]
            )

            # Create the chain and invoke it
            chain = prompt | self.llm | self.article_parser
            result = chain.invoke(
                {
                    "title": article.get("title", "Unknown Title"),
                    "content": article.get("content", article.get("summary", "No content available")),
                    "category_choices": get_category_choices(),
                    "format_instructions": self.article_parser.get_format_instructions(),
                }
            )

            # Create TLDR summary
            return TLDRSummary(
                tldr_text=result.tldr,
                key_points=result.key_facts,
                trending_topics=[result.category],  # Use LLM-generated category
                impact_level="Medium",  # Default for single articles
                reading_time=result.reading_time,
                article_count=1,
                categories=[result.category],  # Use LLM-generated category
                sources=[article.get("source", "Unknown")],
                generated_at=datetime.now().isoformat(),
                model_used=self.model_name,
                emoji="📰",
                color="#36a64f",  # Green for articles
            )

        except Exception as e:
            logger.error(f"Error creating article TLDR with {self.llm_provider}: {e}")

            # Try fallback LLM if available
            if self._try_fallback_llm():
                logger.info(f"Retrying with {self.llm_provider} fallback LLM")
                try:
                    # Retry with fallback LLM
                    chain = prompt | self.llm | self.article_parser
                    result = chain.invoke(
                        {
                            "title": article.get("title", "Unknown Title"),
                            "content": article.get("content", article.get("summary", "No content available")),
                            "category_choices": get_category_choices(),
                            "format_instructions": self.article_parser.get_format_instructions(),
                        }
                    )

                    # Create TLDR summary
                    return TLDRSummary(
                        tldr_text=result.tldr,
                        key_points=result.key_facts,
                        trending_topics=[result.category],  # Use LLM-generated category
                        impact_level="Medium",  # Default for single articles
                        reading_time=result.reading_time,
                        article_count=1,
                        categories=[result.category],  # Use LLM-generated category
                        sources=[article.get("source", "Unknown")],
                        generated_at=datetime.now().isoformat(),
                        model_used=f"{self.llm_provider}_fallback",
                        emoji="📰",
                        color="#36a64f",  # Green for single articles
                    )
                except Exception as fallback_e:
                    logger.error(f"Fallback LLM also failed: {fallback_e}")
                    return self._create_single_article_basic_tldr(article)
            else:
                return self._create_single_article_basic_tldr(article)

    def create_slack_message(self, tldr_summary: TLDRSummary) -> SlackMessage:
        """
        Convert TLDR summary to Slack message format with rich formatting.

        Args:
            tldr_summary: TLDR summary to convert

        Returns:
            SlackMessage ready for posting
        """
        # Create main text
        main_text = f"{tldr_summary.emoji} *AI/ML News TLDR*\n\n{tldr_summary.tldr_text}"

        # Create blocks for rich formatting
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"{tldr_summary.emoji} AI/ML News TLDR",
                    "emoji": True,
                },
            },
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": tldr_summary.tldr_text},
            },
        ]

        # Add key points
        if tldr_summary.key_points:
            blocks.append(
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "*Key Points:*\n" + "\n".join(f"• {point}" for point in tldr_summary.key_points[:3]),
                    },
                }
            )

        # Add trending topics
        if tldr_summary.trending_topics:
            blocks.append(
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "*Trending:* " + ", ".join(tldr_summary.trending_topics[:3]),
                    },
                }
            )

        # Add metadata
        blocks.append(
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": f"📊 {tldr_summary.article_count} articles | 🎯 {tldr_summary.impact_level} impact | ⏱️ {tldr_summary.reading_time}",
                    }
                ],
            }
        )

        # Create attachments for color
        attachments = [
            {
                "color": tldr_summary.color,
                "footer": f"Generated at {tldr_summary.generated_at} using {tldr_summary.model_used}",
            }
        ]

        return SlackMessage(text=main_text, blocks=blocks, attachments=attachments)

    def _create_empty_tldr(self) -> TLDRSummary:
        """Create TLDR summary for empty article list."""
        return TLDRSummary(
            tldr_text="No articles to summarize today.",
            key_points=[],
            trending_topics=[],
            impact_level="Low",
            reading_time="0 min read",
            article_count=0,
            categories=[],
            sources=[],
            generated_at=datetime.now().isoformat(),
            model_used="none",
            emoji="😴",
            color="#cccccc",
        )

    def _create_basic_tldr(self, articles: List[Any]) -> TLDRSummary:
        """Create basic TLDR when Gemini is not available."""
        categories = list(set(article.get("category", "Unknown") for article in articles))
        sources = list(set(article.get("source", "Unknown") for article in articles))

        # Create simple TLDR text
        tldr_text = f"📰 *Daily AI/ML News Roundup*\n\n"
        tldr_text += f"Today's top {len(articles)} stories covering {', '.join(categories[:3])}.\n"
        tldr_text += f"Key sources: {', '.join(sources[:3])}"

        # Extract key points from titles
        key_points = [article.get("title", "Unknown")[:100] + "..." for article in articles[:5]]

        return TLDRSummary(
            tldr_text=tldr_text,
            key_points=key_points,
            trending_topics=categories[:3],
            impact_level="Medium",
            reading_time=f"{len(articles) * 2} min read",
            article_count=len(articles),
            categories=categories,
            sources=sources,
            generated_at=datetime.now().isoformat(),
            model_used="basic_fallback",
            emoji="📰",
            color="#36a64f",
        )

    def _create_single_article_basic_tldr(self, article: Any) -> TLDRSummary:
        """Create basic TLDR for single article when Gemini is not available."""
        title = article.get("title", "Unknown Title")
        summary = article.get("summary", article.get("content", "No summary available"))

        tldr_text = f"📰 *{title}*\n\n{summary}"

        return TLDRSummary(
            tldr_text=tldr_text,
            key_points=[title],
            trending_topics=[article.get("category", "AI/ML")],
            impact_level="Medium",
            reading_time="2 min read",
            article_count=1,
            categories=[article.get("category", "Unknown")],
            sources=[article.get("source", "Unknown")],
            generated_at=datetime.now().isoformat(),
            model_used="basic_fallback",
            emoji="📰",
            color="#36a64f",
        )

    def _prepare_articles_for_tldr(self, articles: List[Any]) -> str:
        """Prepare articles text for TLDR summarization."""
        articles_text = ""
        for i, article in enumerate(articles, 1):
            articles_text += f"Article {i}:\n"
            articles_text += f"Title: {article.get('title', 'Unknown')}\n"
            articles_text += f"Source: {article.get('source', 'Unknown')}\n"
            articles_text += f"Category: {article.get('category', 'Unknown')}\n"
            articles_text += f"Summary: {article.get('summary', 'No summary')}\n"
            content = article.get("content", article.get("summary", "No content"))
            articles_text += f"Content: {content[:300]}...\n\n"
        print(f"🔍 Articles text: {articles_text}")
        return articles_text

    def _extract_impact_level(self, impact_text: str) -> str:
        """Extract impact level from impact assessment text."""
        impact_text = impact_text.lower()
        if any(word in impact_text for word in ["high", "significant", "major", "breakthrough"]):
            return "High"
        elif any(word in impact_text for word in ["medium", "moderate", "notable"]):
            return "Medium"
        else:
            return "Low"


def create_tldr_summarizer(
    llm_provider: Literal["openai", "gemini"] = "openai",
    api_key: Optional[str] = None,
    model_name: Optional[str] = None,
) -> TLDRSummarizer:
    """
    Factory function to create a TLDR summarizer instance.

    Args:
        llm_provider: LLM provider to use ("openai" or "gemini")
        api_key: API key for the specified provider
        model_name: Model to use for the specified provider

    Returns:
        TLDRSummarizer instance
    """
    return TLDRSummarizer(llm_provider=llm_provider, api_key=api_key, model_name=model_name)


if __name__ == "__main__":
    # Test the TLDR summarizer
    print("🧪 TLDR Summarizer Test Mode")
    print("=" * 40)

    # Set up logging
    logging.basicConfig(level=logging.INFO)

    # Test OpenAI summarizer (default)
    print("🔍 Testing OpenAI Summarizer...")
    openai_summarizer = create_tldr_summarizer(llm_provider="openai")

    if openai_summarizer.is_available():
        print("✅ OpenAI TLDR Summarizer initialized successfully")
    else:
        print("⚠️ OpenAI TLDR Summarizer not available - check OPENAI_API_KEY")

    # Test Gemini summarizer
    print("\n🔍 Testing Gemini Summarizer...")
    gemini_summarizer = create_tldr_summarizer(llm_provider="gemini")

    if gemini_summarizer.is_available():
        print("✅ Gemini TLDR Summarizer initialized successfully")
    else:
        print("⚠️ Gemini TLDR Summarizer not available - check GEMINI_API_KEY")

    print("\n💡 Use test scripts in the scripts/ folder to test with real data")
