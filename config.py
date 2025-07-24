import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    EMAIL_HOST = os.getenv("EMAIL_HOST")
    EMAIL_PORT = int(os.getenv("EMAIL_PORT", 587))
    EMAIL_USERNAME = os.getenv("EMAIL_USERNAME")
    EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
    EMAIL_FROM = os.getenv("EMAIL_FROM")
    EMAIL_FROM_NAME = os.getenv("EMAIL_FROM_NAME")

    SECRET_KEY = os.getenv("SECRET_KEY")
    AUTHJWT_SECRET_KEY = os.getenv("AUTHJWT_SECRET_KEY")
    ALGORITHM = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRES_IN = int(os.getenv("ACCESS_TOKEN_EXPIRES_IN", 30))
    REFRESH_TOKEN_EXPIRES_IN = int(os.getenv("REFRESH_TOKEN_EXPIRES_IN", 1440))

    SQUARE_API_URL = os.getenv("SQUARE_API_URL")
    ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")




settings = Settings()

