import jwt, os
from datetime import (
    datetime, timedelta
)
from typing import Optional
from dotenv import load_dotenv

load_dotenv() 


SECRET_KEY = os.getenv("JWT_SECRET_KEY")  # Change this to a more secure secret
ALGORITHM = os.getenv("JWT_ALGORITHM")  # Algorithm used for encoding
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))  # Token expiration time


# Function to create JWT token
def create_access_token(data: dict, expires_in: Optional[timedelta] = None):
    if expires_in is None:
        expires_in = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    expire = datetime.utcnow() + expires_in
    to_encode = data.copy()
    to_encode.update({"exp": expire})
    print(to_encode)
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# Function to verify the JWT token (you can use this to validate the token in the future)
def verify_access_token(token: str):
    try:
        payload = jwt.decode(token.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        print("--------", payload)
        return payload
    except jwt.ExpiredSignatureError:
        return None  # Token expired
    except jwt.PyJWTError:
        return None  # Invalid token
