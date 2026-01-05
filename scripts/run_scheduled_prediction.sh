#!/bin/bash
###############################################################################
# Scheduled Prediction Runner Script
# 
# This script runs the automated prediction and commits results to git.
# Designed to be run by cron or other scheduling systems.
#
# Usage:
#   ./run_scheduled_prediction.sh
#
# Cron example (every 4 hours):
#   0 */4 * * * /path/to/eth-price-prediction/scripts/run_scheduled_prediction.sh >> /var/log/eth-prediction.log 2>&1
###############################################################################

# Exit on error
set -e

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# Change to project directory
cd "$PROJECT_DIR"

# Log start time
echo "========================================================================"
echo "Scheduled Prediction Run Started: $(date -u '+%Y-%m-%d %H:%M:%S UTC')"
echo "========================================================================"

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
fi

# Run the report generation
echo "Running prediction report generation..."
python src/generate_report.py

# Check if generation was successful
if [ $? -eq 0 ]; then
    echo "✓ Report generation successful"
    
    # Git operations
    echo "Committing and pushing to GitHub..."
    
    # Add reports folder
    git add reports/
    
    # Check if there are changes
    if git diff --staged --quiet; then
        echo "No changes to commit"
    else
        # Commit with timestamp
        TIMESTAMP=$(date -u '+%Y-%m-%d %H:%M UTC')
        git commit -m "Automated prediction report: $TIMESTAMP"
        
        # Push to GitHub
        git push origin main
        
        echo "✓ Report committed and pushed successfully"
    fi
else
    echo "✗ Report generation failed"
    exit 1
fi

# Log end time
echo "========================================================================"
echo "Scheduled Prediction Run Completed: $(date -u '+%Y-%m-%d %H:%M:%S UTC')"
echo "========================================================================"
echo ""
