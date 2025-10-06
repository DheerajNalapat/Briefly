#!/bin/bash
# Briefly Bot - Cron Job Setup Script
# This script helps set up the daily cron job for Briefly Bot

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CRON_SCRIPT="$PROJECT_DIR/crons/run_daily_news.sh"
CRON_JOB="30 8 * * * $CRON_SCRIPT >> $PROJECT_DIR/logs/cron.log 2>&1"

echo "🚀 Briefly Bot - Cron Job Setup"
echo "================================="
echo ""
echo "📁 Project Directory: $PROJECT_DIR"
echo "📜 Cron Script: $CRON_SCRIPT"
echo "⏰ Schedule: Daily at 8:30 AM"
echo ""

# Check if the cron script exists
if [ ! -f "$CRON_SCRIPT" ]; then
    echo "❌ Error: Cron script not found at $CRON_SCRIPT"
    echo "Please make sure the project is set up correctly."
    exit 1
fi

# Check if the script is executable
if [ ! -x "$CRON_SCRIPT" ]; then
    echo "🔧 Making cron script executable..."
    chmod +x "$CRON_SCRIPT"
fi

echo "📋 Current crontab:"
echo "==================="
crontab -l 2>/dev/null || echo "No crontab found"
echo ""

echo "🔧 Adding Briefly Bot cron job..."
echo "Cron job: $CRON_JOB"
echo ""

# Check if the job already exists
if crontab -l 2>/dev/null | grep -q "run_daily_news.sh"; then
    echo "⚠️  A Briefly Bot cron job already exists!"
    echo "Current Briefly Bot jobs:"
    crontab -l 2>/dev/null | grep "run_daily_news.sh"
    echo ""
    read -p "Do you want to replace it? (y/N): " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "❌ Cron job setup cancelled."
        exit 0
    fi
    
    # Remove existing Briefly Bot jobs
    echo "🗑️  Removing existing Briefly Bot cron jobs..."
    crontab -l 2>/dev/null | grep -v "run_daily_news.sh" | crontab -
fi

# Add the new cron job
(crontab -l 2>/dev/null; echo "$CRON_JOB") | crontab -

echo "✅ Cron job added successfully!"
echo ""
echo "📋 Updated crontab:"
echo "==================="
crontab -l
echo ""

echo "📝 Next steps:"
echo "=============="
echo "1. Make sure your .env file contains all required environment variables:"
echo "   - NEWSAPI_KEY"
echo "   - SLACK_BOT_TOKEN"
echo "   - SLACK_CHANNEL_ID"
echo "   - OPENAI_API_KEY (or GOOGLE_API_KEY for Gemini)"
echo ""
echo "2. Test the cron job manually:"
echo "   $CRON_SCRIPT"
echo ""
echo "3. Check the logs:"
echo "   tail -f $PROJECT_DIR/logs/cron.log"
echo "   tail -f $PROJECT_DIR/logs/briefly_cron_\$(date +%Y%m%d).log"
echo ""
echo "4. To remove the cron job later:"
echo "   crontab -e"
echo "   (then delete the line with run_daily_news.sh)"
echo ""
echo "🎉 Cron job setup complete!"
