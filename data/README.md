This README helps you navigate the data folder.

# Data for Agentic Retail Forecasting System

**Purpose**: Synthetic retail sales data for testing 6-agent demand forecasting and inventory optimization system.

**Version**: v4.0
**Last Updated**: 2025-12-04
**Status**: Production Ready

---

## Folder Structure

```
data/
├── training/                              # Historical data for model training
│   ├── historical_sales_2022_2024.csv     (164,400 rows, 6.5 MB)
│   ├── store_attributes.csv               (50 stores, 12 features)
│   ├── realistic_stores_dataset1.csv      (alternate store data)
│   └── realistic_stores_dataset2.csv      (alternate store data)
├── scenarios/                             # Test scenarios with weekly actuals
│   ├── normal_season/                     (12 weekly files)
│   ├── high_demand/                       (12 weekly files)
│   ├── low_demand/                        (12 weekly files)
│   ├── underperform/                      (12 weekly files)
│   └── severe_underperform/               (12 weekly files)
├── generate_mock_data.py                  # Main data generation script
├── generate_underperform.py               # Underperform scenario generator
└── README.md                              # This file
```

**Total Files**: 64 CSV files (4 training + 60 scenario)

---

## Quick Start

### Load Data (Python)

```python
import pandas as pd

# Training data
historical = pd.read_csv('data/training/historical_sales_2022_2024.csv')
stores = pd.read_csv('data/training/store_attributes.csv')

# Scenario actuals (e.g., normal season, week 1)
actuals = pd.read_csv('data/scenarios/normal_season/actuals_week_01.csv')
```

### Regenerate Data

```bash
cd data
python generate_mock_data.py --validate
python generate_underperform.py
```

---

## Data Dictionary

### historical_sales_2022_2024.csv

Training data for demand forecasting models (2022-01-01 to 2024-12-31).

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| `date` | DATE | Sales date (YYYY-MM-DD) | `2022-01-01` |
| `store_id` | STRING | Store identifier (S001-S050) | `S023` |
| `category` | STRING | Product category | `Women's Dresses` |
| `quantity_sold` | INT | Units sold on that date | `47` |
| `revenue` | FLOAT | Total revenue (quantity × price) | `2585.50` |

**Statistics**:
- **Rows**: 164,400 (1,096 days × 50 stores × 3 categories)
- **Date Range**: 2022-01-01 to 2024-12-31
- **Categories**: Women's Dresses, Men's Shirts, Accessories

---

### store_attributes.csv

Store features for K-means clustering (K=3) to create store segments.

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| `store_id` | STRING | Store identifier | `S001` |
| `avg_weekly_sales_12mo` | INT | Average weekly sales (12 month) | `924` |
| `store_size_sqft` | INT | Store size in square feet | `12500` |
| `median_income` | INT | Area median household income | `142000` |
| `location_tier` | STRING | Location quality tier | `A`, `B`, `C` |
| `fashion_tier` | STRING | Fashion positioning | `Premium`, `Mainstream`, `Value` |
| `store_format` | STRING | Store format type | `Mall`, `Strip`, `Standalone` |
| `region` | STRING | Geographic region | `Southeast`, `West`, `Midwest` |
| `foot_traffic` | INT | Average daily foot traffic | `2800` |
| `competitor_density` | FLOAT | Competitors within 5 miles | `6.2` |
| `online_penetration` | FLOAT | % of local online shoppers | `0.48` |
| `population_density` | INT | People per square mile | `14500` |
| `mall_location` | BOOL | Is store in shopping mall? | `True` |

**Statistics**:
- **Rows**: 50 (one per store)
- **Clustering Features**: 7 numeric columns used for K-means

**Expected Clusters**:
- **Premium/Fashion_Forward** (~15 stores): Large, wealthy areas, high traffic
- **Mainstream** (~20 stores): Medium size, average income
- **Value** (~15 stores): Smaller stores, lower income areas

---

### actuals_week_XX.csv

Weekly actual sales data for testing (Spring 2025 season, 12 weeks per scenario).

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| `date` | DATE | Sales date (YYYY-MM-DD) | `2025-02-17` |
| `store_id` | STRING | Store identifier | `S001` |
| `quantity_sold` | INT | Units sold on that date | `38` |

**Statistics**:
- **Rows per file**: ~350 (50 stores × 7 days)
- **Date Range**: 2025-02-17 to 2025-05-11 (12 weeks)

---

## Test Scenarios

The system is tested against 5 scenarios to validate agent behavior:

| Scenario | Path | Description | Week 5 Variance |
|----------|------|-------------|-----------------|
| **Normal Season** | `normal_season/` | Expected Spring 2025 patterns | ~32% |
| **High Demand** | `high_demand/` | Consumer confidence surge, +25% | ~37% |
| **Low Demand** | `low_demand/` | Economic uncertainty, -20% | ~24% |
| **Underperform** | `underperform/` | Moderate underperformance | ~20% |
| **Severe Underperform** | `severe_underperform/` | Major underperformance | ~35% |

