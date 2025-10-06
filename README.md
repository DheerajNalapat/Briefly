# NewsFinderBot 🚀

A comprehensive AI-powered news aggregation and summarization bot that automatically collects, processes, and publishes AI/ML news summaries to Slack channels. Built with a modular architecture for easy extension and customization.

## 🌟 Features

- **Multi-Source News Collection**: ArXiv research papers, NewsAPI articles, RSS feeds
- **AI-Powered Summarization**: OpenAI GPT and Google Gemini integration with smart fallback
- **Intelligent Content Processing**: Article reranking, categorization, and impact assessment
- **Slack Integration**: Rich message formatting with Block Kit components
- **Modular Architecture**: Extensible collector and processor system
- **Database Support**: PostgreSQL integration for data persistence
- **Production Ready**: Comprehensive logging, error handling, and monitoring

## 📁 Project Structure

```
NewsFinderBot/
├── main.py                    # Main application entry point
├── pyproject.toml            # Project dependencies and configuration
├── env.template              # Environment variables template
├── README.md                 # This file
├── README_MAIN.md            # Detailed main.py usage guide
├── ARCHITECTURE.md           # System architecture documentation
├── TLDR_STRUCTURE.md         # Summarization system documentation
└── slackbot/                 # Core bot implementation
    ├── collectors/           # News collection modules
    │   ├── arxiv_collector.py      # ArXiv research papers
    │   ├── newsapi_org_collector.py # NewsAPI.org articles
    │   ├── rss_collector.py        # RSS feed processing
    │   ├── base_collector.py       # Abstract base classes
    │   └── sources/                # Configuration files
    ├── services/            # High-level service interfaces
    │   ├── aggregation_service.py  # News aggregation
    │   ├── summarizer_service.py   # Content processing
    │   └── publisher_service.py     # Publishing coordination
    ├── summarizer/          # AI summarization modules
    │   ├── tldr_summarizer.py      # Main summarization logic
    │   ├── models.py              # Data models
    │   └── categories.py          # Content categorization
    ├── slack/              # Slack integration
    │   └── publisher.py            # Slack message publishing
    ├── utils/               # Utility modules
    │   └── reranker.py            # Content reranking
    ├── config.py           # Configuration management
    └── __init__.py         # Package initialization
```

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL database (optional)
- Slack App with bot token
- OpenAI API key (or Google Gemini API key)
- NewsAPI.org API key

### Installation

1. **Clone the repository**:

   ```bash
   git clone <repository-url>
   cd NewsFinderBot
   ```

2. **Set up conda environment** [[memory:6719036]]:

   ```bash
   conda activate news-finder
   ```

3. **Install dependencies**:

   ```bash
   poetry install --no-root
   ```

4. **Configure environment**:

   ```bash
   cp env.template .env
   # Edit .env with your API keys and configuration
   ```

5. **Run the bot**:

   ```bash
   # Test run (dry-run mode)
   poetry run python main.py --dry-run --verbose

   # Production run
   poetry run python main.py
   ```

## ⚙️ Configuration

### Environment Variables

Create a `.env` file with the following variables:

```bash
# News Sources (Required)
NEWSAPI_KEY=your_newsapi_key_here

# AI Provider Configuration (Choose one or both)
OPENAI_API_KEY=your_openai_key_here
GEMINI_API_KEY=your_gemini_key_here

# Slack Configuration (Required for publishing)
SLACK_BOT_TOKEN=xoxb-your-bot-token
SLACK_APP_TOKEN=xapp-your-app-token
SLACK_CHANNEL_ID=C1234567890

# Database Configuration (Optional)
DB_HOST=localhost
DB_PORT=5432
DB_NAME=news_finder
DB_USER=news_finder_user
DB_PASSWORD=your_password

# Logging Configuration
LOG_LEVEL=INFO
LOG_FILE=logs/news_finder_bot.log
LOG_CONSOLE=true
```

### News Sources Configuration

Configure news sources in `slackbot/collectors/sources/api_sources_config.yaml`:

```yaml
sources:
  - name: "ArXiv AI Papers"
    source_type: "arxiv"
    enabled: true
    max_items: 10
    query: "AI OR artificial intelligence OR machine learning"
    category: "Research Papers"
    update_interval: 3600

  - name: "Tech News AI"
    source_type: "newsapi"
    enabled: true
    max_items: 15
    query: "artificial intelligence"
    category: "Technology"
    update_interval: 1800
```

## 🎯 Usage

### Command Line Options

| Option            | Description                               | Default                         |
| ----------------- | ----------------------------------------- | ------------------------------- |
| `--dry-run`       | Test the flow without publishing to Slack | False                           |
| `--verbose`, `-v` | Enable verbose logging                    | False                           |
| `--max-articles`  | Maximum number of articles to process     | 20                              |
| `--channel`       | Target Slack channel ID                   | Uses `SLACK_CHANNEL_ID` env var |
| `--llm-provider`  | LLM provider for TLDR summarization       | `openai`                        |
| `--help`, `-h`    | Show help message                         | -                               |

### Basic Usage Examples

```bash
# Run with default settings (OpenAI)
poetry run python main.py

# Test without publishing to Slack
poetry run python main.py --dry-run --verbose

# Use Gemini for summarization
poetry run python main.py --llm-provider gemini

# Limit to 10 articles
poetry run python main.py --max-articles 10

# Specify different Slack channel
poetry run python main.py --channel C123456789
```

### Programmatic Usage

