from sqlalchemy import Column, Integer, String, DateTime
from app.database import Base


class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    event_type = Column(String, nullable=False)
    page = Column(String, nullable=True)
    product_id = Column(Integer, nullable=True)
    category = Column(String, nullable=True)
    timestamp = Column(DateTime, nullable=False)