# Data Specification v3.2: Mock Data Generation for Fashion Retail PoC

**Status**: Ready for Implementation ✅
**Last Updated**: 2025-10-14
**Version**: 3.2 (aligned with Product Brief, Technical Architecture, Frontend Spec)
**Target Agent**: `*agent dev`

---

## 1. Overview

This document specifies the mock data generation requirements for the **Archetype 1: Fashion Retail PoC** (12-week season). The data supports a 3-agent demand forecasting system (Demand Agent, Inventory Agent, Pricing Agent + Orchestrator).

**Purpose**: Generate realistic synthetic retail sales data that produces **MAPE 12-18%** forecast accuracy (not suspiciously perfect, not unusably bad).

**Key Requirements**:
- ✅ High realism: holidays, promotions, external shocks, competitor effects
- ✅ Different seasonal patterns per category (Women's Dresses, Men's Shirts, Accessories)
- ✅ Store attributes correlate with sales performance
- ✅ Variable pricing with ±10% noise
- ✅ Comprehensive validation suite (6 types)
- ✅ Pure Python (numpy + pandas only)
- ✅ Fixed seed (42) + `--regenerate` flag for fresh data
- ✅ Scenario-based folder structure

---

## 2. Data Architecture

### 2.1 File Structure

```
data/mock/
├── training/
│   ├── historical_sales_2022_2024.csv        (~54,750 rows)
│   └── store_attributes.csv                  (50 rows)
├── scenarios/
│   ├── normal_season/
│   │   ├── actuals_week_01.csv               (~350 rows each)
│   │   ├── actuals_week_02.csv
│   │   ├── actuals_week_03.csv
│   │   ├── ...
│   │   └── actuals_week_12.csv
│   ├── high_demand/
│   │   ├── actuals_week_01.csv
│   │   ├── ...
│   │   └── actuals_week_12.csv
│   └── low_demand/
│       ├── actuals_week_01.csv
│       ├── ...
│       └── actuals_week_12.csv
├── README.md                                  (usage guide)
└── generate_mock_data.py                      (generation script)
```

**Total Files**: 38 CSV files (1 historical + 1 store attributes + 36 weekly actuals)

---

### 2.2 Data Types

| Data Type | Purpose | Time Period | Noise Level | Format |
|-----------|---------|-------------|-------------|--------|
| **Historical Sales** | Training data for Prophet+ARIMA | 2022-01-01 to 2024-12-31 (3 years) | ±10-15% | CSV |
| **Store Attributes** | K-means clustering features | Static (2025) | ±20% (formula-based) | CSV |
| **Weekly Actuals** | Testing data for variance calculation | 2025-02-17 to 2025-05-11 (12 weeks) | ±20-25% + disruptions | CSV |

---

## 3. Data Dictionary

### 3.1 Historical Sales CSV (`training/historical_sales_2022_2024.csv`)

**Purpose**: Training data for Prophet+ARIMA ensemble forecasting and K-means clustering.

**Schema**:

| Column | Data Type | Description | Example | Constraints |
|--------|-----------|-------------|---------|-------------|
| `date` | DATE | Sales date (daily granularity) | `2022-01-01` | `2022-01-01` to `2024-12-31` |
| `store_id` | STRING | Store identifier | `S001` | `S001` to `S050` (50 stores) |
| `category` | STRING | Product category | `Women's Dresses` | One of: `Women's Dresses`, `Men's Shirts`, `Accessories` |
| `quantity_sold` | INTEGER | Units sold on that date | `23` | `0` to `200` (varies by category/season) |
| `revenue` | FLOAT | Total revenue (price × quantity) | `1265.50` | Variable pricing: base ± 10% |

**Row Count**: ~54,750 rows (3 years × 365 days × 50 stores ÷ 3 categories = 18,250 rows per category)

**Key Characteristics**:
- **Cleaner patterns** (±10-15% noise) - Prophet/ARIMA can learn trends
- **Realistic seasonality** (see Section 4.2)
- **Holiday spikes** (Black Friday, Valentine's Day, Mother's Day)
- **Promotional periods** (End of Season Sales, Back to School)
- **Weekly patterns** (weekends higher for Dresses/Accessories, steady for Shirts)

---

### 3.2 Store Attributes CSV (`training/store_attributes.csv`)

**Purpose**: Features for K-means clustering (K=3) to create store segments (Fashion_Forward, Mainstream, Value_Conscious).

**Schema**:

