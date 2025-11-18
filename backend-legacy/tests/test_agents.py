"""Tests for agent scaffolding (PHASE3-009)."""

import pytest
from app.agents import (
    AgentConfig,
    get_agent_config,
    OrchestratorAgent,
    DemandAgent,
    InventoryAgent,
    PricingAgent,
    AgentFactory
)
from app.schemas.workflow_schemas import SeasonParameters
from datetime import date


class TestAgentConfig:
    """Test agent configuration."""

    def test_agent_config_from_settings(self):
        """Test creating AgentConfig from settings."""
        config = get_agent_config()

        assert config is not None
        assert config.openai_client is not None
        assert config.model is not None
        assert config.temperature == 0.2
        assert config.max_tokens == 4000
        assert config.timeout_seconds > 0
        assert config.max_retries > 0

    def test_agent_config_singleton(self):
        """Test that get_agent_config returns same instance."""
        config1 = get_agent_config()
        config2 = get_agent_config()

        assert config1 is config2


class TestAgentFactory:
    """Test agent factory."""

    def test_get_orchestrator(self):
        """Test getting Orchestrator agent from factory."""
        orchestrator = AgentFactory.get_orchestrator()

        assert orchestrator is not None
        assert isinstance(orchestrator, OrchestratorAgent)
        assert orchestrator.config is not None

    def test_get_demand_agent(self):
        """Test getting Demand agent from factory."""
        demand_agent = AgentFactory.get_demand_agent()

        assert demand_agent is not None
        assert isinstance(demand_agent, DemandAgent)
        assert demand_agent.config is not None
        assert len(demand_agent.get_tools()) == 3  # forecast, cluster, allocate

    def test_get_inventory_agent(self):
        """Test getting Inventory agent from factory."""
        inventory_agent = AgentFactory.get_inventory_agent()

        assert inventory_agent is not None
        assert isinstance(inventory_agent, InventoryAgent)
        assert inventory_agent.config is not None
        assert len(inventory_agent.get_tools()) == 3  # manufacturing, dc/store, replenishment

    def test_get_pricing_agent(self):
        """Test getting Pricing agent from factory."""
        pricing_agent = AgentFactory.get_pricing_agent()

        assert pricing_agent is not None
        assert isinstance(pricing_agent, PricingAgent)
        assert pricing_agent.config is not None
        assert len(pricing_agent.get_tools()) == 1  # markdown

    def test_factory_returns_singletons(self):
        """Test that factory returns same instances."""
        orchestrator1 = AgentFactory.get_orchestrator()
        orchestrator2 = AgentFactory.get_orchestrator()

        assert orchestrator1 is orchestrator2


class TestOrchestratorAgent:
    """Test Orchestrator agent."""

    @pytest.mark.asyncio
    async def test_run_forecast_workflow_placeholder(self):
        """Test forecast workflow placeholder implementation."""
        orchestrator = AgentFactory.get_orchestrator()

        parameters = SeasonParameters(
            forecast_horizon_weeks=12,
            season_start_date=date(2025, 3, 1),
            season_end_date=date(2025, 5, 23),
            replenishment_strategy="none",
            dc_holdback_percentage=0.0,
            markdown_checkpoint_week=6
        )

        result = await orchestrator.run_forecast_workflow(
            category_id="womens_dresses",
            parameters=parameters,
            workflow_id="test_wf_123"
        )

        assert result is not None
        assert "forecast_id" in result
        assert "allocation_id" in result
        assert "message" in result

    @pytest.mark.asyncio
    async def test_run_reforecast_workflow_placeholder(self):
        """Test re-forecast workflow placeholder implementation."""
        orchestrator = AgentFactory.get_orchestrator()

        result = await orchestrator.run_reforecast_workflow(
            forecast_id="f_test_123",
            actual_sales=3200,
            forecasted_sales=2550,
            remaining_weeks=8,
            variance_pct=0.255,
            workflow_id="test_wf_456"
        )

        assert result is not None
        assert "forecast_id" in result
        assert "allocation_id" in result
        assert "markdown_id" in result
        assert "message" in result

    def test_orchestrator_instructions(self):
        """Test that orchestrator has instructions."""
        orchestrator = AgentFactory.get_orchestrator()
        instructions = orchestrator.get_instructions()

        assert instructions is not None
        assert len(instructions) > 0
        assert "Orchestrator Agent" in instructions


