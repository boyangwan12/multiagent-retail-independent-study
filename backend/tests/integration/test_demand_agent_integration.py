"""End-to-end integration tests for DemandAgent with EnsembleForecaster."""

import pytest
import pandas as pd
import numpy as np
import sys
import os
from datetime import datetime, date

# Add backend to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from app.agents.demand_agent import DemandAgent
from app.ml.ensemble_forecaster import ForecastingError
from app.schemas.workflow_schemas import SeasonParameters


@pytest.fixture
def historical_data_52_weeks():
    """Generate 52 weeks of synthetic historical sales data."""
    dates = pd.date_range(start='2023-01-01', periods=52, freq='W')
    # Generate realistic sales data with seasonality
    base_demand = 100
    seasonal_factor = 20 * np.sin(np.arange(52) * 2 * np.pi / 52)
    noise = np.random.normal(0, 10, 52)
    quantity = np.maximum(base_demand + seasonal_factor + noise, 10).astype(int)

    return pd.DataFrame({
        'date': dates,
        'quantity_sold': quantity
    })


@pytest.fixture
def season_parameters():
    """Create SeasonParameters for testing."""
    return SeasonParameters(
        forecast_horizon_weeks=12,
        season_start_date=date(2025, 3, 1),
        season_end_date=date(2025, 5, 23),
        replenishment_strategy="weekly",
        dc_holdback_percentage=0.15,
        markdown_checkpoint_week=6,
        markdown_threshold=0.60
    )


class TestDemandAgentInitialization:
    """Test DemandAgent initialization."""

    def test_init_without_config(self):
        """Test initialization without AgentConfig."""
        agent = DemandAgent()
        assert agent.config is None
        assert agent.client is None
        assert agent.forecaster is not None

    def test_init_with_config(self):
        """Test initialization with AgentConfig (would be tested with real config)."""
        # For Phase 6, we test without config
        agent = DemandAgent()
        assert agent is not None


class TestDemandAgentExecute:
    """Test DemandAgent execute() method."""

    @pytest.mark.asyncio
    async def test_execute_with_valid_context(self, historical_data_52_weeks, season_parameters):
        """Test execute() with valid context."""
        agent = DemandAgent()

        result = await agent.execute(
            category_id="womens_dresses",
            parameters=season_parameters,
            historical_data=historical_data_52_weeks
        )

        # Verify output structure
        assert "total_demand" in result
        assert "forecast_by_week" in result
        assert "safety_stock_pct" in result
        assert "confidence" in result
        assert "model_used" in result

        # Verify data types
        assert isinstance(result["total_demand"], int)
        assert isinstance(result["forecast_by_week"], list)
        assert isinstance(result["safety_stock_pct"], float)
        assert isinstance(result["confidence"], float)
        assert isinstance(result["model_used"], str)

        # Verify value ranges
        assert result["total_demand"] > 0
        assert len(result["forecast_by_week"]) == 12
        assert 0.1 <= result["safety_stock_pct"] <= 0.5
        assert 0.0 <= result["confidence"] <= 1.0
        assert result["model_used"] in ["prophet_arima_ensemble", "prophet", "arima"]

    @pytest.mark.asyncio
    async def test_execute_forecast_by_week_sum(self, historical_data_52_weeks, season_parameters):
        """Test that total_demand equals sum of forecast_by_week."""
        agent = DemandAgent()

        result = await agent.execute(
            category_id="womens_dresses",
            parameters=season_parameters,
            historical_data=historical_data_52_weeks
        )

        expected_total = sum(result["forecast_by_week"])
        assert result["total_demand"] == expected_total

    @pytest.mark.asyncio
    async def test_execute_with_different_horizons(self, historical_data_52_weeks):
        """Test execute() with different forecast horizons."""
        agent = DemandAgent()

        # Test 4-week horizon
        params_4w = SeasonParameters(
            forecast_horizon_weeks=4,
            season_start_date=date(2025, 3, 1),
            season_end_date=date(2025, 3, 29),
            replenishment_strategy="weekly",
            dc_holdback_percentage=0.15,
            markdown_checkpoint_week=None,
            markdown_threshold=None
        )

        result_4w = await agent.execute(
            category_id="womens_dresses",
            parameters=params_4w,
            historical_data=historical_data_52_weeks
        )

        assert len(result_4w["forecast_by_week"]) == 4

        # Test 26-week horizon
        params_26w = SeasonParameters(
            forecast_horizon_weeks=26,
            season_start_date=date(2025, 3, 1),
            season_end_date=date(2025, 8, 30),
            replenishment_strategy="weekly",
            dc_holdback_percentage=0.15,
            markdown_checkpoint_week=None,
            markdown_threshold=None
        )

        result_26w = await agent.execute(
            category_id="womens_dresses",
            parameters=params_26w,
            historical_data=historical_data_52_weeks
        )

        assert len(result_26w["forecast_by_week"]) == 26

    @pytest.mark.asyncio
    async def test_execute_safety_stock_inverse_confidence(self, historical_data_52_weeks, season_parameters):
        """Test that safety_stock_pct is inverse of confidence."""
        agent = DemandAgent()

        result = await agent.execute(
            category_id="womens_dresses",
            parameters=season_parameters,
            historical_data=historical_data_52_weeks
        )

        # Safety stock should be roughly 1.0 - confidence
        # (with clamping to [0.1, 0.5])
        expected_safety_stock = 1.0 - result["confidence"]
        expected_safety_stock = max(0.1, min(0.5, expected_safety_stock))

        assert result["safety_stock_pct"] == expected_safety_stock

    @pytest.mark.asyncio
    async def test_execute_with_insufficient_data(self, season_parameters):
        """Test execute() with insufficient historical data."""
        agent = DemandAgent()

        insufficient_data = pd.DataFrame({
            'date': pd.date_range(start='2023-01-01', periods=10, freq='W'),
            'quantity_sold': [100] * 10
        })

        with pytest.raises(ForecastingError):
            await agent.execute(
                category_id="womens_dresses",
                parameters=season_parameters,
                historical_data=insufficient_data
            )


