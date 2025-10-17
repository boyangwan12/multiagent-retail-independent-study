# Phase 5: Demand Agent Implementation - Implementation Plan

**Phase:** 5 of 8
**Agent:** `*agent dev`
**Date:** 2025-10-17
**Status:** Not Started
**Estimated Duration:** 6-8 days (48 hours)

---

## Phase Overview

### Context from Previous Phases

**Phase 4 Deliverables (Available):**
- Orchestrator agent with parameter-driven workflow coordination
- Variance monitoring system (>20% threshold detection)
- Conditional phase execution (skip phases based on parameters)
- Context-rich handoffs with full parameter context
- Human-in-the-loop approval workflow
- WebSocket status streaming
- LLM reasoning integration

**Phase 5 Focus:**
Replace mocked Demand Agent with actual ML implementation:
- Ensemble forecasting (Prophet + ARIMA in parallel, averaged)
- K-means clustering with 7 features (StandardScaler normalization)
- Parameter-aware safety stock adjustment
- Store allocation factors (70% historical + 30% attributes)
- LLM reasoning for parameter interpretation

---

## Phase Goals

### Primary Objectives

1. **Implement Ensemble Forecasting**: Prophet + ARIMA in parallel, average results
2. **Implement K-means Clustering**: 7 features (avg_weekly_sales_12mo, store_size_sqft, median_income, location_tier, fashion_tier, store_format, region)
3. **Parameter-Aware Safety Stock**: Adjust from 20% (default) to 25% (no replenishment)
4. **Store Allocation Logic**: Hybrid (70% historical factor + 30% attribute factor)
5. **LLM Reasoning Integration**: Interpret parameters and explain decisions
6. **Structured Forecast Output**: Return forecast object for orchestrator handoff

### Success Metrics

| Metric | Target | Validation Method |
|--------|--------|-------------------|
| Forecast MAPE (Mean Absolute Percentage Error) | <20% | Compare forecast vs Phase 1 CSV actuals |
| Clustering silhouette score | >0.4 | Scikit-learn metrics |
| Prophet + ARIMA agreement | Within 10% | Compare both model outputs |
| Parameter interpretation accuracy | >90% | LLM reasoning validation |
| Forecast execution time | <10s | Performance testing |
| Context-rich handoff success | 100% | Integration test with Orchestrator |

---

## Task Breakdown

### Task 1: Demand Agent Foundation & LLM Instructions
**Estimated Time:** 4 hours
**Dependencies:** Phase 4 (Orchestrator Agent)
**Priority:** Critical

**Subtasks:**
- [ ] Update `backend/app/agents/demand.py` (remove mock implementation)
- [ ] Define Demand Agent using OpenAI Agents SDK
- [ ] Write LLM instructions for parameter interpretation
  - How `replenishment_strategy` affects safety stock
  - How `forecast_horizon_weeks` affects Prophet/ARIMA settings
  - How to interpret variance triggers for re-forecast
- [ ] Add parameter context to agent initialization
- [ ] Implement handoff registration (to Inventory Agent)
- [ ] Create `DemandAgentContext` data class
  - `parameters: SeasonParameters`
  - `historical_data: pd.DataFrame`
  - `actuals: Optional[pd.DataFrame]` (for re-forecast)
  - `variance_info: Optional[VarianceContext]`
- [ ] Test basic agent creation and parameter reception

**Code Snippet - Agent Definition:**
```python
from openai_agents import Agent

demand_agent = Agent(
    name="Demand Agent",
    instructions="""
    You are a demand forecasting specialist for a parameter-driven retail system.

    Your responsibilities:
    1. Analyze season parameters (forecast_horizon_weeks, replenishment_strategy)
    2. Adjust safety stock based on replenishment strategy:
       - IF replenishment_strategy = "none": Use 25% safety stock (no error correction)
       - IF replenishment_strategy = "weekly": Use 20% safety stock (default)
       - IF replenishment_strategy = "bi-weekly": Use 22% safety stock (moderate)
    3. Run ensemble forecast (Prophet + ARIMA in parallel, average results)
    4. Perform K-means clustering (K=3, 7 features) on stores
    5. Calculate cluster distribution percentages (historical analysis)
    6. Calculate store allocation factors (70% historical + 30% attributes)
    7. Return structured forecast object with LLM reasoning

    Parameter reasoning examples:
    - "12-week horizon with no replenishment → increase safety stock to 25% to buffer against forecast errors"
    - "26-week horizon with weekly replenishment → use default 20% safety stock, rely on weekly corrections"

    Always pass forecast object to Inventory Agent via handoff for manufacturing calculation.
    """,
    model="gpt-4o-mini",
    handoffs=["inventory"]
)
```

**Validation:**
- Agent initializes without errors
- Parameters received correctly in agent context
- LLM instructions accessible
- Handoff to Inventory Agent registered

**Risk:** LLM instruction quality affects reasoning accuracy
**Mitigation:** Validate with multiple parameter sets (Zara, standard retail, luxury)

---

### Task 2: Ensemble Forecasting - Prophet Implementation
**Estimated Time:** 6 hours
**Dependencies:** Task 1
**Priority:** Critical

**Subtasks:**
- [ ] Install Prophet: `uv add prophet`
- [ ] Create `backend/app/ml/prophet_forecast.py`
- [ ] Implement Prophet forecasting function
  - Data preparation (ds, y format)
  - Model training with historical data
  - Forecast for N weeks (from parameters)
  - Extract weekly predictions
- [ ] Handle Prophet-specific parameters
  - `changepoint_prior_scale` tuning
  - `seasonality_mode` (additive vs multiplicative)
  - Weekly seasonality enabled