| Column | Data Type | Description | Example | Range/Values |
|--------|-----------|-------------|---------|--------------|
| `store_id` | STRING | Store identifier | `S001` | `S001` to `S050` |
| `size_sqft` | INTEGER | Store size in square feet | `8500` | `3,000` to `15,000` |
| `income_level` | INTEGER | Median household income in area | `75000` | `35,000` to `150,000` |
| `foot_traffic` | INTEGER | Average daily foot traffic | `1200` | `300` to `3,000` |
| `competitor_density` | FLOAT | Number of competitors within 5 miles | `4.2` | `0.5` to `8.0` |
| `online_penetration` | FLOAT | % of local customers who shop online | `0.35` | `0.15` to `0.60` |
| `population_density` | INTEGER | People per square mile | `5500` | `500` to `15,000` |
| `mall_location` | BOOLEAN | Is store in shopping mall? | `true` | `true` or `false` |

**Row Count**: 50 rows (one per store)

**Correlation Formula** (for sales performance):
```python
# Base sales multiplier for a store
sales_multiplier = (
    0.30 * (size_sqft / 10000) +           # Larger stores sell more
    0.25 * (income_level / 100000) +       # Wealthier areas buy more
    0.20 * (foot_traffic / 2000) +         # More traffic = more sales
    0.10 * (1 - online_penetration) +      # Less online = more in-store
    0.10 * (population_density / 10000) +  # Dense areas = more customers
    0.05 * mall_location                   # Malls boost traffic
) * (1 + np.random.uniform(-0.2, 0.2))     # ±20% noise

# Constraint: sales_multiplier ranges from 0.5x to 2.0x baseline
```

**Expected Clusters** (K-means should discover these):
- **Cluster 1 (Fashion_Forward)**: Large stores, high income, high foot traffic (~15 stores)
- **Cluster 2 (Mainstream)**: Medium stores, medium income, moderate traffic (~20 stores)
- **Cluster 3 (Value_Conscious)**: Small stores, lower income, lower traffic (~15 stores)

---

### 3.3 Weekly Actuals CSV (`scenarios/{scenario}/actuals_week_XX.csv`)

**Purpose**: Testing data uploaded by user every Monday to calculate variance and trigger re-forecast if >20%.

**Schema**:

| Column | Data Type | Description | Example | Constraints |
|--------|-----------|-------------|---------|-------------|
| `date` | DATE | Sales date (daily granularity) | `2025-02-17` | 7 consecutive days (Mon-Sun) |
| `store_id` | STRING | Store identifier | `S001` | `S001` to `S050` |
| `quantity_sold` | INTEGER | Units sold on that date | `18` | Messier than historical (±20-25% noise) |

**Row Count**: ~350 rows per file (50 stores × 7 days)

**Key Characteristics**:
- **Messier patterns** (±20-25% noise) - harder to forecast
- **Unpredictable events** (store renovations, local festivals, competitor sales)
- **Trend breaks** (historical 8% growth → 2025 only 2% growth)
- **Black swan event** (Week 5: viral trend, supply crisis, or competitor bankruptcy)
- **Store heterogeneity** (10-15 stores deviate from cluster patterns)
- **Seasonality shifts** (2025 peak shifts by 2-3 weeks vs historical)

**Note**: System aggregates daily sales to weekly totals, then calculates category-level variance.

---

## 4. Data Generation Requirements

### 4.1 Category Definitions

| Category | Description | Average Price | Seasonality | Target CAGR (2022-2024) |
|----------|-------------|---------------|-------------|-------------------------|
| **Women's Dresses** | Fashion-forward seasonal items | $55 ± $5.50 | Peak Spring/Summer (Mar-Aug) | 8% |
| **Men's Shirts** | Basic wardrobe staples | $35 ± $3.50 | Steady year-round | 3% |
| **Accessories** | Belts, scarves, jewelry, bags | $25 ± $2.50 | Peak holiday season (Nov-Dec) | 5% |

**Auto-Detection**: System automatically detects category from uploaded CSV (no manual selection).

---

### 4.2 Seasonal Patterns (Historical 2022-2024)

