# Data Specification v4.0
# Agentic Retail Forecasting System - Data Requirements

**Version:** 4.0
**Date:** 2025-12-04
**Status:** Implemented
**Alignment:** Architecture v4.0, PRD v4.0

---

## Table of Contents

1. [Overview](#1-overview)
2. [Data Architecture](#2-data-architecture)
3. [Data Dictionary](#3-data-dictionary)
4. [Schema Definitions](#4-schema-definitions)
5. [Test Scenarios](#5-test-scenarios)
6. [Data Usage by Agent](#6-data-usage-by-agent)
7. [Validation Requirements](#7-validation-requirements)
8. [Data Loading](#8-data-loading)
9. [Implementation Notes](#9-implementation-notes)

---

## 1. Overview

### 1.1 Purpose

This document specifies the data requirements for the 6-agent retail forecasting system. The data supports:
- **Demand Agent**: Prophet + ARIMA ensemble training
- **Inventory Agent**: K-means store clustering and hierarchical allocation
- **Variance Agent**: Forecast vs actual comparison and reasoning
- **Reforecast Agent**: Bayesian prior/likelihood/posterior calculation
- **Reallocation Agent**: Store performance analysis
- **Pricing Agent**: Sell-through and markdown calculation

### 1.2 Data Summary

| Data Type | File | Records | Purpose |
|-----------|------|---------|---------|
| **Historical Sales** | `training/historical_sales_2022_2024.csv` | 164,400 | Training Prophet + ARIMA |
| **Store Attributes** | `training/store_attributes.csv` | 50 | K-means clustering |
| **Weekly Actuals** | `scenarios/*/actuals_week_XX.csv` | ~350 each | Variance calculation |

### 1.3 Key Characteristics

| Characteristic | Value |
|----------------|-------|
| **Historical Date Range** | 2022-01-01 to 2024-12-31 (3 years) |
| **Test Season** | 2025-02-17 to 2025-05-11 (12 weeks) |
| **Store Count** | 50 stores (S001-S050) |
| **Categories** | 3 (Women's Dresses, Men's Shirts, Accessories) |
| **Clusters** | 3 (Premium/Fashion_Forward, Mainstream, Value) |
| **Scenarios** | 5 (normal, high_demand, low_demand, underperform, severe_underperform) |

---

## 2. Data Architecture

### 2.1 File Structure

```
data/
├── training/
│   ├── historical_sales_2022_2024.csv     # 164,400 rows (6.5 MB)
│   ├── store_attributes.csv               # 50 rows (12 KB)
│   ├── realistic_stores_dataset1.csv      # Alternate store data
│   └── realistic_stores_dataset2.csv      # Alternate store data
├── scenarios/
│   ├── normal_season/
│   │   ├── actuals_week_01.csv            # ~350 rows each
│   │   ├── actuals_week_02.csv
│   │   ├── ...
│   │   └── actuals_week_12.csv
│   ├── high_demand/
│   │   ├── actuals_week_01.csv
│   │   └── ... (12 files)
│   ├── low_demand/
│   │   └── ... (12 files)
│   ├── underperform/                      # NEW in v4.0
│   │   └── ... (12 files)
│   └── severe_underperform/               # NEW in v4.0
│       └── ... (12 files)
├── generate_mock_data.py                   # Data generation script
├── generate_underperform.py                # Underperform scenario generator
└── README.md                               # Usage guide
```

**Total Files**: 64 CSV files
- 2 training files
- 60 weekly actuals (5 scenarios × 12 weeks)
- 2 alternate store datasets

### 2.2 Data Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    TRAINING DATA LOADER                          │
│                                                                  │
│  historical_sales_2022_2024.csv ───→ Prophet + ARIMA Training   │
│  store_attributes.csv ──────────→ K-means Clustering            │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    FORECASTING CONTEXT                           │
│                                                                  │
│  • data_loader: TrainingDataLoader                              │
│  • forecast_by_week: List[int] (from Demand Agent)              │
│  • actual_sales: List[int] (from user upload)                   │
│  • store_actual_sales: Dict[str, List[int]]                     │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      AGENT USAGE                                 │
│                                                                  │
│  Demand Agent ────────→ historical_sales (category-filtered)    │
│  Inventory Agent ─────→ store_attributes (all 50 stores)        │
│  Variance Agent ──────→ forecast + actual_sales                 │
│  Reforecast Agent ────→ forecast + actual_sales                 │
│  Reallocation Agent ──→ store_actual_sales                      │
│  Pricing Agent ───────→ total_sold / total_allocated            │
└─────────────────────────────────────────────────────────────────┘
```

---

## 3. Data Dictionary

### 3.1 Historical Sales (`training/historical_sales_2022_2024.csv`)

**Purpose**: Training data for Prophet + ARIMA ensemble forecasting.

**Record Count**: 164,400 rows
- Calculation: 1,096 days × 50 stores × 3 categories

**Schema**:

| Column | Type | Description | Example | Constraints |
|--------|------|-------------|---------|-------------|
| `date` | DATE | Sales date (YYYY-MM-DD) | `2022-01-01` | 2022-01-01 to 2024-12-31 |
| `store_id` | STRING | Store identifier | `S001` | S001 to S050 |
| `category` | STRING | Product category | `Women's Dresses` | Enum: 3 values |
| `quantity_sold` | INTEGER | Units sold | `54` | ≥ 0 |
| `revenue` | FLOAT | Total revenue ($) | `2701.55` | ≥ 0 |

**Sample Data**:
```csv
date,store_id,category,quantity_sold,revenue
2022-01-01,S001,Women's Dresses,54,2701.55
2022-01-01,S001,Men's Shirts,47,1772.22
2022-01-01,S001,Accessories,46,1038.52
2022-01-01,S002,Women's Dresses,54,2970.62
```

**Category Values**:
- `Women's Dresses`
- `Men's Shirts`
- `Accessories`

**Data Characteristics**:
- Clean patterns (±10-15% noise) for model training
- Seasonal patterns per category
- Holiday spikes (Valentine's, Mother's Day, Black Friday)
- Weekly patterns (weekends higher for Dresses/Accessories)
- Year-over-year growth trends

---

### 3.2 Store Attributes (`training/store_attributes.csv`)

**Purpose**: Features for K-means clustering (K=3) and store-level allocation.

**Record Count**: 50 rows (one per store)

**Schema**:

| Column | Type | Description | Example | Range/Values |
|--------|------|-------------|---------|--------------|
| `store_id` | STRING | Store identifier | `S001` | S001 to S050 |
| `avg_weekly_sales_12mo` | INTEGER | Avg weekly units (trailing 12mo) | `924` | 200 - 1100 |
| `store_size_sqft` | INTEGER | Store size (sq ft) | `12500` | 3,500 - 15,000 |
| `median_income` | INTEGER | Area median income ($) | `142000` | 36,000 - 148,000 |
| `location_tier` | STRING | Location quality | `A` | A, B, C |
| `fashion_tier` | STRING | Fashion positioning | `Premium` | Premium, Mainstream, Value |
| `store_format` | STRING | Store type | `Mall` | Mall, ShoppingCenter, Standalone, Outlet |
| `region` | STRING | Geographic region | `Southeast` | Northeast, Southeast, Midwest, West |
| `foot_traffic` | INTEGER | Daily foot traffic | `2800` | 400 - 3,100 |
| `competitor_density` | FLOAT | Competitors within 5 mi | `6.2` | 1.1 - 6.8 |
| `online_penetration` | FLOAT | Local online shopping % | `0.48` | 0.20 - 0.51 |
| `population_density` | INTEGER | People per sq mi | `14500` | 1,400 - 14,500 |
| `mall_location` | BOOLEAN | Is in shopping mall? | `True` | True, False |

**Sample Data**:
```csv
store_id,avg_weekly_sales_12mo,store_size_sqft,median_income,location_tier,fashion_tier,store_format,region
S001,924,12500,142000,A,Premium,Mall,Southeast
S016,532,8200,78000,B,Mainstream,ShoppingCenter,Northeast
S036,227,4200,42000,C,Value,Standalone,Northeast
```

**Expected Clusters** (K-means discovers these):

| Cluster | Stores | Location Tier | Fashion Tier | Characteristics |
|---------|--------|---------------|--------------|-----------------|
| **Fashion_Forward (Premium)** | S001-S015 (15) | A | Premium | High income, large stores, high traffic |
| **Mainstream** | S016-S035 (20) | B | Mainstream | Medium income, medium stores |
| **Value_Conscious** | S036-S050 (15) | C | Value | Lower income, smaller stores |

**K-means Validation**:
- Expected silhouette score: > 0.45
- Actual silhouette score: ~0.52

---

### 3.3 Weekly Actuals (`scenarios/*/actuals_week_XX.csv`)

**Purpose**: Testing data for variance calculation and in-season monitoring.

**Record Count**: ~350 rows per file (50 stores × 7 days)

**Schema**:

| Column | Type | Description | Example | Constraints |
|--------|------|-------------|---------|-------------|
| `date` | DATE | Sales date (YYYY-MM-DD) | `2025-02-17` | 7 consecutive days |
| `store_id` | STRING | Store identifier | `S001` | S001 to S050 |
| `quantity_sold` | INTEGER | Units sold | `38` | ≥ 0 |

**Sample Data**:
```csv
date,store_id,quantity_sold
2025-02-17,S001,38
2025-02-17,S002,40
2025-02-17,S003,25
```

**Date Ranges by Week**:

| Week | Start Date | End Date |
|------|------------|----------|
| 1 | 2025-02-17 | 2025-02-23 |
| 2 | 2025-02-24 | 2025-03-02 |
| 3 | 2025-03-03 | 2025-03-09 |
| 4 | 2025-03-10 | 2025-03-16 |
| 5 | 2025-03-17 | 2025-03-23 |
| 6 | 2025-03-24 | 2025-03-30 |
| 7 | 2025-03-31 | 2025-04-06 |
| 8 | 2025-04-07 | 2025-04-13 |
| 9 | 2025-04-14 | 2025-04-20 |
| 10 | 2025-04-21 | 2025-04-27 |
| 11 | 2025-04-28 | 2025-05-04 |
| 12 | 2025-05-05 | 2025-05-11 |

**Data Characteristics**:
- Messier patterns (±20-25% noise) than historical
- Scenario-specific disruptions (black swan events)
- Store-level heterogeneity (some stores deviate from cluster patterns)

**Note**: Weekly actuals do NOT include category column. The system aggregates all sales per store per day. Category-level analysis uses historical patterns for distribution.

---

## 4. Schema Definitions

### 4.1 Pydantic Schemas (Agent Output)

The 6 agents produce typed output via Pydantic schemas. See `backend/schemas/` for full definitions.

**Key Schemas**:

```python
# ForecastResult (Demand Agent output)
class ForecastResult(BaseModel):
    total_demand: int
    forecast_by_week: List[int]  # 12 values
    safety_stock_pct: float
    confidence: float
    model_used: str
    seasonality: SeasonalityExplanation
    explanation: str
    lower_bound: List[int]
    upper_bound: List[int]

# AllocationResult (Inventory Agent output)
class AllocationResult(BaseModel):
    manufacturing_qty: int
    dc_holdback: int
    dc_holdback_percentage: float
    initial_store_allocation: int
    cluster_allocations: List[ClusterAllocation]
    store_allocations: List[StoreAllocation]  # 50 stores
    replenishment_strategy: str
    explanation: str
    reasoning_steps: List[str]
    key_factors: List[str]

# VarianceAnalysis (Variance Agent output)
class VarianceAnalysis(BaseModel):
    variance_pct: float
    is_high_variance: bool
    severity: str  # low, moderate, high, critical
    likely_cause: str
    trend_direction: str
    recommended_action: str
    should_reforecast: bool
    reforecast_adjustments: Optional[str]
    confidence: float
    explanation: str

# ReforecastResult (Reforecast Agent output)
class ReforecastResult(BaseModel):
    updated_forecast_by_week: List[int]
    updated_total: int
    adjustment_factor: float
    posterior_confidence: float
    prior_weight: float
    likelihood_weight: float
    explanation: str

# ReallocationAnalysis (Reallocation Agent output)
class ReallocationAnalysis(BaseModel):
    should_reallocate: bool
    strategy: str  # dc_only, hybrid
    dc_units_available: int
    dc_units_to_release: int
    high_performers: List[str]
    underperformers: List[str]
    on_target_stores: List[str]
    transfers: List[TransferOrder]
    expected_sell_through_improvement: float
    stockout_risk_reduction: int
    confidence: float
    explanation: str

# MarkdownResult (Pricing Agent output)
class MarkdownResult(BaseModel):
    recommended_markdown_pct: float  # 0.0 - 0.40
    current_sell_through: float
    target_sell_through: float
    gap: float
    elasticity_used: float
    raw_markdown_pct: float
    week_number: int
    explanation: str
```

---

## 5. Test Scenarios

### 5.1 Scenario Overview

| Scenario | Description | Week 5 Event | Expected MAPE | Markdown? |
|----------|-------------|--------------|---------------|-----------|
| **normal_season** | Typical Spring 2025 | TikTok viral (+30%) | 12-15% | Maybe |
| **high_demand** | Strong demand (+25%) | Competitor bankruptcy (+40%) | 15-18% | No |
| **low_demand** | Weak demand (-20%) | Supply chain disruption (-25%) | 15-18% | Yes |
| **underperform** | Moderate underperformance (-15%) | Gradual decline | 14-17% | Yes |
| **severe_underperform** | Severe underperformance (-30%) | Economic shock | 18-22% | Yes (max) |

### 5.2 Scenario 1: Normal Season

**Description**: Expected Spring 2025 with typical demand patterns.

**Characteristics**:
- Baseline seasonality (similar to 2022-2024)
- Minor unpredictable events (store renovations, local festivals)
- **Week 5 Black Swan**: Viral TikTok trend boosts Women's Dresses +30% for 5 days
- 10 stores deviate from cluster patterns (±15%)

**Expected Variance by Week**:
| Weeks | Variance Range | Variance Agent Decision |
|-------|----------------|------------------------|
| 1-4 | 8-15% | No reforecast |
| 5 | 25-32% | **Reforecast triggered** |
| 6-12 | 10-16% | Continue monitoring |

**Expected Outcomes**:
- MAPE: 12-15%
- Reforecast: Yes (Week 5)
- Markdown: Depends on sell-through

---

### 5.3 Scenario 2: High Demand

**Description**: Unexpectedly strong Spring 2025 season.

**Characteristics**:
- Economic boom → consumer confidence surge
- All categories +25% above baseline
- Fashion_Forward cluster performs +40%
- **Week 5 Black Swan**: Major competitor bankruptcy → traffic surge
- Seasonality peak shifts earlier (April instead of May)

**Expected Variance by Week**:
| Weeks | Variance Range | Variance Agent Decision |
|-------|----------------|------------------------|
| 1-4 | 12-20% | Monitor closely |
| 5 | 35-42% | **Reforecast triggered** |
| 6-12 | 15-22% | Continue monitoring |

**Expected Outcomes**:
- MAPE: 15-18%
- Reforecast: Yes (Week 5)
- Markdown: No (above target sell-through)
- Stockout risk: High for top stores

---

### 5.4 Scenario 3: Low Demand

**Description**: Weaker-than-expected Spring 2025 season.

**Characteristics**:
- Economic uncertainty → reduced discretionary spending
- All categories -20% below baseline
- Value_Conscious cluster performs worst (-30%)
- **Week 5 Black Swan**: Supply chain disruption → stockouts limit sales
- Online competition intensifies (-5% additional erosion)

**Expected Variance by Week**:
| Weeks | Variance Range | Variance Agent Decision |
|-------|----------------|------------------------|
| 1-4 | -10% to -18% | Monitor closely |
| 5 | -25% to -32% | **Reforecast triggered** |
| 6-12 | -12% to -20% | Continue monitoring |

**Expected Outcomes**:
- MAPE: 15-18%
- Reforecast: Yes (Week 5)
- Markdown: Yes (below 60% sell-through)
- Recommended markdown: 10-20%

---

### 5.5 Scenario 4: Underperform (NEW in v4.0)

**Description**: Moderate underperformance with gradual decline.

**Characteristics**:
- Steady -15% below forecast across all weeks
- No dramatic black swan event
- Gradual erosion of consumer confidence
- Value_Conscious cluster most affected

**Expected Variance by Week**:
| Weeks | Variance Range | Variance Agent Decision |
|-------|----------------|------------------------|
| 1-3 | -12% to -16% | Monitor |
| 4-6 | -14% to -18% | **Reforecast (Week 4 or 5)** |
| 7-12 | -12% to -16% | Continue |

**Expected Outcomes**:
- MAPE: 14-17%
- Reforecast: Yes (Week 4-5)
- Markdown: Yes (10-15%)
- Variance Agent reasoning: "Consistent negative trend suggests systematic overforecast"

---

### 5.6 Scenario 5: Severe Underperform (NEW in v4.0)

**Description**: Severe underperformance requiring aggressive intervention.

**Characteristics**:
- Dramatic -30% below forecast
- Economic shock in Week 2-3
- All clusters affected significantly
- Requires early markdown consideration

**Expected Variance by Week**:
| Weeks | Variance Range | Variance Agent Decision |
|-------|----------------|------------------------|
| 1 | -20% to -25% | Alert |
| 2-3 | -28% to -35% | **Reforecast triggered (Week 2)** |
| 4-6 | -25% to -30% | Continue monitoring |
| 7-12 | -20% to -28% | Aggressive markdown |

**Expected Outcomes**:
- MAPE: 18-22%
- Reforecast: Yes (Week 2-3)
- Markdown: Yes (30-40% - maximum)
- Variance Agent reasoning: "Critical variance with accelerating negative trend requires immediate intervention"

---

## 6. Data Usage by Agent

### 6.1 Demand Agent

**Data Used**:
- `historical_sales_2022_2024.csv` (filtered by category)

**Query Pattern**:
```python
# TrainingDataLoader.get_historical_sales(category)
df = pd.read_csv('training/historical_sales_2022_2024.csv')
category_data = df[df['category'] == category]
daily_totals = category_data.groupby('date')['quantity_sold'].sum()
```

**Tool**: `run_demand_forecast`
- Trains Prophet on aggregated daily sales
- Trains ARIMA on same data
- Ensemble weighting based on validation MAPE

---

### 6.2 Inventory Agent

**Data Used**:
- `store_attributes.csv` (all 50 stores)
- `ForecastResult` from Demand Agent

**Query Pattern**:
```python
# TrainingDataLoader.get_store_attributes()
stores = pd.read_csv('training/store_attributes.csv')

# K-means clustering features (7 features for clustering)
clustering_features = [
    'avg_weekly_sales_12mo',
    'store_size_sqft',
    'median_income',
    'foot_traffic',
    'competitor_density',
    'online_penetration',
    'population_density'
]
```

**Tools**:
- `cluster_stores`: K-means on 7 features
- `allocate_inventory`: 3-layer hierarchical allocation

---

### 6.3 Variance Agent

**Data Used**:
- `forecast_by_week` (from context, original or reforecast)
- `actual_sales` (aggregated from uploaded weekly actuals)

**Input Calculation**:
```python
# Aggregate weekly actuals to category-level
weekly_df = pd.read_csv(f'scenarios/{scenario}/actuals_week_{week:02d}.csv')
weekly_total = weekly_df['quantity_sold'].sum()

# Calculate variance
variance = (actual - forecast) / forecast
```

**Tool**: `analyze_variance_data`
- Calculates MAPE and directional variance
- Identifies trend (comparing multiple weeks)
- Reasons about cause and impact

---

### 6.4 Reforecast Agent

**Data Used**:
- `original_forecast_by_week` (prior)
- `actual_sales` (likelihood)

**Bayesian Calculation**:
```python
# Prior: Original forecast
prior_mean = original_forecast_by_week
prior_variance = historical_mape * prior_mean

# Likelihood: Observed actuals
likelihood_mean = mean(actual_sales)
likelihood_variance = variance(actual_sales)

# Posterior: Conjugate Gaussian update
posterior_mean = (prior_var * likelihood_mean + likelihood_var * prior_mean) / (prior_var + likelihood_var)
```

**Tool**: `bayesian_reforecast`

---

### 6.5 Reallocation Agent

**Data Used**:
- `store_allocations` (from AllocationResult)
- `store_actual_sales` (Dict[store_id, List[weekly_sales]])

**Query Pattern**:
```python
# Calculate velocity per store
for store_id, weekly_sales in store_actual_sales.items():
    velocity = sum(weekly_sales) / len(weekly_sales)
    sell_through = sum(weekly_sales) / allocation[store_id]
```

**Tools**:
- `analyze_store_performance`: Velocity, sell-through, stockout risk
- `generate_transfer_recommendations`: DC releases + store-to-store

---

### 6.6 Pricing Agent

**Data Used**:
- `total_sold` (cumulative actual sales)
- `total_allocated` (initial store allocation)
- Configuration: `target_sell_through`, `elasticity`

**Calculation**:
```python
sell_through = total_sold / total_allocated
gap = target_sell_through - sell_through
raw_markdown = gap * elasticity
final_markdown = round_to_5%(raw_markdown), cap at 40%
```

**Tool**: `calculate_markdown`

---

## 7. Validation Requirements

### 7.1 Validation Checklist

#### Type 1: Completeness
- [ ] Historical CSV has 164,400 rows
- [ ] Store attributes CSV has 50 rows
- [ ] Each weekly actuals CSV has ~350 rows
- [ ] No missing values in required columns
- [ ] All 50 stores present in every file

#### Type 2: Data Quality
- [ ] `quantity_sold` ≥ 0
- [ ] `revenue` ≥ 0
- [ ] `date` is valid YYYY-MM-DD format
- [ ] `store_id` matches S001-S050 pattern
- [ ] `category` is one of 3 valid values

#### Type 3: Format
- [ ] CSV delimiter: comma
- [ ] Date format: YYYY-MM-DD
- [ ] Encoding: UTF-8
- [ ] No extra whitespace
- [ ] Headers match schema

#### Type 4: Statistical
- [ ] Mean weekly sales: 400-800 units (category-level)
- [ ] Store attributes support 3-cluster K-means
- [ ] Silhouette score > 0.45

#### Type 5: Pattern
- [ ] Historical shows clear seasonality
- [ ] Women's Dresses peak Spring/Summer
- [ ] Accessories peak Nov-Dec
- [ ] Weekly actuals have higher variance than historical

#### Type 6: Scenario Validation
- [ ] Each scenario has 12 weekly files
- [ ] Date ranges are consecutive (Mon-Sun)
- [ ] Week 5 shows expected disruption pattern
- [ ] Scenarios produce different variance profiles

---

### 7.2 Validation Script Output

```bash
python generate_mock_data.py --validate

=== Data Validation Report ===

✅ Completeness: PASS
   - Historical: 164,400 rows
   - Store attributes: 50 rows
   - Scenarios: 5 × 12 = 60 weekly files

✅ Data Quality: PASS
   - No negative quantities
   - All dates valid
   - All store IDs valid

✅ Format: PASS
   - UTF-8 encoding
   - Correct headers

✅ Statistical: PASS
   - Mean sales within expected range
   - K-means silhouette: 0.521

✅ Pattern: PASS
   - Seasonality detected
   - Category peaks correct

✅ Scenario Validation: PASS
   - All 5 scenarios complete
   - Date ranges consecutive

=== Summary ===
All 6 validation types: PASS
```

---

## 8. Data Loading

### 8.1 TrainingDataLoader

```python
# backend/utils/data_loader.py

class TrainingDataLoader:
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self._historical_df = None
        self._store_df = None

    def get_historical_sales(self, category: str) -> pd.DataFrame:
        """Load and cache historical sales for a category"""
        if self._historical_df is None:
            self._historical_df = pd.read_csv(
                self.data_dir / "training" / "historical_sales_2022_2024.csv",
                parse_dates=['date']
            )
        return self._historical_df[self._historical_df['category'] == category]

    def get_store_attributes(self) -> pd.DataFrame:
        """Load and cache store attributes"""
        if self._store_df is None:
            self._store_df = pd.read_csv(
                self.data_dir / "training" / "store_attributes.csv"
            )
        return self._store_df

    def get_weekly_actuals(self, scenario: str, week: int) -> pd.DataFrame:
        """Load weekly actuals for a scenario"""
        file_path = self.data_dir / "scenarios" / scenario / f"actuals_week_{week:02d}.csv"
        return pd.read_csv(file_path, parse_dates=['date'])

    def aggregate_weekly_total(self, scenario: str, week: int) -> int:
        """Get category-level total for a week"""
        df = self.get_weekly_actuals(scenario, week)
        return df['quantity_sold'].sum()
```

### 8.2 ForecastingContext Integration

```python
# backend/utils/context.py

@dataclass
class ForecastingContext:
    data_loader: TrainingDataLoader
    session_id: str

    # Season configuration
    season_start_date: Optional[date] = None
    current_week: int = 0
    category: str = "Women's Dresses"

    # Forecast state
    forecast_by_week: List[int] = field(default_factory=list)
    original_forecast: Optional[ForecastResult] = None

    # Actual sales (populated from uploads)
    actual_sales: Optional[List[int]] = None
    store_actual_sales: Dict[str, List[int]] = field(default_factory=dict)

    # Allocation state
    manufacturing_qty: int = 0
    dc_holdback: int = 0
    allocation_result: Optional[AllocationResult] = None

    # Pricing state
    total_allocated: int = 0
    total_sold: int = 0
```

---

## 9. Implementation Notes

### 9.1 Category Detection

The system auto-detects category from historical sales CSV:

```python
# Auto-detect categories
categories = df['category'].unique()
# Returns: ['Women's Dresses', 'Men's Shirts', 'Accessories']
```

### 9.2 Weekly Actuals Aggregation

Weekly actuals don't include category column. Aggregation is per-store:

```python
# Load weekly actuals
weekly_df = pd.read_csv('scenarios/normal_season/actuals_week_01.csv')

# Aggregate by store (daily → weekly)
store_weekly = weekly_df.groupby('store_id')['quantity_sold'].sum()

# Aggregate to category-level (all stores)
category_total = weekly_df['quantity_sold'].sum()
```

### 9.3 K-means Clustering Features

The 7 features used for K-means (order matters for reproducibility):

```python
CLUSTERING_FEATURES = [
    'avg_weekly_sales_12mo',  # Most important - directly correlates to sales
    'store_size_sqft',
    'median_income',
    'foot_traffic',
    'competitor_density',
    'online_penetration',
    'population_density'
]

# Note: location_tier, fashion_tier, store_format, region, mall_location
# are NOT used for clustering but ARE used for reasoning/display
```

### 9.4 Seasonality Alignment

The `season_start_date` parameter aligns forecast seasonality to calendar events:

```python
# If season_start_date = 2025-03-01 (March 1)
# Week 5 falls in late March / early April
# Prophet's seasonal component is adjusted to match

seasonality_insights = {
    'peak_weeks': [5, 6],  # Late March / early April
    'insight': 'Peak demand expected weeks 5-6 (back-to-school preparation)'
}
```

### 9.5 Variance Calculation

Variance is calculated at category level, not store level:

```python
# Category-level variance
variance_pct = (actual_total - forecast_total) / forecast_total

# Store-level variance (for reallocation)
for store_id in stores:
    store_variance = (actual[store_id] - allocated[store_id]) / allocated[store_id]
```

---

## Summary of Changes from v3.2

| Aspect | v3.2 | v4.0 |
|--------|------|------|
| **Historical Rows** | 54,750 | 164,400 |
| **Store Attributes** | 7 columns | 12 columns |
| **Scenarios** | 3 | 5 (+ underperform, severe_underperform) |
| **Agents** | 3 | 6 |
| **Weekly Actuals Schema** | Included category | No category column |
| **Clustering Features** | 7 | 7 (same, but more attributes available) |

---

## Related Documents

- [Architecture v4.0](architecture-v4.0.md) - Technical architecture
- [PRD v4.0](4_prd_v4.0.md) - Product requirements
- [Process Workflow v4.0](2_process_workflow_v4.0.md) - Operational workflow

---

**Document Owner:** Independent Study Project
**Last Updated:** 2025-12-04
**Version:** 4.0
**Status:** Implemented

---

*Document generated by BMad Master v4.0*
