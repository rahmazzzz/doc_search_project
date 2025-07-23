from pymongo import MongoClient, TEXT
from app.core.config import settings

client = MongoClient(settings.MONGO_URI)
db = client["doc_db"]
collection = db["chunks"]
collection.create_index([("text", TEXT)])

def insert_chunks(chunks: list):
    result = collection.insert_many(chunks)
    for chunk, id in zip(chunks, result.inserted_ids):
        chunk["_id"] = str(id)
    return chunks

def text_search(query: str):
    cursor = collection.find({"$text": {"$search": query}})
    return [{"text": doc["text"], "_id": str(doc["_id"])} for doc in cursor]
