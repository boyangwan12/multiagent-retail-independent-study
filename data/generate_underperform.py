"""
Generate underperforming scenario data for pricing agent testing.
Creates actuals ~15-20% below forecast for Accessories category.
"""
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

np.random.seed(123)

NUM_STORES = 50
TESTING_START = datetime(2025, 2, 17)  # Monday, Week 1

# Forecast values for Accessories (from chart analysis)
WEEKLY_FORECAST = {
    1: 8500,
    2: 10000,
    3: 12000,
    4: 14500,
    5: 15000,
    6: 14000,
    7: 14000,
    8: 15000,
    9: 15500,
    10: 15500,
    11: 15000,
    12: 14800
}

# Target: 15-20% below forecast
UNDERPERFORM_RATIO = 0.82  # 18% below forecast on average

# Store tier multipliers (Premium, Mid, Small)
def get_store_multiplier(store_id):
    store_num = int(store_id[1:])
    if store_num <= 15:  # Premium stores
        return np.random.uniform(1.3, 1.7)
    elif store_num <= 35:  # Mid-tier stores
        return np.random.uniform(0.85, 1.15)
    else:  # Small/Value stores
        return np.random.uniform(0.5, 0.75)

# Day of week pattern for Accessories (weekend heavy)
DAY_PATTERNS = [0.7, 0.8, 0.9, 1.0, 1.3, 1.5, 1.2]  # Mon-Sun

def generate_week(week_num):
    """Generate one week of underperforming actuals."""
    week_start = TESTING_START + timedelta(weeks=week_num - 1)

    # Target total for this week (below forecast)
    forecast = WEEKLY_FORECAST[week_num]

    # Add some variance to underperformance (-12% to -22%)
    week_underperform = np.random.uniform(0.78, 0.88)
    target_total = forecast * week_underperform

    # Calculate base per-store-day before applying multipliers
    # We need to work backwards from target
    store_multipliers = {f"S{i:03d}": get_store_multiplier(f"S{i:03d}") for i in range(1, 51)}

    # Sum of (multiplier * day_pattern) across all stores and days
    total_weight = sum(
        store_multipliers[f"S{i:03d}"] * DAY_PATTERNS[d]
        for i in range(1, 51)
        for d in range(7)
    )

    # Base quantity per unit weight
    base_qty = target_total / total_weight

    data = []
    for day_offset in range(7):
        current_date = week_start + timedelta(days=day_offset)
        day_pattern = DAY_PATTERNS[day_offset]

        for store_num in range(1, 51):
            store_id = f"S{store_num:03d}"

            # Calculate quantity
            qty = base_qty * store_multipliers[store_id] * day_pattern

            # Add daily noise (±15%)
            qty *= np.random.uniform(0.85, 1.15)

            # Specific underperformance patterns
            # Week 3: Some stores hit harder (supply issues)
            if week_num == 3 and store_num in [7, 19, 25]:
                qty *= 0.6

            # Week 5-6: Broader weakness
            if week_num in [5, 6]:
                qty *= np.random.uniform(0.90, 1.0)

            # Week 8-9: Slight recovery but still below forecast
            if week_num in [8, 9]:
                qty *= np.random.uniform(0.95, 1.05)

            qty = max(1, int(round(qty)))

            data.append({
                'date': current_date.strftime('%Y-%m-%d'),
                'store_id': store_id,
                'quantity_sold': qty
            })

    return pd.DataFrame(data)

def main():
    print("Generating underperform scenario...")
    print(f"Target: {UNDERPERFORM_RATIO*100:.0f}% of forecast (~15-22% below)")
    print()

    for week in range(1, 13):
        df = generate_week(week)

        # Calculate actual totals
        total = df['quantity_sold'].sum()
        forecast = WEEKLY_FORECAST[week]
        variance_pct = ((total - forecast) / forecast) * 100

        output_path = f'scenarios/underperform/actuals_week_{week:02d}.csv'
        df.to_csv(output_path, index=False)

        print(f"Week {week:02d}: Forecast={forecast:,}, Actual={total:,} ({variance_pct:+.1f}%)")

    print()
    print("[OK] Generated 12 weeks of underperforming actuals")
    print("Files saved to: scenarios/underperform/")

if __name__ == '__main__':
    main()
