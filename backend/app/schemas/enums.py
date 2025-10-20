from enum import Enum

class RetailArchetype(str, Enum):
    """Retail business model archetype"""
    FASHION_RETAIL = "FASHION_RETAIL"
    STABLE_CATALOG = "STABLE_CATALOG"
    CONTINUOUS = "CONTINUOUS"

class ReplenishmentStrategy(str, Enum):
    """Replenishment frequency strategy"""
    NONE = "none"              # One-shot allocation (Zara-style)
    WEEKLY = "weekly"          # Standard retail
    BI_WEEKLY = "bi-weekly"    # Conservative approach

class LocationTier(str, Enum):
    """Store location quality tier"""
    A = "A"  # Prime location
    B = "B"  # Standard location
    C = "C"  # Secondary location

class FashionTier(str, Enum):
    """Fashion-forwardness tier for store clusters"""
    PREMIUM = "PREMIUM"
    MAINSTREAM = "MAINSTREAM"
    VALUE = "VALUE"

class StoreFormat(str, Enum):
    """Physical store format"""
    MALL = "MALL"
    STANDALONE = "STANDALONE"
    SHOPPING_CENTER = "SHOPPING_CENTER"
    OUTLET = "OUTLET"

class Region(str, Enum):
    """Geographic region"""
    NORTHEAST = "NORTHEAST"
    SOUTHEAST = "SOUTHEAST"
    MIDWEST = "MIDWEST"
    WEST = "WEST"

class MarkdownStatus(str, Enum):
    """Markdown decision status"""
    PENDING = "pending"
    APPROVED = "approved"
    APPLIED = "applied"

class WorkflowStatus(str, Enum):
    """Workflow execution status"""
    STARTED = "started"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"