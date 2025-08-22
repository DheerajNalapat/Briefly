# Scrapy News Crawler PoC

This folder contains a proof-of-concept **Scrapy-based news crawler** that demonstrates advanced web scraping capabilities using the Scrapy framework. Scrapy provides better performance, middleware support, and pipeline processing compared to simple BeautifulSoup crawling.

## 🕷️ What is Scrapy?

**Scrapy** is a fast, high-level web crawling and web scraping framework for Python. It's designed for extracting data from websites and provides:

- **Asynchronous requests** for high performance
- **Built-in middleware** for handling cookies, user agents, etc.
- **Pipeline system** for data processing and cleaning
- **Automatic throttling** and respect for robots.txt
- **Export to multiple formats** (JSON, CSV, XML)
- **Spider management** for different scraping strategies

### **💡 Why Scrapy is Superior for Production:**

| Aspect             | Scrapy               | BeautifulSoup   | RSS Feeds        |
| ------------------ | -------------------- | --------------- | ---------------- |
| **Performance**    | ⚡ Very Fast (async) | 🐌 Slow (sync)  | ⚡ Instant       |
| **Scalability**    | ✅ Highly scalable   | ⚠️ Limited      | ✅ Very scalable |
| **Middleware**     | ✅ Built-in support  | ❌ Manual setup | ✅ Not needed    |
| **Robots.txt**     | ✅ Automatic         | ❌ Manual       | ✅ Not needed    |
| **Error Handling** | ✅ Robust            | ⚠️ Basic        | ✅ Very reliable |
| **Data Pipelines** | ✅ Advanced          | ❌ None         | ✅ Basic         |

## 🎯 What the Scrapy Crawler Does

The `scrapy_news_spider.py` script:

- Uses **Scrapy framework** for high-performance web crawling
- Implements **multiple spiders** for different news sources
- Provides **pipeline processing** for data cleaning and deduplication
- Respects **robots.txt** and implements proper delays
- Creates **structured summaries** with metadata
- Supports **YAML configuration** for easy spider management

## ⚙️ Quick Start

1. **Install dependencies** (already done via poetry):

   ```bash
   poetry install --no-root
   ```

2. **Run the Scrapy crawler**:

   ```bash
   python scrapy_news_spider.py
   ```

3. **Check the output**:
   - Console output shows all configured spiders and summary
   - JSON file is saved with timestamp (e.g., `scrapy_summary_20250819_051623.json`)
   - Scrapy also generates `scrapy_news_output.json` automatically

## 🔧 Adding New Scrapy Spiders

### Method 1: Create a New Spider Class

```python
class MyNewsSpider(scrapy.Spider):
    """Spider for crawling My News Source."""

    name = 'my_news_source'
    allowed_domains = ['mynews.com']
    start_urls = ['https://mynews.com/ai-news/']

    custom_settings = {
        'ROBOTSTXT_OBEY': True,
        'DOWNLOAD_DELAY': 2,
        'CONCURRENT_REQUESTS_PER_DOMAIN': 1,
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }

    def parse(self, response):
        """Parse the page and extract news items."""
        # Your parsing logic here
        articles = response.css('article, div[class*="article"]')

        for article in articles[:10]:
            title = article.css('h1, h2, h3::text').get()
            link = article.css('a::attr(href)').get()
            summary = article.css('p::text').get()

            if title and link:
                news_item = NewsItem()
                news_item['title'] = title.strip()
                news_item['link'] = urljoin(response.url, link)
                news_item['summary'] = summary.strip() if summary else ""
                news_item['source'] = 'My News Source'
                news_item['category'] = 'Technology'
                news_item['extracted_at'] = datetime.now().isoformat()

                yield news_item
```

### Method 2: Edit the YAML Configuration

```yaml
scrapy_spiders:
  - name: "my_news_source"
    description: "My News Source spider"
    domain: "mynews.com"
    start_url: "https://mynews.com/ai-news/"
    category: "Technology"
    max_items: 10
    download_delay: 2
    enabled: true
```

### Method 3: Programmatically Add Spiders

```python
from scrapy_news_spider import ScrapyNewsCrawler, MyNewsSpider

crawler = ScrapyNewsCrawler()
crawler.spiders.append(MyNewsSpider)
```

## 📊 Current Features

