# Phase 7 Testing Guide

## Overview

Phase 7 implementation includes comprehensive tests for the Inventory Agent with K-means clustering and hierarchical allocation logic. This guide explains how to run the tests using your actual OpenAI API credentials **without writing them to code or files**.

## Security: Credentials from Environment Variables

**Important Security Practice:**
- API credentials are **NEVER** written to code, configuration files, or version control
- Credentials are passed via **environment variables only**
- The test runners will verify the credential is set but will **NOT display it**

## Running Tests

### Quick Start

```bash
# Set your API key in the environment (do not commit this to version control)
export OPENAI_API_KEY="your-actual-openai-api-key-here"

# Run Phase 7 tests (Python - cross-platform)
python backend/tests/run_phase7_tests.py

# Or run tests with bash (Unix/Linux/MacOS)
bash backend/tests/run_tests.sh
```

### What Gets Tested

#### PHASE7-001: K-means Store Clustering
- ✓ StoreClusterer class initialization (K=3)
- ✓ StandardScaler normalization (mean=0, std=1)
- ✓ K-means++ clustering training
- ✓ Silhouette score validation (target: >0.4)
- ✓ Cluster labeling (Fashion_Forward, Mainstream, Value_Conscious)
- ✓ Cluster statistics (sizes, percentages)
- ✓ 50 stores × 7 features test data

#### PHASE7-002: Inventory Allocation Logic
- ✓ Manufacturing calculation (demand × safety_stock)
- ✓ DC holdback split (parameter-driven: 0% or 45%)
- ✓ 3-layer hierarchical allocation:
  - Layer 1: Manufacturing split (DC + stores)
  - Layer 2: Cluster allocation (based on K-means)
  - Layer 3: Store allocation (hybrid 70/30 factor)
- ✓ Unit conservation validation
- ✓ 2-week minimum inventory enforcement
- ✓ Standard retail scenario (45% holdback)

#### PHASE7-003: Replenishment Scheduling
- ✓ Replenishment calculation formula
- ✓ Parameter-driven logic:
  - Skip if strategy="none" (Zara scenario)
  - Enable if strategy="weekly" (standard retail)
- ✓ DC availability checking
- ✓ Insufficient inventory warnings

## Test Execution Flow

### Python Test Runner (`run_phase7_tests.py`)

```
1. Verify OPENAI_API_KEY environment variable is set
   └─ If not set: Display instructions and exit
   └─ If set: Continue (do not display key)

2. Test PHASE7-001: K-means Clustering
   ├─ Create 50 stores (3 natural clusters)
   ├─ Fit K-means clustering
   ├─ Validate silhouette score > 0.4
   ├─ Verify cluster labels
   └─ Verify allocation percentages sum to 100%

3. Test PHASE7-002 & 003: Allocation & Replenishment
   ├─ Standard retail scenario (45% holdback, weekly replenishment)
   │  ├─ Calculate manufacturing qty
   │  ├─ Verify DC holdback (45%)
   │  ├─ Verify initial allocation (55%)
   │  └─ Verify replenishment enabled
   │
   └─ Fast fashion scenario (0% holdback, no replenishment)
      ├─ Verify DC holdback (0%)
      ├─ Verify initial allocation (100%)
      └─ Verify replenishment disabled

4. Display summary and next steps
```

### Bash Test Runner (`run_tests.sh`)

Similar flow, also displays:
- Project structure verification
- Dependency installation
- Pytest invocation for unit tests

## Test Data

All tests use realistic synthetic data:

**Store Attributes (7 features):**
1. `avg_weekly_sales_12mo` - 12-month average weekly sales
2. `store_size_sqft` - Store square footage
3. `median_income` - Median income of surrounding area
4. `location_tier` - Location tier (A/B/C)
5. `fashion_tier` - Fashion positioning (Premium/Mainstream/Value)
6. `store_format` - Store format (Mall/Standalone/Outlet)
7. `region` - Geographic region (Northeast/Southeast/Midwest/West)

**Store Distribution (50 total):**
- 18 Fashion_Forward (high sales, premium positioning)
- 20 Mainstream (medium sales, standard positioning)
- 12 Value_Conscious (low sales, outlet format)

**Forecast Data (12-week horizon):**
- Total demand: 8,000 units
- Weekly forecasts: [650, 680, 720, 740, 760, 730, 710, 680, 650, 620, 580, 480]
- Safety stock: 20%
- Confidence: 0.85

## Environment Variable Management

