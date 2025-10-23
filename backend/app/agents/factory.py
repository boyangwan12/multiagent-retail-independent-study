"""Agent factory for dependency injection."""

from app.agents.config import get_agent_config
from app.agents.orchestrator import OrchestratorAgent
from app.agents.demand_agent import DemandAgent
from app.agents.inventory_agent import InventoryAgent
from app.agents.pricing_agent import PricingAgent
import logging

logger = logging.getLogger("fashion_forecast")


class AgentFactory:
    """
    Factory for creating agent instances with dependency injection.

    Ensures all agents share the same configuration and OpenAI client.
    """

    _orchestrator: OrchestratorAgent | None = None
    _demand_agent: DemandAgent | None = None
    _inventory_agent: InventoryAgent | None = None
    _pricing_agent: PricingAgent | None = None

    @classmethod
    def get_orchestrator(cls) -> OrchestratorAgent:
        """
        Get or create Orchestrator Agent singleton.

        Returns:
            OrchestratorAgent instance
        """
        if cls._orchestrator is None:
            config = get_agent_config()
            cls._orchestrator = OrchestratorAgent(config)
            logger.info(" Orchestrator Agent created via factory")
        return cls._orchestrator

    @classmethod
    def get_demand_agent(cls) -> DemandAgent:
        """
        Get or create Demand Agent singleton.

        Returns:
            DemandAgent instance
        """
        if cls._demand_agent is None:
            config = get_agent_config()
            cls._demand_agent = DemandAgent(config)
            logger.info(" Demand Agent created via factory")
        return cls._demand_agent

    @classmethod
    def get_inventory_agent(cls) -> InventoryAgent:
        """
        Get or create Inventory Agent singleton.

        Returns:
            InventoryAgent instance
        """
        if cls._inventory_agent is None:
            config = get_agent_config()
            cls._inventory_agent = InventoryAgent(config)
            logger.info(" Inventory Agent created via factory")
        return cls._inventory_agent

    @classmethod
    def get_pricing_agent(cls) -> PricingAgent:
        """
        Get or create Pricing Agent singleton.

        Returns:
            PricingAgent instance
        """
        if cls._pricing_agent is None:
            config = get_agent_config()
            cls._pricing_agent = PricingAgent(config)
            logger.info(" Pricing Agent created via factory")
        return cls._pricing_agent

    @classmethod
    def reset(cls):
        """
        Reset all agent singletons (useful for testing).

        Warning: This will destroy existing agent instances.
        """
        cls._orchestrator = None
        cls._demand_agent = None
        cls._inventory_agent = None
        cls._pricing_agent = None
        logger.info(" Agent factory reset")


# Convenience functions for dependency injection
def get_orchestrator() -> OrchestratorAgent:
    """FastAPI dependency for Orchestrator Agent."""
    return AgentFactory.get_orchestrator()


def get_demand_agent() -> DemandAgent:
    """FastAPI dependency for Demand Agent."""
    return AgentFactory.get_demand_agent()


def get_inventory_agent() -> InventoryAgent:
    """FastAPI dependency for Inventory Agent."""
    return AgentFactory.get_inventory_agent()


def get_pricing_agent() -> PricingAgent:
    """FastAPI dependency for Pricing Agent."""
    return AgentFactory.get_pricing_agent()
