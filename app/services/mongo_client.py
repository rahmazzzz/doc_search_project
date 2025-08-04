from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import TEXT
from app.core.config import settings

# Create async MongoDB client
client = AsyncIOMotorClient(settings.MONGO_URI)
db = client[settings.MONGODB_DATABASE]

# Collections
chunk_collection = db["chunks"]
user_collection = db["users"]

# Ensure text index (runs only once)
chunk_collection.create_index([("text", TEXT)])

# ----- Chunk operations -----

async def insert_chunks(chunks: list):
    result = await chunk_collection.insert_many(chunks)
    for chunk, id in zip(chunks, result.inserted_ids):
        chunk["_id"] = str(id)
    return chunks

async def text_search(query: str):
    cursor = chunk_collection.find({"$text": {"$search": query}})
    results = []
    async for doc in cursor:
        results.append({"text": doc["text"], "_id": str(doc["_id"])})
    return results

# ----- Auth helper -----

def get_user_collection():
    return user_collection