class TestDemandAgent:
    """Test Demand agent."""

    @pytest.mark.asyncio
    async def test_forecast_demand_placeholder(self):
        """Test forecast_demand tool placeholder."""
        demand_agent = AgentFactory.get_demand_agent()

        result = await demand_agent.forecast_demand(
            category_id="womens_dresses",
            forecast_horizon_weeks=12,
            season_start_date="2025-03-01"
        )

        assert result is not None
        assert "forecast_id" in result
        assert "total_season_demand" in result
        assert "weekly_demand" in result

    @pytest.mark.asyncio
    async def test_cluster_stores_placeholder(self):
        """Test cluster_stores tool placeholder."""
        demand_agent = AgentFactory.get_demand_agent()

        result = await demand_agent.cluster_stores(
            category_id="womens_dresses",
            total_season_demand=8000
        )

        assert result is not None
        assert "cluster_id" in result
        assert "distribution" in result
        assert "A" in result["distribution"]
        assert "B" in result["distribution"]
        assert "C" in result["distribution"]

    @pytest.mark.asyncio
    async def test_allocate_to_stores_placeholder(self):
        """Test allocate_to_stores tool placeholder."""
        demand_agent = AgentFactory.get_demand_agent()

        result = await demand_agent.allocate_to_stores(
            forecast_id="f_test_123",
            cluster_distribution={"A": 0.5, "B": 0.3, "C": 0.2}
        )

        assert result is not None
        assert "allocation_id" in result
        assert "store_allocations" in result

    def test_demand_agent_instructions(self):
        """Test that demand agent has instructions."""
        demand_agent = AgentFactory.get_demand_agent()
        instructions = demand_agent.get_instructions()

        assert instructions is not None
        assert len(instructions) > 0
        assert "Demand Agent" in instructions


class TestInventoryAgent:
    """Test Inventory agent."""

    @pytest.mark.asyncio
    async def test_calculate_manufacturing_qty_placeholder(self):
        """Test calculate_manufacturing_qty tool placeholder."""
        inventory_agent = AgentFactory.get_inventory_agent()

        result = await inventory_agent.calculate_manufacturing_qty(
            forecast_id="f_test_123",
            total_season_demand=8000,
            safety_stock_pct=0.20
        )

        assert result is not None
        assert "manufacturing_qty" in result
        assert result["manufacturing_qty"] == 9600  # 8000 * 1.20

    @pytest.mark.asyncio
    async def test_allocate_dc_and_stores_placeholder(self):
        """Test allocate_dc_and_stores tool placeholder."""
        inventory_agent = AgentFactory.get_inventory_agent()

        result = await inventory_agent.allocate_dc_and_stores(
            allocation_id="a_test_123",
            manufacturing_qty=9600,
            dc_holdback_pct=0.45,
            replenishment_strategy="weekly"
        )

        assert result is not None
        assert "dc_allocation" in result
        assert "store_allocation" in result
        assert result["dc_allocation"] + result["store_allocation"] == 9600

    @pytest.mark.asyncio
    async def test_plan_replenishment_placeholder(self):
        """Test plan_replenishment tool placeholder."""
        inventory_agent = AgentFactory.get_inventory_agent()

        result = await inventory_agent.plan_replenishment(
            allocation_id="a_test_123",
            dc_inventory=4320,
            replenishment_strategy="weekly",
            forecast_horizon_weeks=12
        )

        assert result is not None
        assert "replenishment_schedule" in result
        assert len(result["replenishment_schedule"]) == 12  # weekly for 12 weeks

    def test_inventory_agent_instructions(self):
        """Test that inventory agent has instructions."""
        inventory_agent = AgentFactory.get_inventory_agent()
        instructions = inventory_agent.get_instructions()

        assert instructions is not None
        assert len(instructions) > 0
        assert "Inventory Agent" in instructions


class TestPricingAgent:
    """Test Pricing agent."""

    @pytest.mark.asyncio
    async def test_calculate_markdown_needed(self):
        """Test calculate_markdown when markdown is needed."""
        pricing_agent = AgentFactory.get_pricing_agent()

        result = await pricing_agent.calculate_markdown(
            forecast_id="f_test_123",
            allocation_id="a_test_123",
            checkpoint_week=6,
            sell_through_pct=0.35,  # Below target
            target_sell_through_pct=0.60
        )

        assert result is not None
        assert result["markdown_needed"] is True
        assert result["discount_pct"] > 0
        assert result["status"] == "markdown_applied"

    @pytest.mark.asyncio
    async def test_calculate_markdown_not_needed(self):
        """Test calculate_markdown when no markdown needed."""
        pricing_agent = AgentFactory.get_pricing_agent()

        result = await pricing_agent.calculate_markdown(
            forecast_id="f_test_123",
            allocation_id="a_test_123",
            checkpoint_week=6,
            sell_through_pct=0.65,  # Above target
            target_sell_through_pct=0.60
        )

        assert result is not None
        assert result["markdown_needed"] is False
        assert result["discount_pct"] == 0.0
        assert result["status"] == "no_markdown_needed"

    def test_pricing_agent_instructions(self):
        """Test that pricing agent has instructions."""
        pricing_agent = AgentFactory.get_pricing_agent()
        instructions = pricing_agent.get_instructions()

        assert instructions is not None
        assert len(instructions) > 0
        assert "Pricing Agent" in instructions
