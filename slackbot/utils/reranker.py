#!/usr/bin/env python3
"""
Reranker Utility for Briefly Bot

This utility provides intelligent ranking and prioritization of news articles
and research papers based on source type, recency, and other factors.
"""

import logging
from typing import List, Dict, Any, Optional, Callable
from datetime import datetime, timezone
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class RankingConfig:
    """Configuration for article ranking."""

    # Source type weights (higher = more priority)
    newsapi_weight: float = 1.0  # Highest priority for NewsAPI
    rss_weight: float = 0.8  # Medium priority for RSS
    arxiv_weight: float = 0.6  # Lower priority for ArXiv (max 3 articles)

    # Recency weights
    recency_weight: float = 0.3
    max_age_hours: int = 72  # Articles older than this get reduced weight

    # Content quality weights
    title_length_weight: float = 0.1
    summary_length_weight: float = 0.1

    # AI/ML relevance weights
    ai_ml_relevance_weight: float = 0.4  # High weight for AI/ML content
    agentic_systems_weight: float = 0.5  # Highest weight for agentic systems

    # Category weights (can be customized)
    category_weights: Dict[str, float] = None

    def __post_init__(self):
        if self.category_weights is None:
            self.category_weights = {
                # AI/ML and Agentic Systems (highest priority)
                "AI/ML Technology": 1.0,
                "AI/ML Development": 1.0,
                "AI Research & Development": 1.0,
                "AI Business & Technology": 0.95,
                "AI Technology": 0.95,
                "AI Industry News": 0.95,
                "AI Research & Industry": 0.95,
                "AI Research & Tools": 0.9,
                # Technology development
                "Technology & AI": 0.9,
                "Technology & Innovation": 0.85,
                "Computer Vision": 0.9,
                "Natural Language Processing": 0.9,
                "Robotics": 0.9,
                "Machine Learning": 1.0,
                "Deep Learning": 1.0,
                "Neural Networks": 1.0,
                "Transformer Models": 1.0,
                "Large Language Models": 1.0,
                "Agentic Systems": 1.0,
                "Autonomous Agents": 1.0,
                "Multi-Agent Systems": 1.0,
                # General categories
                "technology": 0.8,
                "business": 0.75,
                "science": 0.7,
                "health": 0.6,
                "Research Papers": 0.65,
            }


