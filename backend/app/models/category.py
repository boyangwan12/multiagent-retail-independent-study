from sqlalchemy import Column, String, Date, Integer, Text, DateTime, CheckConstraint
from sqlalchemy.sql import func
from app.database.db import Base

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
