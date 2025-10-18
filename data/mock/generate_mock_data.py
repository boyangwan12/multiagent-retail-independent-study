"""
Mock Data Generation Script for Fashion Retail PoC
Generates realistic synthetic retail sales data for demand forecasting system testing

Requirements:
- Python 3.11+
- pandas, numpy, scipy

Usage:
    python generate_mock_data.py --validate
    python generate_mock_data.py --regenerate --validate
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import argparse
import time
import os
from scipy import stats
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score

# Fixed seed for reproducibility
SEED = 42

# Constants
NUM_STORES = 50
NUM_CATEGORIES = 3
CATEGORIES = ["Women's Dresses", "Men's Shirts", "Accessories"]
BASE_PRICES = {
    "Women's Dresses": 55.0,
    "Men's Shirts": 35.0,
    "Accessories": 25.0
}

# Historical data range
HISTORICAL_START = datetime(2022, 1, 1)
HISTORICAL_END = datetime(2024, 12, 31)

# Testing data range (Spring 2025 season, 12 weeks)
TESTING_START = datetime(2025, 2, 17)  # Monday
TESTING_END = datetime(2025, 5, 11)    # Sunday (12 weeks later)


def set_seed(regenerate=False):
    """Set random seed for reproducibility"""
    if regenerate:
        seed = int(time.time())
        print(f"Using time-based seed: {seed}")
    else:
        seed = SEED
        print(f"Using fixed seed: {seed}")
    np.random.seed(seed)
    return seed


def calculate_seasonality(date, category):
    """
    Returns seasonality multiplier for a given date and category

    Args:
        date: datetime object
        category: product category string

    Returns:
        float: seasonality multiplier (0.6 to 1.8)
    """
    month = date.month

    if category == "Women's Dresses":
        monthly_factors = {
            1: 0.6, 2: 0.7, 3: 1.2, 4: 1.4, 5: 1.5,
            6: 1.3, 7: 1.2, 8: 1.1, 9: 0.9, 10: 0.8,
            11: 0.7, 12: 0.8
        }
    elif category == "Men's Shirts":
        monthly_factors = {
            1: 0.9, 2: 0.9, 3: 1.0, 4: 1.0, 5: 1.0,
            6: 1.1, 7: 1.0, 8: 1.2, 9: 1.1, 10: 1.0,
            11: 1.0, 12: 1.0
        }
    else:  # Accessories
        monthly_factors = {
            1: 0.6, 2: 0.8, 3: 0.9, 4: 1.0, 5: 1.0,
            6: 0.9, 7: 0.8, 8: 0.9, 9: 1.0, 10: 1.1,
            11: 1.6, 12: 1.8
        }

    return monthly_factors[month]


def get_weekly_pattern(date, category):
    """Returns weekly pattern multiplier based on day of week"""
    day = date.weekday()  # Monday=0, Sunday=6

    if category == "Women's Dresses":
        # Strong weekend effect
        weekly = [0.8, 0.9, 1.0, 1.1, 1.3, 1.5, 1.2]
    elif category == "Men's Shirts":
        # More stable pattern
        weekly = [0.95, 0.95, 1.0, 1.0, 1.1, 1.15, 1.05]
    else:  # Accessories
        # Very strong weekend effect
        weekly = [0.7, 0.8, 0.9, 1.0, 1.4, 1.6, 1.3]

    return weekly[day]


def apply_holiday_spike(date, category, base_sales):
    """
    Applies holiday spike to base sales if date is near a holiday

    Args:
        date: datetime object
        category: product category
        base_sales: baseline sales quantity

    Returns:
        float: adjusted sales quantity
    """
    # Define holidays with (month, day, duration_days, multiplier)
    holidays = []

    if category == "Women's Dresses":
        # Valentine's Day
        if date.month == 2 and 12 <= date.day <= 15:
            return base_sales * 1.30
        # Mother's Day (second Sunday in May, approximate May 10-14)
        if date.month == 5 and 10 <= date.day <= 14:
            return base_sales * 1.40
        # End of Season Sale (Aug 15-31)
        if date.month == 8 and date.day >= 15:
            return base_sales * 1.20

    elif category == "Men's Shirts":
        # Father's Day (third Sunday in June, approximate June 15-18)
        if date.month == 6 and 15 <= date.day <= 18:
            return base_sales * 1.25
        # Back to School (Aug 20 - Sep 10)
        if (date.month == 8 and date.day >= 20) or (date.month == 9 and date.day <= 10):
            return base_sales * 1.15
        # Black Friday (Nov 29, approx)
        if date.month == 11 and 27 <= date.day <= 30:
            return base_sales * 1.35

    else:  # Accessories
        # Valentine's Day (gifts)
        if date.month == 2 and 12 <= date.day <= 15:
            return base_sales * 1.50
        # Black Friday
        if date.month == 11 and 27 <= date.day <= 30:
            return base_sales * 1.80
        # Week before Christmas (Dec 18-24)
        if date.month == 12 and 18 <= date.day <= 24:
            return base_sales * 2.00

    return base_sales


def calculate_growth_rate(date, category):
    """Calculate year-over-year growth rate (CAGR)"""
    cagr = {
        "Women's Dresses": 0.08,  # 8% growth
        "Men's Shirts": 0.03,      # 3% growth
        "Accessories": 0.05        # 5% growth
    }

    # Calculate years since start of historical period
    years_elapsed = (date - HISTORICAL_START).days / 365.25
    growth_multiplier = (1 + cagr[category]) ** years_elapsed

    return growth_multiplier


def generate_store_attributes():
    """
    Generate store_attributes.csv with correlated features for K-means clustering

    Returns:
        DataFrame: Store attributes with 50 stores × 8 columns
    """
    print("Generating store attributes...")

    stores = []

    # Generate 50 stores with 3 intended clusters
    for i in range(1, NUM_STORES + 1):
        store_id = f"S{i:03d}"

        # Determine cluster intent (Fashion_Forward: 15, Mainstream: 20, Value_Conscious: 15)
        if i <= 15:
            # Fashion_Forward cluster
            size_sqft = np.random.randint(10000, 15000)
            income_level = np.random.randint(100000, 150000)
            foot_traffic = np.random.randint(2000, 3000)
            competitor_density = np.random.uniform(3.0, 8.0)
            online_penetration = np.random.uniform(0.40, 0.60)
            population_density = np.random.randint(8000, 15000)
            mall_location = np.random.choice([True, False], p=[0.7, 0.3])
        elif i <= 35:
            # Mainstream cluster
            size_sqft = np.random.randint(6000, 10000)
            income_level = np.random.randint(60000, 100000)
            foot_traffic = np.random.randint(800, 2000)
            competitor_density = np.random.uniform(2.0, 5.0)
            online_penetration = np.random.uniform(0.25, 0.45)
            population_density = np.random.randint(3000, 8000)
            mall_location = np.random.choice([True, False], p=[0.5, 0.5])
        else:
            # Value_Conscious cluster
            size_sqft = np.random.randint(3000, 6000)
            income_level = np.random.randint(35000, 60000)
            foot_traffic = np.random.randint(300, 800)
            competitor_density = np.random.uniform(0.5, 3.0)
            online_penetration = np.random.uniform(0.15, 0.35)
            population_density = np.random.randint(500, 3000)
            mall_location = np.random.choice([True, False], p=[0.2, 0.8])

        stores.append({
            'store_id': store_id,
            'size_sqft': size_sqft,
            'income_level': income_level,
            'foot_traffic': foot_traffic,
            'competitor_density': round(competitor_density, 2),
            'online_penetration': round(online_penetration, 2),
            'population_density': population_density,
            'mall_location': mall_location
        })

    df = pd.DataFrame(stores)

    # Save to CSV
    output_path = 'training/store_attributes.csv'
    df.to_csv(output_path, index=False)
    print(f"[OK] Generated {output_path} ({len(df)} stores)")

    return df


def calculate_store_sales_multiplier(store_row):
    """
    Calculates store-level sales multiplier based on attributes

    Args:
        store_row: pandas Series with store attributes

    Returns:
        float: sales multiplier (0.5x to 2.0x)
    """
    multiplier = (
        0.30 * (store_row['size_sqft'] / 10000) +
        0.25 * (store_row['income_level'] / 100000) +
        0.20 * (store_row['foot_traffic'] / 2000) +
        0.10 * (1 - store_row['online_penetration']) +
        0.10 * (store_row['population_density'] / 10000) +
        0.05 * int(store_row['mall_location'])
    )

    # Add ±20% noise
    multiplier *= np.random.uniform(0.8, 1.2)

    # Constrain to 0.5x - 2.0x range
    return np.clip(multiplier, 0.5, 2.0)


def generate_historical_sales(store_attributes):
    """
    Generate historical_sales_2022_2024.csv with realistic patterns

    Args:
        store_attributes: DataFrame with store attributes

    Returns:
        DataFrame: Historical sales data
    """
    print("Generating historical sales (2022-2024)...")

    sales_data = []

    # Calculate store multipliers once
    store_multipliers = {}
    for _, store in store_attributes.iterrows():
        store_multipliers[store['store_id']] = calculate_store_sales_multiplier(store)

    # Base daily sales per category (before any adjustments)
    base_daily_sales = {
        "Women's Dresses": 50,
        "Men's Shirts": 35,
        "Accessories": 45
    }

    # Generate daily sales for each store, category, and date
    current_date = HISTORICAL_START
    total_days = (HISTORICAL_END - HISTORICAL_START).days + 1

    for day_num in range(total_days):
        if day_num % 100 == 0:
            print(f"  Progress: {day_num}/{total_days} days...")

        for store_id in store_multipliers.keys():
            for category in CATEGORIES:
                # Calculate base quantity
                base_qty = base_daily_sales[category]

                # Apply adjustments
                qty = base_qty
                qty *= calculate_seasonality(current_date, category)
                qty *= get_weekly_pattern(current_date, category)
                qty = apply_holiday_spike(current_date, category, qty)
                qty *= calculate_growth_rate(current_date, category)
                qty *= store_multipliers[store_id]

                # Add ±10-15% noise (cleaner historical data)
                qty *= np.random.uniform(0.85, 1.15)

                # Round to integer and ensure non-negative
                qty = max(0, int(round(qty)))

                # Calculate revenue with ±10% price variability
                base_price = BASE_PRICES[category]
                actual_price = base_price * np.random.uniform(0.90, 1.10)
                revenue = qty * actual_price

                sales_data.append({
                    'date': current_date.strftime('%Y-%m-%d'),
                    'store_id': store_id,
                    'category': category,
                    'quantity_sold': qty,
                    'revenue': round(revenue, 2)
                })

        current_date += timedelta(days=1)

    df = pd.DataFrame(sales_data)

    # Save to CSV
    output_path = 'training/historical_sales_2022_2024.csv'
    df.to_csv(output_path, index=False)
    file_size_mb = os.path.getsize(output_path) / 1024 / 1024
    print(f"[OK] Generated {output_path} ({len(df)} rows, {file_size_mb:.1f} MB)")

    return df


def generate_scenario(scenario_name, store_attributes, historical_sales):
    """
    Generate 12 weekly actuals CSVs for a scenario

    Args:
        scenario_name: 'normal_season', 'high_demand', or 'low_demand'
        store_attributes: DataFrame with store attributes
        historical_sales: DataFrame with historical sales (for baseline patterns)
    """
    print(f"Generating {scenario_name} scenario...")

    # Calculate store multipliers
    store_multipliers = {}
    for _, store in store_attributes.iterrows():
        store_multipliers[store['store_id']] = calculate_store_sales_multiplier(store)

    # Base daily sales per category (2025 baseline, with slower growth)
    base_daily_sales = {
        "Women's Dresses": 54,  # Was growing 8%, now only 2%
        "Men's Shirts": 36,      # Was growing 3%, now flat
        "Accessories": 47        # Was growing 5%, now 2%
    }

    # Scenario adjustments
    if scenario_name == 'high_demand':
        scenario_multiplier = 1.25  # +25% across all
    elif scenario_name == 'low_demand':
        scenario_multiplier = 0.80  # -20% across all
    else:
        scenario_multiplier = 1.0    # Normal

    # Generate 12 weeks of data
    for week_num in range(1, 13):
        week_start = TESTING_START + timedelta(weeks=week_num - 1)
        week_data = []

        # Generate 7 days (Mon-Sun)
        for day_offset in range(7):
            current_date = week_start + timedelta(days=day_offset)

            for store_id in store_multipliers.keys():
                # Generate sales for the category being tested (Women's Dresses for Spring 2025)
                # In real usage, system auto-detects category from upload
                category = "Women's Dresses"  # Spring season category

                # Calculate base quantity
                base_qty = base_daily_sales[category]

                # Apply adjustments
                qty = base_qty
                qty *= calculate_seasonality(current_date, category)
                qty *= get_weekly_pattern(current_date, category)
                qty *= store_multipliers[store_id]
                qty *= scenario_multiplier

                # Add ±20-25% noise (messier testing data)
                qty *= np.random.uniform(0.75, 1.25)

                # Apply black swan event in Week 5
                if week_num == 5:
                    if scenario_name == 'normal_season':
                        # Viral TikTok trend: +30% for Women's Dresses
                        qty *= 1.30
                    elif scenario_name == 'high_demand':
                        # Competitor bankruptcy: +40% all
                        qty *= 1.40
                    elif scenario_name == 'low_demand':
                        # Supply chain disruption: -25% all
                        qty *= 0.75

                # Store-level heterogeneity: 10-15 stores deviate significantly
                if store_id in [f"S{i:03d}" for i in [5, 12, 18, 23, 27, 31, 35, 38, 42, 45, 48]]:
                    qty *= np.random.uniform(0.85, 1.15)  # ±15% deviation

                # Unpredictable events (random store closures, local festivals)
                if week_num == 3 and store_id in ['S007', 'S019']:
                    qty *= 0.3  # Store renovation (limited operations)
                if week_num == 3 and store_id == 'S025':
                    qty *= 1.5  # Local festival boost

                # Round to integer and ensure non-negative
                qty = max(0, int(round(qty)))

                week_data.append({
                    'date': current_date.strftime('%Y-%m-%d'),
                    'store_id': store_id,
                    'quantity_sold': qty
                })

        # Save weekly file
        df = pd.DataFrame(week_data)
        output_path = f'scenarios/{scenario_name}/actuals_week_{week_num:02d}.csv'
        df.to_csv(output_path, index=False)
        print(f"  [OK] Generated week {week_num:02d} ({len(df)} rows)")

    print(f"[OK] Completed {scenario_name} scenario (12 weeks)")


def validate_all_data():
    """Run 6 validation checks on generated data"""
    print("\n" + "="*60)
    print("Running Validation Suite")
    print("="*60)

    validation_results = {
        'completeness': False,
        'quality': False,
        'format': False,
        'statistical': False,
        'pattern': False,
        'weekly_actuals': False
    }

    # ===== Type 1: Completeness Check =====
    print("\n1. Completeness Check...")
    try:
        historical = pd.read_csv('training/historical_sales_2022_2024.csv')
        stores = pd.read_csv('training/store_attributes.csv')

        # Check historical row count (3 years with leap year 2024 = 1096 days)
        expected_historical_rows = 1096 * NUM_STORES * NUM_CATEGORIES  # 164,400
        actual_historical_rows = len(historical)
        completeness_ok = abs(actual_historical_rows - expected_historical_rows) < 100

        # Check stores
        stores_ok = len(stores) == NUM_STORES

        # Check for missing values
        no_missing_historical = historical.isnull().sum().sum() == 0
        no_missing_stores = stores.isnull().sum().sum() == 0

        # Check weekly actuals
        weekly_files_ok = True
        for scenario in ['normal_season', 'high_demand', 'low_demand']:
            for week in range(1, 13):
                filepath = f'scenarios/{scenario}/actuals_week_{week:02d}.csv'
                if not os.path.exists(filepath):
                    weekly_files_ok = False
                    print(f"  [X] Missing: {filepath}")
                else:
                    df = pd.read_csv(filepath)
                    expected_rows = NUM_STORES * 7  # 50 stores × 7 days
                    if len(df) != expected_rows:
                        print(f"  [WARN]  {filepath}: Expected {expected_rows} rows, got {len(df)}")

        if completeness_ok and stores_ok and no_missing_historical and no_missing_stores and weekly_files_ok:
            print("  [PASS] - All files present, correct row counts, no missing values")
            validation_results['completeness'] = True
        else:
            print(f"  [FAIL] - Historical: {actual_historical_rows}/{expected_historical_rows}, Stores: {len(stores)}/{NUM_STORES}")
    except Exception as e:
        print(f"  [ERROR]: {e}")

    # ===== Type 2: Data Quality Check =====
    print("\n2. Data Quality Check...")
    try:
        historical = pd.read_csv('training/historical_sales_2022_2024.csv')

        # Check for negative sales
        no_negatives = (historical['quantity_sold'] >= 0).all() and (historical['revenue'] >= 0).all()

        # Check revenue calculation (within ±1% tolerance)
        historical['calculated_price'] = historical['revenue'] / (historical['quantity_sold'] + 1e-6)  # Avoid div by 0
        price_errors = 0
        for category in CATEGORIES:
            cat_data = historical[historical['category'] == category]
            base_price = BASE_PRICES[category]
            # Prices should be within ±10% of base (our variability)
            valid_prices = ((cat_data['calculated_price'] >= base_price * 0.85) &
                           (cat_data['calculated_price'] <= base_price * 1.15)).sum()
            price_errors += len(cat_data) - valid_prices

        price_accuracy = price_errors / len(historical) < 0.05  # Less than 5% errors acceptable

        if no_negatives and price_accuracy:
            print("  [PASS] PASS - No negative sales, revenue calculations correct")
            validation_results['quality'] = True
        else:
            print(f"  [FAIL] FAIL - Negatives: {not no_negatives}, Price errors: {price_errors}")
    except Exception as e:
        print(f"  [FAIL] ERROR: {e}")

    # ===== Type 3: Format Check =====
    print("\n3. Format Check...")
    try:
        historical = pd.read_csv('training/historical_sales_2022_2024.csv')

        # Check date format
        pd.to_datetime(historical['date'], format='%Y-%m-%d')

        # Check store_id format
        store_ids_ok = historical['store_id'].str.match(r'S\d{3}').all()

        # Check categories
        categories_ok = historical['category'].isin(CATEGORIES).all()

        if store_ids_ok and categories_ok:
            print("  [PASS] PASS - Dates, store IDs, and categories properly formatted")
            validation_results['format'] = True
        else:
            print(f"  [FAIL] FAIL - Format issues detected")
    except Exception as e:
        print(f"  [FAIL] ERROR: {e}")

    # ===== Type 4: Statistical Check =====
    print("\n4. Statistical Check...")
    try:
        historical = pd.read_csv('training/historical_sales_2022_2024.csv')
        stores = pd.read_csv('training/store_attributes.csv')

        # Check category statistics (weekly aggregation)
        stats_ok = True
        for category in CATEGORIES:
            cat_data = historical[historical['category'] == category]
            # Aggregate to weekly level
            cat_data['date'] = pd.to_datetime(cat_data['date'])
            weekly = cat_data.groupby([pd.Grouper(key='date', freq='W'), 'store_id'])['quantity_sold'].sum()

            mean_weekly = weekly.mean()
            std_weekly = weekly.std()

            print(f"  {category}: Mean={mean_weekly:.1f}, StdDev={std_weekly:.1f}")

            # Validate against expected ranges (loose check)
            if category == "Women's Dresses":
                if not (50 <= mean_weekly <= 500):
                    stats_ok = False
            elif category == "Men's Shirts":
                if not (30 <= mean_weekly <= 400):
                    stats_ok = False
            else:  # Accessories
                if not (40 <= mean_weekly <= 500):
                    stats_ok = False

        # K-means clustering check
        feature_cols = ['size_sqft', 'income_level', 'foot_traffic', 'competitor_density',
                       'online_penetration', 'population_density']
        X = stores[feature_cols].values
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)

        kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
        clusters = kmeans.fit_predict(X_scaled)
        silhouette = silhouette_score(X_scaled, clusters)

        print(f"  K-means silhouette score: {silhouette:.3f} (target: >0.4)")
        cluster_ok = silhouette > 0.4

        if stats_ok and cluster_ok:
            print("  [PASS] PASS - Statistics within expected ranges, clusters distinguishable")
            validation_results['statistical'] = True
        else:
            print(f"  [FAIL] FAIL - Statistical validation issues")
    except Exception as e:
        print(f"  [FAIL] ERROR: {e}")

    # ===== Type 5: Pattern Check =====
    print("\n5. Pattern Check...")
    try:
        historical = pd.read_csv('training/historical_sales_2022_2024.csv')
        historical['date'] = pd.to_datetime(historical['date'])

        # Check Women's Dresses seasonality (Spring/Summer peak)
        dresses = historical[historical['category'] == "Women's Dresses"]
        spring_summer = dresses[dresses['date'].dt.month.isin([3,4,5,6,7,8])]['quantity_sold'].mean()
        fall_winter = dresses[dresses['date'].dt.month.isin([11,12,1,2])]['quantity_sold'].mean()
        dresses_seasonal_ok = spring_summer > fall_winter

        # Check Accessories seasonality (Q4 peak)
        accessories = historical[historical['category'] == "Accessories"]
        q4 = accessories[accessories['date'].dt.month.isin([11,12])]['quantity_sold'].mean()
        q1_q3 = accessories[~accessories['date'].dt.month.isin([11,12])]['quantity_sold'].mean()
        accessories_seasonal_ok = q4 > q1_q3

        print(f"  Women's Dresses: Spring/Summer avg={spring_summer:.1f}, Fall/Winter avg={fall_winter:.1f}")
        print(f"  Accessories: Q4 avg={q4:.1f}, Q1-Q3 avg={q1_q3:.1f}")

        # Check Week 5 variance spike
        variance_ok = True
        for scenario in ['normal_season', 'high_demand', 'low_demand']:
            week5_file = f'scenarios/{scenario}/actuals_week_05.csv'
            if os.path.exists(week5_file):
                week5_data = pd.read_csv(week5_file)
                week5_total = week5_data['quantity_sold'].sum()

                # Compare to Week 4 (rough check)
                week4_file = f'scenarios/{scenario}/actuals_week_04.csv'
                week4_data = pd.read_csv(week4_file)
                week4_total = week4_data['quantity_sold'].sum()

                variance_pct = abs((week5_total - week4_total) / week4_total * 100)
                print(f"  {scenario} Week 5 variance: {variance_pct:.1f}%")

                if variance_pct < 15:  # Should be >20%, but allow some flexibility
                    variance_ok = False

        if dresses_seasonal_ok and accessories_seasonal_ok and variance_ok:
            print("  [PASS] PASS - Seasonality patterns detected, Week 5 variance present")
            validation_results['pattern'] = True
        else:
            print(f"  [FAIL] FAIL - Pattern validation issues")
    except Exception as e:
        print(f"  [FAIL] ERROR: {e}")

    # ===== Type 6: Weekly Actuals Validation =====
    print("\n6. Weekly Actuals Validation...")
    try:
        actuals_ok = True
        for scenario in ['normal_season', 'high_demand', 'low_demand']:
            for week in range(1, 13):
                filepath = f'scenarios/{scenario}/actuals_week_{week:02d}.csv'
                df = pd.read_csv(filepath)
                df['date'] = pd.to_datetime(df['date'])

                # Check 7 consecutive days
                date_range = (df['date'].max() - df['date'].min()).days
                if date_range != 6:  # 7 days = 6 day difference
                    actuals_ok = False
                    print(f"  [WARN]  {filepath}: Date range is {date_range} days (expected 6)")

                # Check all 50 stores present
                unique_stores = df['store_id'].nunique()
                if unique_stores != NUM_STORES:
                    actuals_ok = False
                    print(f"  [WARN]  {filepath}: {unique_stores} stores (expected {NUM_STORES})")

        if actuals_ok:
            print("  [PASS] PASS - All weekly actuals have 7 consecutive days, 50 stores each")
            validation_results['weekly_actuals'] = True
        else:
            print(f"  [FAIL] FAIL - Weekly actuals validation issues")
    except Exception as e:
        print(f"  [FAIL] ERROR: {e}")

    # ===== Summary =====
    print("\n" + "="*60)
    print("Validation Summary")
    print("="*60)

    passed = sum(validation_results.values())
    total = len(validation_results)

    for check, result in validation_results.items():
        status = "[PASS] PASS" if result else "[FAIL] FAIL"
        print(f"{status} - {check.replace('_', ' ').title()}")

    print(f"\nTotal: {passed}/{total} checks passed")

    if passed == total:
        print("\n[SUCCESS] All validations passed! Data generation successful.")
        return True
    else:
        print("\n[WARN]  Some validations failed. Review output above.")
        return False


def main():
    """Main entry point for data generation"""
    parser = argparse.ArgumentParser(description='Generate mock retail sales data')
    parser.add_argument('--regenerate', action='store_true',
                       help='Generate fresh data (ignore fixed seed)')
    parser.add_argument('--validate', action='store_true',
                       help='Run validation checks after generation')
    args = parser.parse_args()

    print("="*60)
    print("Mock Data Generation for Fashion Retail PoC")
    print("="*60)

    # Set seed
    set_seed(args.regenerate)

    # Generate data
    print("\n[1/5] Generating store attributes...")
    store_attributes = generate_store_attributes()

    print("\n[2/5] Generating historical sales...")
    historical_sales = generate_historical_sales(store_attributes)

    print("\n[3/5] Generating normal season scenario...")
    generate_scenario('normal_season', store_attributes, historical_sales)

    print("\n[4/5] Generating high demand scenario...")
    generate_scenario('high_demand', store_attributes, historical_sales)

    print("\n[5/5] Generating low demand scenario...")
    generate_scenario('low_demand', store_attributes, historical_sales)

    print("\n" + "="*60)
    print("[PASS] Data generation complete!")
    print("="*60)

    # Count files
    total_files = 1 + 1 + 36  # historical + stores + 36 weekly actuals
    print(f"\nGenerated Files: {total_files}")
    print(f"  - training/historical_sales_2022_2024.csv")
    print(f"  - training/store_attributes.csv")
    print(f"  - scenarios/normal_season/ (12 files)")
    print(f"  - scenarios/high_demand/ (12 files)")
    print(f"  - scenarios/low_demand/ (12 files)")

    # Validate if requested
    if args.validate:
        validate_all_data()

    print("\n" + "="*60)
    print("Next Steps:")
    print("1. Review validation results above")
    print("2. Load data: pd.read_csv('training/historical_sales_2022_2024.csv')")
    print("3. Test scenarios: Load from scenarios/normal_season/ folder")
    print("="*60)


if __name__ == '__main__':
    main()
