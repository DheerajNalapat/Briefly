#!/bin/bash
# Briefly Bot - Cron Job Wrapper
# This script sets up the environment and runs the daily news processing

# Set the project directory (parent of crons folder)
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_DIR"

# Load environment variables from .env file if it exists
if [ -f ".env" ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

# Activate conda environment if available
if command -v conda &> /dev/null; then
    source ~/miniconda3/etc/profile.d/conda.sh
    conda activate news-finder
fi

# Set Python path
export PYTHONPATH="$PROJECT_DIR:$PYTHONPATH"

# Run the cron job
python "$PROJECT_DIR/crons/cron_daily_news.py"

# Exit with the same code as the Python script
exit $?
