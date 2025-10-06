# Briefly Bot - Cron Job Setup

This document explains how to set up a daily cron job for Briefly Bot to automatically send AI/ML news digests at 8:30 AM every day.

## 📁 Files Created

- `scripts/cron_daily_news.py` - Python script that runs the daily news processing
- `scripts/run_daily_news.sh` - Shell wrapper that sets up the environment
- `scripts/setup_cron.sh` - Automated setup script for the cron job

## 🚀 Quick Setup

### Option 1: Automated Setup (Recommended)

Run the setup script to automatically configure the cron job:

```bash
./scripts/setup_cron.sh
```

This script will:

- Check if the cron script exists and is executable
- Add the cron job to run daily at 8:30 AM
- Show you the current crontab
- Provide next steps and troubleshooting tips

### Option 2: Manual Setup

If you prefer to set up the cron job manually:

1. **Make scripts executable:**

   ```bash
   chmod +x scripts/cron_daily_news.py
   chmod +x scripts/run_daily_news.sh
   ```

2. **Add to crontab:**

   ```bash
   crontab -e
   ```

3. **Add this line:**

   ```
   30 8 * * * /home/dheeraj/projects/NewsFinderBot/scripts/run_daily_news.sh >> /home/dheeraj/projects/NewsFinderBot/logs/cron.log 2>&1
   ```

4. **Save and exit** (Ctrl+X, then Y, then Enter in nano)

## 🔧 Environment Setup

Make sure your `.env` file contains all required environment variables:

```bash
# Required for news collection
NEWSAPI_KEY=your_newsapi_key_here

# Required for Slack publishing
SLACK_BOT_TOKEN=xoxb-your-slack-bot-token
SLACK_CHANNEL_ID=C1234567890

# Required for AI summarization (choose one)
OPENAI_API_KEY=your_openai_key_here
# OR
GOOGLE_API_KEY=your_google_key_here
```

## 🧪 Testing

### Test the Cron Script Manually

```bash
# Test the shell wrapper
./scripts/run_daily_news.sh

# Or test the Python script directly
python scripts/cron_daily_news.py
```

### Check Cron Job Status

```bash
# View current crontab
crontab -l

# Check if cron service is running
sudo systemctl status cron

# View cron logs
tail -f /var/log/cron
```

## 📊 Monitoring

### Log Files

The cron job creates several log files:

- `logs/cron.log` - General cron output and errors
- `logs/briefly_cron_YYYYMMDD.log` - Daily detailed logs
- `logs/briefly_bot_YYYYMMDD.log` - Standard bot logs

### View Logs

```bash
# View today's cron log
tail -f logs/briefly_cron_$(date +%Y%m%d).log

# View general cron log
tail -f logs/cron.log

# View recent cron activity
grep "run_daily_news" logs/cron.log
```

## ⚙️ Cron Schedule

The default schedule is:

- **Time**: 8:30 AM every day
- **Cron expression**: `30 8 * * *`

### Customizing the Schedule

To change the schedule, edit the crontab:

```bash
crontab -e
```

Common schedule examples:

- `0 9 * * *` - 9:00 AM daily
- `30 8 * * 1-5` - 8:30 AM weekdays only
- `0 8 1 * *` - 8:00 AM on the 1st of every month
- `0 */6 * * *` - Every 6 hours

## 🔍 Troubleshooting

### Common Issues

1. **"Command not found" errors:**

   - Make sure the script paths are absolute
   - Check that conda environment is activated in the shell script

2. **Environment variables not loaded:**

   - Verify `.env` file exists and has correct format
   - Check that the shell script loads the `.env` file

3. **Permission denied:**

   - Make sure scripts are executable: `chmod +x scripts/*.sh scripts/*.py`

4. **Cron job not running:**
   - Check if cron service is running: `sudo systemctl status cron`
   - Verify crontab syntax: `crontab -l`
   - Check cron logs: `tail -f /var/log/cron`

### Debug Mode

To run the cron job with more verbose output:

```bash
# Edit the shell script to add debug mode
# Add this line after the conda activation:
export PYTHONPATH="$PROJECT_DIR:$PYTHONPATH"
python "$PROJECT_DIR/scripts/cron_daily_news.py" --verbose
```

### Manual Testing

```bash
# Test environment setup
source scripts/run_daily_news.sh

# Test Python script directly
cd /home/dheeraj/projects/NewsFinderBot
conda activate news-finder
python scripts/cron_daily_news.py
```

## 📝 Cron Job Management

### View Current Jobs

```bash
crontab -l
```

### Remove Cron Job

```bash
crontab -e
# Delete the line with "run_daily_news.sh"
# Save and exit
```

### Edit Cron Job

```bash
crontab -e
# Modify the schedule or script path
# Save and exit
```

## 🎯 What the Cron Job Does

1. **Sets up environment** - Activates conda environment and loads environment variables
2. **Collects news** - Fetches 20 articles from NewsAPI, RSS feeds, and ArXiv
3. **Creates summaries** - Generates TLDR summaries using OpenAI/Gemini
4. **Publishes to Slack** - Sends formatted message to the configured Slack channel
5. **Logs everything** - Records all activities and any errors

## 📈 Performance

- **Typical runtime**: 2-3 minutes
- **Articles processed**: 20 articles
- **Memory usage**: ~200-300MB
- **Network calls**: ~50-100 API requests

## 🔒 Security Notes

- Environment variables are loaded from `.env` file
- API keys are not logged or exposed
- Cron runs with user permissions (not root)
- Logs are stored locally and not transmitted

## 📞 Support

If you encounter issues:

1. Check the log files first
2. Test the script manually
3. Verify environment variables
4. Check cron service status
5. Review crontab syntax

The cron job is designed to be robust and will log any errors for debugging.