- ✅ **Scrapy Framework Integration** with async crawling
- ✅ **Multiple Spider Classes** for different news sources
- ✅ **Pipeline Processing** for data cleaning and deduplication
- ✅ **Robots.txt Compliance** and respectful crawling
- ✅ **Configurable Download Delays** per spider
- ✅ **Structured Data Output** with metadata
- ✅ **JSON Summary Generation** with timestamps
- ✅ **YAML Configuration Support** for spider management
- ✅ **Automatic Deduplication** using content hashing
- ✅ **Error Handling** and logging

## 🎨 Spider Configuration Options

| Option           | Description                  | Example                                |
| ---------------- | ---------------------------- | -------------------------------------- |
| `name`           | Spider identifier            | `"techcrunch_ai"`                      |
| `description`    | Human-readable description   | `"TechCrunch AI news spider"`          |
| `domain`         | Domain to crawl              | `"techcrunch.com"`                     |
| `start_url`      | Starting URL for the spider  | `"https://techcrunch.com/tag/ai/"`     |
| `category`       | News category                | `"Technology"`, `"Research"`, `"Blog"` |
| `max_items`      | Max items to extract         | `10` (reasonable limit)                |
| `download_delay` | Delay between requests (sec) | `2` (be respectful!)                   |
| `enabled`        | Whether spider is active     | `true` or `false`                      |

## 📁 Output Files

The script generates:

- **Scrapy Summary JSON**: `scrapy_summary_YYYYMMDD_HHMMSS.json`
- **Scrapy Output JSON**: `scrapy_news_output.json` (automatic)
- **Console Output**: Real-time crawling progress and summary

## 🔮 Next Steps for Full Bot

- **Unified News Interface**: Combine Scrapy, RSS, and BeautifulSoup results
- **Slack API Integration**: Publish summaries to Slack channels
- **Advanced Spider Management**: Dynamic spider loading and configuration
- **Content Summarization**: AI-powered article summaries
- **Scheduling System**: Automated daily news aggregation
- **Content Filtering**: Relevance scoring and filtering

## 🛠️ Troubleshooting

### Common Issues:

1. **Import errors**: Ensure Scrapy is installed via poetry
2. **Spider not found**: Check spider names in configuration
3. **Rate limiting**: Increase `download_delay` values
4. **Robots.txt blocking**: Check if sites allow crawling

### Debug Mode:

```python
import logging
logging.getLogger().setLevel(logging.DEBUG)
```

### Scrapy Shell for Testing:

```bash
scrapy shell "https://example.com"
# Test selectors interactively
```

## 📚 Example Output

The crawler successfully extracts news from multiple sources:

- **TechCrunch AI**: Technology news
- **VentureBeat AI**: AI industry news
- **MIT Technology Review**: Academic tech news

## 🔗 Integration with Other Approaches

This Scrapy crawler is designed to work alongside:

- **RSS Aggregator**: For sources with RSS feeds
- **BeautifulSoup Crawler**: For simple HTML parsing needs
- **Unified News Interface**: Combined results from all methods

## 🚀 Scrapy Advantages

### **Performance Benefits:**

- **Asynchronous requests** for concurrent crawling
- **Built-in throttling** to respect server limits
- **Efficient memory usage** with streaming processing
- **Automatic retry logic** for failed requests

### **Production Features:**

- **Middleware support** for authentication, proxies, etc.
- **Pipeline processing** for data transformation
- **Export formats** (JSON, CSV, XML, databases)
- **Monitoring and logging** for production deployment

### **Respectful Crawling:**

- **Robots.txt compliance** by default
- **Configurable delays** between requests
- **User-agent management** for identification
- **Cookie and session handling**

## 📖 Scrapy Best Practices

1. **Always respect robots.txt** and site policies
2. **Use appropriate delays** between requests
3. **Implement proper error handling** for robust crawling
4. **Use pipelines** for data cleaning and validation
5. **Monitor memory usage** for long-running crawls
6. **Test selectors** in Scrapy shell before implementation
7. **Handle rate limiting** gracefully
8. **Log important events** for debugging

## 🎯 When to Use Scrapy vs Other Methods

- **Use Scrapy for**: High-volume, production crawling, complex sites, performance-critical applications
- **Use BeautifulSoup for**: Simple parsing, quick prototypes, one-off scripts
- **Use RSS for**: Sites with RSS feeds, real-time updates, low-maintenance solutions
