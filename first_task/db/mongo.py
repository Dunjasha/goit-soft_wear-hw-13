from motor.motor_asyncio import AsyncIOMotorClient
from config import MONGO_DETAILS

client = AsyncIOMotorClient(MONGO_DETAILS)
db = client.contacts_db
users_collection = db.users
contacts_collection = db.contacts
