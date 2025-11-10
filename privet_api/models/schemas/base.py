"""Base schemas for API models."""

from datetime import datetime
from typing import Optional, Any, Dict
from pydantic import BaseModel, Field, ConfigDict


class BaseSchema(BaseModel):
    """Base schema with common configuration."""
    
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        use_enum_values=True,
        validate_assignment=True,
    )


class TimestampedSchema(BaseSchema):
    """Schema with timestamp fields."""
    
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")


class ResponseSchema(BaseSchema):
    """Base response schema."""
    
    success: bool = Field(True, description="Operation success status")
    message: Optional[str] = Field(None, description="Response message")
    data: Optional[Any] = Field(None, description="Response data")


class ErrorSchema(BaseSchema):
    """Error response schema."""
    
    detail: str = Field(..., description="Error detail message")
    type: str = Field(..., description="Error type")
    field: Optional[str] = Field(None, description="Field that caused the error")
    context: Optional[Dict[str, Any]] = Field(None, description="Additional context")


class PaginationParams(BaseSchema):
    """Pagination parameters."""
    
    offset: int = Field(0, ge=0, description="Number of items to skip")
    limit: int = Field(20, ge=1, le=100, description="Number of items to return")


class PaginatedResponse(BaseSchema):
    """Paginated response schema."""
    
    items: list = Field(..., description="List of items")
    total: int = Field(..., description="Total number of items")
    offset: int = Field(..., description="Current offset")
    limit: int = Field(..., description="Current limit")
    
    @property
    def has_more(self) -> bool:
        """Check if there are more items."""
        return self.offset + len(self.items) < self.total