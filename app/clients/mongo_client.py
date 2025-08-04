from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import TEXT
from app.core.config import settings

class MongoClient:
    def __init__(self):
        self.client = AsyncIOMotorClient(settings.MONGO_URI)
        self.db = self.client[settings.MONGODB_DATABASE]
        self.chunk_collection = self.db["chunks"]
        self.user_collection = self.db["users"]

        
        self.chunk_collection.create_index([("text", TEXT)])

    async def insert_chunks(self, chunks: list):
        result = await self.chunk_collection.insert_many(chunks)
        for chunk, id in zip(chunks, result.inserted_ids):
            chunk["_id"] = str(id)
        return chunks

    async def text_search(self, query: str):
        cursor = self.chunk_collection.find({"$text": {"$search": query}})
        results = []
        async for doc in cursor:
            results.append({"text": doc["text"], "_id": str(doc["_id"])})
        return results

    def get_user_collection(self):
        return self.user_collection
