from app.clients.mongo_client import MongoDBClient

class MongoService:
    def __init__(self, mongo_client: MongoDBClient):
        self.db = mongo_client.get_db()
        self.users_collection = self.db["users"]
        self.documents_collection = self.db["documents"]
        self.files_collection = self.db["uploaded_files"]

    async def insert_chunks(self, chunks: list, user_id: str):
        for chunk in chunks:
            chunk["user_id"] = user_id
        result = await self.documents_collection.insert_many(chunks)
        return result.inserted_ids

    async def get_user_by_username(self, username: str):
        return await self.users_collection.find_one({"username": username})

    async def get_user_by_email(self, email: str):
        return await self.users_collection.find_one({"email": email})

    async def create_user(self, user_data: dict):
        return await self.users_collection.insert_one(user_data)

    async def save_file(self, file_info: dict):
        result = await self.files_collection.insert_one(file_info)
        return result.inserted_id
