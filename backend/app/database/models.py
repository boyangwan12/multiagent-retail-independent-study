"""
Consolidated database models for Fashion Forecast application.
All SQLAlchemy ORM models in one place for better maintainability.
"""
import enum
from sqlalchemy import (
    Column, String, Integer, Float, JSON, DateTime, Date, Text,
    ForeignKey, Enum, CheckConstraint, Index
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database.db import Base


# ============================================================================
# Enums
# ============================================================================

class WorkflowStatus(str, enum.Enum):
    """Workflow status enum."""
    pending = "pending"
    running = "running"
    completed = "completed"
    failed = "failed"
    awaiting_approval = "awaiting_approval"


# ============================================================================
# Core Entities
# ============================================================================

class Category(Base):
    __tablename__ = "categories"

    category_id = Column(String, primary_key=True)
    category_name = Column(String, nullable=False)
    season_start_date = Column(Date, nullable=False)
    season_end_date = Column(Date, nullable=False)
    season_length_weeks = Column(Integer, nullable=False)
    archetype = Column(
        String,
        nullable=False,
        default="FASHION_RETAIL"
    )
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    __table_args__ = (
        CheckConstraint(
            "archetype IN ('FASHION_RETAIL', 'STABLE_CATALOG', 'CONTINUOUS')",
            name="check_archetype"
        ),
    )


class StoreCluster(Base):
    __tablename__ = "store_clusters"

    cluster_id = Column(String, primary_key=True)
    cluster_name = Column(String, nullable=False)
    fashion_tier = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    # Relationships
    stores = relationship("Store", back_populates="cluster")

    __table_args__ = (
        CheckConstraint(
            "fashion_tier IN ('PREMIUM', 'MAINSTREAM', 'VALUE')",
            name="check_fashion_tier"
        ),
    )


class Store(Base):
    __tablename__ = "stores"

    store_id = Column(String, primary_key=True)
    store_name = Column(String, nullable=False)
    cluster_id = Column(String, ForeignKey("store_clusters.cluster_id"), nullable=False)
    store_size_sqft = Column(Integer, nullable=False)
    location_tier = Column(String, nullable=False)
    median_income = Column(Integer, nullable=False)
    store_format = Column(String, nullable=False)
    region = Column(String, nullable=False)
    avg_weekly_sales_12mo = Column(Float, nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    # Relationships
    cluster = relationship("StoreCluster", back_populates="stores")

    __table_args__ = (
        CheckConstraint("location_tier IN ('A', 'B', 'C')", name="check_location_tier"),
        CheckConstraint(
            "store_format IN ('MALL', 'STANDALONE', 'SHOPPING_CENTER', 'OUTLET')",
            name="check_store_format"
        ),
        CheckConstraint(
            "region IN ('NORTHEAST', 'SOUTHEAST', 'MIDWEST', 'WEST')",
            name="check_region"
        ),
    )


# ============================================================================
# Forecast Models
# ============================================================================

class Forecast(Base):
    __tablename__ = "forecasts"

    forecast_id = Column(String, primary_key=True)
    category_id = Column(String, ForeignKey("categories.category_id"), nullable=False)
    season = Column(String, nullable=False)
    forecast_horizon_weeks = Column(Integer, nullable=False)
    total_season_demand = Column(Integer, nullable=False)

    # JSON columns for variable-length arrays
    weekly_demand_curve = Column(JSON, nullable=False)  # [{"week_number": 1, "demand_units": 500}, ...]

    peak_week = Column(Integer, nullable=False)
    forecasting_method = Column(String, nullable=False, default="ensemble_prophet_arima")
    models_used = Column(JSON, nullable=False)  # ["prophet", "arima"]
    prophet_forecast = Column(Integer, nullable=True)
    arima_forecast = Column(Integer, nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    # Relationships
    category = relationship("Category")

    __table_args__ = (
        CheckConstraint("total_season_demand >= 0", name="check_total_demand"),
    )


class ForecastClusterDistribution(Base):
    __tablename__ = "forecast_cluster_distribution"

    distribution_id = Column(String, primary_key=True)
    forecast_id = Column(String, ForeignKey("forecasts.forecast_id"), nullable=False)
    cluster_id = Column(String, ForeignKey("store_clusters.cluster_id"), nullable=False)
    allocation_percentage = Column(Float, nullable=False)
    total_units = Column(Integer, nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    __table_args__ = (
        CheckConstraint(
            "allocation_percentage >= 0 AND allocation_percentage <= 1",
            name="check_allocation_pct"
        ),
        CheckConstraint("total_units >= 0", name="check_total_units"),
    )


# ============================================================================
# Allocation & Markdown Models
# ============================================================================

class Allocation(Base):
    __tablename__ = "allocations"

    allocation_id = Column(String, primary_key=True)
    forecast_id = Column(String, ForeignKey("forecasts.forecast_id"), nullable=False)
    manufacturing_qty = Column(Integer, nullable=False)
    safety_stock_percentage = Column(Float, nullable=False, default=0.20)
    initial_allocation_total = Column(Integer, nullable=False)
    holdback_total = Column(Integer, nullable=False)

    # JSON column for variable-length store allocations
    store_allocations = Column(JSON, nullable=False)  # [{"store_id": "S01", "initial": 176, "holdback": 142}, ...]

    created_at = Column(DateTime, server_default=func.now())

    __table_args__ = (
        CheckConstraint("manufacturing_qty >= 0", name="check_manufacturing_qty"),
        CheckConstraint("safety_stock_percentage >= 0 AND safety_stock_percentage <= 1", name="check_safety_stock"),
    )


class Markdown(Base):
    __tablename__ = "markdowns"

    markdown_id = Column(String, primary_key=True)
    forecast_id = Column(String, ForeignKey("forecasts.forecast_id"), nullable=False)
    week_number = Column(Integer, nullable=False)
    sell_through_pct = Column(Float, nullable=False)
    target_sell_through_pct = Column(Float, nullable=False, default=0.60)
    gap_pct = Column(Float, nullable=False)
    recommended_markdown_pct = Column(Float, nullable=False)
    elasticity_coefficient = Column(Float, nullable=False, default=2.0)
    expected_demand_lift_pct = Column(Float, nullable=True)
    status = Column(String, nullable=False, default="pending")
    reasoning = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    __table_args__ = (
        CheckConstraint("week_number >= 1 AND week_number <= 12", name="check_week_number"),
        CheckConstraint("sell_through_pct >= 0 AND sell_through_pct <= 1", name="check_sell_through"),
        CheckConstraint(
            "recommended_markdown_pct >= 0 AND recommended_markdown_pct <= 0.40",
            name="check_markdown_pct"
        ),
        CheckConstraint("status IN ('pending', 'approved', 'applied')", name="check_status"),
    )


# ============================================================================
# Sales Data Models
# ============================================================================

class HistoricalSales(Base):
    __tablename__ = "historical_sales"

    sale_id = Column(String, primary_key=True)
    store_id = Column(String, ForeignKey("stores.store_id"), nullable=False)
    category_id = Column(String, ForeignKey("categories.category_id"), nullable=False)
    week_start_date = Column(Date, nullable=False)
    units_sold = Column(Integer, nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    __table_args__ = (
        CheckConstraint("units_sold >= 0", name="check_units_sold"),
        Index("idx_historical_sales_store_category", "store_id", "category_id"),
        Index("idx_historical_sales_date", "week_start_date"),
    )


class ActualSales(Base):
    __tablename__ = "actual_sales"

    actual_id = Column(String, primary_key=True)
    store_id = Column(String, ForeignKey("stores.store_id"), nullable=False)
    forecast_id = Column(String, ForeignKey("forecasts.forecast_id"), nullable=False)
    week_number = Column(Integer, nullable=False)
    units_sold = Column(Integer, nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    __table_args__ = (
        CheckConstraint("week_number >= 1 AND week_number <= 12", name="check_week_number"),
        CheckConstraint("units_sold >= 0", name="check_units_sold"),
        Index("idx_actual_sales_forecast_week", "forecast_id", "week_number"),
    )


# ============================================================================
# Workflow Models
# ============================================================================

class SeasonParameters(Base):
    __tablename__ = "season_parameters"

    parameter_id = Column(String, primary_key=True)
    forecast_horizon_weeks = Column(Integer, nullable=False, default=12)
    season_start_date = Column(Date, nullable=False)
    replenishment_strategy = Column(String, nullable=False, default="weekly")
    dc_holdback_percentage = Column(Float, nullable=False, default=0.45)
    markdown_checkpoint_week = Column(Integer, nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    __table_args__ = (
        CheckConstraint("forecast_horizon_weeks >= 1 AND forecast_horizon_weeks <= 52", name="check_horizon_weeks"),
        CheckConstraint(
            "replenishment_strategy IN ('none', 'weekly', 'bi-weekly')",
            name="check_replenishment_strategy"
        ),
        CheckConstraint("dc_holdback_percentage >= 0 AND dc_holdback_percentage <= 1", name="check_holdback_pct"),
        CheckConstraint("markdown_checkpoint_week IS NULL OR (markdown_checkpoint_week >= 1 AND markdown_checkpoint_week <= 12)", name="check_markdown_week"),
    )


class Workflow(Base):
    """Workflow session model."""
    __tablename__ = "workflows"

    workflow_id = Column(String, primary_key=True, index=True)
    workflow_type = Column(String, nullable=False)  # "forecast" or "reforecast"
    forecast_id = Column(String, nullable=True)  # FK to forecasts (null for initial forecast)
    category_id = Column(String, nullable=False)

    # Status tracking
    status = Column(Enum(WorkflowStatus), default=WorkflowStatus.pending, nullable=False)
    current_agent = Column(String, nullable=True)  # "demand", "inventory", "pricing", null
    progress_pct = Column(Integer, default=0)

    # Session parameters (from SeasonParameters)
    forecast_horizon_weeks = Column(Integer, nullable=False)
    season_start_date = Column(String, nullable=False)
    replenishment_strategy = Column(String, nullable=False)
    dc_holdback_percentage = Column(Float, nullable=False)
    markdown_checkpoint_week = Column(Integer, nullable=True)

    # Workflow context (JSON)
    input_data = Column(JSON, nullable=True)  # Original request body
    output_data = Column(JSON, nullable=True)  # Final results
    error_message = Column(String, nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class WorkflowLog(Base):
    __tablename__ = "workflow_logs"

    log_id = Column(String, primary_key=True)
    workflow_id = Column(String, nullable=False)
    agent_name = Column(String, nullable=False)
    action = Column(String, nullable=False)
    input_data = Column(JSON, nullable=True)
    output_data = Column(JSON, nullable=True)
    duration_seconds = Column(Float, nullable=True)
    status = Column(String, nullable=False)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    __table_args__ = (
        CheckConstraint("status IN ('started', 'completed', 'failed')", name="check_status"),
        Index("idx_workflow_logs_workflow", "workflow_id"),
    )


# ============================================================================
# Exports
# ============================================================================

__all__ = [
    # Enums
    "WorkflowStatus",
    # Core entities
    "Category",
    "StoreCluster",
    "Store",
    # Forecast models
    "Forecast",
    "ForecastClusterDistribution",
    # Allocation & Markdown
    "Allocation",
    "Markdown",
    # Sales data
    "HistoricalSales",
    "ActualSales",
    # Workflow models
    "SeasonParameters",
    "Workflow",
    "WorkflowLog",
]
