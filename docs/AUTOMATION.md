'''# Automated Prediction Scheduling

**Document Version:** 1.0  
**Last Updated:** January 5, 2026

---

## 1. Overview

This document provides instructions for setting up and managing the automated prediction reporting system. The system is designed to run on a schedule, generate a new prediction report, and commit the results to the GitHub repository automatically.

**Recommended Schedule:** Every 4 hours (00:00, 04:00, 08:00, 12:00, 16:00, 20:00 UTC)

We provide three methods for automation:

1.  **GitHub Actions (Recommended)**: Cloud-based, fully integrated with the repository, no local infrastructure needed.
2.  **Cron Job (Linux/macOS)**: For users who want to run the automation on their own server.
3.  **Windows Task Scheduler**: For users running a Windows-based automation server.

## 2. Method 1: GitHub Actions (Recommended)

The repository includes a pre-configured GitHub Actions workflow file at `.github/workflows/scheduled-prediction.yml`. This is the easiest and most reliable way to automate the predictions.

### How It Works

- **Trigger**: The workflow is triggered automatically by a `cron` schedule defined in the file.
- **Environment**: It runs on a fresh, cloud-based Ubuntu virtual machine.
- **Steps**:
    1.  Checks out the latest code from your repository.
    2.  Sets up the correct Python version.
    3.  Installs all required dependencies from `requirements.txt`.
    4.  Executes the `src/generate_report.py` script.
    5.  Configures Git with your user details.
    6.  Commits the newly generated files in the `reports/` directory.
    7.  Pushes the commit back to your `main` branch.

### Setup Instructions

**The setup is already complete!** The workflow file is included in the repository. When you push this repository to your GitHub account, GitHub will automatically detect the workflow and start running it on the defined schedule.

### Managing the Workflow

- **View Runs**: Go to your repository on GitHub, click the "Actions" tab. You will see a list of all workflow runs.
- **Manual Trigger**: You can manually trigger a run from the "Actions" tab. Select "Automated ETH Price Prediction" from the list of workflows, click "Run workflow", and then "Run workflow" again.
- **Disable/Enable**: You can disable or enable the workflow from the "Actions" tab if needed.
- **Change Schedule**: To change the schedule, edit the `cron` expression in `.github/workflows/scheduled-prediction.yml`.

    ```yaml
    on:
      schedule:
        # Runs every 4 hours
        - cron: '0 */4 * * *'
    ```

## 3. Method 2: Cron Job (Linux/macOS)

Use this method if you prefer to run the automation on your own Linux or macOS server.

### Prerequisites

- Git installed and configured.
- Python 3.8+ installed.
- The repository cloned to your server.

### Setup Instructions

1.  **Make the script executable**:

    ```bash
    chmod +x /path/to/eth-price-prediction/scripts/run_scheduled_prediction.sh
    ```

2.  **Edit your crontab**:

    ```bash
    crontab -e
    ```

3.  **Add the cron job entry**:

    Add the following line to the file. This will run the script every 4 hours and log the output.

    ```cron
    0 */4 * * * /path/to/eth-price-prediction/scripts/run_scheduled_prediction.sh >> /var/log/eth-prediction.log 2>&1
    ```

    *Make sure to replace `/path/to/eth-price-prediction` with the actual absolute path to the project directory on your server.*

4.  **Save and Exit**: The cron job is now active.

## 4. Method 3: Windows Task Scheduler

Use this method for automation on a Windows machine.

### Prerequisites

- Git for Windows installed and configured.
- Python 3.8+ installed.
- The repository cloned to your machine.

### Setup Instructions

1.  **Open Task Scheduler**: Press `Win + R`, type `taskschd.msc`, and press Enter.

2.  **Create Basic Task**: In the "Actions" pane on the right, click "Create Basic Task...".

3.  **Name and Description**:
    - Name: `Ethereum Price Prediction`
    - Description: `Runs the automated ETH prediction report every 4 hours.`

4.  **Trigger**:
    - Select "Daily".
    - Set it to recur every `1` day.
    - Click "Next".

5.  **Advanced Trigger Settings**:
    - After creating the task, open its properties.
    - Go to the "Triggers" tab and edit your trigger.
    - Under "Advanced settings", check "Repeat task every" and select `4 hours` from the dropdown. Set the duration to `1 day`.

6.  **Action**:
    - Select "Start a program".
    - **Program/script**: Browse to and select the `run_scheduled_prediction.bat` script located in the `scripts` folder of the repository.
    - **Start in (optional)**: It's good practice to set this to the repository's root directory (e.g., `C:\Users\YourUser\Documents\eth-price-prediction`).

7.  **Finish**: Click "Finish" to save the task.

## 5. Report Structure

Regardless of the method used, the automation script will create and update the following structure within the `reports/` directory:

```
reports/
├── YYYY/MM/DD/                  # Archive of all historical reports
│   ├── 2026-01-05_00-00_prediction.json
│   └── 2026-01-05_00-00_overview.png
├── latest/                        # Always contains the most recent report
│   ├── predictions_summary.json
│   ├── eth_prediction_overview.png
│   └── README.md
└── README.md                      # Main index for the reports directory
```

- **Archive (`YYYY/MM/DD/`)**: A new folder is created for each day, containing all reports generated on that day, timestamped for clarity.
- **Latest (`/latest`)**: This folder is overwritten during each run to always contain the most recent prediction files. This provides a stable endpoint for any other applications that might want to consume the latest report.

This robust structure ensures both a complete historical archive and easy access to the latest data.
'''
