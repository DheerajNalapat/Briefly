# Briefly Bot 🚀

An intelligent AI/ML news aggregator that automatically collects, summarizes, and publishes daily news digests to Slack channels.

## Features

- **🤖 Dual LLM Support**: OpenAI GPT-3.5-turbo (default) + Gemini 1.5 Flash
- **📰 Multi-Source Collection**: ArXiv research papers + NewsAPI.org news
- **🧠 Smart TLDR Summarization**: AI-powered article summarization with fallback
- **💬 Rich Slack Integration**: Professional message formatting and delivery
- **🔄 Intelligent Fallback**: Automatic LLM switching for reliability
- **⚡ Configurable**: Customizable article limits and LLM providers

## Installation

```bash
poetry install --no-root
```

## Quick Start

```bash
# Activate environment
conda activate news-finder

# Test with OpenAI (default)
poetry run python main.py --dry-run

# Test with Gemini
poetry run python main.py --dry-run --llm-provider gemini

# Production run
poetry run python main.py
```

## Usage

The bot is designed to run as a scheduled service that aggregates news and publishes to Slack channels. See `README_MAIN.md` for detailed usage instructions.
