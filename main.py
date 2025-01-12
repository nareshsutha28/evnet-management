from typing import List
from fastapi import (
    FastAPI, Depends, HTTPException, status
)
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from fastapi.security import HTTPBearer

from app.jwt import (
    create_access_token, verify_access_token
)
from app import (
    crud, schemas
)
from app.database import (
    engine, Base, get_db
)

# Initialize the database
Base.metadata.create_all(bind=engine)

app = FastAPI()
oauth2_scheme = HTTPBearer()

# Dummy data - Replace this with your DB query
fake_users_db = {
    "admin@gmail.com": {
        "email": "admin@gmail.com",
        "password": "password123"  # bcrypt hash for "password123"
    }
}

# Verify password function
def verify_password(input_password, exist_password):
    return input_password==exist_password


# Get user from database (use your actual database here)
def get_user(db, email: str):
    return db.get(email)


# Dependency to get the current user from the token
def get_current_user(token: str = Depends(oauth2_scheme)):
    payload = verify_access_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return payload


# Create the login endpoint
@app.post("/login", response_model=schemas.LoginResponse)
async def login_for_access_token(user: schemas.User, db: Session = Depends(get_db)):
    db_user = get_user(fake_users_db, user.email)  # Query the database for the user by email

    if not db_user or not verify_password(user.password, db_user["password"]):
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials",
        )
    
    access_token = create_access_token(
        data={"sub": user.email}
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    error_obj = exc.errors()[0]
    if error_obj.get("type")=="value_error":
        error = error_obj["ctx"]["error"].args[0]
    else:
        error = {error_obj["loc"][1] : error_obj["msg"]}
    return JSONResponse({"details": error}, status_code=400)


@app.post("/events/", response_model=schemas.EventResponse )
def create_event(event: schemas.EventCreate, db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    db_event = crud.create_event(db=db, event=event)
    return db_event


@app.get("/events/", response_model=List[schemas.EventResponse])
def get_all_events(db: Session = Depends(get_db)):
    events = crud.get_all_events(db=db)
    return events


@app.put("/events/{event_id}", response_model=schemas.EventResponse)
def update_event(event_id: int, event: schemas.EventUpdate, db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    db_event = crud.update_event(db=db, event_id=event_id, event=event)
    if db_event is None:
        raise HTTPException(status_code=404, detail="Event not found")
    return db_event


@app.delete("/events/{event_id}", response_model=schemas.EventResponse)
def delete_event(event_id: int, db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    db_event = crud.delete_event(db=db, event_id=event_id)
    if db_event is None:
        raise HTTPException(status_code=404, detail="Event not found")
    elif db_event.get("error") is not None:
        raise HTTPException(status_code=400, detail=db_event.get("error"))
    return db_event


@app.post("/attendees/register/", response_model=schemas.AttendeeResponse)
def register_attendee(attendee: schemas.AttendeeCreate, db: Session = Depends(get_db)):
    # Register the attendee
    db_attendee = crud.register_attendee(db=db, attendee=attendee)
    
    if db_attendee is None:
        raise HTTPException(status_code=404, detail="Event not found")
    elif db_attendee.get("error") is not None:
        raise HTTPException(status_code=400, detail=db_attendee.get("error"))
    return db_attendee


@app.get("/events/{event_id}/attendees/", response_model=list[schemas.AttendeeResponse])
def get_attendees_by_event_id(event_id: int, db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    attendees = crud.get_attendees_by_event_id(db=db, event_id=event_id)
    if not attendees:
        raise HTTPException(status_code=404, detail="Attendees not found for this event")
    return attendees


@app.post("/attendees/check-in/", response_model=schemas.AttendeeResponse)
def check_in_attendee(request: schemas.CheckInRequest, db: Session = Depends(get_db)):
    attendee = crud.check_in_attendee(db, email=request.email, event_id=request.event_id)
    if not attendee:
        raise HTTPException(status_code=404, detail="Attendee not found or invalid email/event combination")
    
    elif attendee.get("error") is not None:
        raise HTTPException(status_code=400, detail=attendee.get("error"))
    return attendee


@app.get("/")
def read_root():
    return {"message": "Welcome to the Event Management API"}
