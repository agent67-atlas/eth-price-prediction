@echo off
REM ============================================================================
REM Scheduled Prediction Runner Script for Windows
REM 
REM This script runs the automated prediction and commits results to git.
REM Designed to be run by Windows Task Scheduler.
REM
REM Usage:
REM   run_scheduled_prediction.bat
REM
REM Task Scheduler setup:
REM   1. Open Task Scheduler
REM   2. Create Basic Task
REM   3. Trigger: Daily, repeat every 4 hours
REM   4. Action: Start a program
REM   5. Program: C:\path\to\eth-price-prediction\scripts\run_scheduled_prediction.bat
REM ============================================================================

REM Get script directory
set SCRIPT_DIR=%~dp0
set PROJECT_DIR=%SCRIPT_DIR%..

REM Change to project directory
cd /d "%PROJECT_DIR%"

echo ========================================================================
echo Scheduled Prediction Run Started: %date% %time%
echo ========================================================================

REM Activate virtual environment if it exists
if exist "venv\Scripts\activate.bat" (
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
)

REM Run the report generation
echo Running prediction report generation...
python src\generate_report.py

REM Check if generation was successful
if %ERRORLEVEL% EQU 0 (
    echo [SUCCESS] Report generation successful
    
    REM Git operations
    echo Committing and pushing to GitHub...
    
    REM Add reports folder
    git add reports/
    
    REM Commit with timestamp
    git commit -m "Automated prediction report: %date% %time%"
    
    REM Push to GitHub
    git push origin main
    
    echo [SUCCESS] Report committed and pushed successfully
) else (
    echo [ERROR] Report generation failed
    exit /b 1
)

echo ========================================================================
echo Scheduled Prediction Run Completed: %date% %time%
echo ========================================================================
echo.
