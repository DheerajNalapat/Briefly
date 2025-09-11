# News Source Quality POC

Simple collectors for testing news source quality - includes RSS and NewsAPI collectors.

## RSS Collector

### Basic Usage

```python
from rss_collector import SimpleRSSCollector

# Create collector
collector = SimpleRSSCollector("my_articles.json")

# Collect from a single source
collector.run_single_source(
    source_name="BBC News",
    rss_url="https://feeds.bbci.co.uk/news/rss.xml",
    max_items=5
)
```

### Run from command line

```bash
python rss_collector.py
```

## NewsAPI Collector (HTTP Requests)

### Basic Usage

```python
from newsapi_collector import SimpleNewsAPICollector

# Create collector (you need a NewsAPI key)
collector = SimpleNewsAPICollector("your_api_key", "my_articles.json")

# Search for news using Everything endpoint (comprehensive)
collector.run_search("artificial intelligence", max_articles=5, sort_by="relevancy")

# Get top headlines (more accurate for breaking news)
collector.run_top_headlines(category="technology", max_articles=5)

# Search with specific sources (more accurate)
collector.run_search("AI", max_articles=3, sources="techcrunch,ars-technica")

# Get available news sources
collector.run_sources_search(category="technology")
```

## NewsAPI Client Collector (Official SDK)

### Basic Usage

```python
from newsapi_client_collector import NewsAPIClientCollector

# Create collector using official NewsAPI Python SDK
collector = NewsAPIClientCollector("your_api_key", "my_articles.json")

# Search for news using Everything endpoint (comprehensive)
collector.run_search("artificial intelligence", max_articles=5, sort_by="relevancy")

# Get top headlines (more accurate for breaking news)
collector.run_top_headlines(category="technology", max_articles=5)

# Search with specific sources (more accurate)
collector.run_search("AI", max_articles=3, sources="techcrunch,ars-technica")

# Get available news sources
collector.run_sources_search(category="technology")
```

### Run from command line

```bash
python newsapi_collector.py
python newsapi_client_collector.py
python demo_newsapi.py
```

## Event Registry Collector

### Basic Usage

```python
from eventregistry_collector import EventRegistryCollector

# Create collector (you need an Event Registry API key)
collector = EventRegistryCollector("your_api_key", "my_sources.json")

# Suggest news sources based on prefix
collector.run_suggest_sources("BBC")
```

### Run from command line

```bash
python eventregistry_collector.py
```

## Features

### RSS Collector

- Collect articles from RSS feeds one source at a time
- HTML to text conversion for clean summaries
- Append new articles to existing collection

### NewsAPI Collectors

**HTTP Requests Collector (`newsapi_collector.py`):**

- **Everything endpoint**: Comprehensive search across all sources
- **Top Headlines endpoint**: More accurate for breaking news
- **Sources endpoint**: Get available news sources
- Advanced parameters: sorting, domains, specific sources
- Multiple search methods for different use cases
- Append new articles to existing collection

**Client SDK Collector (`newsapi_client_collector.py`):**

- **Official NewsAPI Python SDK**: Cleaner, more maintainable code
- **Same functionality**: Everything, Top Headlines, Sources endpoints
- **Better error handling**: Built-in SDK error management
- **Easier parameter handling**: SDK handles request formatting
- **Categorized news fetching**: Same category-based collection
- **Append new articles to existing collection**

### Event Registry Collector

- **suggestSourcesFast endpoint**: Find news sources by prefix
- Source discovery and validation
- JSON response storage for analysis

### Both Collectors

- Save to JSON file with metadata in the same directory
- Simple error handling
- Rich article data (title, description, author, images, content)

## Output Format

Articles are saved with:

- title, link, published date, summary/description
- source name and RSS URL/query
- collection timestamp
