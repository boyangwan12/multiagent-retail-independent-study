"""
Shared pytest fixtures for backend tests.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database.db import Base, get_db
from app.core.config import settings
import os

# Set test environment variables before importing settings
os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["AZURE_OPENAI_ENDPOINT"] = "https://test.openai.azure.com/"
os.environ["AZURE_OPENAI_API_KEY"] = "test_key_for_testing"
os.environ["DEBUG"] = "false"


@pytest.fixture(scope="function")
def db_session():
    """
    Create a fresh database session for each test.

    Uses in-memory SQLite database that is destroyed after each test.
    """
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)

    TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestSessionLocal()

    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    """
    FastAPI test client with database session override.

    Usage:
        def test_endpoint(client):
            response = client.get("/api/health")
            assert response.status_code == 200
    """
    def override_get_db():
        try:
            yield db_session
        finally:
            pass  # Session cleanup handled by db_session fixture

    # Override database dependency
    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture
def mock_season_parameters():
    """Mock SeasonParameters for testing."""
    return {
        "forecast_horizon_weeks": 12,
        "season_start_date": "2025-03-03",
        "season_end_date": "2025-05-26",
        "replenishment_strategy": "weekly",
        "dc_holdback_percentage": 0.45,
        "markdown_checkpoint_week": 6,
        "markdown_threshold": 0.60,
        "extraction_confidence": "high"
    }


@pytest.fixture
def mock_category():
    """Mock category data for testing."""
    return {
        "category_id": "CAT001",
        "category_name": "Women's Blouses",
        "department": "Women's Apparel"
    }


@pytest.fixture
def mock_store():
    """Mock store data for testing."""
    return {
        "store_id": "STORE001",
        "store_name": "Fifth Avenue Flagship",
        "cluster_id": "fashion_forward",
        "store_size_sqft": 15000,
        "location_tier": "A",
        "median_income": 120000,
        "region": "NORTHEAST"
    }


@pytest.fixture
def mock_forecast_response():
    """Mock forecast API response."""
    return {
        "forecast_id": "FC_123456",
        "category_name": "Women's Blouses",
        "season_start_date": "2025-03-03",
        "season_end_date": "2025-05-26",
        "total_season_demand": 7750,
        "forecasting_method": "ensemble_prophet_arima",
        "prophet_forecast": 8000,
        "arima_forecast": 7500,
        "weekly_demand_curve": [
            {
                "week_number": 1,
                "week_start_date": "2025-03-03",
                "week_end_date": "2025-03-09",
                "forecasted_units": 1320,
                "confidence_lower": 1122,
                "confidence_upper": 1518
            }
        ],
        "cluster_distribution": [
            {
                "cluster_id": "fashion_forward",
                "cluster_name": "Fashion Forward",
                "allocation_percentage": 0.40,
                "total_units": 3100
            }
        ]
    }
