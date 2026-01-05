# GitHub Actions Workflow Setup

Due to GitHub security restrictions, workflow files cannot be pushed directly via API tokens. You need to add the workflow file manually through the GitHub web interface.

## Option 1: Add via GitHub Web Interface (Recommended)

1. Go to your repository: https://github.com/Madgeniusblink/eth-price-prediction

2. Click on "Add file" → "Create new file"

3. In the filename field, type: `.github/workflows/scheduled-prediction.yml`

4. Copy and paste the following content:

```yaml
name: Automated ETH Price Prediction

on:
  schedule:
    # Run every 4 hours at 00:00, 04:00, 08:00, 12:00, 16:00, 20:00 UTC
    - cron: '0 0,4,8,12,16,20 * * *'
  
  workflow_dispatch:  # Allow manual trigger
    inputs:
      reason:
        description: 'Reason for manual run'
        required: false
        default: 'Manual trigger'

jobs:
  generate-prediction:
    runs-on: ubuntu-latest
    
    permissions:
      contents: write  # Allow pushing to repository
    
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4
        with:
          fetch-depth: 0  # Full history for proper git operations
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
          cache: 'pip'
      
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
      
      - name: Generate prediction report
        run: |
          python src/generate_report.py
        env:
          TZ: UTC
      
      - name: Configure Git
        run: |
          git config user.name "Cris R"
          git config user.email "Madgeniusblink@users.noreply.github.com"
      
      - name: Commit and push report
        run: |
          git add reports/
          
          # Check if there are changes to commit
          if git diff --staged --quiet; then
            echo "No changes to commit"
          else
            TIMESTAMP=$(date -u +"%Y-%m-%d %H:%M UTC")
            git commit -m "Automated prediction report: $TIMESTAMP"
            git push
            echo "Report committed and pushed successfully"
          fi
      
      - name: Upload artifacts (for debugging)
        if: failure()
        uses: actions/upload-artifact@v4
        with:
          name: failed-run-logs
          path: |
            *.log
            reports/
          retention-days: 7
```

5. Scroll down and click "Commit new file"

6. The workflow will now run automatically every 4 hours!

## Option 2: Add via Git Push (From Your Local Machine)

If you have the repository cloned on your local machine with proper credentials:

1. Create the directory structure:
   ```bash
   mkdir -p .github/workflows
   ```

2. Copy the workflow file from the repository to `.github/workflows/scheduled-prediction.yml`

3. Commit and push:
   ```bash
   git add .github/workflows/scheduled-prediction.yml
   git commit -m "Add GitHub Actions workflow for automated predictions"
   git push origin main
   ```

## Verify Setup

After adding the workflow:

1. Go to the "Actions" tab in your repository
2. You should see "Automated ETH Price Prediction" in the list
3. Click on it to see the schedule
4. You can manually trigger a test run by clicking "Run workflow"

## Schedule Details

The workflow runs at these times (UTC):
- 00:00 - Asian session opening
- 04:00 - Asian session peak
- 08:00 - European session opening
- 12:00 - European/US overlap
- 16:00 - US session peak
- 20:00 - US session closing

This provides 6 prediction reports per day, capturing all major trading sessions.

## Troubleshooting

**If the workflow doesn't appear:**
- Make sure the file is in the correct location: `.github/workflows/scheduled-prediction.yml`
- Check that the YAML syntax is correct (no extra spaces or tabs)

**If the workflow fails:**
- Check the "Actions" tab for error logs
- Verify that all dependencies are in `requirements.txt`
- Ensure the `reports/` directory exists in the repository

**If commits aren't being pushed:**
- The workflow has `contents: write` permission, which should be sufficient
- Check the repository settings under "Actions" → "General" → "Workflow permissions"
- Ensure "Read and write permissions" is selected
