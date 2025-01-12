from pydantic import (
    BaseModel, Field, model_validator, EmailStr
)    
from datetime import datetime
from enum import Enum
from typing import Optional


class EventStatus(str, Enum):
    scheduled = "scheduled"
    ongoing = "ongoing"
    completed = "completed"
    canceled = "canceled"


class User(BaseModel):
    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str


class EventCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Name of the event")
    description: Optional[str] = Field(None, max_length=500, description="Description of the event")
    start_time: datetime = Field(..., description="Start time of the event (must be before end_time)")
    end_time: datetime = Field(..., description="End time of the event (must be after start_time)")
    location: str = Field(..., min_length=1, max_length=200, description="Location of the event")
    max_attendees: int = Field(..., ge=1, description="Maximum number of attendees (must be at least 1)")

    @model_validator(mode="after")
    def validate_start_time(cls, data):
        start_time_naive = data.start_time.replace(tzinfo=None)  # Make it naive
        if data.start_time >= data.end_time:
            raise ValueError("Start time should less then end Time.")
        
        # Ensure start_time is in the future
        if start_time_naive <= datetime.utcnow():
            raise ValueError("Start time must be in the future.")
        return data

    class Config:
        schema_extra = {
            "example": {
                "name": "Tech Conference 2025",
                "description": "A conference on emerging technologies.",
                "start_time": "2025-02-15T10:00:00",
                "end_time": "2025-02-15T17:00:00",
                "location": "New York Convention Center",
                "max_attendees": 500,
            }
        }


class EventUpdate(EventCreate):
    status: EventStatus = None


class EventResponse(BaseModel):
    event_id: int
    name: str
    description: Optional[str] = None
    start_time: datetime
    end_time: datetime
    location: str
    max_attendees: int
    status: EventStatus

    class Config:
        orm_mode = True


class AttendeeCreate(BaseModel):
    first_name: str = Field(..., min_length=3, max_length=100, description="First Name of the Attendee")
    last_name: str = Field(..., min_length=3, max_length=100, description="Last Name of the Attendee")
    email: EmailStr 
    phone_number: str = Field(..., min_length=10, max_length=15, description="Location of the event")
    event_id: int

    class Config:
        orm_mode = True


class AttendeeResponse(BaseModel):
    attendee_id: int
    first_name: str
    last_name: str
    email: str
    phone_number: str
    check_in_status: bool

    class Config:
        orm_mode = True


class CheckInRequest(BaseModel):
    email: str
    event_id: int


class AttendeeBase(BaseModel):
    first_name: str
    last_name: str
    email: str
    phone_number: str
    check_in_status: bool
