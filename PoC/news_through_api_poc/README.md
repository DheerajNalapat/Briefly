# API News Collector PoC

This Proof of Concept demonstrates how to collect news and research papers using **APIs** instead of web scraping. It integrates three powerful APIs:

1. **ArXiv API** - For academic research papers and scientific publications
2. **NewsAPI.org** - For general news articles from various sources
3. **Papers with Code API** - For research papers with code implementations

## 🚀 Why APIs Over Web Scraping?

- **Reliability**: APIs are more stable than web scraping
- **Performance**: Faster data retrieval with structured responses
- **Rate Limiting**: Built-in rate limiting and respect for service terms
- **Data Quality**: Clean, structured data without HTML parsing
- **Scalability**: Easier to scale and maintain
- **Compliance**: Follows API terms of service and robots.txt

## ✨ Features

- **Multi-API Integration**: Combines ArXiv, NewsAPI.org, and Papers with Code
- **Configurable Sources**: YAML-based configuration for easy customization
- **Smart Caching**: Prevents duplicate content across runs
- **Rate Limiting**: Respectful API usage with configurable delays
- **Error Handling**: Robust error handling and logging
- **Structured Output**: Clean JSON format for easy processing
- **Update Intervals**: Configurable refresh rates for each source
- **Content Deduplication**: Hash-based deduplication across sources

## 🛠️ Quick Start

### 1. Environment Setup

First, activate your conda environment and install dependencies:

```bash
# Activate conda environment
conda activate news-finder

# Install dependencies using poetry
poetry add arxiv newsapi-python PyYAML
```

### 2. API Keys Setup

#### NewsAPI.org (Required for NewsAPI features)

1. Visit [NewsAPI.org](https://newsapi.org/)
2. Sign up for a free account
3. Get your API key
4. Set environment variable:

```bash
export NEWSAPI_KEY="your_api_key_here"
```

#### ArXiv API (No key required!)

- ArXiv provides free access without authentication
- Rate limits: 1 request per 3 seconds (automatically handled)

### 3. Run the Collector

```bash
cd PoC/news_through_api_poc
python api_news_collector.py
```

## 📁 Output Files

The script generates two main files:

1. **`api_news_summary_YYYYMMDD_HHMMSS.json`** - Complete news data
2. **`api_sources_config.yaml`** - Current source configuration

## 🔧 Configuration

### Adding New Sources

#### Method 1: YAML Configuration (Recommended)

Edit `example_api_sources.yaml` or create your own:

```yaml
sources:
  - name: "My Custom Source"
    source_type: "arxiv" # or "newsapi"
    enabled: true
    max_items: 10
    update_interval: 3600
    query: "your search query"
    category: "Custom Category"
```

#### Method 2: Programmatic Addition

```python
from api_news_collector import APINewsCollector, APINewsSource

collector = APINewsCollector()

# Add ArXiv source
arxiv_source = APINewsSource(
    name="Custom ArXiv",
    source_type="arxiv",
    query="deep learning OR neural networks",
    max_results=20,
    category="Deep Learning"
)

# Add NewsAPI source
news_source = APINewsSource(
    name="Custom News",
    source_type="newsapi",
    query="AI technology",
    category="technology",
    language="en",
    country="us"
)

collector.sources.extend([arxiv_source, news_source])
```

### Source Configuration Options

#### ArXiv Sources (`source_type: "arxiv"`)

- `query`: Search query string
- `max_results`: Maximum number of papers to fetch
- `sort_by`: Sort criterion (submittedDate, relevance, lastUpdatedDate)
- `sort_order`: Sort order (ascending, descending)

#### NewsAPI Sources (`source_type: "newsapi"`)

- `query`: Search keywords
- `category`: News category (technology, business, science, health, etc.)
- `language`: Language code (en, fr, de, etc.)
- `country`: Country code (us, gb, fr, etc.)
- `domains`: Specific domains to search (comma-separated)

#### Common Options (Both Types)

- `enabled`: Enable/disable source
- `max_items`: Maximum items to fetch
- `update_interval`: Refresh interval in seconds
- `category`: Custom category for organization

## 📊 Data Structure

Each news item contains:

```json
{
  "title": "Article Title",
  "link": "URL to article",
  "source": "Source name",
  "source_type": "arxiv or newsapi",
  "category": "Category",
  "summary": "Article summary/description",
  "published_date": "Publication date",
  "content_hash": "Unique content hash",
  "api_data": {
    "authors": ["Author 1", "Author 2"],
    "pdf_url": "PDF download link",
    "journal_ref": "Journal reference",
    "doi": "Digital Object Identifier"
  }
}
```

## 🔄 Update Intervals

Configure how often each source should be updated:

- **1800 seconds (30 min)**: High-frequency news sources
- **3600 seconds (1 hour)**: Standard news sources
- **7200 seconds (2 hours)**: Research papers
- **10800 seconds (3 hours)**: Low-frequency sources

## 🚦 Rate Limiting

The script includes built-in rate limiting:

- **ArXiv**: 0.1 second delay between requests
- **NewsAPI**: 1 second delay between sources

- **Overall**: Respects API rate limits automatically

## 🐛 Troubleshooting

### Common Issues

1. **NewsAPI Key Error**

   ```
   NEWSAPI_KEY environment variable not set
   ```

   - Set your API key: `export NEWSAPI_KEY="your_key"`
   - NewsAPI features will be disabled if key is missing

2. **Import Errors**

   ```
   ModuleNotFoundError: No module named 'arxiv'
   ```

   - Install dependencies: `poetry add arxiv newsapi-python PyYAML`

3. **Rate Limit Errors**

   ```
   Too Many Requests
   ```

   - Increase delays in the script
   - Check your API plan limits

4. **No Results**
   - Verify your search queries
   - Check if sources are enabled
   - Ensure API keys are valid

### Debug Mode

Enable detailed logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 🔮 Next Steps

1. **Slack Integration**: Send summaries to Slack channels
2. **Database Storage**: Store results in PostgreSQL/MongoDB
3. **Scheduling**: Run automatically with cron/APScheduler
4. **Web Interface**: Create a dashboard for monitoring
5. **Content Filtering**: Add keyword-based filtering
6. **Sentiment Analysis**: Analyze article sentiment
7. **Multi-language Support**: Support for multiple languages

## 📚 API Documentation

- **ArXiv API**: [arxiv.org/help/api](https://arxiv.org/help/api)
- **NewsAPI**: [newsapi.org/docs](https://newsapi.org/docs)
- **Python ArXiv**: [pypi.org/project/arxiv](https://pypi.org/project/arxiv)
- **Python NewsAPI**: [pypi.org/project/newsapi-python](https://pypi.org/project/newsapi-python)

## 🤝 Contributing

Feel free to:

- Add new API sources
- Improve error handling
- Enhance configuration options
- Add new output formats

## 📄 License

This PoC is part of the Briefly Bot project.