#### Women's Dresses
```python
# Base seasonality (multiplicative)
seasonality = {
    "Jan": 0.6, "Feb": 0.7, "Mar": 1.2, "Apr": 1.4, "May": 1.5,  # Spring peak
    "Jun": 1.3, "Jul": 1.2, "Aug": 1.1,                           # Summer high
    "Sep": 0.9, "Oct": 0.8, "Nov": 0.7, "Dec": 0.8               # Fall/Winter low
}

# Holiday spikes (additive)
holidays = {
    "Valentine's Day (Feb 14)": +30% for 3 days,
    "Mother's Day (May 12)": +40% for 5 days,
    "End of Season Sale (Aug 15-31)": +20% sustained
}

# Weekly pattern
weekly = {
    "Mon": 0.8, "Tue": 0.9, "Wed": 1.0, "Thu": 1.1,
    "Fri": 1.3, "Sat": 1.5, "Sun": 1.2  # Weekend shopping
}
```

#### Men's Shirts
```python
# Base seasonality (flatter than dresses)
seasonality = {
    "Jan": 0.9, "Feb": 0.9, "Mar": 1.0, "Apr": 1.0, "May": 1.0,
    "Jun": 1.1, "Jul": 1.0, "Aug": 1.2,  # Back to school
    "Sep": 1.1, "Oct": 1.0, "Nov": 1.0, "Dec": 1.0
}

# Holiday spikes
holidays = {
    "Father's Day (Jun 16)": +25% for 4 days,
    "Back to School (Aug 20-Sep 10)": +15% sustained,
    "Black Friday (Nov 29)": +35% for 4 days
}

# Weekly pattern (more stable)
weekly = {
    "Mon": 0.95, "Tue": 0.95, "Wed": 1.0, "Thu": 1.0,
    "Fri": 1.1, "Sat": 1.15, "Sun": 1.05
}
```

#### Accessories
```python
# Base seasonality (holiday-driven)
seasonality = {
    "Jan": 0.6, "Feb": 0.8, "Mar": 0.9, "Apr": 1.0, "May": 1.0,
    "Jun": 0.9, "Jul": 0.8, "Aug": 0.9, "Sep": 1.0, "Oct": 1.1,
    "Nov": 1.6, "Dec": 1.8  # Massive holiday surge
}

# Holiday spikes
holidays = {
    "Valentine's Day (Feb 14)": +50% for 3 days (jewelry/scarves as gifts),
    "Black Friday (Nov 29)": +80% for 4 days (gift shopping),
    "Week before Christmas (Dec 18-24)": +100% sustained
}

# Weekly pattern (strong weekend effect)
weekly = {
    "Mon": 0.7, "Tue": 0.8, "Wed": 0.9, "Thu": 1.0,
    "Fri": 1.4, "Sat": 1.6, "Sun": 1.3  # Heavy weekend shopping
}
```

---

### 4.3 Pricing Strategy

**Base Prices** (2022-2024):
- Women's Dresses: $55.00
- Men's Shirts: $35.00
- Accessories: $25.00

**Price Variability**: ±10% random noise per transaction
```python
actual_price = base_price * np.random.uniform(0.90, 1.10)
```

**Why variable pricing?**
- ✅ Simulates promotions, discounts, clearance
- ✅ More realistic than fixed prices
- ✅ Simple enough (no complex markdown logic in historical data)

**Revenue Calculation**:
```python
revenue = quantity_sold * actual_price
```

---

### 4.4 Scenario Definitions (2025 Testing Data)

#### Scenario 1: Normal Season
**Description**: Expected Spring 2025 season with typical patterns.

**Characteristics**:
- ✅ Baseline seasonality (similar to 2022-2024)
- ✅ 8% → 2% growth slowdown (economic headwinds)
- ✅ Minor unpredictable events (2-3 store renovations, local festival in Week 3)
- ✅ Week 5 black swan: Viral TikTok trend boosts Women's Dresses +30% for 5 days
- ✅ 10 stores deviate from cluster patterns (±15%)

**Expected MAPE**: 12-15%

---

#### Scenario 2: High Demand
**Description**: Unexpectedly strong Spring 2025 season.

**Characteristics**:
- ✅ Economic boom → consumer confidence surge
- ✅ All categories +25% above baseline
- ✅ Fashion_Forward cluster performs +40% (wealthy consumers spending more)
- ✅ Week 5 black swan: Major competitor bankruptcy → traffic surge to our stores
- ✅ Seasonality peak shifts earlier (April instead of May for Dresses)
- ✅ 12 stores deviate significantly (±20%)

**Expected MAPE**: 15-18% (harder to predict surge)

---

#### Scenario 3: Low Demand
**Description**: Weaker-than-expected Spring 2025 season.

**Characteristics**:
- ✅ Economic uncertainty → reduced discretionary spending
- ✅ All categories -20% below baseline
- ✅ Value_Conscious cluster performs worst (-30%, income-sensitive)
- ✅ Week 5 black swan: Supply chain disruption → stockouts limit sales
- ✅ Online competition intensifies → 5% additional erosion
- ✅ 15 stores deviate significantly (±25%, unpredictable local conditions)