- [ ] Implement error handling for Prophet failures
- [ ] Add logging for Prophet model parameters
- [ ] Unit tests for Prophet forecast function

**Code Snippet - Prophet Implementation:**
```python
from prophet import Prophet
import pandas as pd
from typing import Dict, List

def prophet_forecast(
    historical_data: pd.DataFrame,
    forecast_horizon_weeks: int,
    category_id: str
) -> Dict:
    """
    Forecast demand using Prophet

    Args:
        historical_data: Historical sales with 'date' and 'units_sold' columns
        forecast_horizon_weeks: Number of weeks to forecast (from parameters)
        category_id: Category identifier

    Returns:
        Dict with forecast results:
        {
            'method': 'prophet',
            'total_forecast': 8200,
            'weekly_predictions': [650, 680, 720, ...],
            'model_params': {...}
        }
    """
    # Prepare data in Prophet format
    df_prophet = historical_data.rename(columns={
        'date': 'ds',
        'units_sold': 'y'
    })

    # Initialize Prophet with tuned parameters
    model = Prophet(
        changepoint_prior_scale=0.05,  # Flexibility in trend changes
        seasonality_mode='additive',    # Additive seasonality
        weekly_seasonality=True,
        yearly_seasonality=False,       # Not enough history
        daily_seasonality=False
    )

    # Fit model
    model.fit(df_prophet)

    # Create future dataframe
    future = model.make_future_dataframe(periods=forecast_horizon_weeks, freq='W')

    # Generate forecast
    forecast = model.predict(future)

    # Extract predictions for forecast horizon
    weekly_predictions = forecast['yhat'].tail(forecast_horizon_weeks).tolist()
    total_forecast = sum(weekly_predictions)

    return {
        'method': 'prophet',
        'total_forecast': round(total_forecast),
        'weekly_predictions': [round(p) for p in weekly_predictions],
        'model_params': {
            'changepoint_prior_scale': 0.05,
            'seasonality_mode': 'additive',
            'weekly_seasonality': True
        },
        'confidence_intervals': {
            'lower': forecast['yhat_lower'].tail(forecast_horizon_weeks).tolist(),
            'upper': forecast['yhat_upper'].tail(forecast_horizon_weeks).tolist()
        }
    }
```

**Validation:**
- Prophet forecasts Phase 1 CSV data correctly
- Weekly predictions sum to total forecast
- Confidence intervals returned
- Execution time <5 seconds

**Risk:** Prophet requires significant historical data (>2 years recommended)
**Mitigation:** Use at least 52 weeks of historical data from Phase 1 CSVs

---

### Task 3: Ensemble Forecasting - ARIMA Implementation
**Estimated Time:** 6 hours
**Dependencies:** Task 1
**Priority:** Critical

**Subtasks:**
- [ ] Install pmdarima: `uv add pmdarima`
- [ ] Create `backend/app/ml/arima_forecast.py`
- [ ] Implement auto-ARIMA forecasting function
  - Automatic parameter selection (p, d, q)
  - Model training with historical data
  - Forecast for N weeks
  - Extract weekly predictions
- [ ] Handle ARIMA-specific settings
  - Seasonal ARIMA (SARIMAX) with weekly seasonality
  - `stepwise=True` for faster parameter search
  - AIC/BIC information criteria
- [ ] Implement error handling for ARIMA failures
- [ ] Add logging for ARIMA model parameters (p, d, q, P, D, Q, m)
- [ ] Unit tests for ARIMA forecast function

**Code Snippet - ARIMA Implementation:**
```python
from pmdarima import auto_arima
import pandas as pd
from typing import Dict, List

def arima_forecast(
    historical_data: pd.DataFrame,
    forecast_horizon_weeks: int,
    category_id: str
) -> Dict:
    """
    Forecast demand using auto-ARIMA

    Args:
        historical_data: Historical sales with 'date' and 'units_sold' columns
        forecast_horizon_weeks: Number of weeks to forecast (from parameters)
        category_id: Category identifier

    Returns:
        Dict with forecast results:
        {
            'method': 'arima',
            'total_forecast': 7800,
            'weekly_predictions': [620, 640, 660, ...],
            'model_params': {...}
        }
    """
    # Prepare time series (weekly aggregation)
    ts_data = historical_data.set_index('date')['units_sold']
    ts_weekly = ts_data.resample('W').sum()

    # Auto-ARIMA model selection
    model = auto_arima(
        ts_weekly,
        seasonal=True,           # Enable seasonal ARIMA
        m=52,                    # Weekly seasonality (52 weeks/year)
        stepwise=True,           # Faster parameter search
        suppress_warnings=True,
        error_action='ignore',
        information_criterion='aic',
        max_p=5,                 # Max AR order
        max_q=5,                 # Max MA order
        max_P=2,                 # Max seasonal AR order
        max_Q=2,                 # Max seasonal MA order
        max_d=2,                 # Max differencing
        max_D=1                  # Max seasonal differencing
    )

    # Generate forecast
    forecast_values, conf_int = model.predict(
        n_periods=forecast_horizon_weeks,
        return_conf_int=True
    )

    weekly_predictions = forecast_values.tolist()
    total_forecast = sum(weekly_predictions)

    return {
        'method': 'arima',
        'total_forecast': round(total_forecast),
        'weekly_predictions': [round(p) for p in weekly_predictions],
        'model_params': {
            'order': model.order,         # (p, d, q)
            'seasonal_order': model.seasonal_order,  # (P, D, Q, m)
            'aic': model.aic()
        },
        'confidence_intervals': {
            'lower': conf_int[:, 0].tolist(),
            'upper': conf_int[:, 1].tolist()
        }
    }
```

**Validation:**
- ARIMA forecasts Phase 1 CSV data correctly
- Auto-ARIMA selects reasonable parameters
- Weekly predictions sum to total forecast
- Execution time <5 seconds

