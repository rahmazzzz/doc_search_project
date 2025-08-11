from app.clients.nosqldb_client import MongoDBClient
from bson.binary import Binary
import aiofiles
from typing import List




class MongoRepository:
    def __init__(self, mongo_client: MongoDBClient):
        self.db = mongo_client.get_db()
        self.users_collection = self.db["users"]
        self.documents_collection = self.db["documents"]
        self.prompts_collection = self.db["prompt"]
        self.files_collection = self.db["uploaded_files"]
        self.collection = self.db["uploaded_files"]
    async def insert_chunks(self, chunks: list):
        result = await self.documents_collection.insert_many(chunks)
        return result.inserted_ids

    async def get_user_by_username(self, username: str):
        return await self.users_collection.find_one({"username": username})

    async def get_user_by_email(self, email: str):
        return await self.users_collection.find_one({"email": email})

    async def create_user(self, user_data: dict):
        return await self.users_collection.insert_one(user_data)

    async def save_file(self, file_path: str, file_name: str, username: str):
        # Read file content asynchronously
        async with aiofiles.open(file_path, 'rb') as f:
            file_bytes = await f.read()

        # Prepare the document with binary data and metadata combined
        file_doc = {
            "filename": file_name,
            "username": username,
        }

        # Insert the document into MongoDB collection
        result = await self.files_collection.insert_one(file_doc)
        return result.inserted_id
    async def get_all_files_metadata(self, username: str = None):
        """
        Fetch all files with their IDs, filenames, and usernames.
        Optionally filter by username if provided.
        """
        query = {}
        if username:
            query["username"] = username

        cursor = self.collection.find(query, {"_id": 1, "filename": 1, "username": 1})
        files = []
        async for doc in cursor:
            files.append({
                "file_id": str(doc["_id"]),
                "filename": doc.get("filename", ""),
                "username": doc.get("username", ""),
            })

        return files
   
    