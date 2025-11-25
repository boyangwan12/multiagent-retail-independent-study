"""
Retail Forecasting Backend - Deterministic Workflow Architecture

This backend uses the OpenAI Agents SDK with deterministic workflow orchestration.
Key patterns:
- Agents have output_type for structured Pydantic output
- Workflows control WHEN agents run (Python code)
- Agents control HOW they reason (LLM)
- Guardrails validate outputs before returning
"""

__version__ = "2.0.0"