**Expected MAPE**: 15-18% (harder to predict decline)

---

### 4.5 Realism Strategies (Target MAPE 12-18%)

**Problem**: Synthetic data can be "too clean" → suspiciously low MAPE (5-8%).

**Solution - 6 Techniques**:

1. **Training vs Test Noise Differential**
   - Historical (2022-2024): ±10-15% noise
   - Weekly Actuals (2025): ±20-25% noise
   - **Effect**: Models trained on clean data, tested on messy reality

2. **Unpredictable Events (2025 only)**
   - Store renovations (2-3 stores, 2-week closures)
   - Local festivals (1-day traffic spikes)
   - Competitor flash sales (temporary demand drops)
   - **Effect**: Prophet/ARIMA can't predict these from historical data

3. **Trend Breaks**
   - Historical CAGR (2022-2024): Women's Dresses +8%
   - Actual 2025 growth: +2% (economic slowdown)
   - **Effect**: Prophet extrapolates 8%, reality diverges

4. **Black Swan Event (Week 5)**
   - Normal: Viral TikTok trend (+30% Dresses for 5 days)
   - High Demand: Competitor bankruptcy (+40% all categories)
   - Low Demand: Supply chain crisis (-25% all categories)
   - **Effect**: Massive variance spike → triggers re-forecast

5. **Store-Level Heterogeneity**
   - 10-15 stores deviate from cluster patterns
   - Example: S023 (Mainstream cluster) performs like Fashion_Forward
   - **Effect**: K-means clusters imperfect predictors

6. **Seasonality Shifts (2025 vs Historical)**
   - Historical: Women's Dresses peak in May
   - 2025: Peak shifts to April (weather change, fashion trends)
   - **Effect**: Prophet's seasonal component slightly off

**Validation**: If MAPE <10%, add more noise. If MAPE >20%, reduce disruptions.

---

## 5. Data Validation Requirements

**Purpose**: Ensure generated data is usable for ML training and testing.

### 5.1 Validation Types (All 6 Required)

#### Type 1: Completeness Check
- [ ] Historical CSV has 54,750 rows (3 years × 365 days × 50 stores)
- [ ] Store attributes CSV has 50 rows
- [ ] Each weekly actuals CSV has ~350 rows (50 stores × 7 days)
- [ ] No missing values in required columns
- [ ] All 50 stores present in every file

#### Type 2: Data Quality Check
- [ ] `quantity_sold` ≥ 0 (no negative sales)
- [ ] `revenue` = `quantity_sold` × `price` (within ±1% tolerance)
- [ ] `date` is valid and sequential
- [ ] `store_id` matches `S001` to `S050` format
- [ ] `category` is one of 3 valid values

#### Type 3: Format Check
- [ ] CSV delimiter: comma (`,`)
- [ ] Date format: `YYYY-MM-DD`
- [ ] Encoding: UTF-8
- [ ] No extra whitespace in columns
- [ ] Headers match schema exactly

#### Type 4: Statistical Check
- [ ] Women's Dresses: Mean weekly sales 50-150 units/store, StdDev 20-60
- [ ] Men's Shirts: Mean weekly sales 30-100 units/store, StdDev 15-40
- [ ] Accessories: Mean weekly sales 40-120 units/store, StdDev 25-70
- [ ] Store attributes: Mean income_level $70K-$90K, StdDev $25K-$40K
- [ ] K-means on store_attributes produces 3 distinct clusters (silhouette score >0.4)

#### Type 5: Pattern Check
- [ ] Historical data shows clear seasonality (FFT or autocorrelation test)
- [ ] Women's Dresses peak in Spring/Summer (Mar-Aug avg > Nov-Feb avg)
- [ ] Accessories peak in Nov-Dec (Q4 avg > Q1-Q3 avg)
- [ ] Weekly actuals (2025) have higher variance than historical (2022-2024)
- [ ] Week 5 shows variance spike >20% in at least 2 scenarios

#### Type 6: Weekly Actuals Validation
- [ ] Each actuals file covers exactly 7 consecutive days (Mon-Sun)
- [ ] Week 1 starts 2025-02-17 (Monday of Spring 2025 season start)
- [ ] Week 12 ends 2025-05-11 (Sunday of season end)
- [ ] Actuals files have same `store_id` as historical (50 stores)
- [ ] Category can be inferred from aggregated weekly sales patterns

