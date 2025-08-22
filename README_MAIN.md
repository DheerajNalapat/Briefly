# Briefly Bot - Main Application

This is the main entry point for the Briefly Bot application that orchestrates the complete flow: **News Collection → TLDR Summarization → Slack Publishing**.

## 🚀 Quick Start

### Prerequisites

1. **Environment Setup**: Make sure you have the required environment variables set
2. **Conda Environment**: Activate the `news-finder` conda environment
3. **Dependencies**: Install dependencies with `poetry install --no-root`

### Basic Usage

```bash
# Activate conda environment
conda activate news-finder

# Source environment variables
source .env

# Run with default settings (collects 20 articles and publishes to Slack)
poetry run python main.py

# Test the flow without publishing to Slack (dry run)
poetry run python main.py --dry-run

# Enable verbose logging
poetry run python main.py --verbose

# Limit to 10 articles
poetry run python main.py --max-articles 10

# Specify a different Slack channel
poetry run python main.py --channel C123456789

# Use Gemini instead of OpenAI for TLDR summarization
poetry run python main.py --llm-provider gemini
```

## 📋 Command Line Options

| Option            | Description                               | Default                         |
| ----------------- | ----------------------------------------- | ------------------------------- |
| `--dry-run`       | Test the flow without publishing to Slack | False                           |
| `--verbose`, `-v` | Enable verbose logging                    | False                           |
| `--max-articles`  | Maximum number of articles to process     | 20                              |
| `--channel`       | Target Slack channel ID                   | Uses `SLACK_CHANNEL_ID` env var |
| `--llm-provider`  | LLM provider for TLDR summarization       | `openai`                        |
| `--help`, `-h`    | Show help message                         | -                               |

## 🔧 Environment Variables

### Required

- `NEWSAPI_KEY`: Your NewsAPI.org API key

### Required for LLM Services

- `OPENAI_API_KEY`: Your OpenAI API key (for GPT-3.5-turbo)
- `GEMINI_API_KEY`: Your Google AI API key (for Gemini 1.5 Flash)

### Required for Slack Publishing (non-dry-run)

- `SLACK_BOT_TOKEN`: Your Slack bot token (xoxb-...)
- `SLACK_APP_TOKEN`: Your Slack app token (xoxp-...)
- `SLACK_CHANNEL_ID`: Target Slack channel ID (C...)

## 🤖 LLM Providers

The Briefly Bot supports multiple LLM providers for TLDR summarization:

### **OpenAI (Default)** 🚀

- **Model**: GPT-3.5-turbo
- **Advantages**: Fast, reliable, consistent quality
- **Use Case**: Production environments, daily news digests
- **Command**: `python main.py` (default)

### **Gemini** 🌟

- **Model**: Gemini 1.5 Flash
- **Advantages**: Alternative AI perspective, Google's latest model
- **Use Case**: Testing, comparison, backup processing
- **Command**: `python main.py --llm-provider gemini`

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

- **OpenAI (Default)**: Uses GPT-3.5-turbo for fast, reliable summaries
- **Gemini Option**: Can switch to Gemini 1.5 Flash for alternative AI processing
- **Smart Fallback**: Automatically falls back to the other LLM if one fails
- **Basic Fallback**: Ultimate fallback to basic summarization if both LLMs fail
- Generates structured TLDR content for each article

### 3. **Slack Message Creation** 💬

- Formats summaries into rich Slack blocks
- Includes article titles, TLDR summaries, and links
- Creates professional-looking news digest

### 4. **Slack Publishing** 📤

- Sends the formatted message to your Slack channel
- Provides delivery confirmation and message ID
- Handles errors gracefully

## 🧪 Testing and Development

### Dry Run Mode

Perfect for testing the complete flow without sending messages to Slack:

```bash
poetry run python main.py --dry-run --verbose
```

This will:

- ✅ Collect news from all sources
- ✅ Create TLDR summaries
- ✅ Generate Slack message structure
- ✅ Show what would be sent (without actually sending)

### Verbose Logging

Enable detailed logging to see exactly what's happening:

```bash
poetry run python main.py --dry-run --verbose
```

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

3. **Gemini API Rate Limits**

   ```
   ⚠️ Error creating article TLDR with Gemini: 429 You exceeded your current quota
   ```

   **Solution**: The bot will automatically fall back to basic summarization

4. **No Articles Collected**
   ```
   ❌ No articles collected - stopping
   ```
   **Solution**: Check your NewsAPI key and ArXiv connectivity

## 🚀 Production Deployment

### Automated Execution

Set up a cron job or scheduler to run the bot daily:

```bash
# Example cron job (runs daily at 9 AM)
0 9 * * * cd /path/to/briefly-bot && conda activate news-finder && source .env && poetry run python main.py
```

### Monitoring

The bot creates log files with timestamps:

- `briefly_bot_YYYYMMDD.log` - Daily log files
- Console output for real-time monitoring

## 📈 Performance

- **Collection**: ~30-60 seconds for 20 articles
- **Summarization**: ~2-5 seconds per article (Gemini) or ~0.1 seconds (fallback)
- **Total Runtime**: ~2-5 minutes for 20 articles

## 🎯 Next Steps

1. **Set Real Slack Tokens**: Update your `.env` file with valid Slack credentials
2. **Test Full Flow**: Run `python main.py` to publish to Slack
3. **Automate**: Set up scheduled execution
4. **Customize**: Modify source configurations in `slackbot/collectors/sources/`
5. **Scale**: Add more news sources or adjust article limits

---

**🎉 Congratulations!** You now have a fully functional AI/ML news aggregator that automatically collects, summarizes, and publishes daily news digests to Slack!
