"""
Article categories for LLM-based categorization.
"""

from enum import Enum


class ArticleCategory(Enum):
    """Article categories that the LLM can choose from."""

    # Core AI/ML Categories
    AI_RESEARCH = "AI Research"
    MACHINE_LEARNING = "Machine Learning"
    DEEP_LEARNING = "Deep Learning"
    NEURAL_NETWORKS = "Neural Networks"
    NATURAL_LANGUAGE_PROCESSING = "Natural Language Processing"
    COMPUTER_VISION = "Computer Vision"
    ROBOTICS = "Robotics"

    # AI Applications
    AI_APPLICATIONS = "AI Applications"
    AI_TOOLS = "AI Tools"
    AI_FRAMEWORKS = "AI Frameworks"
    AI_PLATFORMS = "AI Platforms"
    AI_SERVICES = "AI Services"

    # Industry & Business
    AI_INDUSTRY = "AI Industry"
    AI_BUSINESS = "AI Business"
    AI_STARTUPS = "AI Startups"
    AI_INVESTMENT = "AI Investment"
    AI_PARTNERSHIPS = "AI Partnerships"

    # Technology & Infrastructure
    AI_HARDWARE = "AI Hardware"
    AI_CHIPS = "AI Chips"
    AI_COMPUTING = "AI Computing"
    AI_CLOUD = "AI Cloud"
    AI_DATA = "AI Data"

    # Ethics & Policy
    AI_ETHICS = "AI Ethics"
    AI_SAFETY = "AI Safety"
    AI_POLICY = "AI Policy"
    AI_REGULATION = "AI Regulation"
    AI_BIAS = "AI Bias"

    # Research & Development
    AI_BREAKTHROUGHS = "AI Breakthroughs"
    AI_PAPERS = "AI Papers"
    AI_CONFERENCES = "AI Conferences"
    AI_OPEN_SOURCE = "AI Open Source"
    AI_STANDARDS = "AI Standards"

    # Emerging Technologies
    AGENTIC_AI = "Agentic AI"
    AUTONOMOUS_SYSTEMS = "Autonomous Systems"
    MULTI_AGENT_SYSTEMS = "Multi-Agent Systems"
    RAG_SYSTEMS = "RAG Systems"
    VECTOR_DATABASES = "Vector Databases"

    # Programming & Development
    AI_PROGRAMMING = "AI Programming"
    AI_APIS = "AI APIs"
    AI_DEVELOPMENT = "AI Development"
    AI_DEVOPS = "AI DevOps"
    AI_TESTING = "AI Testing"

    # General
    GENERAL_TECH = "General Tech"
    OTHER = "Other"


def get_category_descriptions() -> dict:
    """Get descriptions for each category to help the LLM choose correctly."""
    return {
        ArticleCategory.AI_RESEARCH: "Academic research, scientific papers, and theoretical advances in AI",
        ArticleCategory.MACHINE_LEARNING: "Machine learning algorithms, techniques, and methodologies",
        ArticleCategory.DEEP_LEARNING: "Deep learning models, neural networks, and deep learning techniques",
        ArticleCategory.NEURAL_NETWORKS: "Neural network architectures, training methods, and optimization",
        ArticleCategory.NATURAL_LANGUAGE_PROCESSING: "NLP models, language understanding, and text processing",
        ArticleCategory.COMPUTER_VISION: "Computer vision, image recognition, and visual AI systems",
        ArticleCategory.ROBOTICS: "Robotics, autonomous systems, and physical AI applications",
        ArticleCategory.AI_APPLICATIONS: "Real-world applications and use cases of AI technology",
        ArticleCategory.AI_TOOLS: "AI development tools, libraries, and software",
        ArticleCategory.AI_FRAMEWORKS: "AI frameworks, platforms, and development environments",
        ArticleCategory.AI_PLATFORMS: "AI platforms, cloud services, and infrastructure",
        ArticleCategory.AI_SERVICES: "AI-as-a-Service offerings and commercial AI services",
        ArticleCategory.AI_INDUSTRY: "AI industry news, market trends, and sector developments",
        ArticleCategory.AI_BUSINESS: "AI business strategies, corporate AI initiatives, and enterprise AI",
        ArticleCategory.AI_STARTUPS: "AI startup news, funding, and entrepreneurial developments",
        ArticleCategory.AI_INVESTMENT: "AI investment, funding rounds, and financial developments",
        ArticleCategory.AI_PARTNERSHIPS: "AI partnerships, collaborations, and strategic alliances",
        ArticleCategory.AI_HARDWARE: "AI hardware, processors, and specialized computing",
        ArticleCategory.AI_CHIPS: "AI chips, GPUs, TPUs, and specialized AI processors",
        ArticleCategory.AI_COMPUTING: "AI computing infrastructure, data centers, and processing",
        ArticleCategory.AI_CLOUD: "AI cloud services, distributed computing, and cloud AI",
        ArticleCategory.AI_DATA: "AI data, datasets, data processing, and data management",
        ArticleCategory.AI_ETHICS: "AI ethics, responsible AI, and ethical considerations",
        ArticleCategory.AI_SAFETY: "AI safety, alignment, and risk management",
        ArticleCategory.AI_POLICY: "AI policy, government initiatives, and public policy",
        ArticleCategory.AI_REGULATION: "AI regulation, legal frameworks, and compliance",
        ArticleCategory.AI_BIAS: "AI bias, fairness, and algorithmic bias issues",
        ArticleCategory.AI_BREAKTHROUGHS: "Major AI breakthroughs, discoveries, and innovations",
        ArticleCategory.AI_PAPERS: "Research papers, academic publications, and scientific literature",
        ArticleCategory.AI_CONFERENCES: "AI conferences, events, and academic gatherings",
        ArticleCategory.AI_OPEN_SOURCE: "Open source AI projects, contributions, and community",
        ArticleCategory.AI_STANDARDS: "AI standards, protocols, and industry standards",
        ArticleCategory.AGENTIC_AI: "Agentic AI, autonomous agents, and intelligent agents",
        ArticleCategory.AUTONOMOUS_SYSTEMS: "Autonomous systems, self-driving, and independent AI",
        ArticleCategory.MULTI_AGENT_SYSTEMS: "Multi-agent systems, swarm intelligence, and collaborative AI",
        ArticleCategory.RAG_SYSTEMS: "RAG systems, retrieval-augmented generation, and knowledge systems",
        ArticleCategory.VECTOR_DATABASES: "Vector databases, embeddings, and semantic search",
        ArticleCategory.AI_PROGRAMMING: "AI programming languages, coding, and development practices",
        ArticleCategory.AI_APIS: "AI APIs, integrations, and developer tools",
        ArticleCategory.AI_DEVELOPMENT: "AI development practices, methodologies, and best practices",
        ArticleCategory.AI_DEVOPS: "AI DevOps, MLOps, and AI operations",
        ArticleCategory.AI_TESTING: "AI testing, validation, and quality assurance",
        ArticleCategory.GENERAL_TECH: "General technology news that may relate to AI",
        ArticleCategory.OTHER: "Other topics that don't fit into specific categories",
    }


def get_category_choices() -> str:
    """Get a formatted string of category choices for the LLM prompt."""
    categories = []
    descriptions = get_category_descriptions()

    for category in ArticleCategory:
        categories.append(f"- {category.value}: {descriptions[category]}")

    return "\n".join(categories)