**Risk:** ARIMA may fail on non-stationary data
**Mitigation:** auto_arima handles differencing automatically

---

### Task 4: Ensemble Averaging & Parallel Execution
**Estimated Time:** 4 hours
**Dependencies:** Task 2, Task 3
**Priority:** Critical

**Subtasks:**
- [ ] Create `backend/app/ml/ensemble_forecast.py`
- [ ] Implement parallel execution of Prophet + ARIMA
  - Use `asyncio.gather()` for concurrent execution
  - Handle individual model failures gracefully
- [ ] Implement ensemble averaging logic
  - Simple average: `(prophet_total + arima_total) / 2`
  - Weekly curve averaging: `(prophet_week_1 + arima_week_1) / 2`
- [ ] Add model agreement metric
  - Calculate percentage difference between models
  - Log warning if difference >20%
- [ ] Implement fallback logic
  - If Prophet fails: Use ARIMA only
  - If ARIMA fails: Use Prophet only
  - If both fail: Return error
- [ ] Unit tests for ensemble logic

**Code Snippet - Ensemble Implementation:**
```python
import asyncio
from typing import Dict, Tuple
import logging

async def ensemble_forecast_parallel(
    historical_data: pd.DataFrame,
    forecast_horizon_weeks: int,
    category_id: str
) -> Dict:
    """
    Run Prophet and ARIMA in parallel, average results

    Returns:
        Dict with ensemble forecast:
        {
            'method': 'ensemble',
            'total_forecast': 8000,  # Averaged
            'weekly_predictions': [635, 660, 690, ...],  # Averaged
            'prophet_result': {...},
            'arima_result': {...},
            'model_agreement_pct': 95.2
        }
    """
    # Run both models in parallel
    prophet_task = asyncio.to_thread(
        prophet_forecast,
        historical_data,
        forecast_horizon_weeks,
        category_id
    )
    arima_task = asyncio.to_thread(
        arima_forecast,
        historical_data,
        forecast_horizon_weeks,
        category_id
    )

    # Wait for both to complete
    try:
        prophet_result, arima_result = await asyncio.gather(
            prophet_task,
            arima_task,
            return_exceptions=True
        )
    except Exception as e:
        logging.error(f"Ensemble forecast failed: {e}")
        raise

    # Handle individual failures
    if isinstance(prophet_result, Exception):
        logging.warning(f"Prophet failed: {prophet_result}, using ARIMA only")
        return {**arima_result, 'method': 'arima_only'}

    if isinstance(arima_result, Exception):
        logging.warning(f"ARIMA failed: {arima_result}, using Prophet only")
        return {**prophet_result, 'method': 'prophet_only'}

    # Calculate ensemble average
    total_prophet = prophet_result['total_forecast']
    total_arima = arima_result['total_forecast']
    total_ensemble = round((total_prophet + total_arima) / 2)

    # Weekly curve averaging
    weekly_ensemble = [
        round((p + a) / 2)
        for p, a in zip(
            prophet_result['weekly_predictions'],
            arima_result['weekly_predictions']
        )
    ]

    # Calculate model agreement
    model_agreement_pct = 100 * (1 - abs(total_prophet - total_arima) / max(total_prophet, total_arima))

    if model_agreement_pct < 80:
        logging.warning(
            f"Low model agreement: {model_agreement_pct:.1f}% "
            f"(Prophet: {total_prophet}, ARIMA: {total_arima})"
        )

    return {
        'method': 'ensemble',
        'total_forecast': total_ensemble,
        'weekly_predictions': weekly_ensemble,
        'prophet_result': prophet_result,
        'arima_result': arima_result,
        'model_agreement_pct': round(model_agreement_pct, 1)
    }
```

**Validation:**
- Prophet and ARIMA run in parallel (<5s total, not <10s sequential)
- Ensemble average calculated correctly
- Model agreement metric accurate
- Fallback logic works when one model fails

**Risk:** Low model agreement may indicate data quality issues
**Mitigation:** Log warnings when agreement <80%, investigate causes

---

### Task 5: K-means Store Clustering
**Estimated Time:** 5 hours
**Dependencies:** Task 1
**Priority:** Critical

**Subtasks:**
- [ ] Install scikit-learn: `uv add scikit-learn`
- [ ] Create `backend/app/ml/clustering.py`
- [ ] Implement K-means clustering with 7 features
  - Load store data from database
  - Extract 7 features: `avg_weekly_sales_12mo`, `store_size_sqft`, `median_income`, `location_tier`, `fashion_tier`, `store_format`, `region`
  - Apply StandardScaler normalization
  - Run K-means++ (K=3)
  - Assign cluster labels
- [ ] Calculate cluster characteristics
  - Cluster size (number of stores)
  - Average features per cluster
  - Cluster names (Fashion_Forward, Mainstream, Value_Conscious)
- [ ] Calculate clustering quality metrics
  - Silhouette score (target >0.4)
  - Inertia (within-cluster sum of squares)
- [ ] Save cluster assignments to database
- [ ] Unit tests for clustering logic

