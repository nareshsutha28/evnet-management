from datetime import datetime
from sqlalchemy.orm import Session
from app.models import Event, Attendee
from app.schemas import (
    EventCreate, AttendeeCreate
)


def create_event(db: Session, event: EventCreate) -> Event:
    db_event = Event(
        name=event.name,
        description=event.description,
        start_time=event.start_time,
        end_time=event.end_time,
        location=event.location,
        max_attendees=event.max_attendees
    )
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    return db_event


def update_event(db: Session, event_id: int, event: EventCreate) -> Event:
    db_event = db.query(Event).filter(Event.event_id == event_id).first()
    if db_event is None:
        return None  # Event not found

    # Update event fields
    db_event.name = event.name
    db_event.description = event.description
    db_event.start_time = event.start_time
    db_event.end_time = event.end_time
    db_event.location = event.location
    db_event.max_attendees = event.max_attendees
    db_event.status = event.status

    db.commit()
    db.refresh(db_event)
    return db_event


def delete_event(db: Session, event_id: int):
    db_event = db.query(Event).filter(Event.event_id == event_id).first()
    if db_event is None:
        return None  # Event not found

    check_attendee = db.query(Attendee).filter(Attendee.event_id == event_id).first()
    if check_attendee:
        return {"error": "Attendees already register in this event so can't be delete."} 
    
    db.delete(db_event)
    db.commit()
    return db_event


def get_all_events(db: Session):
    # Fetch events with attendees using join
    events = db.query(Event).all()
    return events


def register_attendee(db: Session, attendee: AttendeeCreate):
    # Check if the event exists
    db_event = db.query(Event).filter(Event.event_id == attendee.event_id,     
                                      Event.start_time > datetime.utcnow()).first()
    if not db_event:
        return None  # Event not found

    attendees_count = db.query(Attendee).filter(Attendee.event_id == attendee.event_id).count()
    if db_event.max_attendees <= attendees_count:
        return {"error": "Event Limit is Exceeds."}

    try: 
        # Create a new Attendee
        db_attendee = Attendee(
            first_name=attendee.first_name,
            last_name=attendee.last_name,
            email=attendee.email,
            phone_number=attendee.phone_number,
            event_id=attendee.event_id,
        )
        db.add(db_attendee)
        db.commit()
        db.refresh(db_attendee)
        return db_attendee
    except:
        return {"error": "You are already registered for this event."}


def get_attendees_by_event_id(db: Session, event_id: int):
    return db.query(Attendee).filter(Attendee.event_id == event_id).all()


def check_in_attendee(db: Session, email: str, event_id: int):
    attendee = db.query(Attendee).filter(Attendee.email == email, Attendee.event_id == event_id).first()
    if not attendee:
        return None  # Attendee not found

    db_event = db.query(Event).filter(Event.event_id == attendee.event_id).first()
    
    if not db_event.start_time <= datetime.utcnow():
        return {"error": "Event is not started yet."}
        
    elif datetime.utcnow() > db_event.end_time:
        return {"error": "Event is over."}

    attendee.check_in_status = True
    db.commit()
    db.refresh(attendee)
    return attendee
