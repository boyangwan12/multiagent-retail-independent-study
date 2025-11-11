#!/usr/bin/env python3
"""
Fix mock actuals CSV files to have correct dates matching season_start_date.

Season starts: 2025-03-01
Week 1: 2025-03-01 to 2025-03-07
Week 2: 2025-03-08 to 2025-03-14
etc.
"""

import csv
from datetime import datetime, timedelta
from pathlib import Path

# Configuration
SEASON_START = datetime(2025, 3, 1).date()
SCENARIOS_DIR = Path(__file__).parent / "high_demand"

def fix_week_file(week_num: int):
    """Fix dates in a single week's actuals CSV file."""
    input_file = SCENARIOS_DIR / f"actuals_week_{week_num:02d}.csv"

    if not input_file.exists():
        print(f"[X] File not found: {input_file}")
        return

    # Calculate date range for this week
    week_start = SEASON_START + timedelta(days=(week_num - 1) * 7)
    week_end = week_start + timedelta(days=6)

    print(f"\nWeek {week_num}: {week_start} to {week_end}")

    # Read original CSV
    with open(input_file, 'r') as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    # Group by original date to maintain daily structure
    dates_in_file = sorted(set(row['date'] for row in rows))
    print(f"   Original dates: {len(dates_in_file)} days")

    # Map old dates to new dates
    date_mapping = {}
    for i, old_date_str in enumerate(dates_in_file):
        new_date = week_start + timedelta(days=i)
        if new_date <= week_end:
            date_mapping[old_date_str] = new_date.strftime('%Y-%m-%d')

    # Update rows with new dates
    updated_rows = []
    for row in rows:
        old_date = row['date']
        if old_date in date_mapping:
            row['date'] = date_mapping[old_date]
            updated_rows.append(row)

    # Write corrected CSV
    with open(input_file, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['date', 'store_id', 'quantity_sold'])
        writer.writeheader()
        writer.writerows(updated_rows)

    print(f"   [OK] Updated {len(updated_rows)} rows")
    print(f"   New dates: {date_mapping.get(dates_in_file[0])} to {date_mapping.get(dates_in_file[-1])}")

def main():
    print("Fixing mock actuals CSV files...")
    print(f"Season start date: {SEASON_START}")

    # Fix all 12 weeks
    for week in range(1, 13):
        fix_week_file(week)

    print("\nDone! All files have been updated with correct dates.")

if __name__ == "__main__":
    main()
