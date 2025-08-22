# TLDR Summarizer Structure Documentation

## Overview

The TLDR summarizer creates concise, Slack-friendly summaries of AI/ML news articles using Google Gemini with LangChain. It transforms multiple articles into a structured format perfect for busy professionals.

## Data Flow

```
Articles → TLDR Summarizer → TLDR Summary → Slack Message → Slack API
```

## 1. TLDR Summary Structure

### Core Fields

- **`tldr_text`**: Main summary (2-3 sentences)
- **`key_points`**: List of key developments
- **`trending_topics`**: What's hot right now
- **`impact_level`**: High/Medium/Low impact
- **`reading_time`**: Estimated reading time

### Metadata

- **`article_count`**: Number of articles processed
- **`categories`**: Article categories covered
- **`sources`**: News sources
- **`generated_at`**: Timestamp
- **`model_used`**: Gemini model or fallback

### Slack Formatting

- **`emoji`**: Visual indicator (🚀 for digest, 📰 for articles)
- **`color`**: Hex color for Slack attachments

## 2. Slack Message Structure

### Main Components

```json
{
  "text": "Main message text",
  "blocks": [
    {
      "type": "header",
      "text": {
        "type": "plain_text",
        "text": "🚀 AI/ML News TLDR",
        "emoji": true
      }
    },
    {
      "type": "section",
      "text": {
        "type": "mrkdwn",
        "text": "TLDR summary content..."
      }
    },
    {
      "type": "section",
      "text": {
        "type": "mrkdwn",
        "text": "*Key Points:*\n• Point 1\n• Point 2\n• Point 3"
      }
    },
    {
      "type": "section",
      "text": {
        "type": "mrkdwn",
        "text": "*Trending:* AI Research, Robotics, Quantum Computing"
      }
    },
    {
      "type": "context",
      "elements": [
        {
          "type": "mrkdwn",
          "text": "📊 8 articles | 🎯 Medium impact | ⏱️ 16 min read"
        }
      ]
    }
  ],
  "attachments": [
    {
      "color": "#ff6b6b",
      "footer": "Generated at 2024-01-15T10:00:00 using gemini-pro"
    }
  ]
}
```

## 3. Example Output

### TLDR Summary

```
📰 *Daily AI/ML News Roundup*

Today's top 8 stories covering Robotics, AI Safety, Quantum Computing.
Key sources: TechCrunch, Nature, VentureBeat
```

### Key Points

- OpenAI Releases GPT-5 with Multimodal Capabilities
- Google DeepMind Achieves Breakthrough in Protein Folding
- Meta's Llama 3 Shows Promise in Multilingual Tasks
- Tesla's Optimus Robot Shows Human-like Dexterity
- New Quantum Machine Learning Algorithm Outperforms Classical Methods

### Trending Topics

- AI Research
- Robotics
- Quantum Computing

### Impact Assessment

- **High Impact**: GPT-5 release, DeepMind breakthrough
- **Medium Impact**: Llama 3, Optimus robot
- **Low Impact**: Algorithm improvements, tool updates

## 4. Slack Integration

### Block Kit Components

1. **Header**: Title with emoji
2. **Main Content**: TLDR summary
3. **Key Points**: Bullet points of developments
4. **Trending**: Current hot topics
5. **Metadata**: Article count, impact, reading time

### Visual Elements

- **Colors**: Red (#ff6b6b) for daily digest, Green (#36a64f) for articles
- **Emojis**: 🚀 for digest, 📰 for articles, 📊 for stats
- **Formatting**: Bold headers, bullet points, contextual metadata

## 5. Gemini Integration

### When Available

- Uses `gemini-pro` model for AI-powered summaries
- Structured output using Pydantic models
- Intelligent impact assessment and trend detection

### Fallback Mode

- Basic summarization when Gemini unavailable
- Extracts key information from article titles and metadata
- Maintains same output structure

## 6. Usage Example

```python
from slackbot.summarizer import create_tldr_summarizer
# Use real data from API collectors instead of dummy data

# Create summarizer
summarizer = create_tldr_summarizer()

# Get articles
# Get real articles from API collector instead of dummy data
articles = collector.collect()[:5]  # Get 5 articles for testing

# Create TLDR digest
tldr_digest = summarizer.create_tldr_digest(articles)

# Convert to Slack message
slack_msg = summarizer.create_slack_message(tldr_digest)

# Ready to send to Slack API
slack_json = {
    "text": slack_msg.text,
    "blocks": slack_msg.blocks,
    "attachments": slack_msg.attachments
}
```

## 7. Benefits

### For Users

- **Quick Scanning**: 2-3 sentence summaries
- **Actionable Insights**: Key points and trends
- **Impact Assessment**: Know what matters most
- **Reading Time**: Estimate time investment

### For Slack

- **Rich Formatting**: Block Kit components
- **Visual Appeal**: Colors, emojis, structure
- **Mobile Friendly**: Optimized for all devices
- **API Ready**: Direct integration with Slack

## 8. Configuration

### Environment Variables

```bash
GEMINI_API_KEY=your_gemini_api_key_here
```

### Model Settings

- **Temperature**: 0.3 (balanced creativity/consistency)
- **Max Tokens**: 2048 (sufficient for TLDR summaries)
- **Model**: gemini-pro (latest Gemini model)

## 9. Future Enhancements

- **Multi-language Support**: International news summaries
- **Custom Categories**: User-defined topic groupings
- **Interactive Elements**: Slack buttons for deeper dives
- **Scheduling**: Automated daily digest posting
- **Analytics**: Track engagement and preferences

---

_This structure ensures that every TLDR summary is concise, informative, and perfectly formatted for Slack integration._
