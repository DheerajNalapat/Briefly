## Minimalist Slack Bot Architecture

Scheduler (Cron / Cloud Function)
│
▼
[Data Collector] → [Database] → [Summarizer] → [Slack Publisher]

- Optional Extensions

             ┌───────────── User Query ─────────────┐
            ▼                                       ▼
       [Slack Bot Listener]                 [Real-time Data Collector]
            │                                       │
            └──────>  [Retriever (Vector DB + RAG)] ───────> [LLM Answer]

## Folder / Module Structure

slackbot/
│
├── main.py # Entry point (runs scheduler or bot listener)
│
├── config.py # Config (API keys, Slack tokens, DB connection)
│
├── collectors/ # Data Collection Layer
│ ├── **init**.py
│ ├── api_collector.py # API-based news collection
│ ├── rss_collector.py # Functions to fetch from RSS feeds (later)
│ ├── api_collector.py # Functions to fetch from APIs (NewsAPI, arXiv) (later)
│ └── scraper.py # (Optional) HTML scrapers
│
├── db/ # Persistence Layer
│ ├── **init**.py
│ ├── models.py # ORM models (SQLAlchemy / Peewee)
│ └── db_utils.py # CRUD helpers
│
├── summarizer/ # Summarization Layer
│ ├── **init**.py
│ └── summarize.py # Uses OpenAI/Gemini API to create TL;DR
│
├── slack/ # Slack Integration
│ ├── **init**.py
│ ├── publisher.py # Posts daily updates
│ └── listener.py # (Optional) Handles @bot queries
│
├── retriever/ # (Future) RAG Layer
│ ├── **init**.py
│ ├── embedder.py # Create embeddings (SentenceTransformers / OpenAI)
│ ├── vector_store.py # FAISS / Weaviate / Chroma
│ └── retriever.py # Query → similarity search → context return
│
└── utils/ # Utilities
├── logger.py # Logging
└── helpers.py # Shared helpers (dedup, formatting, etc.)

## ✅ Priorities

### **Phase 1 — MVP (Daily Digest Bot)**

- [x] **Data Collection**

  - Collect from RSS + APIs (NewsAPI, arXiv). (initially data collection should be mocked and dummy data can be used)
  - Normalize into schema (`title, url, source, published_at, content`).
  - Store in DB (Postgres).

- [x] **Summarization**

  - Use LLM (OpenAI/Gemini) to create a **short TL;DR digest**.
  - Aggregate into Markdown or Slack Block format.

- [x] **Slack Posting**

  - Use `slack_bolt` SDK.
  - Post daily digest in a channel (e.g., `#ai-updates`).

- [ ] **Scheduler**
  - Run `main.py run_daily` via cronjob / Cloud Scheduler.

## Instructions

- strictly stick to the plan
- keep the code clean and simple
- keep the code modular so that it is easily plugable and replaceable
