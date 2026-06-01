from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from collections import Counter

from app.schemas import UserEvent, UserEventResponse
from app.producer import send_event_to_kafka
from app.config import KAFKA_TOPIC
from app.database import SessionLocal, engine, Base
from app.models import Event

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="User Behavior Analytics API",
    description="Real-time user behavior tracking system with FastAPI, Kafka, Spark, PostgreSQL and analytics.",
    version="1.0.0"
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
def read_root():
    return {
        "message": "User Behavior Analytics API is running",
        "docs": "/docs"
    }


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": "User Behavior Analytics API"
    }


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
    return db.query(Event).order_by(Event.id.desc()).all()


@app.get("/events/{event_id}")
def get_event_by_id(event_id: int, db: Session = Depends(get_db)):
    event = db.query(Event).filter(Event.id == event_id).first()

    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    return event


@app.delete("/events/{event_id}")
def delete_event(event_id: int, db: Session = Depends(get_db)):
    event = db.query(Event).filter(Event.id == event_id).first()

    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    db.delete(event)
    db.commit()

    return {"message": "Event deleted successfully"}


@app.get("/analytics/summary")
def analytics_summary(db: Session = Depends(get_db)):
    events = db.query(Event).all()

    if not events:
        return {
            "total_events": 0,
            "total_users": 0,
            "top_page": None,
            "top_event_type": None,
            "top_category": None
        }

    pages = [event.page for event in events if event.page]
    event_types = [event.event_type for event in events if event.event_type]
    categories = [event.category for event in events if event.category]

    return {
        "total_events": len(events),
        "total_users": len(set(event.user_id for event in events)),
        "top_page": Counter(pages).most_common(1)[0][0] if pages else None,
        "top_event_type": Counter(event_types).most_common(1)[0][0] if event_types else None,
        "top_category": Counter(categories).most_common(1)[0][0] if categories else None
    }


@app.get("/analytics/users")
def user_analytics(db: Session = Depends(get_db)):
    events = db.query(Event).all()

    user_counts = Counter(event.user_id for event in events)

    result = []
    for user_id, count in user_counts.items():
        if count <= 2:
            segment = "low"
        elif count <= 5:
            segment = "medium"
        else:
            segment = "high"

        result.append({
            "user_id": user_id,
            "event_count": count,
            "segment": segment,
            "status": "suspicious" if count > 5 else "normal"
        })

    return result


@app.get("/analytics/pages")
def page_analytics(db: Session = Depends(get_db)):
    events = db.query(Event).all()

    pages = [event.page for event in events if event.page]
    page_counts = Counter(pages)

    return [
        {"page": page, "count": count}
        for page, count in page_counts.most_common()
    ]


@app.get("/analytics/events")
def event_type_analytics(db: Session = Depends(get_db)):
    events = db.query(Event).all()

    event_types = [event.event_type for event in events if event.event_type]
    event_counts = Counter(event_types)

    return [
        {"event_type": event_type, "count": count}
        for event_type, count in event_counts.most_common()
    ]


@app.get("/analytics/categories")
def category_analytics(db: Session = Depends(get_db)):
    events = db.query(Event).all()

    categories = [event.category for event in events if event.category]
    category_counts = Counter(categories)

    return [
        {"category": category, "count": count}
        for category, count in category_counts.most_common()
    ]


@app.get("/recommendations/{user_id}")
def recommend_for_user(user_id: int, db: Session = Depends(get_db)):
    events = db.query(Event).filter(Event.user_id == user_id).all()

    if not events:
        raise HTTPException(status_code=404, detail="No events found for this user")

    categories = [event.category for event in events if event.category]

    if not categories:
        return {
            "user_id": user_id,
            "recommended_category": None,
            "message": "Not enough category data"
        }

    recommended_category = Counter(categories).most_common(1)[0][0]

    return {
        "user_id": user_id,
        "recommended_category": recommended_category,
        "reason": "Based on the user's most frequent activity category"
    }


@app.get("/fraud/users")
def fraud_users(db: Session = Depends(get_db)):
    events = db.query(Event).all()

    user_counts = Counter(event.user_id for event in events)

    result = []

    for user_id, count in user_counts.items():
        fraud_score = min(count / 10, 1)

        result.append({
            "user_id": user_id,
            "event_count": count,
            "fraud_score": round(fraud_score, 2),
            "status": "suspicious" if fraud_score >= 0.6 else "normal"
        })

    return result

@app.get("/analytics/engagement")
def engagement_analytics(db: Session = Depends(get_db)):
    events = db.query(Event).all()

    user_counts = Counter(event.user_id for event in events)

    result = []

    for user_id, count in user_counts.items():
        if count <= 2:
            engagement_level = "Low"
        elif count <= 5:
            engagement_level = "Medium"
        else:
            engagement_level = "High"

        engagement_score = min(count * 10, 100)

        result.append({
            "user_id": user_id,
            "event_count": count,
            "engagement_score": engagement_score,
            "engagement_level": engagement_level
        })

    return sorted(result, key=lambda x: x["engagement_score"], reverse=True)