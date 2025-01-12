from sqlalchemy import (
    Column, Integer, String, DateTime, Boolean, ForeignKey, Enum, UniqueConstraint
)
from sqlalchemy.orm import relationship
from app.database import Base
import enum


# Define Event Status Enum
class EventStatus(enum.Enum):
    scheduled = "scheduled"
    ongoing = "ongoing"
    completed = "completed"
    canceled = "canceled"


# Event Model
class Event(Base):
    __tablename__ = "events"

    event_id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    location = Column(String, nullable=False)
    max_attendees = Column(Integer, nullable=False)
    status = Column(Enum(EventStatus), default=EventStatus.scheduled, nullable=False)

    # Relationship with Attendee
    attendees = relationship("Attendee", back_populates="event")


# Attendee Model
class Attendee(Base):
    __tablename__ = "attendees"

    attendee_id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    phone_number = Column(String, nullable=False)
    check_in_status = Column(Boolean, default=False, nullable=False)

    # Foreign key to Event
    event_id = Column(Integer, ForeignKey("events.event_id"), nullable=False)

    # Add unique constraint for event_id and email
    __table_args__ = (UniqueConstraint('event_id', 'email', name='unique_event_email'),)

    # Relationship with Event
    event = relationship("Event", back_populates="attendees")
