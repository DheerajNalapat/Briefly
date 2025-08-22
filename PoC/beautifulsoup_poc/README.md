# Generalized News Crawler PoC

This folder contains a proof-of-concept **generalized news crawling script** that demonstrates the core functionality for the Briefly Bot. The crawler is now **fully configurable** and can easily be extended with new news sources.

## 🚀 What's New - Generalized Crawling

The `news_crawler.py` script now features:

- **Configurable Sources**: Add/remove news sources without code changes
- **YAML Configuration**: Define sources in simple YAML files
- **Flexible Extraction**: CSS selectors for titles, links, and summaries
- **Multiple Categories**: Group sources by category (Technology, Research, Blog, etc.)
- **Rate Limiting**: Configurable delays per source
- **Easy Extension**: Add new sources in minutes

## 🎯 What it does

The `news_crawler.py` script:

- Crawls **multiple configurable news sources** using BeautifulSoup
- Extracts structured news data (title, link, source, category, summary)
- Creates comprehensive daily summaries in JSON format
- Implements intelligent deduplication logic
- Generates YAML configuration files for easy source management

## ⚙️ Quick Start

1. **Install dependencies** (already done via poetry):

   ```bash
   poetry install --no-root
   ```

2. **Run the crawler**:

   ```bash
   python news_crawler.py
   ```

3. **Check the output**:
   - Console output shows all configured sources and summary
   - JSON file is saved with timestamp (e.g., `daily_summary_20250819_045547.json`)
   - YAML configuration file is generated (`sources_config.yaml`)

## 🔧 Adding New News Sources

### Method 1: Edit the YAML Configuration

```yaml
sources:
  - name: "Your News Source"
    url: "https://example.com/ai-news"
    base_url: "https://example.com"
    title_selectors: ["h1", "h2", "h3"]
    link_selectors: ["a"]
    summary_selectors: ["p"]
    category: "Technology"
    delay: 2
```

### Method 2: Use the Example Configuration

```bash
# Copy the example and modify it
cp example_sources.yaml my_sources.yaml
# Edit my_sources.yaml with your sources
python news_crawler.py my_sources.yaml
```

### Method 3: Programmatically Add Sources

```python
from news_crawler import NewsCrawler, NewsSource

crawler = NewsCrawler()

# Add a new source
new_source = NewsSource(
    name="My Source",
    url="https://example.com",
    base_url="https://example.com",
    title_selectors=["h1", "h2"],
    link_selectors=["a"],
    summary_selectors=["p"],
    category="Technology",
    delay=2
)

crawler.add_source(new_source)
```

## 📊 Current Features

- ✅ **Generalized Web Crawling** with BeautifulSoup
- ✅ **Configurable News Sources** via YAML
- ✅ **Multiple Source Types**: Tech news, research papers, blogs
- ✅ **Structured Data Output** with metadata
- ✅ **JSON Summary Generation** with timestamps
- ✅ **YAML Configuration Export** for source management
- ✅ **Intelligent Logging** and error handling
- ✅ **Rate Limiting** per source (be respectful!)
- ✅ **Category Grouping** and source statistics

## 🎨 Source Configuration Options

| Option              | Description                      | Example                                |
| ------------------- | -------------------------------- | -------------------------------------- |
| `name`              | Display name for the source      | `"TechCrunch AI"`                      |
| `url`               | URL to crawl                     | `"https://techcrunch.com/tag/ai/"`     |
| `base_url`          | Base URL for resolving links     | `"https://techcrunch.com"`             |
| `title_selectors`   | CSS selectors for titles         | `["h1", "h2", "h3"]`                   |
| `link_selectors`    | CSS selectors for links          | `["a", "a[href*='/article/']"]`        |
| `summary_selectors` | CSS selectors for summaries      | `["p", "div.summary"]`                 |
| `category`          | Source category                  | `"Technology"`, `"Research"`, `"Blog"` |
| `delay`             | Delay between requests (seconds) | `2` (be respectful!)                   |

## 📁 Output Files

The script generates:

- **Daily Summary JSON**: `daily_summary_YYYYMMDD_HHMMSS.json`
- **Sources Configuration**: `sources_config.yaml`
- **Console Output**: Real-time crawling progress and summary

## 🔮 Next Steps for Full Bot

- Implement Slack API integration
- Add advanced content deduplication algorithms
- Create scheduling mechanism for daily runs
- Add content filtering and sentiment analysis
- Implement RSS feed support (feedparser integration)
- Add content summarization using AI models

## 🛠️ Troubleshooting

### Common Issues:

1. **No articles found**: Check CSS selectors in your configuration
2. **Rate limiting**: Increase `delay` values in your sources
3. **Invalid URLs**: Ensure `base_url` and `url` are correct
4. **Permission errors**: Check if the script can write to the current directory

### Debug Mode:

```python
import logging
logging.getLogger().setLevel(logging.DEBUG)
```

## 📚 Example Output

The crawler successfully extracts news from multiple sources:

- **TechCrunch AI**: 8 articles
- **VentureBeat AI**: 8 articles
- **MIT Technology Review**: 3 articles

Total: **19 unique news items** across **Technology** category
