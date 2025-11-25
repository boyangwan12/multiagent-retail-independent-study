"""
Guardrails for OpenAI Agents SDK

Output guardrails enforce data integrity and business rules
before agent responses reach the user.
"""

from .demand_guardrails import validate_forecast_output

__all__ = ['validate_forecast_output']
