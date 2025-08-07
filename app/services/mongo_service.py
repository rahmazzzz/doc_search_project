from app.repositories.mongo_repository import MongoRepository

class MongoService:
    def __init__(self, mongo_repository: MongoRepository):
        self.mongo_repository = mongo_repository

    async def insert_chunks_with_user(self, chunks: list, user_id: str):
        for chunk in chunks:
            chunk["user_id"] = user_id
        return await self.mongo_repository.insert_chunks(chunks)

    async def get_user_by_username(self, username: str):
        return await self.mongo_repository.get_user_by_username(username)

    async def get_user_by_email(self, email: str):
        return await self.mongo_repository.get_user_by_email(email)

    async def create_user(self, user_data: dict):
        return await self.mongo_repository.create_user(user_data)

    async def save_file(self, file_info: dict):
        return await self.mongo_repository.save_file(file_info)