**Code Snippet - K-means Clustering:**
```python
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score
import pandas as pd
from typing import Dict, List

def kmeans_store_clustering(
    stores_df: pd.DataFrame,
    n_clusters: int = 3
) -> Dict:
    """
    Cluster stores using K-means with 7 features

    Args:
        stores_df: DataFrame with store attributes
        n_clusters: Number of clusters (default 3)

    Returns:
        Dict with clustering results:
        {
            'cluster_assignments': [0, 2, 1, ...],
            'cluster_names': ['Fashion_Forward', 'Mainstream', 'Value_Conscious'],
            'cluster_sizes': [20, 18, 12],
            'silhouette_score': 0.52,
            'cluster_characteristics': {...}
        }
    """
    # Extract 7 features
    features = [
        'avg_weekly_sales_12mo',  # MOST IMPORTANT
        'store_size_sqft',
        'median_income',
        'location_tier',          # A=3, B=2, C=1
        'fashion_tier',           # Premium=3, Mainstream=2, Value=1
        'store_format',           # Mall=4, Standalone=3, ShoppingCenter=2, Outlet=1
        'region'                  # Northeast=1, Southeast=2, Midwest=3, West=4
    ]

    X = stores_df[features].values

    # Standardize features (mean=0, std=1)
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # K-means++ initialization
    kmeans = KMeans(
        n_clusters=n_clusters,
        init='k-means++',
        n_init=10,
        max_iter=300,
        random_state=42
    )

    # Fit and predict
    cluster_labels = kmeans.fit_predict(X_scaled)

    # Calculate silhouette score
    silhouette = silhouette_score(X_scaled, cluster_labels)

    # Assign cluster names based on avg_weekly_sales_12mo
    cluster_avg_sales = {}
    for cluster_id in range(n_clusters):
        mask = cluster_labels == cluster_id
        cluster_avg_sales[cluster_id] = stores_df.loc[mask, 'avg_weekly_sales_12mo'].mean()

    # Sort clusters by sales (high to low)
    sorted_clusters = sorted(cluster_avg_sales.items(), key=lambda x: x[1], reverse=True)
    cluster_name_map = {
        sorted_clusters[0][0]: 'Fashion_Forward',
        sorted_clusters[1][0]: 'Mainstream',
        sorted_clusters[2][0]: 'Value_Conscious'
    }

    # Map labels to names
    cluster_names = [cluster_name_map[label] for label in cluster_labels]

    # Calculate cluster sizes
    unique, counts = np.unique(cluster_labels, return_counts=True)
    cluster_sizes = dict(zip(unique, counts))

    return {
        'cluster_assignments': cluster_labels.tolist(),
        'cluster_names': cluster_names,
        'cluster_sizes': [cluster_sizes[0], cluster_sizes[1], cluster_sizes[2]],
        'silhouette_score': round(silhouette, 2),
        'cluster_characteristics': {
            'Fashion_Forward': {
                'avg_sales': cluster_avg_sales[sorted_clusters[0][0]],
                'store_count': cluster_sizes[sorted_clusters[0][0]]
            },
            'Mainstream': {
                'avg_sales': cluster_avg_sales[sorted_clusters[1][0]],
                'store_count': cluster_sizes[sorted_clusters[1][0]]
            },
            'Value_Conscious': {
                'avg_sales': cluster_avg_sales[sorted_clusters[2][0]],
                'store_count': cluster_sizes[sorted_clusters[2][0]]
            }
        },
        'scaler': scaler,
        'kmeans_model': kmeans
    }
```

**Validation:**
- Clustering produces 3 clusters
- Silhouette score >0.4
- Cluster names assigned correctly (high sales → Fashion_Forward)
- All 50 stores assigned to a cluster

**Risk:** Poor clustering may lead to suboptimal allocations
**Mitigation:** Validate silhouette score, manually review cluster assignments

---

### Task 6: Cluster Distribution & Store Allocation Factors
**Estimated Time:** 5 hours
**Dependencies:** Task 5
**Priority:** Critical

**Subtasks:**
- [ ] Create `backend/app/ml/allocation.py`
- [ ] Implement cluster distribution calculation
  - Analyze historical sales by cluster
  - Calculate percentage distribution (e.g., 40%, 35%, 25%)
  - Adjust based on forecast vs historical total
- [ ] Implement store allocation factor calculation (within cluster)
  - Historical factor (70% weight): `store_sales / cluster_sales`
  - Attribute factor (30% weight): `store_capacity / total_capacity`
  - Hybrid factor: `0.70 × hist + 0.30 × attr`
- [ ] Validate allocation factors sum to 100% per cluster
- [ ] Unit tests for allocation logic

**Code Snippet - Allocation Factors:**
```python
def calculate_store_allocation_factors(
    stores_df: pd.DataFrame,
    cluster_assignments: List[str],
    historical_data: pd.DataFrame
) -> pd.DataFrame:
    """
    Calculate store allocation factors within each cluster

    Args:
        stores_df: Store attributes
        cluster_assignments: Cluster names per store
        historical_data: Historical sales by store

    Returns:
        DataFrame with allocation factors per store
        Columns: store_id, cluster, historical_factor, attribute_factor, allocation_factor
    """
    stores_df = stores_df.copy()
    stores_df['cluster'] = cluster_assignments

    allocation_factors = []

    for cluster_name in ['Fashion_Forward', 'Mainstream', 'Value_Conscious']:
        cluster_stores = stores_df[stores_df['cluster'] == cluster_name].copy()

        # Historical factor (70% weight)
        cluster_hist_sales = historical_data[
            historical_data['store_id'].isin(cluster_stores['store_id'])
        ].groupby('store_id')['units_sold'].sum()

        total_cluster_sales = cluster_hist_sales.sum()
        cluster_stores['historical_factor'] = cluster_stores['store_id'].map(
            lambda sid: cluster_hist_sales.get(sid, 0) / total_cluster_sales
        )

        # Attribute factor (30% weight) - based on store size
        total_cluster_size = cluster_stores['store_size_sqft'].sum()
        cluster_stores['attribute_factor'] = (
            cluster_stores['store_size_sqft'] / total_cluster_size
        )

        # Hybrid allocation factor
        cluster_stores['allocation_factor'] = (
            0.70 * cluster_stores['historical_factor'] +
            0.30 * cluster_stores['attribute_factor']
        )

        # Normalize to ensure sum = 1.0 within cluster
        total_factor = cluster_stores['allocation_factor'].sum()
        cluster_stores['allocation_factor'] = (
            cluster_stores['allocation_factor'] / total_factor
        )

        allocation_factors.append(cluster_stores)

    return pd.concat(allocation_factors, ignore_index=True)
```

