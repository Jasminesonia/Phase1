from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
# MONGO_URI = "mongodb://localhost:27017/poster_generation" #MongoDB URL
# MONGO_URI = "MONGO_URI" #MongoDB URL
print("Using MongoDB URI:", MONGO_URI)

DATABASE_NAME = "social_media"

client = AsyncIOMotorClient(MONGO_URI)
db = client[DATABASE_NAME]


def get_collection(name: str):
    return db[name]