---

### 5.2 Validation Script Output

```python
# Expected output from generate_mock_data.py --validate

=== Data Validation Report ===

✅ Completeness: PASS (38/38 files, 0 missing values)
✅ Data Quality: PASS (0 negative sales, 0 calculation errors)
✅ Format: PASS (UTF-8, correct headers, valid dates)
✅ Statistical: PASS (means/stdevs within expected ranges)
✅ Pattern: PASS (seasonality detected, correct peaks)
✅ Weekly Actuals: PASS (date ranges correct, 50 stores)

⚠️  Warnings:
- Scenario "high_demand" Week 5 variance: 28% (expected >20%, OK)
- Store S042 deviates +22% from cluster (expected <25%, OK)

=== Generated Files ===
training/historical_sales_2022_2024.csv: 54,750 rows, 3.2 MB
training/store_attributes.csv: 50 rows, 12 KB
scenarios/normal_season/: 12 files, 0.8 MB total
scenarios/high_demand/: 12 files, 0.9 MB total
scenarios/low_demand/: 12 files, 0.7 MB total

=== Next Steps ===
1. Load training data: pd.read_csv('data/mock/training/historical_sales_2022_2024.csv')
2. Test Scenario 1: Load 'data/mock/scenarios/normal_season/' folder
3. Expected MAPE: 12-18% (if <10% or >20%, regenerate with adjusted noise)
```

---

## 6. Implementation Guidance

### 6.1 Script Structure

```python
# generate_mock_data.py

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import argparse

# Fixed seed for reproducibility (can override with --regenerate)
SEED = 42

def main():
    parser = argparse.ArgumentParser(description='Generate mock retail sales data')
    parser.add_argument('--regenerate', action='store_true',
                        help='Generate fresh data (ignore fixed seed)')
    parser.add_argument('--validate', action='store_true',
                        help='Run validation checks after generation')
    args = parser.parse_args()

    # Set seed
    if args.regenerate:
        np.random.seed(int(time.time()))
    else:
        np.random.seed(SEED)

    # Generate data
    generate_store_attributes()
    generate_historical_sales()
    generate_scenario('normal_season')
    generate_scenario('high_demand')
    generate_scenario('low_demand')

    # Validate if requested
    if args.validate:
        validate_all_data()

    print("✅ Data generation complete!")

def generate_store_attributes():
    """Generate store_attributes.csv with correlated features"""
    # Implementation: 50 stores, 7 features, formula-based correlation
    pass

def generate_historical_sales():
    """Generate historical_sales_2022_2024.csv with seasonality"""
    # Implementation: 3 years, 3 categories, seasonality + holidays + weekly
    pass

def generate_scenario(scenario_name):
    """Generate 12 weekly actuals CSVs for a scenario"""
    # Implementation: 12 weeks, messier patterns, black swan in Week 5
    pass

def validate_all_data():
    """Run 6 validation checks"""
    # Implementation: completeness, quality, format, stats, patterns, weekly
    pass

if __name__ == '__main__':
    main()
```

---

### 6.2 Key Functions to Implement

#### Function 1: `calculate_seasonality(date, category)`
```python
def calculate_seasonality(date, category):
    """
    Returns seasonality multiplier for a given date and category.

    Args:
        date: datetime object
        category: 'Women's Dresses', 'Men's Shirts', or 'Accessories'

    Returns:
        float: seasonality multiplier (0.6 to 1.8)
    """
    month = date.month

    if category == "Women's Dresses":
        monthly_factors = {1: 0.6, 2: 0.7, 3: 1.2, 4: 1.4, 5: 1.5,
                          6: 1.3, 7: 1.2, 8: 1.1, 9: 0.9, 10: 0.8,
                          11: 0.7, 12: 0.8}
    elif category == "Men's Shirts":
        monthly_factors = {1: 0.9, 2: 0.9, 3: 1.0, 4: 1.0, 5: 1.0,
                          6: 1.1, 7: 1.0, 8: 1.2, 9: 1.1, 10: 1.0,
                          11: 1.0, 12: 1.0}
    else:  # Accessories
        monthly_factors = {1: 0.6, 2: 0.8, 3: 0.9, 4: 1.0, 5: 1.0,
                          6: 0.9, 7: 0.8, 8: 0.9, 9: 1.0, 10: 1.1,
                          11: 1.6, 12: 1.8}

    return monthly_factors[month]
```

