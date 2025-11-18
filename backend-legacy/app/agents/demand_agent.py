"""Demand Agent for forecasting and demand analysis using Prophet + ARIMA ensemble."""

from typing import Any, Dict, List, Optional
from app.agents.config import AgentConfig
from app.ml.ensemble_forecaster import EnsembleForecaster, ForecastingError
from app.schemas.workflow_schemas import SeasonParameters
import pandas as pd
import logging

logger = logging.getLogger("fashion_forecast")


class DemandAgent:
    """
    Demand Agent forecasts demand using Prophet + ARIMA ensemble.

    Integrates with Phase 5 orchestrator to consume DemandAgentContext and
    produce forecast_result output. Uses EnsembleForecaster internally for
    accurate, model-agnostic demand forecasting.

    Phase 6 Implementation: Uses real EnsembleForecaster for actual forecasting
    Phase 8 Implementation: Will integrate with OpenAI Agents SDK
    """

    def __init__(self, config: Optional[AgentConfig] = None):
        """
        Initialize Demand Agent.

        Args:
            config: Agent configuration with OpenAI client (optional for Phase 6)
        """
        self.config = config
        self.client = config.openai_client if config else None
        self.forecaster = EnsembleForecaster()
        logger.info("DemandAgent initialized with EnsembleForecaster")

    async def execute(
        self,
        category_id: str,
        parameters: SeasonParameters,
        historical_data: pd.DataFrame
    ) -> Dict[str, Any]:
        """
        Execute demand forecasting using ensemble model.

        Args:
            category_id: Product category identifier
            parameters: Season parameters with forecast horizon
            historical_data: DataFrame with historical sales data

        Returns:
            Dictionary with forecast results:
            - total_demand: int (sum of weekly forecasts)
            - forecast_by_week: List[int] (weekly predictions)
            - safety_stock_pct: float (0.1-0.5 range)
            - confidence: float (0.0-1.0)
            - model_used: str ("prophet_arima_ensemble" | "prophet" | "arima")

        Raises:
            ForecastingError: If both models fail
        """
        logger.info(
            f"DemandAgent executing forecast for {category_id} "
            f"({parameters.forecast_horizon_weeks} weeks)"
        )

        try:
            # Train ensemble forecaster
            logger.info("Training ensemble forecaster...")
            self.forecaster.train(historical_data)

            # Generate forecast
            logger.info(f"Generating {parameters.forecast_horizon_weeks}-period forecast...")
            forecast_result = self.forecaster.forecast(parameters.forecast_horizon_weeks)

            # Calculate total demand
            total_demand = int(sum(forecast_result['predictions']))

            # Calculate safety stock percentage
            # High confidence (0.9) → Low safety stock (0.1 = 10%)
            # Low confidence (0.5) → High safety stock (0.5 = 50%)
            safety_stock_pct = 1.0 - forecast_result['confidence']
            # Clamp to reasonable range [0.1, 0.5]
            safety_stock_pct = max(0.1, min(0.5, safety_stock_pct))

            # Format output
            output = {
                "total_demand": total_demand,
                "forecast_by_week": forecast_result['predictions'],
                "safety_stock_pct": round(safety_stock_pct, 2),
                "confidence": round(forecast_result['confidence'], 2),
                "model_used": forecast_result['model_used']
            }

            logger.info(
                f"Forecast complete: total_demand={total_demand}, "
                f"confidence={output['confidence']}, model={output['model_used']}"
            )

            return output

        except ForecastingError as e:
            logger.error(f"Forecasting failed: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during forecasting: {e}")
            raise ForecastingError(f"Demand forecasting failed: {str(e)}")

    def get_tools(self) -> List[Dict[str, Any]]:
        """
        Get tool definitions for OpenAI function calling (Phase 8).

        Returns:
            List of tool definitions
        """
        return [
            {
                "type": "function",
                "function": {
                    "name": "forecast_demand",
                    "description": "Generate weekly demand forecast using Prophet + ARIMA ensemble",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "category_id": {
                                "type": "string",
                                "description": "Product category identifier (e.g., 'womens_dresses')"
                            },
                            "forecast_horizon_weeks": {
                                "type": "integer",
                                "description": "Number of weeks to forecast (e.g., 12)"
                            }
                        },
                        "required": ["category_id", "forecast_horizon_weeks"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "cluster_stores",
                    "description": "Cluster stores by performance tier (A/B/C) based on historical sales",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "category_id": {
                                "type": "string",
                                "description": "Product category identifier"
                            },
                            "total_season_demand": {
                                "type": "integer",
                                "description": "Total demand across all weeks"
                            }
                        },
                        "required": ["category_id", "total_season_demand"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "allocate_to_stores",
                    "description": "Allocate forecasted units to stores based on cluster distribution",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "forecast_id": {
                                "type": "string",
                                "description": "Forecast identifier"
                            },
                            "cluster_distribution": {
                                "type": "object",
                                "description": "Demand distribution across store clusters (A/B/C percentages)"
                            }
                        },
                        "required": ["forecast_id", "cluster_distribution"]
                    }
                }
            }
        ]

    async def cluster_stores(
        self,
        category_id: str,
        total_season_demand: int
    ) -> Dict[str, Any]:
        """
        Tool: Cluster stores by performance tier (A/B/C).

        Args:
            category_id: Product category identifier
            total_season_demand: Total demand across all weeks

        Returns:
            Store clusters with distribution percentages
        """
        logger.info(f"Clustering stores for {category_id} (demand: {total_season_demand})")

        # TODO (Phase 7): Implement actual clustering logic using K-means
        # Placeholder implementation
        return {
            "cluster_id": f"c_{category_id}",
            "category_id": category_id,
            "distribution": {
                "A": 0.50,  # 50% to A stores (high performers)
                "B": 0.30,  # 30% to B stores (medium performers)
                "C": 0.20   # 20% to C stores (lower performers)
            },
            "store_assignments": {
                "A": ["store_001", "store_002"],
                "B": ["store_003", "store_004"],
                "C": ["store_005"]
            }
        }

    async def allocate_to_stores(
        self,
        forecast_id: str,
        cluster_distribution: Dict[str, float]
    ) -> Dict[str, Any]:
        """
        Tool: Allocate forecasted units to stores based on cluster distribution.

        Args:
            forecast_id: Forecast identifier
            cluster_distribution: Demand distribution across clusters

        Returns:
            Store allocations
        """
        logger.info(f"Allocating units for forecast {forecast_id}")

        # TODO (Phase 7): Implement actual allocation logic
        # Placeholder implementation
        return {
            "allocation_id": f"a_{forecast_id}",
            "forecast_id": forecast_id,
            "store_allocations": [
                {"store_id": "store_001", "units": 2000, "cluster": "A"},
                {"store_id": "store_002", "units": 2000, "cluster": "A"},
                {"store_id": "store_003", "units": 1200, "cluster": "B"},
                {"store_id": "store_004", "units": 1200, "cluster": "B"},
                {"store_id": "store_005", "units": 800, "cluster": "C"}
            ]
        }

    def get_instructions(self) -> str:
        """
        Get agent instructions (system prompt for Phase 8).

        Returns:
            Demand agent instructions
        """
        return """
You are the Demand Agent for a fashion retail forecasting system.

Your responsibilities:
1. Forecast weekly demand using ensemble Prophet + ARIMA models
   - Analyze historical sales patterns
   - Consider seasonality, trends, and category characteristics
   - Generate week-by-week demand projections
   - Provide confidence scores for each forecast

2. Cluster stores by performance tier (A/B/C)
   - Group stores into performance tiers based on historical sales
   - Calculate distribution percentages for each tier
   - Consider store format, location, and market conditions

3. Allocate units to stores
   - Distribute forecasted units across stores
   - Apply cluster-based allocation rules
   - Ensure total allocation matches forecast
   - Optimize for balanced inventory across network

Workflow:
1. Generate demand forecast for specified horizon
2. Cluster stores into performance tiers (A/B/C)
3. Allocate forecasted units based on cluster distribution
4. Return consolidated forecast results

Rules:
- Always provide confidence scores (0.0-1.0)
- Validate outputs between steps
- Handle re-forecast scenarios with actuals context
- Return structured forecast_result matching DemandAgentOutput contract
""".strip()
