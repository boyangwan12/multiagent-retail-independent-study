# Story: Implement Context-Rich Agent Handoffs with Historical Data

**Epic:** Phase 5 - Orchestrator Foundation
**Story ID:** PHASE5-004
**Status:** Ready for Implementation
**Estimate:** 4 hours
**Agent:** `*agent dev`
**Dependencies:** PHASE5-001, PHASE5-002

**Planning References:**
- PRD v3.3: Section 4.1 (Context-Rich Handoffs Between Agents)
- Technical Architecture v3.3: Section 4.4 (Orchestrator - Context Assembly)
- Product Brief v3.3: Section 2.2 (Sequential Agent Workflow with Full Context)

---

## Story

As a backend developer,
I want to assemble rich context packages for each agent containing parameters + historical data,
So that agents receive all necessary information to make intelligent forecasting decisions.

**Business Value:** Context-rich handoffs are what make the agent system intelligent. Without full context, the Demand Agent would only see parameters but not the historical sales patterns it needs for forecasting. This story ensures each agent receives everything it needs: parameters define "what to do," historical data provides "what happened before," and agent results flow forward for cumulative intelligence.

**Epic Context:** This is Story 4 of 6 in Phase 5 (Orchestrator Foundation). It builds on Stories 5.1 (parameters) and 5.2 (handoff framework) to create the complete context assembly pipeline. In Phase 6, when we build the real Demand Agent, this context structure will enable Prophet/ARIMA to run on actual historical data instead of mocks.

---

## Acceptance Criteria

### Functional Requirements

1. ✅ `ContextAssembler` class created to package agent context
2. ✅ Historical data loader fetches sales data from Phase 1 CSV files
3. ✅ Context package for Demand Agent includes:
   - `parameters`: SeasonParameters object
   - `historical_data`: pandas DataFrame with sales history
   - `stores_data`: pandas DataFrame with store attributes
   - `category_id`: Category identifier
4. ✅ Historical data validated before packaging (required columns exist)
5. ✅ Context package for Inventory Agent includes:
   - `parameters`: SeasonParameters object (forwarded)
   - `forecast_result`: Result from Demand Agent
   - `stores_data`: Store attributes (forwarded)
6. ✅ Context packages are Pydantic models with validation
7. ✅ Missing historical data handled gracefully with error message
8. ✅ Context assembly completes in <2 seconds

### Quality Requirements

