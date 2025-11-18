"""Agent package for OpenAI Agents SDK integration."""

from app.agents.config import AgentConfig, get_agent_config
from app.agents.orchestrator import OrchestratorAgent
from app.agents.demand_agent import DemandAgent
from app.agents.inventory_agent import InventoryAgent
from app.agents.pricing_agent import PricingAgent
from app.agents.factory import (
    AgentFactory,
    get_orchestrator,
    get_demand_agent,
    get_inventory_agent,
    get_pricing_agent
)

__all__ = [
    # Configuration
    "AgentConfig",
    "get_agent_config",
    # Agents
    "OrchestratorAgent",
    "DemandAgent",
    "InventoryAgent",
    "PricingAgent",
    # Factory
    "AgentFactory",
    "get_orchestrator",
    "get_demand_agent",
    "get_inventory_agent",
    "get_pricing_agent",
]
