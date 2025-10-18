# Mock Data for Fashion Retail PoC

**Purpose**: Synthetic retail sales data for testing 3-agent demand forecasting system.

**Generated**: 2025-10-17
**Version**: v3.2
**Status**: Ready for Use

---

## Quick Start

### Generate Data
```bash
cd data/mock
python generate_mock_data.py --validate
```

**Expected Output**: 38 CSV files with 6/6 validations passing

### Load Data (Python)
```python
import pandas as pd

# Training data (for model training)
historical = pd.read_csv('data/mock/training/historical_sales_2022_2024.csv')
stores = pd.read_csv('data/mock/training/store_attributes.csv')

# Testing data - Scenario 1 (Normal Season)
actuals_w1 = pd.read_csv('data/mock/scenarios/normal_season/actuals_week_01.csv')
```

---

## File Structure

```
data/mock/
├── training/
│   ├── historical_sales_2022_2024.csv   (164,400 rows, 6.5 MB)
│   └── store_attributes.csv             (50 rows, 12 KB)
├── scenarios/
│   ├── normal_season/                   (12 weekly files)
│   ├── high_demand/                     (12 weekly files)
│   └── low_demand/                      (12 weekly files)
├── generate_mock_data.py                (generation script)
└── README.md                            (this file)
```

**Total Files**: 38 CSV files
**Total Size**: ~8 MB

---

### store_attributes.csv

Features for K-means clustering (K=3) to create store segments.

| Column | Type | Description | Range |
|--------|------|-------------|-------|
| `store_id` | STRING | Store identifier | `S001`-`S050` |
| `size_sqft` | INT | Store size in square feet | 3,000-15,000 |
| `income_level` | INT | Area median household income | $35K-$150K |
| `foot_traffic` | INT | Average daily foot traffic | 300-3,000 |
| `competitor_density` | FLOAT | # of competitors within 5 miles | 0.5-8.0 |
| `online_penetration` | FLOAT | % of local customers shopping online | 0.15-0.60 |
| `population_density` | INT | People per square mile | 500-15,000 |
| `mall_location` | BOOL | Is store in shopping mall? | true/false |

**Rows**: 50 (one per store)
**Silhouette Score**: 0.521 (validates 3 distinct clusters)

**Expected Clusters** (K-means discovers these):
- **Fashion_Forward** (~15 stores): Large, wealthy areas, high traffic
- **Mainstream** (~20 stores): Medium size, average income
- **Value_Conscious** (~15 stores): Small stores, lower income areas

---

### actuals_week_XX.csv

Testing data for weekly variance calculation (Spring 2025 season, 12 weeks).

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| `date` | DATE | Sales date (YYYY-MM-DD) | `2025-02-17` |
| `store_id` | STRING | Store identifier | `S023` |
| `quantity_sold` | INT | Units sold on that date | `52` |

**Rows**: 350 per file (50 stores × 7 days)
**Date Range**: 2025-02-17 (Mon) to 2025-05-11 (Sun) - 12 weeks
**Noise Level**: ±20-25% (messier for realistic testing)

