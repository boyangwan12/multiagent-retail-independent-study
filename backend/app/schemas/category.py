from pydantic import BaseModel, Field, ConfigDict
from datetime import date, datetime
from typing import Optional
from app.schemas.enums import RetailArchetype

class CategoryBase(BaseModel):
    """Base category fields"""
    category_name: str = Field(..., description="Display name (e.g., 'Women's Dresses')")
    season_start_date: date = Field(..., description="Season start")
    season_end_date: date = Field(..., description="Season end")
    season_length_weeks: int = Field(..., description="Duration in weeks", ge=1, le=52)
    archetype: RetailArchetype = Field(default=RetailArchetype.FASHION_RETAIL, description="Business model archetype")
    description: Optional[str] = Field(None, description="Category description")

class CategoryCreate(CategoryBase):
    """Create new category"""
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "category_name": "Women's Dresses",
            "season_start_date": "2025-03-01",
            "season_end_date": "2025-05-23",
            "season_length_weeks": 12,
            "archetype": "FASHION_RETAIL",
            "description": "Spring/Summer 2025 women's dresses collection"
        }
    })
    category_id: str = Field(..., description="Unique category ID")

class Category(CategoryBase):
    """Category read model"""
    category_id: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)