```python
from slackbot.services import AggregationService, ContentProcessingService, PublisherService

# Initialize services
aggregation_service = AggregationService()
processing_service = ContentProcessingService()
publisher_service = PublisherService()

# Collect news
news_items = aggregation_service.collect_all_news()

# Process and summarize
processed_content = processing_service.process_content(news_items)

# Publish to Slack
publisher_service.publish_content(processed_content)
```

## 🤖 AI Providers

The bot supports multiple LLM providers with intelligent fallback:

### **OpenAI (Default)** 🚀

- **Model**: GPT-3.5-turbo
- **Advantages**: Fast, reliable, consistent quality
- **Use Case**: Production environments, daily news digests

### **Gemini** 🌟

- **Model**: Gemini 1.5 Flash
- **Advantages**: Alternative AI perspective, Google's latest model
- **Use Case**: Testing, comparison, backup processing

### **Smart Fallback System** 🔄

- If the primary LLM fails, automatically tries the other
- If both LLMs fail, falls back to basic summarization
- Ensures the bot always produces summaries

## 📊 What the Bot Does

### 1. **News Collection** 📰

- Fetches articles from ArXiv (AI/ML research papers)
- Collects news from NewsAPI.org (technology, business, science, health)
- Configurable number of articles (default: 20)

### 2. **TLDR Summarization** 🧠

- Uses AI to create concise, structured summaries
- Generates key points, trending topics, and impact assessment
- Formats content for optimal Slack presentation

### 3. **Slack Message Creation** 💬

- Formats summaries into rich Slack blocks
- Includes article titles, TLDR summaries, and links
- Creates professional-looking news digest

### 4. **Slack Publishing** 📤

- Sends the formatted message to your Slack channel
- Provides delivery confirmation and message ID
- Handles errors gracefully

## 🔧 Development

### Adding New Collectors

1. Create a new collector class inheriting from `BaseCollector`:

```python
from slackbot.collectors.base_collector import BaseCollector

class CustomCollector(BaseCollector):
    def __init__(self, name: str = "Custom Collector"):
        super().__init__(name=name)
        # Initialize your collector

    def is_available(self) -> bool:
        # Check if collector is ready
        return True

    def collect(self, **kwargs) -> List[Dict[str, Any]]:
        # Implement collection logic
        return []
```

2. Add to `slackbot/collectors/__init__.py`:

```python
from .custom_collector import CustomCollector, create_custom_collector
```

### Adding New AI Providers

1. Extend the `TLDRSummarizer` class:

```python
from slackbot.summarizer.tldr_summarizer import TLDRSummarizer

class CustomAISummarizer(TLDRSummarizer):
    def __init__(self, provider: str = "custom"):
        super().__init__(provider=provider)
        # Initialize your AI provider
```

### Testing

```bash
# Run tests
poetry run python -m pytest tests/

# Test specific components
poetry run python scripts/test_collectors.py
poetry run python scripts/test_summarizer.py
```

## 🚀 Production Deployment

### Automated Execution

Set up a cron job or scheduler to run the bot daily:

```bash
# Example cron job (runs daily at 9 AM)
0 9 * * * cd /path/to/NewsFinderBot && conda activate news-finder && source .env && poetry run python main.py
```

### Monitoring

The bot creates log files with timestamps:

- `logs/briefly_bot_YYYYMMDD.log` - Daily log files
- Console output for real-time monitoring

### Performance

- **Collection**: ~30-60 seconds for 20 articles
- **Summarization**: ~2-5 seconds per article (AI) or ~0.1 seconds (fallback)
- **Total Runtime**: ~2-5 minutes for 20 articles

## 🔍 Troubleshooting

### Common Issues

1. **Missing Environment Variables**

   ```
   ❌ Missing required environment variables: ['NEWSAPI_KEY']
   ```

   **Solution**: Set the required environment variables in your `.env` file

2. **Slack Authentication Failed**

   ```
   ❌ Failed to initialize Slack app: token is invalid
   ```

   **Solution**: Check your Slack tokens and make sure they're valid

3. **AI API Rate Limits**

   ```
   ⚠️ Error creating article TLDR with Gemini: 429 You exceeded your current quota
   ```

   **Solution**: The bot will automatically fall back to basic summarization

4. **No Articles Collected**
   ```
   ❌ No articles collected - stopping
   ```
   **Solution**: Check your NewsAPI key and ArXiv connectivity

## 📈 Architecture

The bot follows a modular architecture with clear separation of concerns:

```
Scheduler (Cron / Cloud Function)
│
▼
[Data Collector] → [Database] → [Summarizer] → [Slack Publisher]
```

### Core Components

- **Collectors**: Modular news collection from various sources
- **Services**: High-level orchestration and business logic
- **Summarizers**: AI-powered content processing and summarization
- **Publishers**: Multi-platform content distribution
- **Utils**: Shared utilities and helpers

## 🔒 Security

- Environment variables for sensitive data
- Secure API key management
- Input validation and sanitization
- Rate limiting for API calls
- Error handling without data leakage

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For issues and questions:

1. Check the [Issues](https://github.com/your-repo/issues) page
2. Review the documentation files:
   - `README_MAIN.md` - Detailed main.py usage guide
   - `ARCHITECTURE.md` - System architecture documentation
   - `TLDR_STRUCTURE.md` - Summarization system documentation
3. Contact the maintainers

## 🔄 Changelog

### v0.1.0

- Initial release
- ArXiv and NewsAPI collectors
- OpenAI and Gemini summarization
- Slack integration
- Basic content processing pipeline
- Comprehensive documentation

---

**🎉 Ready to get started?** Check out the [Quick Start](#-quick-start) section above and begin collecting AI/ML news summaries for your Slack workspace!