**Validation:**
- Allocation factors sum to 1.0 within each cluster
- Historical factor reflects past sales correctly
- Attribute factor reflects store capacity
- Hybrid factor reasonable (e.g., Store_01 = 5.5%)

**Risk:** Allocation factors may heavily favor historical data
**Mitigation:** 30% attribute weight provides flexibility for new trends

---

### Task 7: Parameter-Aware Safety Stock Adjustment
**Estimated Time:** 3 hours
**Dependencies:** Task 1, Task 4
**Priority:** High

**Subtasks:**
- [ ] Create `backend/app/agents/demand_reasoning.py`
- [ ] Implement safety stock adjustment logic
  - Default: 20% (weekly replenishment)
  - No replenishment: 25% (increased buffer)
  - Bi-weekly replenishment: 22% (moderate)
- [ ] Add LLM reasoning for safety stock decision
  - Prompt LLM to explain adjustment
  - Log reasoning to database
- [ ] Return safety stock multiplier with forecast
- [ ] Unit tests for safety stock logic

**Code Snippet - Safety Stock Adjustment:**
```python
async def calculate_safety_stock_multiplier(
    parameters: SeasonParameters,
    llm_client: Any
) -> Tuple[float, str]:
    """
    Calculate safety stock multiplier based on replenishment strategy

    Args:
        parameters: Season parameters
        llm_client: OpenAI client for LLM reasoning

    Returns:
        Tuple of (multiplier, reasoning)
        Example: (1.25, "No replenishment means...")
    """
    # Deterministic base logic
    if parameters.replenishment_strategy == "none":
        base_multiplier = 1.25  # 25% safety stock
    elif parameters.replenishment_strategy == "weekly":
        base_multiplier = 1.20  # 20% safety stock (default)
    elif parameters.replenishment_strategy == "bi-weekly":
        base_multiplier = 1.22  # 22% safety stock
    else:
        base_multiplier = 1.20  # Default fallback

    # LLM reasoning (for logging/explanation)
    prompt = f"""
    You are a demand forecasting agent. The user has configured:
    - Replenishment strategy: {parameters.replenishment_strategy}
    - Forecast horizon: {parameters.forecast_horizon_weeks} weeks
    - DC holdback: {parameters.dc_holdback_percentage * 100}%

    Explain why safety stock of {int((base_multiplier - 1) * 100)}% is appropriate.
    Provide a 1-2 sentence reasoning.
    """

    response = await llm_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=150
    )

    reasoning = response.choices[0].message.content.strip()

    return base_multiplier, reasoning
```

**Validation:**
- Safety stock adjusts correctly per replenishment strategy
- LLM reasoning is coherent and accurate
- Reasoning logged to database

**Risk:** LLM reasoning may be inconsistent
**Mitigation:** Use deterministic base logic, LLM only for explanation

---

### Task 8: Structured Forecast Output & Handoff Object
**Estimated Time:** 4 hours
**Dependencies:** Task 4, Task 5, Task 6, Task 7
**Priority:** Critical

**Subtasks:**
- [ ] Create `backend/app/schemas/forecast.py`
- [ ] Define `ForecastResult` Pydantic model
  - Total season forecast
  - Weekly curve (list of weekly predictions)
  - Cluster distribution (Fashion_Forward %, Mainstream %, Value_Conscious %)
  - Store allocation factors
  - Safety stock multiplier
  - Ensemble details (Prophet, ARIMA, agreement %)
  - LLM reasoning
- [ ] Implement forecast object builder
- [ ] Test JSON serialization for handoff
- [ ] Integration test with Orchestrator handoff

**Code Snippet - Forecast Output Schema:**
```python
from pydantic import BaseModel, Field
from typing import List, Dict, Optional

class ClusterDistribution(BaseModel):
    cluster_name: str = Field(..., description="Cluster name")
    percentage: float = Field(..., description="% of total forecast", ge=0, le=1)
    units: int = Field(..., description="Absolute units for cluster")

class StoreAllocation(BaseModel):
    store_id: str
    cluster_name: str
    allocation_factor: float = Field(..., description="Within-cluster allocation %")
    season_total_units: int = Field(..., description="Total units for season")

class ForecastResult(BaseModel):
    """Structured forecast output for Demand Agent"""

    # Ensemble forecast
    method: str = Field(default="ensemble", description="prophet, arima, or ensemble")
    total_forecast: int = Field(..., description="Total season forecast (units)")
    weekly_curve: List[int] = Field(..., description="Weekly predictions [week 1, week 2, ...]")

    # Clustering & allocation
    cluster_distribution: List[ClusterDistribution] = Field(
        ...,
        description="Distribution across 3 clusters"
    )
    store_allocations: List[StoreAllocation] = Field(
        ...,
        description="Allocation factors for all stores"
    )

    # Parameter-driven adjustments
    safety_stock_multiplier: float = Field(
        ...,
        description="Safety stock % (1.20 = 20%, 1.25 = 25%)"
    )
    safety_stock_reasoning: str = Field(
        ...,
        description="LLM explanation of safety stock adjustment"
    )

    # Model details
    prophet_forecast: Optional[int] = Field(None, description="Prophet result")
    arima_forecast: Optional[int] = Field(None, description="ARIMA result")
    model_agreement_pct: Optional[float] = Field(
        None,
        description="Agreement between models (%)"
    )

    # Clustering quality
    silhouette_score: float = Field(..., description="Clustering quality metric")

    # Metadata
    forecast_timestamp: str
    parameters_used: Dict = Field(..., description="Parameters that drove this forecast")

    class Config:
        json_schema_extra = {
            "example": {
                "method": "ensemble",
                "total_forecast": 8000,
                "weekly_curve": [650, 680, 720, 740, 760, 730, 710, 680, 650, 620, 580, 480],
                "cluster_distribution": [
                    {"cluster_name": "Fashion_Forward", "percentage": 0.40, "units": 3200},
                    {"cluster_name": "Mainstream", "percentage": 0.35, "units": 2800},
                    {"cluster_name": "Value_Conscious", "percentage": 0.25, "units": 2000}
                ],
                "store_allocations": [
                    {"store_id": "Store_01", "cluster_name": "Fashion_Forward", "allocation_factor": 0.055, "season_total_units": 176}
                ],
                "safety_stock_multiplier": 1.25,
                "safety_stock_reasoning": "No replenishment configured, using 25% buffer",
                "prophet_forecast": 8200,
                "arima_forecast": 7800,
                "model_agreement_pct": 95.2,
                "silhouette_score": 0.52
            }
        }
```