### Setting the API Key

**Option 1: Temporary (current shell only)**
```bash
export OPENAI_API_KEY="your-key-here"
python backend/tests/run_phase7_tests.py
```

**Option 2: Shell profile (persistent for your user)**
```bash
# Add to ~/.bashrc, ~/.zshrc, or equivalent
export OPENAI_API_KEY="your-key-here"
```

**Option 3: Directory-specific (.env file - do NOT commit)**
```bash
# Create .env file (add to .gitignore if not already there)
echo "OPENAI_API_KEY=your-key-here" > .env

# Load in current shell
source .env
python backend/tests/run_phase7_tests.py
```

### .gitignore Protection

**Ensure .env is in .gitignore:**
```bash
# Check if .env is ignored
grep "^.env$" .gitignore

# If not, add it
echo ".env" >> .gitignore
```

## Full Test Suite (Pytest)

For complete unit test coverage, install pytest and run:

```bash
export OPENAI_API_KEY="your-key-here"

# PHASE7-001 unit tests
pytest backend/tests/unit/ml/test_store_clustering.py -v

# PHASE7-002/003 unit tests (requires full app setup)
pytest backend/tests/unit/agents/test_inventory_agent.py -v

# PHASE7-004 integration tests (requires Phase 6 Demand Agent)
pytest backend/tests/integration/test_inventory_agent_integration.py -v

# All Phase 7 tests with coverage
pytest backend/tests/ -k "phase7 or inventory_agent or store_clustering" -v --cov=backend/app
```

## Test Results Interpretation

### Successful Run
```
✓ PHASE7-001: StoreClusterer (K-means clustering)
✓ PHASE7-002: Inventory Allocation (3-layer hierarchy)
✓ PHASE7-003: Replenishment (parameter-driven)

Overall Status: ✓ ALL TESTS PASSED

Next steps:
  1. Run pytest for full unit test coverage
  2. Run integration tests (requires full app setup)
```

### Failed Run
If any test fails:
1. Check that OPENAI_API_KEY is set: `echo $OPENAI_API_KEY`
2. Verify environment: `python -c "import pandas, numpy, sklearn; print('OK')"`
3. Check logs in output for specific failure
4. Review test code in `backend/tests/` directory

## Troubleshooting

**"OPENAI_API_KEY environment variable not set"**
- Solution: `export OPENAI_API_KEY="your-key"`

**"ModuleNotFoundError: No module named 'prophet'"**
- Solution: Install dependencies: `pip install prophet pandas numpy scikit-learn`

**"No module named 'app'"**
- Solution: Run from project root directory: `cd /path/to/project && python ...`

**"Silhouette score below 0.4"**
- This is a warning but test may still pass depending on data
- Indicates clusters may not be well-separated
- Verify store data quality

## CI/CD Integration

For continuous integration (GitHub Actions, etc.):

```yaml
- name: Run Phase 7 Tests
  env:
    OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
  run: |
    python backend/tests/run_phase7_tests.py
```

**Key Points:**
- Store API key in CI/CD secrets (e.g., GitHub Secrets)
- Never commit credentials to repository
- Tests read from environment variables automatically

## Documentation Reference

- **PHASE7-001:** `docs/04_MVP_Development/implementation/phase_7_inventory_agent/stories/PHASE7-001-kmeans-clustering.md`
- **PHASE7-002:** `docs/04_MVP_Development/implementation/phase_7_inventory_agent/stories/PHASE7-002-allocation-logic.md`
- **PHASE7-003:** `docs/04_MVP_Development/implementation/phase_7_inventory_agent/stories/PHASE7-003-replenishment-scheduling.md`
- **PHASE7-004:** `docs/04_MVP_Development/implementation/phase_7_inventory_agent/stories/PHASE7-004-integration-testing.md`
- **Checklist:** `docs/04_MVP_Development/implementation/phase_7_inventory_agent/checklist.md`
- **Implementation Plan:** `docs/04_MVP_Development/implementation/phase_7_inventory_agent/implementation_plan.md`

## Security Best Practices

✓ **Do:**
- Store API keys in environment variables
- Use `.env` for local development (add to `.gitignore`)
- Use CI/CD secrets for automated testing
- Never display credentials in logs or output

✗ **Don't:**
- Hardcode credentials in code
- Commit `.env` or credential files
- Display API keys in logs or console output
- Share credentials in repositories or documentation

---

**Last Updated:** 2025-11-16
**Phase 7 Status:** Complete and tested
