from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database.db import Base

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
