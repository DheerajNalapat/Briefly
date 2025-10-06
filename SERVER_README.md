# Briefly Bot Server

A Slack bot server that responds to `@briefly` mentions and `/briefly` slash commands to provide AI/ML news summaries.

## Features

- **@briefly mentions**: Responds to `@briefly` mentions in any Slack channel
- **/briefly slash command**: Responds to `/briefly` slash commands
- **Real-time processing**: Collects and summarizes news in real-time
- **LLM-generated categories**: Uses AI to categorize articles
- **Prioritized sources**: NewsAPI → RSS → ArXiv priority order

## Setup

### 1. Environment Variables

Create a `.env` file with the following variables:

```bash
# Slack Configuration
SLACK_BOT_TOKEN=xoxb-your-bot-token
SLACK_APP_TOKEN=xapp-your-app-token
SLACK_SIGNING_SECRET=your-signing-secret
SLACK_DEFAULT_CHANNEL=#ai-updates

# LLM Configuration
OPENAI_API_KEY=your-openai-api-key
GEMINI_API_KEY=your-gemini-api-key

# News API Configuration
NEWSAPI_KEY=your-newsapi-key
```

### 2. Slack App Configuration

1. **Create a Slack App** at https://api.slack.com/apps
2. **Enable Socket Mode** in your app settings
3. **Add Bot Token Scopes**:
   - `app_mentions:read`
   - `channels:read`
   - `chat:write`
   - `commands`
   - `im:read`
   - `im:write`
4. **Create a Slash Command**:
   - Command: `/briefly`
   - Request URL: (not needed for Socket Mode)
   - Short Description: `Get AI/ML news summary`
5. **Subscribe to Events**:
   - `app_mention`
   - `message.im`
6. **Install the App** to your workspace

### 3. Install Dependencies

```bash
# Install Python dependencies
pip install -e .

# Or using poetry
poetry install
```

### 4. Test Configuration

```bash
# Test the server configuration
python scripts/test_server.py
```

## Usage

### Start the Server

```bash
# Start the server
python server.py

# Start with verbose logging
python server.py --verbose

# Test configuration without starting
python server.py --dry-run
```

### Using the Bot

1. **@briefly mentions**: Type `@briefly` in any channel where the bot is present
2. **/briefly command**: Use the `/briefly` slash command in any channel
3. **Direct messages**: Send a message to the bot directly

The bot will:

1. Send an immediate acknowledgment
2. Collect the latest AI/ML news
3. Create TLDR summaries with LLM-generated categories
4. Publish the formatted message to the channel

## Architecture

```
server.py                    # Main server entry point
├── slackbot/slack/
│   ├── listener.py          # Event listener for @briefly mentions
│   └── publisher.py         # Message publisher
├── slackbot/services/
│   ├── aggregation_service.py    # News collection
│   ├── summarizer_service.py     # TLDR creation
│   └── publisher_service.py      # Publishing orchestration
└── main.py                  # Core news processing logic
```

## Logs

Logs are saved to the `logs/` directory:

- `briefly_server_YYYYMMDD.log` - Server logs
- `briefly_bot_YYYYMMDD.log` - Bot processing logs

## Troubleshooting

### Common Issues

1. **"No app token provided"**

   - Ensure `SLACK_APP_TOKEN` is set in your `.env` file
   - Enable Socket Mode in your Slack app settings

2. **"Configuration validation failed"**

   - Run `python scripts/test_server.py` to identify missing variables
   - Check that all required environment variables are set

3. **"Failed to start Slack event listener"**

   - Verify your Slack app tokens are correct
   - Check that the bot has the required scopes
   - Ensure the app is installed to your workspace

4. **"No articles found"**
   - Check your `NEWSAPI_KEY` is valid
   - Verify network connectivity
   - Check the logs for specific error messages

### Debug Mode

Run with verbose logging to see detailed information:

```bash
python server.py --verbose
```

## Development

### Testing

```bash
# Test configuration and services
python scripts/test_server.py

# Test the original main.py functionality
python main.py --dry-run --max-articles 5
```

### Adding New Features

1. **New event handlers**: Add to `slackbot/slack/listener.py`
2. **New services**: Add to `slackbot/services/`
3. **New collectors**: Add to `slackbot/collectors/`

## Production Deployment

For production deployment, consider:

1. **Process management**: Use `systemd`, `supervisor`, or `pm2`
2. **Logging**: Set up log rotation and monitoring
3. **Monitoring**: Add health checks and metrics
4. **Security**: Use environment variable management
5. **Scaling**: Consider multiple instances with load balancing

Example systemd service:

```ini
[Unit]
Description=Briefly Bot Server
After=network.target

[Service]
Type=simple
User=briefly-bot
WorkingDirectory=/path/to/briefly-bot
ExecStart=/path/to/briefly-bot/venv/bin/python server.py
Restart=always
RestartSec=10
Environment=PATH=/path/to/briefly-bot/venv/bin
EnvironmentFile=/path/to/briefly-bot/.env

[Install]
WantedBy=multi-user.target
```
