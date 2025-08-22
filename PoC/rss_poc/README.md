# RSS News Aggregator PoC

This folder contains a proof-of-concept **RSS-based news aggregator** that demonstrates how to fetch news from RSS feeds using the `feedparser` library. This approach is more efficient and reliable than web crawling for news aggregation.

## 🚀 What is RSS?

**RSS (Really Simple Syndication)** is a web feed format that allows websites to publish frequently updated content in a standardized, machine-readable format. Think of it as a "news wire" that websites use to broadcast their latest articles.

### **💡 Why RSS is Perfect for News Bots:**

- **Real-time Updates**: Get news as soon as it's published
- **Structured Data**: Clean, consistent format for parsing
- **Efficient**: Only fetch new content, not entire web pages
- **Respectful**: No need to crawl websites repeatedly
- **Standardized**: Works the same way across different news sources

### **📊 RSS vs Web Crawling:**

| Aspect            | RSS Feeds            | Web Crawling                   |
| ----------------- | -------------------- | ------------------------------ |
| **Speed**         | ⚡ Instant           | 🐌 Slower (parse HTML)         |
| **Reliability**   | ✅ Very reliable     | ⚠️ Can break with site changes |
| **Data Quality**  | 🎯 Clean, structured | 🔍 Variable, needs parsing     |
| **Rate Limiting** | ✅ No concerns       | ⚠️ Need to be respectful       |
| **Maintenance**   | ✅ Low maintenance   | 🔧 High maintenance            |

## 🎯 What the RSS Aggregator Does

The `rss_news_aggregator.py` script:

- Fetches news from **multiple configurable RSS feeds**
- Implements **intelligent caching** to avoid duplicates
- Provides **configurable update intervals** per source
- Creates **structured summaries** with metadata
- Supports **multiple categories** (Technology, Research, Blog, Business)
- Generates **JSON outputs** and **YAML configurations**

## ⚙️ Quick Start

1. **Install dependencies** (already done via poetry):

   ```bash
   poetry install --no-root
   ```

2. **Run the RSS aggregator**:

   ```bash
   python rss_news_aggregator.py
   ```

3. **Check the output**:
   - Console output shows all configured RSS sources and summary
   - JSON file is saved with timestamp (e.g., `rss_summary_20250819_045547.json`)
   - YAML configuration file is generated (`rss_sources_config.yaml`)

## 🔧 Adding New RSS Sources

### Method 1: Edit the YAML Configuration

```yaml
rss_sources:
  - name: "Your RSS Source"
    url: "https://example.com/feed/"
    category: "Technology"
    max_items: 8
    update_interval: 3600 # 1 hour
    enabled: true
```

### Method 2: Use the Example Configuration

```bash
# Copy the example and modify it
cp example_rss_sources.yaml my_rss_sources.yaml
# Edit my_rss_sources.yaml with your sources
python rss_news_aggregator.py my_rss_sources.yaml
```

### Method 3: Programmatically Add Sources

```python
from rss_news_aggregator import RSSNewsAggregator, RSSSource

aggregator = RSSNewsAggregator()

# Add a new RSS source
new_source = RSSSource(
    name="My RSS Source",
    url="https://example.com/feed/",
    category="Technology",
    max_items=8,
    update_interval=3600,
    enabled=True
)

aggregator.add_source(new_source)
```

## 📊 Current Features

- ✅ **RSS Feed Parsing** with feedparser library
- ✅ **Configurable RSS Sources** via YAML
- ✅ **Multiple Source Types**: Tech news, research papers, blogs, business
- ✅ **Intelligent Caching** and deduplication
- ✅ **Configurable Update Intervals** per source
- ✅ **Structured Data Output** with metadata
- ✅ **JSON Summary Generation** with timestamps
- ✅ **YAML Configuration Export** for source management
- ✅ **Category Grouping** and source statistics
- ✅ **Automatic Cache Cleanup**

## 🎨 RSS Source Configuration Options

| Option            | Description                 | Example                                 |
| ----------------- | --------------------------- | --------------------------------------- |
| `name`            | Display name for the source | `"TechCrunch AI"`                       |
| `url`             | RSS feed URL                | `"https://techcrunch.com/tag/ai/feed/"` |
| `category`        | Source category             | `"Technology"`, `"Research"`, `"Blog"`  |
| `max_items`       | Max items to fetch per feed | `8` (reasonable limit)                  |
| `update_interval` | Update frequency (seconds)  | `3600` (1 hour)                         |
| `enabled`         | Whether source is active    | `true` or `false`                       |

## 📁 Output Files

The script generates:

- **RSS Summary JSON**: `rss_summary_YYYYMMDD_HHMMSS.json`
- **Sources Configuration**: `rss_sources_config.yaml`
- **Console Output**: Real-time feed fetching progress and summary

## 🔮 Next Steps for Full Bot

- **Unified News Interface**: Combine RSS and web crawling results
- **Slack API Integration**: Publish summaries to Slack channels
- **Advanced Deduplication**: Cross-source duplicate detection
- **Content Summarization**: AI-powered article summaries
- **Scheduling System**: Automated daily news aggregation
- **Content Filtering**: Relevance scoring and filtering

## 🛠️ Troubleshooting

### Common Issues:

1. **No articles found**: Check if the RSS feed URL is valid
2. **Feed parsing errors**: Some feeds may have malformed XML
3. **Rate limiting**: RSS feeds don't have rate limits, but be respectful
4. **Invalid URLs**: Ensure the RSS feed URL is accessible

### Debug Mode:

```python
import logging
logging.getLogger().setLevel(logging.DEBUG)
```

### Testing RSS Feeds:

You can test RSS feed URLs in your browser to see if they're valid:

- `https://www.technologyreview.com/feed/ai/`
- `https://techcrunch.com/tag/artificial-intelligence/feed/`

## 📚 Example Output

The aggregator successfully fetches from multiple RSS sources:

- **MIT Technology Review AI**: Technology news
- **TechCrunch AI**: Startup and tech news
- **VentureBeat AI**: AI industry news
- **Ars Technica**: Technology lab news
- **Wired**: General tech news

## 🔗 Integration with BeautifulSoup Crawler

This RSS aggregator is designed to work alongside the BeautifulSoup web crawler:

- **RSS for reliable, fast news updates**
- **Web crawling for sources without RSS feeds**
- **Unified data format** for both approaches
- **Shared deduplication** and categorization

## 📖 RSS Feed Discovery

To find RSS feeds for news sources:

1. Look for RSS icons on websites
2. Check for `/feed/` or `/rss/` URLs
3. Search for "RSS" in site footers
4. Use RSS feed directories
5. Check if sites support RSS in their robots.txt