**Validation:**
- All fields populate correctly
- JSON serializes without errors
- Orchestrator can receive and parse forecast object
- Store allocations sum correctly

**Risk:** Large forecast object may cause serialization issues
**Mitigation:** Test with 50 stores, optimize JSON structure if needed

---

### Task 9: Demand Agent Main Logic Integration
**Estimated Time:** 5 hours
**Dependencies:** All previous tasks
**Priority:** Critical

**Subtasks:**
- [ ] Implement `demand_agent_main()` function
- [ ] Orchestrate all components:
  1. Receive parameter context from Orchestrator
  2. Load historical data from database
  3. Run LLM reasoning for parameter interpretation
  4. Calculate safety stock multiplier
  5. Run ensemble forecast (Prophet + ARIMA in parallel)
  6. Run K-means clustering
  7. Calculate cluster distribution
  8. Calculate store allocation factors
  9. Build structured forecast object
  10. Return to Orchestrator for handoff to Inventory Agent
- [ ] Add comprehensive error handling
- [ ] Add logging for all major steps
- [ ] Add WebSocket status updates

**Code Snippet - Main Agent Logic:**
```python
async def demand_agent_main(
    context: DemandAgentContext,
    llm_client: Any,
    websocket: Any
) -> ForecastResult:
    """
    Main Demand Agent execution logic

    Args:
        context: Agent context with parameters and historical data
        llm_client: OpenAI client
        websocket: WebSocket for status updates

    Returns:
        ForecastResult object for handoff to Inventory Agent
    """
    params = context.parameters

    # Step 1: LLM reasoning for parameter interpretation
    await websocket.send_json({
        "type": "agent_status",
        "agent": "demand",
        "status": "Interpreting parameters"
    })

    safety_stock_multiplier, safety_reasoning = await calculate_safety_stock_multiplier(
        params,
        llm_client
    )

    # Step 2: Ensemble forecast (Prophet + ARIMA in parallel)
    await websocket.send_json({
        "type": "agent_status",
        "agent": "demand",
        "status": "Running ensemble forecast (Prophet + ARIMA)"
    })

    ensemble_result = await ensemble_forecast_parallel(
        context.historical_data,
        params.forecast_horizon_weeks,
        context.category_id
    )

    # Step 3: K-means clustering
    await websocket.send_json({
        "type": "agent_status",
        "agent": "demand",
        "status": "Clustering stores (K-means with 7 features)"
    })

    clustering_result = kmeans_store_clustering(context.stores_df, n_clusters=3)

    # Step 4: Cluster distribution
    cluster_dist = calculate_cluster_distribution(
        ensemble_result['total_forecast'],
        clustering_result,
        context.historical_data
    )

    # Step 5: Store allocation factors
    await websocket.send_json({
        "type": "agent_status",
        "agent": "demand",
        "status": "Calculating store allocation factors"
    })

    store_allocations_df = calculate_store_allocation_factors(
        context.stores_df,
        clustering_result['cluster_names'],
        context.historical_data
    )

    # Step 6: Build structured forecast object
    forecast_result = ForecastResult(
        method=ensemble_result['method'],
        total_forecast=ensemble_result['total_forecast'],
        weekly_curve=ensemble_result['weekly_predictions'],
        cluster_distribution=cluster_dist,
        store_allocations=store_allocations_df.to_dict('records'),
        safety_stock_multiplier=safety_stock_multiplier,
        safety_stock_reasoning=safety_reasoning,
        prophet_forecast=ensemble_result.get('prophet_result', {}).get('total_forecast'),
        arima_forecast=ensemble_result.get('arima_result', {}).get('total_forecast'),
        model_agreement_pct=ensemble_result.get('model_agreement_pct'),
        silhouette_score=clustering_result['silhouette_score'],
        forecast_timestamp=datetime.now().isoformat(),
        parameters_used=params.dict()
    )

    await websocket.send_json({
        "type": "agent_status",
        "agent": "demand",
        "status": "Forecast complete, handing off to Inventory Agent"
    })

    return forecast_result
```

**Validation:**
- All 10 steps execute successfully
- WebSocket updates sent at each step
- Forecast object returned correctly
- Execution time <10 seconds

**Risk:** Any step failure breaks entire workflow
**Mitigation:** Comprehensive error handling, log all errors, fail gracefully

---

### Task 10: Re-Forecast Logic (Variance-Triggered)
**Estimated Time:** 4 hours
**Dependencies:** Task 9
**Priority:** High

