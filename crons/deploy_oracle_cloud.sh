#!/bin/bash
# Briefly Bot - Oracle Cloud Deployment Script
# This script sets up Briefly Bot on Oracle Cloud Infrastructure

set -e  # Exit on any error

echo "🚀 Briefly Bot - Oracle Cloud Deployment"
echo "========================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   print_error "This script should not be run as root"
   exit 1
fi

print_status "Starting Oracle Cloud deployment setup..."

# Update system packages
print_status "Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install required system packages
print_status "Installing system dependencies..."
sudo apt install -y \
    python3 \
    python3-pip \
    python3-venv \
    git \
    curl \
    wget \
    unzip \
    cron \
    htop \
    nano \
    vim

# Install Miniconda
print_status "Installing Miniconda..."
if [ ! -d "$HOME/miniconda3" ]; then
    wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O ~/miniconda3.sh
    bash ~/miniconda3.sh -b -p $HOME/miniconda3
    rm ~/miniconda3.sh
    
    # Add conda to PATH
    echo 'export PATH="$HOME/miniconda3/bin:$PATH"' >> ~/.bashrc
    source ~/.bashrc
    print_success "Miniconda installed successfully"
else
    print_warning "Miniconda already installed"
fi

# Create conda environment
print_status "Creating conda environment..."
source ~/miniconda3/etc/profile.d/conda.sh
conda create -n news-finder python=3.9 -y
conda activate news-finder

# Install Python dependencies
print_status "Installing Python dependencies..."
pip install \
    feedparser==6.0.10 \
    requests==2.31.0 \
    python-dotenv==1.0.0 \
    html2text==2020.1.16 \
    newsapi-python==0.2.7 \
    arxiv==2.1.0 \
    langchain==0.1.0 \
    langchain-openai==0.0.5 \
    langchain-google-genai==0.0.6 \
    slack-bolt==1.18.1 \
    slack-sdk==3.26.1 \
    pydantic==2.5.0 \
    httpx==0.25.2

print_success "Python dependencies installed successfully"

# Create project directory
PROJECT_DIR="$HOME/briefly-bot"
print_status "Setting up project directory: $PROJECT_DIR"

if [ -d "$PROJECT_DIR" ]; then
    print_warning "Project directory already exists, updating..."
    cd "$PROJECT_DIR"
    git pull origin main 2>/dev/null || print_warning "Could not pull updates"
else
    print_status "Creating project directory..."
    mkdir -p "$PROJECT_DIR"
    cd "$PROJECT_DIR"
fi

# Create necessary directories
mkdir -p logs
mkdir -p crons

print_success "Project directory setup complete"

# Create environment file template
print_status "Creating environment file template..."
cat > .env.template << 'EOF'
# Briefly Bot Environment Variables
# Copy this file to .env and fill in your actual values

# NewsAPI.org API Key (required)
NEWSAPI_KEY=your_newsapi_key_here

# Slack Configuration (required)
SLACK_BOT_TOKEN=xoxb-your-slack-bot-token
SLACK_CHANNEL_ID=C1234567890

# AI Provider (choose one)
OPENAI_API_KEY=your_openai_key_here
# OR
GOOGLE_API_KEY=your_google_key_here

# Optional: Slack App Configuration (for server mode)
SLACK_APP_TOKEN=xapp-your-slack-app-token
SLACK_SIGNING_SECRET=your_slack_signing_secret
EOF

# Create deployment info file
print_status "Creating deployment information..."
cat > DEPLOYMENT_INFO.md << EOF
# Briefly Bot - Oracle Cloud Deployment

## Deployment Details
- **Date**: $(date)
- **User**: $(whoami)
- **Hostname**: $(hostname)
- **OS**: $(lsb_release -d | cut -f2)
- **Python**: $(python3 --version)
- **Conda**: $(conda --version)

## Project Structure
\`\`\`
$PROJECT_DIR/
├── crons/                    # Cron job scripts
│   ├── cron_daily_news.py    # Main cron script
│   ├── run_daily_news.sh     # Shell wrapper
│   ├── setup_cron.sh         # Cron setup script
│   └── CRON_SETUP.md         # Cron documentation
├── logs/                     # Log files
├── .env.template             # Environment variables template
└── DEPLOYMENT_INFO.md        # This file
\`\`\`

## Next Steps
1. Copy .env.template to .env and fill in your API keys
2. Run: ./crons/setup_cron.sh
3. Test: ./crons/run_daily_news.sh
4. Monitor logs: tail -f logs/briefly_cron_\$(date +%Y%m%d).log

## Useful Commands
\`\`\`bash
# Activate environment
conda activate news-finder

# Check cron job
crontab -l

# View logs
tail -f logs/cron.log
tail -f logs/briefly_cron_\$(date +%Y%m%d).log

# Test cron job manually
./crons/run_daily_news.sh

# Check system status
htop
df -h
free -h
\`\`\`
EOF

print_success "Deployment setup complete!"

echo ""
echo "🎉 Oracle Cloud deployment setup completed successfully!"
echo ""
echo "📋 Next steps:"
echo "=============="
echo "1. Copy your project files to: $PROJECT_DIR"
echo "2. Copy .env.template to .env and fill in your API keys:"
echo "   cp .env.template .env"
echo "   nano .env"
echo ""
echo "3. Set up the cron job:"
echo "   ./crons/setup_cron.sh"
echo ""
echo "4. Test the cron job:"
echo "   ./crons/run_daily_news.sh"
echo ""
echo "5. Monitor the logs:"
echo "   tail -f logs/briefly_cron_\$(date +%Y%m%d).log"
echo ""
echo "📊 System Information:"
echo "====================="
echo "• Project Directory: $PROJECT_DIR"
echo "• Conda Environment: news-finder"
echo "• Cron Schedule: Daily at 8:30 AM"
echo "• Logs Directory: $PROJECT_DIR/logs"
echo ""
echo "🔧 Useful Commands:"
echo "==================="
echo "• Activate environment: conda activate news-finder"
echo "• Check cron jobs: crontab -l"
echo "• View system resources: htop"
echo "• Check disk space: df -h"
echo "• Check memory: free -h"
echo ""
print_success "Deployment ready! Follow the next steps above."

