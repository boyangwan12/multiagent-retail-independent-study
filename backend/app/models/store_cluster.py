from sqlalchemy import Column, String, Text, DateTime, CheckConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database.db import Base

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