**Subtasks:**
- [ ] Implement re-forecast logic for variance triggers
- [ ] Receive variance context from Orchestrator
  - Actual sales to date
  - Variance percentage
  - Week number
- [ ] Adjust historical data with actuals
- [ ] Re-run ensemble forecast for remaining weeks
- [ ] Return updated forecast object
- [ ] Unit tests for re-forecast logic

**Code Snippet - Re-Forecast Logic:**
```python
async def demand_agent_reforecast(
    context: DemandAgentContext,
    llm_client: Any,
    websocket: Any
) -> ForecastResult:
    """
    Re-forecast remaining weeks after variance trigger

    Args:
        context: Includes variance_info with actuals and current week

    Returns:
        Updated ForecastResult for remaining weeks
    """
    params = context.parameters
    variance_info = context.variance_info

    await websocket.send_json({
        "type": "agent_status",
        "agent": "demand",
        "status": f"Re-forecasting due to {variance_info.variance_pct}% variance at Week {variance_info.week_number}"
    })

    # Adjust historical data with actuals
    adjusted_history = pd.concat([
        context.historical_data,
        context.actuals  # Actual sales to date
    ])

    # Calculate remaining weeks
    weeks_elapsed = variance_info.week_number
    weeks_remaining = params.forecast_horizon_weeks - weeks_elapsed

    # Re-run ensemble forecast for remaining weeks only
    ensemble_result = await ensemble_forecast_parallel(
        adjusted_history,
        weeks_remaining,
        context.category_id
    )

    # Recalculate total forecast (already sold + remaining forecast)
    total_sold = context.actuals['units_sold'].sum()
    total_forecast = total_sold + ensemble_result['total_forecast']

    # Update weekly curve (replace remaining weeks)
    original_curve = context.original_forecast.weekly_curve
    updated_curve = original_curve[:weeks_elapsed] + ensemble_result['weekly_predictions']

    # Rebuild forecast object with updated predictions
    forecast_result = ForecastResult(
        method=ensemble_result['method'],
        total_forecast=total_forecast,
        weekly_curve=updated_curve,
        # Keep original clustering/allocations (don't re-cluster)
        cluster_distribution=context.original_forecast.cluster_distribution,
        store_allocations=context.original_forecast.store_allocations,
        safety_stock_multiplier=context.original_forecast.safety_stock_multiplier,
        safety_stock_reasoning=f"Re-forecast triggered at Week {weeks_elapsed}",
        prophet_forecast=ensemble_result.get('prophet_result', {}).get('total_forecast'),
        arima_forecast=ensemble_result.get('arima_result', {}).get('total_forecast'),
        model_agreement_pct=ensemble_result.get('model_agreement_pct'),
        silhouette_score=context.original_forecast.silhouette_score,  # Keep original
        forecast_timestamp=datetime.now().isoformat(),
        parameters_used=params.dict()
    )

    await websocket.send_json({
        "type": "agent_status",
        "agent": "demand",
        "status": "Re-forecast complete"
    })

    return forecast_result
```

**Validation:**
- Re-forecast uses actual sales to date
- Remaining weeks forecasted correctly
- Updated forecast object returned
- Original clustering preserved (no re-clustering)

**Risk:** Re-forecast may worsen MAPE if variance was due to noise
**Mitigation:** 20% threshold reduces false positives

---

### Task 11: Integration Testing with Orchestrator
**Estimated Time:** 4 hours
**Dependencies:** Task 9, Phase 4 Orchestrator
**Priority:** Critical

**Subtasks:**
- [ ] Create integration test suite
- [ ] Test 1: Zara parameters (no replenishment)
  - Verify 25% safety stock used
  - Verify forecast completes successfully
  - Verify handoff to Inventory Agent
- [ ] Test 2: Standard retail parameters (weekly replenishment)
  - Verify 20% safety stock used
  - Verify forecast completes successfully
- [ ] Test 3: Luxury parameters (no markdowns)
  - Verify markdown parameters ignored
  - Verify forecast completes
- [ ] Test 4: Variance-triggered re-forecast
  - Simulate >20% variance at Week 5
  - Verify re-forecast triggered
  - Verify remaining weeks re-forecasted
- [ ] Test 5: Prophet failure fallback
  - Mock Prophet to fail
  - Verify ARIMA-only fallback
- [ ] Test 6: End-to-end workflow
  - Phase 0: Parameter extraction
  - Phase 1: Orchestrator → Demand Agent
  - Phase 1: Demand Agent → Inventory Agent (handoff)

**Validation:**
- All 6 tests pass
- Handoff to Inventory Agent successful
- No errors in logs
- Execution time <10 seconds per test

**Risk:** Integration issues between Orchestrator and Demand Agent
**Mitigation:** Use mocked Inventory Agent for Phase 5 testing

---

### Task 12: Performance Optimization
**Estimated Time:** 3 hours
**Dependencies:** Task 9, Task 11
**Priority:** Medium

**Subtasks:**
- [ ] Profile forecast execution time
  - Prophet execution time
  - ARIMA execution time
  - Clustering execution time
  - Total workflow time
- [ ] Optimize slow components
  - Cache StandardScaler for clustering
  - Optimize Pandas operations
  - Parallelize where possible
- [ ] Target: <10 seconds total execution
- [ ] Add performance metrics to logs

**Validation:**
- Total execution time <10 seconds
- No performance regressions
- Metrics logged correctly

**Risk:** Prophet/ARIMA may be inherently slow for large datasets
**Mitigation:** Acceptable for MVP with <2 years historical data

---

### Task 13: Documentation & Code Quality
**Estimated Time:** 3 hours
**Dependencies:** All previous tasks
**Priority:** Medium