9. ✅ Historical data cached after first load (don't reload every time)
10. ✅ Context models have type hints for all fields
11. ✅ Docstrings explain what each context field is used for
12. ✅ Unit tests for context assembly with valid and invalid data
13. ✅ Integration test with AgentHandoffManager using real context
14. ✅ Memory-efficient (don't load all historical data if only need subset)

---

## Prerequisites

Before implementing this story, ensure the following are ready:

**Story Dependencies:**
- [x] PHASE5-001 (Parameter Extraction) complete
- [x] PHASE5-002 (Agent Handoff Framework) complete
- [x] `SeasonParameters` schema exists
- [x] `AgentHandoffManager` class exists

**Data Dependencies:**
- [x] Phase 1 CSV files exist with historical sales data
- [ ] Path to Phase 1 CSV files configured in `.env` or settings
- [ ] CSV files have required columns: date, store_id, category_id, units_sold

**Python Libraries:**
- [ ] pandas installed for DataFrame operations
- [ ] pydantic installed for context validation

**Why This Matters:**
Without historical data, the Demand Agent can't forecast. This story bridges the gap between static CSV files and dynamic agent execution. Getting the context structure right now means agents in Phase 6-8 receive clean, validated data in a predictable format.

---

## Tasks

### Task 1: Define Context Data Models

**Goal:** Create Pydantic models for agent context packages

**Subtasks:**
- [ ] Create file: `backend/app/schemas/agent_context.py`
- [ ] Define `DemandAgentContext` model:
  ```python
  from pydantic import BaseModel, Field
  import pandas as pd
  from app.schemas.parameters import SeasonParameters

  class DemandAgentContext(BaseModel):
      """
      Context package for Demand Agent

      Contains everything needed for category-level forecasting:
      - parameters: User's strategic parameters
      - historical_data: Past sales for time-series forecasting
      - stores_data: Store attributes for clustering
      - category_id: Category being forecasted
      """
      parameters: SeasonParameters
      historical_data: pd.DataFrame = Field(
          ...,
          description="Historical sales with columns: date, category_id, units_sold"
      )
      stores_data: pd.DataFrame = Field(
          ...,
          description="Store attributes with columns: store_id, store_size_sqft, median_income, location_tier, etc."
      )
      category_id: str = Field(..., description="Category identifier (e.g., 'CAT001')")

      class Config:
          arbitrary_types_allowed = True  # Allow pandas DataFrame
  ```
- [ ] Define `InventoryAgentContext` model:
  ```python
  class InventoryAgentContext(BaseModel):
      """
      Context package for Inventory Agent

      Contains forecast + parameters for manufacturing calculation:
      - parameters: User's strategic parameters (forwarded from Demand)
      - forecast_result: Demand Agent's forecast output
      - stores_data: Store attributes (forwarded from Demand)
      """
      parameters: SeasonParameters
      forecast_result: dict = Field(
          ...,
          description="Forecast from Demand Agent with total_forecast, safety_stock_multiplier, clusters, etc."
      )
      stores_data: pd.DataFrame

      class Config:
          arbitrary_types_allowed = True
  ```
- [ ] Define `PricingAgentContext` model (for Phase 8):
  ```python
  class PricingAgentContext(BaseModel):
      """
      Context package for Pricing Agent

      Contains forecast + inventory plan for markdown recommendations
      """
      parameters: SeasonParameters
      forecast_result: dict
      inventory_plan: dict = Field(
          ...,
          description="Manufacturing order from Inventory Agent"
      )
      actuals_data: pd.DataFrame = Field(
          default=None,
          description="Actual sales to date (for markdown decisions)"
      )

      class Config:
          arbitrary_types_allowed = True
  ```
- [ ] Test model validation with sample data

---

### Task 2: Create Historical Data Loader

**Goal:** Load Phase 1 CSV files into pandas DataFrames

**Subtasks:**
- [ ] Create file: `backend/app/data/historical_loader.py`
- [ ] Define configuration for data paths:
  ```python
  import os
  from pathlib import Path

  # Data directory from environment or default
  DATA_DIR = Path(os.getenv("DATA_DIR", "data"))
  SALES_DATA_PATH = DATA_DIR / "historical_sales.csv"
  STORES_DATA_PATH = DATA_DIR / "stores.csv"
  ```
- [ ] Implement `load_historical_sales()` function:
  ```python
  import pandas as pd
  import logging

  logger = logging.getLogger(__name__)

  def load_historical_sales(category_id: str = None) -> pd.DataFrame:
      """
      Load historical sales data from Phase 1 CSV

      Args:
          category_id: Optional category filter (e.g., 'CAT001')
                      If None, load all categories

      Returns:
          DataFrame with columns: date, store_id, category_id, units_sold

      Raises:
          FileNotFoundError: If CSV file doesn't exist
          ValueError: If required columns missing
      """
      if not SALES_DATA_PATH.exists():
          raise FileNotFoundError(
              f"Historical sales data not found at {SALES_DATA_PATH}"
          )

      logger.info(f"Loading historical sales from {SALES_DATA_PATH}")
      df = pd.read_csv(SALES_DATA_PATH)

      # Validate required columns
      required_columns = ["date", "store_id", "category_id", "units_sold"]
      missing = set(required_columns) - set(df.columns)
      if missing:
          raise ValueError(f"Missing required columns: {missing}")

      # Parse date column
      df["date"] = pd.to_datetime(df["date"])

      # Filter by category if specified
      if category_id:
          df = df[df["category_id"] == category_id].copy()
          logger.info(f"Filtered to category {category_id}: {len(df)} rows")

      return df
  ```
- [ ] Implement `load_stores_data()` function:
  ```python
  def load_stores_data() -> pd.DataFrame:
      """
      Load store attributes from Phase 1 CSV

      Returns:
          DataFrame with columns: store_id, store_size_sqft, median_income,
                                  location_tier, fashion_tier, store_format, region

      Raises:
          FileNotFoundError: If CSV file doesn't exist
          ValueError: If required columns missing
      """
      if not STORES_DATA_PATH.exists():
          raise FileNotFoundError(
              f"Stores data not found at {STORES_DATA_PATH}"
          )

      logger.info(f"Loading stores data from {STORES_DATA_PATH}")
      df = pd.read_csv(STORES_DATA_PATH)

      # Validate required columns (7 features for clustering)
      required_columns = [
          "store_id",
          "store_size_sqft",
          "median_income",
          "location_tier",
          "fashion_tier",
          "store_format",
          "region"
      ]
      missing = set(required_columns) - set(df.columns)
      if missing:
          raise ValueError(f"Missing required store columns: {missing}")

      return df
  ```
- [ ] Add caching to avoid repeated file reads:
  ```python
  from functools import lru_cache

  @lru_cache(maxsize=1)
  def load_stores_data_cached() -> pd.DataFrame:
      """Cached version of load_stores_data()"""
      return load_stores_data()
  ```
- [ ] Test data loading with Phase 1 CSV files

---

### Task 3: Create Context Assembler

**Goal:** Assemble complete context packages for each agent

**Subtasks:**
- [ ] Create file: `backend/app/orchestrator/context_assembler.py`
- [ ] Implement `ContextAssembler` class:
  ```python
  from app.schemas.agent_context import (
      DemandAgentContext,
      InventoryAgentContext,
      PricingAgentContext
  )
  from app.schemas.parameters import SeasonParameters
  from app.data.historical_loader import (
      load_historical_sales,
      load_stores_data_cached
  )
  import logging

  class ContextAssembler:
      """
      Assembles context packages for agents with parameters + data

      Usage:
          assembler = ContextAssembler()
          demand_context = await assembler.assemble_demand_context(parameters)
      """

      def __init__(self):
          self.logger = logging.getLogger(__name__)

      async def assemble_demand_context(
          self,
          parameters: SeasonParameters,
          category_id: str = "CAT001"
      ) -> DemandAgentContext:
          """
          Assemble context for Demand Agent

          Args:
              parameters: Extracted season parameters
              category_id: Category to forecast

          Returns:
              DemandAgentContext with parameters + historical data + stores

          Raises:
              FileNotFoundError: If data files missing
              ValueError: If data validation fails
          """
          self.logger.info(f"Assembling Demand Agent context for {category_id}")

          # Load historical sales for category
          historical_data = load_historical_sales(category_id)

          if historical_data.empty:
              raise ValueError(f"No historical data found for category {category_id}")

          # Load store attributes (cached)
          stores_data = load_stores_data_cached()

          # Assemble context
          context = DemandAgentContext(
              parameters=parameters,
              historical_data=historical_data,
              stores_data=stores_data,
              category_id=category_id
          )

          self.logger.info(
              f"Context assembled: {len(historical_data)} historical records, "
              f"{len(stores_data)} stores"
          )

          return context

      async def assemble_inventory_context(
          self,
          parameters: SeasonParameters,
          forecast_result: dict,
          stores_data: pd.DataFrame
      ) -> InventoryAgentContext:
          """
          Assemble context for Inventory Agent

          Args:
              parameters: Season parameters (forwarded from Demand)
              forecast_result: Forecast from Demand Agent
              stores_data: Store attributes (forwarded from Demand)

          Returns:
              InventoryAgentContext
          """
          self.logger.info("Assembling Inventory Agent context")

          context = InventoryAgentContext(
              parameters=parameters,
              forecast_result=forecast_result,
              stores_data=stores_data
          )

          return context

      async def assemble_pricing_context(
          self,
          parameters: SeasonParameters,
          forecast_result: dict,
          inventory_plan: dict,
          actuals_data: pd.DataFrame = None
      ) -> PricingAgentContext:
          """
          Assemble context for Pricing Agent

          Args:
              parameters: Season parameters
              forecast_result: Forecast from Demand Agent
              inventory_plan: Manufacturing order from Inventory Agent
              actuals_data: Optional actual sales to date (for markdown decisions)

          Returns:
              PricingAgentContext
          """
          self.logger.info("Assembling Pricing Agent context")

          context = PricingAgentContext(
              parameters=parameters,
              forecast_result=forecast_result,
              inventory_plan=inventory_plan,
              actuals_data=actuals_data
          )

          return context
  ```
- [ ] Test context assembly with mock parameters and real CSV data

---

### Task 4: Integrate Context Assembly with Orchestrator

**Goal:** Use ContextAssembler in orchestrator workflow

**Subtasks:**
- [ ] Update `backend/app/routers/orchestrator.py` workflow endpoint:
  ```python
  from app.orchestrator.context_assembler import ContextAssembler

  @router.post("/run-workflow")
  async def run_workflow(
      strategy_description: str,
      session_id: str,
      category_id: str = "CAT001",  # NEW PARAMETER
      openai_client: Any = Depends(get_openai_client)
  ):
      """
      Run complete orchestrator workflow with context assembly

      Args:
          strategy_description: User's natural language strategy
          session_id: WebSocket session ID for progress updates
          category_id: Category to forecast (default CAT001)
          openai_client: Azure OpenAI client
      """
      from app.orchestrator.agent_handoff import handoff_manager
      from app.orchestrator.websocket_manager import connection_manager

      assembler = ContextAssembler()

      try:
          # Step 1: Extract parameters
          parameters = await extract_parameters_from_text(
              strategy_description,
              openai_client
          )

          # Step 2: Assemble Demand Agent context
          await connection_manager.send_message(
              session_id,
              ProgressMessage(
                  session_id=session_id,
                  agent="orchestrator",
                  status="Loading historical data...",
                  progress=20
              )
          )

          demand_context = await assembler.assemble_demand_context(
              parameters,
              category_id
          )

          # Step 3: Call Demand Agent with full context
          forecast = await handoff_manager.call_agent(
              "demand",
              demand_context,  # Now passing full context instead of just parameters
              session_id=session_id
          )

          # Step 4: Assemble Inventory Agent context (when Inventory Agent exists)
          # inventory_context = await assembler.assemble_inventory_context(
          #     parameters,
          #     forecast,
          #     demand_context.stores_data
          # )

          return {"status": "success", "forecast": forecast}

      except FileNotFoundError as e:
          await connection_manager.send_message(
              session_id,
              ErrorMessage(
                  session_id=session_id,
                  error="Historical data not found",
                  details=str(e)
              )
          )
          raise HTTPException(status_code=404, detail=str(e))

      except Exception as e:
          await connection_manager.send_message(
              session_id,
              ErrorMessage(
                  session_id=session_id,
                  error="Workflow failed",
                  details=str(e)
              )
          )
          raise HTTPException(status_code=500, detail=str(e))
  ```
- [ ] Update mock Demand Agent to accept `DemandAgentContext`:
  ```python
  async def mock_demand_agent(context: DemandAgentContext) -> Dict:
      """
      Mock Demand Agent now receives full context

      Args:
          context: DemandAgentContext with parameters + historical data + stores
      """
      await asyncio.sleep(0.5)

      params = context.parameters
      historical_rows = len(context.historical_data)
      store_count = len(context.stores_data)

      # Adapt safety stock based on replenishment strategy
      if params.replenishment_strategy == "none":
          safety_stock = 1.25
      elif params.replenishment_strategy == "weekly":
          safety_stock = 1.20
      else:
          safety_stock = 1.22

      return {
          "agent": "demand",
          "category_id": context.category_id,
          "total_forecast": 8000,
          "safety_stock_multiplier": safety_stock,
          "weekly_curve": [650, 680, 720, 740, 760, 730, 710, 680, 650, 620, 580, 480],
          "clusters": ["Fashion_Forward", "Mainstream", "Value_Conscious"],
          "message": f"Mock forecast using {historical_rows} historical records, {store_count} stores"
      }
  ```
- [ ] Test end-to-end workflow with context assembly

---

### Task 5: Add Error Handling for Missing Data

**Goal:** Handle data loading failures gracefully

**Subtasks:**
- [ ] Add custom exceptions in `backend/app/exceptions.py`:
  ```python
  class DataNotFoundError(Exception):
      """Raised when required historical data is not found"""
      pass

  class DataValidationError(Exception):
      """Raised when data doesn't meet requirements"""
      pass
  ```
- [ ] Update historical loader to use custom exceptions:
  ```python
  def load_historical_sales(category_id: str = None) -> pd.DataFrame:
      if not SALES_DATA_PATH.exists():
          raise DataNotFoundError(
              f"Historical sales data not found. "
              f"Please ensure Phase 1 CSV file exists at {SALES_DATA_PATH}"
          )

      # ... rest of function
  ```
- [ ] Add data quality checks:
  ```python
  def validate_historical_data(df: pd.DataFrame, category_id: str):
      """
      Validate historical data meets minimum requirements

      Args:
          df: Historical sales DataFrame
          category_id: Category being validated

      Raises:
          DataValidationError: If data quality issues found
      """
      if df.empty:
          raise DataValidationError(
              f"No data found for category {category_id}"
          )

      if len(df) < 52:  # Need at least 52 weeks for Prophet
          raise DataValidationError(
              f"Insufficient history for {category_id}: {len(df)} rows. "
              f"Prophet requires at least 52 weeks (1 year) of data."
          )

      # Check for nulls in critical columns
      null_counts = df[["date", "units_sold"]].isnull().sum()
      if null_counts.any():
          raise DataValidationError(
              f"Missing values in historical data: {null_counts.to_dict()}"
          )
  ```
- [ ] Test error handling with missing/invalid data

---

### Task 6: Write Tests

**Goal:** Ensure context assembly works correctly

**Subtasks:**
- [ ] Create file: `backend/tests/test_context_assembly.py`
- [ ] **Test 1:** Load historical sales
  ```python
  def test_load_historical_sales():
      from app.data.historical_loader import load_historical_sales

      df = load_historical_sales(category_id="CAT001")

      assert not df.empty
      assert "date" in df.columns
      assert "units_sold" in df.columns
      assert df["date"].dtype == "datetime64[ns]"
  ```
- [ ] **Test 2:** Load stores data
  ```python
  def test_load_stores_data():
      from app.data.historical_loader import load_stores_data

      df = load_stores_data()

      assert not df.empty
      assert "store_id" in df.columns
      assert len(df.columns) >= 7  # 7 features for clustering
  ```
- [ ] **Test 3:** Assemble Demand context
  ```python
  @pytest.mark.asyncio
  async def test_assemble_demand_context():
      from app.orchestrator.context_assembler import ContextAssembler
      from app.schemas.parameters import SeasonParameters
      from datetime import date

      assembler = ContextAssembler()

      params = SeasonParameters(
          forecast_horizon_weeks=12,
          season_start_date=date(2025, 3, 1),
          season_end_date=date(2025, 5, 23),
          replenishment_strategy="none",
          dc_holdback_percentage=0.0
      )

      context = await assembler.assemble_demand_context(params, "CAT001")

      assert context.parameters == params
      assert not context.historical_data.empty
      assert not context.stores_data.empty
      assert context.category_id == "CAT001"
  ```
- [ ] **Test 4:** Missing data error handling
  ```python
  @pytest.mark.asyncio
  async def test_missing_data_handling():
      from app.orchestrator.context_assembler import ContextAssembler

      assembler = ContextAssembler()

      with pytest.raises(ValueError, match="No historical data"):
          await assembler.assemble_demand_context(params, "INVALID_CATEGORY")
  ```
- [ ] Run tests: `uv run pytest backend/tests/test_context_assembly.py -v`

---

## Implementation Notes

**Data Path Configuration (.env):**
```bash
# backend/.env
DATA_DIR=data
```

**Expected CSV Structure:**
```
data/
  historical_sales.csv      # Columns: date, store_id, category_id, units_sold
  stores.csv                # Columns: store_id, store_size_sqft, median_income, location_tier, fashion_tier, store_format, region
```

**Context Flow Through Agents:**
```
User Input
    ↓
Parameters (5 fields)
    ↓
+ Historical Data (52+ weeks)
+ Stores Data (50 stores, 7 features)
    ↓
Demand Agent Context
    ↓
Forecast Result (total, curve, clusters, allocations)
    ↓
+ Parameters (forwarded)
+ Stores Data (forwarded)
    ↓
Inventory Agent Context
    ↓
Manufacturing Order
    ↓
+ Parameters (forwarded)
+ Forecast (forwarded)
    ↓
Pricing Agent Context
```

---

## Definition of Done

- [ ] `DemandAgentContext`, `InventoryAgentContext`, `PricingAgentContext` models defined
- [ ] Historical data loader implemented with `load_historical_sales()`
- [ ] Stores data loader implemented with `load_stores_data()`
- [ ] Data caching implemented to avoid repeated file reads
- [ ] `ContextAssembler` class created with context assembly methods
- [ ] Orchestrator workflow updated to use context assembly
- [ ] Mock Demand Agent updated to accept full context
- [ ] Error handling for missing/invalid data
- [ ] Data validation checks (minimum 52 weeks, no nulls)
- [ ] Unit tests for data loading and context assembly
- [ ] Integration test with full workflow
- [ ] Documentation for expected CSV structure
- [ ] Code reviewed and merged

---

**Created:** 2025-11-04
**Last Updated:** 2025-11-04
