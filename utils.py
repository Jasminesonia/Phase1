from os import getenv
from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import JWTError, jwt
from dotenv import load_dotenv
# from auth import ALGORITHM, SECRET_KEY
import os

# Load the .env file
load_dotenv()

# Access the environment variables
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM","HS256")
ACCESS_TOKEN_EXPIRES_IN = os.getenv("ACCESS_TOKEN_EXPIRES_IN",30)  # minutes
REFRESH_TOKEN_EXPIRES_IN = os, getenv("REFRESH_TOKEN_EXPIRES_IN",1440)  # 1 day

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str):
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)


def create_reset_token(email: str, RESET_TOKEN_EXPIRE_MINUTES=30):
    expire = datetime.utcnow() + timedelta(minutes=RESET_TOKEN_EXPIRE_MINUTES)
    to_encode = {"sub": email, "exp": expire}
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def verify_reset_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        return email
    except JWTError:
        return None
