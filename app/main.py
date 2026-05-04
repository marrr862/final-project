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


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": "User Behavior Analytics API"
    }


@app.get("/analytics/summary")
def analytics_summary(db: Session = Depends(get_db)):
    events = db.query(Event).all()

    if not events:
        return {
            "total_events": 0,
            "total_users": 0,
            "top_page": None,
            "top_event_type": None
        }

    total_events = len(events)
    total_users = len(set(event.user_id for event in events))

    pages = [event.page for event in events if event.page]
    event_types = [event.event_type for event in events if event.event_type]

    top_page = max(set(pages), key=pages.count) if pages else None
    top_event_type = max(set(event_types), key=event_types.count) if event_types else None

    return {
        "total_events": total_events,
        "total_users": total_users,
        "top_page": top_page,
        "top_event_type": top_event_type
    }