from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class UserEvent(BaseModel):
    user_id: int
    event_type: str
    page: Optional[str] = None
    product_id: Optional[int] = None
    category: Optional[str] = None
    timestamp: datetime


class UserEventResponse(BaseModel):
    id: int
    user_id: int
    event_type: str
    page: Optional[str] = None
    product_id: Optional[int] = None
    category: Optional[str] = None
    timestamp: datetime

    class Config:
        from_attributes = True