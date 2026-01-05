#!/usr/bin/env python3
"""
Automated Report Generation Script
Generates prediction reports for scheduled tasks
"""

import sys
import os
import json
import shutil
from datetime import datetime, timezone
import pandas as pd

# Add src directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def create_report_folders():
    """Create folder structure for reports"""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    reports_dir = os.path.join(base_dir, 'reports')
    
    now = datetime.now(timezone.utc)
    year = now.strftime('%Y')
    month = now.strftime('%m')
    day = now.strftime('%d')
    
    # Create dated folder structure
    dated_dir = os.path.join(reports_dir, year, month, day)
    os.makedirs(dated_dir, exist_ok=True)
    
    # Create/update latest folder
    latest_dir = os.path.join(reports_dir, 'latest')
    os.makedirs(latest_dir, exist_ok=True)
    
    return dated_dir, latest_dir, now

def generate_report_filename(timestamp):
    """Generate standardized report filename"""
    return timestamp.strftime('%Y-%m-%d_%H-%M')

def run_prediction_pipeline():
    """Run the complete prediction pipeline"""
    print("=" * 70)
    print("  AUTOMATED ETHEREUM PRICE PREDICTION REPORT")
    print("=" * 70)
    print(f"\nGeneration Time: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}\n")
    
    # Step 1: Fetch Data
    print("Step 1/3: Fetching latest market data...")
    try:
        import fetch_data
        print("✓ Data fetched successfully\n")
    except Exception as e:
        print(f"✗ Error fetching data: {e}")
        return False
    
    # Step 2: Generate Predictions
    print("Step 2/3: Generating predictions...")
    try:
        import predict
        print("✓ Predictions generated successfully\n")
    except Exception as e:
        print(f"✗ Error generating predictions: {e}")
        return False
    
    # Step 3: Create Visualizations
    print("Step 3/3: Creating visualizations...")
    try:
        import visualize
        print("✓ Visualizations created successfully\n")
    except Exception as e:
        print(f"✗ Error creating visualizations: {e}")
        return False
    
    return True

def copy_outputs_to_report_folder(dated_dir, latest_dir, timestamp):
    """Copy prediction outputs to report folders"""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    filename_base = generate_report_filename(timestamp)
    
    # Files to copy
    files_to_copy = {
        'predictions_summary.json': f'{filename_base}_prediction.json',
        'eth_prediction_overview.png': f'{filename_base}_overview.png',
        'eth_1hour_prediction.png': f'{filename_base}_1hour.png',
        'eth_technical_indicators.png': f'{filename_base}_indicators.png',
        'eth_1m_data.csv': f'{filename_base}_data.csv'
    }
    
    copied_files = []
    
    for source_name, dest_name in files_to_copy.items():
        source_path = os.path.join('/home/ubuntu', source_name)
        
        if os.path.exists(source_path):
            # Copy to dated folder
            dated_dest = os.path.join(dated_dir, dest_name)
            shutil.copy2(source_path, dated_dest)
            
            # Copy to latest folder (with generic name)
            latest_dest = os.path.join(latest_dir, source_name)
            shutil.copy2(source_path, latest_dest)
            
            copied_files.append(dest_name)
            print(f"  ✓ Copied {source_name}")
        else:
            print(f"  ✗ Warning: {source_name} not found")
    
    return copied_files