### Scenario Details

#### Normal Season
- 8% → 2% growth slowdown (economic headwinds)
- Week 5: Viral TikTok trend (+30% Women's Dresses)
- Expected MAPE: 12-15%

#### High Demand
- Consumer confidence surge → +25% all categories
- Week 5: Major competitor bankruptcy (+40% traffic)
- Expected MAPE: 15-18%

#### Low Demand
- Economic uncertainty → -20% discretionary spending
- Week 5: Supply chain disruption (-25% stockouts)
- Expected MAPE: 15-18%

#### Underperform
- Steady decline below forecast
- Tests Variance Agent threshold detection
- Triggers moderate reforecast adjustments

#### Severe Underperform
- Significant deviation from forecast
- Tests aggressive reallocation decisions
- Triggers Pricing Agent markdown recommendations

---

## Agent Data Usage

### Pre-Season Workflow

| Agent | Data Used | Purpose |
|-------|-----------|---------|
| **Demand Agent** | `historical_sales_2022_2024.csv` | Train forecasting model, generate 12-week demand forecast |
| **Inventory Agent** | `store_attributes.csv` | K-means clustering, initial allocation across 50 stores |

### In-Season Workflow

| Agent | Data Used | Purpose |
|-------|-----------|---------|
| **Variance Agent** | `actuals_week_XX.csv` + forecast | Detect significant deviations, decide if reforecast needed |
| **Reforecast Agent** | Historical + actuals | Bayesian update to remaining weeks forecast |
| **Reallocation Agent** | Store attributes + current inventory | Recommend inter-store transfers |
| **Pricing Agent** | Inventory levels + weeks remaining | Recommend markdowns when needed |

---

## Generation Scripts

### generate_mock_data.py

Main data generation script for training data and scenario actuals.

```bash
python generate_mock_data.py --validate    # Generate with validation
python generate_mock_data.py --regenerate  # Regenerate with new seed
```

**Features**:
- Generates 164,400 rows of historical sales data
- Creates 50 stores with realistic attributes
- Produces 3 base scenarios (normal, high_demand, low_demand)
- Applies seasonality, trends, and noise

### generate_underperform.py

Generates underperformance scenarios for testing agent responses.

```bash
python generate_underperform.py
```

**Features**:
- Creates `underperform/` and `severe_underperform/` scenarios
- Applies progressive decline patterns
- Tests markdown and reallocation triggers

---

## Usage Examples

### Example 1: Load and Explore Training Data

```python
import pandas as pd

# Load data
historical = pd.read_csv('data/training/historical_sales_2022_2024.csv')
stores = pd.read_csv('data/training/store_attributes.csv')

# Quick stats
print(f"Historical: {len(historical):,} rows, {historical['store_id'].nunique()} stores")
print(f"Date range: {historical['date'].min()} to {historical['date'].max()}")
print(f"Categories: {historical['category'].unique().tolist()}")
print(f"\nStores: {len(stores)} with {len(stores.columns)} features")
```

### Example 2: Process Weekly Actuals

```python
import glob

# Load all weeks for a scenario
scenario = 'normal_season'
files = sorted(glob.glob(f'data/scenarios/{scenario}/actuals_week_*.csv'))

for week_num, file in enumerate(files, 1):
    actuals = pd.read_csv(file)
    total_units = actuals['quantity_sold'].sum()
    print(f"Week {week_num:2d}: {total_units:,} units across {actuals['store_id'].nunique()} stores")
```

### Example 3: K-Means Clustering

```python
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

# Load store attributes
stores = pd.read_csv('data/training/store_attributes.csv')

# Select clustering features
features = ['avg_weekly_sales_12mo', 'store_size_sqft', 'median_income',
            'foot_traffic', 'competitor_density', 'online_penetration', 'population_density']
X = stores[features].values

# Cluster
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)
kmeans = KMeans(n_clusters=3, random_state=42)
stores['cluster'] = kmeans.fit_predict(X_scaled)

# Summarize
print(stores.groupby('cluster')[features].mean().round(0))
```

---

## Data Quality

### Validation Checks

| Check | Status |
|-------|--------|
| No missing values | ✓ |
| No negative quantities | ✓ |
| Valid date formats | ✓ |
| All 50 stores present | ✓ |
| 7 days per week in actuals | ✓ |
| Revenue = quantity × price (approx) | ✓ |

### Key Metrics

- Week 5 variance >20% in all scenarios ✓
- Historical data shows clear seasonality ✓
- Store clusters distinguishable (silhouette >0.4) ✓
- Target MAPE 12-18% achievable ✓

---

## Related Documentation

- `docs/04_MVP_Development/planning/6_data_specification_v4.0.md` - Detailed data specification
- `docs/04_MVP_Development/planning/3_technical_architecture_v4.0.md` - System architecture
- `docs/04_MVP_Development/planning/2_process_workflow_v4.0.md` - Operational workflow

---

**Document Version**: v4.0
**Last Updated**: 2025-12-04