class ArticleReranker:
    """
    Intelligent reranker for news articles and research papers.

    Prioritizes NewsAPI articles over ArXiv papers and applies
    configurable ranking strategies.
    """

    def __init__(self, config: Optional[RankingConfig] = None):
        """
        Initialize the reranker.

        Args:
            config: Ranking configuration, uses defaults if None
        """
        self.config = config or RankingConfig()
        logger.info("Initializing ArticleReranker")

    def calculate_source_score(self, article: Dict[str, Any]) -> float:
        """
        Calculate score based on source type.

        Args:
            article: Article dictionary

        Returns:
            Source type score (higher = better)
        """
        source_type = article.get("source_type", "").lower()

        if source_type == "newsapi":
            return self.config.newsapi_weight
        elif source_type == "arxiv":
            return self.config.arxiv_weight
        elif source_type == "rss":
            return self.config.rss_weight
        else:
            # Default weight for unknown sources
            return 0.5

    def calculate_recency_score(self, article: Dict[str, Any]) -> float:
        """
        Calculate score based on article recency.

        Args:
            article: Article dictionary

        Returns:
            Recency score (higher = more recent)
        """
        try:
            # Try to parse published_at
            published_at = article.get("published_at")
            if not published_at:
                return 0.5  # Default score if no date

            # Parse the date (handle different formats)
            if isinstance(published_at, str):
                # Try different date formats
                for fmt in ["%Y-%m-%d", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M:%SZ"]:
                    try:
                        pub_date = datetime.strptime(published_at, fmt)
                        break
                    except ValueError:
                        continue
                else:
                    return 0.5  # Could not parse date
            else:
                pub_date = published_at

            # Calculate age in hours
            now = datetime.now(timezone.utc)
            if pub_date.tzinfo is None:
                pub_date = pub_date.replace(tzinfo=timezone.utc)

            age_hours = (now - pub_date).total_seconds() / 3600

            # Apply recency weight
            if age_hours <= self.config.max_age_hours:
                # Recent articles get full weight
                recency_score = 1.0 - (age_hours / self.config.max_age_hours) * 0.3
            else:
                # Older articles get reduced weight
                recency_score = 0.7 * (self.config.max_age_hours / age_hours)

            return recency_score * self.config.recency_weight

        except Exception as e:
            logger.warning(f"Error calculating recency score: {e}")
            return 0.5

    def calculate_content_score(self, article: Dict[str, Any]) -> float:
        """
        Calculate score based on content quality indicators.

        Args:
            article: Article dictionary

        Returns:
            Content quality score
        """
        score = 0.0

        # Title length score
        title = article.get("title", "")
        if title:
            title_length = len(title)
            if 20 <= title_length <= 100:  # Optimal title length
                score += self.config.title_length_weight
            elif title_length > 100:  # Too long
                score += self.config.title_length_weight * 0.5

        # Summary length score
        summary = article.get("summary", "")
        if summary:
            summary_length = len(summary)
            if 50 <= summary_length <= 500:  # Optimal summary length
                score += self.config.summary_length_weight
            elif summary_length > 500:  # Too long
                score += self.config.summary_length_weight * 0.7

        return score

    def calculate_category_score(self, article: Dict[str, Any]) -> float:
        """
        Calculate score based on article category.

        Args:
            article: Article dictionary

        Returns:
            Category score
        """
        category = article.get("category", "").lower()

        # Find best matching category
        best_score = 0.5  # Default score

        for cat_pattern, weight in self.config.category_weights.items():
            if cat_pattern.lower() in category or category in cat_pattern.lower():
                best_score = max(best_score, weight)

        return best_score

    def calculate_ai_ml_relevance_score(self, article: Dict[str, Any]) -> float:
        """
        Calculate score based on AI/ML relevance.

        Args:
            article: Article dictionary

        Returns:
            AI/ML relevance score
        """
        title = article.get("title", "").lower()
        summary = article.get("summary", "").lower()
        category = article.get("category", "").lower()

        # AI/ML and agentic systems keywords with weights
        ai_ml_keywords = {
            # Core AI/ML terms (highest weight)
            "artificial intelligence": 1.0,
            "ai": 1.0,
            "machine learning": 1.0,
            "ml": 1.0,
            "deep learning": 1.0,
            "neural network": 1.0,
            "transformer": 1.0,
            "gpt": 1.0,
            "llm": 1.0,
            "large language model": 1.0,
            # Agentic systems (highest weight)
            "agentic": 1.0,
            "autonomous agent": 1.0,
            "multi-agent": 1.0,
            "agent-based": 1.0,
            "intelligent agent": 1.0,
            "autonomous system": 1.0,
            "agent framework": 1.0,
            "agent orchestration": 1.0,
            # RAG and Vector Systems (highest weight)
            "rag": 1.0,
            "retrieval augmented generation": 1.0,
            "retrieval-augmented": 1.0,
            "vector database": 1.0,
            "vector search": 1.0,
            "embedding": 1.0,
            "semantic search": 1.0,
            "knowledge base": 1.0,
            "document retrieval": 1.0,
            "context window": 1.0,
            # LangChain and AI Frameworks
            "langchain": 1.0,
            "lang chain": 1.0,
            "llama index": 1.0,
            "haystack": 1.0,
            "transformers": 1.0,
            "hugging face": 1.0,
            "openai": 1.0,
            "anthropic": 1.0,
            "claude": 1.0,
            "gemini": 1.0,
            # Software Development & AI Engineering
            "software development": 0.95,
            "programming": 0.95,
            "coding": 0.95,
            "api": 0.9,
            "rest api": 0.9,
            "graphql": 0.9,
            "microservices": 0.9,
            "docker": 0.85,
            "kubernetes": 0.85,
            "devops": 0.85,
            "ci/cd": 0.85,
            "cloud computing": 0.85,
            "aws": 0.85,
            "azure": 0.85,
            "gcp": 0.85,
            # Programming Languages & Tools
            "python": 0.9,
            "javascript": 0.9,
            "typescript": 0.9,
            "java": 0.85,
            "go": 0.85,
            "rust": 0.85,
            "sql": 0.9,
            "nosql": 0.85,
            "mongodb": 0.85,
            "postgresql": 0.85,
            "redis": 0.85,
            # Advanced AI concepts
            "reinforcement learning": 0.95,
            "computer vision": 0.95,
            "natural language processing": 0.95,
            "nlp": 0.95,
            "robotics": 0.95,
            "automation": 0.9,
            "optimization": 0.9,
            "scalability": 0.9,
            "performance": 0.9,
            "model training": 0.95,
            "inference": 0.9,
            "deployment": 0.9,
            "mlops": 0.9,
            "model serving": 0.9,
            "a/b testing": 0.85,
            # Data & Analytics
            "data science": 0.95,
            "data engineering": 0.9,
            "etl": 0.85,
            "data pipeline": 0.9,
            "data warehouse": 0.85,
            "data lake": 0.85,
            "analytics": 0.9,
            "business intelligence": 0.85,
            "dashboard": 0.8,
            # Industry and research
            "startup": 0.8,
            "venture capital": 0.8,
            "investment": 0.8,
            "innovation": 0.85,
            "research": 0.9,
            "academic": 0.9,
            "paper": 0.9,
            "conference": 0.85,
            "workshop": 0.85,
            "competition": 0.8,
            "hackathon": 0.85,
            "open source": 0.9,
            "github": 0.85,
        }

        content = f"{title} {summary} {category}"
        max_score = 0.0

        for keyword, weight in ai_ml_keywords.items():
            if keyword in content:
                max_score = max(max_score, weight)

        return max_score * self.config.ai_ml_relevance_weight

    def calculate_total_score(self, article: Dict[str, Any]) -> float:
        """
        Calculate total ranking score for an article.

        Args:
            article: Article dictionary

        Returns:
            Total ranking score (higher = better)
        """
        source_score = self.calculate_source_score(article)
        recency_score = self.calculate_recency_score(article)
        content_score = self.calculate_content_score(article)
        category_score = self.calculate_category_score(article)
        ai_ml_relevance_score = self.calculate_ai_ml_relevance_score(article)

        # Combine scores with AI/ML focus
        total_score = (
            source_score * 0.3  # 30% weight for source type
            + ai_ml_relevance_score  # 25% weight for AI/ML relevance
            + recency_score  # 20% weight for recency
            + category_score * 0.15  # 15% weight for category
            + content_score * 0.1  # 10% weight for content quality
        )

        return total_score

    def rerank_articles(self, articles: List[Dict[str, Any]], strategy: str = "smart") -> List[Dict[str, Any]]:
        """
        Rerank articles based on specified strategy.

        Args:
            articles: List of article dictionaries
            strategy: Ranking strategy ('smart', 'source_priority', 'recency', 'custom')

        Returns:
            Reranked list of articles
        """
        if not articles:
            return []

        logger.info(f"🔄 Reranking {len(articles)} articles using strategy: {strategy}")

        if strategy == "smart":
            # Use all ranking factors
            scored_articles = []
            for article in articles:
                score = self.calculate_total_score(article)
                scored_articles.append((article, score))

            # Sort by score (highest first)
            scored_articles.sort(key=lambda x: x[1], reverse=True)

        elif strategy == "source_priority":
            # Only consider source type
            scored_articles = []
            for article in articles:
                score = self.calculate_source_score(article)
                scored_articles.append((article, score))

            scored_articles.sort(key=lambda x: x[1], reverse=True)

        elif strategy == "recency":
            # Only consider recency
            scored_articles = []
            for article in articles:
                score = self.calculate_recency_score(article)
                scored_articles.append((article, score))

            scored_articles.sort(key=lambda x: x[1], reverse=True)

        elif strategy == "custom":
            # Use custom ranking function if provided
            custom_ranker = getattr(self, "custom_ranking_function", None)
            if custom_ranker and callable(custom_ranker):
                scored_articles = []
                for article in articles:
                    score = custom_ranker(article)
                    scored_articles.append((article, score))

                scored_articles.sort(key=lambda x: x[1], reverse=True)
            else:
                logger.warning("Custom ranking strategy requested but no custom function found")
                return articles
        else:
            logger.warning(f"Unknown ranking strategy: {strategy}, returning original order")
            return articles

        # Extract articles from scored tuples
        reranked_articles = [article for article, score in scored_articles]

        # Log ranking summary
        if reranked_articles:
            top_source = reranked_articles[0].get("source_type", "unknown")
            top_source_name = reranked_articles[0].get("source", "unknown")
            logger.info(f"✅ Reranking complete. Top article: {top_source} - {top_source_name}")

        return reranked_articles

    def get_ranking_summary(self, articles: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Get a summary of article ranking statistics.

        Args:
            articles: List of article dictionaries

        Returns:
            Ranking summary dictionary
        """
        if not articles:
            return {"message": "No articles to analyze"}

        # Count by source type
        source_counts = {}
        category_counts = {}

        for article in articles:
            source_type = article.get("source_type", "unknown")
            source_counts[source_type] = source_counts.get(source_type, 0) + 1

            category = article.get("category", "unknown")
            category_counts[category] = category_counts.get(category, 0) + 1

        # Calculate average scores
        total_scores = []
        for article in articles:
            score = self.calculate_total_score(article)
            total_scores.append(score)

        avg_score = sum(total_scores) / len(total_scores) if total_scores else 0
        min_score = min(total_scores) if total_scores else 0
        max_score = max(total_scores) if total_scores else 0

        return {
            "total_articles": len(articles),
            "source_distribution": source_counts,
            "category_distribution": category_counts,
            "score_statistics": {
                "average": round(avg_score, 3),
                "minimum": round(min_score, 3),
                "maximum": round(max_score, 3),
            },
            "ranking_config": {
                "newsapi_weight": self.config.newsapi_weight,
                "arxiv_weight": self.config.arxiv_weight,
                "rss_weight": self.config.rss_weight,
                "recency_weight": self.config.recency_weight,
                "ai_ml_relevance_weight": self.config.ai_ml_relevance_weight,
                "agentic_systems_weight": self.config.agentic_systems_weight,
            },
        }


def create_article_reranker(config: Optional[RankingConfig] = None) -> ArticleReranker:
    """
    Factory function to create an ArticleReranker instance.

    Args:
        config: Optional ranking configuration

    Returns:
        ArticleReranker instance
    """
    return ArticleReranker(config)


if __name__ == "__main__":
    # Test the reranker
    import logging

    # Set up logging
    logging.basicConfig(level=logging.INFO)

    # Create test articles
    test_articles = [
        {
            "title": "AI Breakthrough in Computer Vision",
            "source_type": "newsapi",
            "source": "Tech News",
            "category": "technology",
            "published_at": "2025-08-24T10:00:00Z",
            "summary": "A major breakthrough in computer vision technology has been announced...",
        },
        {
            "title": "New Research on Transformer Architecture",
            "source_type": "arxiv",
            "source": "ArXiv AI Papers",
            "category": "Research Papers",
            "published_at": "2025-08-23T15:30:00Z",
            "summary": "This paper presents novel findings on transformer architecture...",
        },
        {
            "title": "Business Impact of AI in Healthcare",
            "source_type": "newsapi",
            "source": "Business News",
            "category": "business",
            "published_at": "2025-08-24T08:00:00Z",
            "summary": "Analysis of how AI is transforming healthcare business models...",
        },
        {
            "title": "Revolutionary Agentic AI Systems for Autonomous Decision Making",
            "source_type": "rss",
            "source": "TechCrunch AI",
            "category": "AI/ML Technology",
            "published_at": "2025-08-24T12:00:00Z",
            "summary": "New autonomous agent systems that can make complex decisions without human intervention...",
        },
        {
            "title": "Multi-Agent Reinforcement Learning in Robotics",
            "source_type": "rss",
            "source": "Medium AI/ML",
            "category": "AI/ML Development",
            "published_at": "2025-08-24T09:00:00Z",
            "summary": "Advanced multi-agent systems learning complex robotic tasks through reinforcement learning...",
        },
    ]

    # Create reranker
    reranker = create_article_reranker()

    # Test reranking
    print("🧪 Testing Article Reranker...")
    print("=" * 50)

    # Show original order
    print("📰 Original article order:")
    for i, article in enumerate(test_articles, 1):
        print(f"  {i}. {article['title']} ({article['source_type']})")

    print("\n🔄 Reranking articles...")
    reranked = reranker.rerank_articles(test_articles, strategy="smart")

    # Show reranked order
    print("\n📊 Reranked article order:")
    for i, article in enumerate(reranked, 1):
        score = reranker.calculate_total_score(article)
        print(f"  {i}. {article['title']} ({article['source_type']}) - Score: {score:.3f}")

    # Show ranking summary
    print("\n📈 Ranking Summary:")
    summary = reranker.get_ranking_summary(reranked)
    for key, value in summary.items():
        if key != "ranking_config":
            print(f"  {key}: {value}")

    print("\n⚙️ Ranking Configuration:")
    for key, value in summary["ranking_config"].items():
        print(f"  {key}: {value}")