def generate_report_summary(dated_dir, timestamp, copied_files):
    """Generate a summary README for the report"""
    filename_base = generate_report_filename(timestamp)
    
    # Load prediction data
    prediction_file = os.path.join(dated_dir, f'{filename_base}_prediction.json')
    
    try:
        with open(prediction_file, 'r') as f:
            predictions = json.load(f)
    except:
        print("  ✗ Warning: Could not load prediction data for summary")
        return
    
    # Generate markdown summary
    summary = f"""# Ethereum Price Prediction Report

**Generated:** {timestamp.strftime('%Y-%m-%d %H:%M:%S UTC')}

## Current Market Status

- **Current Price:** ${predictions['current_price']:.2f}
- **Market Trend:** {predictions['trend_analysis']['trend']}
- **RSI:** {predictions['trend_analysis']['rsi']:.2f} ({predictions['trend_analysis']['rsi_signal']})
- **MACD Signal:** {predictions['trend_analysis']['macd_signal']}

## Price Predictions

| Time Horizon | Predicted Price | Change | Timestamp |
|:-------------|:----------------|:-------|:----------|
"""
    
    for time_label, pred_data in predictions['predictions'].items():
        summary += f"| **{time_label}** | ${pred_data['price']:.2f} | {pred_data['change_pct']:+.2f}% | {pred_data['timestamp']} |\n"
    
    summary += f"""
## Model Performance

| Model | R² Score | Weight |
|:------|:---------|:-------|
"""
    
    for model, score in predictions['model_scores'].items():
        weight = predictions['model_weights'].get(model, 0) * 100
        summary += f"| {model.replace('_', ' ').title()} | {score:.4f} | {weight:.1f}% |\n"
    
    summary += f"""
## Report Files

"""
    for filename in copied_files:
        summary += f"- `{filename}`\n"
    
    summary += f"""
## Disclaimer

This is an automated prediction generated by a machine learning model. Cryptocurrency trading carries substantial risk. These predictions are for informational purposes only and should not be considered financial advice.

---

*Report generated by [Ethereum Price Prediction System](https://github.com/Madgeniusblink/eth-price-prediction)*
"""
    
    # Save summary
    summary_file = os.path.join(dated_dir, f'{filename_base}_README.md')
    with open(summary_file, 'w') as f:
        f.write(summary)
    
    print(f"  ✓ Generated report summary")
    
    return summary

def update_latest_readme(latest_dir, summary):
    """Update the latest folder README"""
    readme_path = os.path.join(latest_dir, 'README.md')
    with open(readme_path, 'w') as f:
        f.write(summary)
    print(f"  ✓ Updated latest README")

def generate_index(reports_dir):
    """Generate an index of all reports"""
    index_content = """# Ethereum Price Prediction Reports

This directory contains automated prediction reports generated every 4 hours.

## Latest Report

See the [`latest/`](latest/) folder for the most recent prediction.

## Report Schedule

Reports are generated at the following times (UTC):
- 00:00 - Asian session opening
- 04:00 - Asian session peak  
- 08:00 - European session opening
- 12:00 - European/US overlap
- 16:00 - US session peak
- 20:00 - US session closing

## Archive Structure

Reports are organized by date: `YYYY/MM/DD/`

Each report includes:
- Prediction data (JSON)
- Overview chart (PNG)
- 1-hour focused chart (PNG)
- Technical indicators chart (PNG)
- Raw market data (CSV)
- Summary README (MD)

## How to Use

1. Navigate to the date you're interested in
2. Open the README file for a quick summary
3. View the PNG charts for visual analysis
4. Download the JSON for programmatic access

---

*Generated by [Ethereum Price Prediction System](https://github.com/Madgeniusblink/eth-price-prediction)*
"""
    
    index_path = os.path.join(reports_dir, 'README.md')
    with open(index_path, 'w') as f:
        f.write(index_content)

def main():
    """Main report generation function"""
    try:
        # Create folder structure
        dated_dir, latest_dir, timestamp = create_report_folders()
        print(f"Report folders created:")
        print(f"  Dated: {dated_dir}")
        print(f"  Latest: {latest_dir}\n")
        
        # Run prediction pipeline
        success = run_prediction_pipeline()
        
        if not success:
            print("\n✗ Report generation failed")
            return 1
        
        # Copy outputs to report folders
        print("Organizing report files...")
        copied_files = copy_outputs_to_report_folder(dated_dir, latest_dir, timestamp)
        
        # Generate summaries
        print("\nGenerating report summaries...")
        summary = generate_report_summary(dated_dir, timestamp, copied_files)
        
        if summary:
            update_latest_readme(latest_dir, summary)
        
        # Update main index
        reports_dir = os.path.dirname(dated_dir).split('/')[:-2]
        reports_dir = '/'.join(reports_dir[:-2]) + '/' + reports_dir[-2]
        base_reports = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'reports')
        generate_index(base_reports)
        
        print("\n" + "=" * 70)
        print("  REPORT GENERATION COMPLETE")
        print("=" * 70)
        print(f"\nReport Location: {dated_dir}")
        print(f"Latest Report: {latest_dir}")
        print(f"\nFiles Generated: {len(copied_files)}")
        
        return 0
        
    except Exception as e:
        print(f"\n✗ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
