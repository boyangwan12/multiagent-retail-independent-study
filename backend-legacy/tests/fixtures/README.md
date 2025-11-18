# Test Fixtures

This directory contains test data files used for integration and manual testing.

## CSV Files

### `test_historical_sales.csv`
Historical sales data for testing demand forecasting.

**Columns:**
- `date`: Sale date (YYYY-MM-DD)
- `category`: Product category
- `store_id`: Store identifier
- `quantity_sold`: Units sold
- `revenue`: Total revenue

**Usage:**
- Manual testing of data upload endpoints
- Integration tests for historical data processing
- Seed data for forecast model validation

### `test_store_attributes.csv`
Store attribute data for testing store clustering and allocation.

**Columns:**
- `store_id`: Store identifier
- `store_name`: Store name
- `avg_weekly_sales_12mo`: Average weekly sales (12-month)
- `store_size_sqft`: Store size in square feet
- `median_income`: Area median income
- `location_tier`: Location tier (A, B, C)
- `fashion_tier`: Fashion tier (Premium, Mainstream, Value)
- `store_format`: Store format (MALL, SHOPPING_CENTER, etc.)
- `region`: Geographic region

**Usage:**
- Manual testing of store data endpoints
- Integration tests for clustering algorithms
- Seed data for allocation logic validation

### `test_week1_actuals.csv`
Weekly actual sales data for testing re-forecast workflows.

**Columns:**
- `date`: Week date
- `store_id`: Store identifier
- `quantity_sold`: Actual units sold

**Usage:**
- Manual testing of actuals upload endpoint
- Integration tests for variance calculation
- Re-forecast workflow validation

## Loading Test Data

### Via API (Manual Testing)

```bash
# Upload historical sales
curl -X POST http://localhost:8000/api/v1/data/upload/historical \
  -F "file=@tests/fixtures/test_historical_sales.csv" \
  -F "category_id=womens_dresses"

# Upload store attributes
curl -X POST http://localhost:8000/api/v1/data/upload/stores \
  -F "file=@tests/fixtures/test_store_attributes.csv"

# Upload week 1 actuals
curl -X POST http://localhost:8000/api/v1/data/upload/actuals \
  -F "file=@tests/fixtures/test_week1_actuals.csv" \
  -F "forecast_id=f_test_123"
```

### Via Integration Tests

Integration tests automatically use these fixtures when testing data upload endpoints. See `tests/integration/test_uploads.py` for examples.

## Maintenance

- Keep test data files small (<100 rows) for fast test execution
- Update fixtures when schema changes
- Document any new test data files in this README
