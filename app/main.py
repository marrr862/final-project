from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session

from app.schemas import UserEvent, UserEventResponse
from app.producer import send_event_to_kafka
from app.config import KAFKA_TOPIC
from app.database import SessionLocal, engine, Base
from app.models import Event

Base.metadata.create_all(bind=engine)

app = FastAPI(title="User Behavior Analytics API")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
def read_root():
    return {"message": "API is running"}


@app.post("/events", response_model=UserEventResponse)
def create_event(event: UserEvent, db: Session = Depends(get_db)):
    db_event = Event(
        user_id=event.user_id,
        event_type=event.event_type,
        page=event.page,
        product_id=event.product_id,
        category=event.category,
        timestamp=event.timestamp
    )

    db.add(db_event)
    db.commit()
    db.refresh(db_event)

    event_dict = {
        "id": db_event.id,
        "user_id": db_event.user_id,
        "event_type": db_event.event_type,
        "page": db_event.page,
        "product_id": db_event.product_id,
        "category": db_event.category,
        "timestamp": db_event.timestamp.isoformat()
    }

    send_event_to_kafka(event_dict, KAFKA_TOPIC)

    return db_event


@app.get("/events")
def get_events(db: Session = Depends(get_db)):
    return db.query(Event).all()