class TestDemandAgentOutputContract:
    """Test DemandAgent output matches expected contract."""

    @pytest.mark.asyncio
    async def test_output_structure(self, historical_data_52_weeks, season_parameters):
        """Test output structure matches DemandAgentOutput contract."""
        agent = DemandAgent()

        result = await agent.execute(
            category_id="womens_dresses",
            parameters=season_parameters,
            historical_data=historical_data_52_weeks
        )

        # Required fields as per contract
        required_fields = [
            "total_demand",
            "forecast_by_week",
            "safety_stock_pct",
            "confidence",
            "model_used"
        ]

        for field in required_fields:
            assert field in result, f"Missing required field: {field}"

    @pytest.mark.asyncio
    async def test_output_all_predictions_positive(self, historical_data_52_weeks, season_parameters):
        """Test that all predictions are non-negative."""
        agent = DemandAgent()

        result = await agent.execute(
            category_id="womens_dresses",
            parameters=season_parameters,
            historical_data=historical_data_52_weeks
        )

        assert all(p >= 0 for p in result["forecast_by_week"]), \
            "All predictions must be non-negative"

    @pytest.mark.asyncio
    async def test_output_reasonable_confidence(self, historical_data_52_weeks, season_parameters):
        """Test that confidence score is in reasonable range."""
        agent = DemandAgent()

        result = await agent.execute(
            category_id="womens_dresses",
            parameters=season_parameters,
            historical_data=historical_data_52_weeks
        )

        # Confidence should be between 0.0 and 1.0
        assert 0.0 <= result["confidence"] <= 1.0
        # For synthetic data with 52 weeks of history, confidence should be decent
        assert result["confidence"] > 0.3, "Expected reasonable confidence for 52-week history"


