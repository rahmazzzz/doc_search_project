from typing import Optional, Dict
from motor.motor_asyncio import AsyncIOMotorDatabase

class PromptRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db["prompts"]

    async def insert_prompt(self, system: str, user: str, prompt_name: str) -> str:
        doc = {"system": system, "user": user, "prompt_name": prompt_name}
        res = await self.collection.insert_one(doc)
        return str(res.inserted_id)

    async def get_prompt_by_name(self, prompt_name: str) -> Optional[Dict]:
        return await self.collection.find_one({"prompt_name": prompt_name})
