from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import os

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "codara")

client = AsyncIOMotorClient(MONGO_URI)
db = client[DATABASE_NAME]

levels_collection = db["levels"]
attempts_collection = db["attempts"]
progress_collection = db["progress"]
daily_tasks_collection = db["daily_tasks"]