class TestDemandAgentTools:
    """Test DemandAgent tool methods."""

    def test_get_tools(self):
        """Test get_tools() returns expected tool definitions."""
        agent = DemandAgent()
        tools = agent.get_tools()

        assert isinstance(tools, list)
        assert len(tools) == 3  # forecast_demand, cluster_stores, allocate_to_stores

        tool_names = [tool["function"]["name"] for tool in tools]
        assert "forecast_demand" in tool_names
        assert "cluster_stores" in tool_names
        assert "allocate_to_stores" in tool_names

    @pytest.mark.asyncio
    async def test_cluster_stores(self):
        """Test cluster_stores() method."""
        agent = DemandAgent()

        result = await agent.cluster_stores(
            category_id="womens_dresses",
            total_season_demand=8000
        )

        assert "cluster_id" in result
        assert "distribution" in result
        assert "store_assignments" in result

        # Verify distribution sums to 1.0
        dist_sum = sum(result["distribution"].values())
        assert abs(dist_sum - 1.0) < 0.01

    @pytest.mark.asyncio
    async def test_allocate_to_stores(self):
        """Test allocate_to_stores() method."""
        agent = DemandAgent()

        result = await agent.allocate_to_stores(
            forecast_id="f_test_123",
            cluster_distribution={"A": 0.5, "B": 0.3, "C": 0.2}
        )

        assert "allocation_id" in result
        assert "store_allocations" in result

        # Verify each allocation has required fields
        for allocation in result["store_allocations"]:
            assert "store_id" in allocation
            assert "units" in allocation
            assert "cluster" in allocation

    def test_get_instructions(self):
        """Test get_instructions() returns system prompt."""
        agent = DemandAgent()
        instructions = agent.get_instructions()

        assert isinstance(instructions, str)
        assert len(instructions) > 0
        assert "Demand Agent" in instructions
        assert "Prophet" in instructions or "forecast" in instructions


class TestDemandAgentMultipleCalls:
    """Test DemandAgent behavior across multiple calls."""

    @pytest.mark.asyncio
    async def test_sequential_forecasts(self, historical_data_52_weeks, season_parameters):
        """Test that agent produces consistent results across multiple calls."""
        agent = DemandAgent()

        result1 = await agent.execute(
            category_id="womens_dresses",
            parameters=season_parameters,
            historical_data=historical_data_52_weeks
        )

        result2 = await agent.execute(
            category_id="womens_dresses",
            parameters=season_parameters,
            historical_data=historical_data_52_weeks
        )

        # Results should be identical (same data, same forecaster state)
        assert result1["total_demand"] == result2["total_demand"]
        assert result1["confidence"] == result2["confidence"]
        assert result1["model_used"] == result2["model_used"]

    @pytest.mark.asyncio
    async def test_different_categories(self, historical_data_52_weeks, season_parameters):
        """Test agent with different category IDs."""
        agent = DemandAgent()

        categories = ["womens_dresses", "mens_shirts", "kids_apparel"]

        for category in categories:
            result = await agent.execute(
                category_id=category,
                parameters=season_parameters,
                historical_data=historical_data_52_weeks
            )

            assert result is not None
            assert result["total_demand"] > 0
            assert len(result["forecast_by_week"]) == 12


class TestDemandAgentErrorHandling:
    """Test DemandAgent error handling."""

    @pytest.mark.asyncio
    async def test_invalid_historical_data_columns(self, season_parameters):
        """Test error handling for invalid data columns."""
        agent = DemandAgent()

        invalid_data = pd.DataFrame({
            'date': pd.date_range(start='2023-01-01', periods=52, freq='W'),
            'invalid_column': [100] * 52
        })

        with pytest.raises(ForecastingError):
            await agent.execute(
                category_id="womens_dresses",
                parameters=season_parameters,
                historical_data=invalid_data
            )

    @pytest.mark.asyncio
    async def test_empty_historical_data(self, season_parameters):
        """Test error handling for empty historical data."""
        agent = DemandAgent()

        empty_data = pd.DataFrame({
            'date': [],
            'quantity_sold': []
        })

        with pytest.raises(ForecastingError):
            await agent.execute(
                category_id="womens_dresses",
                parameters=season_parameters,
                historical_data=empty_data
            )
