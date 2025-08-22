# News Explorer PoC

Discover news and trends without predefined sources by exploring the open web.

## Goals

- Automatically discover trending topics and recent news without a curated source list
- Minimize bias by sampling SERPs and deduplicating content
- Produce structured JSON summaries (title, url, source, summary, published_at, topic, score)

## Approach (Plan)

1. Query generation
   - Seed with generic intents: "latest ai news", "trending machine learning", "breaking tech"
2. Web discovery
   - Uses Tavily Search (requires `TAVILY_API_KEY`) to fetch top links per query
   - Blocklist filters out social and irrelevant domains
3. Content fetching & extraction
   - Fetch pages with `requests` and parse with `trafilatura`
   - If extraction fails, falls back to Tavily snippet content
4. Scoring & ranking
   - Freshness, serp position, and domain reputation
5. Deduplication
   - By normalized title and URL hash
6. Output
   - JSON file with items and a topics summary

## Quick start

```bash
conda activate news-finder
poetry install --no-root
export TAVILY_API_KEY="your_tavily_key"
poetry run python PoC/news_explorer_poc/news_explorer.py
```

## Files

- `news_explorer.py` – main script (Tavily-only search)
- `blocklist.txt` – domains to skip (optional)
- `explorer_output_YYYYMMDD_HHMMSS.json` – results

## Notes

- Respects basic politeness with small delays
- Does not bypass paywalls or protected content
- Purely for PoC and research