**Subtasks:**
- [ ] Document Demand Agent logic (docstrings)
- [ ] Add inline code comments for complex sections
- [ ] Create `backend/app/agents/README_DEMAND.md`
  - Ensemble forecasting methodology
  - K-means clustering approach
  - Allocation factor calculation
  - Parameter interpretation logic
- [ ] Add type hints to all functions
- [ ] Run mypy type checking
- [ ] Run Ruff linting and formatting
- [ ] Update main README with Demand Agent details

**Validation:**
- All functions have docstrings
- mypy passes with no errors
- Ruff passes with no warnings
- README complete and accurate

**Risk:** Documentation may become outdated
**Mitigation:** Keep documentation close to code (docstrings)

---

## Validation Checkpoints

### Checkpoint 1: Mid-Phase (40% complete)
**Tasks 1-5 Complete**
- [ ] Demand Agent foundation created
- [ ] Ensemble forecasting (Prophet + ARIMA) working
- [ ] K-means clustering functional
- [ ] Clustering quality metrics acceptable (silhouette >0.4)
- [ ] Parameter context received correctly

**Status:** Not Started

---

### Checkpoint 2: Pre-Completion (80% complete)
**Tasks 1-10 Complete**
- [ ] All ML components integrated
- [ ] Structured forecast object returned
- [ ] Safety stock adjustment working
- [ ] Store allocation factors calculated
- [ ] Re-forecast logic functional
- [ ] WebSocket status updates working

**Status:** Not Started

---

### Checkpoint 3: Final (100% complete)
**All 13 Tasks Complete**
- [ ] Integration tests passing (6/6)
- [ ] End-to-end workflow test passing (Orchestrator → Demand → Inventory handoff)
- [ ] Forecast MAPE <20% on Phase 1 CSV data
- [ ] Performance target met (<10 seconds)
- [ ] Documentation complete
- [ ] Ready for handoff to Phase 6 (Inventory Agent)

**Status:** Not Started

---

## Risk Register

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Prophet requires >2 years historical data | Medium | High | Use Phase 1 CSVs with 52+ weeks, fallback to ARIMA if Prophet fails |
| ARIMA fails on non-stationary data | Low | Medium | auto_arima handles differencing automatically |
| Low clustering quality (silhouette <0.4) | Medium | Medium | Validate with Phase 1 CSV store data, adjust K if needed |
| Low model agreement (<80%) | Medium | Low | Log warnings, proceed with ensemble average |
| Forecast execution time >10 seconds | Medium | Low | Optimize Prophet/ARIMA parameters, profile bottlenecks |
| Parameter interpretation inconsistency | Low | Medium | Use deterministic base logic, LLM only for explanation |
| Integration issues with Orchestrator | Low | High | Comprehensive integration tests, mock Inventory Agent |

---

## Dependencies

### Upstream Dependencies (Must Complete First)
- **Phase 4 (Orchestrator Agent)**: Orchestrator must be functional to test handoffs

### Downstream Dependencies (Blocked Until Phase 5 Complete)
- **Phase 6 (Inventory Agent)**: Needs forecast object structure
- **Phase 7 (Pricing Agent)**: Needs forecast + allocation data

### External Dependencies
- Phase 1 CSV historical data (50 stores, 52+ weeks)
- Azure OpenAI API access (gpt-4o-mini)
- Python libraries: Prophet, pmdarima, scikit-learn

---

## Handoff Notes for Phase 6 (Inventory Agent)

**What Phase 6 needs to know:**
- Demand Agent returns structured `ForecastResult` object
- Forecast includes: total forecast, weekly curve, cluster distribution, store allocations, safety stock multiplier
- Safety stock adjusted based on replenishment strategy (20%-25%)
- Clustering creates 3 clusters: Fashion_Forward, Mainstream, Value_Conscious
- Store allocation factors are hybrid: 70% historical + 30% attributes
- Ensemble forecast averages Prophet + ARIMA (both run in parallel)
- Re-forecast logic updates remaining weeks when variance >20%

**Files/APIs available:**
- Main agent: `backend/app/agents/demand.py`
- Forecast schema: `backend/app/schemas/forecast.py`
- ML modules: `backend/app/ml/{prophet_forecast.py, arima_forecast.py, ensemble_forecast.py, clustering.py, allocation.py}`
- Agent reasoning: `backend/app/agents/demand_reasoning.py`

**Recommendations for Phase 6:**
1. Use `forecast_result.total_forecast × forecast_result.safety_stock_multiplier` for manufacturing order
2. Use `forecast_result.store_allocations` for store-level allocations
3. Use `forecast_result.cluster_distribution` for cluster-level reporting
4. Test with both Zara parameters (25% safety stock) and standard retail (20% safety stock)
5. Reference `process_workflow_v3.3.md` for complete Inventory Agent behavior

---

## Success Criteria

**Phase 5 is complete when:**
1. ✅ Ensemble forecasting (Prophet + ARIMA) functional and accurate (MAPE <20%)
2. ✅ K-means clustering produces 3 high-quality clusters (silhouette >0.4)
3. ✅ Parameter-aware safety stock adjustment working (20%-25%)
4. ✅ Store allocation factors calculated correctly (hybrid 70/30)
5. ✅ Structured forecast object returned to Orchestrator
6. ✅ Re-forecast logic functional for variance triggers
7. ✅ Integration tests passing (6/6)
8. ✅ End-to-end workflow test passing (Orchestrator → Demand → Inventory)
9. ✅ Performance target met (<10 seconds execution)
10. ✅ Documentation complete (README, docstrings, type hints)

---

**Created:** 2025-10-17
**Last Updated:** 2025-10-17
**Status:** Phase 5 Not Started
**Previous Phase:** Phase 4 (Orchestrator Agent) - Complete
**Next Phase:** Phase 6 (Inventory Agent)
