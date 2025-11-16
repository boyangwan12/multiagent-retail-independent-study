"""Inventory Agent for hierarchical allocation and replenishment (Phase 7)."""

from typing import Any, Dict, List, Optional
from app.agents.config import AgentConfig
from app.ml.store_clustering import StoreClusterer
from app.schemas.workflow_schemas import SeasonParameters
import pandas as pd
import numpy as np
import logging

logger = logging.getLogger("fashion_forecast")


class InventoryAgent:
    """
    Inventory Agent for hierarchical allocation and replenishment planning.

    Implements 3-layer allocation hierarchy (category → cluster → store) with
    parameter-driven DC holdback. Uses K-means clustering for store segmentation.
    Integrates with Phase 6 Demand Agent output via AgentHandoffManager.

    **Agent Framework:**
    - Follows OpenAI SDK-compatible agent pattern (same as DemandAgent)
    - Uses AgentConfig with OpenAI client (prepared for Phase 8 SDK migration)
    - Async execute() method for orchestrator coordination
    - Tool definitions in OpenAI function-calling format (Phase 8 ready)

    **Phase 7 Implementation:**
    - Real K-means clustering (Story 001)
    - Real hierarchical allocation (Story 002)
    - Real replenishment scheduling (Story 003)
    - Integration testing (Story 004)

    **Phase 8 Handoff:**
    - Output: InventoryAgentOutput schema (cluster allocations, store allocations)
    - Input to Pricing Agent for markdown analysis
    - Will migrate to OpenAI Agents SDK when available

    **Attributes:**
        config: Agent configuration with OpenAI client (Phase 8)
        client: OpenAI client (optional in Phase 7, required Phase 8)
        clusterer: StoreClusterer instance for K-means clustering
    """

    def __init__(self, config: Optional[AgentConfig] = None):
        """
        Initialize Inventory Agent.

        Args:
            config: Agent configuration with OpenAI client (provided by AgentFactory in Phase 8)
        """
        self.config = config
        self.client = config.openai_client if config else None
        self.clusterer = StoreClusterer(n_clusters=3, random_state=42)
        logger.info("InventoryAgent initialized with StoreClusterer (Phase 7)")

    async def execute(
        self,
        forecast_result: Dict[str, Any],
        parameters: SeasonParameters,
        stores_data: pd.DataFrame
    ) -> Dict[str, Any]:
        """
        Execute inventory allocation workflow (main orchestrator entry point).

        **Flow:**
        1. Calculate manufacturing quantity (demand × safety stock)
        2. Train K-means clustering on store features
        3. Allocate to clusters based on K-means percentages
        4. Allocate to stores using hybrid factors (70/30)
        5. Plan replenishment (parameter-driven, skipped if strategy="none")
        6. Validate unit conservation at each step

        Args:
            forecast_result: Demand Agent output containing:
                - total_demand: int
                - forecast_by_week: List[int]
                - safety_stock_pct: float
                - confidence: float
                - model_used: str
            parameters: Season parameters containing:
                - dc_holdback_percentage: float (0.0 or 0.45)
                - replenishment_strategy: str ("none" or "weekly")
                - forecast_horizon_weeks: int
            stores_data: Store attributes DataFrame with 7 features (store_id indexed)

        Returns:
            Dictionary with allocation results:
            {
                "manufacturing_qty": int,
                "safety_stock_pct": float,
                "initial_allocation_total": int,
                "dc_holdback_total": int,
                "clusters": List[Dict],
                "replenishment_enabled": bool,
                "replenishment_queue": List[Dict]
            }

        Raises:
            ValueError: If unit conservation fails or input validation fails
            ForecastingError: If clustering fails
        """
        logger.info(
            f"InventoryAgent executing allocation for {len(stores_data)} stores "
            f"({parameters.forecast_horizon_weeks} weeks)"
        )

        try:
            # Extract forecast inputs
            total_demand = forecast_result['total_demand']
            safety_stock_pct = forecast_result['safety_stock_pct']
            forecast_by_week = forecast_result['forecast_by_week']

            # Step 1: Calculate manufacturing quantity
            logger.info("Step 1: Calculating manufacturing quantity...")
            manufacturing_qty = self.calculate_manufacturing(total_demand, safety_stock_pct)
            logger.info(
                f"Manufacturing: {total_demand} × (1 + {safety_stock_pct}) = {manufacturing_qty} units"
            )

            # Step 2: Train K-means clustering
            logger.info("Step 2: Training K-means clustering on store features...")
            self.clusterer.fit(stores_data)
            cluster_stats = self.clusterer.get_cluster_stats()
            cluster_labels = self.clusterer.get_cluster_labels()
            logger.info(f"Clustering complete: {len(cluster_labels)} clusters identified")

            # Step 3: Allocate to clusters and stores
            logger.info("Step 3: Allocating inventory to clusters and stores...")
            allocation_result = self._allocate_initial(
                manufacturing_qty,
                parameters,
                stores_data,
                cluster_stats,
                cluster_labels,
                forecast_by_week
            )

            # Step 4: Handle replenishment (parameter-driven)
            logger.info("Step 4: Planning replenishment...")
            if parameters.replenishment_strategy == "none":
                logger.info("Replenishment strategy='none' - skipping replenishment phase")
                replenishment_enabled = False
                replenishment_queue = []
            else:
                logger.info(f"Replenishment strategy='{parameters.replenishment_strategy}' - enabling replenishment")
                replenishment_enabled = True
                replenishment_queue = []  # Will be populated weekly by workflow

            # Combine results
            output = {
                "manufacturing_qty": manufacturing_qty,
                "safety_stock_pct": safety_stock_pct,
                "initial_allocation_total": allocation_result["initial_allocation_total"],
                "dc_holdback_total": allocation_result["dc_holdback_total"],
                "clusters": allocation_result["clusters"],
                "replenishment_enabled": replenishment_enabled,
                "replenishment_queue": replenishment_queue
            }

            logger.info(
                f"Allocation complete: {allocation_result['initial_allocation_total']} to stores, "
                f"{allocation_result['dc_holdback_total']} to DC"
            )

            return output

        except Exception as e:
            logger.error(f"Inventory allocation failed: {e}", exc_info=True)
            raise

    def calculate_manufacturing(
        self,
        total_demand: int,
        safety_stock_pct: float
    ) -> int:
        """
        Calculate manufacturing order quantity.

        **Formula:** manufacturing_qty = total_demand × (1 + safety_stock_pct)

        Args:
            total_demand: Total season demand from forecast
            safety_stock_pct: Safety stock percentage (0.1-0.5)

        Returns:
            Manufacturing quantity (integer)

        Example:
            >>> agent.calculate_manufacturing(8000, 0.20)
            9600  # 8000 × 1.20
        """
        # Validate inputs
        if total_demand <= 0:
            raise ValueError(f"total_demand must be positive, got {total_demand}")

        if not (0.0 <= safety_stock_pct <= 1.0):
            raise ValueError(f"safety_stock_pct must be in [0, 1], got {safety_stock_pct}")

        manufacturing_qty = int(total_demand * (1 + safety_stock_pct))

        return manufacturing_qty

    def _allocate_initial(
        self,
        manufacturing_qty: int,
        parameters: SeasonParameters,
        stores_data: pd.DataFrame,
        cluster_stats: pd.DataFrame,
        cluster_labels: Dict[int, str],
        forecast_by_week: List[int]
    ) -> Dict[str, Any]:
        """
        Allocate manufacturing quantity to clusters and stores.

        **Allocation Hierarchy:**
        1. Layer 1 - Manufacturing split:
           - DC holdback: manufacturing_qty × dc_holdback_percentage
           - Initial allocation: manufacturing_qty × (1 - dc_holdback_percentage)

        2. Layer 2 - Cluster allocation:
           - Initial allocation × cluster_percentage (from K-means)
           - Example: 5280 × 40% = 2112 units to Fashion_Forward cluster

        3. Layer 3 - Store allocation:
           - Cluster allocation × store_factor (hybrid: 70% historical + 30% attributes)
           - Enforce 2-week minimum per store

        Args:
            manufacturing_qty: Total units from calculate_manufacturing()
            parameters: Season parameters with dc_holdback_percentage
            stores_data: Store attributes for allocation factors
            cluster_stats: Cluster statistics from K-means
            cluster_labels: Mapping of cluster IDs to labels
            forecast_by_week: Weekly forecasts for 2-week minimum calculation

        Returns:
            Dictionary with clusters and store allocations
        """
        # Extract DC holdback from parameters
        dc_holdback_pct = parameters.dc_holdback_percentage
        initial_allocation_pct = 1.0 - dc_holdback_pct

        # Calculate split
        initial_allocation_total = int(manufacturing_qty * initial_allocation_pct)
        dc_holdback_total = manufacturing_qty - initial_allocation_total

        # Validate unit conservation at manufacturing split
        self._validate_unit_conservation(
            expected=manufacturing_qty,
            actual=initial_allocation_total + dc_holdback_total,
            step="manufacturing_split"
        )

        logger.info(
            f"DC Holdback: {dc_holdback_pct*100:.0f}% = {dc_holdback_total} units, "
            f"Initial Allocation: {initial_allocation_pct*100:.0f}% = {initial_allocation_total} units"
        )

        # Allocate to clusters
        cluster_allocations = []
        for idx, row in cluster_stats.iterrows():
            cluster_id = idx
            cluster_label = row['cluster_label']
            allocation_pct = row['allocation_percentage'] / 100.0

            cluster_units = int(initial_allocation_total * allocation_pct)

            # Get stores in this cluster
            cluster_stores = self.clusterer.training_data_[
                self.clusterer.training_data_['cluster_id'] == cluster_id
            ].copy()

            # Calculate store allocations within cluster
            store_allocations = self._allocate_to_stores(
                cluster_id=cluster_id,
                cluster_label=cluster_label,
                cluster_units=cluster_units,
                stores_data=stores_data,
                cluster_stores=cluster_stores,
                forecast_by_week=forecast_by_week
            )

            cluster_allocations.append({
                "cluster_id": int(cluster_id),
                "cluster_label": cluster_label,
                "allocation_percentage": row['allocation_percentage'],
                "total_units": cluster_units,
                "stores": store_allocations
            })

        # Validate cluster allocations sum to initial_allocation_total
        actual_cluster_sum = sum(c['total_units'] for c in cluster_allocations)
        self._validate_unit_conservation(
            expected=initial_allocation_total,
            actual=actual_cluster_sum,
            step="cluster_allocation"
        )

        # Validate store allocations sum correctly
        total_store_allocation = sum(
            sum(s['initial_allocation'] for s in c['stores'])
            for c in cluster_allocations
        )
        self._validate_unit_conservation(
            expected=initial_allocation_total,
            actual=total_store_allocation,
            step="store_allocation"
        )

        return {
            "initial_allocation_total": initial_allocation_total,
            "dc_holdback_total": dc_holdback_total,
            "clusters": cluster_allocations
        }

    def _allocate_to_stores(
        self,
        cluster_id: int,
        cluster_label: str,
        cluster_units: int,
        stores_data: pd.DataFrame,
        cluster_stores: pd.DataFrame,
        forecast_by_week: List[int]
    ) -> List[Dict[str, Any]]:
        """
        Distribute cluster allocation to stores with 2-week minimum enforcement.

        Args:
            cluster_id: Cluster ID
            cluster_label: Cluster label (e.g., "Fashion_Forward")
            cluster_units: Units allocated to this cluster
            stores_data: All store attributes
            cluster_stores: Stores in this cluster
            forecast_by_week: Weekly forecasts for minimum calculation

        Returns:
            List of store allocations
        """
        # Calculate cluster averages for reference
        cluster_avg = cluster_stores[[
            'avg_weekly_sales_12mo', 'store_size_sqft', 'median_income'
        ]].mean().to_dict()

        # Calculate allocation factor for each store
        store_factors = {}
        for store_id, store_row in cluster_stores.iterrows():
            factor = self._calculate_allocation_factor(store_row, cluster_avg)
            store_factors[store_id] = factor

        # Normalize factors to sum to 1.0
        total_factor = sum(store_factors.values())
        if total_factor > 0:
            normalized_factors = {sid: f / total_factor for sid, f in store_factors.items()}
        else:
            # Equal allocation if all factors are zero
            normalized_factors = {sid: 1.0 / len(store_factors) for sid in store_factors.keys()}

        # Allocate to stores
        store_allocations = []
        min_allocation_units = forecast_by_week[0] * 2 if forecast_by_week else 0

        for store_id, factor in normalized_factors.items():
            store_row = stores_data.loc[store_id]

            base_allocation = int(cluster_units * factor)

            # Enforce 2-week minimum
            final_allocation = max(base_allocation, min_allocation_units)

            if final_allocation > base_allocation:
                logger.debug(
                    f"Store {store_id}: Bumped to 2-week minimum "
                    f"({base_allocation} → {final_allocation} units)"
                )

            store_allocations.append({
                "store_id": str(store_id),
                "cluster": cluster_label,
                "initial_allocation": final_allocation,
                "allocation_factor": float(factor)
            })

        return store_allocations

    def _calculate_allocation_factor(
        self,
        store: pd.Series,
        cluster_avg: Dict[str, float]
    ) -> float:
        """
        Calculate store allocation factor (70% historical + 30% attributes).

        **Formula:**
        - historical_score = store_avg_sales / cluster_avg_sales
        - attribute_score = 0.5×size_score + 0.3×income_score + 0.2×tier_score
        - allocation_factor = 0.7×historical_score + 0.3×attribute_score

        Args:
            store: Store row with features
            cluster_avg: Cluster average features for normalization

        Returns:
            Normalized allocation factor (typically 0.5-1.5)
        """
        # Calculate historical performance score
        if cluster_avg['avg_weekly_sales_12mo'] > 0:
            historical_score = store['avg_weekly_sales_12mo'] / cluster_avg['avg_weekly_sales_12mo']
        else:
            historical_score = 1.0

        # Calculate attribute score
        if cluster_avg['store_size_sqft'] > 0:
            size_score = store['store_size_sqft'] / cluster_avg['store_size_sqft']
        else:
            size_score = 1.0

        if cluster_avg['median_income'] > 0:
            income_score = store['median_income'] / cluster_avg['median_income']
        else:
            income_score = 1.0

        # Normalize location tier (A=1.0, B=0.67, C=0.33)
        location_tier_numeric = self.clusterer.LOCATION_TIER_MAP.get(store['location_tier'], 1)
        tier_score = location_tier_numeric / 3.0

        # Weighted average of attribute scores
        attribute_score = (0.5 * size_score + 0.3 * income_score + 0.2 * tier_score)

        # Final allocation factor (70% historical + 30% attributes)
        allocation_factor = 0.7 * historical_score + 0.3 * attribute_score

        return allocation_factor

    def _validate_unit_conservation(
        self,
        expected: int,
        actual: int,
        step: str
    ) -> None:
        """
        Validate unit conservation (no units lost or gained).

        **Checkpoints:**
        1. Manufacturing split: manufacturing_qty == initial + holdback
        2. Cluster allocation: sum(cluster_totals) == initial_allocation_total
        3. Store allocation: sum(store_totals) == cluster_total
        4. Final validation: sum(all_store_allocations) == initial_allocation_total

        Args:
            expected: Expected total units
            actual: Actual total units after allocation
            step: Step name for error message (e.g., "manufacturing_split")

        Raises:
            ValueError: If expected != actual
        """
        if expected != actual:
            raise ValueError(
                f"Unit conservation failed at {step}: "
                f"expected {expected}, got {actual} (diff: {actual - expected})"
            )

        logger.debug(f"Unit conservation OK at {step}: {expected} units")

    def calculate_replenishment(
        self,
        store_id: str,
        current_week: int,
        forecast_by_week: List[int],
        current_inventory: int
    ) -> int:
        """
        Calculate weekly replenishment needs per store.

        **Formula:** replenish_qty = max(0, forecast_next_week - current_inventory)

        Args:
            store_id: Store identifier
            current_week: Current week (0-indexed)
            forecast_by_week: List of weekly forecasts
            current_inventory: Current inventory level

        Returns:
            Replenishment quantity (non-negative)
        """
        if current_week + 1 >= len(forecast_by_week):
            return 0  # No replenishment past forecast horizon

        next_week_forecast = forecast_by_week[current_week + 1]
        replenish_qty = max(0, next_week_forecast - current_inventory)

        if replenish_qty > 0:
            logger.info(
                f"Store {store_id}: Replenish {replenish_qty} "
                f"(forecast: {next_week_forecast}, inventory: {current_inventory})"
            )

        return replenish_qty

    def generate_replenishment_queue(
        self,
        current_week: int,
        parameters: SeasonParameters,
        stores_allocation: List[Dict],
        dc_inventory: int,
        forecast_by_week: List[int]
    ) -> List[Dict[str, Any]]:
        """
        Generate queue of stores needing replenishment.

        Args:
            current_week: Current week (0-indexed)
            parameters: Season parameters with replenishment_strategy
            stores_allocation: Store allocation data from initial allocation
            dc_inventory: Available DC inventory
            forecast_by_week: Weekly forecasts

        Returns:
            Replenishment queue (empty if strategy="none")
        """
        # Check if replenishment enabled
        if parameters.replenishment_strategy == "none":
            logger.info("Replenishment disabled (strategy='none') - phase skipped")
            return []

        logger.info(f"Generating replenishment queue (strategy: {parameters.replenishment_strategy})...")

        replenishment_queue = []
        total_needed = 0

        for store_data in stores_allocation:
            store_id = store_data['store_id']
            current_inventory = store_data['initial_allocation']

            replenish_qty = self.calculate_replenishment(
                store_id=store_id,
                current_week=current_week,
                forecast_by_week=forecast_by_week,
                current_inventory=current_inventory
            )

            if replenish_qty > 0:
                total_needed += replenish_qty
                replenishment_queue.append({
                    "store_id": store_id,
                    "current_inventory": current_inventory,
                    "forecast_next_week": forecast_by_week[current_week + 1] if current_week + 1 < len(forecast_by_week) else 0,
                    "replenish_needed": replenish_qty,
                    "dc_available": "pending"
                })

        # Check DC availability
        if total_needed > dc_inventory:
            logger.warning(
                f"Insufficient DC inventory: needed {total_needed}, available {dc_inventory} "
                f"(shortfall: {total_needed - dc_inventory})"
            )
            # Flag stores with insufficient inventory
            remaining_dc = dc_inventory
            for item in replenishment_queue:
                if remaining_dc >= item['replenish_needed']:
                    item['dc_available'] = "yes"
                    remaining_dc -= item['replenish_needed']
                else:
                    item['dc_available'] = f"partial ({remaining_dc})"
                    remaining_dc = 0
        else:
            logger.info(f"DC inventory sufficient: {dc_inventory} available, {total_needed} needed")
            for item in replenishment_queue:
                item['dc_available'] = "yes"

        return replenishment_queue

    def get_tools(self) -> List[Dict[str, Any]]:
        """
        Get tool definitions for OpenAI function calling (Phase 8).

        **Note:** Phase 7 uses direct method calls via orchestrator.
        Phase 8 will use these definitions with OpenAI Agents SDK.

        Returns:
            List of tool definitions in OpenAI function-calling format
        """
        return [
            {
                "type": "function",
                "function": {
                    "name": "calculate_manufacturing_qty",
                    "description": "Calculate manufacturing quantity with safety stock buffer",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "total_demand": {
                                "type": "integer",
                                "description": "Total forecasted demand"
                            },
                            "safety_stock_pct": {
                                "type": "number",
                                "description": "Safety stock percentage (0.1-0.5)"
                            }
                        },
                        "required": ["total_demand", "safety_stock_pct"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "allocate_to_clusters",
                    "description": "Allocate manufactured units to store clusters using K-means",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "manufacturing_qty": {
                                "type": "integer",
                                "description": "Manufacturing quantity"
                            },
                            "dc_holdback_pct": {
                                "type": "number",
                                "description": "DC holdback percentage"
                            }
                        },
                        "required": ["manufacturing_qty", "dc_holdback_pct"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "generate_replenishment_plan",
                    "description": "Generate weekly replenishment schedule from DC to stores",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "dc_inventory": {
                                "type": "integer",
                                "description": "DC holdback inventory available"
                            },
                            "replenishment_strategy": {
                                "type": "string",
                                "description": "Replenishment strategy (none/weekly)"
                            }
                        },
                        "required": ["dc_inventory", "replenishment_strategy"]
                    }
                }
            }
        ]

    def get_instructions(self) -> str:
        """
        Get agent instructions (system prompt for Phase 8).

        **Note:** Phase 7 doesn't require LLM calls.
        Phase 8 will use this for OpenAI Agents SDK orchestration.

        Returns:
            Agent instructions string
        """
        return """
You are the Inventory Agent for a fashion retail forecasting system.

Your responsibilities:
1. Calculate manufacturing quantity
   - Add safety stock buffer to forecasted demand
   - Consider lead times and constraints
   - Return manufacturing quantity for production

2. Allocate inventory to clusters and stores
   - Use K-means clustering to segment stores (3 tiers: Fashion_Forward, Mainstream, Value_Conscious)
   - Apply parameter-driven DC holdback (0% for Zara, 45% for standard retail)
   - Distribute to stores using hybrid factors (70% historical performance + 30% attributes)
   - Enforce 2-week minimum inventory per store

3. Plan replenishment schedule
   - Calculate weekly replenishment needs based on forecast
   - Check DC inventory availability
   - Skip replenishment if strategy="none"
   - Generate replenishment queue with DC status

Tools available:
- calculate_manufacturing_qty: Determine manufacturing quantity
- allocate_to_clusters: Allocate units to store clusters
- generate_replenishment_plan: Plan weekly replenishment schedule

Workflow:
1. Call calculate_manufacturing_qty with total_demand and safety_stock_pct from Demand Agent
2. Call allocate_to_clusters with manufacturing_qty and dc_holdback_pct
3. Call generate_replenishment_plan if replenishment_strategy != "none"
4. Return allocation_plan and replenishment_queue to Pricing Agent

Rules:
- Always validate unit conservation (no units lost or gained)
- Enforce 2-week minimum inventory per store
- Skip replenishment planning if strategy is "none"
- Return structured allocation matching InventoryAgentOutput contract
""".strip()