#### Function 2: `apply_holiday_spike(date, category, base_sales)`
```python
def apply_holiday_spike(date, category, base_sales):
    """
    Applies holiday spike to base sales if date is near a holiday.

    Args:
        date: datetime object
        category: product category
        base_sales: baseline sales quantity

    Returns:
        int: adjusted sales quantity
    """
    # Check if date is within holiday window
    # Apply category-specific spike multiplier
    # Examples: Valentine's +30% Dresses, Black Friday +80% Accessories
    pass
```

#### Function 3: `calculate_store_sales_multiplier(store_attributes)`
```python
def calculate_store_sales_multiplier(store_attributes):
    """
    Calculates store-level sales multiplier based on attributes.

    Args:
        store_attributes: dict with 7 features

    Returns:
        float: sales multiplier (0.5x to 2.0x)
    """
    multiplier = (
        0.30 * (store_attributes['size_sqft'] / 10000) +
        0.25 * (store_attributes['income_level'] / 100000) +
        0.20 * (store_attributes['foot_traffic'] / 2000) +
        0.10 * (1 - store_attributes['online_penetration']) +
        0.10 * (store_attributes['population_density'] / 10000) +
        0.05 * store_attributes['mall_location']
    )

    # Add ±20% noise
    multiplier *= np.random.uniform(0.8, 1.2)

    # Constrain to 0.5x - 2.0x range
    return np.clip(multiplier, 0.5, 2.0)
```

#### Function 4: `inject_black_swan_event(scenario, week, category_sales)`
```python
def inject_black_swan_event(scenario, week, category_sales):
    """
    Injects black swan event in Week 5 based on scenario.

    Args:
        scenario: 'normal_season', 'high_demand', or 'low_demand'
        week: 1-12
        category_sales: pandas DataFrame with daily sales

    Returns:
        DataFrame: adjusted sales with black swan effect
    """
    if week != 5:
        return category_sales  # No change

    if scenario == 'normal_season':
        # Viral TikTok trend: +30% Women's Dresses for 5 days
        mask = category_sales['category'] == "Women's Dresses"
        category_sales.loc[mask, 'quantity_sold'] *= 1.30

    elif scenario == 'high_demand':
        # Competitor bankruptcy: +40% all categories
        category_sales['quantity_sold'] *= 1.40

    elif scenario == 'low_demand':
        # Supply chain disruption: -25% all categories
        category_sales['quantity_sold'] *= 0.75

    return category_sales
```

---

### 6.3 Usage Examples

#### Generate Data (First Time)
```bash
cd data/mock
python generate_mock_data.py --validate
```

**Expected Output**:
```
Generating store attributes... ✓ (50 stores)
Generating historical sales... ✓ (54,750 rows, 2022-2024)
Generating normal_season scenario... ✓ (12 weeks)
Generating high_demand scenario... ✓ (12 weeks)
Generating low_demand scenario... ✓ (12 weeks)

Running validation checks...
✅ All 6 validation types passed!
✅ Data generation complete!
```

---

#### Regenerate Fresh Data
```bash
python generate_mock_data.py --regenerate --validate
```

**Use Case**: Want to test robustness across different data variations.

---

#### Load Data in Backend (Python)
```python
import pandas as pd

# Load training data
historical = pd.read_csv('data/mock/training/historical_sales_2022_2024.csv')
stores = pd.read_csv('data/mock/training/store_attributes.csv')

# Train Prophet+ARIMA models
demand_agent.train(historical, stores)

# Test with Scenario 1
actuals_week_1 = pd.read_csv('data/mock/scenarios/normal_season/actuals_week_01.csv')
variance = demand_agent.calculate_variance(forecast_week_1, actuals_week_1)

print(f"Variance: {variance:.1f}%")  # Expected: 8-15%
```

---

## 7. Testing Workflow

### 7.1 Pre-Season (Setup)
1. User uploads `historical_sales_2022_2024.csv` (one-time)
2. System trains Prophet+ARIMA models (2-3 minutes)
3. System runs K-means clustering on `store_attributes.csv` → 3 clusters
4. System generates forecast for 12-week season (category-level)
5. Frontend shows initial forecast in dashboard

---

### 7.2 In-Season (Weekly Loop)
**Every Monday for 12 weeks**:

1. User uploads `actuals_week_X.csv` (previous week's sales)
2. System aggregates daily sales → weekly totals per store → category-level actuals
3. System calculates variance: `(actual - forecast) / forecast × 100%`
4. If variance >20%:
   - System triggers re-forecast (Orchestrator calls Demand Agent)
   - Inventory Agent recalculates manufacturing orders
   - Pricing Agent adjusts markdown timing if needed
5. Frontend updates variance chart, alert banners

---

### 7.3 Mid-Season (Week 6 Checkpoint)
1. System calculates sell-through: `(units_sold_weeks_1-6) / (initial_inventory)`
2. If sell-through <60%:
   - Pricing Agent calculates markdown: `Gap × Elasticity` formula
   - System recommends uniform markdown across all stores
3. Frontend shows markdown recommendations in Section 6

---

### 7.4 Expected Test Results

| Scenario | Week 1-4 Variance | Week 5 Variance | Week 6-12 Variance | MAPE | Re-forecast Triggered? |
|----------|-------------------|-----------------|---------------------|------|------------------------|
| **Normal Season** | 8-15% | 22-28% | 10-16% | 12-15% | ✅ Yes (Week 5) |
| **High Demand** | 12-18% | 30-35% | 15-20% | 15-18% | ✅ Yes (Week 5) |
| **Low Demand** | 10-17% | 25-32% | 12-18% | 15-18% | ✅ Yes (Week 5) |

**Validation Criteria**:
- ✅ MAPE between 12-18% (realistic forecast accuracy)
- ✅ Week 5 variance >20% in all scenarios (black swan event)
- ✅ Re-forecast improves accuracy in Weeks 6-12 (variance decreases)

---

## 8. README.md Template

**Create this file at `data/mock/README.md`** (for *agent dev and *agent qa):

```markdown
# Mock Data for Fashion Retail PoC

**Purpose**: Synthetic retail sales data for testing 3-agent demand forecasting system.

## Quick Start

### Generate Data
```bash
python generate_mock_data.py --validate
```

### Load Data (Python)
```python
import pandas as pd

# Training data
historical = pd.read_csv('training/historical_sales_2022_2024.csv')
stores = pd.read_csv('training/store_attributes.csv')

# Testing data (Scenario 1)
actuals_w1 = pd.read_csv('scenarios/normal_season/actuals_week_01.csv')
```

---

## File Structure

- `training/` - Historical data for model training (2022-2024)
- `scenarios/normal_season/` - 12 weekly actuals for typical Spring 2025
- `scenarios/high_demand/` - 12 weekly actuals for high-demand Spring 2025
- `scenarios/low_demand/` - 12 weekly actuals for low-demand Spring 2025

---

## Data Dictionary

### historical_sales_2022_2024.csv
| Column | Type | Description | Example |
|--------|------|-------------|---------|
| `date` | DATE | Sales date | `2022-01-01` |
| `store_id` | STRING | Store ID (S001-S050) | `S023` |
| `category` | STRING | Product category | `Women's Dresses` |
| `quantity_sold` | INT | Units sold | `47` |
| `revenue` | FLOAT | Total revenue | `2585.50` |

**Rows**: 54,750 (3 years × 50 stores × 3 categories)

### store_attributes.csv
| Column | Type | Description | Range |
|--------|------|-------------|-------|
| `store_id` | STRING | Store ID | `S001`-`S050` |
| `size_sqft` | INT | Store size | 3,000-15,000 |
| `income_level` | INT | Area median income | $35K-$150K |
| `foot_traffic` | INT | Daily foot traffic | 300-3,000 |
| `competitor_density` | FLOAT | Competitors nearby | 0.5-8.0 |
| `online_penetration` | FLOAT | Online shopping % | 0.15-0.60 |
| `population_density` | INT | People per sq mi | 500-15,000 |
| `mall_location` | BOOL | In shopping mall? | true/false |

**Rows**: 50 (one per store)

### actuals_week_XX.csv
| Column | Type | Description | Example |
|--------|------|-------------|---------|
| `date` | DATE | Sales date | `2025-02-17` |
| `store_id` | STRING | Store ID | `S023` |
| `quantity_sold` | INT | Units sold | `52` |

**Rows**: ~350 per file (50 stores × 7 days)

---

## Testing Instructions

### Test Scenario 1: Normal Season
```python
# Load all 12 weekly actuals
import glob
actuals_files = sorted(glob.glob('scenarios/normal_season/actuals_week_*.csv'))
for week, file in enumerate(actuals_files, start=1):
    actuals = pd.read_csv(file)
    variance = calculate_variance(forecast[week], actuals)
    print(f"Week {week}: Variance = {variance:.1f}%")
```

**Expected Result**:
- Weeks 1-4: Variance 8-15%
- Week 5: Variance ~25% (viral TikTok trend) → triggers re-forecast
- Weeks 6-12: Variance 10-16% (improved after re-forecast)
- **Final MAPE**: 12-15%

### Test Scenario 2: High Demand
```python
# Same code, but use 'scenarios/high_demand/' folder
```

**Expected Result**:
- Week 5: Variance ~32% (competitor bankruptcy)
- **Final MAPE**: 15-18%

### Test Scenario 3: Low Demand
```python
# Same code, but use 'scenarios/low_demand/' folder
```

**Expected Result**:
- Week 5: Variance ~28% (supply chain disruption)
- **Final MAPE**: 15-18%

---

## Validation

Run validation checks:
```bash
python generate_mock_data.py --validate
```

**Expected Output**: ✅ All 6 validation types passed

---

## Regenerate Fresh Data

To test robustness with different data variations:
```bash
python generate_mock_data.py --regenerate --validate
```

This uses a time-based seed instead of fixed seed (42).

---

## Categories

| Category | Price | Seasonality | CAGR (2022-2024) |
|----------|-------|-------------|------------------|
| Women's Dresses | $55 ± $5.50 | Peak Spring/Summer | 8% |
| Men's Shirts | $35 ± $3.50 | Steady year-round | 3% |
| Accessories | $25 ± $2.50 | Peak Nov-Dec | 5% |

---

## Store Clusters (K-means, K=3)

| Cluster | Size | Description | Example Stores |
|---------|------|-------------|----------------|
| Fashion_Forward | ~15 | Large, wealthy, high traffic | S001, S005, S012 |
| Mainstream | ~20 | Medium stores, average income | S015, S023, S034 |
| Value_Conscious | ~15 | Small, lower income | S042, S048, S050 |

---

## Need Help?

- **Data Dictionary**: See Section 3 of `data_specification_v3.2.md`
- **Generation Logic**: See Section 4 of `data_specification_v3.2.md`
- **Validation Rules**: See Section 5 of `data_specification_v3.2.md`

---

**Document Version**: v3.2
**Last Updated**: 2025-10-14
**Status**: Ready for Implementation ✅
```

---

## 9. Summary Checklist for *agent dev

Use this checklist when implementing `generate_mock_data.py`:

### Core Requirements
- [ ] Pure Python (numpy + pandas only, no extra dependencies)
- [ ] Fixed seed (42) by default, `--regenerate` flag for fresh data
- [ ] Scenario-based folder structure (`training/` and `scenarios/`)
- [ ] 38 total CSV files (1 historical + 1 store attributes + 36 weekly actuals)

### Data Generation Logic
- [ ] 3 categories with different seasonal patterns (see Section 4.2)
- [ ] Store attributes correlate with sales (formula in Section 3.2)
- [ ] Variable pricing (base ± 10% noise)
- [ ] Historical data cleaner (±10-15%), actuals messier (±20-25%)
- [ ] Black swan event in Week 5 for all scenarios (see Section 4.4)
- [ ] 6 realism strategies to achieve MAPE 12-18% (see Section 4.5)

### Validation Suite
- [ ] Implement all 6 validation types (see Section 5.1)
- [ ] Output validation report (see Section 5.2)
- [ ] Check MAPE target: reject if <10% or >20%

### Documentation
- [ ] Inline comments in Python script
- [ ] README.md in `data/mock/` folder (see Section 8)
- [ ] Data dictionary clearly documented (see Section 3)

### Testing
- [ ] Generate all 38 files successfully
- [ ] Pass all 6 validation checks
- [ ] Confirm 3 scenarios produce different patterns
- [ ] Verify Week 5 variance >20% in all scenarios

---

## 10. References

**Related Documents** (all v3.2, aligned):
- `product_brief/product_brief_v3.2.md` - System overview
- `product_brief/operational_workflow_v3.2.md` - Agent behavior examples
- `architecture/technical_architecture_v3.2.md` - ML approach, API contracts
- `design/front-end-spec_v3.2.md` - UI/UX, weekly actuals upload workflow

**Key Sections**:
- Frontend Spec Section 12: Data Requirements (original requirements, now superseded by this doc)
- Technical Architecture Section 9: ML Approach (Prophet+ARIMA, K-means)
- Technical Architecture Section 11: API Contracts (data models)

---

**Document Owner**: Independent Study Project
**Status**: Ready for Implementation ✅
**Next Step**: Run `*agent dev` to implement `generate_mock_data.py`

---

**End of Data Specification v3.2**
