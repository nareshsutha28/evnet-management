from celery import Celery
from celery.schedules import crontab
from fastapi import Depends

from sqlalchemy.orm import Session
from sqlalchemy import not_
from app import crud, database, models
from app.models import Event, EventStatus
from datetime import datetime 
from contextlib import contextmanager


# Initialize Celery
celery_app = Celery(
    "worker",
    broker="redis://localhost:6379/0",  # Redis broker
    backend="redis://localhost:6379/0",  # Redis backend
)

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    beat_schedule={
        "update_event_status_every_minute": {
            "task": "app.tasks.update_event_status",
            "schedule": crontab(minute="*"),  # Every minute
        },
    },
)

# Context manager for database session
@contextmanager
def get_db():
    db: Session = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


@celery_app.task(name="app.tasks.update_event_status")
def update_event_status():
    with get_db() as db:
        try:
            current_time = datetime.utcnow()  # Use UTC to avoid timezone issues
            events = db.query(Event).filter(
                not_(Event.status.in_([EventStatus.completed, EventStatus.canceled]))
                ).all()

            for event in events:
                if event.start_time <= current_time <= event.end_time:
                    event.status = EventStatus.ongoing
                elif current_time > event.end_time:
                    event.status = EventStatus.completed
                
                db.add(event)  # Stage the changes
            db.commit()  # Commit all changes at once
        finally:
            db.close()  # Always close the database session
