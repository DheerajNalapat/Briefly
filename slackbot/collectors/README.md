# News Collectors Package

This package provides various methods for collecting news and research content for the Briefly Bot. It's designed to be modular and extensible, allowing different collection methods to work together seamlessly.

## Overview

The collectors package consists of:

1. **Base Collector Interface** - Abstract base class that all collectors must implement
2. **API News Collector** - Collects news from APIs like ArXiv and NewsAPI.org
3. **Dummy Data Collector** - Provides test data for development and testing
4. **Collector Manager** - Coordinates multiple collectors and manages their execution

## Architecture

```
collectors/
├── __init__.py              # Package exports
├── base_collector.py        # Abstract base class and manager
├── api_collector.py         # API-based news collection
├── api_sources_config.yaml # Configuration for API sources
└── README.md               # This file
```

## Base Collector Interface

All collectors inherit from `BaseCollector` and must implement:

- `collect(**kwargs)` - Collect news items from the source
- `is_available()` - Check if the collector is ready to use

The base class provides:

- Statistics tracking (run count, success rate, etc.)
- Timing controls (when to run, update intervals)
- Error handling and logging
- Status reporting

## API News Collector

The `APINewsCollector` collects news from multiple API sources:

### Supported Sources

1. **ArXiv API** - Research papers and academic content

   - No API key required
   - Configurable queries and sorting
   - Automatic deduplication

2. **NewsAPI.org** - General news articles
   - Requires `NEWSAPI_KEY` environment variable
   - Category-based filtering
   - Geographic and language filtering

### Configuration

Sources are configured in `api_sources_config.yaml`:

```yaml
sources:
  - name: "ArXiv AI Papers"
    source_type: "arxiv"
    enabled: true
    max_items: 10
    query: "AI OR artificial intelligence OR machine learning"
    category: "Research Papers"
    update_interval: 3600 # 1 hour
```

### Environment Variables

```bash
# Required for NewsAPI
NEWSAPI_KEY=your_newsapi_key_here

# Optional: Override default configuration
NEWS_COLLECTOR_CONFIG_PATH=path/to/custom/config.yaml
```

## Collector Manager

The `CollectorManager` coordinates multiple collectors:

```python
from slackbot.collectors.base_collector import CollectorManager
from slackbot.collectors import create_api_collector

# Create manager
manager = CollectorManager()

# Add collectors
api_collector = create_api_collector()
manager.add_collector(api_collector)

# Run all collectors
results = manager.run_all_collectors()
```

## Usage Examples

### Basic API Collection

```python
from slackbot.collectors import create_api_collector

# Create collector with default sources
collector = create_api_collector()

# Collect news items
if collector.is_available():
    items = collector.collect()
    print(f"Collected {len(items)} news items")
```

### Custom Configuration

```python
# Use custom configuration file
collector = create_api_collector(
    config_file="path/to/custom_sources.yaml",
    name="Custom News Collector"
)
```

### Source Management

```python
# Enable/disable sources
collector.enable_source("ArXiv AI Papers")
collector.disable_source("Tech News AI")

# Get source status
status = collector.get_source_status()
for source in status:
    print(f"{source['name']}: {'Enabled' if source['enabled'] else 'Disabled'}")
```

### Integration with Summarizer

```python
from slackbot.collectors import create_api_collector
from slackbot.summarizer import create_tldr_summarizer

# Collect news
collector = create_api_collector()
news_items = collector.collect()

# Summarize
summarizer = create_tldr_summarizer()
tldr_summary = summarizer.create_tldr_digest(news_items)
```

## Testing

Run the test suite:

```bash
# Test API collector
poetry run python scripts/test_api_collector.py

# Test with conda environment
conda activate news-finder
poetry run python scripts/test_api_collector.py
```

## Dependencies

Required packages (install with Poetry):

```bash
poetry add arxiv newsapi-python pyyaml
```

Or install manually:

```bash
pip install arxiv newsapi-python pyyaml
```

## Adding New Collectors

To add a new collection method:

1. Create a new class inheriting from `BaseCollector`
2. Implement required methods (`collect`, `is_available`)
3. Add to the collectors package `__init__.py`
4. Create tests in `scripts/test_*.py`

Example:

```python
from .base_collector import BaseCollector

class RSSCollector(BaseCollector):
    def __init__(self, name: str = "RSS Collector"):
        super().__init__(name=name)
        # Initialize RSS client

    def is_available(self) -> bool:
        return self.rss_client is not None

    def collect(self, **kwargs) -> List[Dict[str, Any]]:
        # Implement RSS collection logic
        pass
```

## Configuration Files

### API Sources Configuration

The `api_sources_config.yaml` file supports:

- **Source Types**: `arxiv`, `newsapi`
- **Filtering**: Categories, languages, countries
- **Timing**: Update intervals, rate limiting
- **Queries**: Search terms and parameters

### Environment Overrides

Configuration can be overridden with environment variables:

```bash
# Override config file path
NEWS_COLLECTOR_CONFIG_PATH=/custom/path/config.yaml

# Override global settings
NEWS_MAX_ARTICLES=30
NEWS_CACHE_TTL=7200
```

## Error Handling

The collectors include comprehensive error handling:

- **API Failures**: Graceful degradation when APIs are unavailable
- **Rate Limiting**: Automatic delays between requests
- **Network Issues**: Retry logic and timeout handling
- **Data Validation**: Sanitization of collected content

## Performance Considerations

- **Caching**: Content deduplication prevents duplicate articles
- **Rate Limiting**: Configurable delays between API calls
- **Batch Processing**: Efficient handling of multiple sources
- **Memory Management**: Streaming processing for large datasets

## Monitoring and Logging

All collectors provide:

- **Statistics**: Run counts, success rates, error counts
- **Timing**: Execution duration and last run times
- **Logging**: Detailed logs for debugging and monitoring
- **Status**: Real-time availability and health information

## Future Enhancements

Planned features:

- **Web Scraping Collector** - For sites without APIs
- **Social Media Collector** - Twitter, Reddit, etc.
- **Database Collector** - From existing news databases
- **Streaming Collector** - Real-time news feeds
- **AI-Powered Collector** - Intelligent source selection