**Note**: Category is auto-detected from aggregated sales patterns (Women's Dresses for Spring 2025).

---

## Testing Scenarios

### Scenario 1: Normal Season
**Path**: `scenarios/normal_season/`
**Description**: Expected Spring 2025 with typical patterns

**Characteristics**:
- 8% → 2% growth slowdown (economic headwinds)
- Minor unpredictable events (store renovations in Week 3)
- **Week 5 Black Swan**: Viral TikTok trend (+30% Women's Dresses for 5 days)
- 10 stores deviate from cluster patterns

**Expected Results**:
- Weeks 1-4 Variance: 8-15%
- Week 5 Variance: ~32% (triggers re-forecast)
- Weeks 6-12 Variance: 10-16% (improved after re-forecast)
- **Final MAPE**: 12-15%

---

### Scenario 2: High Demand
**Path**: `scenarios/high_demand/`
**Description**: Unexpectedly strong Spring 2025

**Characteristics**:
- Consumer confidence surge → +25% across all categories
- Fashion_Forward cluster performs exceptionally (+40%)
- **Week 5 Black Swan**: Major competitor bankruptcy (+40% traffic surge)
- Seasonality peak shifts earlier (April vs May)

**Expected Results**:
- Week 5 Variance: ~37%
- **Final MAPE**: 15-18%

---

### Scenario 3: Low Demand
**Path**: `scenarios/low_demand/`
**Description**: Weaker-than-expected Spring 2025

**Characteristics**:
- Economic uncertainty → -20% discretionary spending
- Value_Conscious cluster worst affected (-30%)
- **Week 5 Black Swan**: Supply chain disruption (-25% stockouts)
- Increased online competition (-5% additional erosion)

**Expected Results**:
- Week 5 Variance: ~24%
- **Final MAPE**: 15-18%

---

## Validation Results

All 6 validation types passed:

1. **Completeness**: 38/38 files, 164,400 historical rows, 50 stores, no missing values ✓
2. **Quality**: No negative sales, revenue calculations correct ✓
3. **Format**: Valid dates, store IDs, categories ✓
4. **Statistical**: Category means/stdevs within ranges, K-means silhouette 0.521 ✓
5. **Pattern**: Seasonality detected (Dresses peak Spring/Summer, Accessories peak Q4) ✓
6. **Weekly Actuals**: 7 consecutive days per week, all 50 stores present ✓

**Key Metrics**:
- Week 5 variance >20% in all 3 scenarios ✓
- Historical data shows clear seasonality ✓
- Store clusters distinguishable (silhouette >0.4) ✓
- Target MAPE 12-18% achievable ✓

---

## Usage Examples

### Example 1: Test Full Workflow (Normal Season)

```python
import pandas as pd
import glob

# Load training data
historical = pd.read_csv('data/mock/training/historical_sales_2022_2024.csv')
stores = pd.read_csv('data/mock/training/store_attributes.csv')

# Train models (your implementation)
# forecast_model.train(historical)
# clustering_model.fit(stores)

# Test with Normal Season scenario
actuals_files = sorted(glob.glob('data/mock/scenarios/normal_season/actuals_week_*.csv'))

for week, file in enumerate(actuals_files, start=1):
    actuals = pd.read_csv(file)

    # Calculate variance (your implementation)
    # variance = calculate_variance(forecast[week], actuals)

    # Check if re-forecast needed
    # if variance > 20%:
    #     trigger_reforecast()

    print(f"Week {week}: {len(actuals)} rows, {actuals['quantity_sold'].sum()} total units")
```

**Expected Output**:
```
Week 1: 350 rows, 18,234 total units
Week 2: 350 rows, 19,567 total units
...
Week 5: 350 rows, 26,891 total units  ← Variance spike (TikTok trend)
...
Week 12: 350 rows, 17,432 total units
```

---

### Example 2: Analyze Seasonality Patterns

```python
import pandas as pd
import matplotlib.pyplot as plt

# Load historical data
df = pd.read_csv('data/mock/training/historical_sales_2022_2024.csv')
df['date'] = pd.to_datetime(df['date'])
df['month'] = df['date'].dt.month

# Aggregate by category and month
monthly = df.groupby(['category', 'month'])['quantity_sold'].sum().unstack()

# Plot
monthly.T.plot(figsize=(12, 6), marker='o')
plt.title('Seasonal Patterns by Category (2022-2024)')
plt.xlabel('Month')
plt.ylabel('Total Units Sold')
plt.legend(title='Category')
plt.grid(True)
plt.show()
```

**Expected Patterns**:
- Women's Dresses: Peak Mar-Aug (Spring/Summer)
- Men's Shirts: Flat year-round with Aug bump (Back to School)
- Accessories: Massive Nov-Dec surge (Holiday gifts)

---

### Example 3: Cluster Analysis

```python
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

# Load store attributes
stores = pd.read_csv('data/mock/training/store_attributes.csv')

# Prepare features for clustering
feature_cols = ['size_sqft', 'income_level', 'foot_traffic',
                'competitor_density', 'online_penetration', 'population_density']
X = stores[feature_cols].values

# Standardize and cluster
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)
kmeans = KMeans(n_clusters=3, random_state=42)
stores['cluster'] = kmeans.fit_predict(X_scaled)

# Analyze clusters
cluster_summary = stores.groupby('cluster').agg({
    'size_sqft': 'mean',
    'income_level': 'mean',
    'foot_traffic': 'mean'
})

print(cluster_summary)
```

**Expected Output**:
```
         size_sqft  income_level  foot_traffic
cluster
0          12,450       119,233         2,345  ← Fashion_Forward
1           7,823        78,542         1,298  ← Mainstream
2           4,567        48,932           542  ← Value_Conscious
```

---

## Regenerate Fresh Data

To test system robustness with different data variations:

```bash
python generate_mock_data.py --regenerate --validate
```

This uses a time-based seed instead of fixed seed (42), generating statistically similar but numerically different data.

---

## Troubleshooting

### Issue: MAPE too low (<10%)
**Solution**: Data is too clean. Increase noise levels in `generate_scenario()` or add more unpredictable events.

### Issue: Week 5 variance below 20%
**Solution**: Increase black swan event magnitude in Week 5 (line 420 in script).

### Issue: K-means silhouette score <0.4
**Solution**: Increase separation between cluster attribute ranges (lines 191-226).

### Issue: CSV encoding errors
**Solution**: Ensure all files are UTF-8 encoded. Script automatically handles this.

---

## Next Steps

1. **Load Training Data**: Use historical sales and store attributes to train Prophet+ARIMA models
2. **Test Scenario 1**: Process normal_season weekly actuals, validate variance detection
3. **Validate MAPE**: Confirm forecast accuracy is 12-18% across all scenarios
4. **Test Re-forecast**: Verify Week 5 variance >20% triggers re-forecast workflow
5. **Integration Testing**: Connect to backend API endpoints and frontend dashboard

---

## References

**Related Documentation**:
- `docs/04_MVP_Development/planning/6_data_specification_v3.2.md` - Detailed specification
- `docs/04_MVP_Development/planning/2_process_workflow_v3.3.md` - Agent workflow examples
- `docs/04_MVP_Development/planning/3_technical_architecture_v3.3.md` - ML approach details

**Key Requirements**:
- MAPE Target: 12-18% (realistic forecast accuracy)
- Week 5 Variance: >20% (triggers re-forecast)
- Store Clusters: 3 distinguishable segments (silhouette >0.4)
- Data Quality: 6/6 validation checks passing

---

**Document Version**: v3.2
**Last Updated**: 2025-10-17
**Status**: Phase 1 Complete - Ready for Phase 2 (Frontend) ✓

---

## Need Help?

- **Data Dictionary**: See above sections
- **Generation Logic**: Review `generate_mock_data.py` source code
- **Validation Rules**: Check `validate_all_data()` function
- **Planning Docs**: See `docs/04_MVP_Development/planning/` folder
